# The prompt

```
Install this for me: https://github.com/briembra/bug-bounty-workbench
```

That is it. Nothing to configure, nothing to paste after it.

The agent reads the repository and finds its own instructions at the top of
[`README.md`](README.md#if-you-are-the-agent) — run the installer, or read the
method directly if it has no shell.

---

**After the install it says "Ready".** Then one command:

```
/hunt https://app.example.com "Acme" on Intigriti
```

**Optional additions** to the same prompt, if the agent asks for more:

| Situation | Add |
|---|---|
| Target known | `Then hunt <host> from the <program> program on <platform>.` |
| One agent only | `Install for claude only.` |
| No npm | `Use the flag: --global.` |

Manual paths, plugin installs and uninstall: [`INSTALL.md`](INSTALL.md).
