# Install prompt

Paste this into your agent. It installs the method and the 25 commands for
itself, then waits for a target.

```text
Install the bug bounty method from https://github.com/briembra/bug-bounty-workbench
for the agent you are running in, then report back.

  git clone https://github.com/briembra/bug-bounty-workbench
  cd bug-bounty-workbench
  python tools/sync_commands.py --target <claude|opencode|codex|cursor>

If you cannot tell which agent you are, read INSTALL.md and follow that section.
If you have no shell, read SKILL.md and AGENTS.md instead and treat commands/*.md
as procedures you execute by reading them.

Then read SKILL.md and AGENTS.md, install the commands, and reply in three lines:

  Commands: <n> installed to <path>
  Method:   loaded
  Ready:    waiting for a program, a platform and a target
```

Then:

```
/hunt https://app.example.com "Acme" on Intigriti
```

---

**Variants** — append one line.

| Situation | Line |
|---|---|
| Local copy | `The repository is already at <path>. Work from there.` |
| No network | `Read https://github.com/briembra/bug-bounty-workbench/blob/master/SKILL.md and AGENTS.md directly. Skip the install.` |
| Target known | `Program: <name> on <platform>. Target: <host>. Start with /scope.` |
| Hunting only | `Scope is attached. Anything not in it is out of scope.` |

Per-agent detail, plugin installs and uninstall: [`INSTALL.md`](INSTALL.md).
