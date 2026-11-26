# 25 — Chaining and escalation

A single Low is a Low. Two Lows in a chain can be a High. Most "how did they get
that payout" stories are chains. This document is how to think in chains without
inventing impact you did not prove.

---

## The chain rule

A chain is legitimate only if **every link is proven** and the composition is a
real path an attacker would take. If one link is assumed, the chain is a
hypothesis, not a finding.

Write the chain as a sentence before you test it:

```
[pre-condition] + [bug A] + [bug B] = [impact]
```

Example:

```
An attacker who can set the Host header + password reset builds links from it
+ the victim opens the emailed link = account takeover.
```

Every clause must be something you can show.

---

## The productive chains

### 1. Enumeration → credential attack → ATO

- Link A: login reveals valid emails (no lockout).
- Link B: weak password policy accepts a known-breached password.
- Impact: account takeover at scale.
Only report if you can show B on an account you control. Never attack a real user.

### 2. Host header injection → reset poisoning → ATO

- Link A: reset email builds the link from `Host`/`X-Forwarded-Host`.
- Link B: you receive the email (your own address) pointing at your listener.
- Impact: a victim who clicks the link hands you their reset token.
Report with the email body as evidence. Do not involve a real victim.

### 3. Open redirect → OAuth `redirect_uri` → token theft → ATO

- Link A: `redirect_uri` validation is bypassable via an open redirect on the
  IdP's allowlisted domain.
- Link B: the code/token lands at the redirect target you control.
- Impact: ATO.

### 4. Self-XSS → CSRF-like form → stored XSS

- Link A: self-XSS in a field.
- Link B: a request that writes to that field can be triggered cross-site.
- Impact: stored XSS for the victim.

### 5. XSS → cookie theft → session reuse

- Link A: XSS executes.
- Link B: cookie lacks `HttpOnly`, session not rotated.
- Impact: ATO.

### 6. SSRF → internal service → credential

- Link A: URL fetch reaches localhost.
- Link B: an internal service returns a token.
- Impact: cloud/internal compromise.

### 7. IDOR → admin object → privilege escalation

- Link A: read an object belonging to an admin (e.g. an invite, a config).
- Link B: use a value from it (token, id) to perform an admin action.
- Impact: admin.

### 8. Business logic → free goods → fraud at scale

- Link A: price manipulation to €0.
- Link B: no rate limit / no fraud check.
- Impact: financial loss at scale.

---

## When a chain is NOT a finding

- The composition requires the victim to be an attacker (self-XSS chains).
- A link needs a precondition the attacker cannot achieve.
- A link is theoretical ("if the token were predictable").
- The impact is "could lead to" not "did lead to".
- The chain crosses out of scope at a link.

If you cannot prove all links, report the **strongest single link** at its true
severity, and mention the potential chain in one sentence as unproven. Do not
inflate.

---

## Escalation within one bug

Sometimes the bug is one, but the impact is bigger than you first thought.
Ask:

- **Scale.** Is it one object or a list endpoint? Test the collection once.
- **Sensitivity.** Are there more fields than you assumed? A PII field in the
  same response changes the score.
- **Breadth.** Does the same code serve other roles/tenants?
- **Persistence.** Can the attacker keep access (token, backdoor account)?
- **Automation.** Is there a rate limit? No limit = scale.

A BOLA read of a display name is Low. The same bug returning email + address +
order history, with no rate limit, is High. Same bug, proven impact, higher score.

---

## The pre-condition ladder

Order your chains by how easy the pre-condition is:

| Pre-condition | Ease |
|---|---|
| Anonymous, one request | Easiest — highest severity |
| Any authenticated user | Common |
| Victim interaction (click) | Medium |
| Specific config / race | Hard — lowers CVSS AC |

A chain that needs no authentication and no interaction is the best finding you
can get. If your chain needs a rare config, say so and score `AC:H`.

---

## Reporting a chain

Structure the report as the chain:

```
Title: Account takeover via Host header injection in password reset

Summary: The reset endpoint builds the link from the X-Forwarded-Host header.
An attacker who requests a reset for a victim's email, with a forged host, causes
the victim's reset email to point at the attacker's domain. When the victim
clicks, the reset token is sent to the attacker, who sets a new password.

Steps:
1. ... (forged host)
2. ... (email received at your address, body shown)
3. ... (attacker uses token)
```

Each step is a link. Each link has evidence. The triager walks the chain once and
accepts.

---

## The chain mindset

When you find a Low, do not discard it. Ask: **what does this unlock?** Save it in
`notes.md` as a link. Hunt the other links. The repository of half-chains is where
your first High comes from.

Conversely: when a program says "Low, no impact," the chain in your notes is the
reply — if and only if you proved it.
