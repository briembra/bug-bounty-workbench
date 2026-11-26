#!/usr/bin/env python3
"""Diff two scope snapshots. A new asset is almost always untested.

usage:
    python tools/scope_diff.py scope-old.json scope-new.json

Prints added and removed assets per type. Standard library only.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

TYPES = ("wildcards", "hosts", "urls", "mobile", "ips", "excluded")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Diff two scope.json snapshots")
    ap.add_argument("old", help="older scope.json")
    ap.add_argument("new", help="newer scope.json")
    args = ap.parse_args(argv)

    try:
        old = load(Path(args.old))
        new = load(Path(args.new))
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 2

    any_change = False
    for kind in TYPES:
        before = set(old.get(kind) or [])
        after = set(new.get(kind) or [])
        added = sorted(after - before)
        removed = sorted(before - after)
        if not added and not removed:
            continue
        any_change = True
        print(f"\n{kind}:")
        for item in added:
            print(f"  + {item}")
        for item in removed:
            print(f"  - {item}")

    if not any_change:
        print("no changes")
    else:
        print("\nnext: the added assets are the freshest surface — map them first.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
