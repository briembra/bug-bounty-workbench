# Checklist — Business logic

## Flow model

- [ ] Flow written as a state machine.
- [ ] Illegal edges listed.
- [ ] Server recompute points identified.

## Price / total

- [ ] Client-supplied price tested.
- [ ] Negative quantity tested.
- [ ] Missing total tested.
- [ ] Arbitrary discount tested.
- [ ] Currency swap tested.
- [ ] Proof reached confirmation step; **no real purchase**.

## Coupons / credits

- [ ] Stacking tested.
- [ ] Reuse tested.
- [ ] Race (10 concurrent max) tested.
- [ ] Case/space duplicates tested.
- [ ] Self-referral tested.
- [ ] Cross-currency tested.

## Refunds / payouts

- [ ] Refund > paid tested.
- [ ] Double refund (sequential + concurrent) tested.
- [ ] Refund to different method tested.
- [ ] Refund of cancelled order tested.
- [ ] Negative withdrawal tested on controlled balance.

## Quotas / limits

- [ ] Batch endpoint bypass tested.
- [ ] UI-only limit vs API tested.
- [ ] `X-Forwarded-For` reset tested.
- [ ] Client-side counter tested.

## Invites / roles

- [ ] Invite after removal tested.
- [ ] Role in acceptance body tested.
- [ ] Orphan-admin claim tested.
- [ ] Cross-tenant `org_id` tested.

## Evidence

- [ ] Two requests creating the illegal edge.
- [ ] Resulting state shown.
- [ ] No financial harm caused.

## Severity

- [ ] Money/access impact scored, not elegance.
- [ ] Trial-abuse-only → Low.

## Verdict

- [ ] Works / Closed / Inconclusive written.
