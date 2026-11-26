# The prompt

One block. Paste it into your agent and it installs the method and the 25
commands for itself.

Works in Claude Code, OpenCode, Codex, Cursor, and anything else that can run a
shell command and read a file. No plugin loader required, though
[`INSTALL.md`](INSTALL.md) has the plugin path for Claude Code if you prefer it.

---

## Copy this

```text
Install the bug bounty hunting method from https://github.com/briembra/bug-bounty-hunter
into this agent, then confirm it loaded.

1. Get the repository:
     git clone https://github.com/briembra/bug-bounty-hunter
   If git is unavailable, download the archive:
     https://github.com/briembra/bug-bounty-hunter/archive/refs/heads/master.zip
   Read the top of the repo and identify yourself:
     - Claude Code   -> .claude-plugin/plugin.json, commands/ , SKILL.md
     - OpenCode      -> .opencode/  (command/ and skill/)
     - Codex         -> .codex-plugin/plugin.json, AGENTS.md, ~/.codex/prompts/
     - Cursor        -> .cursor-plugin/plugin.json, .cursor/commands/
     - anything else -> commands/ + SKILL.md + AGENTS.md, read as prose

2. Install the 25 commands for this agent:
     python tools/sync_commands.py --target opencode     # or: claude, cursor, codex
     python tools/sync_commands.py --dir <your command dir>
   The script is standard-library Python. If Python is unavailable, copy
   commands/*.md into your command directory by hand; the files are plain
   markdown with YAML frontmatter.

3. Load the method. Read, in this order:
     SKILL.md        - the router
     AGENTS.md       - the binding conduct contract
   Follow SKILL.md's links into references/, workflows/ and checklists/ as you
   need them. Do not improvise a method when one is provided.

4. Report back in exactly three lines:
     Commands:  <n> installed to <path> — list the first three
     Method:    SKILL.md + AGENTS.md loaded
     Ready:     waiting for a program, a platform and a target

Then do nothing else until I give you a target.

Rules for every engagement after this:
  - Authorization is the boundary. If an asset is not in the program's published
    scope and rules, it does not exist.
  - Evidence beats claims. A finding is a request, a response, and a numbered
    reproduction. If you cannot show it, you have not found it.
  - Do not break things. No denial of service, no mass scanning, no brute force,
    no destructive writes, no social engineering, no contacting real people, no
    touching real customer data beyond the minimum needed to prove impact.
  - Never present a lead as a finding. Say "lead" when it is a lead.
  - Never call something HIGH because it sounds severe. Score it with /score.
  - If a control holds, say "closed" and move on.
  - Short answers. No lectures, no theory where I asked for a result.
```

---

## Variants

**Target already chosen** — append:

```text
Program: <name> on <platform>.
Target: <host or URL>.
Rules I already checked: <rate limit / test accounts / exclusions>.
Start with /scope, then /recon, then /surface.
```

**No shell access, no clone** — replace step 1 with:

```text
Read https://github.com/briembra/bug-bounty-hunter/blob/master/SKILL.md and
.../AGENTS.md directly. Treat commands/*.md as procedures you execute by reading
them. Skip the install step; report only "Method loaded" in step 4.
```

**Local copy** — replace step 1 with:

```text
The repository is already at <local path>. Work from there.
```

**Hunting only, no program selection** — replace step 4 with:

```text
Scope is attached below. Treat anything not in it as out of scope, including
subdomains of a domain that appears in the list.
```

---

## After it says "Ready"

```
/hunt https://app.example.com "Acme" on Intigriti
/programs hackerone fintech
/scope https://app.intigriti.com/programs/acme/detail intigriti
```

Each command is a full procedure with its own input, steps, output shape and stop
conditions. The index is [`commands/README.md`](commands/README.md).

---

## Why a prompt and a script, not just a plugin

A plugin only loads in the tool that built the loader. A prompt that clones a repo
and runs a 100-line copy script works in every agent that can run a shell command,
and the fallback — read `SKILL.md` and `AGENTS.md` as prose — works in the ones
that cannot.

`tools/sync_commands.py` exists so the 25 command files live in exactly one place
in the repository and are still installable into four different directory layouts.
It is the only thing that touches your filesystem, and `--dry-run` shows what it
would write.
