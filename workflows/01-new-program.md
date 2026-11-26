# Workflow 01 — New program

Run this once per program. It produces a scope file, a rules summary, and a
prioritised target list. Time box: 90 minutes.

---

## Step 1 — Read the program page (15 min)

- Open the program on its platform.
- Copy the **scope** (all asset types) and the **rules** to a local file.
- Copy the **bounty table** (or note "VDP, no bounty").
- Note the **disclosed reports** count and the newest one.
- Check `security.txt` and `robots.txt` on the primary domain.

Write `engagements/<program>/rules.md` with quoted rules, not your paraphrase.

---

## Step 2 — Normalise the scope (10 min)

```bash
python tools/scope.py --platform <platform> --program <handle> -o engagements/<program>/scope.json
```

If the API returns nothing (some programs), scrape the program's public asset
list and pass it:

```bash
python tools/scope.py --file scope.txt --format text -o engagements/<program>/scope.json
```

Verify: does `scope.json` contain wildcards, hosts, urls, exclusions? If the
count is zero, do not proceed.

---

## Step 3 — Enumerate (20 min)

```bash
python tools/subdomains.py engagements/<program>/scope.json -o engagements/<program>/subs.json
python tools/probe.py engagements/<program>/subs.json -o engagements/<program>/alive.json
```

If the program forbids active enumeration, stop after passive sources and state
that in notes.

---

## Step 4 — Triage (20 min)

Open `alive.json`. Bucket by signal:

- 401/403 → auth exists
- `/bbw-api`, `/bbw-graphql`, `/swagger` → API map
- stage/dev/test in hostname → debug candidates
- login/SSO → auth flows
- admin panels → direct check
- file hosts → ACL check

Write `buckets.md`. Pick **one** target from the highest bucket.

---

## Step 5 — Baseline the chosen target (20 min)

On the one host:

- `GET /`, read the HTML.
- Read `robots.txt`, `sitemap.xml`.
- Download the main JS bundle, grep for `/api/`, `graphql`, base URLs.
- Check `/openapi.json`, `/swagger.json`, `/bbw-graphql`.
- Register or log in (test account if available).
- Write the endpoint inventory to `endpoints.tsv`.

---

## Step 6 — Set the engagement parameters (5 min)

Write at the top of `notes.md`:

```
program:      <name>
platform:     <platform>
scope:        <file>
budget:       <N requests / <rate> per second>
timebox:      <hours>
test accounts: <yes/no, email>
listener:     <interactsh domain>
marker:       bbtest-<date>-<rand>
rules flags:  <e.g. "no automated scanning">
```

---

## Step 7 — Pick the first class

From `04-attack-surface-mapping.md`, pick the highest ceiling that matches the
target:

- Object ids → `03-hunt-idor.md`
- Login/SSO → `04-hunt-auth-bypass.md`
- URL fetch → `05-hunt-ssrf.md`
- Money flow → `08-hunt-business-logic.md`
- API docs → `12-api-and-graphql.md` reference + IDOR workflow
- Chatbot → `11-ai-assistant-deep-dive.md`

Go. Do not run all six in parallel; run one to conclusion, then the next.

---

## Definition of done

- [ ] `scope.json` exists and is non-empty.
- [ ] `rules.md` has quoted rules.
- [ ] `alive.json` exists.
- [ ] `buckets.md` has a ranked list.
- [ ] One target chosen and mapped.
- [ ] Budget and timebox written.

If any is missing, the engagement has not started. It is still setup.
