#!/usr/bin/env python3
"""Resolve and fingerprint hosts from a subdomains file.

usage:
    python tools/probe.py subs.json -o alive.json --threads 20 --rate 30 --cap 2000

Resolves each name (A/CNAME), then fetches https:// and http:// to record
status, title, server, redirect, and a light tech guess. Bounded threads, rate,
and request cap. Flags CNAMEs to takeover-prone services. Standard library only.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import queue
import re
import socket
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

TAKEOVER_HINTS = (
    "herokudns.com", "s3.amazonaws.com", "cloudfront.net", "azurewebsites.net",
    "github.io", "readme.io", "statuspage.io", "zendesk.com", "surge.sh",
    "netlify.app", "vercel.app", "bitbucket.io", "fastly.net", "wpengine.com",
    "myshopify.com", "unbounce.com", "pantheonsite.io", "tumblr.com",
    "ghost.io", "gitbook.io", "helpscout.net", "freshdesk.com", "teamwork.com",
    "aftership.com", "bigcartel.com", "cargocollective.com", "leadpages.net",
    "instapage.com", "unstack.com", "canny.io", "pingdom.com", "strikingly.com",
    "agilecrm.com", "uservoice.com", "kajabi.com", "thinkific.com",
    "wishpond.com", "dlvr.it", "landingi.com", "ngrok.io", "ngrok-free.app",
)

TECH_PATTERNS = {
    "wordpress": r"wp-content|wp-includes",
    "drupal": r"Drupal|sites/default/files",
    "laravel": r"laravel|XSRF-TOKEN",
    "next.js": r"__NEXT_DATA__|_next/static",
    "react": r"react|__REACT",
    "vue": r"vue(\.min)?\.js|__VUE__",
    "angular": r"ng-version|angular(\.min)?\.js",
    "django": r"csrfmiddlewaretoken|django",
    "spring": r"Whitelabel Error|JSESSIONID",
    "aspnet": r"ASP\.NET|__VIEWSTATE",
    "php": r"PHPSESSID|\.php",
    "jenkins": r"Jenkins",
    "gitlab": r"GitLab",
    "grafana": r"Grafana",
    "kibana": r"kibana",
    "cloudflare": r"cloudflare",
}

_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE


class Rate:
    def __init__(self, per_second: float) -> None:
        self.interval = 1.0 / per_second if per_second > 0 else 0.0
        self.next_at = 0.0

    def wait(self) -> None:
        if not self.interval:
            return
        now = time.monotonic()
        if now < self.next_at:
            time.sleep(self.next_at - now)
        self.next_at = max(now, self.next_at) + self.interval


def resolve(name: str) -> tuple[list[str], list[str]]:
    ips: list[str] = []
    cnames: list[str] = []
    try:
        infos = socket.getaddrinfo(name, None, proto=socket.IPPROTO_TCP)
        ips = sorted({info[4][0] for info in infos})
    except Exception:  # noqa: BLE001
        return [], []
    try:
        # getaddrinfo does not expose CNAME; use a best-effort canonical name
        canon = socket.getfqdn(name)
        if canon and canon != name:
            cnames.append(canon)
    except Exception:  # noqa: BLE001
        pass
    return ips, cnames


def fetch(url: str, timeout: float) -> dict | None:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_ssl_ctx) as resp:
            body = resp.read(200_000).decode("utf-8", "replace")
            return {
                "status": resp.status,
                "final_url": resp.geturl(),
                "server": resp.headers.get("Server", ""),
                "ctype": resp.headers.get("Content-Type", ""),
                "len": resp.headers.get("Content-Length", ""),
                "body": body,
            }
    except urllib.error.HTTPError as exc:
        body = ""
        try:
            body = exc.read(50_000).decode("utf-8", "replace")
        except Exception:  # noqa: BLE001
            pass
        return {
            "status": exc.code,
            "final_url": exc.geturl(),
            "server": (exc.headers or {}).get("Server", "") if exc.headers else "",
            "ctype": (exc.headers or {}).get("Content-Type", "") if exc.headers else "",
            "len": "",
            "body": body,
        }
    except Exception:  # noqa: BLE001 - connection refused, timeout, TLS error
        return None


def title_of(body: str) -> str:
    m = re.search(r"<title[^>]*>([^<]{0,200})", body, re.I | re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def tech_of(body: str, server: str) -> list[str]:
    blob = body + " " + server
    return [name for name, pat in TECH_PATTERNS.items() if re.search(pat, blob, re.I)]


def probe(name: str, rate: Rate, timeout: float) -> dict | None:
    ips, cnames = resolve(name)
    if not ips:
        return None
    result = {"host": name, "ips": ips, "cnames": cnames, "takeover_hint": False}
    for cname in cnames:
        if any(h in cname for h in TAKEOVER_HINTS):
            result["takeover_hint"] = True

    for scheme in ("https", "http"):
        rate.wait()
        got = fetch(f"{scheme}://{name}/", timeout)
        if not got:
            continue
        got["title"] = title_of(got.pop("body", ""))
        got["tech"] = tech_of("", got.get("server", ""))  # placeholder, refined below
        result.update({"status": got["status"], "url": got["final_url"],
                       "title": got["title"], "server": got["server"],
                       "ctype": got["ctype"], "scheme": scheme,
                       "tech": got["tech"]})
        break
    if "status" not in result:
        result["status"] = None
    return result


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Resolve and fingerprint hosts")
    ap.add_argument("subs", help="subs.json from tools/subdomains.py")
    ap.add_argument("-o", "--output", default="alive.json")
    ap.add_argument("--threads", type=int, default=20)
    ap.add_argument("--rate", type=float, default=30.0, help="requests per second (global)")
    ap.add_argument("--timeout", type=float, default=10.0)
    ap.add_argument("--cap", type=int, default=2000, help="max hosts to probe")
    args = ap.parse_args(argv)

    data = json.loads(Path(args.subs).read_text(encoding="utf-8"))
    names = data.get("names") or []
    if not names:
        print("error: no names in subs file", file=sys.stderr)
        return 2

    names = names[: args.cap]
    print(f"probing {len(names)} hosts (threads={args.threads}, rate={args.rate}/s)")

    rate = Rate(args.rate)
    alive: list[dict] = []
    dead = 0
    with cf.ThreadPoolExecutor(max_workers=args.threads) as pool:
        futures = {pool.submit(probe, n, rate, args.timeout): n for n in names}
        for fut in cf.as_completed(futures):
            try:
                res = fut.result()
            except Exception:  # noqa: BLE001
                res = None
            if res:
                alive.append(res)
            else:
                dead += 1

    alive.sort(key=lambda r: (r.get("status") is None, r["host"]))
    out = {
        "program": data.get("program"),
        "count": len(alive),
        "dead": dead,
        "hosts": alive,
    }
    Path(args.output).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"wrote {args.output}: {len(alive)} alive, {dead} dead")

    takeover = [h["host"] for h in alive if h.get("takeover_hint")]
    if takeover:
        print(f"takeover candidates ({len(takeover)}):")
        for host in takeover[:20]:
            print(f"  {host}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
