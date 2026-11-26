---
description: Final gate before submitting — checklist, platform fields, redaction, disclosure window.
argument-hint: <slug> [platform]
allowed-tools: Bash, Read, Write
---

# /bbw-submit

`checklists/submission.md`, `workflows/12`, `templates/report-*.md`.

**Input:** `$ARGUMENTS` — the slug with a finished `report.md`.

```
/bbw-submit orders-bola intigriti
```

Nothing new is discovered here. This is the gate that stops a good finding going out
with a hole in it.

---

## Step 1 — The report exists and is complete

- [ ] `findings/<slug>/report.md` exists
- [ ] Title names asset + class + impact
- [ ] Summary is three sentences or fewer
- [ ] Steps reproduce from a clean state
- [ ] Evidence attached (request/response, not just a screenshot)
- [ ] Impact states attacker gain, not the class name
- [ ] Remediation is specific and testable
- [ ] Version, date and account roles are stated

Any box empty → back to `/bbw-report`.

## Step 2 — The evidence pack

- [ ] Cookies and tokens replaced with `<A session>`, `<token>`
- [ ] Real PII redacted, one example value kept where it proves impact
- [ ] No other researchers' artefacts in the captures
- [ ] No credentials you intend to keep secret are in the report
- [ ] Listener logs included for blind bugs
- [ ] Screenshots show the URL bar and the account context

## Step 3 — Scope and rules still hold

- [ ] Asset is in the current published scope
- [ ] Class is not excluded
- [ ] Test stayed inside the rate limits
- [ ] No test account was left behind
- [ ] Any object you created and could delete has been deleted
- [ ] Any test data has been removed

## Step 4 — Fill the platform form

| Field | Value |
|---|---|
| Title | from `report.md` |
| Asset | exact in-scope entry, as the program listed it |
| Severity | from `/bbw-score`, matching their band |
| Weakness / CWE | best match; BOLA → CWE-639, SSRF → CWE-918 |
| CVSS | vector or 0.0 if they use their own scale |
| Description | summary + steps + impact + fix |
| Attachments | evidence pack |
| Disclosure | per their policy, default: private |

Never mark public before the program sets the disclosure date.

## Step 5 — The pre-send read

Read the whole report once as the triager:

- Can I reproduce this in 5 minutes?
- Do I know which account is the victim?
- Is the impact clear in one line?
- Is there any sentence that is speculation?

Cut every sentence that does not help them reproduce or understand impact.

## Step 6 — Submit and log

```
findings/<slug>/submitted.md
  platform: <name>
  report id: <id>
  submitted: <timestamp UTC>
  severity requested: <band>
  status: triaged | new
```

Then:

1. Report back to the user with the id and the requested severity.
2. Keep hunting the same asset — a submitted bug is a better map, not a finish line.
3. Watch the inbox for triage questions and answer with evidence, not opinion.

## Step 7 — If it comes back rejected

- Ask which part failed to reproduce or which exclusion applies.
- Provide the missing artefact, once.
- Accept the decision if it is correct; say so to the user and move on.
- Do not resubmit the same finding under a new title.

---

## Output shape

```
slug: <slug>
checklist: pass
severity requested: <band>
submitted: <platform> — <report id>
left behind: none | <list>
next: <next asset or class>
```

## Stop conditions

- Any checklist item fails → fix it, do not submit.
- Scope changed since testing → re-verify before submitting.
- Real third-party PII in the pack → redact, then submit.
- The program forbids public disclosure → keep it private until they say otherwise.
