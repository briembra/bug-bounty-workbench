---
description: Passive-first subdomain and host discovery for a program, bounded and rules-aware.
argument-hint: <program> [--active]
allowed-tools: Bash, Read, Write, WebFetch
---

# /recon

Find the surface. Passive sources first, active only if the program allows it,
always bounded.

**Input:** `$ARGUMENTS` — program name from `/scope`, optional `--active`.

```
/recon acme
/recon acme --active
```

---

## Step 1 — Check the rules first

Open `engagements/<program>/rules.md`. If it says "no automated scanning" or "no
active enumeration", stop after Step 2 and say so. Passive research of public data
is not scanning, but heavy DNS brute force is.

## Step 2 — Passive (always allowed)

```bash
python tools/subdomains.py engagements/<program>/scope.json \
  -o engagements/<program>/subs.json
```

That hits certificate transparency. Widen it by hand with sources that need no
target contact:

- `crt.sh` JSON export, `*.target.com`
- Wayback Machine CDX for `*.target.com`
- Public GitHub org repos, CI configs, READMEs
- Shodan/Censys search for TLS SANs (view only, no target traffic)
- Public bug bounty writeups mentioning the target

Merge extra names with `--merge-file names.txt`.

## Step 3 — Resolve and fingerprint (bounded)

```bash
python tools/probe.py engagements/<program>/subs.json \
  -o engagements/<program>/alive.json --threads 20 --rate 30 --cap 2000
```

Defaults: 20 threads, 30 requests/second, 2000-host cap. Lower them if the rules
are stricter. The output records status, title, server, redirect, tech guess and
CNAME. `takeover_hint` flags third-party CNAMEs — feed those to `/takeover`.

## Step 4 — Bucket

Write `engagements/<program>/buckets.md`:

| bucket | hosts | why it matters |
|---|---|---|
| admin / staff panels | … | direct access check |
| `dev`/`stage`/`test`/`uat` | … | debug on, weaker auth |
| API and docs | … | schema, versions, batch |
| login / SSO / OAuth | … | auth bypass, ATO |
| file and export hosts | … | ACL, IDOR on files |
| AI / chat | … | RAG disclosure, SSRF |
| everything else | … | background |

Rank the buckets by expected ceiling, not by count.

## Step 5 — Quick probes on the top bucket

Three requests per host in the top bucket:

```bash
curl -sD- "https://<host>/" -o /dev/null
curl -sD- "https://<host>/robots.txt" -o /dev/null
curl -sD- "https://<host>/.well-known/security.txt" -o /dev/null
```

Note candidates. Do not dig yet.

## Step 6 — Exposure and secret sweep (optional, bounded)

```bash
python tools/exposure.py engagements/<program>/alive.json -o engagements/<program>/exposures.json
python tools/secrets.py engagements/<program>/alive.json -o engagements/<program>/secrets.json
python tools/unauth_json.py engagements/<program>/alive.json -o engagements/<program>/collections.json
```

Read every hit. Most are HTML error pages — the tool flags those. One real `.env`
or one unauthenticated JSON collection is a finding; hand it to `/secrets` or
`/api`.

---

## Output shape

```
domains: N   names: N   alive: N
takeover candidates: N
top bucket: <name> — <host>
chosen target: <host>
next: /surface
```

## Stop conditions

- Rules forbid enumeration → passive only, and say it.
- 429 or blanket 403 streak → stop, back off, reduce.
- Free-tier or shared-IP rate limiting you → wait, do not retry harder.
