# Checklist — IDOR / BOLA

## Setup

- [ ] Two accounts you control, same role.
- [ ] Third account for vertical (if roles exist).
- [ ] One object of the same type created in each; ids recorded.
- [ ] Endpoint inventory built (`endpoints.tsv`).
- [ ] Baseline response with own id recorded.

## Horizontal (A against B's object)

- [ ] Read by id → 403/404, or 200 with B's data.
- [ ] Read the child (`/{B_id}/items`).
- [ ] Read via export (`/orders.csv?ids={B_id}`).
- [ ] Read via search (`/search?user_id={B}`).
- [ ] Read via GraphQL (`node(id:"…")`).
- [ ] Read via alternate API version (`/v1/`, `/mobile/`).
- [ ] Update (`PATCH`/`PUT`) — on a controlled object only.
- [ ] Delete — on a controlled object only.
- [ ] Create for B (`POST {"user_id":B}`).
- [ ] Move own object into B (`{"owner":B}`).
- [ ] List endpoint with `?user_id=B`.

## Vertical

- [ ] Admin endpoint called from low account.
- [ ] Staff endpoint called from customer account.
- [ ] Role set via body (`{"role":"admin"}`).
- [ ] Internal header trusted (`X-Internal`, `X-User-Id`).

## Proof

- [ ] B's session creating the object (response with id and owner).
- [ ] A's session fetching B's id (response with B's fields).
- [ ] Field names listed; values redacted.
- [ ] Data is not public/demo.
- [ ] Scale stated (one object or list).
- [ ] Boundary stated (same tenant or cross-tenant).

## Severity

- [ ] Scored per `20-severity-and-cvss.md`.
- [ ] Multi-tenant → Critical/High considered.
- [ ] Demo-data caveat written if applicable.

## Verdict

- [ ] Works / Closed / Inconclusive written.
