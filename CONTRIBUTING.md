# Contributing

Contributions are welcome when they make a hunter's next engagement measurably
better. That means one of:

- a new vulnerability-class document with a real, current technique,
- a workflow that removes a step or a guess,
- a tool that runs and is bounded by default,
- a template or checklist that prevents a rejected report.

## Rules for contributions

1. **No destructive tooling.** Nothing that sends load, brute forces, or writes
   destructively. PRs with those are closed without discussion.
2. **Every technique must be testable.** State the precondition, the request,
   the observable result, and the failure mode.
3. **Evidence over anecdote.** If you add a class, include what a confirming
   response looks like and what a false positive looks like.
4. **Keep the voice.** Direct, technical, no hype, no "hacking" theatre.
5. **Link the source of a claim** when it is version-specific or
   vendor-specific. Out-of-date claims are worse than none.

## Adding a vulnerability class

Create:

```
references/NN-<class>.md
workflows/NN-hunt-<class>.md
checklists/<class>.md
```

Add it to the router table in `SKILL.md`, the command index in `SKILL.md`, and the
index in `commands/README.md` if you add a command. Keep the numbering stable once
published.

## Adding a command

```
commands/<name>.md
```

Frontmatter must have `description`, `argument-hint`, `allowed-tools`. Body must
have: the references it depends on, `**Input:**` with `$ARGUMENTS` and two
examples, numbered steps with the exact commands, `## Output shape`, and
`## Stop conditions`. Then add it to `commands/README.md` and the command index in
`SKILL.md`. `tools/sync_commands.py` picks it up with no change.

## Adding a tool

- Python 3.10+, standard library where possible.
- `--help` works. `--dry-run` exists for anything that sends traffic.
- Bounded defaults: thread cap, request cap, timeout, backoff.
- Prints a summary of what it did and what it skipped, and why.
- Exits non-zero only on real failure, not on "no results".

## Commit style

```
<area>: <what changed>

Why: <the problem it solves>
```

Areas: `references`, `workflows`, `checklists`, `templates`, `tools`, `data`,
`skill`.

## Testing a change

Before opening a PR:

```bash
python -m compileall tools
python tools/cvss.py "AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
python tools/report.py templates/example-finding.yaml --dry-run
```

Skills are prose; read the changed file top to bottom once before submitting.
