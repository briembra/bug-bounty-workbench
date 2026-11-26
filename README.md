# Bug Bounty Workbench

**Give this to your agent:**

```
Install this for me: https://github.com/briembra/bug-bounty-workbench
```

An agent skill for authorized bug bounty hunting — from picking a program to a
report a triager accepts without asking a question.

**25 slash commands. 26 references. 13 workflows. 15 checklists.**
Works in Claude Code, OpenCode, Codex, Cursor, or any agent that can read a file.

---

## If you are the agent

Run this in the user's project directory:

```bash
npx github:briembra/bug-bounty-workbench setup
```

It detects which agent it is running in, writes the 25 commands and the method
into that agent's directories, and prints the next step. Then read `SKILL.md`
(router) and `AGENTS.md` (binding conduct) before touching any target.

If `npx` is unavailable: read `SKILL.md` and `AGENTS.md` from this repository,
treat `commands/*.md` as procedures, and tell the user which path you took.

Then report in three lines — commands installed, method loaded, waiting for a
program, a platform and a target — and stop.

---

## Install

Node 18+, no dependencies:

```bash
npx github:briembra/bug-bounty-workbench setup   # from this repository
npx bug-bounty-workbench setup                   # once published to npm
```

Other shapes:

```bash
npx bug-bounty-workbench setup --agent claude --global   # user-level dirs
npx bug-bounty-workbench setup --dry-run                 # print the plan
npx bug-bounty-workbench update                          # re-apply from this version
npx bug-bounty-workbench status                          # what is installed
npx bug-bounty-workbench uninstall                       # remove what setup wrote
```

Commands install with a `bbw-` prefix, so typing `bbw` in your agent lists all
25 of them: `/bbw-hunt`, `/bbw-programs`, `/bbw-scope`, `/bbw-recon`,
`/bbw-surface`, `/bbw-idor`, `/bbw-auth`, `/bbw-ssrf`, `/bbw-xss`,
`/bbw-injection`, `/bbw-files`, `/bbw-logic`, `/bbw-api`, `/bbw-graphql`,
`/bbw-cloud`, `/bbw-secrets`, `/bbw-cache`, `/bbw-takeover`, `/bbw-mobile`,
`/bbw-ai`, `/bbw-chain`, `/bbw-score`, `/bbw-report`, `/bbw-dedup`,
`/bbw-submit`.

Per-agent detail, the Claude Code plugin, the Python path and uninstall:
[`INSTALL.md`](INSTALL.md).

---

## Use

```
/bbw-hunt https://app.example.com "Acme" on Intigriti
```

That is the whole loop: scope gate, map the asset, pick one class by ceiling,
prove it with two accounts, score it honestly, write it, dedup it, submit it.

Or drive the steps yourself:

```
/bbw-programs          find programs worth hunting across every platform
/bbw-scope             program page -> one verified scope file
/bbw-recon             passive-first subdomain discovery, bounded
/bbw-surface           map one host: actors, objects, flows, trust boundaries
```

---

## The 25 commands

| Stage | Command | Purpose |
|---|---|---|
| Start | `/bbw-hunt` | Full loop on one target URL. |
| Start | `/bbw-programs` | Search and rank bug bounty programs. |
| Setup | `/bbw-scope` | Build and verify the scope file. |
| Setup | `/bbw-recon` | Subdomain discovery and fingerprinting. |
| Setup | `/bbw-surface` | Map one host before testing it. |
| Hunt | `/bbw-idor` | Broken object-level authorization. |
| Hunt | `/bbw-auth` | Auth, session, OAuth, JWT. |
| Hunt | `/bbw-ssrf` | Server-side request forgery. |
| Hunt | `/bbw-xss` | Reflected, stored, DOM, blind. |
| Hunt | `/bbw-injection` | SQL, NoSQL, command, SSTI, XXE. |
| Hunt | `/bbw-files` | Upload, traversal, storage ACLs. |
| Hunt | `/bbw-logic` | Price, coupon, refund, quota, role. |
| Hunt | `/bbw-api` | REST surface and authz gaps. |
| Hunt | `/bbw-graphql` | Introspection and field-level authz. |
| Hunt | `/bbw-cloud` | Buckets, metadata, CI/CD trust. |
| Hunt | `/bbw-secrets` | Live secrets in JS and repos. |
| Hunt | `/bbw-cache` | Cache poisoning and deception. |
| Hunt | `/bbw-takeover` | Dangling CNAMEs. |
| Hunt | `/bbw-mobile` | APK/IPA review. |
| Hunt | `/bbw-ai` | Prompt injection, RAG, tool abuse. |
| Finish | `/bbw-chain` | Link findings into a kill chain. |
| Finish | `/bbw-score` | CVSS plus the program's own band. |
| Finish | `/bbw-report` | Write the platform-ready report. |
| Finish | `/bbw-dedup` | Check duplicates and prior art. |
| Finish | `/bbw-submit` | Final gate before sending. |

Full index with what each one covers: [`commands/README.md`](commands/README.md).

---

## What is inside

| Path | Contents |
|---|---|
| `commands/` | 25 slash commands. |
| `PROMPT.md` | The paste-able install prompt. |
| `INSTALL.md` | Per-agent install paths. |
| `SKILL.md` | The router the skill loads. |
| `AGENTS.md` | Binding operating contract: scope gate, evidence, safety rails, stop conditions. |
| `references/` | 26 deep documents — method, every vulnerability class, delivery. |
| `workflows/` | 13 step-by-step playbooks for a full engagement. |
| `checklists/` | 15 testable checklists, one per class plus the submission gate. |
| `templates/` | Report templates for Intigriti, HackerOne, Bugcrowd, YesWeHack; PoC and CVSS worksheets. |
| `prompts/` | 6 role prompts for sub-agents. |
| `tools/` | 14 Python scripts, standard library only. |
| `data/` | Severity matrix, common paths, sensitive patterns, takeover fingerprints, JWT secrets, parameters, subdomains. |

---

## The tools are optional

Every tool is plain Python 3.10+ with no dependencies. Nothing needs installing;
there is no `pip install` step. The commands work entirely by hand.

```bash
python tools/scope.py --file scope.txt -o scope.json
python tools/subdomains.py scope.json -o subs.json
python tools/probe.py subs.json -o alive.json
python tools/exposure.py alive.json -o exposures.json
python tools/secrets.py alive.json -o secrets.json
python tools/unauth_json.py alive.json -o collections.json
```

---

## The three laws

1. **Authorization is the boundary.** Out of scope means it does not exist.
2. **Evidence beats claims.** Request, response, reproduction — or it is not a finding.
3. **Do not break things.** No DoS, no destructive writes, no mass scanning, no brute force.

---

## Scope of use

This repository is for testing systems you are **authorized** to test under a
program's published policy, or systems you own. It deliberately contains no
denial-of-service tooling, no credential brute forcers, and no mass scanners.
See [DISCLAIMER.md](DISCLAIMER.md).

## License

MIT. See [LICENSE](LICENSE).
