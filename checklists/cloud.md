# Checklist — Cloud and infrastructure

## Scope check

- [ ] Asset is the customer's tenant/bucket/project, not the shared platform.
- [ ] Scope line quoted for the cloud asset.

## Storage

- [ ] S3 list/ACL (`?list-type=2`, `?acl`).
- [ ] GCS list (`storage.googleapis.com/BUCKET/`).
- [ ] Azure blob list (`?restype=container&comp=list`).
- [ ] Data proven to belong to the company.
- [ ] Data proven sensitive.

## Firebase

- [ ] Realtime DB `.json` read.
- [ ] Firestore REST read.
- [ ] Project id found in JS/mobile.
- [ ] Requests spaced ≥2 s (throttle).
- [ ] Client `apiKey` recognised as public (not reported).

## Orchestration

- [ ] Kubelet `:10250/pods`.
- [ ] K8s dashboard unauth.
- [ ] API server `:6443/version`.
- [ ] etcd `:2379`.
- [ ] Docker API `:2375`.
- [ ] Stopped at first confirmation; no exploitation beyond proof.

## Functions

- [ ] Lambda function URL unauth.
- [ ] Cloud Functions unauth.
- [ ] Azure Functions `?code=` leaked.
- [ ] API Gateway `/dev` stage unauth.

## CI/CD

- [ ] Jenkins `/script`, `/api/json`, `/credentials`.
- [ ] GitLab `/explore`, `/api/v4/projects`.
- [ ] Artifactory/Nexus anonymous read.
- [ ] Proof command harmless (`id`, no mutation).

## Sweep

- [ ] `tools/exposure.py` run, hits read.
- [ ] `.env`, `.git`, `actuator`, backups checked.

## Evidence

- [ ] Response with the data or the unauth page.
- [ ] No mutation performed.
- [ ] Redaction done.

## Severity

- [ ] Customer PII public → High–Critical.
- [ ] Unauth admin/CI → Critical.
- [ ] Marketing assets public → Info.

## Verdict

- [ ] Works / Closed / Inconclusive written.
