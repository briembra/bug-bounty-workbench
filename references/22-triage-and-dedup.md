# 22 — Triage and deduplication

Most reports are not rejected for being wrong. They are rejected for being
duplicates, out of scope, or unproven. This document is how to lose fewer.

---

## Before you write: the dedup check

Five minutes of checking saves a rejected report.

1. **Disclosed reports.** Search the program's disclosed/hacktivity feed for the
   endpoint, the parameter, and the class.
   - HackerOne: `hackerone.com/<program>/hacktivity`, filter disclosed.
   - Bugcrowd: program "Activity".
   - Intigriti: program "Reports" (public ones).
2. **Search engines.** `site:target.com <endpoint>` and
   `<endpoint> site:hackerone.com`.
3. **The program's changelog / release notes.** If they shipped a fix that
   matches your bug, it is likely known.
4. **Public writeups.** `target + vulnerability class + writeup`.
5. **Your own notes.** Have you tested this asset before? Check `findings/`.

If you find a close match, your bug is a duplicate **unless** you can show a
distinct impact or a distinct asset. "Same bug, different user" is a duplicate.

---

## What counts as a duplicate

- Same root cause, same endpoint, same class → duplicate, regardless of payload.
- Same root cause, different endpoint → often duplicate (same code path).
- Same class, genuinely different code path → usually accepted as separate.
- Same bug on staging vs production → usually one finding (production is the
  meaningful one).
- Same bug reported by you earlier → update the earlier report, do not file
  twice.

---

## The "already known" reply

If triage says "known issue," ask (once, politely) for the report id or the fix
commit. Then:

- If it is the same root cause → accept, move on.
- If yours is a different code path → reply with the distinguishing request.
- If they will not share → accept and move on. Arguing burns reputation.

---

## Scope disputes

If triage says out of scope:

1. Quote the scope line that includes your asset.
2. If the asset is a third-party host, state the scope reasoning (customer tenant
   vs platform).
3. If it is genuinely out of scope, accept.

Do not argue a third-party platform into scope. It never works and it marks you.

---

## Severity disputes

Triagers downgrade for three reasons: the impact is lower than you claimed, the
program's matrix caps it, or they disagree on a metric.

Your reply has three lines:

1. The request/response that shows the impact they missed.
2. The one metric you dispute (`S:U` vs `S:C`, `C:H` vs `C:L`) and why.
3. The business consequence in one sentence.

Then stop. If they hold, accept. One calm exchange; never a thread war.

---

## Reproducibility failures

"Cannot reproduce" usually means:

- Your steps assumed a state you did not describe (logged in, a specific tenant,
  a feature flag).
- A WAF or cache made it work once.
- The bug was fixed between your test and their triage.

Fix: re-run from scratch, capture fresh evidence with timestamps, resubmit with
the exact sequence and a note on the state. If it no longer reproduces, it is
fixed — say so and close it yourself if the platform allows.

---

## Duplicate-heavy programs

Signals a program is mined out:

- 500+ resolved reports, mostly Low/Medium.
- Disclosed reports cover the main app.
- Hacktivity shows 10 researchers on the same host.

Strategy on these: go to the **newest** assets (recent launches, new subdomains,
mobile app versions), the **deepest** objects (multi-tenant, admin), and the
**least-hunted** classes (business logic, cache, AI). Do not report reflected XSS
on the main site.

---

## The report hygiene that avoids dedup flags

- Search before you write.
- State what you checked: "Searched disclosed reports for `/api/orders` — none
  match this endpoint."
- If it resembles a known class, say how yours differs.
- One finding per report. Do not bundle five issues; bundling gets you one closed
  report instead of five accepted ones.

---

## After a duplicate

A duplicate is information, not a failure. It tells you:

- The asset is being worked — go deeper, not wider.
- The class is known — try the class on the *child* endpoints or a different
  object type.
- The program is active — good, keep going.

Record it in `findings/` and pick the next surface.

---

## The dedup mindset

The goal is not "a bug nobody has found" — that is luck. The goal is **a bug
whose impact nobody has demonstrated**. The same endpoint, with a stronger proof
of scale or a chain to a higher impact, is a new report. Depth is the anti-dedup.
