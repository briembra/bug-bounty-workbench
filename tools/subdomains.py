#!/usr/bin/env python3
"""Passive-first subdomain enumeration from a scope file.

usage:
    python tools/subdomains.py scope.json -o subs.json
    python tools/subdomains.py scope.json --active-brute --wordlist words.txt -o subs.json

Default: passive only (certificate transparency). No brute force unless asked.
Bounded: caps names per domain and total requests. Standard library only.

Hints:
- crt.sh is the default source; it is free and needs no key.
- For deeper passive coverage, mount subfinder/amass and merge their output with
  --merge-file.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

UA = "Mozilla/5.0 (compatible; bbh-subs/1.0)"
CRT = "https://crt.sh/?q=%25.{domain}&output=json"


def apex(host: str) -> str:
    parts = host.split(".")
    if len(parts) >= 2:
        return ".".join(parts[-2:])
    return host


def crt_lookup(domain: str, timeout: int = 30, retries: int = 3) -> set[str]:
    url = CRT.format(domain=urllib.parse.quote(domain, safe="."))
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8", "replace") or "[]")
            names = set()
            for row in data:
                for name in str(row.get("name_value", "")).splitlines():
                    name = name.strip().lower().lstrip("*.")
                    if name.endswith(domain):
                        names.add(name)
            return names
        except Exception:  # noqa: BLE001 - crt.sh intermittently 502s
            if attempt == retries - 1:
                return set()
            time.sleep(1.5 * (attempt + 1))
    return set()


def brute(domain: str, words: list[str], cap: int) -> set[str]:
    found = set()
    for word in words[:cap]:
        candidate = f"{word.strip().lower()}.{domain}"
        found.add(candidate)  # resolution happens in probe.py
    return found


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Passive-first subdomain enumeration")
    ap.add_argument("scope", help="scope.json from tools/scope.py")
    ap.add_argument("-o", "--output", default="subs.json")
    ap.add_argument("--merge-file", action="append", default=[],
                    help="extra names file to merge (one per line)")
    ap.add_argument("--active-brute", action="store_true",
                    help="add a wordlist brute (opt-in; check program rules)")
    ap.add_argument("--wordlist", help="wordlist for --active-brute")
    ap.add_argument("--brute-cap", type=int, default=5000, help="max words to use")
    ap.add_argument("--max-domains", type=int, default=60, help="cap domains processed")
    args = ap.parse_args(argv)

    scope = json.loads(Path(args.scope).read_text(encoding="utf-8"))
    domains: set[str] = set()

    for w in scope.get("wildcards", []):
        domains.add(w[2:].lower() if w.startswith("*.") else w.lower())
    for h in scope.get("hosts", []):
        domains.add(h.lower())
    for u in scope.get("urls", []):
        host = urllib.parse.urlparse(u).hostname
        if host:
            domains.add(host.lower())

    if not domains:
        print("error: no domains in scope", file=sys.stderr)
        return 2

    domains = sorted(domains)[: args.max_domains]
    print(f"domains: {len(domains)}")

    names: set[str] = set()
    sources: dict[str, int] = {}

    for domain in domains:
        got = crt_lookup(domain)
        sources[domain] = len(got)
        names |= got
        print(f"  crt.sh {domain}: {len(got)}")
        time.sleep(0.5)

    if args.active_brute:
        if not args.wordlist or not Path(args.wordlist).exists():
            print("error: --active-brute needs an existing --wordlist", file=sys.stderr)
            return 2
        words = Path(args.wordlist).read_text(encoding="utf-8", errors="replace").splitlines()
        for domain in domains:
            names |= brute(domain, words, args.brute_cap)
        print(f"  brute added candidates (cap {args.brute_cap}/domain)")

    for extra in args.merge_file:
        p = Path(extra)
        if p.exists():
            names |= {line.strip().lower() for line in p.read_text(encoding="utf-8").splitlines() if line.strip()}

    names = sorted(n for n in names if n and not n.startswith("*"))

    out = {
        "program": scope.get("program"),
        "domains": domains,
        "count": len(names),
        "sources": sources,
        "names": names,
    }
    Path(args.output).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"wrote {args.output}: {len(names)} unique names")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
