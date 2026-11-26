# Changelog

## 1.0.0 — 2026-11-26

First release.

- `SKILL.md` router with the three laws, the engagement loop, severity table,
  reporting shape, tooling quickstart, stuck-list, and hard stops.
- 26 reference documents covering program selection, scope, recon, attack
  surface, auth/session, BOLA/IDOR, injection, SSRF, XSS/client-side, file
  handling, business logic and payments, API/GraphQL, cloud, secrets and JS,
  AI/LLM surfaces, caching and protocol, subdomain takeover, mobile/thick
  clients, evidence, severity/CVSS, reporting, triage/dedup, opsec, tooling,
  chaining/escalation, and mindset.
- 13 workflows: new program, recon pass, IDOR, auth bypass, SSRF, XSS,
  injection, business logic, secrets, takeover, AI assistant, submit, dedup.
- 15 checklists including a submission gate.
- Report templates for Intigriti, HackerOne, Bugcrowd, YesWeHack, plus PoC and
  CVSS worksheets.
- 6 role prompts.
- 13 runnable tools with bounded defaults, standard library only.
- `PROMPT.md`: the single paste-able prompt. There is no plugin, manifest, or
  install step — an agent reads the prompt, loads `SKILL.md` and `AGENTS.md`,
  and follows the routes.
- Data files: severity matrix, common paths, takeover fingerprints, sensitive
  patterns, parameter list, JWT secret starter, subdomain wordlist.
