# Checklist — Submission gate

Run top to bottom. If anything fails, fix it before submitting.

## Scope

- [ ] Asset is in scope (quoted from scope.json / program page).
- [ ] Not on an exclusion list.
- [ ] Class is not excluded by the program.

## Validity

- [ ] Reproduced twice from a clean state.
- [ ] Not a duplicate (disclosed reports + search engines checked).
- [ ] Not a known issue (changelog checked).
- [ ] Not demo/seed data (emails, timestamps, ids checked).

## Evidence

- [ ] Exact request(s) captured.
- [ ] Exact response(s) with impact captured.
- [ ] Two-account proof (for cross-user bugs).
- [ ] Cross-user data proven to be the victim's.
- [ ] Data proven sensitive, not public.
- [ ] Redaction done (tokens, PII).
- [ ] Screenshot/video where visual.

## Impact

- [ ] Impact written in business terms (fields, scale, who).
- [ ] Scale tested (list endpoint if claimed).
- [ ] CVSS vector matches the impact sentence (`tools/cvss.py`).
- [ ] No inflation (A:H without DoS? mass without list?).

## Report

- [ ] Title is the impact, noun phrase.
- [ ] Summary ≤3 sentences.
- [ ] Steps numbered, copy-pasteable, from clean state.
- [ ] Remediation specific and testable.
- [ ] `tools/report.py finding.yaml --dry-run` passes.

## Hygiene

- [ ] Test objects cleaned up.
- [ ] Uploaded files/shells removed.
- [ ] Live proof (takeover) deleted.
- [ ] No real customer data retained beyond proof.
- [ ] No third party contacted.

## Submit

- [ ] Platform fields filled (asset, severity, CWE, CVSS).
- [ ] Evidence attached.
- [ ] Report id recorded in `notes.md`.

## After

- [ ] Triage responded to within a day.
- [ ] Dedup/severity replies calm and evidence-based.
- [ ] Same asset re-mapped for a second bug.
