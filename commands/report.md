---
description: Write a submission-ready report for the program's platform — summary, steps, evidence, impact, fix.
argument-hint: <slug> [platform]
allowed-tools: Bash, Read, Write
---

# /bbw-report

`references/21`, `tools/report.py`, `templates/report-*.md`,
`prompts/report-editor.md`.

**Input:** `$ARGUMENTS` — the finding slug under `findings/`, plus the platform.

```
/bbw-report orders-bola intigriti
/bbw-report reset-poisoning hackerone
```

The triager reads hundreds. Structure is respect: title, impact, steps, evidence,
fix. Nothing else.

---

## Step 1 — Gather before writing

```
findings/<slug>/
  request-01.http   response-01.http
  request-02.http   response-02.http
  notes.md
  finding.yaml
```

If `finding.yaml` is missing, create it from `templates/example-finding.yaml`:

```yaml
title: ""
program: ""
asset: ""
class: ""
severity: ""
cvss: ""
impact: ""
steps: []
evidence: []
fix: ""
```

If any of those is empty, you are not ready to write. Go back and prove it.

## Step 2 — Pick the template and render

```bash
python tools/report.py findings/<slug>/finding.yaml --platform intigriti \
  -o findings/<slug>/report.md
```

Templates exist for Intigriti, HackerOne, Bugcrowd, YesWeHack. Match the platform
the program actually uses.

## Step 3 — The five sections, in this order

**Title** — asset + class + impact. Not "IDOR". Yes:
`BOLA on /api/orders/{id} allows any customer to read other customers' orders (name, address, phone, card last4)`

**Summary** — three sentences max: what, where, what an attacker gains.

**Steps to reproduce** — numbered, from a clean state, with the exact requests:

```http
1. Sign in as victim (account B) and create an order. Note the id: 1043.

   GET /api/orders/1043 HTTP/1.1
   Host: app.example.com
   Cookie: <B session>

2. Sign in as attacker (account A).

3. Request the victim's order id from the attacker session:

   GET /api/orders/1043 HTTP/1.1
   Host: app.example.com
   Cookie: <A session>

   Response: 200 OK
   {"id":1043,"email":"b***@example.com","address":"…","card_last4":"4242"}
```

Every step reproducible by someone who has never seen the app.

**Impact** — what the attacker gains, in business terms. Who is affected, at what
scale, with what consequence.

**Remediation** — specific and testable:

- *"Check that `order.user_id == session.user_id` in the handler for `GET
  /api/orders/{id}`, before serialising the response. Add a regression test that
  fetches another user's order and expects 403."*

Not *"implement proper authorization"*.

## Step 4 — Evidence pack

Attach or inline:

- request/response pairs, redacted (cookies → `<A session>`)
- screenshots only where they add something
- a short screen recording for multi-step chains
- listener logs for blind bugs
- one redacted value, never a dump

Redact: tokens, cookies, real PII, other researchers' data. Keep: the field names,
the shape, the proof.

## Step 5 — Self-review against the submission checklist

Run `checklists/submission.md` top to bottom. Common failures:

- [ ] Steps assume you are already logged in
- [ ] The victim account is not identified
- [ ] Impact is a class name, not a consequence
- [ ] Evidence is a screenshot of a JSON blob with no request
- [ ] The finding is on an excluded asset or excluded class
- [ ] Duplicate of an existing report (run `/bbw-dedup` first)
- [ ] Version/date of testing missing

## Step 6 — Tone

- No lecturing, no "as a security researcher I believe"
- No speculation about other endpoints you did not test
- No demands, no deadline pressure, no "this is critical, pay me"
- Past tense, factual, short sentences
- State what you did **not** test, in one line, if it matters

## Step 7 — Save and hand off

`findings/<slug>/report.md` is the artefact. `/bbw-dedup` next, then `/bbw-submit`.

---

## Output shape

```
report: findings/<slug>/report.md
platform: <name>
title: <the final title>
sections: summary | steps | evidence | impact | fix   all present
checklist: pass | <n failures>
next: /bbw-dedup then /bbw-submit
```

## Stop conditions

- Any section empty → do not submit; go prove it.
- Evidence does not reproduce from a clean state → not ready.
- Finding is on an excluded asset → do not report as a bug; ask the program if in
  doubt, once.
