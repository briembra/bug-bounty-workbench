# Workflow 12 — Report and submit

You have a confirmed finding with evidence. This workflow turns it into a
submitted report that gets accepted. Time box: 45 minutes.

---

## Step 1 — Run the submission checklist

Open `checklists/submission.md`. Every box must be checked. If one is not, fix it
before writing.

The big ones:

- [ ] Two-account proof (for cross-user bugs).
- [ ] Data is sensitive, not public/demo.
- [ ] In scope, quoted.
- [ ] Reproduced twice.
- [ ] Redaction done.

---

## Step 2 — Run the dedup check

Per `workflows/13-dedup-check.md`. Search disclosed reports, the endpoint, and the
class. Note what you searched in the report ("Searched disclosed reports for
`/api/orders` — no match").

---

## Step 3 — Build the finding.yaml

```yaml
title: "Any customer can read any other customer's order history and PII"
severity: high
cvss: "AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N"
asset: "https://app.example.com/api/orders/{id}"
summary: |
  The order detail endpoint returns any order by id without checking that the
  order belongs to the requesting user. Any authenticated customer can read
  another customer's name, address, phone and payment last-4.
steps:
  - "Log in as account A; create an order; note id 1042."
  - "Log in as account B; create an order; note id 1043."
  - "As account A, GET /api/orders/1043."
  - "Observe B's data returned."
evidence:
  - request-01.http
  - response-01.http
  - request-02.http
  - response-02.http
impact: |
  Any customer can read any other customer's PII and order history by
  incrementing the id. No rate limit. ~N customers exposed.
remediation: |
  Filter by session user in the query: Order.objects.get(id=id, user_id=request.user.id),
  return 404 for non-owners. Apply to /orders/{id}/items and the CSV export.
```

Then:

```bash
python tools/report.py finding.yaml -o report.md
python tools/report.py finding.yaml --dry-run   # validate only
```

---

## Step 4 — Read the report out loud

- Does the title say the impact?
- Does the summary fit in three sentences?
- Can a stranger reproduce it from the steps alone?
- Is the impact concrete (fields, scale, who)?
- Is the remediation a fix a dev can apply?

If any answer is no, edit. Short beats long.

---

## Step 5 — Submit

Paste into the platform's form. Keep the platform's own fields where they exist
(asset, severity, CWE). Attach evidence files.

Intigriti: asset + severity + CVSS + CWE.
HackerOne: weakness + severity + CVSS vector.
Bugcrowd: VRT category + severity.
YesWeHack: scope asset + CVSS.

---

## Step 6 — After submit

- Note the report id and date in `notes.md`.
- Respond to triage within a day.
- If asked for more evidence, give exactly that.
- If downgraded, one calm reply (`20-severity-and-cvss.md`), then accept.
- Keep hunting the same asset — you now know it best.

---

## Definition of done

- [ ] Checklist passed.
- [ ] Dedup checked and noted.
- [ ] finding.yaml valid.
- [ ] report.md rendered and read.
- [ ] Submitted.
- [ ] Report id recorded.
