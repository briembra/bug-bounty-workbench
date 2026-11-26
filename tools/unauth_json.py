#!/usr/bin/env python3
"""Look for unauthenticated JSON collections on alive hosts.

usage:
    python tools/unauth_json.py alive.json -o collections.json
    python tools/unauth_json.py alive.json --cap 200 --threads 10

GETs a bounded path list per host and records any 200 that returns a JSON array
or object with records. Reports count and field names only — never the data.
Standard library only.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

PATHS = [
    "/api/users", "/api/v1/users", "/api/v2/users", "/api/user",
    "/api/accounts", "/api/v1/accounts", "/api/customers", "/api/v1/customers",
    "/rest/users", "/rest/api/users", "/users.json", "/accounts.json",
    "/wp-json/wp/v2/users", "/api/orders", "/api/v1/orders",
    "/api/products", "/api/v1/products", "/api/items", "/api/v1/items",
    "/api/config", "/api/settings", "/api/health", "/api/status",
    "/graphql?query=%7B__typename%7D",
]

_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE


def get_json(url: str, timeout: float) -> tuple[int, object] | None:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_ssl_ctx) as resp:
            raw = resp.read(400_000)
            if "json" not in resp.headers.get("Content-Type", ""):
                return None
            return resp.status, json.loads(raw.decode("utf-8", "replace"))
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403, 404):
            return None
        return None
    except Exception:  # noqa: BLE001
        return None


def shape(value: object) -> tuple[int, list[str]]:
    """Return (record count, field names) without exposing values."""
    if isinstance(value, list):
        count = len(value)
        fields = sorted({k for row in value if isinstance(row, dict) for k in row})
        return count, fields
    if isinstance(value, dict):
        # common envelopes
        for key in ("data", "items", "results", "rows", "records"):
            inner = value.get(key)
            if isinstance(inner, list):
                fields = sorted({k for row in inner if isinstance(row, dict) for k in row})
                return len(inner), fields
        return 1, sorted(value.keys())
    return 0, []


def check(host: dict, timeout: float) -> list[dict]:
    base = f"https://{host['host']}"
    hits = []
    for path in PATHS:
        got = get_json(base + path, timeout)
        if not got:
            continue
        status, value = got
        count, fields = shape(value)
        if count == 0:
            continue
        hits.append({
            "host": host["host"],
            "path": path,
            "url": base + path,
            "status": status,
            "records": count,
            "fields": fields[:30],
        })
    return hits


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Find unauthenticated JSON collections")
    ap.add_argument("alive", help="alive.json from tools/probe.py")
    ap.add_argument("-o", "--output", default="collections.json")
    ap.add_argument("--threads", type=int, default=10)
    ap.add_argument("--timeout", type=float, default=10.0)
    ap.add_argument("--cap", type=int, default=250)
    args = ap.parse_args(argv)

    data = json.loads(Path(args.alive).read_text(encoding="utf-8"))
    hosts = (data.get("hosts") or [])[: args.cap]
    if not hosts:
        print("error: no hosts", file=sys.stderr)
        return 2

    print(f"checking {len(hosts)} hosts x {len(PATHS)} paths")
    hits: list[dict] = []
    with cf.ThreadPoolExecutor(max_workers=args.threads) as pool:
        futures = [pool.submit(check, h, args.timeout) for h in hosts]
        for fut in cf.as_completed(futures):
            try:
                hits.extend(fut.result())
            except Exception:  # noqa: BLE001
                continue

    Path(args.output).write_text(json.dumps({"count": len(hits), "hits": hits}, indent=2),
                                encoding="utf-8")
    print(f"wrote {args.output}: {len(hits)} collections")
    for h in hits[:30]:
        print(f"  {h['records']:>4} records  {h['url']}  fields={h['fields'][:6]}")
    if hits:
        print("next: confirm ONE record belongs to a real user, redact, stop.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
