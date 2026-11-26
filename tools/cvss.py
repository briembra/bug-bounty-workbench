#!/usr/bin/env python3
"""CVSS 3.1 base score calculator.

usage:
    python tools/cvss.py "AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N"
    python tools/cvss.py --interactive

Prints the score, the rating band, and a one-line justification.
Standard library only.
"""
from __future__ import annotations

import argparse
import math
import sys

AV = {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.20}
AC = {"L": 0.77, "H": 0.44}
PR_U = {"N": 0.85, "L": 0.62, "H": 0.27}
PR_C = {"N": 0.85, "L": 0.68, "H": 0.50}
UI = {"N": 0.85, "R": 0.62}
CIA = {"H": 0.56, "L": 0.22, "N": 0.00}

BANDS = (
    (9.0, "Critical"),
    (7.0, "High"),
    (4.0, "Medium"),
    (0.1, "Low"),
    (0.0, "None"),
)


def _roundup(value: float) -> float:
    # CVSS 3.1 "Roundup": smallest 1-decimal number >= value.
    # Round to 6 dp first so float error (e.g. 4.000000001) does not bump up.
    return math.ceil(round(value * 10, 6)) / 10.0


def parse_vector(vector: str) -> dict:
    parts = {}
    for token in vector.strip().split("/"):
        if ":" not in token:
            raise ValueError(f"bad metric: {token!r}")
        key, val = token.split(":", 1)
        parts[key.strip().upper()] = val.strip().upper()
    required = {"AV", "AC", "PR", "UI", "S", "C", "I", "A"}
    missing = required - set(parts)
    if missing:
        raise ValueError(f"missing metrics: {', '.join(sorted(missing))}")
    return parts


def validate(p: dict) -> None:
    checks = {
        "AV": "NALP",
        "AC": "LH",
        "PR": "NLH",
        "UI": "NR",
        "S": "UC",
        "C": "HLN",
        "I": "HLN",
        "A": "HLN",
    }
    for key, allowed in checks.items():
        if p[key] not in allowed:
            raise ValueError(f"{key} must be one of {allowed}, got {p[key]!r}")


def score(vector: str) -> tuple[float, str, dict]:
    p = parse_vector(vector)
    validate(p)

    changed = p["S"] == "C"
    pr = (PR_C if changed else PR_U)[p["PR"]]

    iss = 1 - (
        (1 - CIA[p["C"]]) * (1 - CIA[p["I"]]) * (1 - CIA[p["A"]])
    )
    if changed:
        impact = 7.52 * (iss - 0.029) - 3.25 * (iss - 0.02) ** 15
    else:
        impact = 6.42 * iss

    exploitability = 8.22 * AV[p["AV"]] * AC[p["AC"]] * pr * UI[p["UI"]]

    if impact <= 0:
        base = 0.0
    elif changed:
        base = _roundup(min(1.08 * (impact + exploitability), 10.0))
    else:
        base = _roundup(min(impact + exploitability, 10.0))

    band = next(name for floor, name in BANDS if base >= floor)
    return base, band, p


def justification(p: dict) -> str:
    who = {"N": "an unauthenticated attacker", "L": "any authenticated user",
           "H": "an authenticated admin"}[p["PR"]]
    what = []
    if p["C"] == "H":
        what.append("read sensitive data")
    elif p["C"] == "L":
        what.append("read limited data")
    if p["I"] == "H":
        what.append("modify any data")
    elif p["I"] == "L":
        what.append("modify limited data")
    if p["A"] == "H":
        what.append("deny service")
    elif p["A"] == "L":
        what.append("degrade service")
    if not what:
        what.append("gain no measurable impact")
    scope = " across a security boundary" if p["S"] == "C" else ""
    interact = (" with victim interaction" if p["UI"] == "R" else " without interaction")
    return f"{who} can {' and '.join(what)}{scope}{interact}."


def interactive() -> str:
    print("CVSS 3.1 base score — answer each metric.")
    prompts = [
        ("AV", "Attack Vector [N]etwork/[A]djacent/[L]ocal/[P]hysical", "N"),
        ("AC", "Attack Complexity [L]ow/[H]igh", "L"),
        ("PR", "Privileges Required [N]one/[L]ow/[H]igh", "N"),
        ("UI", "User Interaction [N]one/[R]equired", "N"),
        ("S", "Scope [U]nchanged/[C]hanged", "U"),
        ("C", "Confidentiality [H]igh/[L]ow/[N]one", "N"),
        ("I", "Integrity [H]igh/[L]ow/[N]one", "N"),
        ("A", "Availability [H]igh/[L]ow/[N]one", "N"),
    ]
    parts = []
    for key, label, default in prompts:
        raw = input(f"{label} [{default}]: ").strip().upper() or default
        parts.append(f"{key}:{raw}")
    return "/".join(parts)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="CVSS 3.1 base score calculator")
    ap.add_argument("vector", nargs="?", help="CVSS 3.1 base vector")
    ap.add_argument("--interactive", action="store_true", help="prompt for metrics")
    args = ap.parse_args(argv)

    vector = args.vector
    if args.interactive or not vector:
        vector = interactive()

    try:
        value, band, parsed = score(vector)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(f"vector:  {vector}")
    print(f"score:   {value}")
    print(f"rating:  {band}")
    print(f"impact:  {justification(parsed)}")
    if value >= 7.0:
        print("note:    confirm every H metric with captured evidence before submitting.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
