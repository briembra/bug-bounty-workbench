---
description: Turn a lead into a chained exploit — link impact, build the kill chain, prove the end state.
argument-hint: <finding or host>
allowed-tools: Bash, Read, Write, WebFetch
---

# /bbw-chain

`references/25`.

**Input:** `$ARGUMENTS` — a confirmed low/medium finding you want to escalate, or a
host where several small issues exist.

```
/bbw-chain "open redirect on /login?next="
/bbw-chain https://app.acme.com
```

Most High and Critical reports are chains. A low on its own is a note; a low that
feeds a token into a critical endpoint is a payout.

---

## Step 1 — List what you actually have

Only confirmed items, each with evidence:

| # | Finding | Severity alone | What it gives you |
|---|---|---|---|
| 1 | Open redirect on `/login` | Low | control of a redirect after auth |
| 2 | `redirect_uri` loose match | Low | auth code to my host |
| 3 | Tokens in URL fragment | Info | code → token |
| 4 | No session rotation | Low | stolen token survives |

## Step 2 — Find the joins

Ask, for each pair: **does the output of A become the input of B?**

Common joins:

- open redirect + OAuth `redirect_uri` → token theft → ATO
- self-XSS + CSRF → stored XSS that fires for the victim
- SSRF + metadata → cloud credentials → data access
- IDOR read + email change → ATO
- cache deception + authenticated page → private data
- host header injection + password reset → token theft → ATO
- XSS + no `HttpOnly` + no rotation → session hijack
- prototype pollution + gadget → RCE (client or server)
- subdomain takeover + cookie scope → session theft
- API mass assignment + admin role → vertical escalation
- secrets in JS + internal API → bypass WAF and auth

## Step 3 — Write the chain as a sequence

```
1. Victim clicks https://acme.com/login?next=https://acme.com.attacker.com
2. Server sets redirect_uri to attacker.com after OAuth
3. IdP returns code to attacker.com?code=...
4. Attacker exchanges code for token (no PKCE)
5. Token grants victim account
```

Every arrow must be a request you can show or a documented behaviour. If an arrow
is a guess, the chain is a guess.

## Step 4 — Prove each link, in order

Reuse the evidence from the individual findings, then add the **join** requests:

- the request that carries A's output into B
- the response that shows the escalated state

The last artefact is the money shot: the victim account's data, the admin action,
the internal service, the token that works.

## Step 5 — Score the chain, not the links

`/bbw-score` on the end state.

| End state | Severity |
|---|---|
| Account takeover | High–Critical |
| Cross-tenant data at scale | High–Critical |
| RCE | Critical |
| Internal network read | High |
| Privilege escalation within tenant | Medium–High |
| Phishing on the brand domain only | Low–Medium |

## Step 6 — Write it so the triager follows

Order the report by the chain, not by discovery order:

```
Summary: open redirect + loose redirect_uri = account takeover
Chain:
  1. ...
  2. ...
Impact: any user who clicks one link loses their account
Evidence: request/response pairs numbered per step
```

A chain report fails when the triager cannot reproduce link 2. Test your own report
by following it from a clean browser.

---

## Output shape

```
links: N   confirmed links: N
chain: <A> + <B> → <impact>
end state: ATO | data | RCE | escalation
evidence: findings/<slug>/chain-*
severity: <band>
next: /bbw-report
```

## Stop conditions

- A link is unproven → report the individual findings at their real severities,
  name the unproven join in one line. Do not write it as a chain.
- A chain needs a real victim to click → test with your own two accounts, and state
  the victim-click requirement in the report.
- A chain needs DoS or brute force → not a chain, drop it.
