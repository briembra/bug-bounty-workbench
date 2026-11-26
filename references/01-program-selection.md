# 01 — Program selection

Choosing the right program is more predictive of your first accepted bug than
your skill level. A good program gives you surface, clarity, and feedback. A bad
one gives you silence.

## The signals that matter

Score each program 1–5 on these, then pick the highest total that matches your
available time.

| Signal | Good | Bad |
|---|---|---|
| Scope size | Wildcards, many apps, APIs | One marketing site |
| Asset type | Customer-facing apps, APIs, auth, payments | Static brochure pages |
| Age of program | 0–12 months, still finding bugs | 4+ years, mined out |
| Response time | Median < 7 days | Weeks of silence |
| Bounty | Pays for the classes you hunt | VDP only, or pays only critical |
| Rules | Clear, permissive, test accounts allowed | Vague, "no automated tools", ambiguous |
| Duplicates | New program, low participant count | 3,000 researchers, 500 reports |
| Disclosure | Public reports you can read | Fully private, no learning |
| Tech | Modern stack, API-first, mobile app | Legacy CMS only |

## Where to find programs

- **HackerOne** — `hackerone.com/directory/programs`, filtered by "bounty
  available", "new". Public disclosed reports are a free education.
- **Bugcrowd** — `bugcrowd.com/programs`, priority briefs are usually quieter.
- **Intigriti** — strong EU programs. Public programs are testable immediately;
  private ones need an invite. Scope lives in the program page HTML.
- **YesWeHack** — EU-heavy, many VDPs, good for regulated sectors.
- **Immunefi** — smart contracts and Web3; different skill set entirely.
- **Open Bug Bounty** — no scope relationship, reports go to site owners. Low yield.
- **Self-hosted** — `/security.txt`, `/responsible-disclosure`, `/.well-known/security.txt`.

## Reading a program in five minutes

1. **Scope table.** Which asset types? Any wildcards? Any `*` on a domain you
   can enumerate?
2. **Exclusions.** Whole classes removed? Read twice.
3. **Bounty table.** What does this program actually pay for? If the top payout
   is for RCE and they exclude everything else, the program is telling you where
   the value is.
4. **Rules.** Test accounts? Automated scanning? Rate limits? Required headers?
5. **Disclosed reports.** Sort by "newest" and "highest". You are looking for
   the *shape* of accepted bugs, not to duplicate them.

## The economics of picking

- A wildcard with 500 live hosts at 5% acceptance beats one app at 40%
  acceptance if you can process 100 hosts in the time you would spend on one app
  — *only if* you can process them for the same classes.
- Depth wins on mature programs; breadth wins on new ones.
- The best programs for a HIGH are those with **authentication, multiple roles,
  object ids, and money movement**. Those four create authorization bugs, and
  authorization bugs are the highest-yield class in the last five years.

## Programs to skip

- No scope, no rules, "test anything of ours".
- Scope only says "our website".
- Payouts only for critical with no VDP credit.
- Program has 0 reports resolved in 6 months.
- Wildcard scope with no list of what exists (you will spend the whole budget
  enumerating).

## First-hour checklist

- [ ] Read scope and rules, save them locally.
- [ ] Check `security.txt`, `robots.txt`, `sitemap.xml` on the primary domain.
- [ ] Enumerate subdomains (see `03-recon.md`).
- [ ] Identify the top 5 "interesting" hosts by name and tech.
- [ ] Pick **one** and build its model before touching the others.
- [ ] Set a request budget and a time box.

Do not start with the main marketing site unless it is the only thing in scope.
Start with the app where users log in.
