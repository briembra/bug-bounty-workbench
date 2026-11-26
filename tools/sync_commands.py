#!/usr/bin/env python3
"""Copy the 25 command files into an agent's command directory.

The commands live once, in `commands/`. Every agent wants them somewhere else
under a slightly different name. This copies them, converts the frontmatter key
where the agent expects a different one, and writes an index so the agent sees
the list.

Usage:
    python tools/sync_commands.py --target opencode
    python tools/sync_commands.py --target claude
    python tools/sync_commands.py --target cursor --dir .cursor/commands
    python tools/sync_commands.py --dir /some/commands/dir

Targets and their defaults (relative to the repo root unless absolute):
    opencode   .opencode/command
    claude     .claude/commands
    cursor     .cursor/commands
    codex      .codex/prompts

Standard library only. Idempotent: re-running overwrites the same files and
leaves anything else in the directory alone.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SOURCE = REPO / "commands"

TARGETS = {
    "opencode": ".opencode/command",
    "claude": ".claude/commands",
    "cursor": ".cursor/commands",
    "codex": ".codex/prompts",
}

# Frontmatter keys some agents do not define. Claude Code understands both;
# OpenCode, Codex and Cursor only document `description`, so the hint and the
# tool list are dropped. The same information is in the body of every file.
DROP_KEYS = {"allowed-tools", "argument-hint"}

FRONT = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)


def rewrite(text: str, target: str) -> str:
    """Trim frontmatter keys the target agent does not define."""
    if target == "claude":
        return text
    match = FRONT.match(text)
    if not match:
        return text
    kept = []
    for line in match.group(1).splitlines():
        key = line.split(":", 1)[0].strip()
        if key in DROP_KEYS:
            continue
        kept.append(line)
    body = text[match.end():]
    return "---\n" + "\n".join(kept) + "\n---\n" + body


def main() -> int:
    ap = argparse.ArgumentParser(description="Install the commands into an agent.")
    ap.add_argument("--target", choices=sorted(TARGETS), help="agent to install for")
    ap.add_argument("--dir", help="explicit destination directory (overrides target)")
    ap.add_argument("--dry-run", action="store_true", help="list, do not write")
    args = ap.parse_args()

    if not args.dir and not args.target:
        ap.error("give --target or --dir")

    destination = Path(args.dir) if args.dir else REPO / TARGETS[args.target]
    if not destination.is_absolute():
        destination = REPO / destination

    if not SOURCE.is_dir():
        print(f"no commands directory at {SOURCE}", file=sys.stderr)
        return 1

    files = sorted(p for p in SOURCE.glob("*.md") if p.name != "README.md")
    if not files:
        print("no command files found", file=sys.stderr)
        return 1

    if args.dry_run:
        print(f"would copy {len(files)} commands to {destination}")
        for path in files:
            print(f"  {path.name}")
        return 0

    destination.mkdir(parents=True, exist_ok=True)
    for path in files:
        text = rewrite(path.read_text(encoding="utf-8"), args.target or "")
        (destination / path.name).write_text(text, encoding="utf-8", newline="\n")

    print(f"copied {len(files)} commands to {destination}")
    print("index: " + ", ".join("/" + p.stem for p in files))

    skill_source = REPO / "SKILL.md"
    if skill_source.exists() and args.target in {"claude", "opencode"}:
        skill_dir = (
            REPO / ".claude/skills/bug-bounty-workbench"
            if args.target == "claude"
            else REPO / ".opencode/skill/bug-bounty-workbench"
        )
        # The skill is the router plus everything it links to, so relative links
        # inside SKILL.md keep resolving after the copy.
        bundled = [
            "SKILL.md",
            "AGENTS.md",
            "PROMPT.md",
            "INSTALL.md",
            "README.md",
            "CONTRIBUTING.md",
            "DISCLAIMER.md",
            "LICENSE",
            "references",
            "workflows",
            "checklists",
            "templates",
            "prompts",
            "data",
            "commands",
        ]
        for name in bundled:
            source = REPO / name
            destination_path = skill_dir / name
            if source.is_dir():
                if destination_path.exists():
                    shutil.rmtree(destination_path)
                shutil.copytree(source, destination_path)
            elif source.is_file():
                skill_dir.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination_path)
        print(f"skill: {skill_dir / 'SKILL.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
