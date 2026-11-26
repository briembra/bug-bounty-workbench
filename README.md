# Bug Bounty Workbench

An agent skill for authorized bug bounty hunting — from picking a program to a
report a triager accepts without asking a question.

**25 slash commands. 26 references. 13 workflows. 15 checklists.**
Works in Claude Code, OpenCode, Codex, Cursor, or any agent that can read a file.

---

## Install

Into the agent you are running in — Node 18+, no dependencies:

```bash
npx bug-bounty-workbench setup
```

It detects Claude Code, OpenCode, Cursor or Codex from the project markers or the
process environment, writes the 25 commands and the method into that agent's
directories, and prints the one command to run next. Nothing else is touched.

From this repository, before or without an npm release:

```bash
npx github:briembra/bug-bounty-workbench setup
```

Other shapes:

```bash
npx bug-bounty-workbench setup --agent claude --global   # user-level dirs
npx bug-bounty-workbench setup --dry-run                 # print the plan
npx bug-bounty-workbench status                          # what is installed
npx bug-bounty-workbench uninstall                       # remove what setup wrote
```

No Node? Paste the block in [`PROMPT.md`](PROMPT.md) and the agent installs
itself. Per-agent detail, plugin installs and the Python path:
[`INSTALL.md`](INSTALL.md).

---

## Use

```
/hunt https://app.example.com "Acme" on Intigriti
```

That is the whole loop: scope gate, map the asset, pick one class by ceiling,
prove it with two accounts, score it honestly, write it, dedup it, submit it.

Or drive the steps yourself:

```
/programs          find programs worth hunting across every platform
/scope             program page -> one verified scope file
/recon             passive-first subdomain discovery, bounded
/surface           map one host: actors, objects, flows, trust boundaries
```

---

## The 25 commands

| Stage | Command | Purpose |
|---|---|---|
| Start | `/hunt` | Full loop on one target URL. |
| Start | `/programs` | Search and rank bug bounty programs. |
| Setup | `/scope` | Build and verify the scope file. |
| Setup | `/recon` | Subdomain discovery and fingerprinting. |
| Setup | `/surface` | Map one host before testing it. |
| Hunt | `/idor` | Broken object-level authorization. |
| Hunt | `/auth` | Auth, session, OAuth, JWT. |
| Hunt | `/ssrf` | Server-side request forgery. |
| Hunt | `/xss` | Reflected, stored, DOM, blind. |
| Hunt | `/injection` | SQL, NoSQL, command, SSTI, XXE. |
| Hunt | `/files` | Upload, traversal, storage ACLs. |
| Hunt | `/logic` | Price, coupon, refund, quota, role. |
| Hunt | `/api` | REST surface and authz gaps. |
| Hunt | `/graphql` | Introspection and field-level authz. |
| Hunt | `/cloud` | Buckets, metadata, CI/CD trust. |
| Hunt | `/secrets` | Live secrets in JS and repos. |
| Hunt | `/cache` | Cache poisoning and deception. |
| Hunt | `/takeover` | Dangling CNAMEs. |
| Hunt | `/mobile` | APK/IPA review. |
| Hunt | `/ai` | Prompt injection, RAG, tool abuse. |
| Finish | `/chain` | Link findings into a kill chain. |
| Finish | `/score` | CVSS plus the program's own band. |
| Finish | `/report` | Write the platform-ready report. |
| Finish | `/dedup` | Check duplicates and prior art. |
| Finish | `/submit` | Final gate before sending. |

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
