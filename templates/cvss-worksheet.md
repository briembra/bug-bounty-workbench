# CVSS worksheet

Fill this before writing a report. It forces you to match the score to the
impact you actually demonstrated.

---

## The finding in one sentence

```
<who> can <do what> to <whose data / what function> by <how>, at <scale>.
```

---

## Metric decisions

| Metric | Value | Why (one line) |
|---|---|---|
| AV | N / A / L / P | Web-hosted = N |
| AC | L / H | H only if race, config, or prior info required |
| PR | N / L / H | N anonymous, L any user, H admin |
| UI | N / R | R if the victim must click/open something |
| S | U / C | C only if it crosses a security authority (tenant, admin) |
| C | N / L / H | H if you read sensitive data |
| I | N / L / H | H if you can modify any data |
| A | N / L / H | H only with proof of availability impact (rare, excluded) |

Vector: `AV:_/AC:_/PR:_/UI:_/S:_/C:_/I:_/A:_`

Score with:

```bash
python tools/cvss.py "AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N"
```

---

## Sanity checks

- [ ] If I claim `C:H`, did I show sensitive data? (PII, payment, auth material)
- [ ] If I claim `I:H`, did I show a write? (not "could")
- [ ] If I claim `S:C`, does it cross a tenant or privilege boundary?
- [ ] If I claim `PR:N`, did I demonstrate it without any login?
- [ ] If I claim `A:H`, am I sure? (usually no)
- [ ] If I claim `AC:H`, is the difficulty real?
- [ ] Does the program have its own severity matrix that caps this?

---

## Impact sentence (must match the vector)

```
An <PR> attacker can <C/I/A> <what data> for <scope> by <how>. No rate limit.
```

---

## Final

```
Severity: <Critical|High|Medium|Low>
Vector:   <vector>
Score:    <score>
CWE:      <id>
```
