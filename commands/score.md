---
description: Score a confirmed finding honestly — CVSS vector, program severity table, impact sentence.
argument-hint: <finding> or <cvss vector>
allowed-tools: Bash, Read
---

# /bbw-score

`references/20`, `data/severity-matrix.md`, `templates/cvss-worksheet.md`,
`tools/cvss.py`.

**Input:** `$ARGUMENTS` — a finding summary, or a vector you already built.

```
/bbw-score "BOLA read on /api/orders/{id} — other customer's order incl. address+phone"
/bbw-score "AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N"
```

Scoring is where good findings die. Two rules:

1. **Score the impact you proved**, not the impact you imagined.
2. **The program's table wins** over CVSS when they disagree.

---

## Step 1 — Build the vector from the evidence

`python tools/cvss.py "AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N"`

Work each metric against proof, not vibes:

| Metric | Question | Trap |
|---|---|---|
| `AV` | reachable over the internet? | internal-only = `A` |
| `AC` | needs luck, a race, or a special state? | race = `H` |
| `PR` | what does the attacker need first? | own account = `L` |
| `UI` | must a victim click? | victim click = `R` |
| `S` | does it cross a security boundary? | cross-tenant = `C` |
| `C/I/A` | what data or state is affected? | one field ≠ `H` |

## Step 2 — The honest downgrades

Apply every one that is true:

- [ ] Data is **demo, seed, or test** → down one band
- [ ] Requires a **victim to click** and no other precondition → `UI:R`
- [ ] Only **your own** account affected → not a bug
- [ ] Field is **public by design** (display name, avatar) → `C:L` or Info
- [ ] **Self-XSS**, no chain → Info/Low, usually excluded
- [ ] Rate limiting absent only → Low, usually excluded
- [ ] Missing headers only → Info
- [ ] Email/username **enumeration** alone → Low
- [ ] Out-of-date software, **no working exploit** → Info
- [ ] Requires **rooted device / physical access** → Low
- [ ] **Requires admin** already → much lower
- [ ] One record vs all records → `C:L` vs `C:H`

If you downgrade, say why in one line. Triagers respect it; they punish inflation.

## Step 3 — Map to the program's table

Open the program's own severity policy. Most map like this:

| CVSS | Typical program band | Typical bounty |
|---|---|---|
| 9.0–10.0 | Critical | top |
| 7.0–8.9 | High | high |
| 4.0–6.9 | Medium | mid |
| 0.1–3.9 | Low | low |
| 0.0 | None / informational | none |

If the program pays by class rather than CVSS, use their class names. If they pay
flat per severity, match the band, not the decimal.

## Step 4 — Write the impact sentence

One sentence, attacker-gains framing:

> *"An authenticated customer can read any other customer's order — including full
> name, address, phone and last four of the payment card — by changing the numeric
> id in `GET /api/orders/{id}`, with no rate limit and no audit trail."*

Not: *"IDOR on the orders endpoint."* That is a class name, not impact.

## Step 5 — Cross-check against the matrix

`data/severity-matrix.md` has the house view per class. If your score is two bands
above the matrix for that class, you are probably wrong. Re-read the evidence.

## Step 6 — Handle disagreement

If the triager scores lower:

- Ask which metric they disagree with, not for a higher number
- Provide the one piece of evidence that justifies your metric
- Accept it if they are right; most disagreements are `S` and `C`
- Never argue about bounty amount

---

## Output shape

```
finding: <one line>
vector: <AV:..>
score: <n.n>  band: <Critical|High|Medium|Low>
program table: <their band>
downgrades applied: <list or none>
impact: <one sentence>
next: /bbw-report
```

## Stop conditions

- Score depends on a **guess** about internal impact → state the assumption, score
  conservatively, say "provisional".
- Program excludes the class entirely → do not report; say so.
- Two independent scorers would land two bands apart → you have not proved impact.
