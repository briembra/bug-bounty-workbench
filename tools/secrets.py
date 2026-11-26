#!/usr/bin/env python3
"""Scan alive hosts' JavaScript for high-signal secret candidates.

usage:
    python tools/secrets.py alive.json -o secrets.json
    python tools/secrets.py alive.json --cap 100 --js-cap 3

Fetches the page, finds script sources, downloads up to --js-cap bundles per
host, and greps for high-signal patterns. Flags candidates; does NOT test
liveness — you do that manually with one minimal call. Standard library only.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

# (name, regex, confidence). Known-public prefixes are excluded by name below.
PATTERNS = [
    ("aws_access_key", r"AKIA[0-9A-Z]{16}", "likely-live"),
    ("github_pat", r"ghp_[A-Za-z0-9]{36}", "likely-live"),
    ("github_fine_grained", r"github_pat_[A-Za-z0-9_]{82}", "likely-live"),
    ("slack_token", r"xox[baprs]-[A-Za-z0-9-]{10,}", "likely-live"),
    ("stripe_secret", r"sk_live_[A-Za-z0-9]{24,}", "likely-live"),
    ("sendgrid_key", r"SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}", "likely-live"),
    ("google_api_key", r"AIza[0-9A-Za-z_-]{35}", "format-only"),
    ("private_key", r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", "likely-live"),
    ("twilio_sid", r"AC[a-f0-9]{32}", "format-only"),
    ("jwt", r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}", "format-only"),
]

# public-by-design or obvious test fixtures; drop these matches
FALSE_POSITIVES = re.compile(
    r"(AKIAIOSFODNN7EXAMPLE|xxxx+|your[-_]?key|example|placeholder|test[-_]?key)",
    re.I,
)

SCRIPT = re.compile(r"<script[^>]+src=[\"']([^\"']+)[\"']", re.I)

_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE


def fetch(url: str, timeout: float, limit: int = 1_500_000) -> str | None:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_ssl_ctx) as resp:
            return resp.read(limit).decode("utf-8", "replace")
    except Exception:  # noqa: BLE001
        return None


def redact(value: str) -> str:
    if len(value) <= 8:
        return "…"
    return f"{value[:4]}…{value[-4:]}"


def scan_text(text: str, source: str, host: str) -> list[dict]:
    hits = []
    for name, pattern, confidence in PATTERNS:
        for m in re.finditer(pattern, text):
            value = m.group(0)
            if FALSE_POSITIVES.search(value):
                continue
            hits.append({
                "host": host,
                "source": source,
                "pattern": name,
                "match_redacted": redact(value),
                "confidence": confidence,
            })
    return hits


def scan_host(host: dict, timeout: float, js_cap: int) -> list[dict]:
    name = host["host"]
    base = f"https://{name}"
    page = fetch(f"{base}/", timeout)
    if not page:
        return []
    hits = scan_text(page, f"{base}/", name)

    scripts = []
    for src in SCRIPT.findall(page):
        url = urllib.parse.urljoin(f"{base}/", src)
        if url not in scripts:
            scripts.append(url)

    for url in scripts[:js_cap]:
        body = fetch(url, timeout)
        if body:
            hits.extend(scan_text(body, url, name))
    return hits


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Scan JS for secret candidates")
    ap.add_argument("alive", help="alive.json from tools/probe.py")
    ap.add_argument("-o", "--output", default="secrets.json")
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--timeout", type=float, default=15.0)
    ap.add_argument("--cap", type=int, default=150, help="max hosts")
    ap.add_argument("--js-cap", type=int, default=4, help="max scripts per host")
    args = ap.parse_args(argv)

    data = json.loads(Path(args.alive).read_text(encoding="utf-8"))
    hosts = (data.get("hosts") or [])[: args.cap]
    if not hosts:
        print("error: no hosts", file=sys.stderr)
        return 2

    print(f"scanning {len(hosts)} hosts (js-cap {args.js_cap})")
    hits: list[dict] = []
    with cf.ThreadPoolExecutor(max_workers=args.threads) as pool:
        futures = [pool.submit(scan_host, h, args.timeout, args.js_cap) for h in hosts]
        for fut in cf.as_completed(futures):
            try:
                hits.extend(fut.result())
            except Exception:  # noqa: BLE001
                continue

    # dedupe on (host, pattern, redacted)
    seen = set()
    unique = []
    for h in hits:
        key = (h["host"], h["pattern"], h["match_redacted"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(h)

    Path(args.output).write_text(json.dumps({"count": len(unique), "candidates": unique}, indent=2),
                                encoding="utf-8")
    print(f"wrote {args.output}: {len(unique)} candidates")
    for h in unique[:40]:
        print(f"  [{h['confidence']}] {h['pattern']}: {h['match_redacted']}  ({h['host']})")
    if unique:
        print("next: verify liveness with ONE minimal call per candidate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
