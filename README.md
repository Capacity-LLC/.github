# Capacity-LLC/.github

Organisation-wide defaults for Capacity-LLC repositories.

- `CONTRIBUTING.md`: the rules every repository follows, including "every change updates the
  documentation, in the same PR".
- `pull_request_template.md`: the default PR template for any repository without its own.
- `.github/workflows/docs-section.yml`: the **docs section** check. The organisation ruleset
  "docs section required" runs it on every repository's default branch.
- `scripts/check_docs_section.py` and its tests (`scripts/test_check_docs_section.py`, run by
  `.github/workflows/test.yml`).

This repository is public because GitHub applies an organisation's default community health files
only from a public `.github` repository. Keep anything internal out of it.
