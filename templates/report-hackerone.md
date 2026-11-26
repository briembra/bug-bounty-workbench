# HackerOne report template

HackerOne splits fields: Title, Weakness, Severity, CVSS, Description, Impact,
Steps to Reproduce, Supporting Material. Use them.

---

**Title**

```
Any customer can read any other customer's order history and PII via order id
```

---

**Weakness**

```
CWE-639: Authorization Bypass Through User-Controlled Key
```

---

**Severity / CVSS**

```
High — AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (6.5)
```

---

**Description**

*What the endpoint does and what the flaw is.*

`GET /api/orders/{id}` returns an order by id. The handler authenticates the
request but does not verify that the order belongs to the caller. Any
authenticated user can read any order by changing the id.

---

**Impact**

*Business consequence, concrete.*

Any customer can read any other customer's PII (name, address, phone, card
last-4) and order history. No rate limit, so the full customer base is
enumerable. GDPR-relevant personal data disclosure.

---

**Steps to Reproduce**

1. Log in as account A; `POST /api/orders`; note id `1042`.
2. Log in as account B; `POST /api/orders`; note id `1043`.
3. As A: `GET /api/orders/1043`.
4. Response contains B's data.

```
### request-02.http
GET /api/orders/1043 HTTP/1.1
Host: app.example.com
Cookie: session=<A_REDACTED>

### response-02.http
HTTP/1.1 200 OK
Content-Type: application/json

{"id":1043,"user":"b@example.com","address":"REDACTED","phone":"REDACTED","card_last4":"4242"}
```

---

**Supporting Material**

- `request-01.http`, `response-01.http`
- `request-02.http`, `response-02.http`
- `screenshot-01.png`
- `repro.py` (optional, takes credentials as args)

---

**Remediation**

Filter by `user_id` in the query and return 404 for non-owners. Apply to the
child endpoint and the CSV export.

---

**Notes**

Searched disclosed reports for `/api/orders` — no matching report. The closest
disclosed finding is on `/api/invoices`, a different code path.
