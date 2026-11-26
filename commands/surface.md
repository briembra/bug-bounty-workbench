---
description: Map one host — actors, objects, flows, endpoints, trust boundaries — before testing.
argument-hint: <host or url>
allowed-tools: Bash, Read, Write, WebFetch
---

# /surface

You cannot break what you have not mapped. This is the 20-minute pass that turns
a host into an attack plan.

**Input:** `$ARGUMENTS` — one host or URL, already confirmed in scope.

```
/surface https://app.acme.com
```

---

## Step 1 — Read the outside

```bash
curl -sD- "https://<host>/" -o home.html
curl -s "https://<host>/robots.txt"
curl -s "https://<host>/sitemap.xml" | head -100
curl -s "https://<host>/.well-known/security.txt"
```

From headers and HTML record: server, framework, CDN/WAF, cookies and their
flags, meta generator, auth provider, analytics ids.

## Step 2 — Get the endpoint list from the client

```bash
grep -Eo 'src="[^"]+\.js[^"]*"' home.html | sort -u
# download each, then:
grep -Eo '"/api/[a-zA-Z0-9/_{}.-]+"' *.js | sort -u
grep -Eio '(https?://[a-z0-9.-]+)' *.js | sort -u
grep -Ei 'graphql|swagger|openapi|/v[0-9]/' *.js
```

Also check `/openapi.json`, `/swagger.json`, `/v3/api-docs`, `/graphql`,
`/graphiql`.

## Step 3 — Write the four tables

`engagements/<program>/surface.md`:

**Actors**

| actor | how obtained | what they can do |
|---|---|---|
| anonymous | none | browse, sign up |
| customer | register | own objects |
| staff/admin | program-provided | other objects |

**Objects**

| object | id shape | created by | read by | sensitive fields |
|---|---|---|---|---|
| order | numeric | customer | owner, staff | address, phone, last4 |
| document | uuid | customer | owner, shared | file, title |

**Flows**

```
signup → verify → login → checkout → pay → refund
invite → accept → role change
upload → preview → share
```

**Trust boundaries**

- What does the server take from the client that it should compute? (price, role,
  owner id, tenant id, redirect target, file path)
- Where does one user id appear in a request that belongs to another user?
- Which endpoint takes an id from the URL?
- Which endpoint returns fields the UI never shows?

## Step 4 — Pick the objects with the most value

Order them: money > identity > private content > public content. The top object
decides your first class.

## Step 5 — Set the engagement parameters

Top of `notes.md`:

```
program:       <name>
target:        <host>
budget:        <N requests, <rate>/s>
timebox:       <hours>
accounts:      A=<email>  B=<email>
listener:      <interactsh domain>
marker:        bbtest-<date>-<rand>
```

---

## Output shape

```
Host: <host>   Stack: <tech>
Actors: N   Objects: N   Flows: N
Top object: <object> — because <reason>
Trust gap spotted: <one sentence>
Recommended class: <class>  → run /<command>
```

## Stop conditions

- No two-account possibility and the top objects are all owner-scoped → say it,
  pick a class that does not need a second account (SSRF, takeover, secrets).
- SPA with no discoverable API and no auth → note it and move to another host.
