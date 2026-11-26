---
description: Hunt web cache deception and poisoning, plus response-header and protocol-level flaws.
argument-hint: <host>
allowed-tools: Bash, Read, Write, WebFetch
---

# /cache

`references/16`, `checklists/caching.md`.

**Input:** `$ARGUMENTS` — host behind a CDN or reverse proxy.

```
/cache https://app.acme.com
```

Two different bugs, often confused:

- **Cache poisoning** — you make the cache store a response that harms others.
- **Cache deception** — you make the cache store a victim's private response so you
  can read it.

Both need a cache in front. Prove one first.

---

## Step 1 — Is there a cache?

```bash
curl -sD- https://<host>/ | grep -i -E 'x-cache|cf-cache-status|age|cache-control|via|x-served-by|x-varnish|akamai|x-proxy'
```

| Header | Meaning |
|---|---|
| `x-cache: HIT` / `cf-cache-status: HIT` | cached |
| `age: >0` | cached |
| `x-cache: MISS` on first, `HIT` on second | confirm by requesting twice |

Then find **what is cached**: static paths, marketing pages, sitemaps, `?`-less
routes. A cache that only caches `/static/*` is not exploitable.

## Step 2 — Find the unkeyed input

The core of poisoning: something that changes the response but is **not** in the
cache key.

```
X-Forwarded-Host
X-Forwarded-Scheme
X-Host
X-Original-URL
X-Rewrite-URL
X-Forwarded-Prefix
X-Forwarded-Port
X-Forwarded-For
```

Test on a cacheable page:

```bash
curl -sD- "https://<host>/" -H "X-Forwarded-Host: <your-id>.oast.fun"
# then unauthenticated, see if the cached copy references your host
curl -s "https://<host>/"
```

If the second response contains your host, the cache is poisoned. That is a
working proof — but only if you can see it from a clean request.

## Step 3 — Poison with impact

A `X-Forwarded-Host` reflection alone is low. Chain it:

- Reflected into `<script src="//X-F-H/...">` → stored XSS for every visitor
- Reflected into a redirect → open redirect / OAuth redirect hijack
- Reflected into a JSONP callback → data exfiltration
- Reflected into a `Location` → phishing on their domain

Show: the poisoning request, then a clean request from the same cache reading the
poisoned body. Both raw, both saved.

## Step 4 — Cache deception (needs two accounts)

The trick: append a static-looking extension to a private path so the CDN caches it.

```
GET /account/profile.css
GET /api/me.json
GET /user/settings/;.css
GET /account/profile%2fcss
GET /account/profile?.css
GET /account/profile#.css
```

1. As victim account B (yours), request `/account/profile.css`.
2. As attacker A, request the same URL.
3. If A sees B's profile, the cache served private content. High.

Only with accounts you own. Cache rules vary — test each suffix once.

## Step 5 — Header and protocol issues

- `Vary` missing on `Accept-Language` / `Cookie` / `Origin` → wrong-user responses
- `Cache-Control: public` on authenticated endpoints
- `Set-Cookie` stored in a cached response → session fixation at scale
- HTTP request smuggling (only if you can prove it safely; usually out of reward)
- Host header injection into password-reset links → `/auth` reset poisoning
- `X-Forwarded-Proto: http` downgrade on a redirect

## Step 6 — Prove safely

Cache poisoning is dangerous: you are changing what other users see. Therefore:

- Use a harmless marker (`bbtest-<rand>`) in the reflected value
- Poison a path nobody uses if possible (`/bbtest-<rand>`)
- Read it back clean, save both responses, then let the TTL expire
- Never poison the login page on production with anything that changes behaviour

If the only proof requires harming real traffic, report it as Medium with the
unproven-impact line, not Critical.

---

## Output shape

```
cache: <cdn>   cacheable paths: N
unkeyed headers: <list>   reflected: <list>
poisoned: yes/no   deception: yes/no
impact: <xss | redirect | private-data>
evidence: findings/<slug>/
severity: <band>
next: /score then /report
```

## Stop conditions

- No cache in front → "no cache", move to another host.
- Unkeyed header reflected but no impact → Low, note, move on.
- Poisoning would affect the login flow → use a test path or stop.
- Deception needs a real victim → only your own accounts.
