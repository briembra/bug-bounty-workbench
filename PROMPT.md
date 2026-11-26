# Install prompt

Paste this into your agent. It installs the method and the 25 commands for
itself, then waits for a target.

```text
Install the bug bounty method: run

  npx bug-bounty-workbench setup

If that package is not published yet, use the repository form:

  npx github:briembra/bug-bounty-workbench setup

It detects which agent you are and writes the 25 commands plus the method into
that agent's directories. Then read SKILL.md and AGENTS.md from
https://github.com/briembra/bug-bounty-workbench and reply in three lines:

  Commands: <n> installed to <path>
  Method:   loaded
  Ready:    waiting for a program, a platform and a target
```

Then:

```
/hunt https://app.example.com "Acme" on Intigriti
```

---

**No Node, no shell** — use this instead:

```text
Read https://github.com/briembra/bug-bounty-workbench/blob/master/SKILL.md and
AGENTS.md, then treat commands/*.md as procedures you execute by reading them.
Reply: Method loaded — waiting for a program, a platform and a target.
```

**Variants** — append one line.

| Situation | Line |
|---|---|
| Agent not detected | `Run: npx bug-bounty-workbench setup --agent <claude\|opencode\|cursor\|codex>` |
| Local copy | `The repository is already at <path>. Work from there.` |
| Target known | `Program: <name> on <platform>. Target: <host>. Start with /scope.` |
| Hunting only | `Scope is attached. Anything not in it is out of scope.` |

Per-agent detail, plugin installs and uninstall: [`INSTALL.md`](INSTALL.md).
