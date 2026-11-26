---
description: Find dangling CNAMEs and claim the service before someone else does — safely and in scope.
argument-hint: <host or subs.json>
allowed-tools: Bash, Read, Write, WebFetch
---

# /bbw-takeover

`references/17`, `workflows/10`, `checklists/takeover.md`,
`data/takeover-fingerprints.txt`.

**Input:** `$ARGUMENTS` — a host, or the `alive.json` from `/bbw-recon` with
`takeover_hint` set.

```
/bbw-takeover https://dev.acme.com
/bbw-takeover engagements/acme/alive.json
```

The bug is a subdomain pointing at a service nobody owns any more. Claiming it is
the proof. Claiming it **wrong** is a rule violation.

---

## Step 1 — Confirm the CNAME dangles

```bash
# what does it point at?
python tools/probe.py <subs.json> -o alive.json --threads 1
# or by hand
nslookup -type=CNAME dev.acme.com 8.8.8.8
dig +short CNAME dev.acme.com
dig +short dev.acme.com
```

Dangling looks like:

| Symptom | Meaning |
|---|---|
| CNAME exists, target returns NXDOMAIN | service gone — claimable |
| CNAME to `*.herokuapp.com` + 404 "no such app" | claimable |
| CNAME to `*.s3.amazonaws.com` + `NoSuchBucket` | claimable |
| CNAME to `*.github.io` + 404 | claimable if the username is free |
| CNAME to `*.azurewebsites.net` + 404 | claimable |
| CNAME to `*.cloudfront.net` + `Bad request` | usually **not** claimable |

Fingerprints in `data/takeover-fingerprints.txt`. Match the body text, not the
status code.

## Step 2 — Decide whether you may claim

Check the rule first, in this order:

1. Is the host **in scope**? Wildcard covers subdomains, not the target service.
2. Does the program explicitly **allow** takeover claims?
3. Would claiming it require registering an account on a third-party service?
4. Would claiming it affect other users right now?

If any answer stops you, **do not claim**. Report the dangling CNAME as a
low-severity finding with the evidence that it is dangling, and say the claim was
not performed.

## Step 3 — Claim the minimum

Only when all four pass:

- Register the free tier with `bramontech+bbtest@gmail.com`
- Publish **one static file** that says `bbtest-<date>` and nothing else
- Do not deploy anything that collects data, redirects, or serves JS
- Do not point it at a page that looks like the target's login
- Screenshot the claimed host resolving to your marker
- Save the registration confirmation

That marker file **is** the proof. No phishing page, ever.

## Step 4 — Prove it resolves

```bash
curl -s https://dev.acme.com/ | head -20
# must contain bbtest-<date>
```

Save: DNS answer, HTTP response, marker content, registration screenshot. Four
artefacts, one folder.

## Step 5 — Release

After you have the evidence:

1. Delete the resource on the third-party service.
2. Wait for the CNAME to stop resolving to you.
3. Tell the program exactly what you claimed and when you released it.

Leaving it claimed is how researchers get banned. Release is part of the finding.

## Step 6 — Severity

| Situation | Severity |
|---|---|
| Dangling CNAME, claimable, no claim made | Low–Medium |
| Claimed + marker served on target subdomain | Medium–High |
| Claimed + cookies in scope / SSO callback on that host | High |
| Claimed + can receive password-reset emails | Critical |

Do not inflate. A dangling CNAME with no cookie scope is Medium.

---

## Output shape

```
candidates: N   dangling: N   claimable: N
claimed: yes/no — <host> — <service>
marker: bbtest-<date>  released: yes/no
evidence: findings/<slug>/
severity: <band>
next: /bbw-score then /bbw-report
```

## Stop conditions

- Claim would require a paid plan or an identity you do not have → report dangling
  only.
- Target service is out of scope → do not claim, note it.
- You cannot release afterwards → do not claim.
- The host would receive real user traffic → report immediately, do not sit on it.
