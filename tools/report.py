#!/usr/bin/env python3
"""Build a bug bounty report from a structured finding file.

usage:
    python tools/report.py finding.yaml -o report.md
    python tools/report.py finding.yaml --dry-run

Accepts JSON or a small YAML subset (key: value, "- " lists, "|" block scalars).
Validates required fields before writing. Standard library only.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED = ("title", "severity", "asset", "summary", "steps", "impact", "remediation")


def parse_simple_yaml(text: str) -> dict:
    """Parse a YAML subset: scalars, lists of scalars, and '|' block scalars."""
    data: dict = {}
    key = None
    mode = None  # "block" or "list"
    block: list[str] = []
    base_indent = None

    def flush():
        nonlocal key, mode, block, base_indent
        if key is None:
            return
        if mode == "block":
            data[key] = "\n".join(block).strip("\n")
        elif mode == "list":
            data[key] = [b.strip().strip("\"'") for b in block if b.strip()]
        key, mode, block, base_indent = None, None, [], None

    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        line = raw.rstrip()
        indent = len(line) - len(line.lstrip())

        if indent == 0 and ":" in line:
            flush()
            k, _, rest = line.partition(":")
            key = k.strip()
            rest = rest.strip()
            if rest in ("|", ">"):
                mode = "block"
            elif rest == "":
                mode = None  # might become a list
            else:
                data[key] = rest.strip("\"'")
                key = None
        elif line.lstrip().startswith("- "):
            mode = "list" if mode != "block" else mode
            block.append(line.lstrip()[2:])
        elif indent > 0 and key and mode == "block":
            if base_indent is None:
                base_indent = indent
            block.append(line[base_indent:] if indent >= base_indent else line.lstrip())
        elif indent > 0 and key:
            # continuation of a folded scalar
            if base_indent is None:
                base_indent = indent
            block.append(line[base_indent:] if indent >= base_indent else line.strip())
            mode = "block"
    flush()
    return data


def load(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return parse_simple_yaml(text)


def render(f: dict) -> str:
    steps = f.get("steps") or []
    if isinstance(steps, str):
        steps = [s.strip() for s in steps.splitlines() if s.strip()]
    numbered = "\n".join(f"{i}. {s}" for i, s in enumerate(steps, 1))

    evidence = f.get("evidence") or []
    if isinstance(evidence, str):
        evidence = [evidence]
    evidence_md = "\n".join(f"- `{e}`" for e in evidence) if evidence else "- (attach request/response pairs)"

    cvss = f.get("cvss", "")
    cwe = f.get("cwe", "")
    meta_parts = []
    if cvss:
        meta_parts.append(f"CVSS `{cvss}`")
    if cwe:
        meta_parts.append(cwe)
    meta = " · ".join(meta_parts)

    parts = [
        f"# {f['title']}",
        "",
        f"**Severity:** {f['severity']}",
    ]
    if meta:
        parts.append(f"**Scoring:** {meta}")
    parts += [
        f"**Asset:** `{f['asset']}`",
        "",
        "## Summary",
        "",
        str(f["summary"]).strip(),
        "",
        "## Steps to reproduce",
        "",
        numbered,
        "",
        "## Evidence",
        "",
        evidence_md,
        "",
        "## Impact",
        "",
        str(f["impact"]).strip(),
        "",
        "## Remediation",
        "",
        str(f["remediation"]).strip(),
        "",
    ]
    return "\n".join(parts)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Render a bug bounty report from a finding file")
    ap.add_argument("finding", help="finding.yaml or finding.json")
    ap.add_argument("-o", "--output", help="write report here (default: stdout)")
    ap.add_argument("--dry-run", action="store_true", help="validate only, do not write")
    args = ap.parse_args(argv)

    path = Path(args.finding)
    if not path.exists():
        print(f"error: not found: {path}", file=sys.stderr)
        return 2

    try:
        finding = load(path)
    except Exception as exc:  # noqa: BLE001 - report the parse failure clearly
        print(f"error: cannot parse {path}: {exc}", file=sys.stderr)
        return 2

    missing = [k for k in REQUIRED if not finding.get(k)]
    if missing:
        print("error: missing required fields: " + ", ".join(missing), file=sys.stderr)
        return 2

    if finding["severity"].lower() not in ("critical", "high", "medium", "low", "info"):
        print(f"warning: unusual severity {finding['severity']!r}", file=sys.stderr)

    report = render(finding)

    if args.dry_run:
        print(f"ok: {path} is valid ({len(report)} bytes, {len(finding.get('steps', []))} steps)")
        return 0

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
