# Bug Bounty Hunter

A complete method for authorized bug bounty hunting — from picking a program to a
report a triager accepts without asking a question.

No install. No plugin. You paste one prompt into your agent and it runs on this
repository.

---

## Use it

Open [`PROMPT.md`](PROMPT.md) and copy the block. That is the whole setup.

```
Read https://github.com/briembra/bug-bounty-hunter — start with SKILL.md and
AGENTS.md, then hunt <program> on <platform>, in scope only.
```

The prompt tells the agent to load the method, obey the three laws, establish
scope before the first request, and report back in a fixed shape. Anything that
can read a URL or a folder can run it — Claude, Codex, Cursor, a local model, an
automation harness.

If the agent has no network access, give it the cloned folder instead:

```
The repository is at <local path>. Read <local path>/SKILL.md and
<local path>/AGENTS.md first, then follow their links.
```

---

## What is inside

| Path | Contents |
|---|---|
| `PROMPT.md` | The paste-able prompt. Start here. |
| `SKILL.md` | Entry point and router. What the prompt loads. |
| `AGENTS.md` | Binding operating contract: scope gate, evidence contract, safety rails, stop conditions. |
| `references/` | 26 deep documents: method, every vulnerability class, delivery. |
| `workflows/` | 13 step-by-step playbooks for a full engagement. |
| `checklists/` | 15 testable checklists, one per class plus the submission gate. |
| `templates/` | Report templates for Intigriti, HackerOne, Bugcrowd, YesWeHack; PoC and CVSS worksheets. |
| `prompts/` | Role prompts: recon planner, class selector, triage reviewer, report editor, dedup analyst, exploit reviewer. |
| `tools/` | 13 optional Python tools, standard library only. |
| `data/` | Severity matrix, common paths, sensitive patterns, takeover fingerprints, JWT secret starter, parameter list, subdomain wordlist. |

---

## The tools are optional

Every tool is plain Python 3.10+ with no dependencies. Nothing needs installing;
there is no `pip install` step. The method works entirely by hand — the tools
just do the repetitive parts (scope parsing, probing, CVSS maths, report
rendering).

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
