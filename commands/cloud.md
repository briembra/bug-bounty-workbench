---
description: Hunt cloud and infrastructure exposure — buckets, metadata, managed services, CI/CD trust.
argument-hint: <host or org> [cloud]
allowed-tools: Bash, Read, Write, WebFetch
---

# /bbw-cloud

`references/13`, `checklists/cloud.md`.

**Input:** `$ARGUMENTS` — a host, a company name, or a cloud hint (aws/gcp/azure).

```
/bbw-cloud https://app.acme.com
/bbw-cloud acme aws
```

The bug is not "a bucket exists". It is **the program's data, readable, because of
their misconfiguration**.

---

## Step 1 — Find the cloud footprint

```bash
# where do they host?
curl -sD- https://<host>/ | grep -i -E 'server|x-amz|x-goog|x-azure|cf-ray|via'
# who serves their static assets?
grep -rEo 'https?://[a-z0-9.-]+\.(s3|s3-[a-z0-9-]+)\.amazonaws\.com[^"'"'"' ]*' *.js
grep -rEo 'https?://storage\.googleapis\.com/[^"'"'"' ]*' *.js
grep -rEo 'https?://[a-z0-9.-]+\.blob\.core\.windows\.net[^"'"'"' ]*' *.js
grep -rEo 'https?://[a-z0-9.-]+\.cloudfront\.net[^"'"'"' ]*' *.js
```

Also: `*.firebaseio.com`, `*.firebaseapp.com`, `*.herokuapp.com`,
`*.elasticbeanstalk.com`, `*.azurewebsites.net`, `*.cloudfunctions.net`.

## Step 2 — Test each bucket properly

```bash
# list
curl -s "https://BUCKET.s3.amazonaws.com/?list-type=2"
# ACL
curl -s "https://BUCKET.s3.amazonaws.com/?acl"
# per-object read
curl -sI "https://BUCKET.s3.amazonaws.com/some-key"
# GCS
curl -s "https://storage.googleapis.com/BUCKET/"
# Azure
curl -s "https://ACCOUNT.blob.core.windows.net/CONTAINER?restype=container&comp=list"
# Firebase
curl -s "https://PROJECT.firebaseio.com/.json"
```

| Result | Verdict |
|---|---|
| `ListBucketResult` with keys | public listing — continue |
| `AccessDenied` | private — closed |
| `AllAccessDisabled` | closed |
| `NoSuchBucket` | takeover candidate → `/bbw-takeover` |
| `200` on a known key | public read, record it |

## Step 3 — Prove the data is theirs and sensitive

Before writing a single word of the report:

- [ ] The bucket name or object metadata references the program's domain/brand
- [ ] The content is their product, not a marketing image set
- [ ] It contains something not meant to be public: PII, dumps, keys, source,
      invoices, backups, internal docs
- [ ] One redacted example, not a dump

A public bucket of logos is by design. A backup of `customers.sql.gz` is Critical.

## Step 4 — Metadata and SSRF-adjacent

If you already have SSRF (`/bbw-ssrf`), escalate to metadata here. Without SSRF, check
whether an app endpoint proxies cloud storage:

```
https://<host>/proxy?url=https://169.254.169.254/latest/meta-data/
https://<host>/media?bucket=other-tenant
https://<host>/files?path=../other-bucket/key
```

Cross-tenant bucket access through the app = High.

## Step 5 — CI/CD and deployment trust

- Public repo with secrets in Actions/GitLab CI logs
- `pull_request_target` workflows that run fork code with secrets
- Open registration on a self-hosted runner
- Deploy keys or tokens in a public build artefact
- `docker-compose.yml` with credentials in a public repo

These are `/bbw-secrets` finding material — record and hand off.

## Step 6 — Firebase and serverless

For Firebase: `.json` on the root when rules allow read is a full DB dump. Check
`auth` rules, not just data:

```bash
curl -s "https://PROJECT.firebaseio.com/users.json?shallow=true" | head -20
```

If it returns a key list, stop after the count and one redacted record. Firestore
and RTDB both need a read/write test, not a brute force.

---

## Output shape

```
buckets found: N   public: N   sensitive: N
cloud: <provider>
worst: <resource> — <what is inside>
evidence: findings/<slug>/
severity: <band>
next: /bbw-score then /bbw-report
```

## Stop conditions

- Everything `AccessDenied` → "closed", move on.
- Real customer data at scale → one redacted object, stop, report.
- Credentials found → do not use them; name the role, redact, stop.
- A bucket belongs to a third party (not the program) → out of scope, note only.
