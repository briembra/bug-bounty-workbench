# 21 — Report writing

A report is not a story. It is a technical document a triager reads in two
minutes and either reproduces or rejects. This is the shape that gets accepted.

---

## The skeleton

```
Title:      <impact> via <vector> on <asset>
Severity:   <rating> (<CVSS vector>, <score>)
Asset:      <exact in-scope host/endpoint>

Summary
  Two or three sentences: what the bug is, who can trigger it, what it gives.

Steps to reproduce
  1. Log in as account A (attacker). Create an order; note id.
  2. Log in as account B (victim). Create an order; note id 1043.
  3. As account A, request GET /api/orders/1043.
  4. Observe B's data returned.

Evidence
  request/response pairs, screenshots, script.

Impact
  What an attacker gains, in business terms, at what scale.

Remediation
  Specific, testable fix.

References (optional)
  CWE, OWASP, prior art.
```

---

## Title

The title is the impact, not the class.

- Bad: "IDOR in /api/orders"
- Good: "Any customer can read any other customer's order history and PII via order id"

- Bad: "SSRF"
- Good: "Image importer reaches AWS metadata and returns instance credentials"

- Bad: "XSS in profile"
- Good: "Stored XSS in support ticket subject executes in the agent admin panel"

The title is what the triager puts in their queue. Make it say the consequence.

---

## Summary

Three sentences maximum:

1. What the endpoint does and what the bug is.
2. Who can trigger it and what they need.
3. What it gives them, at what scale.

No background, no "in today's world", no threat model essay.

---

## Steps to reproduce

- Numbered.
- Copy-pasteable.
- From a clean state (fresh browser, logged out).
- Every account named (A, B) and every id shown.
- No "then figure it out".

If a step needs a value only the program has (a specific tenant, an internal
host), name it in one line: `# requires a tenant id — any tenant works; used
1042 here`.

---

## Evidence

Raw HTTP beats prose. Include:

- The exact request that triggers it.
- The exact response showing impact.
- One screenshot for anything visual.
- The script if multi-step.

Redact tokens and third-party PII. Keep field names.

---

## Impact

Answer three questions:

1. **What data or capability?** Name the fields / the action.
2. **Whose?** One user, all users, another tenant, the platform.
3. **At what scale and cost?** One request, a loop, no rate limit.

Then one sentence on business consequence: regulatory (GDPR), financial, brand,
or platform integrity.

---

## Remediation

Specific and testable:

- Bad: "Sanitize input."
- Good: "In `GET /api/orders/{id}`, filter by `session.user_id` in the query:
  `Order.objects.get(id=id, user_id=request.user.id)`, returning 404 for
  non-owners. Apply the same to `/api/orders/{id}/items` and the CSV export."

A fix a developer can apply without asking is a fix that gets applied, which
gets your report marked resolved faster.

---

## Tone

- Neutral, technical, no drama.
- No "CRITICAL!!!", no bold everywhere.
- No speculation about what *might* be possible. Only what you showed.
- If something is unproven, say "unproven" and why.

---

## Common rejection reasons and the fix

| Rejection | Fix |
|---|---|
| "Cannot reproduce" | More exact steps; include the full request; state preconditions |
| "This is your own data" | Two-account proof with victim id |
| "Public information" | Show the field is private; compare anonymous vs authenticated |
| "Out of scope" | Quote the scope line; or drop it |
| "Known issue / duplicate" | See `22-triage-and-dedup.md` |
| "No impact" | Add the concrete impact sentence and the list-endpoint scale test |
| "By design" | Show the security consequence; if by design, accept |
| "Missing headers" | Do not report these alone |

---

## Length

Short is a feature. Most accepted reports are 200–500 words plus evidence. A
2,000-word report with one request reads as padding. A 300-word report with a
clear reproduction reads as competence.

---

## Before you submit

Run `checklists/submission.md`. It catches the rejections above.

---

## After you submit

- Respond to triage within a day.
- If asked for more evidence, give exactly what was asked, nothing more.
- If downgraded, one calm reply with the metric and the impact (`20-severity-and-cvss.md`).
- If resolved, ask (once) if disclosure is allowed; published reports compound
  your reputation.
- Keep hunting the same asset — you now know it better than anyone.
