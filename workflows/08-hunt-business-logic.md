# Workflow 08 — Hunt business logic

Run this on any app with money, credits, coupons, subscriptions, invites, or a
multi-step flow. Time box: 2 hours.

---

## Step 1 — Find the flows (15 min)

List every flow that changes state or money:

```
cart → checkout → pay → fulfill → refund
signup → trial → upgrade → downgrade → cancel
invite → accept → role change
claim reward → refer → credit
withdraw → deposit
```

Write each as a state machine in `notes.md`.

---

## Step 2 — Price and total (25 min)

Intercept the checkout request. Try:

```json
{"items":[{"id":1,"price":0.01,"qty":1}]}
{"items":[{"id":1,"qty":-1}]}
{"total":0}
{"discount":100}
{"currency":"XYZ"}
{"coupon":"ADMIN"}
```

Look for: server trusting client price, negative qty, missing total recompute,
accepted arbitrary discount.

Prove by reaching payment confirmation with the wrong total. **Do not complete a
purchase that costs the company money or ships goods.** Stop at the confirm step.

---

## Step 3 — Coupons (20 min)

- Stack two coupons.
- Reuse one coupon across orders.
- Race: apply to N carts concurrently (10 requests max).
- Case/space duplicates.
- Self-referral with your own email/device.
- Cross-currency coupon.

---

## Step 4 — Refunds/credits (20 min)

- Refund more than paid.
- Double refund (sequential and concurrent).
- Refund to a different method.
- Refund a cancelled order.
- Negative withdrawal.

Use a small object you control; never push real money out.

---

## Step 5 — Quotas and limits (15 min)

- Batch endpoint bypasses a per-request limit.
- UI-only limit; API allows more.
- `X-Forwarded-For` resets the counter.
- Client-side counter (cookie/localStorage).

---

## Step 6 — Invites and roles (15 min)

- Accept an invite after removal.
- Change `role` in the acceptance body.
- Guess an invite token (only if low-entropy — do not brute force).
- Remove last admin → orphan org → claim.
- Cross-tenant `org_id` in the body.

---

## Step 7 — Prove the illegal edge (10 min)

Show the two requests that create the bad state, and the resulting state:

```
1. POST /checkout {"price":0.01} → 200 {"total":0.01,"status":"awaiting_payment"}
2. GET /checkout/{id} → {"total":0.01}
```

That is the proof. Do not pay.

---

## Step 8 — Score honestly

Money/access impact, not elegance:

| Shown | Severity |
|---|---|
| Buy for €0 | High–Critical |
| Refund > paid | High |
| Redeem another's gift card | Critical |
| Double refund | High |
| Trial reset only | Low |
| Role change via body | High |

Run `checklists/business-logic.md` and write the report.

---

## Definition of done

- [ ] Flows mapped as state machines.
- [ ] Price/total tested.
- [ ] Coupons tested.
- [ ] Refunds tested.
- [ ] Quotas tested.
- [ ] Invites/roles tested.
- [ ] Illegal edge proven without financial harm.
- [ ] Report written.

A flow where the server recomputes everything is closed. Write it and move to the
next flow.
