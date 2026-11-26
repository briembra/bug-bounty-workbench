# 19 — Evidence and reproduction

A finding is a claim a triager can verify in under two minutes. Evidence is how
you make that possible. Sloppy evidence is the main reason real bugs get
rejected.

---

## The evidence contract

For every finding, capture:

1. **Exact request** — method, full URL, headers that matter (Cookie, Auth,
   Content-Type, custom), body. Redact only what is not needed to reproduce.
2. **Exact response** — status, relevant headers, the body slice that proves it.
3. **The minimal reproduction** — numbered, from a clean state, with the account
   that is acting.
4. **The artifact** — screenshot or video only where state is visual (a UI, a
   rendered XSS, a panel).
5. **The proof of ownership / sensitivity** — for cross-user bugs, the evidence
   that the data belongs to someone else.

Store in `findings/<slug>/`:

```
findings/<slug>/
  notes.md            # the reasoning, the timeline
  request-01.http
  response-01.http
  request-02.http
  response-02.http
  screenshot-01.png
  finding.yaml        # structured data for tools/report.py
  report.md           # final
```

---

## Writing a `.http` file (reproducible)

```
### Account A creates own order
POST /api/orders HTTP/1.1
Host: app.example.com
Cookie: session=A_SESSION_REDACTED
Content-Type: application/json

{"product":"sku-1","qty":1}

### Account B creates own order (second account)
POST /api/orders HTTP/1.1
Host: app.example.com
Cookie: session=B_SESSION_REDACTED
Content-Type: application/json

{"product":"sku-1","qty":1}

### Account A reads B's order (THE BUG)
GET /api/orders/1043 HTTP/1.1
Host: app.example.com
Cookie: session=A_SESSION_REDACTED
```

Triagers can replay these in Burp/VS Code REST client. That is the difference
between "trust me" and "here it is".

---

## Redaction that still proves

- Cookies/tokens: replace the value with `REDACTED`, keep the header name.
- PII: keep field names (`email`, `phone`, `address`), replace values with
  `REDACTED` or `b***@example.com`.
- Keep **one** unredacted value only if it is essential (e.g. an error string).
- Never paste a full dump. Show the shape: `{"email":"...","phone":"...",
  "address":"..."}` plus "N records returned".

---

## The two-account proof, in detail

The most common rejection: "this is the reporter's own data." Kill it:

1. **Create B's object with B's session.** Show B's `Set-Cookie` / login in the
   request chain.
2. **Show B's object id** in the response (`{"id":1043,"user":"b@..."}`).
3. **Use A's session** to fetch id 1043. Show A's cookie, B's id, B's data.
4. **Never use the same account twice** and never use a real user.

If you cannot create a second account (email verification, invite-only), say so
and use the strongest available proof — but a two-account test is the gold
standard and you should try hard to get it.

---

## Screenshots and video

- **Screenshots:** for rendered XSS (show the alert), a UI panel showing another
  user's data, an admin function succeeding.
- **Video:** for multi-step flows (race conditions, state machines) where a static
  screenshot cannot show sequence. Keep it short (<30 s) and narrate with text
  overlays, not voice.
- **Redact in the image**, not just in the caption. Triagers see the raw image.

---

## The reproduction script

When a bug needs many steps, write a script that reproduces it end-to-end from
two fresh logins. `tools/report.py` can embed it. The script is the strongest
evidence because it is runnable.

```python
# repro.py — BOLA on /api/orders/{id}
# usage: python repro.py <A_EMAIL> <A_PASS> <B_EMAIL> <B_PASS> <B_ORDER_ID>
```

Do not hardcode real credentials in the report; the script takes them as args.

---

## What "confirmed" means

A finding is confirmed only when **you** reproduced it from scratch **after**
writing the report. Not "I saw it once." Re-run the exact steps. If it fails the
second time (flaky, WAF, cache needed), it is not confirmed — investigate or
downgrade.

Three states, always named out loud:

- **Works** — reproduced twice, evidence captured.
- **Closed** — the control exists and holds.
- **Inconclusive** — you could not tell. Say so; do not guess.

---

## Evidence for each class (quick reference)

| Class | Minimum evidence |
|---|---|
| BOLA | two account sessions, victim id, attacker response with victim data |
| Auth bypass | request without/with forged auth → 200 + protected data |
| SQLi | request + response with `version()`/row |
| SSRF | listener hit with source IP, or metadata response |
| XSS | request + rendered response with executing payload, screenshot of alert |
| File read | request + first line of `/etc/passwd` or app config |
| Upload RCE | request + response showing `echo` output |
| Logic | the two requests that create the illegal state, and the resulting state |
| Secret | the key + one live API call + the identity it resolves to |
| Takeover | the subdomain serving your marker + the claim steps |
| Cache | poisoned response + anonymous HIT serving it |

---

## Timestamps and integrity

- Screenshot with a visible system clock if the claim is time-sensitive.
- Keep the raw HTTP as text — it is falsifiable and cheap to store.
- Do not edit evidence to look cleaner. If a response had a warning, leave it.

---

## The evidence test

Before submitting, ask: *if I had not written the summary, could a triager read
only the requests and responses and reach the same conclusion?* If no, the
evidence is not done.
