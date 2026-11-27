# Commands

25 commands. Each one is a complete procedure, not a prompt fragment: it names its
inputs, its steps, its evidence standard, and its stop conditions.

In Claude Code, Codex, Cursor and OpenCode these appear as `/bbw-hunt`, `/bbw-programs`,
and so on once the repository is installed (see [`../INSTALL.md`](../INSTALL.md)).
In any other agent, open the file and follow it — same procedure either way.

**Every command reports the same way:** short and plain. Answer or verdict in the
first line, three lines for a status, four for a finding, no preamble and no recap.
The long version goes in the file, not in the chat. Rules: [`../AGENTS.md`](../AGENTS.md#5-output-discipline).

**Every command opens with the two numbers**, whatever the command is: surface age
(0–5) and median payout days. One line, then work. If the surface is stale, name the
newest in-scope asset. See [`../SKILL.md`](../SKILL.md#the-standing-check) and
[`../references/01-program-selection.md`](../references/01-program-selection.md).

**Abandoned is a result.** A class gets 60 minutes or 150 requests; if nothing
moves, say `dead — <reason>`, log it in `engagements/<program>/dead.md`, and take
the next item from the shortlist. Never re-run the same class on the same asset
without new information. Rules: [`../AGENTS.md`](../AGENTS.md#61-kill-and-pivot).

---

## Start here

| Command | What it does |
|---|---|
| `/bbw-hunt` | The whole loop on one target: scope → map → one class → prove → score → report. |
| `/bbw-programs` | Search HackerOne, Bugcrowd, Intigriti, YesWeHack, Immunefi, huntr, OBB and self-hosted policies; rank the shortlist. |

## Set up the engagement

| Command | What it does |
|---|---|
| `/bbw-scope` | Turn a program page into one scope file with hosts, wildcards, exclusions and rules. |
| `/bbw-recon` | Passive-first subdomain discovery, bounded resolution, bucket the results. |
| `/bbw-surface` | Map one host: actors, objects, flows, endpoints, trust boundaries. |

## Hunt a class

| Command | What it does |
|---|---|
| `/bbw-idor` | Broken object-level authorization: read, write, delete, escalate across users and tenants. |
| `/bbw-auth` | Reset poisoning, MFA skip, OAuth redirect abuse, JWT forgery, session flaws. |
| `/bbw-ssrf` | Prove the server-side fetch, reach localhost, then metadata. |
| `/bbw-xss` | Reflected, stored, DOM and blind — with the chain to real impact. |
| `/bbw-injection` | SQL, NoSQL, command, SSTI, XXE, deserialization. One proof, then stop. |
| `/bbw-files` | Upload bypass, path traversal, arbitrary write, storage ACLs. |
| `/bbw-logic` | Price manipulation, coupons, refunds, payouts, quota bypass, role escalation. |
| `/bbw-api` | REST surface: docs discovery, authz gaps, mass assignment, versioning, batching. |
| `/bbw-graphql` | Introspection, field-level authz, global-id IDOR, mutation flaws. |
| `/bbw-cloud` | Buckets, metadata, managed services, CI/CD trust. |
| `/bbw-secrets` | Live secrets in JS, source maps, public repos and build artefacts. |
| `/bbw-cache` | Cache poisoning and deception, header and protocol flaws. |
| `/bbw-takeover` | Dangling CNAMEs — prove it, claim the minimum, release it. |
| `/bbw-mobile` | APK/IPA review: keys, endpoints, storage, deep links, pinning. |
| `/bbw-ai` | Prompt injection, system prompt leakage, RAG disclosure, tool-call abuse. |

## Finish it

| Command | What it does |
|---|---|
| `/bbw-chain` | Link a low finding into a kill chain and prove the end state. |
| `/bbw-score` | Honest CVSS plus the program's own band, with the downgrades applied. |
| `/bbw-report` | Write the platform-ready report from the evidence folder. |
| `/bbw-dedup` | Check for duplicates and prior art before you spend a triager's time. |
| `/bbw-submit` | Final gate: checklist, platform fields, redaction, disclosure window. |

---

## How a command is shaped

```markdown
---
description: one line — this is what the agent sees in the command list
argument-hint: <what to type after the command>
allowed-tools: Bash, Read, Write, WebFetch
---

# /name
References it depends on, then:
**Input:** `$ARGUMENTS` — what it accepts, with examples.
Step 1 … Step N — the procedure, with the exact commands.
## Output shape — the fixed report back to you.
## Stop conditions — when to quit instead of pushing.
```

`$ARGUMENTS` is whatever follows the command. Examples throughout the files use
`app.example.com` — replace with the in-scope host.

## Chains

```
/bbw-programs → /bbw-scope → /bbw-recon → /bbw-surface
/bbw-surface  → /bbw-idor | /bbw-auth | /bbw-ssrf | /bbw-xss | /bbw-injection | /bbw-files | /bbw-logic | /bbw-api
          → /bbw-graphql | /bbw-cloud | /bbw-secrets | /bbw-cache | /bbw-takeover | /bbw-mobile | /bbw-ai
any finding → /bbw-chain → /bbw-score → /bbw-report → /bbw-dedup → /bbw-submit
```

`/bbw-hunt` runs that whole path on one target when you do not want to drive each step.
