---
description: Full hunt on one target URL — scope check, map, pick a class, prove, report.
argument-hint: <url or host> [program]
allowed-tools: Bash, Read, Write, WebFetch
---

# /hunt

The end-to-end loop on a single target. Everything else in `commands/` is a
step of this, run on its own.

**Input:** `$ARGUMENTS` — a URL or host, optionally followed by the program name.

```
/hunt https://app.example.com "Acme" on Intigriti
/hunt api.example.com
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

## Step 1 — Map before you test (20 min)

- `curl -sD- https://<host>/`, `robots.txt`, `sitemap.xml`, `/.well-known/security.txt`
- Download the JS bundle, grep `/api/`, `graphql`, base URLs (`references/14`)
- Check `/openapi.json`, `/swagger.json`, `/graphql` (`references/12`)
- Note stack from headers, cookies, error pages
- Register two accounts if the app allows (`you+bb@yourdomain`, unique password)

Write `engagements/<program>/map.md`: actors, objects, flows, endpoints, trust
boundaries. If you cannot name three objects and two roles, you are not ready.

## Step 2 — Pick one class (10 min)

Use `prompts/vuln-class-selector.md`. Rank by ceiling × likelihood / effort, drop
anything the program excludes, then take the top one and run its command:

| Signal you saw | Command |
|---|---|
| object ids in paths, `?user_id=` | `/idor` |
| login, reset, signup, SSO | `/auth` |
| URL / webhook / import params | `/ssrf` |
| user input rendered anywhere | `/xss` |
| sort, filter, search, numeric ids | `/injection` |
| upload / download / export | `/files` |
| cart, coupon, refund, credits | `/logic` |
| API docs, versions, batch | `/api` or `/graphql` |
| S3/GCS/Azure/Firebase hosts | `/cloud` |
| CNAME to a SaaS service | `/takeover` |
| chatbot, copilot, AI search | `/ai` |
| mobile or Electron client | `/mobile` |
| JS with tokens in it | `/secrets` |
| CDN headers, `Vary`, cache | `/cache` |

Do not run five classes in parallel. One to conclusion.

## Step 3 — Prove (the only step that counts)

- Two accounts, both yours. Victim object created by account B, read by A.
- Capture `request-01.http` … `response-02.http` into `findings/<slug>/` as you go.
- Reproduce twice from a clean state. If the second run fails, it is not confirmed.

## Step 4 — Score

`/score` — run `python tools/cvss.py "<vector>"`, check the impact sentence
against `references/20`, downgrade if the data is demo/seed.

## Step 5 — Write and submit

`/report` then `/dedup` then `/submit`.

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
