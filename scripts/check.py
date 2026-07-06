#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []

required = [
    "README.md", "LICENSE", "SECURITY.md", "CONTRIBUTING.md", "CHANGELOG.md",
    "CODE_OF_CONDUCT.md", "SUPPORT.md", "AGENTS.md", "Makefile", "assets/hero.svg"
]
for rel in required:
    if not (ROOT / rel).exists():
        errors.append(f"missing required file: {rel}")

for path in sorted((ROOT / "docs").glob("*.md")):
    text = path.read_text(encoding="utf-8")
    if path.name not in {"architecture.md", "repo-complete.md"} and "## Bronnen" not in text:
        errors.append(f"missing ## Bronnen: {path.relative_to(ROOT)}")
    if "TODO" in text or "TBD" in text:
        errors.append(f"placeholder marker in {path.relative_to(ROOT)}")

private_patterns = [
    r"Herendam\s*137", r"Patershof", r"Anne\s+Meesters", r"Duco", r"\bBSN\b",
    r"BEGIN (RSA|OPENSSH|PRIVATE) KEY", r"gho_[A-Za-z0-9_]+", r"xox[baprs]-",
]
for path in ROOT.rglob("*"):
    if path.relative_to(ROOT).as_posix() == "scripts/check.py":
        continue
    if path.is_file() and ".git" not in path.parts:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pat in private_patterns:
            if re.search(pat, text, re.IGNORECASE):
                errors.append(f"privacy/sensitive pattern {pat!r} in {path.relative_to(ROOT)}")

for path in sorted(list((ROOT / "prompts").glob("*.md")) + list((ROOT / "examples").glob("*.md"))):
    if not path.read_text(encoding="utf-8").strip().startswith("# "):
        errors.append(f"missing title heading: {path.relative_to(ROOT)}")

if errors:
    print("CHECK FAILED")
    for err in errors:
        print(f"- {err}")
    sys.exit(1)
print("CHECK OK")
print("docs", len(list((ROOT / "docs").glob("*.md"))))
print("prompts", len(list((ROOT / "prompts").glob("*.md"))))
print("examples", len(list((ROOT / "examples").glob("*.md"))))
