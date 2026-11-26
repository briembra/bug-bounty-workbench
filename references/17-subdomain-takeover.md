# 17 — Subdomain takeover

A subdomain points at a third-party service that no longer exists. You can claim
that service under your account, and now the company's subdomain serves your
content. Impact scales with what the subdomain is trusted for: cookies, CORS,
OAuth redirect_uri, email SPF, or brand.

---

## The pattern

```
sub.example.com  CNAME  project.herokudns.com   (project deleted)
                        → you create a Heroku app named "project"
                        → sub.example.com now serves your app
```

The company still controls the DNS record; the *target* is unclaimed.

---

## Detect

### 1. Find CNAMEs to third-party services

```bash
dnsx -l subs.txt -cname -resp -silent | grep -Ei 'heroku|s3|azure|cloudfront|github|readme|statuspage|zendesk|surge|netlify|vercel|bitbucket|fastly|wpengine|shopify|unbounce|pantheon|tumblr|wordpress|ghost|gitbook|helpscout|intercom|freshdesk|teamwork|aftership|tictail|bigcartel|cargo|smartjob|leadpages|instapage|unbounce|unstack|canny|simplebooklet|isnot|pingdom|strikingly|hatenablog|surveygizmo|agilecrm|uservoice|kajabi|thinkific|beautiful|wishpond|dlvr|landingi|ngrok'
```

### 2. Check each for the "unclaimed" response

| Service | Unclaimed signal |
|---|---|
| Heroku | `No such app` / `There's nothing here, yet.` |
| AWS S3 | `NoSuchBucket` / `The specified bucket does not exist` |
| GitHub Pages | `There isn't a GitHub Pages site here.` |
| Shopify | `Sorry, this shop is currently unavailable.` |
| Zendesk | `Help Center Closed` |
| Unbounce | `The requested URL was not found` + unbounce branding |
| Netlify | `Not found - Request ID:` |
| Vercel | `The deployment could not be found` |
| Azure | `404 Web Site not found` |
| CloudFront | `Bad request` / `ERROR: The request could not be satisfied` |
| WordPress.com | `Do you want to register` |
| Tumblr | `There's nothing here.` |
| Fastly | `Fastly error: unknown domain` |
| Readme | `Project doesnt exist... yet!` |
| Statuspage | `This page is reserved for future use` |
| Surge | `project not found` |
| Pantheon | `The gods are wise, but do not know of the site` |
| Cargo | `404 Not Found` + cargo |
| Bitbucket | `Repository not found` |
| Ghost | `Domain error` |

Fingerprints live in `data/takeover-fingerprints.txt`.

### 3. Confirm, do not assume

A 404 is not a takeover. The service must let **you** claim the name. Verify:

1. The CNAME target is a service with a claimable namespace.
2. The exact resource name is free (try to create it in your own account).
3. The service still routes that subdomain to the claimed resource.

Only then is it a takeover. A dangling CNAME to a service that does not allow
name claiming is a **dangling CNAME** (Low/Medium at best).

---

## Proof (safe, reversible)

1. Create the resource in your own account (e.g. a Heroku app named `project`).
2. Serve a harmless page: `<h1>bbh-takeover-proof-<random></h1>`.
3. Fetch `https://sub.example.com/` and show your marker.
4. **Delete the resource immediately** after capturing evidence.
5. Never serve phishing, never log visitors, never keep it.

If you cannot create the resource without side effects, stop and report the
dangling CNAME as a lower-severity finding with the fingerprint.

---

## Severity: it depends on trust

| Subdomain | Severity |
|---|---|
| `www.` / main brand | High–Critical |
| Cookie-scoped (`*.example.com` cookie set on parent) | High (session theft) |
| In an OAuth `redirect_uri` allowlist | Critical (ATO) |
| Used for email (SPF/MX) | High (email spoofing) |
| `dev-` / `test-` branch | Medium |
| Unused, no cookies, no trust | Medium |
| Dangling CNAME, unclaimable | Low/Info |

The escalator is **what the parent domain trusts the subdomain for.** A takeover
of `assets.example.com` with no cookies is Medium. `login.example.com` is
Critical.

---

## Related: dangling DNS

- **NS takeover:** the domain's NS record points at a nameserver provider where
  the zone is unclaimed → you control DNS entirely. Critical.
- **MX takeover:** mail to the domain goes to a provider you can claim → read
  email, reset tokens. Critical.
- **Dangling A record** to a cloud IP you can claim (rare, provider-specific).
- **S3 bucket takeover:** CNAME to a deleted bucket → you create it. High.

`tools/probe.py` flags CNAMEs; check them against the fingerprint list manually.

---

## What closed looks like

- CNAME target returns the real service (claimed and active) → closed.
- CNAME points to a service with no user-claimable namespace → dangling only.
- The subdomain is not in scope → out of scope, do not touch.
- The DNS record was removed between detection and testing → gone, NXDOMAIN.

---

## Discipline

- Claim, prove, delete. Same session.
- Do not leave a proof page up; a live takeover page is a real incident.
- Do not use the takeover for anything beyond the marker.
- Report the *trust* of the subdomain, not just the takeover.
