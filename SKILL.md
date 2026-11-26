---
name: bug-bounty-hunter
description: Hunt bugs on authorized bug bounty and VDP programs end to end. Use when the task is to find, validate, or report a vulnerability against an in-scope target on HackerOne, Bugcrowd, Intigriti, YesWeHack, Immunefi, Open Bug Bounty, or a self-hosted program. Covers program selection and scope parsing, recon and asset discovery, attack-surface mapping, vulnerability-class hunting (BOLA/IDOR, auth and session, injection, SSRF, XSS, file handling, business logic, API/GraphQL, cloud, secrets, cache/protocol, subdomain takeover, mobile, AI/LLM surfaces), evidence standards, severity scoring, report writing, and triage/dedup. Not for exploiting systems outside an authorized scope, denial of service, or social engineering of real people.
metadata:
  version: "1"
  license: MIT
---

# Bug Bounty Hunter

A complete operating system for authorized bug bounty work. The goal is not
"find something" — it is **find a real, reproducible, in-scope vulnerability,
prove it with evidence, and report it so a triager accepts it without asking a
single question**.

Read this file first. It routes. Everything deep lives in `references/`,
`workflows/`, `checklists/`, and `templates/`.

> **How this is used:** there is nothing to install. The user pastes the block in
> [`PROMPT.md`](PROMPT.md) into their agent; the prompt tells the agent to load
> this file and `AGENTS.md`, then follow the routes below. If you are the agent
> reading this, continue at "Route the engagement first".

---

## The three laws

1. **Authorization is the boundary.** If the asset is not in the program's
   scope and rules, it does not exist. Wildcards are scope; a host that merely
   *looks* related is not. Confirm the scope text before touching a target.
2. **Evidence beats claims.** A finding is a request, a response, and a
   reproduction path. "It looks vulnerable" is not a finding. If you cannot
   show it, you have not found it.
3. **Do not break things.** No denial of service, no destructive writes, no
   mass scanning, no brute force, no touching real customer data beyond the
   minimum needed to prove impact. Prove access, then stop.

If a request conflicts with these, the laws win.

---

## Route the engagement first

Pick the entry point from what the user gave you.

| Input | Start here |
|---|---|
| "Find me a program" / no target named | [program selection](references/01-program-selection.md) → [scope](references/02-scope-and-rules.md) |
| A program URL or handle | [scope and rules](references/02-scope-and-rules.md) → [new program workflow](workflows/01-new-program.md) |
| A list of domains/hosts | [recon](references/03-recon.md) → [recon pass](workflows/02-recon-pass.md) |
| A live web app, "hunt it" | [attack surface](references/04-attack-surface-mapping.md) → pick a class below |
| "I have a 401/403" or a login page | [auth and sessions](references/05-authentication-and-sessions.md) |
| "I have two accounts" or object ids | [BOLA/IDOR](references/06-authorization-idor-bola.md) |
| A parameter, form, or API field | [injection](references/07-injection.md), [XSS](references/09-xss-and-client-side.md) |
| A URL fetcher, import, webhook, preview | [SSRF](references/08-ssrf.md) |
| A file upload, export, archive | [file handling](references/10-file-handling.md) |
| A checkout, cart, refund, invite, points | [business logic](references/11-business-logic-and-payments.md) |
| A REST/GraphQL API or mobile app | [API and GraphQL](references/12-api-and-graphql.md) |
| S3/GCS/Azure/Firebase/K8s/CI | [cloud and infrastructure](references/13-cloud-and-infrastructure.md) |
| JavaScript bundles, source maps | [secrets and JS](references/14-secrets-and-js-analysis.md) |
| A chatbot, assistant, RAG, agent | [AI and LLM surfaces](references/15-ai-and-llm-surfaces.md) |
| Cache headers, proxies, HTTP/2 | [caching and protocol](references/16-caching-and-protocol.md) |
| Dangling CNAME, dead SaaS page | [subdomain takeover](references/17-subdomain-takeover.md) |
| An APK/IPA/desktop client | [mobile and thick clients](references/18-mobile-and-thick-clients.md) |
| A confirmed bug, needs a report | [evidence](references/19-evidence-and-reproduction.md) → [severity](references/20-severity-and-cvss.md) → [report](references/21-report-writing.md) |
| "Is this a duplicate?" / triager pushed back | [triage and dedup](references/22-triage-and-dedup.md) |

When two classes are plausible, hunt the one with the higher ceiling first
(BOLA, auth bypass, SSRF to internal, business logic) before the one that pays
low (reflected XSS, missing headers).

---

## The loop

