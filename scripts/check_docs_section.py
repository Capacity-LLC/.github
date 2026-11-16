#!/usr/bin/env python3
"""Fails a pull request whose "## Documentation" section is missing, empty or a bare "None".

Rule (every Capacity-LLC repository, people and Claude Code alike): every change updates the
documents that describe it - ITSD docs, partner docs, GitOps docs, READMEs, CLAUDE.md - in the same
PR or in a linked PR that merges with it. The PR says which, or "None:" and why.

Reads PR_BODY, PR_AUTHOR, PR_AUTHOR_TYPE, PR_LABELS (comma-separated), PR_NUMBER,
GITHUB_REPOSITORY and GITHUB_TOKEN from the environment.

The docs-exempt label ("no docs needed") counts when a code owner of the repository added it: anyone
named as @user in its CODEOWNERS (.github/, root or docs/), plus EXEMPT_APPROVERS for repositories
without one. A code owner cannot exempt their own PR, except EXEMPT_APPROVERS. Organisation admins can
also merge past a failing check (ruleset bypass), so the label is the recorded "no docs" decision and
the bypass is the escape hatch.
"""
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request
from typing import Callable, Optional

EXEMPT_LABEL = "docs-exempt"
EXEMPT_APPROVERS = {"rbhocap"}  # always count, also on their own PRs
CODEOWNERS_PATHS = (".github/CODEOWNERS", "CODEOWNERS", "docs/CODEOWNERS")
MIN_REASON = 15  # characters of explanation after "None"


def last_labeler(repo: str, number: str, token: str, label: str) -> Optional[str]:
    """Login of whoever most recently added `label` to the PR, from its issue events."""
    actor, page = None, 1
    while True:
        req = urllib.request.Request(
            f"https://api.github.com/repos/{repo}/issues/{number}/events?per_page=100&page={page}",
            headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            events = json.load(resp)
        for e in events:
            if e.get("event") == "labeled" and (e.get("label") or {}).get("name") == label:
                actor = (e.get("actor") or {}).get("login")
        if len(events) < 100:
            return actor
        page += 1


def _get(url: str, token: str):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}",
                                               "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def parse_codeowners(text: str) -> set[str]:
    """Individual @user owners in a CODEOWNERS file. Teams (@org/team) and e-mail owners are
    ignored: the workflow token cannot read team membership."""
    owners = set()
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        for tok in line.split()[1:]:
            if tok.startswith("@") and "/" not in tok:
                owners.add(tok[1:].lower())
    return owners


def code_owners(repo: str, ref: str, token: str) -> set[str]:
    """Code owners of the PR's base branch; empty when the repository has no CODEOWNERS."""
    for path in CODEOWNERS_PATHS:
        try:
            data = _get(f"https://api.github.com/repos/{repo}/contents/{path}?ref={ref}", token)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                continue
            raise
        return parse_codeowners(base64.b64decode(data.get("content", "")).decode("utf-8", "replace"))
    return set()


def check(body: str, author: str, author_type: str, labels: list[str],
          labeler: Callable[[], Optional[str]] = lambda: None,
          owners: Callable[[], set[str]] = lambda: set()) -> tuple[bool, str]:
    if author_type == "Bot" or author.endswith("[bot]"):
        return True, f"skipped: opened by a bot ({author})"
    if EXEMPT_LABEL in labels:
        who = labeler()
        w = (who or "").lower()
        allowed = {a.lower() for a in EXEMPT_APPROVERS} | owners()
        if w in {a.lower() for a in EXEMPT_APPROVERS}:
            return True, f"skipped: {who} applied the {EXEMPT_LABEL} label"
        if w and w in allowed and w != author.lower():
            return True, f"skipped: code owner {who} applied the {EXEMPT_LABEL} label"
        why = ("a code owner cannot exempt their own PR" if w and w == author.lower() and w in allowed
               else f"only a code owner of this repository can add it (added by {who or 'unknown'})")
        return False, (f"the {EXEMPT_LABEL} label does not count: {why}. Fill in the Documentation "
                       f"section, or ask another code owner to add the label.")

    text = (body or "").replace("\r\n", "\n")
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)  # template hints do not count
    m = re.search(r"^#{2,3}[ \t]*Documentation[ \t]*:?[ \t]*\n(.*?)(?=^#{1,3}[ \t]|\Z)",
                  text, flags=re.M | re.S | re.I)
    if not m:
        return False, ('the PR description has no "## Documentation" section. Add one listing each '
                       'document updated, or "None:" and why no document describes this change.')
    section = m.group(1).strip()
    if not section:
        return False, ('the "## Documentation" section is empty. List each document updated (ITSD, '
                       'partner, GitOps, README, CLAUDE.md, or the linked docs PR), or write "None:" '
                       'and why no document describes this change.')
    plain = re.sub(r"[\s*_`>#\-\[\]]+", " ", section).strip()
    none = re.match(r"(none|n/?a|nothing|no docs?|not applicable)\b[\s:.,;-]*(.*)", plain, flags=re.I | re.S)
    if none and len(none.group(2).strip()) < MIN_REASON:
        return False, ('the "## Documentation" section says None without a reason. Write why no '
                       'document describes this change, e.g. "None: test-only change, no behaviour '
                       'changes".')
    return True, "Documentation section present"


def current_pr(repo: str, number: str, token: str) -> dict:
    """The PR as it is now. A ruleset-required workflow runs only on opened/synchronize/reopened,
    and a re-run replays the original event, so the event payload can hold a stale description."""
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/pulls/{number}",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def main() -> int:
    env = os.environ
    repo, number, token = env.get("GITHUB_REPOSITORY"), env.get("PR_NUMBER"), env.get("GITHUB_TOKEN")
    if repo and number and token:
        pr = current_pr(repo, number, token)
        body, author = pr.get("body") or "", pr["user"]["login"]
        author_type = pr["user"].get("type", "")
        labels = [l["name"] for l in pr.get("labels", [])]
        base = (pr.get("base") or {}).get("ref") or "HEAD"
    else:  # local runs without a token: use the event values
        body, author, author_type = env.get("PR_BODY", ""), env.get("PR_AUTHOR", ""), env.get("PR_AUTHOR_TYPE", "")
        labels = [l.strip() for l in env.get("PR_LABELS", "").split(",") if l.strip()]
        base = "HEAD"
    ok, message = check(body, author, author_type, labels,
                        lambda: last_labeler(repo, number, token, EXEMPT_LABEL),
                        lambda: code_owners(repo, base, token))
    if ok:
        print(f"OK: {message}")
        return 0
    print(f"::error title=Documentation section::{message} After editing the description, "
          "re-run this check (Re-run jobs) or push a commit: edits alone do not start it.")
    print("Rule: https://github.com/Capacity-LLC/.github/blob/main/CONTRIBUTING.md")
    return 1


if __name__ == "__main__":
    sys.exit(main())
