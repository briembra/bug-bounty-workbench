# Checklist — SSRF

## Sinks

- [ ] All URL/host/webhook/import params listed.
- [ ] Each tested against a listener.

## Fetch proof

- [ ] Listener hit with server User-Agent and datacenter IP → server-side.
- [ ] Or: no hit → **not SSRF** (stored only); recorded.

## Reach

- [ ] `127.0.0.1`, `localhost`, `[::1]`, `0.0.0.0`.
- [ ] Decimal/hex/octal IP forms.
- [ ] Localhost service identified (header/body).
- [ ] RFC1918 hosts tried (one, not a scan).

## Metadata

- [ ] AWS IMDSv1.
- [ ] AWS IMDSv2 (token; or redirect bypass).
- [ ] GCP (header requirement noted).
- [ ] Azure (header requirement noted).
- [ ] Other providers (DO, Alibaba, Oracle, K8s).
- [ ] Credentials redacted to first/last 4; **not used**.

## Bypass

- [ ] `nip.io` / `sslip.io` / rebinding.
- [ ] Redirect from listener to internal.
- [ ] `file://`, `gopher://`, `dict://`.
- [ ] URL parsing confusion (`@`, `#`).

## Generators

- [ ] PDF/screenshot generator runs JS.
- [ ] DevTools endpoint (`:9222/json`) reachable.
- [ ] `file://` in iframe + screenshot tested.

## Evidence

- [ ] Exact bypass string recorded.
- [ ] Response or listener hit captured with source IP.
- [ ] Impact stated (localhost / internal / metadata).

## Severity

- [ ] Blind DNS only → Medium and labelled blind.
- [ ] Internal reach → High.
- [ ] Metadata creds → Critical.

## Verdict

- [ ] Works / Closed / Inconclusive written.
