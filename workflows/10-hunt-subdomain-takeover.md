# Workflow 10 — Hunt subdomain takeover

Run this on the alive/CNAME inventory. Time box: 60 minutes. Claim, prove,
delete — same session.

---

## Step 1 — Collect CNAMEs (10 min)

```bash
dnsx -l subs.txt -cname -resp -silent -o cnames.txt
grep -Ei 'heroku|s3|azure|cloudfront|github|readme|statuspage|zendesk|surge|netlify|vercel|bitbucket|fastly|wpengine|shopify|unbounce|pantheon|tumblr|wordpress|ghost|gitbook|helpscout|intercom|freshdesk|teamwork|aftership|bigcartel|cargo|leadpages|instapage|unstack|canny|pingdom|strikingly|agilecrm|uservoice|kajabi|thinkific|wishpond|dlvr|landingi|ngrok' cnames.txt
```

---

## Step 2 — Fingerprint (20 min)

For each candidate, fetch the host and match against
`data/takeover-fingerprints.txt`:

```bash
curl -s -i "https://sub.example.com/" | head -40
```

Common fingerprints:

| Service | Body |
|---|---|
| Heroku | `No such app` |
| S3 | `NoSuchBucket` |
| GitHub Pages | `There isn't a GitHub Pages site here.` |
| Shopify | `Sorry, this shop is currently unavailable.` |
| Zendesk | `Help Center Closed` |
| Netlify | `Not found - Request ID:` |
| Vercel | `The deployment could not be found` |
| Azure | `404 Web Site not found` |
| Readme | `Project doesnt exist... yet!` |
| Statuspage | `This page is reserved for future use` |
| Surge | `project not found` |
| Pantheon | `The gods are wise` |

A 404 is **not** proof. A matching fingerprint is a candidate.

---

## Step 3 — Verify claimability (15 min)

The service must let you claim the name. For each:

- Heroku: create an app with the exact name → succeeds = claimable.
- S3: create a bucket with the exact name in the right region.
- GitHub Pages: create a repo `<user>.github.io` or a Pages site with the CNAME.
- Netlify/Vercel: add the domain to your project.

If the name is taken or the service does not allow claiming, it is a **dangling
CNAME** — Low/Medium, not a takeover.

---

## Step 4 — Prove (10 min)

1. Claim the resource.
2. Serve a harmless marker: `<h1>bbh-takeover-<rand></h1>`.
3. `curl https://sub.example.com/` → show the marker.
4. **Delete the resource immediately.**
5. Keep the request/response and a screenshot.

Never serve anything else. Never log visitors. Never keep it live.

---

## Step 5 — Assess trust (10 min)

Severity depends on what the subdomain is trusted for:

- Cookies scoped to parent → session theft (High).
- OAuth `redirect_uri` allowlist → ATO (Critical).
- Email (SPF/MX) → spoofing (High).
- Main brand / `www` → High–Critical.
- `dev-`/`test-` → Medium.
- No trust → Medium.

State the trust explicitly in the report.

---

## Step 6 — Report

Include: the DNS record, the fingerprint, the claim steps, the marker response,
the trust, and confirmation you deleted the resource. Run
`checklists/takeover.md`.

---

## Definition of done

- [ ] CNAMEs collected.
- [ ] Fingerprints matched.
- [ ] Claimability verified.
- [ ] Marker proven and deleted.
- [ ] Trust assessed.
- [ ] Report written.

A dangling CNAME that cannot be claimed is Low. Report it as such or not at all —
do not call it a takeover.
