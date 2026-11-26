---
description: Pull a program's scope and rules into one file you can filter, quote and diff.
argument-hint: <program url or handle> [platform]
allowed-tools: Bash, Read, Write, WebFetch
---

# /bbw-scope

Scope first, always. This command produces the single file every later command
checks against.

**Input:** `$ARGUMENTS` — the program page URL or handle, plus platform.

```
/bbw-scope https://app.intigriti.com/programs/acme/detail intigriti
/bbw-scope acme bugcrowd
```

---

## Step 1 — Get the raw text

Paste the program's asset list and rules into `engagements/<program>/scope.txt`
verbatim. Tag each block:

```
In scope
*.acme.com
acme.com
https://api.acme.com/v2/*
com.acme.app
203.0.113.0/24
Rules: two test accounts on request; automated scanning allowed at ≤5 rps
Excluded
status.acme.com
blog.acme.com
```

For Intigriti the tool can fetch the public page:

```bash
python tools/scope.py --platform intigriti --program acme -o engagements/acme/scope.json
```

Every other platform: paste + `--file`.

```bash
python tools/scope.py --file engagements/acme/scope.txt -o engagements/acme/scope.json
```

## Step 2 — Verify the parse

Open `scope.json` and check every bucket by eye:

- [ ] Wildcards present (`*.acme.com`, not `acme.com`)
- [ ] Hosts exact, lowercased, no stray ports or schemes
- [ ] URLs keep their path pattern
- [ ] Mobile bundle ids (`com.acme.app`)
- [ ] CIDRs (`/24`, not one IP)
- [ ] Exclusions in `excluded`, not in `hosts`
- [ ] `rules_notes` has the rate limit, test-account policy, prohibited actions

If a bucket is empty and should not be, fix the input text. A wrong scope file
poisons the whole engagement.

## Step 3 — Write the rules digest

`engagements/<program>/rules.md`, quoted not paraphrased:

```
Program:        <name>
Platform:       <platform>
Bounty:         <range or VDP>
Response:       <median time, if shown>
Test accounts:  <yes/no/how>
Rate limits:    <stated, or "none stated">
Prohibited:     <list, quoted>
Exclusions:     <list, quoted>
Safe harbour:   <yes/no, link>
```

## Step 4 — Confirm scope for the target you intend to test

Answer in one line, out loud:

```
<host> is in scope because <exact quoted entry>.
```

If you cannot fill that line, you do not have permission. Stop.

## Step 5 — Snapshot for diffing

Keep every later version. Newly added assets are the freshest surface:

```bash
python tools/scope_diff.py engagements/acme/scope-old.json engagements/acme/scope.json
```

---

## Output shape

```
Scope file:  engagements/<program>/scope.json
wildcards: N  hosts: N  urls: N  mobile: N  ips: N  excluded: N
Rules: <one line summary>
Target in scope: yes/no — <quoted entry>
Next: /bbw-recon
```
