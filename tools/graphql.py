#!/usr/bin/env python3
"""Introspect a GraphQL endpoint and list operations.

usage:
    python tools/graphql.py https://target/graphql --introspect -o schema.json
    python tools/graphql.py https://target/graphql --list-mutations
    python tools/graphql.py https://target/graphql --field-probe user

Sends a read-only introspection query (or a field-suggestion probe). Never runs a
mutation. Standard library only.
"""
from __future__ import annotations

import argparse
import json
import ssl
import sys
import urllib.error
import urllib.request

UA = "Mozilla/5.0 (compatible; bbh-graphql/1.0)"

INTROSPECTION = """
query IntrospectionQuery {
  __schema {
    queryType { name }
    mutationType { name }
    types {
      kind name
      fields { name args { name type { name kind ofType { name kind } } } }
      inputFields { name }
      enumValues { name }
    }
  }
}
"""

_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE


def post(url: str, query: str, timeout: float) -> dict:
    body = json.dumps({"query": query}).encode()
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json", "User-Agent": UA, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout, context=_ssl_ctx) as resp:
        return json.loads(resp.read().decode("utf-8", "replace"))


def summarize(schema: dict) -> None:
    data = (schema.get("data") or {}).get("__schema")
    if not data:
        print("introspection returned no schema")
        if schema.get("errors"):
            print("errors:", json.dumps(schema["errors"])[:400])
        return
    types = data.get("types") or []
    queries = next((t for t in types if t["name"] == (data.get("queryType") or {}).get("name")), None)
    mutations = next((t for t in types if t["name"] == (data.get("mutationType") or {}).get("name")), None)

    if queries:
        print("queries:")
        for f in queries.get("fields") or []:
            args = ", ".join(a["name"] for a in f.get("args") or [])
            print(f"  {f['name']}({args})")
    if mutations:
        print("mutations:")
        for f in mutations.get("fields") or []:
            args = ", ".join(a["name"] for a in f.get("args") or [])
            print(f"  {f['name']}({args})")
    print(f"types: {len(types)}")


def field_probe(url: str, name: str, timeout: float) -> None:
    """Send an unknown field and read the 'Did you mean' suggestion."""
    q = "{ " + name + " }"
    try:
        result = post(url, q, timeout)
    except urllib.error.HTTPError as exc:
        result = json.loads(exc.read().decode("utf-8", "replace") or "{}")
    errors = result.get("errors") or []
    if not errors:
        print("no error — field may exist or errors are suppressed")
        return
    for err in errors:
        print(err.get("message", "")[:300])


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="GraphQL introspection helper")
    ap.add_argument("url", help="GraphQL endpoint URL")
    ap.add_argument("--introspect", action="store_true", help="run introspection")
    ap.add_argument("--list-mutations", action="store_true", help="print mutation names")
    ap.add_argument("--field-probe", metavar="NAME", help="probe a field name for suggestions")
    ap.add_argument("-o", "--output", help="write raw introspection JSON here")
    ap.add_argument("--timeout", type=float, default=30.0)
    args = ap.parse_args(argv)

    try:
        if args.field_probe:
            field_probe(args.url, args.field_probe, args.timeout)
            return 0

        if not (args.introspect or args.list_mutations):
            ap.error("choose --introspect, --list-mutations, or --field-probe")

        result = post(args.url, INTROSPECTION, args.timeout)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2)
        print(f"wrote {args.output}")

    summarize(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
