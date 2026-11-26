# Workflow 03 — Hunt IDOR/BOLA

The highest-yield workflow. Run it on any app with user objects. Time box: 2–3
hours.

---

## Step 1 — Prepare the accounts (15 min)

- Account A (attacker) and Account B (victim), same role.
- Create the same object type in each: order, document, ticket, profile.
- Record both ids in `notes.md`.

If you cannot register two accounts, state why and use the strongest available
proof — but try hard first (different email domains, different browsers, the
mobile API).

---

## Step 2 — Collect the object endpoints (20 min)

From the JS, HAR, API docs, and network tab, list every endpoint that takes an
id:

```
GET    /api/orders/{id}
GET    /api/orders/{id}/items
GET    /api/invoices/{id}/pdf
PATCH  /api/users/{id}
POST   /api/documents/{id}/share
DELETE /api/comments/{id}
```

Write `endpoints.tsv`: method, path, param, auth, object.

---

## Step 3 — Build the baseline (10 min)

As A, call each endpoint with **A's own id**. Record the 200 response. This is
the control.

---

## Step 4 — Swap the id (30 min)

As A, call the same endpoint with **B's id**. For each, record status and a 20
byte slice of the body.

Verdicts:

| Result | Meaning |
|---|---|
| 403/404 | check exists |
| 200 with B's data | **BOLA read** |
| 200 but own data | server ignored the id — different bug (mass assignment?) |
| 500 | possible but unproven — retry, check child |

---

## Step 5 — Test the children and alternates (30 min)

For every object with a check, test:

- The child: `/orders/{B_id}/items`
- The export: `/orders.csv?ids={B_id}`
- The GraphQL node: `{ node(id:"base64(User:B)") { … } }`
- The search: `/search?q=…&user_id={B}`
- The webhook payload / email link

The parent usually has the check. The child usually does not.

---

## Step 6 — Test write and delete (20 min)

Only on an object B created and you own both accounts.

```
PATCH /api/orders/{B_id} {"note":"test"}
DELETE /api/comments/{B_id}
```

A 200 that changes B's object is BOLA write — High. Prove with a GET as B
showing the change, then revert if possible.

---

## Step 7 — Test vertical (20 min)

If a third lower-privilege account exists:

- Call admin endpoints from the low account.
- Call staff endpoints.
- Check role in the body: `PATCH /users/me {"role":"admin"}`.

BFLA/BOLA-write to admin is High.

---

## Step 8 — Prove and write (20 min)

Capture:

1. B's session creating the object (response with id).
2. A's session fetching B's id (response with B's data).
3. Field names and one redacted value.

Run `checklists/idor.md`. Write `finding.yaml` and `report.md`.

---

## Step 9 — Escalate severity honestly

Ask the four questions from `20-severity-and-cvss.md`:

- Whose data? (one user / all users / another tenant)
- What fields? (public / PII / payment / auth material)
- Scale? (one object / list endpoint / no rate limit)
- Boundary? (same tenant / cross-tenant)

Cross-tenant → Critical. Own-tenant PII at scale → High. Display name only → Low.

---

## Definition of done

- [ ] Two accounts, both objects recorded.
- [ ] Every id endpoint tested with the swapped id.
- [ ] Children and alternates tested.
- [ ] Write/delete tested on a controlled object.
- [ ] Vertical tested if roles exist.
- [ ] Evidence captured, report written.

If every endpoint returned 403/404, the app is well-built — record "closed" and
move to the next class, not the next random host.
