---
description: Check a finding against existing reports before submitting — duplicates, prior art, known-by-design.
argument-hint: <slug or class + asset>
allowed-tools: Bash, Read, WebFetch, WebSearch
---

# /bbw-dedup

`references/22`, `workflows/13`, `prompts/dedup-analyst.md`.

**Input:** `$ARGUMENTS` — the finding slug, or class + asset.

```
/bbw-dedup orders-bola
/bbw-dedup "cache poisoning app.example.com"
```

A duplicate is not just unpaid — it burns triager patience. Five minutes here saves
a week of arguing.

---

## Step 1 — Check the program's own record

- **Disclosed reports** on the program page: filter by the same asset and class.
- **Hacktivity / public feed** on the platform: search the asset name.
- The program's **changelog / announcements**: did they already fix or acknowledge
  this class?
- Their **exclusion list**: is this class explicitly out of scope today?

## Step 2 — Check the public record

```
site:hackerone.com "<asset>" <class>
site:bugcrowd.com "<asset>" <class>
"<asset>" "<endpoint or param>" writeup
"<class>" "<technology>" <year>
```

Also: the vendor's own security advisories, CVE databases for their product,
GitHub issues on their open-source components.

## Step 3 — Ask the four dedup questions

| Question | If yes |
|---|---|
| Has the exact endpoint + class been reported publicly? | likely dup — say so |
| Has the same class been reported on the same asset (different endpoint)? | partial dup — argue scope |
| Is this **known and accepted as designed**? | not a bug |
| Is this already on the exclusion list? | not a bug |

## Step 4 — Argue scope, not novelty

If it is a **partial duplicate**, your case is:

- Different endpoint, different handler, different fix → separate report
- Same endpoint, different impact (read vs write) → separate, higher severity
- Different asset entirely → separate

Write that one line in the report: *"This is a distinct handler from report #12345
— the fix for that one does not cover `/api/orders/{id}/items`."*

If it is the **same thing**, do not submit. Note it and move on.

## Step 5 — Prior art improves the report

Public writeups give you:

- the exact technique the triager already understands
- the standard remediation they expect
- the severity they historically assigned

Use it to match their expectations, not to copy.

## Step 6 — Log it

`findings/<slug>/dedup.md`:

```
checked: program disclosed list, hacktivity, public search
closest match: #12345 — /api/orders/{id} (same handler? no)
verdict: distinct
reason: different handler, higher impact (write vs read)
```

That file is your defence if the triager calls dup.

---

## Output shape

```
checked: <sources>
closest: <report id or none>
verdict: distinct | partial-dup | duplicate | by-design
argument: <one line if not distinct>
next: /bbw-submit | drop
```

## Stop conditions

- Exact duplicate → do not submit; keep hunting the same asset for a different bug.
- By design → do not submit.
- Unsure between distinct and partial → submit, and pre-empt it with the one-line
  distinction in the report. Triagers prefer that to a silent duplicate.
