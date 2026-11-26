# 20 — Severity and CVSS

Severity is the difference between a paid bug and a closed one. Triagers score
against CVSS and against the program's own matrix. Score honestly: inflation gets
downgraded and remembered; deflation gets you less than you earned.

---

## CVSS 3.1 in one page

CVSS 3.1 vector:

```
AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N
```

| Metric | Values | Notes |
|---|---|---|
| **AV** Attack Vector | N (network), A (adjacent), L (local), P (physical) | Web = N almost always |
| **AC** Attack Complexity | L (low), H (high) | H = needs a race, specific config, or prior info |
| **PR** Privileges Required | N, L, H | L = any user; H = admin |
| **UI** User Interaction | N, R (required) | R = victim must click/open |
| **S** Scope | U (unchanged), C (changed) | C = affects another security authority |
| **C** Confidentiality | N, L, H | H = full read of sensitive data |
| **I** Integrity | N, L, H | H = can modify any data |
| **A** Availability | N, L, H | Do not claim A without proof (DoS is usually excluded) |

### Score bands

| Score | Rating |
|---|---|
| 9.0–10.0 | Critical |
| 7.0–8.9 | High |
| 4.0–6.9 | Medium |
| 0.1–3.9 | Low |
| 0.0 | None |

Compute with `tools/cvss.py "<vector>"` — it prints the score and the band.

---

## Reference vectors by class

| Finding | Vector | Score |
|---|---|---|
| BOLA read of another user's PII | `AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N` | 6.5 |
| BOLA write/modify another user's data | `AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N` | 6.5 |
| Cross-tenant read (S:C) | `AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N` | 7.7 |
| Unauth admin panel | `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H` | 9.8 |
| RCE | `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H` | 9.8 |
| SQLi read only | `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N` | 7.5 |
| SSRF to metadata (creds) | `AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N` | 9.9–10 |
| SSRF internal only, no creds | `AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N` | 5.8 |
| Stored XSS (other users) | `AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N` | 5.4 |
| Reflected XSS | `AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N` | 6.1 |
| Open redirect | `AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N` | 3.1 |
| Account takeover (reset poisoning) | `AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H` | 8.8 |
| Public bucket, customer PII | `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N` | 7.5 |
| Internal doc disclosure, no PII | `AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N` | 5.3 |
| Missing headers | `AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:L/A:N` | 3.1 |
| Self-XSS | `AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:L/A:N` | 3.1 (often excluded) |

These are anchors, not gospel — adjust for what you actually demonstrated.

---

## The four severity questions

1. **Who can trigger it?** Anonymous (PR:N) vs user (PR:L) vs admin (PR:H).
2. **What does it give?** Read (C), write (I), both. Which data, whose.
3. **Does it cross a boundary?** Tenant, privilege, user. Scope C or not.
4. **How hard?** A race or a specific config = AC:H, which lowers the score.

Then check the program's own matrix. Some programs cap BOLA at Medium; some cap
XSS at Low. The program's table outranks CVSS for payout.

---

## Impact language that matches the score

Write impact as **what an attacker gains**, in business terms:

- Bad: "IDOR on /orders".
- Good: "Any authenticated customer can read any other customer's order
  history, including full name, address, phone, and payment last-4, by
  incrementing the order id. No rate limit."

- Bad: "SSRF".
- Good: "The image importer fetches any URL, including the AWS metadata endpoint,
  returning the instance role's temporary credentials. Those credentials have
  `s3:GetObject` on the production bucket."

The score follows the sentence. If the sentence is concrete, the score is
defensible.

---

## The inflation traps

| Trap | Reality |
|---|---|
| Calling a read of your own data "BOLA" | Not a bug |
| Claiming A:H (availability) without taking anything down | Do not |
| Claiming S:C when it is the same authority | S:U |
| Claiming "mass exploitation" from one id | Show a list endpoint or drop it |
| Calling demo data a breach | Check emails/timestamps first |
| Calling a public Firebase key a secret | It is public |
| Calling missing CSP a vuln | It is best practice |
| Calling a 200 with an empty body "exposure" | Show the data |

---

## The deflation traps (do not undersell)

| What you did | Do not call it |
|---|---|
| Read another tenant's data | "minor IDOR" — it is S:C, High |
| Live cloud key | "info" — it is Critical |
| ATO | "auth issue" — it is High |
| Unauth admin | "access control" — it is Critical |
| SSRF to metadata | "SSRF" — say "cloud credential theft" |

Name the impact, not the category. The category is in the title; the impact is in
the summary.

---

## When the program disagrees

If triage downgrades, do not argue with adjectives. Reply with:

1. The exact request/response that shows the impact they missed.
2. The metric you think is wrong and why (one line per metric).
3. The business consequence in one sentence.

One calm reply. If they hold, accept and keep hunting. Reputation compounds.
