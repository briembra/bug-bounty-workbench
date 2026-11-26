# Checklist — Authentication

Run before submitting any auth finding.

## Surface

- [ ] Login endpoint identified and tested.
- [ ] Signup tested for duplicate/weird emails.
- [ ] Password reset flow walked end to end (your own email).
- [ ] Email change flow walked.
- [ ] MFA setup and verify tested.
- [ ] SSO/OAuth callback tested.
- [ ] Session/logout tested.

## Login

- [ ] Valid user + wrong pass vs invalid user: message/status/timing compared.
- [ ] Lockout exists or is absent/bypassable (tested with 3 attempts on your own account).
- [ ] API accepts only passwords the UI would accept (no empty/oversized/breached).
- [ ] Case/unicode duplicate signup tested.

## Reset

- [ ] Token length ≥128 bits.
- [ ] Token single-use (second use fails).
- [ ] Token expires (or expiry unreasonably long).
- [ ] New request invalidates old token.
- [ ] Password change invalidates token.
- [ ] Token bound to the user (test with your email + victim token).
- [ ] Host header / `X-Forwarded-Host` tested → email link to your listener.
- [ ] Step skipping tested (`/reset/complete` without token step).

## MFA

- [ ] Step skipping after first factor.
- [ ] OTP reuse.
- [ ] OTP brute force limited (tested 3 wrong, observed lockout).
- [ ] Disable MFA requires re-auth.
- [ ] Backup codes single-use, invalidated.

## SSO/OAuth

- [ ] `redirect_uri` exact match.
- [ ] `state` present and validated.
- [ ] Code single-use.
- [ ] PKCE enforced for public client.
- [ ] Account linking: pre-register + SSO auto-link tested.
- [ ] `email_verified` trusted from IdP that verifies.

## Session

- [ ] Cookie `HttpOnly`, `Secure`, `SameSite`.
- [ ] Session id rotates on login.
- [ ] Logout invalidates server-side (replayed old cookie).
- [ ] Password change invalidates other sessions.
- [ ] JWT: `alg`, sig verified, `exp`, `kid`, `jku` (`tools/jwt_tool.py`).
- [ ] No predictable session ids.

## Evidence

- [ ] Two accounts (or a clear reason why not).
- [ ] Request + response for the failing control.
- [ ] Chain proven if claiming ATO.
- [ ] Redaction done.

## Verdict

- [ ] Works / Closed / Inconclusive — written in notes.
