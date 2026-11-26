# Checklist — File upload and handling

## Upload

- [ ] Extension allowlist probed (`.php`, `.phtml`, `.jsp`, `.aspx`, `.svg`, `.html`, `.htaccess`).
- [ ] Content-Type confusion (`image/png` + PHP body).
- [ ] Magic bytes bypass (`GIF89a;<?php`).
- [ ] Double extension (`shell.php.jpg`, `shell.jpg.php`).
- [ ] Trailing chars (`%00`, `.`, space, `::$DATA`).
- [ ] Filename traversal (`../../`).
- [ ] SVG with `<script>`/`onload` tested.
- [ ] HTML upload served same-origin.
- [ ] Zip-slip (`../` in entries).
- [ ] Upload dir served by the app (executable?).
- [ ] Stored shell deleted after proof; marker output only.

## File read

- [ ] `../../../../etc/passwd` and encoded variants.
- [ ] Absolute path (`/etc/passwd`).
- [ ] Windows (`..\..\windows\win.ini`).
- [ ] `file://` if param is a URL.
- [ ] Double decode, `....//`.
- [ ] One real file read proves impact; stopped there.

## File write / delete

- [ ] Write a harmless marker file, then delete it.
- [ ] Overwrite tested on a controlled path only.
- [ ] Symlink attack noted only if safe.

## Storage

- [ ] Bucket list/ACL checked (S3/GCS/Azure).
- [ ] Data proven to belong to the company.
- [ ] Data proven sensitive (not marketing assets).

## Evidence

- [ ] Request + response for the file read/exec.
- [ ] First line of the file (redacted) or `echo` output.
- [ ] Cleanup confirmed (file deleted, shell removed).

## Severity

- [ ] `/etc/passwd` → Medium–High.
- [ ] Config/credentials → High.
- [ ] Upload RCE → Critical.
- [ ] Public bucket with customer data → High–Critical.

## Verdict

- [ ] Works / Closed / Inconclusive written.
