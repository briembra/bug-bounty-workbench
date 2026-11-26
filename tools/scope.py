#!/usr/bin/env python3
"""Normalise a bug bounty program's scope into one JSON file.

usage:
    python tools/scope.py --file scope.txt -o scope.json
    python tools/scope.py --platform intigriti --program <handle> -o scope.json

Parses a pasted/exported scope list into typed assets: wildcards, hosts, urls,
mobile, ips, excluded, rules_notes. Standard library only.

Notes:
- The platform API is used only where it is public. If it is unavailable, paste
  the scope text into a file and use --file.
- Everything you later touch must appear in the output. If it is not there, it
  does not exist for you.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

IPV4_CIDR = re.compile(r"^\d{1,3}(\.\d{1,3}){3}(/\d{1,2})?$")
HOST = re.compile(r"^(?=.{1,253}$)([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}$", re.I)
MOBILE = re.compile(r"^(com|org|net|io|dev|co)\.[a-z0-9_]+\.[a-z0-9_.]+$", re.I)

UA = "Mozilla/5.0 (compatible; bbh-scope/1.0)"


def classify(token: str) -> tuple[str, str] | None:
    t = token.strip().strip(",;").strip()
    if not t or t.startswith("#"):
        return None
    t = t.strip("'\"`")

    if t.startswith(("http://", "https://")):
        return "urls", t
    if t.startswith("*."):
        return "wildcards", t.lower()
    if IPV4_CIDR.match(t):
        return "ips", t
    if MOBILE.match(t) and t.count(".") == 2:
        return "mobile", t
    if HOST.match(t):
        return "hosts", t.lower()
    return None


def parse_text(text: str) -> dict:
    out = {
        "program": None,
        "platform": None,
        "wildcards": [],
        "hosts": [],
        "urls": [],
        "mobile": [],
        "ips": [],
        "excluded": [],
        "rules_notes": [],
    }
    in_excluded = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        low = line.lower()
        if low.startswith(("excluded", "out of scope", "out-of-scope", "not in scope")):
            in_excluded = True
            continue
        if low.startswith(("in scope", "scope:")):
            in_excluded = False
            continue
        if low.startswith(("rule", "note", "prohibited", "allowed")):
            out["rules_notes"].append(line)
            continue

        # a line may contain a label then a token: "Web app - app.example.com"
        candidates = re.split(r"[\s,|]+", line)
        for cand in candidates:
            parsed = classify(cand)
            if not parsed:
                continue
            kind, value = parsed
            bucket = "excluded" if in_excluded else kind
            if value not in out[bucket]:
                out[bucket].append(value)
    return out


def fetch_intigriti(handle: str) -> str:
    """Fetch the public program page and return visible text for asset parsing."""
    url = f"https://app.intigriti.com/programs/{handle}/detail"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8", "replace")
    # strip tags, keep asset-looking tokens
    text = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "\n", text)
    return text


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Normalise program scope into JSON")
    ap.add_argument("--file", help="scope text file to parse")
    ap.add_argument("--format", default="text", choices=["text"], help="input format")
    ap.add_argument("--platform", choices=["intigriti", "hackerone"], help="platform to query")
    ap.add_argument("--program", "--handle", dest="program", help="program handle")
    ap.add_argument("-o", "--output", default="scope.json", help="output path")
    args = ap.parse_args(argv)

    if args.file:
        text = Path(args.file).read_text(encoding="utf-8", errors="replace")
    elif args.platform and args.program:
        if args.platform != "intigriti":
            print(f"error: {args.platform} scope API is not public; use --file", file=sys.stderr)
            return 2
        try:
            text = fetch_intigriti(args.program)
        except Exception as exc:  # noqa: BLE001
            print(f"error: could not fetch program page: {exc}", file=sys.stderr)
            print("hint: paste the scope text into a file and use --file", file=sys.stderr)
            return 2
    else:
        ap.error("provide --file or --platform with --program")

    scope = parse_text(text)
    scope["program"] = args.program
    scope["platform"] = args.platform

    total = sum(len(scope[k]) for k in ("wildcards", "hosts", "urls", "mobile", "ips"))
    if total == 0:
        print("error: no assets parsed — check the input text", file=sys.stderr)
        return 1

    Path(args.output).write_text(json.dumps(scope, indent=2), encoding="utf-8")
    print(f"wrote {args.output}")
    print(f"  wildcards: {len(scope['wildcards'])}")
    print(f"  hosts:     {len(scope['hosts'])}")
    print(f"  urls:      {len(scope['urls'])}")
    print(f"  mobile:    {len(scope['mobile'])}")
    print(f"  ips:       {len(scope['ips'])}")
    print(f"  excluded:  {len(scope['excluded'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
