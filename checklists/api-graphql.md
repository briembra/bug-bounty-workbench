# Checklist — API and GraphQL

## Discovery

- [ ] Docs endpoints checked (`/swagger`, `/openapi.json`, `/api-docs`, `/graphql`).
- [ ] JS bundle route list extracted.
- [ ] API subdomains checked (`api.`, `api-v2.`, `mobile.`).
- [ ] Mobile base URL extracted.
- [ ] Endpoint inventory built.

## REST

- [ ] Auth required? tested without / expired / low-priv token.
- [ ] Object authz tested (see `idor.md`).
- [ ] Method overrides (`PUT`/`DELETE`/`OPTIONS`).
- [ ] Mass assignment (`role`, `is_admin`, `credits`, `plan`, `tenant_id`).
- [ ] Old version (`/v0/`, `/v1/`, `/beta/`) tested with new token.
- [ ] Batch endpoint bypass tested.

## GraphQL

- [ ] Introspection (`tools/graphql.py`) or field-suggestion leak.
- [ ] Field-level authz (query multiple users in one query).
- [ ] Global id decode/swap (`base64("User:123")`).
- [ ] Mutation role checks (`updateUser(role:"admin")`).
- [ ] Alias batching (rate-limit bypass) noted, not abused.
- [ ] Error verbosity checked.
- [ ] GET-based query / `text/plain` CSRF tested.

## Anti-patterns

- [ ] `Authorization: Bearer <uuid>` forgeable.
- [ ] `X-User-Id` trusted.
- [ ] API key in URL.
- [ ] JWT in `localStorage`.
- [ ] `?user_id=` beside `/me`.
- [ ] CORS `*` with credentials.

## Evidence

- [ ] Request + response for each finding.
- [ ] Unauthenticated vs authenticated comparison.

## Severity

- [ ] BOLA → per `idor.md`.
- [ ] Mass assignment to admin → High.
- [ ] Schema leak only → Info.

## Verdict

- [ ] Works / Closed / Inconclusive written.
