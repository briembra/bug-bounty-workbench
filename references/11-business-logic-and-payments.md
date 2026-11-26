# 11 — Business logic and payments

Business logic bugs cannot be found by a scanner because they are not
misconfigurations — they are sequences the state machine allows but should not.
They pay well because impact is concrete: money, goods, access, reputation.

Hunt this class on: cart, checkout, coupon, gift card, wallet/credits, referral,
trial, subscription, refund, payout, withdrawal, invite, quota, rate limits,
auction, booking, delivery.

---

## The logic-bug questions

Ask these of every flow. Every "yes" is a candidate.

1. **Skip.** Can I reach state N without passing N-1? (`/checkout/complete`
   without payment; `/reset/step3` without step2.)
2. **Repeat.** Can I do the action twice? (coupon twice, refund twice, claim
   reward twice, accept invite twice.)
3. **Reorder.** Can I do steps out of order? (refund before payment clears;
   ship before payment; withdraw before deposit clears.)
4. **Substitute.** Can I change a value the server should control? (price, total,
   currency, role, quantity negative, discount, user id, plan id.)
5. **Race.** Can two concurrent requests pass a check that one would not? (balance,
   stock, invite slots, coupon limit, withdrawal limit.)
6. **Round.** Can rounding work in my favour? (0.001 currency units, percentage
   rounding, currency conversion.)
7. **Boundary.** Negative numbers? Zero? Extremely large? `NaN`? `Infinity`?
   Integer overflow in a total?
8. **Type confusion.** Send a string where a number is expected, an array where a
   scalar, `true` where an id.

---

## Price and total manipulation

The single most common payment bug.

- `POST /checkout {"items":[{"id":1,"price":0.01}]}` — server trusts client price.
- `{"quantity": -1}` → negative line item reduces total.
- `{"discount": 100}` or `{"coupon":"ADMIN"}` accepted.
- `{"currency":"XYZ"}` with a bad conversion rate.
- `{"total": 0}` accepted because the server only re-computes when a field is
  absent.
- Decimal: price `0.001` truncated to `0.00` server-side but quantity large.

Prove it by reaching a payment confirmation screen with a total of 0 (or 0.01)
**without paying**. Do not complete the purchase if it would cost the company
real money or ship goods — stop at the confirmation/authorize step and report.

---

## Coupon / gift card logic

- **Stacking.** Two coupons in one order when only one is allowed.
- **Reuse.** Same coupon on multiple orders.
- **Race.** Apply the same coupon to N concurrent carts.
- **Case/space.** `SAVE10 ` and `save10` both valid but counted separately.
- **Prediction.** Gift card codes that are sequential or low-entropy.
- **Self-referral.** Refer with your own email/device → credit.
- **Negative.** Coupon with a negative discount increases the total? (charge
  manipulation.)
- **Currency.** Coupon in one currency applied to another.

Gift-card prediction is Critical if you can redeem a card you did not buy — but
**never redeem someone else's card**. Prove with a card you bought.

---

## Refund / payout logic

- Refund more than paid (quantity * price mismatch).
- Refund to a different payment method than the one used.
- Refund after already refunded (double refund).
- Partial refunds that sum above the total.
- Refund a cancelled/failed order.
- Withdraw more than balance via race.
- Negative withdrawal (deposit to yourself) if the amount is unvalidated.

Prove with a small object you control and stop. Never push money out of the
platform into a real account.

---

## Trial / subscription abuse

- Re-register with `+alias`, different case, trailing dot to reset the trial.
- Cancel then re-activate to extend a paid period.
- Downgrade then upgrade keeps the higher tier's quota.
- Timezone/clock manipulation for "one trial per day".
- Coupon on a plan that excludes coupons.

Trial abuse alone is usually Low ("business decision"). It becomes Medium when it
gives access to *paid data* you should not see.

---

## Invite / membership / role logic

- Accept an invite for an org you were removed from (invite not invalidated).
- Change `role` in the invite acceptance body.
- Invite yourself to another org by guessing the invite token.
- Remove the last admin → orphaned org → claim.
- Role change without the owner's confirmation.
- Cross-tenant invite: `org_id` from the body.

Privilege escalation via role body param is High.

---

## Quota and rate-limit logic

- The limit is enforced per request but not per action (batch endpoint bypasses).
- Enforced on the UI but not the API.
- Enforced per account but not per IP, or vice versa — combine.
- `X-Forwarded-For` spoofing resets the counter.
- Counter stored client-side (cookie/localStorage).

Absent rate limiting is often excluded; a *bypass* of a stated control is not.

---

## Concurrency testing (safely)

Race bugs need parallel requests, but keep them bounded and non-destructive:

```python
import concurrent.futures, requests
def hit(_):
    return requests.post(url, json=body, cookies=cookies).status_code
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
    print(list(ex.map(hit, range(10))))
```

Ten requests, one object, one account. Enough to prove the race without load.
Never run a race against a shared production resource (stock, global counter) at
scale — use a test object.

---

## The state machine as an attack surface

Write the flow, then the illegal edges:

```
cart --pay--> paid --ship--> shipped --refund--> refunded
```

Illegal edges to try:

- `cart --> refunded` (refund without pay)
- `paid --> paid` (double charge then double refund)
- `shipped --> cart` (un-ship, then re-buy cheaper)
- `refunded --> shipped` (keep goods and money)

If the server accepts an illegal edge, that is the bug. Show the two requests
that create it.

---

## Severity

| What you showed | Severity |
|---|---|
| Buy for €0 / free goods | High–Critical |
| Refund more than paid | High |
| Redeem another's gift card | Critical |
| Double refund | High |
| Trial reset only | Low |
| Role change via body | High |
| Rate-limit bypass on a stated control | Medium |
| Quota bypass giving paid data | Medium–High |

Business logic severity is judged on **money and access**, not on elegance. A
clean €0 checkout beats a clever bypass that gains nothing.

---

## What closed looks like

- Server recomputes totals from authoritative data → closed.
- Coupon single-use enforced with a unique constraint → closed.
- Refund checks `sum(refunds) < paid` under a transaction → closed.
- Role changes require owner confirmation and server-side role map → closed.
- Rate limit enforced server-side per account + per action → closed.

Closed is a result. Write it and pick the next flow.
