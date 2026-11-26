---
description: Map and test a REST API — docs discovery, authz gaps, mass assignment, versioning, batching.
argument-hint: <base url>
allowed-tools: Bash, Read, Write, WebFetch
---

# /api

`references/12`, `checklists/api-graphql.md`.

**Input:** `$ARGUMENTS` — API base URL or host.

```
/api https://api.acme.com
/api https://app.acme.com/api
```

---

## Step 1 — Find the docs

```
/swagger  /swagger-ui  /swagger.json  /swagger.yaml
/openapi.json  /openapi.yaml  /api-docs  /v2/api-docs  /v3/api-docs
/redoc  /docs  /.well-known/openapi.json
```

A public Swagger is the whole menu: every route, parameter and model. Record it
and move to Step 3.

If docs are closed, build the route list from the JS bundle and the mobile app:

```bash
grep -Eo '"/api/[a-zA-Z0-9/_{}.-]+"' bundle.js | sort -u
grep -Eo "'/v[0-9]/[a-zA-Z0-9/_{}.-]+'" bundle.js | sort -u
```

## Step 2 — Fingerprint versions

`/v1/` hardened, `/v2/` new, `/v0/`, `/beta/`, `/internal/`, `/staging/` forgotten.
Test the **old** version with the **new** token — deprecation usually removes the
auth checks the new one added.

## Step 3 — The four questions per endpoint

1. **Auth:** does it need a token? Try without; try with an expired one; try with a
   low-privilege user's token.
2. **Object authz:** does it check ownership? → `/idor`
3. **Methods:** `OPTIONS` to see what is allowed; then `PUT`, `PATCH`, `DELETE`.
4. **Mass assignment:** does `PATCH /users/me` accept fields the UI never sends?

```json
{"name":"a","role":"admin"}
{"email":"a@x.com","is_verified":true}
{"plan":"enterprise","credits":999999}
{"org_id":"<another tenant>"}
```

`role` / `is_admin` / `tenant_id` accepted = High.

## Step 4 — Batching

```http
POST /api/batch
[{"op":"read","path":"/api/me"},{"op":"read","path":"/api/admin/users"}]
```

If the batch handler routes without re-checking authorization, one allowed op plus
one forbidden op is the proof. A batch can also bypass per-endpoint rate limits.

## Step 5 — Auth anti-patterns

| Pattern | Bug |
|---|---|
| `Authorization: Bearer <uuid>` unsigned | forgeable |
| `X-User-Id` / `X-Internal` trusted | impersonation |
| API key in the query string | leaks via logs and Referer |
| JWT in localStorage | XSS steals it |
| `?user_id=` beside `/me` | BOLA |
| CORS `*` with credentials | cross-origin read |

Test CORS directly:

```bash
curl -sD- "https://<host>/api/me" -H "Origin: https://evil.com" -H "Cookie: <s>" \
  | grep -i 'access-control'
```

`ACAO: https://evil.com` + `ACAC: true` = read any authenticated response.

## Step 6 — Errors are data

Trigger 400/500 and read: stack traces name the framework, the ORM, the internal
path and sometimes the SQL. Note it; it feeds `/injection`.

## Step 7 — Discipline

- 2 concurrent, ≤5 req/s. Back off on 429/503.
- Realistic `User-Agent`, and the app's own `Origin`/`Referer`.
- Never fuzz a login endpoint at rate — you will lock accounts.
- Record every request you send in `findings/<slug>/`.

---

## Output shape

```
docs: found | closed
endpoints mapped: N   versions: <list>
findings: auth-gap N, mass-assign N, cors N
worst: <endpoint> — <what it allows>
next: /idor or /score
```

## Stop conditions

- Introspection and docs both closed, and no mobile app → route from JS only.
- Blanket 403 after a few requests → you are fingerprinted, stop.
- Anything that mutates other users' data → do not.
