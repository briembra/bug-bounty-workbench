# Workflow 13 — Dedup check

Five minutes that saves a rejected report. Run before writing, and again before
submitting.

---

## Step 1 — Disclosed reports (2 min)

- HackerOne: `https://hackerone.com/<program>/hacktivity` → filter "Disclosed".
- Bugcrowd: program → "Activity".
- Intigriti: program page → "Reports" (public ones).
- YesWeHack: program → "Reports".

Search for the endpoint path, the parameter name, and the class. If a disclosed
report matches the **root cause**, yours is likely a duplicate.

---

## Step 2 — Search engines (1 min)

```
site:hackerone.com "<endpoint>"
site:bugcrowd.com "<endpoint>"
"<program>" "<class>" writeup
```

Also check `github.com` for the endpoint in public repos / writeups.

---

## Step 3 — Changelog and releases (1 min)

If the program shipped a fix that matches your bug in the last weeks, it is
almost certainly known. Check the app's changelog, release notes, and the mobile
app store "What's New".

---

## Step 4 — Your own history (30 s)

```
grep -r "<endpoint>" findings/
```

Have you reported this before? Update the existing report; do not file twice.

---

## Step 5 — Classify

| Finding | Action |
|---|---|
| Same root cause, same endpoint | Duplicate — do not submit |
| Same root cause, different endpoint, same code path | Likely duplicate — only submit with a distinct impact |
| Same class, genuinely different code path | Submit, state the difference |
| Same bug on staging vs prod | One report (prod) |
| Your earlier report | Update, do not duplicate |

---

## Step 6 — Note it in the report

State what you checked:

> Searched disclosed reports and public writeups for `/api/orders` and
> "IDOR order" — no matching report. The closest disclosed finding is on
> `/api/invoices`, a different code path.

This single sentence prevents the "already known" bounce.

---

## Definition of done

- [ ] Disclosed reports searched.
- [ ] Search engines checked.
- [ ] Changelog checked.
- [ ] Own history checked.
- [ ] Classified.
- [ ] Dedup note written into the report.
