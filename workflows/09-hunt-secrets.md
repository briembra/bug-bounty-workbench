# Workflow 09 — Hunt secrets

Run this on a list of alive hosts. Time box: 60 minutes. The rule: a secret is a
finding only if it does something.

---

## Step 1 — Collect the JS (15 min)

```bash
python tools/secrets.py alive.json -o secrets.json
```

Or manually, per host:

```bash
curl -s https://host/ -o index.html
grep -Eo 'src="[^"]+\.js[^"]*"' index.html
# download each, beautify
npx js-beautify bundle.js > bundle.pretty.js
```

Also grab `manifest.json`, `asset-manifest.json`, `sw.js`, `env.js`, `config.js`.

---

## Step 2 — Grep the high-signal patterns (10 min)

```bash
grep -Eo 'AKIA[0-9A-Z]{16}' *.js
grep -Eo 'ghp_[A-Za-z0-9]{36}' *.js
grep -Eo 'github_pat_[A-Za-z0-9_]{82}' *.js
grep -Eo 'xox[baprs]-[A-Za-z0-9-]+' *.js
grep -Eo 'sk_live_[A-Za-z0-9]{24,}' *.js
grep -Eo 'SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}' *.js
grep -Eo 'AIza[0-9A-Za-z_-]{35}' *.js
grep -Eo 'https://[a-z0-9.-]+\.(s3|blob\.core|storage\.googleapis)[^"'"'"']*' *.js
grep -Ei 'BEGIN (RSA|EC|OPENSSH) PRIVATE KEY' *.js
```

Also internal hostnames and `/api/` paths — not secrets, but a map.

---

## Step 3 — Triage each hit (15 min)

For every candidate:

1. Is it a **known public type**? Firebase `apiKey`, Stripe `pk_live`, restricted
   Maps key → not a secret.
2. Is it a **test fixture**? `AKIAIOSFODNN7EXAMPLE`, `your-key-here`, `xxxx`.
3. Is it **base64 noise** that happens to match? Decode and check.
4. Does it **do something**? One minimal call (below).

---

## Step 4 — Liveness test (15 min)

Least invasive call per provider:

```bash
# AWS
AWS_ACCESS_KEY_ID=... AWS_SECRET_ACCESS_KEY=... aws sts get-caller-identity

# GitHub
curl -s -H "Authorization: token <tok>" https://api.github.com/user

# Stripe
curl -s https://api.stripe.com/v1/account -u "<sk>:"

# SendGrid
curl -s -H "Authorization: Bearer <key>" https://api.sendgrid.com/v3/user/account

# Slack
curl -s -H "Authorization: Bearer <tok>" https://slack.com/api/auth.test
```

A 401/403 is dead — do not report. A 200 that identifies an account is live.

**Stop there.** Do not enumerate permissions, do not list data. Report the identity
and the scope if visible.

---

## Step 5 — Blast radius (10 min)

For a live key, state what it can do:

- AWS: the IAM user/role ARN; from the name, infer scope. Never call mutating APIs.
- GitHub: the token's scopes (`X-OAuth-Scopes` header) and the org.
- Stripe: live vs test, restricted vs full.
- Cloud: the project/account and the service account email.

---

## Step 6 — Report

Redact to first 4 / last 4. Show one live call. Run `checklists/secrets.md`.

```
AWS key AKIA…XXXX calls sts:GetCallerIdentity as
arn:aws:iam::123456789012:user/ci-deploy.
```

---

## Definition of done

- [ ] JS collected and grepped.
- [ ] Candidates triaged (public? fixture? noise?).
- [ ] Liveness tested with one minimal call.
- [ ] Blast radius stated.
- [ ] Report written or candidates closed.

A dead key is closed. Say it and move on. Do not report trivia.
