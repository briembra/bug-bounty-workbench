# Bug Bounty Hunter

An agent skill for authorized bug bounty hunting — from picking a program to a
report a triager accepts without questions.

Point any capable AI agent at this repository and it has a working method, a
working toolkit, and hard rules about scope and evidence.

```
You:  "https://github.com/briembra/bug-bounty-hunter — hunt <program>, in scope only."
AI:   reads SKILL.md → routes to scope + recon → hunts → writes the report
```

## Why this exists

Most "bug bounty prompt" material is a list of tricks. This is an operating
system: how to read a program, how to map an asset, how to model what the server
trusts, how to prove it, how to score it honestly, and how to write it up. It
also contains the parts nobody writes down — dedup, triage pushback, evidence
hygiene, and the refusal surface.

## What is inside

| Path | Contents |
|---|---|
| `SKILL.md` | Entry point and router. Read this first. |
| `AGENTS.md` | Hard operating contract for agents. |
| `references/` | 26 deep documents: method, every vulnerability class, delivery. |
| `workflows/` | 13 step-by-step playbooks for a full engagement. |
| `checklists/` | 15 testable checklists, one per class plus submission. |
| `templates/` | Report templates for Intigriti, HackerOne, Bugcrowd, YesWeHack; PoC and CVSS worksheets. |
| `prompts/` | Role prompts: recon planner, class selector, triage reviewer, report editor, dedup analyst, exploit reviewer. |
| `tools/` | 13 runnable Python tools: scope, subdomains, probe, exposure, secrets, unauth JSON, GraphQL, JWT, IDOR diff, CVSS, report builder, scope diff, link checker. |
| `data/` | Severity matrix, common paths, sensitive patterns, payload references. |

## Quick start

```bash
git clone https://github.com/briembra/bug-bounty-hunter
cd bug-bounty-hunter
pip install -r tools/requirements.txt
```

Then, for an authorized program:

```bash
python tools/scope.py --platform intigriti --program example -o scope.json
python tools/subdomains.py scope.json -o subs.json
python tools/probe.py subs.json -o alive.json
python tools/exposure.py alive.json -o exposures.json
python tools/secrets.py alive.json -o secrets.json
python tools/unauth_json.py alive.json -o collections.json
```

Or hand the repo to an agent and let `SKILL.md` route.

## Install as a skill

**Claude Code / Codex / Cursor (plugin):** the manifests in `.claude-plugin/`,
`.codex-plugin/`, and `.cursor-plugin/` point at this repo as a plugin.

**Any agent with a skills directory:** copy or symlink this repository to
`<skills>/bug-bounty-hunter/`. `SKILL.md` carries the frontmatter.

**Manual:** paste `SKILL.md` into the system prompt and reference the folders by
path. The router works without any plugin machinery.

## The three laws

1. **Authorization is the boundary.** Out of scope means it does not exist.
2. **Evidence beats claims.** Request, response, reproduction. Or it is not a finding.
3. **Do not break things.** No DoS, no destructive writes, no mass scanning, no brute force.

## Scope of use

This repository is for testing systems you are **authorized** to test under a
program's published policy, or systems you own. It deliberately contains no
denial-of-service tooling, no credential brute forcers, and no mass scanners.
See [DISCLAIMER.md](DISCLAIMER.md).

## License

MIT. See [LICENSE](LICENSE).
