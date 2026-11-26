"""Verify that every relative markdown link in the repo resolves to a file."""
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
bad = []
count = 0

for md in root.rglob("*.md"):
    text = md.read_text(encoding="utf-8", errors="replace")
    for target in LINK.findall(text):
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        path_part = target.split("#", 1)[0]
        if not path_part:
            continue
        count += 1
        resolved = (md.parent / path_part).resolve()
        if not resolved.exists():
            bad.append(f"{md.relative_to(root)} -> {target}")

print(f"checked {count} relative links")
if bad:
    print(f"BROKEN ({len(bad)}):")
    for item in bad:
        print(" ", item)
    sys.exit(1)
print("all links resolve")
