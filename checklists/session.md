# Checklist — Session

## Cookies

- [ ] `HttpOnly` present.
- [ ] `Secure` present.
- [ ] `SameSite` set (Lax/Strict; None requires Secure).
- [ ] Scope (`Domain`, `Path`) minimal.
- [ ] No session in URL.

## Lifecycle

- [ ] Session id changes on login (no fixation).
- [ ] Logout invalidates server-side (old cookie replayed → 401).
- [ ] Password change invalidates other sessions.
- [ ] "Log out all devices" works.
- [ ] Concurrent sessions listed/killable.
- [ ] Remember-me token rotated, bound, revocable.

## Tokens

- [ ] JWT `alg` is a strong algorithm (`none` rejected).
- [ ] Signature verified server-side.
- [ ] `exp` enforced.
- [ ] `kid` resolved from a fixed map (no traversal/SQLi).
- [ ] `jku`/`x5u` not attacker-controlled.
- [ ] Secret not weak (`tools/jwt_tool.py --attack crack`).

## CSRF

- [ ] Token present on mutating requests.
- [ ] Token validated on every method (`PUT`/`DELETE` too).
- [ ] `Origin`/`Referer` checked.
- [ ] JSON endpoint rejects `text/plain` (no simple-request bypass).

## Evidence

- [ ] Replay-after-logout request + response.
- [ ] Forged token request + response (if applicable).
- [ ] Redaction done.

## Severity

- [ ] Fixation / no logout → Medium–High.
- [ ] Forged JWT to admin → Critical.
- [ ] Missing flags alone → Low/Info (often excluded).

## Verdict

- [ ] Works / Closed / Inconclusive written.
