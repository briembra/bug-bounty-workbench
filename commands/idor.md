---
description: Hunt broken object level authorization — read, write, delete and escalate across users and tenants.
argument-hint: <host or endpoint>
allowed-tools: Bash, Read, Write, WebFetch
---

# /bbw-idor

The highest-yield class on the modern web. `references/06`, `workflows/03`,
`checklists/idor.md`.

**Input:** `$ARGUMENTS` — host or a specific endpoint family.

```
/bbw-idor https://app.acme.com
/bbw-idor "GET /api/orders/{id}"
```

---

## Step 1 — Two accounts, same role

- Account A: `you+bb1@yourdomain`, password unique.
- Account B: `you+bb2@yourdomain`.
- Create the **same object type** in each. Record both ids.

If registration needs a verified inbox, say so and use the mobile API or an
invite path — but try hard, because BOLA without a second account is a guess.

## Step 2 — Inventory every id-taking endpoint

From `/bbw-surface` and the JS bundle:

```
GET    /api/orders/{id}
GET    /api/orders/{id}/items
GET    /api/invoices/{id}/pdf
PATCH  /api/users/{id}
DELETE /api/comments/{id}
POST   /api/documents/{id}/share
GET    /api/search?user_id={id}
GET    /api/export?ids={id}
```

Write `endpoints.tsv`: method, path, param, auth seen, object.

## Step 3 — Baseline with your own id

For each endpoint call it with **A's own id** and save the 200. That is the
control. Without a working control, a 403 elsewhere proves nothing.

## Step 4 — Swap to B's id

Call each with B's id from A's session. Record status and the first 300 bytes.

| Result | Meaning |
|---|---|
| 403 / 404 | check exists — good sign, move to children |
| 200 with B's data | **BOLA read** — capture it |
| 200 with A's data | the id was ignored — look for mass assignment |
| 500 | unproven, retry once, then try the child path |

## Step 5 — The children and the alternates

The parent usually has the check. These often do not:

- `/orders/{B}/items`, `/invoices/{B}/pdf`, `/documents/{B}/versions`
- Export: `/export.csv?ids={B}`, `/download?file={B}`
- Search: `/search?q=x&user_id={B}`
- GraphQL: `node(id:"<base64 User:B>")`, or a field that takes an id
- Old versions: `/v1/...`, `/mobile/...`
- Batch endpoint: `POST /batch` with one allowed and one forbidden op

## Step 6 — Write side (only on objects you own)

```http
PATCH /api/orders/<B_ID> {"note":"bbtest"}
DELETE /api/comments/<B_ID>
POST /api/documents {"owner_id":"<B>"}
```

A 200 that changes B's object is BOLA write = High. Show the GET as B afterwards,
then revert if the API allows. Never touch an object you did not create.

## Step 7 — Vertical

If a staff/admin role exists:

- Call admin endpoints from the low account.
- `PATCH /users/me {"role":"admin"}`, `{"is_admin":true}`, `{"plan":"enterprise"}`
- Send `X-User-Id`, `X-Internal`, `X-Original-URL` and see if anything changes.

## Step 8 — Prove, score, hand off

Evidence: B's session creating the object, A's session fetching it, field names
with one redacted value (`references/19`).

```bash
python tools/idor.py --a a.json --b b.json
python tools/cvss.py "AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N"
```

Cross-tenant → `S:C`, that is High/Critical. Display name only → Low, say so.

---

## Output shape

```
endpoints tested: N   BOLA: N
worst: <endpoint> — read|write — <fields exposed>
evidence: findings/<slug>/
severity: <band> (<vector>)
next: /bbw-score then /bbw-report
```

## Stop conditions

- Every endpoint 403/404 including children → write "closed", move class, not host.
- A write test would hit a real customer's object → do not.
- Rate limiting appears → slow to 1/s and finish only the evidence requests.
