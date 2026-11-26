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
| Payout speed | Median report-to-money < 30 days, paid recently | 90+ days, nothing paid in months |
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

Most bugs on a program that has been open for four years are already found. Not
all of them, but the ones you can reach in an evening are. So the default is:
**hunt the newest surface you can find, and only go deep on something old when you
have a specific edge.**

Edges that justify an old target: you know the stack from work, you have source or
a decompiled client, you have a test account the rest of the crowd does not, or the
bug class is one you hunt better than the average participant.

That is it. Otherwise, spend your time where nobody has looked yet.

## What counts as new surface

Program age is the wrong number. Scope-change age is the right one. A program
launched in 2019 that shipped a new product last month is a better target than a
program launched last month with one marketing site.

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

## How fast it pays

A paid bug in six months is worse than a paid bug in three weeks. Money you cannot
plan on is not money, and a program that sits on reports is a program whose
researchers leave. Time-to-payout belongs in the ranking next to bounty size.

Every platform publishes the numbers; read them instead of guessing:

| Platform | Where the numbers are |
|---|---|
| HackerOne | Program page "Response Efficiency" — average time to first response, time to triage, time to bounty, time to resolution. Disclosed reports show each transition with dates. |
| Bugcrowd | Program page shows average payout and reward range; the activity feed shows recent submissions and their state. |
| Intigriti | Program page shows response time and average payout; disclosed reports carry the full timeline. |
| YesWeHack | Program page shows average bounty and response time. |
| Immunefi | Per-program payout terms; severity-based fixed amounts, paid in crypto. |

Median beats average on every one of these. A program with a 30-day average is
usually a program with a fast median and two abandoned reports from 2021.

**What to record per candidate:**

- Median time to first response (hours or days)
- Median time to bounty, report to money
- Average or median bounty paid, and the floor for the class you hunt
- Paid-report ratio: how many reports actually result in a reward
- Recent activity: any bounty paid in the last 30 days

**How to weigh it.** A rough expected value per hunting hour, in the order the
factors actually bite:

```
EV ≈ P(accept) × median_bounty ÷ (hunt_hours + payout_wait_in_working_days × 0.2)
```

The 0.2 is a deliberately small weight: waiting is not work, but a program that
pays in 180 days also triages in 180 days, which means your next three reports are
sitting in the same queue. Treat a payout lag over 60 days as a signal about the
whole program, not just the money.

**Red flags that override a good payout number:**

- No bounty paid in the last 90 days on a program that claims bounties.
- Payout terms changed recently, or "bounty at our discretion" with no published
  history.
- Currency or payment method you cannot actually receive, or a threshold below
  the platform's payout minimum.
- A high average bounty produced by one huge critical two years ago and nothing
  since. Read the distribution, not the headline.

**The practical rule:** among candidates that pass the surface-age gate, prefer the
one that pays a *median* you would accept, in under 30 days, on reports they have
paid recently. A slightly smaller bounty that lands in three weeks funds the next
month of hunting. A large bounty that lands in six months does not.

## Score by months since the surface changed

Use this instead of "program age" when ranking:

| Last meaningful change | Score | Reading |
|---|---|---|
| Under 1 month | 5 | Land rush, but nothing is picked over yet |
| 1–3 months | 5 | Best window: shipped, rarely tested |
| 3–6 months | 4 | Still good; low-hanging gone, depth remains |
| 6–12 months | 3 | Needs a class you are strong in |
| 12–24 months | 1 | Only with an edge |
| Over 24 months, thousands of resolved reports | 0 | Skip |

Take the score of the **newest asset in scope**, not of the program. A mature
program with a three-week-old acquisition scores 5 on that asset.

## Programs that are already mined out

Skip by default, unless you have one of the edges above:

- Open 4+ years, 3,000+ resolved reports, no scope change in 12 months.
- No new app release in 18 months on a program that is app-only.
- Top payouts all for RCE, everything else excluded, and no source access.
- Public writeups already cover the classes you hunt on that exact stack.

That is not a judgement on the program. It is arithmetic: the crowd got there
first, and your hours are better spent on an asset with forty reports instead of
four thousand.

## Where "new" lies to you

- Brand-new programs often have a two-week land rush of obvious bugs, then silence,
  and a triage team still learning its own policy. Real payout table, unreliable
  acceptance.
- Launched features frequently had a pentest before launch. The gap is usually in
  the integration: SSO on the new app, permissions on the new object, the old
  endpoint that now accepts the new id.
- Acquisitions are routinely excluded in writing. Read the exclusion list before
  you get excited about the shiny new domain.
- A wildcard added with nothing resolving is enumeration cost, not surface.
- An asset added to scope is not the same as an asset deployed. If it 404s, it is
  not surface yet — note it and check again in a month.

## Budget rule

Default split: **90% on the newest surface, 10% on the flagship** where depth and
your edge still pay. If nothing in scope has changed in a year, pick another
program rather than grinding a mined-out app.

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
