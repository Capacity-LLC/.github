#!/usr/bin/env python3
"""Fails a pull request whose "## Documentation" section is missing, empty or a bare "None".

Rule (every Capacity-LLC repository, people and Claude Code alike): every change updates the
documents that describe it - ITSD docs, partner docs, GitOps docs, READMEs, CLAUDE.md - in the same
PR or in a linked PR that merges with it. The PR says which, or "None:" and why.

Reads PR_BODY, PR_AUTHOR, PR_AUTHOR_TYPE and PR_LABELS (comma-separated) from the environment.
"""
import os
import re
import sys

EXEMPT_LABEL = "docs-exempt"
MIN_REASON = 15  # characters of explanation after "None"


def check(body: str, author: str, author_type: str, labels: list[str]) -> tuple[bool, str]:
    if author_type == "Bot" or author.endswith("[bot]"):
        return True, f"skipped: opened by a bot ({author})"
    if EXEMPT_LABEL in labels:
        return True, f"skipped: a reviewer applied the {EXEMPT_LABEL} label"

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


def main() -> int:
    labels = [l.strip() for l in os.environ.get("PR_LABELS", "").split(",") if l.strip()]
    ok, message = check(os.environ.get("PR_BODY", ""), os.environ.get("PR_AUTHOR", ""),
                        os.environ.get("PR_AUTHOR_TYPE", ""), labels)
    if ok:
        print(f"OK: {message}")
        return 0
    print(f"::error title=Documentation section::{message}")
    print("Rule: https://github.com/Capacity-LLC/.github/blob/main/CONTRIBUTING.md")
    return 1


if __name__ == "__main__":
    sys.exit(main())
