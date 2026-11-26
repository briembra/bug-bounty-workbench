# 12 — API and GraphQL

Most modern surface is API surface. This document is the map: how to discover the
API, how to read it, and where the authorization and injection gaps sit.

---

## Discovering the API

- **Docs endpoints:** `/swagger`, `/swagger-ui`, `/swagger.json`,
  `/openapi.json`, `/api-docs`, `/v2/api-docs`, `/v3/api-docs`, `/redoc`,
  `/docs`, `/bbw-graphql`, `/graphiql`, `/playground`, `/.well-known/openapi.json`.
- **JS bundles:** grep for base URLs, `/api/`, `graphql`, fetch wrappers.
- **Subdomains:** `api.`, `api-v2.`, `internal-api.`, `mobile.`, `m.`.
- **Mobile app:** base URL string literals after decompile.
- **HAR:** the user's browser network log.
- **Error messages:** a 404 often suggests the real path (`/api/v1/...`).

If Swagger is public, you have the whole menu. If GraphQL introspection is on,
you have the whole schema. Both are the fastest maps you will get.

---

## REST: the checks that matter

For each endpoint, the four questions:

1. **Auth.** Does it require a token? Try without. Try with an expired token. Try
   with a token from a lower-privilege account.
2. **Object authz.** Does it check ownership? (See `06-authorization-idor-bola.md`.)
3. **Method.** `GET` allowed but `PUT`/`DELETE` also? `OPTIONS` leaks the allowed
   methods.
4. **Mass assignment.** Does `PATCH /users/me` accept fields the UI never sends?
   (`role`, `is_admin`, `credits`, `verified`, `plan`, `tenant_id`.)

```json
{"name":"a","role":"admin"}
{"email":"a@x.com","is_verified":true}
{"plan":"enterprise","credits":999999}
```

Mass assignment that sets `role` or `is_admin` is High.

### Versioning

`/v1/` may be hardened; `/v2/` new and buggy; `/v0/`, `/beta/`, `/internal/`
forgotten. Test the deprecated version with the new token. Old versions often
lack the auth checks the new one added.

### Batching

`POST /api/batch` with an array of operations can bypass per-endpoint rate limits
or authorization if the batch handler routes without re-checking. Test a batch of
one allowed + one forbidden operation.

---

## GraphQL: the method

### 1. Introspection

```bash
python tools/graphql.py https://target/graphql --introspect -o schema.json
```

If it returns a schema, you have every type, field, argument, and mutation. Read
it like a menu.

If introspection is disabled, try:

- Field suggestions: send `{ usr }` → error `Did you mean "user"?` leaks names.
- `__type(name:"Query")` directly.
- GET-based introspection, or a different path (`/graphql/v2`, `/api/graphql`).
- The mobile app's schema (often embedded).

### 2. The three GraphQL bug classes

**a) Authorization per field.** GraphQL resolvers are per-field. A query with
three fields may check auth on one and forget the others.

```graphql
{
  me { email role }
  user(id: "1043") { email phone role }   # does this check ownership?
}
```

**b) IDOR via global ids.** `id` is often `base64("User:1043")`. Decode, change,
re-encode:

```
VXNlcjoxMDQz  →  base64("User:1043")  →  base64("User:1042")
```

**c) Query depth / batching.** Deeply nested queries amplify load (DoS — skip
unless the program pays). Alias batching runs many mutations in one request,
bypassing rate limits:

```graphql
mutation { a: login(u:"x",p:"1"){token}  b: login(u:"x",p:"2"){token} ... }
```

**d) Mutation field-level authz.** `updateUser(id, role:"admin")` may not check
the caller's role.

### 3. GraphQL injection

Variables are JSON, not SQL, but resolvers can still pass them into:
- a search filter (`filter: {name_contains: "..."}`) — try SQL/NoSQL metachars,
- a URL fetcher field (SSRF),
- a template field (SSTI).

### 4. Error leakage

GraphQL errors are verbose. Cause an error and read the stack, the DB name, the
resolver name. Debug mode in GraphQL returns SQL.

### 5. GraphQL CSRF

A `GET`-based query (if enabled) with a cookie session is CSRF-able. POST with
`Content-Type: text/plain` also bypasses preflight on some stacks.

---

## Common API auth anti-patterns

| Pattern | Bug |
|---|---|
| `Authorization: Bearer <uuid>` with no signature | forgeable token |
| `X-User-Id` header trusted | impersonation |
| API key in URL (`?api_key=`) | leakage via logs/referer |
| JWT stored in `localStorage` | XSS steals it |
| `?user_id=` beside `/me` | BOLA |
| GraphQL `viewer` field returns other users | BOLA |
| CORS `*` with credentials | cross-origin read |

---

## API rate/scan discipline

APIs are where WAFs and rate limits bite hardest. Rules:

- 2 concurrent, ≤5 req/s per host unless the program states otherwise.
- On 429, back off exponentially (1s, 2s, 4s, 8s) and reduce concurrency.
- On 403 for everything, stop — you are fingerprinted.
- Use a realistic `User-Agent` and the app's own headers (`Origin`, `Referer`).
- Never fuzz a login endpoint at rate; you will lock accounts.

---

## Tools

```bash
# introspect and list operations
python tools/graphql.py https://target/graphql --introspect

# probe for unauth object access on a REST collection
python tools/unauth_json.py alive.json

# diff two responses for IDOR
python tools/idor.py --a a.json --b b.json
```

---

## What closed looks like

- Introspection disabled, field suggestions off → schema hidden. Still test known
  fields.
- Every field resolver checks ownership → BOLA closed on that query.
- Token is a signed JWT with `exp`, verified server-side → forge closed.
- `X-User-Id` ignored, identity from session → impersonation closed.
- CORS exact allowlist → cross-origin read closed.

Write it down. API work is high-volume; "closed" keeps you moving.
