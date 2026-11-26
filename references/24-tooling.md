# 24 — Tooling

The `tools/` directory is a working toolkit. Every script is bounded by default:
it prints what it did, what it skipped, and why. Nothing sends load, brute forces,
or writes destructively.

Nothing to install: every script is standard-library Python 3.10+, so
`python tools/<name>.py` works on a clean machine. Skip to the pipeline.

---

## The pipeline

```
scope.py ──► subdomains.py ──► probe.py ──► exposure.py
                                          ├─ secrets.py
                                          ├─ unauth_json.py
                                          └─ graphql.py
```

Then, per finding:

```
jwt_tool.py    idor.py    cvss.py    report.py    scope_diff.py
```

---

## scope.py

Normalise a program's scope into one JSON file you can quote and filter with.

```bash
python tools/scope.py --platform intigriti --program <handle> -o scope.json
python tools/scope.py --platform hackerone --handle <handle> -o scope.json
python tools/scope.py --file scope.txt --format text -o scope.json
```

Output: `wildcards`, `hosts`, `urls`, `mobile`, `ips`, `excluded`, `rules_notes`.

Everything you later touch must appear in this file. If it is not there, it does
not exist for you.

If the platform API is unavailable (some programs return 404 for scope), scrape
the public program page's asset list and pass it with `--file`.

---

## subdomains.py

Passive-first enumeration from a scope file. Uses certificate transparency and
passive sources; no brute force by default.

```bash
python tools/subdomains.py scope.json -o subs.json
python tools/subdomains.py scope.json --active-brute --wordlist data/subdomains.txt -o subs.json
```

Default: passive only. `--active-brute` is opt-in and rate-limited; use it only
when the program allows active enumeration.

Output: `{ "program": ..., "names": [...], "sources": {...} }`.

---

## probe.py

Resolve and fingerprint the alive hosts. Bounded threads and rate.

```bash
python tools/probe.py subs.json -o alive.json --threads 20 --rate 30
```

Records: status, title, tech, content-length, redirect, server, CNAME. Flags
takeover candidates against `data/takeover-fingerprints.txt`.

---

## exposure.py

Checks a fixed list of high-signal paths on alive hosts. One request per path per
host, capped hosts.

```bash
python tools/exposure.py alive.json -o exposures.json
```

Paths: `.env`, `.git/config`, `.git/HEAD`, `actuator/env`, `actuator/heapdump`,
`phpinfo.php`, `server-status`, backups, `.DS_Store`, `docker-compose.yml`, and
more (`data/common-paths.txt`).

Prints every hit with status and a 200-byte preview. A 200 with an HTML error
page is flagged as "likely false positive" — read it.

---

## secrets.py

Fetches JS from alive hosts and greps for high-signal secret patterns. Flags
candidates, does not test liveness.

```bash
python tools/secrets.py alive.json -o secrets.json
```

Each candidate: `{host, url, pattern, match_redacted, confidence}`. Confidence is
`format-only` or `likely-live` based on pattern specificity. You test liveness
manually with one minimal call.

Known false positives are filtered: `AKIAIOSFODNN7EXAMPLE`, Firebase configs,
publishable Stripe keys, base64 noise.

---

## unauth_json.py

Looks for unauthenticated JSON collections (the classic BOLA-at-scale leak).

```bash
python tools/unauth_json.py alive.json -o collections.json
```

Tries a bounded path list (`/api/users`, `/api/v1/users`, `/rest/users`,
`/wp-json/wp/v2/users`, `/graphql?query={users{id}}`, …) and records any 200 that
returns a JSON array/object with records. Reports the count and field names only
— never the data.

---

## graphql.py

Introspect a GraphQL endpoint and list operations.

```bash
python tools/graphql.py https://target/graphql --introspect -o schema.json
python tools/graphql.py https://target/graphql --list-mutations
```

If introspection is off, it tries field-suggestion probing to leak type names.
It does **not** run mutations.

---

## jwt_tool.py

Fingerprint and test a JWT.

```bash
python tools/jwt_tool.py "<token>"
python tools/jwt_tool.py "<token>" --attack none
python tools/jwt_tool.py "<token>" --attack crack --wordlist data/jwt-secrets.txt
python tools/jwt_tool.py "<token>" --attack rs2hs --pubkey pub.pem
```

Prints header/payload, flags missing `exp`, weak `alg`, and produces forged tokens
for you to test manually.

---

## idor.py

Diff two saved request/response pairs and decide whether B returned A's data.

```bash
python tools/idor.py --a a.json --b b.json
```

Input shape:

```json
{"request": {"method":"GET","url":"...","headers":{},"body":""},
 "response": {"status":200,"headers":{},"body":"..."}}
```

Prints: same-response / different-response, shared field names, whether B's body
contains A's unique marker. It is a documentation aid; you still reason about
ownership.

---

## cvss.py

Score a vector.

```bash
python tools/cvss.py "AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N"
```

Prints score, band, and a one-line justification. Use it so your score matches
your impact sentence.

---

## report.py

Build a report from a structured finding.

```bash
python tools/report.py finding.yaml -o report.md
python tools/report.py finding.yaml --dry-run
```

It renders the skeleton from `21-report-writing.md` and validates that every
required field is present (title, severity, asset, steps, impact, remediation).
`--dry-run` validates without writing.

---

## scope_diff.py

Diff two scope snapshots. A new asset is almost always untested.

```bash
python tools/scope_diff.py scope-old.json scope-new.json
```

Prints added/removed hosts per asset type. Run it weekly on a long engagement.

---

## sync_commands.py

Installs the 25 command files into an agent's command directory. It is the only
tool that writes to your filesystem, and it only writes inside the target
directory.

```bash
python tools/sync_commands.py --target opencode    # .opencode/command/
python tools/sync_commands.py --target claude      # .claude/commands/
python tools/sync_commands.py --target cursor      # .cursor/commands/
python tools/sync_commands.py --target codex       # .codex/prompts/
python tools/sync_commands.py --dir <any dir>
python tools/sync_commands.py --target opencode --dry-run
```

Codex gets its frontmatter trimmed to the keys it defines. Re-running is
idempotent: it overwrites the same 25 files and never touches anything else in
the directory. For Claude Code and OpenCode it also installs the skill
(`SKILL.md` + `AGENTS.md`) into the agent's skill directory.

---

## check_links.py

Repository maintenance, not hunting. Walks every markdown file and verifies that
every relative link resolves.

```bash
python tools/check_links.py
```

Run it before any commit that adds or renames a file.

---

## Writing your own tool

If a tool is missing, the rules from `CONTRIBUTING.md` apply:

- `--help` works.
- Bounded defaults: threads, rate, timeout, request cap.
- `--dry-run` for anything that sends traffic.
- Prints actions, skips, and reasons.
- Exits non-zero only on real failure.

A tool that does not print what it skipped is a tool you cannot trust.
