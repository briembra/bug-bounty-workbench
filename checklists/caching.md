# Checklist — Caching and protocol

## Cache detection

- [ ] `X-Cache` / `CF-Cache-Status` / `Age` observed.
- [ ] Static extensions cached; dynamic decision noted.

## Poisoning

- [ ] `X-Forwarded-Host` reflected and cached.
- [ ] `X-Forwarded-Scheme` / `Forwarded` tested.
- [ ] Unkeyed query params (`utm_`, `cb`, `x`) reflected.
- [ ] Cookie reflected but not keyed.
- [ ] Marker cached and served anonymously.
- [ ] Harmless marker used (no real payload on live page).

## Deception

- [ ] Authenticated page fetched with `.css`/`.js`/`.png` suffix.
- [ ] Second anonymous request served the private page → leak.
- [ ] Variants (`;`, `%00`, `?`, `..%2f`) tested.

## Host header

- [ ] `Host: evil.com` → absolute URLs / redirect.
- [ ] `X-Forwarded-Host` in reset email → your listener (own account only).
- [ ] `X-Forwarded-For: 127.0.0.1` routing.

## Protocol

- [ ] Smuggling only if explicitly allowed (else note suspicion).
- [ ] Absolute-URI request line tested for internal routing.

## Evidence

- [ ] Poisoned response + anonymous HIT.
- [ ] Exact header/param used.
- [ ] Purge requested or URL noted.

## Severity

- [ ] Cached XSS → High–Critical.
- [ ] Cache deception PII → High.
- [ ] Host header reset → Critical.
- [ ] Missing `Vary` alone → Info.

## Verdict

- [ ] Works / Closed / Inconclusive written.
