---
description: Hunt business logic — price manipulation, coupon abuse, refund and payout flaws, role escalation.
argument-hint: <host>
allowed-tools: Bash, Read, Write, WebFetch
---

# /bbw-logic

`references/11`, `workflows/08`, `checklists/business-logic.md`.

**Input:** `$ARGUMENTS` — host with money, credits, subscriptions or invites.

```
/bbw-logic https://shop.acme.com
```

The proof is a state the system should not allow, reached without paying and
without harming anyone.

---

## Step 1 — Draw the state machine

```
cart --pay--> paid --ship--> shipped --refund--> refunded
signup --trial--> trialing --upgrade--> paid --cancel--> cancelled
invite --accept--> member --role--> admin
deposit --balance--> withdraw
```

Write it in `notes.md`, then list the **illegal edges**:

- `cart → refunded` (refund without paying)
- `paid → paid` (double charge, then double refund)
- `shipped → cart` (un-ship, re-buy cheaper)
- `refunded → shipped` (keep goods and money)
- `cancelled → trialing` (trial reset by cancel)

Every accepted illegal edge is a bug.

## Step 2 — Price and total

Intercept checkout and try:

```json
{"items":[{"id":1,"price":0.01,"qty":1}]}
{"items":[{"id":1,"qty":-1}]}
{"total":0}
{"discount":100}
{"currency":"XYZ"}
{"coupon":"ADMIN"}
{"plan":"enterprise","price":0}
```

Look for: server trusting a client price, negative quantity, no recompute when a
field is present, accepted arbitrary discount, integer overflow in the total.

**Stop at the payment confirmation screen.** Do not complete a purchase that costs
the company money or ships goods. The confirmation with the wrong total is the
proof.

## Step 3 — Coupons, credits, referrals

- Stack two coupons when only one is allowed
- Reuse one coupon across orders
- Race: apply the same coupon to 10 carts concurrently (10 max)
- `SAVE10 ` vs `save10` counted separately
- Self-referral with your own email/device → credit
- Negative coupon that increases the total
- Coupon from one currency applied to another

Never redeem a gift card you did not buy.

## Step 4 — Refunds and payouts

- Refund more than paid (quantity × price mismatch)
- Double refund, sequential and concurrent
- Refund to a different method than the one used
- Partial refunds that sum above the total
- Refund a cancelled or failed order
- Withdraw more than the balance via a race
- Negative withdrawal (deposits to you) if the amount is unvalidated

Use the smallest object you control. Never push money into a real bank account.

## Step 5 — Quotas and limits

- Batch endpoint bypasses a per-request limit
- The limit is in the UI but not the API
- Per-account limit, no per-IP limit — combine two
- `X-Forwarded-For` resets the counter
- Counter lives in a cookie or localStorage

A *bypass of a stated control* is a finding; absent rate limiting alone usually is
not.

## Step 6 — Invites and roles

- Accept an invite after being removed (not invalidated)
- Change `role` in the invite acceptance body
- Remove the last admin → orphaned org → claim it
- Cross-tenant `org_id` in the body
- Role change without the owner's confirmation

Role escalation via a body field is High.

## Step 7 — Prove the edge, score it

Show the two requests that create the illegal state, and the resulting state:

```http
POST /checkout {"items":[{"id":1,"price":0.01}]}
→ 200 {"total":0.01,"status":"awaiting_payment"}

GET /checkout/<id>
→ {"total":0.01,"status":"awaiting_payment"}
```

---

## Output shape

```
flows mapped: N   illegal edges accepted: N
worst: <flow> — <what it gives>
financial harm caused: none
severity: <band>
next: /bbw-score then /bbw-report
```

## Stop conditions

- Server recomputes everything → "closed", next flow.
- A race needs load to trigger → cap at 10 requests, or report it as unproven.
- Any step would move real money or ship real goods → do not.
