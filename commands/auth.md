---
description: Hunt authentication and session flaws — reset poisoning, MFA skip, OAuth redirect abuse, JWT forgery.
argument-hint: <host>
allowed-tools: Bash, Read, Write, WebFetch
---

# /bbw-auth

`references/05`, `workflows/04`, `checklists/auth.md`, `tools/jwt_tool.py`.

**Input:** `$ARGUMENTS` — the host with the login surface.

```
/bbw-auth https://app.acme.com
```

Use **your own** email only. Never trigger a mail to an address you do not own.

---

## Step 1 — Map the surface

```
POST /login  /signup  /logout
POST /forgot  /reset  /reset/{token}  /change-password
POST /mfa/verify  /mfa/setup  /mfa/disable
GET  /oauth/authorize  /oauth/callback  /saml/acs
POST /email/change  /email/verify
GET  /me  /session
```

Write `auth.tsv`: endpoint, method, params, auth required, response shape.

## Step 2 — Login differential

- Valid user + wrong pass vs nonexistent user + wrong pass: message, status
  code, and response time. Differences = enumeration, usually Low, note only.
- Signup: case variants (`A@x.com` vs `a@x.com`), trailing dot, `+alias`.
- Does the API accept a password the UI rejects (empty, 1 char, 10k chars)?
- Lockout: three wrong attempts on **your** account, observe. Never brute force.

## Step 3 — Password reset (highest yield)

1. Trigger the reset for your own address. Capture the email.
2. Inspect the link: scheme, host, token length, token in path or query, expiry.
3. Reuse the token → must fail.
4. Request twice → the old token must die.
5. Change the password → the token must die.
6. **Host header:** re-trigger with `X-Forwarded-Host: <your listener>` and
   `Host: <your listener>`. If the emailed link points at your listener, that is
   reset poisoning → ATO. `references/25` has the chain.
7. Send `POST /reset` with your token and a different email in the body.

## Step 4 — Response manipulation

Intercept the login/MFA response:

```
{"success":false}   → {"success":true}
{"mfa_required":true} → false
{"role":"user"}     → {"role":"admin"}
```

Only a bug if the **server** honours it. Client-side only = note, usually excluded.

## Step 5 — MFA

- Step skipping: after factor one, request the post-login page directly.
- OTP reuse: submit the same code twice.
- OTP brute force: observe the lockout after 3 wrong codes; do not continue.
- Disable MFA without re-authentication.
- Backup codes: reusable, predictable, not invalidated.
- Enrol a second device without confirming the first.

## Step 6 — OAuth / SSO

```
redirect_uri exact match? try:
  https://target/callback/../evil
  https://evil.target.com
  https://target.com.evil.com
  https://target/callback?next=https://evil.com
  //evil.com
state present and validated? remove it → login CSRF
code single use? replay it
PKCE enforced for public clients?
Account linking: register the victim's email first, then "sign in with Google"
```

Token theft through `redirect_uri` + an open redirect = Critical chain.

## Step 7 — Session and JWT

```bash
curl -sD- https://<host>/ | grep -i set-cookie
python tools/jwt_tool.py "<token>"
python tools/jwt_tool.py "<token>" --attack crack --wordlist data/jwt-secrets.txt
python tools/jwt_tool.py "<token>" --attack none
```

Check: `HttpOnly`, `Secure`, `SameSite`; id rotates on login; logout invalidates
server-side (replay the old cookie); password change kills other sessions; `exp`
enforced; `alg:none` rejected; `kid` not traversable.

---

## Output shape

```
controls tested: N
broken: <control> — <what it allows>
chain: <link A> + <link B> = <impact>
severity: <band>
next: /bbw-score or /bbw-report
```

## Stop conditions

- A test needs an email to a non-owned address → do not.
- OTP guessing beyond the observed lockout → do not.
- Real victim accounts → never; own accounts only.
