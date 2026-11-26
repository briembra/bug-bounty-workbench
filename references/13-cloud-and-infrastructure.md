# 13 — Cloud and infrastructure

Cloud bugs are where "the customer's configuration" becomes the company's
problem. Hunt this class when you see S3/GCS/Azure hosts, Firebase apps, Kubernetes
dashboards, CI runners, serverless functions, or a company that clearly built on
cloud primitives.

**Scope reminder:** a shared cloud *platform* (S3 itself, Cloudflare itself) is
out of scope. The customer's *bucket*, *tenant*, *project*, *function*, *repo* is
in scope if the program says so. Read the scope.

---

## Object storage

### S3

```bash
# bucket listing
curl -s "https://BUCKET.s3.amazonaws.com/?list-type=2"
curl -s "https://BUCKET.s3.amazonaws.com/?acl"
curl -s "https://s3.amazonaws.com/BUCKET?list-type=2"
# regional endpoints
curl -s "https://BUCKET.s3.eu-west-1.amazonaws.com/?list-type=2"
```

Signals:

- `ListBucketResult` with `<Key>` entries → public list.
- `<Grantee>…AllUsers</Grantee>` with `READ` → world ACL.
- A 403 with `AccessDenied` means exists-but-private — a candidate for a name
  squat, not a leak.
- `NoSuchBucket` means the name is free — takeover candidate (see
  `17-subdomain-takeover.md`).

### GCS

```bash
curl -s "https://storage.googleapis.com/BUCKET/"
curl -s "https://storage.googleapis.com/storage/v1/b/BUCKET/o"
```

`allUsers` / `allAuthenticatedUsers` in IAM = public.

### Azure Blob

```bash
curl -s "https://ACCOUNT.blob.core.windows.net/CONTAINER?restype=container&comp=list"
```

A 200 with `<Blob>` entries = public container. Check `Public Access Level` on the
account.

### Bucket name discovery

Bucket names are not always in DNS. Sources:

- JS bundles (`https://myapp-assets.s3.amazonaws.com`).
- Error pages with full URLs.
- Subdomain CNAMEs (`assets.example.com → example-assets.s3.amazonaws.com`).
- Certificate SANs.
- Mobile app strings.
- Public repos / readme / docs.

**Before reporting:** prove the data is the company's (their domain in object
metadata, their brand, their customer emails), and prove it is sensitive (not
public marketing assets). A public bucket of product images is by design.

---

## Firebase (very common, very often misconfigured)

Firebase Realtime Database and Firestore with public read rules leak entire
collections.

```bash
# Realtime DB
curl -s "https://PROJECT.firebaseio.com/.json"
curl -s "https://PROJECT-default-rtdb.firebaseio.com/.json"
curl -s "https://PROJECT.firebaseio.com/users.json?shallow=true"

# Firestore (REST)
curl -s "https://firestore.googleapis.com/v1/projects/PROJECT/databases/(default)/documents/users"
```

Signals: JSON with user data; `{"error":"Permission denied"}` = locked.

Project id discovery: JS bundles (`firebaseConfig` object in the app),
`*.firebaseapp.com`, `*.web.app`, the mobile app.

**Rate limit:** Firebase throttles rapid requests (~429). Space requests 2+ s
apart, and do not enumerate collections at scale — one collection, one record,
redacted.

Firebase auth with `ALLOW_READ` on user profiles is High. A public config object
(apiKey, projectId) is **not a secret** — Firebase client keys are public by
design. Do not report them.

---

## Kubernetes / container orchestration

- **Kubelet:** `https://HOST:10250/pods` — unauthenticated kubelet returns pod
  list and can exec. Critical.
- **Dashboard:** `https://HOST/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/`
  — unauth dashboard. Critical.
- **API server:** `https://HOST:6443/version` — exposed API server; `anonymous-auth`
  enabled → list secrets.
- **etcd:** `https://HOST:2379/v2/keys` — unauth etcd holds all secrets. Critical.
- **Docker API:** `http://HOST:2375/containers/json` — unauth Docker = host takeover.

These are rare but when present they are Critical. Scan only in-scope hosts, one
port at a time, and stop at the first confirmation.

---

## Serverless and managed functions

- **AWS Lambda URL:** public function URL → invoke without auth; check the
  response for data.
- **Cloud Functions:** `https://REGION-PROJECT.cloudfunctions.net/NAME` — test
  unauthenticated.
- **Azure Functions:** `https://APP.azurewebsites.net/api/NAME?code=` — key in the
  URL is often leaked in JS.
- **API Gateway:** stage endpoints (`/prod`, `/dev`, `/stage`) — the `/dev` stage
  is often unauthenticated.

---

## CI/CD

- **Jenkins:** `/script` (Groovy RCE), `/computer/(master)/script`, `/api/json`
  (job list), `/credentials` — unauth Jenkins is Critical.
- **GitLab:** `/explore`, `/api/v4/projects`, public snippets with secrets.
- **GitHub Actions:** look for `pull_request_target` + checkout of untrusted code
  in *public* repos; a leaked `GITHUB_TOKEN` in logs.
- **Drone/Argo/Tekton:** `/api/v1/...` without auth.
- **Artifactory/Nexus:** anonymous read of internal packages, config files.

A Jenkins `/script` that runs `println "id".execute().text` is Critical. Prove
with a harmless command.

---

## Metadata and IAM (the SSRF endgame)

Covered in `08-ssrf.md`. The cloud-specific piece:

- AWS role credentials → enumerate what the role can do with `--dry-run` only
  (`aws sts get-caller-identity`), never mutate.
- GCP service account token → `gcloud auth` — do not use, just report scope.
- Azure managed identity token → decode the JWT to show the role.

Report the *identity and permissions*, not the keys. Redact the secret.

---

## CloudFront / CDN cache

- Cache poisoning and deception are their own class — see
  `16-caching-and-protocol.md`.
- A CDN origin exposed directly (bypassing the WAF) is an origin-IP leak; often
  Low, sometimes High if the origin has weaker auth.

---

## Exposure sweep (bounded)

`tools/exposure.py` checks a fixed list of high-signal paths on alive hosts:

```
.env  .git/config  .git/HEAD  .svn/  .DS_Store
config.php.bak  wp-config.php.bak  .aws/credentials
actuator/env  actuator/heapdump  actuator/mappings
server-status  phpinfo.php  info.php
backup.zip  db.sql  dump.sql  .sql
docker-compose.yml  .dockercfg  .npmrc
```

It is bounded (one request per path per host, capped hosts), reports what it found
and what it skipped, and never writes.

---

## Severity

| What you showed | Severity |
|---|---|
| Public bucket with customer PII | High–Critical |
| Public bucket with internal backups | Critical |
| Firebase public read of users | High |
| Unauth Jenkins `/script` | Critical |
| Unauth etcd / kubelet / Docker API | Critical |
| Unauth dashboard with cluster admin | Critical |
| Public Lambda URL returning data | Medium–High |
| Public bucket with marketing assets | Info (not a bug) |
| Firebase client apiKey in JS | Info (not a secret) |

---

## What closed looks like

- Bucket returns `AccessDenied` for list and object → closed.
- Firestore returns `PERMISSION_DENIED` → closed.
- Kubelet returns 401/403 → closed.
- Jenkins requires login → closed (but check for known CVEs on the version).
- Lambda URL returns 403 without auth → closed.

Say it, move on. Cloud surface is wide; do not linger on a locked door.
