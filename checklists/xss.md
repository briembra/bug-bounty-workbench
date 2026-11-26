# Checklist — XSS

## Discovery

- [ ] Input points that render listed.
- [ ] Unique marker traced to the raw response.
- [ ] Context identified (body / attribute / script / URL).

## Reflection

- [ ] Context-matched payload tested.
- [ ] Encoded output recognised (not a finding).
- [ ] WAF bypass tried (case, alternate tags, encoding).
- [ ] Execution confirmed (alert/beacon).

## Stored

- [ ] Payload persists after reload.
- [ ] Fires for a second role (admin/agent) if reachable.
- [ ] Blind payload beacons out (`interactsh`).

## DOM

- [ ] `innerHTML`/`eval`/`location.hash` sinks traced.
- [ ] Fragment payload tested (`#<img src=x onerror=…>`).
- [ ] `postMessage` origin check tested.

## Impact chain

- [ ] Cookie `HttpOnly` checked.
- [ ] CSP checked (`unsafe-inline`, wildcard, JSONP).
- [ ] Session rotation on login checked.
- [ ] Change-email/password callable from the payload.

## Evidence

- [ ] Request with payload captured.
- [ ] Screenshot of execution (alert) or beacon hit.
- [ ] Chain stated if ATO.

## Severity

- [ ] Reflected only → Low.
- [ ] Stored, fires for users → Medium.
- [ ] Stored in admin/agent panel, or chain to ATO → High.

## Verdict

- [ ] Works / Closed / Inconclusive written.
