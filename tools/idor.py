#!/usr/bin/env python3
"""Diff two saved request/response pairs to document a BOLA/IDOR.

usage:
    python tools/idor.py --a a.json --b b.json

Input shape:
    {"request": {"method":"GET","url":"...","headers":{},"body":""},
     "response": {"status":200,"headers":{},"body":"..."}}

Tells you whether B's response appears to contain A's data (or vice versa),
which field names are shared, and whether the two responses are distinct.
Standard library only.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if "response" not in data:
        raise ValueError(f"{path}: missing 'response'")
    return data


def body_of(entry: dict) -> str:
    body = (entry.get("response") or {}).get("body", "")
    return body if isinstance(body, str) else json.dumps(body)


def status_of(entry: dict) -> int | None:
    return (entry.get("response") or {}).get("status")


def fields(body: str) -> set[str]:
    try:
        data = json.loads(body)
    except Exception:  # noqa: BLE001
        return set()
    keys: set[str] = set()

    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                keys.add(k)
                walk(v)
        elif isinstance(node, list):
            for item in node[:5]:
                walk(item)

    walk(data)
    return keys


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Diff two request/response pairs for BOLA")
    ap.add_argument("--a", required=True, help="account A's capture (attacker session, victim object)")
    ap.add_argument("--b", required=True, help="account B's capture (victim creating/owning the object)")
    args = ap.parse_args(argv)

    try:
        a = load(Path(args.a))
        b = load(Path(args.b))
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 2

    a_body, b_body = body_of(a), body_of(b)
    a_status, b_status = status_of(a), status_of(b)

    print(f"A: {a_status}  {(a.get('request') or {}).get('url','?')}")
    print(f"B: {b_status}  {(b.get('request') or {}).get('url','?')}")

    if a_body.strip() == b_body.strip():
        print("\nidentical bodies — A received the same response as B")
        print("this is the BOLA signature IF the object belongs to B and A is a different user")
    else:
        print("\ndifferent bodies")

    shared = fields(a_body) & fields(b_body)
    if shared:
        print(f"\nshared field names ({len(shared)}): {', '.join(sorted(shared)[:25])}")
    else:
        print("\nno shared JSON field names (check that both bodies are JSON)")

    print("\nchecklist:")
    print("  [ ] A's session differs from B's")
    print("  [ ] the object id in A's URL is B's")
    print("  [ ] the returned data is sensitive (PII/payment), not public")
    print("  [ ] you did not use a real user's object")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