Every engagement is the same loop. Do not skip a step because a target "looks
boring".

```
1. BOUND   → read scope + rules + payout table + known issues
2. MAP     → what exists (subdomains, apps, APIs, roles, flows, tech)
3. MODEL   → how it is supposed to work (roles, objects, state machine)
4. BREAK   → find the assumption the model makes that the server doesn't enforce
5. PROVE   → minimal reproducible evidence, no excess
6. SCORE   → real CVSS + real business impact
7. WRITE   → report a triager can accept without questions
8. SUBMIT  → then keep hunting the same asset; first bug is a map
```

The value is in step 4. Most hunters stop at step 2 and report what a scanner
found. The assumption gap is where HIGH lives.

**Where HIGH actually comes from** (ordered by historical yield):

1. **Object-level authorization** — the server trusts an id from the client.
2. **Authentication/session flaws** — token confusion, missing binding, reset logic.
3. **Business logic** — the state machine allows a sequence it should not.
4. **SSRF with internal reach** — metadata, admin panels, internal APIs.
5. **Secrets with real blast radius** — cloud keys, signing keys, DB creds.
6. **Injection with data access** — SQLi/NoSQLi/SSTI that returns rows.
7. **Cross-tenant access** — anything that crosses a tenant boundary.
8. **AI/LLM tool abuse** — the assistant can act with the server's privileges.

Reflected XSS, open redirect, missing SPF, clickjacking, and version banners are
LOW by default. Hunt them only as a chained step.

---

## Working rules

- **Read before you request.** `robots.txt`, `sitemap.xml`, JS bundles, and the
  program's own docs tell you the surface before a single probe.
- **One target at a time.** Depth beats breadth. Ten requests that understand one
  app beat 10,000 that understand none.
- **Bounded scans.** Cap threads, cap paths, cap time. A scan that trips WAF
  rate limits and gets your IP banned is a failed engagement.
- **Two accounts, always.** Any authorization test needs a victim account you
  own. Never use another real user's data to prove IDOR — create the pair.
- **Respect production data.** If you land in real PII, capture the minimum
  (one record, redacted), stop, report. Do not enumerate.
- **Write as you go.** Evidence in a file the moment you see it. Memory lies.
- **Re-read the rules after every finding.** Some programs exclude whole classes
  (e.g. self-XSS, missing headers, rate limits). A great bug that is out of
  scope is worth zero.

---

## Severity in one screen

| Signal | Typical |
|---|---|
| Read another user's PII at scale, unauth admin access, RCE, cloud takeover | **Critical/High** |
| Cross-tenant read/write, auth bypass on a single account, SSRF to metadata, SQLi read | **High** |
| Single-user data leak, stored XSS on a low-traffic page, internal doc disclosure | **Medium** |
| Reflected XSS, CSV injection, open redirect, IDOR on non-sensitive metadata | **Low** |
| Missing headers, banners, best-practice-only, self-XSS | **Informational** |

Full method: [severity and CVSS](references/20-severity-and-cvss.md). Do not
inflate. A triager downgrades inflation and remembers your handle.

---

## Reporting shape

Every report has the same skeleton, regardless of platform:

```
Title: <impact> via <vector> on <asset>
Summary: 2–3 sentences, what and why it matters
Asset: exact in-scope host/endpoint
Steps to reproduce: numbered, copy-pasteable
Evidence: request + response, screenshots, video if stateful
Impact: what an attacker gains, in business terms
Fix: specific, testable
CVSS: vector + score, justified
```

Platform wrappers: [Intigriti](templates/report-intigriti.md),
[HackerOne](templates/report-hackerone.md),
[Bugcrowd](templates/report-bugcrowd.md),
[YesWeHack](templates/report-yeswehack.md).

Before submitting, run the
[submission checklist](checklists/submission.md) top to bottom.

---

## Tooling

The `tools/` directory is a working toolkit, not decoration. Every script runs.

```bash
pip install -r tools/requirements.txt

python tools/scope.py --platform intigriti --program <handle> -o scope.json
python tools/subdomains.py scope.json -o subs.json
python tools/probe.py subs.json -o alive.json
python tools/exposure.py alive.json -o exposures.json
python tools/secrets.py alive.json -o secrets.json
python tools/unauth_json.py alive.json -o collections.json
python tools/graphql.py https://target/graphql --introspect
python tools/jwt_tool.py "<token>"
python tools/idor.py --a a.json --b b.json
python tools/cvss.py "AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N"
python tools/report.py finding.yaml -o report.md
```

Read [tooling](references/24-tooling.md) before using them. Each tool prints what
it did, what it skipped, and why — trust the skip reasons.

