---
description: Find live secrets in JS, source maps, public repos and build artefacts — then prove one is valid.
argument-hint: <host>
allowed-tools: Bash, Read, Write, WebFetch
---

# /bbw-secrets

`references/14`, `workflows/09`, `checklists/secrets.md`, `tools/secrets.py`.

**Input:** `$ARGUMENTS` — host, or a repo/org to sweep.

```
/bbw-secrets https://app.acme.com
/bbw-secrets github.com/acme
```

A secret is only a finding when it is **live** and **theirs**. Both, or it is a note.

---

## Step 1 — Harvest the client

```bash
mkdir -p findings/<slug>/js && cd findings/<slug>/js
curl -s https://<host>/ -o home.html
grep -Eo 'src="[^"]+\.js[^"]*"' home.html | sed 's/src="//;s/"$//' | sort -u
# download each, then:
grep -Eo '//# sourceMappingURL=.+' home.html *.js
```

Beautify. Then sweep for patterns (`data/sensitive-patterns.txt`):

```bash
python tools/secrets.py alive.json -o engagements/<program>/secrets.json
```

Manual greps that find things the tool misses:

```bash
grep -Ei 'api[_-]?key|secret|token|password|passwd|bearer|authorization' *.js
grep -Eo '(AKIA|ASIA)[0-9A-Z]{16}' *.js                      # AWS
grep -Eo 'AIza[0-9A-Za-z_-]{35}' *.js                        # Google
grep -Eo 'gh[pousr]_[0-9A-Za-z]{36,}' *.js                    # GitHub
grep -Eo 'sk_live_[0-9A-Za-z]{24,}' *.js                      # Stripe
grep -Eo 'xox[baprs]-[0-9A-Za-z-]{10,}' *.js                  # Slack
grep -Eo 'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.' *.js   # JWT
```

Source maps are the jackpot: `bundle.js.map` gives you original filenames,
comments and sometimes config.

## Step 2 — Public repos and history

```
github.com/<org> → all repos → search for: .env, config, terraform.tfstate,
docker-compose.yml, .npmrc, id_rsa, .pypirc
git log -p --all | grep -Ei 'secret|key|token'      # history keeps what HEAD deleted
GitHub search: org:<org> "PRIVATE KEY"
CI: .github/workflows, logs with `set -x`
```

Also: Wayback Machine snapshots of `/.env`, `/config.js`, deleted S3 keys.

## Step 3 — Classify before you touch

| Class | Example | Usable? |
|---|---|---|
| Public by design | Firebase web API key with rules, Maps key with referer | No — note |
| Namespaced test key | `pk_test_`, `sk_test_` | Maybe — usually no impact |
| Client id / publishable key | Stripe `pk_live_` | No |
| Server secret | `sk_live_`, AWS `AKIA`, DB DSN, SMTP creds | **Yes** |
| Signing key | JWT HS256 secret | **Yes** — forge tokens |
| Third-party token | Slack bot, GitHub PAT, SendGrid | Yes, if scope allows |

## Step 4 — Validate with the minimum request

Only inside scope, only a read:

```bash
# AWS — identity only, no listing
aws sts get-caller-identity --access-key ... --secret-key ...
# Google
curl "https://maps.googleapis.com/maps/api/geocode/json?address=x&key=<key>"
# Stripe
curl https://api.stripe.com/v1/balance -u "sk_live_...:"
# GitHub
curl -H "Authorization: token <pat>" https://api.github.com/user
# Slack
curl -H "Authorization: Bearer <token>" https://slack.com/api/auth.test
# JWT secret
python tools/jwt_tool.py "<token>" --attack crack --wordlist data/jwt-secrets.txt
```

One call. Record the response. **Do not** enumerate what it can reach, do not pull
data, do not use it for anything else.

## Step 5 — JWT signing key = account takeover

If you cracked or found the HS256 secret:

1. Decode your own token.
2. Change `sub`/`user_id` to the victim account you control (account B).
3. Re-sign with the secret.
4. Use it. Access B = ATO, Critical.

Only between your own two accounts.

## Step 6 — Report shape

Secret reports fail when they are vague. Give:

- Exact file and URL where it was found
- The key's prefix and last four only (redact the middle)
- The one validation response proving it is live
- What it grants, stated narrowly
- Rotation advice in one line

---

## Output shape

```
js files: N   patterns hit: N   live: N
worst: <type> — <what it grants> — found in <file>
evidence: findings/<slug>/
severity: <band>
next: /bbw-score then /bbw-report
```

## Stop conditions

- Key is public by design → say "closed by design", do not report.
- Validation needs enumerating data → do not; the identity call is enough.
- Third-party service → check the program's scope covers it, else note only.
- AWS keys → `get-caller-identity`, then stop. Never list S3 with them.
