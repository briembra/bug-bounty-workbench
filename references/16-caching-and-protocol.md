# 16 — Caching and protocol

Cache bugs are subtle, high-impact, and under-hunted. A cache that serves one
user's response to another is a data leak at CDN scale. This document covers
cache poisoning, cache deception, request smuggling, and host-header attacks.

---

## Cache poisoning

The cache keys on *some* part of the request (path, Host, sometimes a query
param). If an unkeyed input changes the response, and you can get the poisoned
response cached, every subsequent visitor gets it.

### Find unkeyed inputs

- **Headers the app reflects:** `X-Forwarded-Host`, `X-Forwarded-Scheme`,
  `X-Host`, `X-Original-URL`, `X-Rewrite-URL`, `Forwarded`, `X-Forwarded-For`.
- **Query params not in the cache key:** `?utm_source=`, `?callback=`,
  `?cb=`, `?x=`.
- **Cookie values reflected** but not keyed.

### Test procedure

1. Confirm the response is cached: send a request twice, look for
   `X-Cache: HIT`, `CF-Cache-Status: HIT`, `Age: >0`.
2. Send a request with a unique marker in an unkeyed header.
3. Fetch again **without** the header. If the marker appears → poisoned.

```bash
curl -s -D- "https://target/page" -H "X-Forwarded-Host: evil.com"
# then
curl -s -D- "https://target/page"
```

If the second response contains `evil.com` in a link/redirect/script src, you have
cache poisoning. If it is an XSS payload cached for all users, that is High.

### Common payloads

- `X-Forwarded-Host: evil.com` → cached redirect or absolute URLs point at
  attacker.
- `X-Forwarded-Scheme: nothttps` → cached redirect loop / mixed scheme.
- Query `?cb=<svg onload=…>` if `cb` is reflected but not keyed.
- Fat GET: body param reflected for a GET request that the cache treats as keyed
  only on URL.

---

## Cache deception

The cache stores a *private* page under a *public* URL because the extension
confuses it:

```
GET /account/profile.css      → app returns /account/profile (ignores .css)
                              → cache stores authenticated response at /profile.css
GET /account/profile.css      → cache serves it to an anonymous attacker
```

Variants: `.css`, `.js`, `.png`, `.jpg`, `.ico`, `.avif`, trailing `;`,
`%00`, `?` in the path, `/account/profile/..%2fstyle.css`.

Test:

1. Log in, request `/account` with a cache-busting suffix that the app ignores.
2. Look for `X-Cache: HIT` on the second anonymous request.
3. If the anonymous request returns the authenticated page → High.

Cache deception is High when it leaks PII/session pages.

---

## Web cache key confusion

- **`Vary` missing** on a response that differs by cookie → one user's data
  cached for all.
- **`Vary: User-Agent`** but the app branches on `Accept-Language` → wrong
  language/data cached.
- **CDN normalizes the path differently** from the origin (`/admin` vs
  `/admin/` vs `//admin`) → cache bypass of auth.
- **Query parameter pollution** `?a=1&a=2` — CDN and origin disagree on the key.

---

## Host header attacks

The app builds absolute URLs (password reset, redirects, email links) from the
`Host` header. If it trusts an arbitrary `Host`, you get:

- **Password reset poisoning** → account takeover (email links to attacker).
- **Cache poisoning** (above).
- **Web cache / routing bypass** — `X-Forwarded-Host` routes to internal vhost.
- **SSRF** — some proxies route by Host to internal services.

Test:

```bash
curl -s -D- "https://target/" -H "Host: evil.com"
curl -s -D- "https://target/" -H "X-Forwarded-Host: evil.com"
curl -s -D- "https://target/" -H "X-Forwarded-For: 127.0.0.1"
```

Check `Location:` and any absolute URLs. Use your own listener to see if a reset
email hits it (only your own account).

---

## HTTP request smuggling (advanced)

When a front-end proxy and back-end server disagree on message boundaries
(`Content-Length` vs `Transfer-Encoding`), a smuggled request executes in the
next user's connection. High impact, high difficulty, easy to break the service.

Signals: different `Server` on front vs back, a CDN in front, HTTP/1.1 to origin.

Techniques: CL.TE, TE.CL, TE.TE, H2.CL, H2.TE. Test with **timing** first:

```
POST / HTTP/1.1
Host: target
Content-Length: 4
Transfer-Encoding: chunked

5c
GPOST / HTTP/1.1
...
```

**Do not** run smuggling tests on production without the program explicitly
allowing it — a bad test can poison the connection pool for real users. Report
suspected smuggling from safe probes (differential server headers, response
splitting on your own request).

---

## HTTP/2 and protocol

- **H2 connection coalescing** — a cert allowing multiple hosts lets one connection
  serve another host; misrouting.
- **`TE: trailers`** abuse.
- **HTTP/1.1 downgrade** at the proxy.
- **Absolute-URI in request line** (`GET http://internal/ HTTP/1.1`) — some
  proxies route it internally (SSRF).

---

## The cache findings that pay

| What you showed | Severity |
|---|---|
| Cached XSS served to all users | High–Critical |
| Cached redirect to attacker for reset tokens | High |
| Cache deception leaking authenticated PII | High |
| Cache poisoning of a JS file | High |
| Host header in reset email to your listener | Critical (ATO) |
| Cache poisoning causing a 404 on a public page | Low |
| Missing `Vary` with no demonstrated leak | Info |

---

## Discipline for cache testing

- Always use a **unique cache-buster** you control, and cache a harmless marker
  first. Do not poison a real page with a payload that real users will execute.
- Use a low-traffic path or a test tenant if available.
- After proving, request a purge if the program has a channel, or note the exact
  URL so triage can purge.
- Never run cache tests at high volume; poisoning is global.

---

## What closed looks like

- `Vary` correct, cache key includes all inputs that change the response →
  closed.
- Host header ignored; absolute URLs from config → closed.
- No caching on authenticated responses (`Cache-Control: private, no-store`) →
  closed.
- Cache deception suffix returns 404 or the unauthenticated page → closed.
