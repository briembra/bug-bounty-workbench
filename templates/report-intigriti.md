# Intigriti report template

Fill every section. Delete the guidance lines in italics.

---

**Title**
*Impact, not class. e.g. "Any customer can read any other customer's order history and PII via order id"*

---

**Asset**
*The exact in-scope asset from the program's list.*

```
https://app.example.com
```

---

**Severity**
*High / Medium / Low / Critical, and the CVSS below.*

```
CVSS 3.1: AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (6.5)
CWE-639: Authorization Bypass Through User-Controlled Key
```

---

**Summary**

*2–3 sentences. What it is, who can trigger it, what it gives.*

The order detail endpoint returns any order by its id without verifying the order
belongs to the requesting user. Any authenticated customer can read another
customer's name, address, phone and payment last-4 by changing the id.

---

**Steps to reproduce**

1. Log in as account A (attacker). Create an order via `POST /api/orders`; note
   the returned id (e.g. `1042`).
2. Log in as account B (victim). Create an order; note the id (`1043`).
3. As account A, send:
   ```
   GET /api/orders/1043 HTTP/1.1
   Host: app.example.com
   Cookie: session=<A>
   ```
4. The response is B's order: `{"id":1043,"user":"b@example.com","address":"…","phone":"…","card_last4":"…"}`.

---

**Impact**

*What an attacker gains, in business terms, at what scale.*

Any customer can read any other customer's PII and order history by incrementing
the id. There is no rate limit, so the full customer base is enumerable. This is a
GDPR-relevant disclosure of personal data.

---

**Remediation**

*Specific and testable.*

Filter by session user in the query:
`Order.objects.get(id=id, user_id=request.user.id)`, returning 404 for non-owners.
Apply the same to `/api/orders/{id}/items` and `GET /api/orders/export`.

---

**Evidence**

*Attach: request/response pairs, screenshot, script. Redact tokens and third-party PII.*

- `request-01.http` / `response-01.http` — B creates own order (id 1043)
- `request-02.http` / `response-02.http` — A reads 1043, returns B's data
- `screenshot-01.png`

---

**References**

- CWE-639
- OWASP API Security Top 10 — API1:2023 Broken Object Level Authorization
