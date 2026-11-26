---
description: Full hunt on one target URL — scope check, map, pick a class, prove, report.
argument-hint: <url or host> [program]
allowed-tools: Bash, Read, Write, WebFetch
---

# /bbw-hunt

The end-to-end loop on a single target. Everything else in `commands/` is a
step of this, run on its own.

**Input:** `$ARGUMENTS` — a URL or host, optionally followed by the program name.

```
/bbw-hunt https://app.example.com "Acme" on Intigriti
/bbw-hunt api.example.com
```

---

## Step 0 — Refuse to guess scope

1. Identify the program and platform from the argument or by asking once.
2. Read the program's own scope page. Record: in-scope assets, wildcards,
   exclusions, prohibited actions, rate limits.
3. Confirm `$ARGUMENTS` matches an in-scope entry — exact host, wildcard parent,
   or listed URL pattern.
4. If it does not match, **stop**. Say what is missing. Do not probe.

Save to `engagements/<program>/scope.json` with `python tools/scope.py --file scope.txt`.

## Step 0.5 — Check how old the surface is

One question before the map: when did anything in this scope change?

- Look for scope updates, acquisitions, new features, a v2 API, a recent app
  release. Newest asset wins (`references/01`).
- If the asset you were handed is the flagship and nothing in scope has changed in
  over a year, say so in one line and name the newest in-scope asset instead —
  that is where the reachable bugs are.
- Freshness does not unlock anything out of scope. It only decides *where* inside
  the scope you spend the first hour.

## Step 1 — Map before you test (20 min)

- `curl -sD- https://<host>/`, `robots.txt`, `sitemap.xml`, `/.well-known/security.txt`
- Download the JS bundle, grep `/api/`, `graphql`, base URLs (`references/14`)
- Check `/openapi.json`, `/swagger.json`, `/bbw-graphql` (`references/12`)
- Note stack from headers, cookies, error pages
- Register two accounts if the app allows (`you+bb@yourdomain`, unique password)

Write `engagements/<program>/map.md`: actors, objects, flows, endpoints, trust
boundaries. If you cannot name three objects and two roles, you are not ready.

## Step 2 — Pick one class (10 min)

Use `prompts/vuln-class-selector.md`. Rank by ceiling × likelihood / effort, drop
anything the program excludes, then take the top one and run its command:

| Signal you saw | Command |
|---|---|
| object ids in paths, `?user_id=` | `/bbw-idor` |
| login, reset, signup, SSO | `/bbw-auth` |
| URL / webhook / import params | `/bbw-ssrf` |
| user input rendered anywhere | `/bbw-xss` |
| sort, filter, search, numeric ids | `/bbw-injection` |
| upload / download / export | `/bbw-files` |
| cart, coupon, refund, credits | `/bbw-logic` |
| API docs, versions, batch | `/bbw-api` or `/bbw-graphql` |
| S3/GCS/Azure/Firebase hosts | `/bbw-cloud` |
| CNAME to a SaaS service | `/bbw-takeover` |
| chatbot, copilot, AI search | `/bbw-ai` |
| mobile or Electron client | `/bbw-mobile` |
| JS with tokens in it | `/bbw-secrets` |
| CDN headers, `Vary`, cache | `/bbw-cache` |

Do not run five classes in parallel. One to conclusion.

## Step 3 — Prove (the only step that counts)

- Two accounts, both yours. Victim object created by account B, read by A.
- Capture `request-01.http` … `response-02.http` into `findings/<slug>/` as you go.
- Reproduce twice from a clean state. If the second run fails, it is not confirmed.

## Step 4 — Score

`/bbw-score` — run `python tools/cvss.py "<vector>"`, check the impact sentence
against `references/20`, downgrade if the data is demo/seed.

## Step 5 — Write and submit

`/bbw-report` then `/bbw-dedup` then `/bbw-submit`.

---

## Report back to the user, every step

```
Confirmed:     <what is proven> — <evidence path>
Not confirmed: <what failed> — <what would settle it>
Next:          <exactly one action>
```

## Hard stops

- Out of scope, ambiguous scope, or a rule you cannot satisfy → stop, say why.
- Real third-party PII at scale → one record, redact, stop.
- Anything in the forbidden table (`AGENTS.md` §3) → do not.
- The next step would break a service, touch a real customer, or contact a person
  → stop and report.
