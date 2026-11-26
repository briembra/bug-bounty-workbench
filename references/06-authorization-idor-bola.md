# 06 — Authorization: IDOR and BOLA

The single highest-yield vulnerability class in modern bug bounty. If you learn
one thing, learn this.

**Definition.** The server authenticates you (knows who you are) but does not
authorize you for a specific object or function (does not check that *this*
object or action is yours). The client sends an identifier; the server trusts it.

- **IDOR** — Insecure Direct Object Reference. Classic: `/invoice/1042` →
  `/invoice/1043`.
- **BOLA** — Broken Object Level Authorization. The API version of the same
  thing, often with UUIDs so enumeration is not the point: the point is that the
  server never compares the object's owner to the caller.
- **BFLA** — Broken Function Level Authorization. The *function* is admin-only,
  but the endpoint does not check the role.

---

## The setup you need

Two accounts you control, in the same role. Same program, same app.

```
Account A: a@example.com   (attacker)
Account B: b@example.com   (victim)
```

Create one real object in each: an order, a document, a ticket, a profile.
Note both ids. Now A should never be able to read, modify, or delete B's object.

If roles exist, create a third: a lower-privilege account. Now B is the
higher-privilege victim and you test vertical escalation.

---

## The test matrix

For every object endpoint, run all nine where applicable:

| # | Test | Expected if secure | Finding if |
|---|---|---|---|
| 1 | A reads B's object by id | 403/404 | 200 with B's data → BOLA read |
| 2 | A updates B's object (`PATCH`/`PUT`) | 403/404 | 200 / changed → BOLA write |
| 3 | A deletes B's object | 403/404 | deleted → BOLA delete |
| 4 | A reads B's child (`/B/items`) | 403/404 | 200 → child BOLA |
| 5 | A creates an object *for* B (`POST {user_id:B}`) | ignored/rejected | created under B → BOLA create |
| 6 | A moves own object into B's scope (`{owner:B}`) | rejected | accepted → transfer / takeover |
| 7 | A uses a list endpoint with `?user_id=B` | filtered | returns B's rows → mass BOLA |
| 8 | A calls an admin-only function | 403 | 200 → BFLA |
| 9 | A accesses by an alternate path (export, search, GraphQL) | 403 | 200 → BOLA via another door |

Test the **child** and the **alternate path** first. The parent usually has the
check. The CSV export usually does not.

---

## Where to look, specifically

### Numbers and shape

- **Sequential integers** — classic. Never assume; test.
- **UUIDv4** — enumeration is not the vector, but the check is still often
  missing. Get a victim UUID from: a share link, a webhook payload, a public
  profile, an invite, an email you receive, a GraphQL node id.
- **UUIDv1** — time-based, partially predictable. Can be brute-forced in theory;
  the authorization question is easier.
- **Hashed ids** (`md5(user_id)`) — check whether the hash is of a guessable
  value.
- **GraphQL global ids** — `base64("User:1042")`. Decode, change, re-encode.
- **Composite keys** — `tenant/slug`, `org/project`. Change the tenant half.

### The ten endpoint patterns that leak

```
GET    /api/users/{id}
GET    /api/users/{id}/orders
GET    /api/orders/{id}
GET    /api/orders/{id}/items
GET    /api/invoices/{id}/pdf
GET    /api/documents/{id}/download
GET    /api/messages/{id}
POST   /api/orders/{id}/refund
PATCH  /api/users/{id}
DELETE /api/documents/{id}
```

Also: `/api/me` → is there a `/api/users/{id}` beside it that skips the filter?
`?id=` on a list endpoint. `[1,2,3]` batch bodies. `ids[]=` arrays. GraphQL
`node(id:)`. Export jobs with an `id`.

---

## The tools

`tools/idor.py` diffs two saved request/response pairs and tells you whether the
second returned data belonging to the first:

```bash
python tools/idor.py --a a.json --b b.json
```

Where `a.json` is `{"request": {...}, "response": {...}}` captured from A's
session and `b.json` is B's object id replayed with A's session.

Do it manually first; the tool is for documentation and for batch checks.

---

## Proof that it is real

A BOLA report dies when the triager says "that is your own data" or "that is
public data." Kill both before submitting:

1. **Ownership proof.** The object belongs to account B. Show B created it: B's
   session, `POST /orders`, response `{"id": 1043, "owner": "b@..."}`.
2. **Cross proof.** A's session, `GET /orders/1043`, returns B's object. Show
   A's cookie/header in the request, B's id in the URL, B's data in the response.
3. **Sensitivity proof.** The data is not public. Name the fields: email, address,
   phone, order contents, payment last-4. Redact values, keep field names.
4. **Scale statement.** Is it one object or the whole collection? Test the list
   endpoint once: `GET /orders?user_id=B` — if it returns all of B's rows, say
   "all objects of any user", which is a different severity.

A BOLA with those four is accepted. Without them it bounces.

---

## Severity: get it right

Use the real business impact, not the label.

| What you can do | Severity |
|---|---|
| Read one non-sensitive field of another user (e.g. display name that is public) | Low/Info |
| Read another user's PII (email, phone, address) | Medium–High |
| Read another user's order/payment/invoice data | High |
| Write/modify another user's object | High |
| Delete another user's object | High |
| Cross-tenant read or write (multi-tenant SaaS) | Critical/High |
| Admin function reachable by normal user | High |
| Mass read of all users via a list endpoint | Critical/High |
| Read another user's authentication material (tokens, reset links) | Critical |

**Multi-tenant is the multiplier.** Two customers of the same SaaS reading each
other is a breach of the vendor's core promise. Triagers score that at High or
Critical. Same bug between two end-users of one B2C shop is Medium.

**The demo-data trap.** If the leaked records are clearly seeded
(`@example.com`, `@researcher.test`, timestamps all on one import date, sequential
ids starting at 1), it may be a demo tenant. Downgrade honestly and say so. Do
not call a test dataset a breach; the triager will catch it and remember.

---

## BFLA: the function check

Vertical escalation is the same logic on the *function*, not the object.

- A customer calls `POST /api/admin/users/{id}/role`. Does the server check the
  role, or only that you are authenticated?
- A customer calls `GET /api/admin/export`. Filtered, or returns everything?
- The admin SPA hides the button. The API does not hide the endpoint.

Map admin endpoints from the admin app's JS (you can read it even without admin
access — it is served to whoever loads the app), then call them as a customer.

---

## Common reasons a BOLA test is "closed"

Say these out loud so you move on:

- Server checks object ownership via the session, not the id → closed.
- The id is not an object reference but a scoped token (signed, bound).
- The endpoint returns 404 for both "not yours" and "not exists" → good
  hygiene; closed.
- The object is genuinely public (published article, public profile) → not a bug.
- The "cross-account" test used the same account twice → redo with two accounts.

---

## The one-sentence version

**Every time the client sends an id, ask: did the server check that this id is
mine? If you cannot show that it did, you have a BOLA candidate — and BOLA is
where HIGH lives.**
