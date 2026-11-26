# Workflow 04 — Hunt auth bypass

Run this on any app with login, signup, reset, MFA, or SSO. Time box: 2 hours.

---

## Step 1 — Map the auth surface (15 min)

List every auth-related endpoint from JS/docs/network:

```
POST /login, /signup, /logout
POST /forgot, /reset, /reset/{token}, /change-password
POST /mfa/verify, /mfa/disable, /mfa/setup
GET  /oauth/authorize, /oauth/callback, /saml/acs
POST /email/change, /email/verify
GET  /me, /session
```

Write `auth.tsv`: endpoint, method, params, auth required.

---

## Step 2 — Login checks (20 min)

- Valid user + wrong password vs invalid user + wrong password: message, status,
  timing.
- Case/unicode duplicates on signup.
- Does the API accept a password the UI rejects?
- Is there a lockout? Try 3 wrong passwords on **your** account, observe.

Never brute force a real account.

---

## Step 3 — Password reset (30 min)

This is the highest-yield step. Use **your own** email only.

- Trigger reset. Capture the email (use a catch-all inbox you control).
- Inspect the link: host, token length, token in path or query, expiry.
- Re-use the token → should fail.
- Request twice → old token should die.
- Change the password → token should die.
- **Host header injection:** re-trigger with `X-Forwarded-Host: <your list listener>`
  and `Host: <listener>`. If the email link points at your listener → ATO.
- Try `POST /reset` with victim token + your email in the body.

If any of these works, you have a chain — see `25-chaining-and-escalation.md`.

---

## Step 4 — Response manipulation (10 min)

Intercept the auth response where possible:

- `{"success":false}` → `{"success":true}`.
- `{"mfa_required":true}` → `false`.
- `{"role":"user"}` → `{"role":"admin"}`.

If the *server* honours it, you have a bug. If only the client does, note it and
move on (usually Medium at best, often excluded).

---

## Step 5 — MFA (20 min)

- Step skipping: after step 1, request the post-login page directly.
- OTP reuse: submit the same code twice.
- OTP brute force: check the lockout after 3 wrong codes (do not go further).
- Disable MFA without re-auth.
- Backup codes: predictable, reusable, not invalidated.

---

## Step 6 — SSO/OAuth (20 min)

- `redirect_uri`: exact match? Try `https://target/callback/../evil`,
  `https://evil.target.com`, `https://target.com.evil.com`, `//evil.com`,
  `javascript:`.
- `state` present and validated? Remove it → login CSRF.
- Authorization code reuse.
- Account linking: register victim's email first, then SSO → takeover.
- SAML: signed? validated? XML wrapping? (advanced)

---

## Step 7 — Session (15 min)

- Cookie flags: `HttpOnly`, `Secure`, `SameSite`.
- Session id changes on login? (fixation)
- Logout invalidates server-side? (replay the old cookie)
- Password change invalidates other sessions?
- JWT: `python tools/jwt_tool.py "<token>" --attack none` and `--attack crack`.

---

## Step 8 — Prove and write (20 min)

For an ATO, show:

1. The reset request with the forged host.
2. The email body landing at your listener (screenshot/raw).
3. The token use → password changed.
4. Login with the new password.

Run `checklists/auth.md`. Write the report with the chain structure.

---

## Definition of done

- [ ] Auth surface mapped.
- [ ] Login differential tested.
- [ ] Reset flow tested incl. host header.
- [ ] Response manipulation tested.
- [ ] MFA tested.
- [ ] SSO tested.
- [ ] Session/JWT tested.
- [ ] Evidence captured.

If all controls hold, write "closed" and pick the next class.
