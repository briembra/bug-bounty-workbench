# Changelog

## 1.3.4 — 2026-11-26

Payout speed is part of the ranking.

- `references/01` gains **How fast it pays**: where each platform publishes
  response and payout medians, what to record per candidate, an expected-value
  formula that weights the payout wait, and the red flags (nothing paid in 90
  days, "at our discretion" with no history, one huge critical two years ago and
  silence since).
- Ranking in `/bbw-programs` is now surface age → payout speed → bounty floor →
  triage → exclusions → test accounts → scope shape. Shortlist carries the median
  payout days in its own column.
- Signal table gains a payout-speed row: under 30 days is good, 90+ is a warning.
- Rule of thumb: among candidates that pass the surface-age gate, prefer the one
  that pays a median you would accept, in under 30 days, recently.

## 1.3.3 — 2026-11-26

Default is the newest surface, not the flagship.

- `references/01` now leads with the point that most bugs on an old program are
  already found, and that going deep on an old target needs a named edge (stack
  knowledge, source access, a test account nobody else has, a class you are
  strong in).
- New scoring table: **months since the surface changed** — under 3 months is 5,
  3–6 is 4, 6–12 is 3, 12–24 is 1, older with thousands of resolved reports is 0
  and skipped. Score the newest asset, not the program.
- Explicit mined-out skip list (4+ years, 3,000+ resolved, no scope change in 12
  months, no app release in 18 months).
- `/bbw-programs` ranks surface age first as a hard gate and puts the score in its
  own column on the shortlist.
- `/bbw-hunt` gains **Step 0.5** — check how old the surface is before mapping,
  and name the newest in-scope asset when the handed target is the old flagship.
- Budget rule is now 90% newest surface / 10% flagship.

## 1.3.2 — 2026-11-26

Say less.

- `AGENTS.md` §5 is now a binding brevity contract: answer first, no preamble,
  three lines for a status, four for a finding, no recap, plain words, match the
  user's language, stop when done.
- `SKILL.md` gains **How to talk** with the same rules in short form.
- `commands/README.md` states the reporting shape once for all 25 commands.
- Platform reports are explicitly exempt: short for the user, complete for the
  triager.

## 1.3.1 — 2026-11-26

Freshness, in the program-selection path.

- `references/01-program-selection.md` gains **Freshness: hunt new surface, not
  new programs** — a signal table (scope updates, acquisitions, new features, v2
  APIs, newest certificates, app releases, migrations, deadline features, beta
  flows), where "new" misleads, and a 70/30 budget rule.
- `/bbw-programs --fresh` scores candidates on surface added in the last 90 days
  instead of program age.
- SKILL.md routes "where is there still low-hanging fruit?" to that section.
- Scope drift: save the scope on day one, re-run weekly, diff — every added asset
  is a lead that costs one command.

## 1.3.0 — 2026-11-26

`bbw-` prefix and `update`.

- Every command installs as `bbw-<name>.md`, so typing `bbw` in the agent lists
  all 25: `/bbw-hunt`, `/bbw-scope`, `/bbw-idor`, … Flat prefix rather than a
  `bbw:` namespace because `:` is invalid in Windows filenames and every agent
  accepts the flat form.
- `npx bug-bounty-workbench update` re-applies every recorded install from the
  version on disk, across both scopes, and removes files an earlier version
  wrote that this one no longer produces — so the rename from `/hunt` to
  `/bbw-hunt` cleans up after itself.
- `update --dry-run`, `--json`, `--agent`, `--global` behave as in `setup`.
- Install entries now record `version` and `previousVersion`.
- `tools/sync_commands.py` writes the same prefixed filenames.

## 1.2.0 — 2026-11-26

One-line install.

- npm package: `npx bug-bounty-workbench setup`. Detects Claude Code, OpenCode,
  Cursor or Codex, writes the 25 commands and the method into that agent's
  directories, records what it wrote in `.bbw-manifest.json`.
- `npx bug-bounty-workbench status` reports files present vs recorded;
  `uninstall` removes exactly what `setup` wrote and nothing else.
- Also installable before an npm release: `npx github:briembra/bug-bounty-workbench setup`.
- `bin/bbw.mjs` + `lib/agents.mjs` + `lib/install.mjs`, no dependencies,
  Node 18+.
- `PROMPT.md` down to a five-line block: run the npx command, read `SKILL.md` and
  `AGENTS.md`, reply in three lines.
- `INSTALL.md` leads with the npx path; plugin, Python and no-shell paths kept as
  fallbacks.
- Repository renamed to `bug-bounty-workbench`.

## 1.1.0 — 2026-11-26

Commands and installers.

- **25 slash commands** in `commands/`, one per stage and vulnerability class:
  `hunt`, `programs`, `scope`, `recon`, `surface`, `idor`, `auth`, `ssrf`, `xss`,
  `injection`, `files`, `logic`, `api`, `graphql`, `cloud`, `secrets`, `cache`,
  `takeover`, `mobile`, `ai`, `chain`, `score`, `report`, `dedup`, `submit`.
  Each names its input, its steps, its evidence standard, its output shape and
  its stop conditions.
- `commands/README.md` — index with the recommended chains.
- `INSTALL.md` — install paths for Claude Code (plugin and manual), OpenCode,
  Codex and Cursor, plus uninstall.
- `tools/sync_commands.py` — copies the 25 commands into an agent's command
  directory, converts frontmatter where the agent expects less, installs the
  skill for Claude Code and OpenCode. `--dry-run` supported.
- `.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json`,
  `.codex-plugin/plugin.json`, `.cursor-plugin/plugin.json` — plugin manifests so
  the commands and skill are discoverable without any manual copying.
- `PROMPT.md` rewritten as the install prompt: clone, install for the current
  agent, load `SKILL.md` + `AGENTS.md`, report back in three lines, wait.
- `SKILL.md` gains a command index; `README.md` gains install and the 25-command
  table.

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
