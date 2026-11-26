# Bugcrowd report template

Bugcrowd uses: Title, VRT, Severity, Description, Steps, Impact, Fix. Pick the
VRT category precisely — it drives payout.

---

**Title**

```
Any customer can read any other customer's order history and PII via order id
```

---

**VRT**

```
Broken Access Control (BAC) > Insecure Direct Object References (IDOR)
```

*Alternative VRTs: "Sensitive Data Exposure > PII", "Broken Authentication and
Session Management". Pick the one that matches the demonstrated impact.*

---

**Severity**

```
P2 — High
CVSS 3.1: AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (6.5)
```

---

**Description**

`GET /api/orders/{id}` returns an order by id without verifying ownership. Any
authenticated customer can read any order by changing the id.

---

**Steps to Reproduce**

1. Account A creates an order (`POST /api/orders`) → id `1042`.
2. Account B creates an order → id `1043`.
3. Account A requests `GET /api/orders/1043`.
4. Response returns B's order and PII.

---

**Impact**

Any customer can read any other customer's PII and order history. No rate limit →
full enumeration. GDPR-relevant.

---

**Fix**

```python
order = Order.objects.get(id=id, user_id=request.user.id)  # 404 if not found
```

Apply to `/api/orders/{id}/items` and `/api/orders/export`.

---

**Attachments**

- request/response pairs (redacted)
- screenshot
