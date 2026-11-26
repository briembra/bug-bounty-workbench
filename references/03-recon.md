# 03 — Recon

Recon is the part most hunters do badly: they run `subfinder | httpx` and call it
done. The output of that is a list. Recon is not a list, it is an understanding of
what the organization *is* — what it sells, what it built, what it forgot.

Three layers, in order. Never skip layer 1.

1. **Passive** — learn the shape without touching the target.
2. **Active shallow** — resolve, probe, fingerprint. Bounded.
3. **Active deep** — per-host surface mapping. One host at a time.

---

## Layer 1 — Passive (zero requests to the target)

### Registrable domains

Start with what the program's scope gives you, then expand to sibling domains the
organization demonstrably owns:

- Certificate transparency: `crt.sh/?q=%25.example.com&output=json`,
  `crt.sh/?q=example.com`. Free, no target contact.
- Reverse WHOIS on the organization name (paid APIs: SecurityTrails,
  WhoisXML). Free approximation: `viewdns.info/reversewhois`.
- ASN: `bgp.he.net` → organization → announced prefixes. Every prefix is a
  candidate range; confirm scope before touching.
- Program page itself — scope lists often include secondary brands the marketing
  site never mentions.

Write every domain to `domains.txt` with a source column. You will need to prove
scope later.

### Subdomain sources (all passive)

| Source | Command | Notes |
|---|---|---|
| crt.sh | `curl -s "https://crt.sh/?q=%25.$d&output=json"` | Intermittently 502; retry |
| subfinder | `subfinder -d $d -all -silent` | Aggregates ~30 sources |
| amass passive | `amass enum -passive -d $d` | Slow, good coverage |
| DNS history | SecurityTrails / `dnsdumpster.com` | Finds deleted hosts |
| GitHub | `github.com/search?q="$d"&type=code` | Configs, CI, docs |
| Shodan/Censys/Fofa | `hostname:$d` | Favicon + cert pivots |
| Wayback | `web.archive.org/cdx/search/cdx?url=*.$d&collapse=urlkey` | Dead hosts, old paths |
| Chaos dataset | `chaos.projectdiscovery.io` | Free, high quality |

Merge, lowercase, dedupe, strip wildcards:

```bash
subfinder -d example.com -all -silent >> subs.raw
curl -s "https://crt.sh/?q=%25.example.com&output=json" \
  | jq -r '.[].name_value' | tr ',' '\n' >> subs.raw
sort -u subs.raw | grep -v '^\*' > subs.txt
```

### What to extract before you probe

- **Naming taxonomy.** `dev-`, `stg-`, `uat-`, `test-`, `admin-`, `internal-`,
  `api-`, `mx-`, `vpn-`, `jenkins.`, `gitlab.`, `grafana.`, `kibana.`.
  The name tells you the risk. Stage environments are the single highest-yield
  target class in bug bounty, because they ship with debug on and auth off.
- **Boring names with interesting tech.** `blog.` running WordPress with an
  abandoned plugin is a Medium. `api.` returning OpenAPI is a map to HIGH.
- **Orphaned names.** A subdomain pointing at a decommissioned SaaS is a
  takeover candidate (see `17-subdomain-takeover.md`).

---

## Layer 2 — Active shallow (bounded)

### Resolve

```bash
dnsx -l subs.txt -a -resp -silent -o resolved.txt
```

Record: does it resolve, to what (A, CNAME, AAAA). A CNAME to
`*.herokuapp.com`, `*.s3.amazonaws.com`, `*.azurewebsites.net`,
`*.cloudfront.net`, `*.github.io`, `*.readme.io`, `*.statuspage.io`,
`*.zendesk.com` is a takeover candidate — check each against
`data/takeover-fingerprints.txt`.

### Probe

```bash
httpx -l resolved.txt -silent -sc -title -td -cl -location -server \
      -threads 20 -rate-limit 30 -o alive.json
```

`-td` (tech detect) is what makes the output useful. Record status, title, tech,
content length, redirect target.

**Rate discipline:** 20 threads, 30 req/s is safe for most programs. If you see
429 or 403 everywhere, halve it. If you see 403 from a WAF on *all* paths, you
have been fingerprinted — change user agent, slow down, or stop.

### Triage the alive list

Bucket by signal, not by alphabet:

| Bucket | Why |
|---|---|
| 401/403 on `/` | Auth exists → object ids, roles → BOLA candidates |
| 200 on `/bbw-api`, `/bbw-graphql`, `/swagger`, `/openapi.json` | API map, often unauthenticated docs |
| Stage/dev/test in hostname | Debug on, weak auth |
| Login portals (SSO, Keycloak, Okta, Auth0, Azure AD) | Auth flows, redirect_uri, SAML |
| Admin panels (Jenkins, GitLab, Grafana, Kibana, Jira, Confluence) | Direct HIGH if unauthenticated |
| File hosts (S3, Azure blob, GCS) | Directory listing, ACL |
| Upload/preview endpoints | SSRF, XXE, path traversal |
| Anything with a version in the title | Known CVE candidate |

Order the buckets by expected ceiling: unauth admin > stage with debug > API with
docs > login portals > everything else.

---

## Layer 3 — Active deep (one host at a time)

Only after you picked a target. Full method in
`04-attack-surface-mapping.md`. Recon-specific inputs:

- **`robots.txt`** — disallowed paths are the app telling you what it hides.
- **`sitemap.xml`** — every public route, sometimes admin ones too.
- **`/security.txt`** — contacts, and sometimes a scope clarification.
- **JS bundles** — the real route list. See `14-secrets-and-js-analysis.md`.
- **`/openapi.json` / `/swagger.json` / `/v2/api-docs` / `/bbw-graphql`** —
  introspection. If docs are public, the API is a menu.
- **Error pages** — stack traces, framework versions, debug modes.
- **HTTP methods** — `OPTIONS *`, `TRACE`. Rarely a bug alone; occasionally a
  discovery.
- **Response headers** — `X-Powered-By`, `Server`, `Via`, `X-Cache`,
  `X-Amz-*`, `X-Azure-*`. They name the stack and the CDN.

---

## Continuous recon (for a long engagement)

Recon is not a phase, it is a subscription:

- Re-run subdomain enumeration weekly. New hosts ship unhardened.
- Monitor the app's changelog, release notes, and mobile app store updates.
  Every new feature is new surface.
- Watch certificate transparency in real time:
  `certstream.calidog.io` websocket, filtered to the domain.
- Diff the JS bundle hash daily. A changed bundle means changed endpoints.

`tools/scope_diff.py` diffs two scope snapshots so you notice when a program
adds an asset — a newly added asset is almost always untested.

---

## Recon output contract

At the end of layer 2 you must have:

```
engagements/<program>/
  domains.txt          # every registrable domain, with source
  subs.txt             # deduped names
  resolved.txt         # name + record
  alive.json           # status, title, tech, length
  buckets.md           # the triage table above, filled in
  scope.json           # from tools/scope.py
```

If you do not have those six, you are not ready to hunt. You have a list, not a
map, and a list finds nothing.
