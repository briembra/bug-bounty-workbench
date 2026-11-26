# 14 — Secrets and JavaScript analysis

The frontend ships more than it should: API keys, internal URLs, feature flags,
route tables, sometimes entire source maps. Most of what you find is **not** a
secret. This document is about telling the difference.

---

## The difference that matters

| Found in JS | Secret? | Impact |
|---|---|---|
| Firebase `apiKey` / `projectId` | No — public by design | None alone |
| Stripe `pk_live_…` | No — publishable | None |
| Google Maps `AIza…` (restricted) | Usually no | Check restrictions |
| AWS `AKIA…` | **Yes** if live | Critical |
| Stripe `sk_live_…` | **Yes** | Critical |
| GitHub `ghp_…` / `github_pat_…` | **Yes** | High |
| Slack `xox[baprs]-…` | **Yes** | High |
| SendGrid `SG.…` | **Yes** | Medium–High (mail) |
| Twilio `SK…` + `AC…` | **Yes** | High (SMS/calls) |
| JWT signing key | **Yes** | Critical |
| Private key (`BEGIN PRIVATE KEY`) | **Yes** | Critical |
| Internal hostname | No, but useful | Recon |
| Feature flag / admin path | No, but useful | Recon |

**Verify before reporting.** A key that returns 401/403 is dead. A key that
performs an action is live. Test the *least* invasive call (e.g. `aws sts
get-caller-identity`, `GET /v1/account` on Stripe) and stop.

---

## Where to look

### JS bundles

```bash
# download and beautify
curl -s https://target/app.js -o app.js
npx js-beautify app.js > app.pretty.js

# high-signal greps
grep -Eo 'https?://[a-zA-Z0-9._/-]+' app.pretty.js | sort -u
grep -Ei 'api[_-]?key|secret|token|password|passwd|private' app.pretty.js
grep -Eo '/api/[a-zA-Z0-9/_{}-]+' app.pretty.js | sort -u
grep -Eo 'AKIA[0-9A-Z]{16}' app.pretty.js
grep -Eo 'ghp_[A-Za-z0-9]{36}' app.pretty.js
grep -Eo 'xox[baprs]-[A-Za-z0-9-]+' app.pretty.js
grep -Eo 'sk_live_[A-Za-z0-9]+' app.pretty.js
```

### Source maps

If `app.js.map` is served, you get original source:

```bash
curl -s https://target/app.js.map -o app.js.map
npx source-map-explorer app.js.map   # or unwebpack / reverse-sourcemap
```

Original source exposes comments, TODO notes, internal endpoints, and sometimes
test credentials. A served `.map` is not a bug by itself — it is a map.

### Other JS-adjacent places

- **`/static/js/`, `/assets/`, `/build/`, `/_next/static/`** — framework chunk
  names.
- **Webpack manifests** (`manifest.json`, `asset-manifest.json`) — every chunk.
- **Service worker** (`sw.js`) — cached routes, offline endpoints.
- **`env.js` / `config.js` / `runtime-config.json`** — runtime config, often with
  API base and flags.
- **Robots/sitemap** for paths.
- **GitHub** — the org's public repos, gists, CI configs, issues with pasted logs.

---

## The verification protocol

Never report a secret without:

1. **Format match** — it looks like the real thing (length, prefix, checksum).
2. **Not a known-public key** — Firebase/Stripe-publishable/Maps restricted are
   public.
3. **Liveness test** — one minimal call that distinguishes live from dead.
4. **Blast radius** — what can it do? Read? Write? Admin? Say which.
5. **Redaction** — in the report, show first 4 / last 4 characters only.

A report that says "AWS key found, might be live" gets triaged as Informational.
A report that says "AWS key `AKIA…XXXX` calls `sts:GetCallerIdentity` as
`arn:aws:iam::123:user/ci-deploy`, which has `s3:*` on `prod-*` buckets" gets
Critical.

---

## Tools

`tools/secrets.py` scans a list of alive hosts' JS for high-signal patterns and
prints candidates with a confidence label (format-only vs likely-live). It does
**not** test liveness — you do that manually, one call.

```bash
python tools/secrets.py alive.json -o secrets.json
```

Built-in false positives to expect:

- Base64 strings that decode to `AKIA…` but are not keys.
- Test fixtures (`AKIAIOSFODNN7EXAMPLE`).
- Documentation examples.
- Public analytics tokens.

Read `secrets.json` critically. The tool flags candidates; you decide.

---

## GitHub and git history

- **Deleted secrets** live in git history:
  `git log -p | grep -i secret`. Tools: `gitleaks`, `trufflehog`.
- **Public repos** with `.env`, `config.json`, `terraform.tfstate`, `*.pem`.
- **CI logs** pasted in issues with tokens.
- **Gists** from employees.

If the program's scope includes their GitHub org, this is in scope. If it does not,
a secret found there may still be in scope because it affects the production app —
state the scope reasoning explicitly.

---

## Severity

| What you showed | Severity |
|---|---|
| Live AWS key with real permissions | Critical |
| Live Stripe secret key | Critical |
| Live GitHub PAT with repo write | High |
| Live SendGrid/Twilio key | Medium–High |
| JWT signing key | Critical |
| Internal hostnames only | Info |
| Source map served | Info |
| Firebase client config | Info (not a bug) |
| Dead key (401) | Info / closed |

---

## What closed looks like

- Key returns 401/403 → dead, do not report.
- Key is a known public type (Firebase, publishable Stripe) → not a secret.
- Key is restricted by referrer/IP → note the restriction; usually closed.
- Source map served but source contains nothing sensitive → Info at most.

The bench rule: **a secret is only a finding when it does something.** Otherwise
it is trivia.
