# Checklist — Subdomain takeover

## Detection

- [ ] CNAME inventory built.
- [ ] Third-party targets filtered.
- [ ] Fingerprint matched (`data/takeover-fingerprints.txt`).
- [ ] 404 alone not treated as proof.

## Claimability

- [ ] Resource name is free in the provider.
- [ ] You can create it in your own account.
- [ ] Provider still routes the subdomain to the claimed resource.
- [ ] If unclaimable → labelled dangling CNAME, not takeover.

## Proof

- [ ] Harmless marker served (`bbh-takeover-<rand>`).
- [ ] `curl` shows the marker.
- [ ] Request/response + screenshot captured.
- [ ] Resource **deleted** immediately.
- [ ] Nothing else served, no visitor logging.

## Trust

- [ ] Cookie scope on parent checked.
- [ ] OAuth `redirect_uri` allowlist checked.
- [ ] Email (SPF/MX) relevance checked.
- [ ] Brand/`www` status checked.

## Severity

- [ ] `www`/brand → High–Critical.
- [ ] Cookie/OAuth/email trust → High–Critical.
- [ ] `dev`/`test` → Medium.
- [ ] Dangling, unclaimable → Low/Info.

## Evidence

- [ ] DNS record.
- [ ] Fingerprint.
- [ ] Claim steps.
- [ ] Marker response.
- [ ] Deletion confirmation.

## Verdict

- [ ] Works / Closed / Inconclusive written.
