#!/usr/bin/env python3
"""Check high-signal exposure paths on alive hosts.

usage:
    python tools/exposure.py alive.json -o exposures.json
    python tools/exposure.py alive.json --paths data/common-paths.txt --cap 300

One GET per path per host, bounded hosts and threads. Reports hits with status
and a short preview. Never writes to the target. Standard library only.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import re
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

DEFAULT_PATHS = [
    ".env", ".git/config", ".git/HEAD", ".gitignore", ".svn/entries",
    ".DS_Store", ".aws/credentials", ".npmrc", ".dockercfg",
    "config.php.bak", "wp-config.php.bak", "config.json", "settings.py",
    "actuator/env", "actuator/heapdump", "actuator/mappings", "actuator/health",
    "server-status", "phpinfo.php", "info.php", "debug.php",
    "backup.zip", "backup.tar.gz", "db.sql", "dump.sql", ".sql",
    "docker-compose.yml", "composer.lock", "package.json",
    "swagger.json", "openapi.json", "graphql", "api-docs",
]

# a hit is "interesting" only if the body does not look like a generic error page
GENERIC = re.compile(
    r"(<!doctype html|<html)[\s\S]{0,200}(404|not found|forbidden|error)",
    re.I,
)

_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE


def get(url: str, timeout: float) -> tuple[int, str, str] | None:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_ssl_ctx) as resp:
            return resp.status, resp.headers.get("Content-Type", ""), resp.read(4096).decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read(4096).decode("utf-8", "replace")
        except Exception:  # noqa: BLE001
            body = ""
        return exc.code, (exc.headers or {}).get("Content-Type", "") if exc.headers else "", body
    except Exception:  # noqa: BLE001
        return None


def check(host: dict, paths: list[str], timeout: float) -> list[dict]:
    base = f"https://{host['host']}"
    hits = []
    for path in paths:
        got = get(f"{base}/{path}", timeout)
        if not got:
            continue
        status, ctype, body = got
        if status not in (200, 206):
            continue
        generic = bool(GENERIC.search(body[:400]))
        hits.append({
            "host": host["host"],
            "path": path,
            "url": f"{base}/{path}",
            "status": status,
            "ctype": ctype,
            "likely_false_positive": generic,
            "preview": re.sub(r"\s+", " ", body[:200]).strip(),
        })
    return hits


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Check high-signal exposure paths")
    ap.add_argument("alive", help="alive.json from tools/probe.py")
    ap.add_argument("-o", "--output", default="exposures.json")
    ap.add_argument("--paths", help="extra/newline path list to use instead")
    ap.add_argument("--threads", type=int, default=10)
    ap.add_argument("--timeout", type=float, default=10.0)
    ap.add_argument("--cap", type=int, default=300, help="max hosts")
    args = ap.parse_args(argv)

    data = json.loads(Path(args.alive).read_text(encoding="utf-8"))
    hosts = (data.get("hosts") or [])[: args.cap]
    if not hosts:
        print("error: no hosts", file=sys.stderr)
        return 2

    paths = DEFAULT_PATHS
    if args.paths and Path(args.paths).exists():
        paths = [p.strip() for p in Path(args.paths).read_text(encoding="utf-8").splitlines()
                 if p.strip() and not p.startswith("#")]

    print(f"checking {len(hosts)} hosts x {len(paths)} paths")
    all_hits: list[dict] = []
    with cf.ThreadPoolExecutor(max_workers=args.threads) as pool:
        futures = [pool.submit(check, h, paths, args.timeout) for h in hosts]
        for fut in cf.as_completed(futures):
            try:
                all_hits.extend(fut.result())
            except Exception:  # noqa: BLE001
                continue

    real = [h for h in all_hits if not h["likely_false_positive"]]
    Path(args.output).write_text(json.dumps({"count": len(all_hits), "hits": all_hits}, indent=2),
                                encoding="utf-8")
    print(f"wrote {args.output}: {len(all_hits)} hits ({len(real)} not obviously generic)")
    for hit in real[:30]:
        print(f"  {hit['status']} {hit['url']}  {hit['preview'][:80]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
