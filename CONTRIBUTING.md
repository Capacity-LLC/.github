# Contributing to Capacity-LLC repositories

These rules apply to every repository in the Capacity-LLC organisation, including repositories
created later, and to everyone who changes them: people and AI coding assistants (Claude Code)
alike. A repository may add its own rules in its `CLAUDE.md`, README or PR template; it may not
drop these.

## Every change updates the documentation, in the same PR

When you change code, configuration, SQL, manifests or workflows, update every document that
describes the changed behaviour, in the same pull request. Where a document lives in another
repository, open a PR there, link the two, and merge them together.

Where the documents live:

| Documents | Location | What belongs there |
|---|---|---|
| ITSD docs | Capacity repo, `docs/itsd_documentation` | Application behaviour, business processes, servers, jobs, application runbooks |
| Partner docs | Capacity repo, `src/Capacity.Portal.PartnerApi` | Anything a partner sees: endpoints, fields, errors, authentication, webhooks, limits, the OpenAPI contract |
| GitOps docs | Capacity.GitOps repo, `docs/` | Deployment, clusters, Argo CD, observability, infrastructure runbooks |
| Everything else | READMEs, `CLAUDE.md` files, a repo's own `docs/`, comments that state behaviour | Whatever describes the thing you changed |

Before calling a change done, search all of these for the old names, paths and values you changed.

## The Documentation section of every pull request

Every PR description has a `## Documentation` section that lists each document updated (or the
linked docs PR), or says `None:` followed by why no document describes this change, for example
`None: test-only change, no behaviour changes`.

The **docs section** check runs on every PR in every repository (organisation ruleset "docs section
required") and fails when the section is missing, empty, or a bare "None". Fix it by editing the PR
description, then re-run the failed check (**Re-run jobs** on the check) or push a commit. Editing
the description or adding a label does not start the check by itself: GitHub runs an
organisation-required workflow only when a PR is opened, reopened or gets new commits. The check
reads the PR's current description and labels, so a re-run sees your edit.

- PRs opened by bots (the release bot, Dependabot) are skipped.
- **No docs needed:** a code owner (anyone named in the repository's `CODEOWNERS`) adds the
  `docs-exempt` label, then re-runs the check. It does not count when the code owner is the PR's
  author (rbhocap excepted), or when anyone else adds it. Repositories without a `CODEOWNERS` file:
  only `rbhocap`. Writing `None:` and the reason in the section works too and needs nobody else.
- **Merging past the check:** organisation admins can still merge a PR whose check fails (the
  ruleset lets them bypass it; GitHub shows "Merge without waiting for requirements"). Use it when
  the check is in the way, not as the usual route.
