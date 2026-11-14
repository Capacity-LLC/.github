import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from check_docs_section import check

H = "<!-- hint: list docs or None: and why -->"
cases = [
    # (name, body, author, type, labels, expected)
    ("missing section", "## What and why\nfix\n## How it was tested\nran it", "dev", "User", [], False),
    ("empty section (only hint)", f"## What and why\nx\n## Documentation\n{H}\n\n## Manual deployment steps\nNone", "dev", "User", [], False),
    ("bare None", "## Documentation\nNone\n## Manual deployment steps\nNone", "dev", "User", [], False),
    ("None with short reason", "## Documentation\nNone: n/a\n", "dev", "User", [], False),
    ("bare N/A bold", "## Documentation\n**N/A**\n", "dev", "User", [], False),
    ("None with reason", "## Documentation\nNone: test-only change, no behaviour changes\n## Manual deployment steps\nNone", "dev", "User", [], True),
    ("lists docs", f"## Documentation\n{H}\n- docs/itsd_documentation/05-x/page.md updated\n- partner docs: errors.md\n", "dev", "User", [], True),
    ("last section, CRLF", "## What\r\nx\r\n## Documentation\r\n- GitOps docs/argocd/README.md\r\n", "dev", "User", [], True),
    ("h3 heading", "### Documentation\n- README.md\n", "dev", "User", [], True),
    ("bot skipped", "release notes only", "capacity-release-bot[bot]", "Bot", [], True),
    ("dependabot skipped", "", "dependabot[bot]", "Bot", [], True),
    ("label exempt by approver", "no section", "dev", "User", ["bug", "docs-exempt"], True, "rbhocap"),
    ("label added by author", "no section", "dev", "User", ["docs-exempt"], False, "dev"),
    ("label adder unknown", "no section", "dev", "User", ["docs-exempt"], False, None),
    ("Manual steps None does not satisfy", "## Manual deployment steps\nNone\n", "dev", "User", [], False),
]
bad = 0
for name, body, author, typ, labels, want, *adder in cases:
    who = adder[0] if adder else None
    got, msg = check(body, author, typ, labels, lambda: who)
    flag = "PASS" if got == want else "FAIL"
    bad += got != want
    print(f"{flag}  {name:40} -> {got} ({msg[:70]})")
print("all good" if not bad else f"{bad} wrong")
sys.exit(bad)
