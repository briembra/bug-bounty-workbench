# 05 — Authentication and sessions

Authentication is who you are. Session management is how the server remembers.
Almost every HIGH in the last decade that was not BOLA was one of these two.

Hunt this class when you see: login, signup, password reset, email change, MFA,
SSO/SAML/OAuth, "remember me", magic links, API tokens, JWT cookies, session
cookies, device trust, "log out all devices".

---

## The authentication checklist (test all of it)

### Login

- [ ] **Response differential.** Valid user + wrong password vs invalid user +
      wrong password. Different message, status, or timing = user enumeration.
      (Enumeration alone is often excluded — see below — but it is a step toward
      a real bug.)
- [ ] **Lockout.** Is there one? Can it be bypassed by changing case, adding
      whitespace, using a different login endpoint, or by the mobile API? An
      absent or bypassable lockout on a password login is a finding if the
      program pays for it. Never actually brute force.
- [ ] **Password policy bypass.** Does the API accept a password the UI rejects?
      Does it accept an empty password, a very long password (DoS—skip), or a
      known-breached password?
- [ ] **Case/unicode confusion.** `User@x.com` vs `user@x.com` vs
      `user@x.com.` vs Unicode look-alikes. If signup accepts a case-duplicate,
      you may get a pre-account-takeover primitive.
- [ ] **Timing.** Constant-time comparison? A measurable difference between
      "user exists, wrong password" and "no user" is enumeration, sometimes
      exploitable at scale.

### Password reset

This is the highest-yield auth flow in bug bounty.

- [ ] **Host header injection.** `POST /forgot` with `Host: attacker.com` or
      `X-Forwarded-Host`. If the reset email links to `attacker.com/reset?token=`
      you have account takeover. Check the email body if you can receive it —
      use your own address.
- [ ] **Token properties.** Length (≥128 bits?), entropy, expiry, single-use,
      bound to user, invalidated on password change, invalidated on new request.
- [ ] **Token leakage.** In URL (referer leakage), in response body, in a
      redirect, in logs. Reset token reflected in HTML = XSS-adjacent.
- [ ] **Response manipulation.** `{"success":false}` → `{"success":true}`; does
      the *server* check, or only the client?
- [ ] **User binding.** Does the token work for a different email/username in the
      request body? `POST /reset` with victim's token and your email.
- [ ] **Step skipping.** Can you reach `/reset/complete` without the token step?
- [ ] **Email change flow.** Often the same code with a worse check. Changing
      email usually does not require the old email to confirm — that is the bug.

### MFA

- [ ] **Response manipulation** on the MFA step (client-side only check).
- [ ] **Step skipping** — go straight to `/dashboard` after step 1.
- [ ] **OTP reuse** — same code twice.
- [ ] **OTP brute force** — is it rate limited? (Do not actually brute force; test
      with 3 wrong codes and observe whether the account locks or the code stays
      valid.)
- [ ] **Backup codes** — predictable, reusable, not invalidated.
- [ ] **MFA removal** without re-auth.
- [ ] **Race** — two requests with the same valid OTP.

### SSO / OAuth / SAML

- [ ] **`redirect_uri` validation.** Exact match? Wildcard? Path traversal
      (`/callback/../evil`)? Open redirect chain? Missing scheme check
      (`javascript:`, `data:`)? This is the classic OAuth account takeover.
- [ ] **`state` parameter.** Present and validated? Missing state = CSRF on
      login = account linking attack.
- [ ] **Code reuse / PKCE.** Authorization code single-use? PKCE enforced for
      public clients?
- [ ] **`response_mode` / implicit** returning tokens in the fragment — XSS
      reachable.
- [ ] **SAML signature.** Is the assertion signed? Is the signature *validated*?
      XML signature wrapping. `Comment` injection in NameID.
- [ ] **`email_verified`** claim trusted from an IdP that does not verify.
- [ ] **Account linking.** Sign in with Google using an email that already has a
      password account — does it link, or take over?
- [ ] **Pre-registration takeover.** Register with `victim@company.com` before
      they sign up via SSO → their SSO login lands in your account.

### Sessions

- [ ] **Cookie flags.** `HttpOnly`, `Secure`, `SameSite`. Missing `SameSite` +
      state-changing GET = CSRF. Missing `HttpOnly` = XSS steals session.
- [ ] **Session fixation.** Does the session id change on login? If not, an
      attacker who sets it pre-login owns the session.
- [ ] **Session not invalidated** on logout, password change, or "log out all
      devices". Test: log in on A, log out on B, replay A's cookie.
- [ ] **JWT.** `alg:none`, algorithm confusion (RS256→HS256 with public key as
      secret), weak secret (`jwt_tool`), `kid` injection (path traversal / SQLi),
      `jku`/`x5u` pointing at attacker JWKS, missing `exp` check, missing
      signature check.
- [ ] **Predictable session ids.** Sequential, timestamp-based, short.
- [ ] **Concurrent sessions.** Allowed? Is there a device list? Can you kill
      another user's session by id?
- [ ] **Remember-me token.** Long-lived, reusable, not rotated, not bound.

---

## JWT: the five-minute test

```bash
# fingerprint
python tools/jwt_tool.py "<token>"

# none algorithm
python tools/jwt_tool.py "<token>" --attack none

# weak secret
python tools/jwt_tool.py "<token>" --attack crack --wordlist data/jwt-secrets.txt

# algorithm confusion (if you have the public key)
python tools/jwt_tool.py "<token>" --attack rs2hs --pubkey pub.pem
```

A forged admin token is HIGH. A JWT that merely lacks `exp` is Medium at best.

---

## Enumeration: when it counts

Email/username enumeration is on most exclusion lists. It stops being
Informational when:

- it feeds a brute force that has no lockout (then it is the brute force),
- it leaks a *sensitive* attribute (role, tenant, whether the account is
  disabled, last login),
- it is the first step of a pre-account-takeover (register the victim's email),
- it reveals internal accounts (`@company.com` staff).

If the program excludes enumeration, do not report the enumeration — report the
thing it enables, and only if you actually demonstrated it.

---

## Account takeover chains that pay

Rarely one bug. Usually a pair:

1. Enumeration + no lockout → credential stuffing surface (report only with a
   demonstrated account, never against a real user).
2. Host header injection in reset + user-controlled email → ATO.
3. OAuth `redirect_uri` bypass + no `state` → login CSRF → ATO.
4. Pre-registration + SSO auto-link → ATO without touching the victim.
5. XSS on a subdomain + cookie without `HttpOnly` + session not rotated → ATO.
6. JWT `kid` path traversal → sign your own token → admin.

When you find one half, write it down and hunt the other half. Half a chain is a
Medium; the chain is a HIGH.

---

## What "closed" looks like

So you do not over-report:

- Login returns identical message, status, and timing for both cases → closed.
- Reset token is 32 bytes, single-use, 15-min expiry, bound to user, invalidated
  on use → closed.
- `redirect_uri` requires exact string match against a registered list → closed.
- Session id rotates on login and is invalidated on logout → closed.
- JWT signed RS256, signature verified, `exp` enforced, `kid` resolved from a
  fixed map → closed.

Say "closed" out loud in your notes. It stops you circling back.
