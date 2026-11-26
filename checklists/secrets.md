# Checklist — Secrets

## Collection

- [ ] JS bundles downloaded and beautified.
- [ ] `manifest.json`, `asset-manifest.json`, `sw.js`, `env.js`, `config.js` checked.
- [ ] Source maps checked.
- [ ] `tools/secrets.py` run.

## Patterns

- [ ] `AKIA…` (AWS).
- [ ] `ghp_…` / `github_pat_…`.
- [ ] `xox[baprs]-…` (Slack).
- [ ] `sk_live_…` (Stripe).
- [ ] `SG.…` (SendGrid).
- [ ] `AIza…` (Google — check restriction).
- [ ] Private key blocks.
- [ ] Internal hostnames / admin paths (recon, not secret).

## Triage

- [ ] Known public type excluded (Firebase, `pk_live`, restricted Maps).
- [ ] Test fixture excluded (`AKIAIOSFODNN7EXAMPLE`, `xxxx`).
- [ ] Base64 noise decoded and excluded.

## Liveness

- [ ] One minimal call per candidate (`sts get-caller-identity`, `/user`, `/v1/account`).
- [ ] 401/403 → dead, not reported.
- [ ] 200 → live, identity captured.
- [ ] **No data enumeration, no mutation.**

## Blast radius

- [ ] AWS: IAM ARN / role inferred.
- [ ] GitHub: scopes + org.
- [ ] Stripe: live/test, restricted/full.
- [ ] Cloud: project + service account.

## Evidence

- [ ] Key redacted to first/last 4.
- [ ] One live call shown.
- [ ] Identity/scope stated.

## Severity

- [ ] Live cloud key → Critical.
- [ ] Live repo/CI token → High.
- [ ] Dead key / public config → Info.

## Verdict

- [ ] Works / Closed / Inconclusive written.
