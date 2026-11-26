# Workflow 02 — Recon pass

A full recon pass on a program that already has a `scope.json`. Produces the
alive inventory and the ranked buckets. Time box: 2 hours.

---

## Step 1 — Merge sources (30 min)

```bash
subfinder -d example.com -all -silent > subs.raw
curl -s "https://crt.sh/?q=%25.example.com&output=json" \
  | jq -r '.[].name_value' | tr ',' '\n' >> subs.raw
sort -u subs.raw | grep -v '^\*' > subs.txt
```

Repeat per registrable domain in scope. Merge into `subs.json` via
`tools/subdomains.py`.

---

## Step 2 — Resolve (15 min)

```bash
dnsx -l subs.txt -a -resp -silent -o resolved.txt
```

Annotate CNAMEs. Anything pointing at a third-party service goes on the takeover
list (see `10-hunt-subdomain-takeover.md`).

---

## Step 3 — Probe (30 min)

```bash
httpx -l resolved.txt -silent -sc -title -td -cl -location -server \
      -threads 20 -rate-limit 30 -json -o alive.json
```

`-td` is required; the tech decides the next pass.

---

## Step 4 — Bucket (30 min)

Build the table from `03-recon.md`:

| bucket | hosts |
|---|---|
| unauth admin panels | … |
| stage/dev/test | … |
| API/docs | … |
| login/SSO | … |
| file hosts | … |
| everything else | … |

Rank by expected ceiling.

---

## Step 5 — Quick wins on the top bucket (30 min)

For each host in the top bucket, three requests:

```bash
curl -s -D- "https://host/" -o /dev/null
curl -s -D- "https://host/robots.txt" -o /dev/null
curl -s -D- "https://host/.well-known/security.txt" -o /dev/null
```

Any 200 with an admin login or a debug page is a candidate. Note it; do not dig
in yet.

---

## Step 6 — Exposure sweep (15 min)

```bash
python tools/exposure.py alive.json -o exposures.json
python tools/unauth_json.py alive.json -o collections.json
python tools/secrets.py alive.json -o secrets.json
```

Read the hits. Most are false positives (HTML error pages). One real `.env` or
JSON collection is a finding.

---

## Step 7 — Write the pass

Update `engagements/<program>/notes.md`:

```
recon pass <date>
domains: N   names: N   resolved: N   alive: N
buckets: ...
hits: ...
next: <one host, one class>
```

---

## Definition of done

- [ ] `subs.json`, `alive.json` exist.
- [ ] `buckets.md` ranked.
- [ ] Exposure/secret/collection results read.
- [ ] One host chosen for deep dive.
- [ ] Notes updated.

Recon is done when you have a target, not when you have a list.
