# Install prompt

Paste this into your agent. That is the whole install.

```text
Install the bug bounty workbench into this agent:

  npx github:briembra/bug-bounty-workbench setup

Follow what it prints, then wait for my target. If npx is unavailable, read
https://github.com/briembra/bug-bounty-workbench/blob/master/SKILL.md and
AGENTS.md and work from those instead.
```

---

Variants — append one line.

| Situation | Line |
|---|---|
| Target known | `Program: <name> on <platform>. Target: <host>. Start with /scope.` |
| Local copy | `The repo is already at <path>. Work from there.` |
| Install for one agent | `Use --agent claude` (or `opencode`, `cursor`, `codex`). |

Per-agent detail, plugin installs and uninstall: [`INSTALL.md`](INSTALL.md).