---

## When you are stuck

- Re-read the app as three roles: anonymous, normal user, admin. What changes?
- Diff two accounts: same request, different ids. The server's answer is the bug.
- Look at what the frontend *stops* you from doing. Remove that stop.
- Follow the money: cart, discount, refund, payout, credits.
- Follow the identity: signup, invite, reset, email change, SSO linking.
- Follow the file: upload, import, export, preview, share.
- Follow the integration: webhook, OAuth app, API key, chatbot tool.
- Read the changelog and the mobile app — new features ship unhardened.
- Ask: what does the server trust that the client controls?

If none of that moves, change asset, not class. A new host is a new map.

---

## Hard stops

These are refusals, not slowdowns:

- Any action against an asset outside the program's stated scope.
- Denial of service, load testing, or "just checking if it scales".
- Brute forcing credentials, tokens, OTPs, or order numbers.
- Accessing, storing, or enumerating real customer data beyond one proof record.
- Social engineering employees, phishing real users, or physical intrusion.
- Publishing a finding before the program allows disclosure.
- Testing a third-party service that the program does not own.

If a task requires one of these, say so and propose the in-scope alternative.

---

## Reference index

**Method** — [01 program selection](references/01-program-selection.md),
[02 scope](references/02-scope-and-rules.md),
[03 recon](references/03-recon.md),
[04 attack surface](references/04-attack-surface-mapping.md),
[24 tooling](references/24-tooling.md),
[26 mindset](references/26-mindset-and-process.md)

**Classes** — [05 auth/session](references/05-authentication-and-sessions.md),
[06 BOLA/IDOR](references/06-authorization-idor-bola.md),
[07 injection](references/07-injection.md),
[08 SSRF](references/08-ssrf.md),
[09 XSS/client](references/09-xss-and-client-side.md),
[10 files](references/10-file-handling.md),
[11 logic/payments](references/11-business-logic-and-payments.md),
[12 API/GraphQL](references/12-api-and-graphql.md),
[13 cloud](references/13-cloud-and-infrastructure.md),
[14 secrets/JS](references/14-secrets-and-js-analysis.md),
[15 AI/LLM](references/15-ai-and-llm-surfaces.md),
[16 cache/protocol](references/16-caching-and-protocol.md),
[17 takeover](references/17-subdomain-takeover.md),
[18 mobile](references/18-mobile-and-thick-clients.md)

**Delivery** — [19 evidence](references/19-evidence-and-reproduction.md),
[20 severity](references/20-severity-and-cvss.md),
[21 report](references/21-report-writing.md),
[22 triage/dedup](references/22-triage-and-dedup.md),
[23 opsec](references/23-opsec-and-safety.md),
[25 chaining/escalation](references/25-chaining-and-escalation.md),
[24 tooling](references/24-tooling.md),
[26 mindset](references/26-mindset-and-process.md)

**Workflows** — [new program](workflows/01-new-program.md),
[recon pass](workflows/02-recon-pass.md),
[IDOR](workflows/03-hunt-idor.md),
[auth bypass](workflows/04-hunt-auth-bypass.md),
[SSRF](workflows/05-hunt-ssrf.md),
[XSS](workflows/06-hunt-xss.md),
[injection](workflows/07-hunt-injection.md),
[business logic](workflows/08-hunt-business-logic.md),
[secrets](workflows/09-hunt-secrets.md),
[takeover](workflows/10-hunt-subdomain-takeover.md),
[AI assistants](workflows/11-ai-assistant-deep-dive.md),
[submit](workflows/12-report-and-submit.md),
[dedup](workflows/13-dedup-check.md)

**Checklists** — [auth](checklists/auth.md), [idor](checklists/idor.md),
[injection](checklists/injection.md), [ssrf](checklists/ssrf.md),
[xss](checklists/xss.md), [upload](checklists/file-upload.md),
[logic](checklists/business-logic.md), [api](checklists/api-graphql.md),
[cloud](checklists/cloud.md), [secrets](checklists/secrets.md),
[session](checklists/session.md), [caching](checklists/caching.md),
[takeover](checklists/takeover.md), [ai](checklists/ai-llm.md),
[submission](checklists/submission.md)

**Prompts** — [recon planner](prompts/recon-planner.md),
[class selector](prompts/vuln-class-selector.md),
[triage reviewer](prompts/triage-reviewer.md),
[report editor](prompts/report-editor.md),
[dedup analyst](prompts/dedup-analyst.md),
[exploit reviewer](prompts/exploit-reviewer.md)
