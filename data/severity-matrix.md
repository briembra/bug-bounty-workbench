# Severity matrix

Use this as an anchor. The program's own matrix outranks it for payout; CVSS
outranks it for triage. Score what you demonstrated.

---

## By demonstrated impact

| Impact | Severity | Typical CVSS |
|---|---|---|
| RCE on a production host | Critical | 9.0–10.0 |
| Unauth admin access to the platform | Critical | 9.0–10.0 |
| Cloud credential takeover (metadata/keys) | Critical | 9.0–10.0 |
| Cross-tenant read or write of PII | Critical/High | 8.0–9.5 |
| Read another user's payment/financial data | High | 7.0–8.0 |
| Read another user's PII (email/phone/address) | High | 6.5–7.5 |
| Modify another user's object | High | 6.5–7.5 |
| Admin function reachable by normal user | High | 7.0–8.5 |
| Account takeover | High | 7.5–8.8 |
| SSRF to internal service with data | High | 7.0–8.5 |
| SQLi with data read | High | 7.5–8.5 |
| Stored XSS in an admin/agent panel | High | 6.5–8.0 |
| Upload that executes code | Critical | 9.0–10.0 |
| Public bucket with customer data | High–Critical | 7.5–9.5 |
| Live cloud key with real scope | Critical | 9.0–10.0 |
| Business logic: buy for €0 | High–Critical | 7.5–9.5 |
| Refund > paid | High | 7.0–8.0 |

## By weaker signal

| Impact | Severity |
|---|---|
| Read one non-sensitive field of another user | Low |
| Stored XSS on a low-traffic public page | Medium |
| Reflected XSS | Low–Medium |
| Internal document disclosure, no PII | Medium (5.3) |
| SSRF blind, DNS only, no internal reach | Medium (often excluded) |
| Cache deception leaking a non-sensitive page | Medium |
| Open redirect without a chain | Low (often excluded) |
| Subdomain takeover with no trust | Medium |
| Trial reset only | Low |
| IDOR on public metadata | Low |
| Rate-limit absence without demonstrated attack | Low/Info |
| Missing security headers | Info |
| Version banner | Info |
| Self-XSS | Info (usually excluded) |
| CSV injection | Low (usually excluded) |
| Email enumeration alone | Low (usually excluded) |

---

## The multipliers

- **Cross-tenant** → raise one band. Vendor's core promise broken.
- **No authentication required** → raise. `PR:N`.
- **No rate limit + list endpoint** → raise. Scale is part of impact.
- **Persistent access** (token, backdoor) → raise.
- **Victim interaction required** → lower within band.
- **Specific config / race required** → `AC:H`, lower.
- **Demo/seed data** → lower to Medium or below; say so.

---

## The three lies that get you downgraded

1. "Mass exploitation" from one id — prove the list endpoint or drop it.
2. "Availability impact" without taking anything down — remove `A:H`.
3. "Sensitive data" when the response is your own or public — show ownership and
   sensitivity, or drop it.
