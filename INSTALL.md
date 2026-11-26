# Install

Four agents, four paths. Every one of them ends with 25 `/` commands and the
method loaded. Nothing needs `pip install` — the tools are standard-library
Python 3.10+.

Pick your agent, run the block, done.

---

## Claude Code

**Plugin (recommended).** Inside Claude Code:

```
/plugin marketplace add briembra/bug-bounty-workbench
/plugin install bug-bounty-workbench@bug-bounty-workbench
```

Restart the session. `/hunt`, `/programs`, `/scope` and the rest appear in the
command list, and the skill loads when you ask about a target.

**Manual.** Clone and copy:

```bash
git clone https://github.com/briembra/bug-bounty-workbench
cd bug-bounty-workbench
python tools/sync_commands.py --target claude
```

That writes `.claude/commands/*.md` (25 commands) and
`.claude/skills/bug-bounty-workbench/SKILL.md` (the method) into the current project.
For a personal install everywhere, copy the same two trees into `~/.claude/`:

```bash
cp -r .claude/commands/*  ~/.claude/commands/
cp -r .claude/skills/bug-bounty-workbench ~/.claude/skills/
```

---

## OpenCode

```bash
git clone https://github.com/briembra/bug-bounty-workbench
cd bug-bounty-workbench
python tools/sync_commands.py --target opencode
```

Writes `.opencode/command/*.md` and `.opencode/skill/bug-bounty-workbench/SKILL.md`.
OpenCode picks both up from the project root; for a global install, copy the same
two directories into `~/.config/opencode/`:

```bash
mkdir -p ~/.config/opencode/command ~/.config/opencode/skill
cp -r .opencode/command/* ~/.config/opencode/command/
cp -r .opencode/skill/bug-bounty-workbench ~/.config/opencode/skill/
```

Then in a session: `/hunt https://app.example.com "Acme" on Intigriti`.

---

## Codex

Codex reads `AGENTS.md` from the working directory automatically, and custom
prompts from `~/.codex/prompts/`.

```bash
git clone https://github.com/briembra/bug-bounty-workbench
cd bug-bounty-workbench
python tools/sync_commands.py --target codex
mkdir -p ~/.codex/prompts
cp .codex/prompts/*.md ~/.codex/prompts/
```

Codex strips the frontmatter keys it does not define and keeps the procedure.
Run it from the cloned directory so `AGENTS.md` and `SKILL.md` resolve, or point
it at the path in your first message.

---

## Cursor

```bash
git clone https://github.com/briembra/bug-bounty-workbench
cd bug-bounty-workbench
python tools/sync_commands.py --target cursor
```

Writes `.cursor/commands/*.md`. Add the method as a project rule so the agent
always has it:

```
.cursor/rules/bug-bounty-workbench.mdc
---
description: Authorized bug bounty hunting method
globs:
alwaysApply: true
---
```

…with the contents of `SKILL.md` under the frontmatter, or simply paste the block
from [`PROMPT.md`](PROMPT.md) into the chat once.

---

## Any other agent

Two options, both work:

**One prompt.** Copy the block in [`PROMPT.md`](PROMPT.md). It tells the agent to
read `SKILL.md` and `AGENTS.md` from the repository and follow the routes. The
25 commands are then procedures the agent runs by reading
`commands/<name>.md`.

**Copy the files.** Any agent with a command or prompt directory:

```bash
python tools/sync_commands.py --dir <your-agent>/commands
```

---

## Verify the install

```bash
python tools/sync_commands.py --dry-run --target opencode   # lists 25
ls .opencode/command | wc -l                                 # 25
```

Then in the agent:

```
/hunt --help
```

…or just `/hunt https://app.example.com` on a target you are authorized to test.

If the commands do not appear, the frontmatter is the usual cause: the file must
start with `---` on line 1, have a `description:`, and close with `---`.

---

## What you get

| Path | Contents |
|---|---|
| `commands/` | 25 slash commands, one per hunt stage and class. |
| `SKILL.md` | The router the skill loads. |
| `AGENTS.md` | The binding conduct contract: scope gate, evidence, safety rails. |
| `references/` | 26 deep documents. |
| `workflows/` | 13 end-to-end playbooks. |
| `checklists/` | 15 testable gates. |
| `templates/` | Report templates for four platforms, PoC and CVSS sheets. |
| `prompts/` | 6 role prompts for sub-agents. |
| `tools/` | 14 Python scripts, standard library only. |
| `data/` | Severity matrix, paths, patterns, fingerprints, wordlists. |

---

## Uninstall

```bash
rm -rf .claude/commands .claude/skills/bug-bounty-workbench
rm -rf .opencode/command .opencode/skill/bug-bounty-workbench
rm -rf .cursor/commands .codex/prompts
```

Nothing is installed outside those directories and the plugin cache your agent
manages.
