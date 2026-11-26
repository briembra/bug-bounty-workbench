# Install

Node 18+. No dependencies, no build step.

```bash
npx bug-bounty-workbench setup
```

That is the whole install for Claude Code, OpenCode, Cursor and Codex. It detects
which agent you are in, copies the 25 commands and the method into that agent's
directories, records exactly what it wrote, and prints the next command.

```bash
npx bug-bounty-workbench setup --agent claude --global   # user-level dirs
npx bug-bounty-workbench setup --agent claude,opencode   # more than one
npx bug-bounty-workbench setup --dry-run                 # print the plan
npx bug-bounty-workbench status                          # files present vs recorded
npx bug-bounty-workbench uninstall                       # remove what setup wrote
npx bug-bounty-workbench --help
```

Not published to npm yet? Install straight from the repository:

```bash
npx github:briembra/bug-bounty-workbench setup
```

---

## Where it writes

| Agent | Project | Global (`--global`) |
|---|---|---|
| Claude Code | `.claude/commands`, `.claude/skills/bug-bounty-workbench` | `~/.claude/…` |
| OpenCode | `.opencode/command`, `.opencode/skill/bug-bounty-workbench` | `~/.config/opencode/…` |
| Cursor | `.cursor/commands` | `~/.cursor/commands` |
| Codex | — | `~/.codex/prompts` |

Detection: project markers first (`.claude/`, `.opencode/`, `.cursor/`, `.codex/`),
then the process environment (`CLAUDECODE`, `OPENCODE`, `CURSOR_TRACE_ID`,
`CODEX_HOME`). If neither hits, pass `--agent`.

A `.bbw-manifest.json` in the project root (or `~`) lists every file written, so
`uninstall` removes those and nothing else.

---

## Claude Code plugin

If you prefer the plugin loader over the CLI:

```
/plugin marketplace add briembra/bug-bounty-workbench
/plugin install bug-bounty-workbench@bug-bounty-workbench
```

Restart the session. Same 25 commands, same skill.

---

## No Node

**Python path** — clone and copy:

```bash
git clone https://github.com/briembra/bug-bounty-workbench
cd bug-bounty-workbench
python tools/sync_commands.py --target opencode   # or: claude, cursor, codex
```

`--dir <path>` writes to any command directory. `--dry-run` lists first.

**No shell at all** — paste the block in [`PROMPT.md`](PROMPT.md). The agent reads
`SKILL.md` and `AGENTS.md` from the URL and treats `commands/*.md` as procedures.

---

## Verify

```bash
npx bug-bounty-workbench status
```

```
bug-bounty-workbench 1.2.0

ok    claude  project  133/133 files  2026-11-26T17:57:01.616Z
```

`drift` means a file recorded in the manifest is gone — usually another tool
cleaned the directory. Re-run `setup`.

Then in the agent: `/hunt https://app.example.com`.

---

## What you get

| Path | Contents |
|---|---|
| `commands/` | 25 slash commands, one per hunt stage and class. |
| `SKILL.md` | The router the skill loads. |
| `AGENTS.md` | The conduct contract: scope gate, evidence, safety rails. |
| `references/` | 26 deep documents. |
| `workflows/` | 13 end-to-end playbooks. |
| `checklists/` | 15 testable gates. |
| `templates/` | Reports for four platforms, PoC and CVSS sheets. |
| `prompts/` | 6 role prompts for sub-agents. |
| `tools/` | 14 Python scripts, standard library only. |
| `data/` | Severity matrix, paths, patterns, fingerprints, wordlists. |

---

## Uninstall

```bash
npx bug-bounty-workbench uninstall                        # project installs
npx bug-bounty-workbench uninstall --global               # user-level installs
npx bug-bounty-workbench uninstall --agent claude         # one agent only
```

Only files listed in the manifest are removed. Directories it created are removed
when they end up empty.
