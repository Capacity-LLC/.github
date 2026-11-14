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
description; the check re-runs on the edit.

- PRs opened by bots (the release bot, Dependabot) are skipped.
- The `docs-exempt` label skips the check when the rule genuinely does not fit. Like the other
  exemption labels, it counts only when `rbhocap` adds it; added by anyone else, the check fails.
