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

## Freshness: hunt new surface, not new programs

Age of program is a weak signal on its own. What predicts a find is **how recently
the surface changed** and **whether the program pays for what you find there**.

The sweet spot is not the newest program on the platform. It is a program with a
real bounty table and functioning triage where something was added recently —
an acquired product, a new feature, a v2 API, a new app version. The flagship app
may have 4,000 reports against it; the thing they shipped last month has twenty.

| Signal | Where to look | Why it is fresh |
|---|---|---|
| Scope updated / expanded | Program page "last updated", scope diff, changelog | Added assets were reviewed by nobody |
| Acquisition | Press page, "we've acquired X", investor news | Acquired app joins scope later than the buyer's app |
| New product or feature | `/whats-new`, `/changelog`, release notes, blog, docs "beta" | Shipped after the last pentest, or before the first one |
| New API version | `/v2`, `/v3`, `/graphql` beside an older REST API | Often built by a different team with different authz |
| New subdomain | `crt.sh` `notBefore` on the newest certs, CT logs | Newest hosts are the least enumerated |
| New app release | App Store / Play "What's New", version history | New endpoints in the diff, old ones already picked over |
| Migration | Job posts naming a new stack, CDN or header change | Rewrites reintroduce old classes |
| Calendar | Tax season, enrolment windows, Black Friday, elections | Features get built under deadline pressure |
| Beta / waitlist / labs | `/beta`, `/labs`, invite-only flows | Authz and rate logic are usually incomplete |

**Scope drift is the cheapest signal you have.** Save the scope on day one with
`/bbw-scope`, then re-run it weekly and diff. Every added asset is a lead that
costs you one command.

**Where "new" lies to you:**

- Brand-new programs often have a two-week land rush of obvious bugs, then silence,
  and a triage team still learning its own policy. Real payout table, unreliable
  acceptance.
- Launched features frequently had a pentest before launch. The gap is usually in
  the integration: SSO on the new app, permissions on the new object, the old
  endpoint that now accepts the new id.
- Acquisitions are routinely excluded in writing. Read the exclusion list before
  you get excited about the shiny new domain.
- A wildcard added with nothing resolving is enumeration cost, not surface.

**Budget rule:** about 70% of your time on the newest surface of a program that
pays, 30% on the flagship app where depth still wins. Between those two, some of
your flagships come out of the diff.

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
