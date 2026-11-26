---
description: Find bug bounty programs worth hunting — by platform, sector, tech stack or a target you already have.
argument-hint: [platform] [sector] [tech] [keyword]
allowed-tools: Bash, Read, WebFetch, WebSearch
---

# /bbw-programs

Find programs, then rank them. This is the search across the places bounties
live: HackerOne, Bugcrowd, Intigriti, YesWeHack, Immunefi, Open Bug Bounty,
huntr, and self-hosted `security.txt` programs.

**Input:** `$ARGUMENTS` — any mix of platform, sector, tech, keyword.

```
/bbw-programs hackerone fintech
/bbw-programs intigriti "e-commerce"
/bbw-programs --tech shopify
/bbw-programs --new        # recently launched programs
```

---

## Step 1 — Search the platforms

Fetch the public directory pages and record what you find:

| Platform | Where |
|---|---|
| HackerOne | `https://hackerone.com/directory/programs` (filter by industry, bounty) |
| Bugcrowd | `https://bugcrowd.com/programs` (filter by category, reward) |
| Intigriti | `https://app.intigriti.com/programs` (filter by sector, status) |
| YesWeHack | `https://yeswehack.com/programs` |
| Immunefi | `https://immunefi.com/bug-bounty/` (smart contracts only) |
| huntr | `https://huntr.com/bounties` (open-source AI/ML) |
| Open Bug Bounty | `https://openbugbounty.org` (VDP, no reward) |

For each candidate, capture: name, platform, program URL, bounty range, response
time, resolved report count, whether test accounts are provided, whether automated
scanning is allowed, and the launch date.

**Self-hosted:** search `intext:"security.txt" inurl:/.well-known` plus the
`safe-harbor` and `policy` fields; a company with a policy and no platform is a
direct-disclosure target.

## Step 2 — Score the candidates

Rank with this, in order:

1. **New or recently expanded scope** — untested surface, fewer duplicates.
2. **Bounty ≥ your floor**, and pays the classes you actually find.
3. **Slow triage or huge resolved count** — deprioritise; likely mined out.
4. **Exclusions** that kill your strengths (e.g. "no auth bugs", "no IDOR").
5. **Test account policy** — programs that give accounts are worth far more,
   because BOLA and logic bugs need two sessions.
6. **Scope shape** — wildcard-heavy = more surface; one marketing site = dead end.

Write the shortlist to `engagements/shortlist.md` as a table, top 5 only.

## Step 3 — Pick one and hand off

Pick the single best and run `/bbw-scope` on it, then `/bbw-recon`.

Never start two programs at once. Depth beats breadth — `references/26`.

---

## Output shape

```
Top 5 (ranked)
1. <program> — <platform> — <why it ranks first> — <scope size> — <bounty>
...
Recommendation: start <program>; first asset <host>; first class <class>.
```

## Stop conditions

- A program with no published scope or rules → skip, do not guess.
- A program that forbids automated testing → you may still hunt by hand; say so.
- VDP-only with no reward → only worth it for reputation; note it and move on.
