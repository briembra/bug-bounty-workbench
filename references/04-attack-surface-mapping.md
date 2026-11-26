# 04 — Attack surface mapping

Recon tells you what exists. Surface mapping tells you how it *works* — the
actors, the objects, the state machine, the trust boundaries. This is the step
where HIGH bugs are actually found, because HIGH is always a gap between what the
server was designed to enforce and what it actually enforces.

Do this on paper (or in `notes.md`) before you send a payload.

---

## Step 1 — Actors

List every distinct actor the system knows about:

| Actor | How it authenticates | What it can see |
|---|---|---|
| Anonymous | nothing | public pages |
| Customer | email+password / SSO | own orders, own profile |
| Support agent | staff SSO | any customer, view + limited edit |
| Admin | staff SSO + role | everything, including settings |
| API client | API key / OAuth token | scoped resources |
| Service | mTLS / shared secret | internal endpoints |
| Webhook sender | signature | pushes events |

Every actor is a **principal**. Authorization bugs live at the boundary between
two principals: the server checks *that* you are authenticated and *who* you are,
but forgets to check *whether this object belongs to you*.

If the app has only one role, your ceiling is lower. If it has three or more
(customer / support / admin, or tenant A / tenant B / super-admin), your ceiling
is HIGH.

---

## Step 2 — Objects

Every noun in the API is an object. Enumerate them:

```
users, accounts, profiles, sessions, devices
orders, carts, line-items, invoices, payments, refunds, payouts
tickets, messages, attachments, comments
organizations, teams, members, invitations, roles
documents, files, uploads, exports, reports
api-keys, webhooks, integrations, oauth-clients
```

For each object, record:

- **Identifier shape.** Numeric sequential (`1042`) → enumeration risk. UUIDv4 →
  low enumeration risk, but still an authorization question. Slug → guessable.
  Hash → check what is hashed.
- **Owner field.** Does the object carry a `user_id` / `tenant_id` / `org_id`?
  If yes, the authorization check is *supposed* to compare it against the
  caller. That comparison is the thing you test.
- **Child objects.** `orders/{id}/items`. The parent id often has a check; the
  child endpoint often does not. Test the child with the *other* account's
  parent id.
- **Alternate access paths.** REST `/orders/{id}`, GraphQL `order(id:)`,
  export `/orders.csv?ids=`, search `/search?q=`, webhook payload. Four paths,
  four chances that one forgot the check.

---

## Step 3 — The state machine

Write down the intended sequence for the flows that move money or change
identity:

```
signup → verify email → set password → login
cart → apply coupon → checkout → pay → fulfill → refund
invite → accept → join org → role change → remove
reset request → token issued → token used → password changed
```

Then ask, at each transition:

- Can I skip a step? (checkout without payment; change password without old one)
- Can I repeat a step? (apply the same coupon twice; refund twice)
- Can I reorder steps? (accept invite before verification; refund before fulfill)
- Can I substitute a parameter? (my id for another's; my price for zero)
- Can I replay a request? (nonce, idempotency key absent)
- Can I race two requests past a check? (balance, stock, invite slots)

Every "yes" is a candidate. Business logic bugs are the second-highest-yield
class because scanners cannot find them — they need a model, and you just built
one.

---

## Step 4 — Trust boundaries

Draw arrows between components and mark where data crosses from less trusted to
more trusted:

```
browser ──► CDN ──► app ──► API ──► DB
                      │
                      ├──► internal service (no auth assumed)
                      ├──► object storage
                      ├──► email / SMS provider
                      └──► LLM provider
```

Bugs cluster at boundaries:

- **Browser → app:** client-side validation only (price, role, `is_admin`),
  CORS, CSRF, XSS, postMessage.
- **App → API:** the app trusts its own client; the API trusts the app's
  internal header (`X-Internal: true`, `X-User-Id: <from client>`).
- **API → internal service:** SSRF surface. The internal service assumes the
  API already authorized. Test the URL fetcher.
- **App → storage:** signed URLs, ACLs, bucket policies.
- **App → LLM:** prompt injection, tool abuse, data exfiltration through the
  model.

---

## Step 5 — The three-question test per endpoint

For every endpoint you are about to test, write these three lines. If you cannot,
you do not understand the endpoint yet:

```
Assumption:     the server will only return MY orders because it filters on session user_id
Test:           GET /api/orders/1043 with account B's session (1043 belongs to A)
Proves if true: BOLA — cross-user read
Proves if not:  the check exists; try the child endpoint /api/orders/1043/items
```

This is the difference between hunting and poking. Poking produces a scanner
report. Hunting produces a finding with a stated hypothesis and a clean proof.

---

## Step 6 — Endpoint inventory from the client

The frontend knows every endpoint. Extract it:

- **JS bundle:** grep for `fetch(`, `axios.`, `"/api/`, `graphql`, route tables.
  Beautiful-print with `js-beautify` first; minified strings still contain URLs.
- **Source maps:** if `.map` files are served, you get the original source —
  route names, parameter names, sometimes internal comments. See
  `14-secrets-and-js-analysis.md`.
- **Mobile app:** decompile; API base URLs and endpoints are string literals.
  See `18-mobile-and-thick-clients.md`.
- **OpenAPI/Swagger:** if served, it is the complete menu with parameter types.
- **GraphQL introspection:** if enabled, the full schema.
- **HAR file:** the user browses, you get every request the app makes, with
  headers. Ask for one; it is the fastest map.

Build `endpoints.tsv`: `method \t path \t params \t auth \t object \t actor`.

---

## Step 7 — Prioritise by ceiling

Not all endpoints are worth your time. Sort:

| Signal | Ceiling |
|---|---|
| Takes an object id + returns object data | BOLA — HIGH |
| Admin/staff function reachable by customer role | Privilege escalation — HIGH |
| Accepts a URL, host, path, or webhook | SSRF — HIGH |
| Moves money, credits, or stock | Logic — HIGH |
| Changes identity (email, password, SSO link) | Account takeover — HIGH |
| Returns a file by path/name | Traversal — HIGH/Medium |
| Renders user input | XSS — Medium |
| Reflects a parameter in a redirect | Open redirect — Low |
| Returns config/version | Info |

Spend your first hour on the top five rows. That is where the acceptance rate is.

---

## The map is the deliverable

A good surface map is reusable across engagements on the same program and is the
single best predictor of a second bug. Keep it in the engagement folder, update
it when you learn something, and when you finish an engagement, write the three
sentences that would have saved you the most time. That is the note future-you
reads.
