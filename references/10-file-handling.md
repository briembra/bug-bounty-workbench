# 10 — File handling

Upload, download, import, export, preview, archive, share. File handling classes
are high-yield because the server touches the filesystem and the network on
behalf of user input — two powerful primitives.

---

## Upload: the checklist

Test each independently. A failure in any one row can be High.

- [ ] **Extension allowlist.** `.php`, `.phtml`, `.php5`, `.jsp`, `.jspx`,
      `.asp`, `.aspx`, `.svg`, `.html`, `.htm`, `.js`, `.htaccess`, `.config`,
      `.shtml`, `.cgi`.
- [ ] **Content-Type confusion.** `image/png` header with `<?php` body. Server
      trusts the header, not the bytes.
- [ ] **Magic bytes.** `GIF89a;<?php …` passes an image check and executes on
      some stacks.
- [ ] **Double extension.** `shell.php.jpg`, `shell.jpg.php`, `shell.pHp`.
- [ ] **Trailing characters.** `shell.php%00.jpg`, `shell.php.`, `shell.php `,
      `shell.php::$DATA` (Windows ADS).
- [ ] **Filename traversal.** `../../var/www/shell.php` as the filename.
- [ ] **SVG.** SVG is XML and runs JS. `<svg onload=alert(1)>` uploaded and served
      same-origin = stored XSS.
- [ ] **HTML.** An uploaded `.html` served from the app origin = XSS/phishing on
      your domain.
- [ ] **Zip.** Zip-slip (`../../` in entry names), zip bombs (skip DoS but note
      structure), symlinks in the archive.
- [ ] **Where it lands.** Same origin? A CDN with a different origin (safe)? An
      S3 bucket with public read?
- [ ] **Executable path.** Is the upload dir served by PHP/ASP? Is
      `/uploads/shell.php` reachable?

### Proving code execution

Do **not** upload a web shell and leave it. Prove minimally:

```
<?php echo "BBH".(7*7); ?>
```

If the response is `BBH49`, you have code execution. Delete the file if you can,
and report. Never upload a full interactive shell to production.

---

## Path traversal / arbitrary file read

The classic HIGH when it returns real files.

```
GET /download?file=../../../../etc/passwd
GET /download?file=..%2f..%2f..%2fetc%2fpasswd
GET /download?file=....//....//etc/passwd
GET /download?file=..%252f..%252fetc%252fpasswd
GET /download?file=/etc/passwd          (absolute)
GET /download?file=file:///etc/passwd   (if the param is a URL)
```

Windows:

```
..\..\..\windows\win.ini
..%5c..%5cwindows%5cwin.ini
C:\windows\win.ini
\\?\C:\windows\win.ini
```

Confirm with a real file whose content you recognise. `root:x:0:0` or
`[extensions]` in `win.ini`. An empty 200 is not proof.

### Reachable targets that matter

- `/etc/passwd` — proof of read (not sensitive but unambiguous).
- App config: `.env`, `config.php`, `settings.py`, `appsettings.json`,
  `web.config` — credentials.
- SSH keys: `~/.ssh/id_rsa` — Critical.
- Cloud creds: `~/.aws/credentials`, `~/.config/gcloud/…` — Critical.
- Source: `/proc/self/cmdline`, `proc/self/environ` — env secrets.
- Windows: `C:\Windows\System32\drivers\etc\hosts`, `win.ini`.

Read `passwd` first, then one config file, and stop. Do not enumerate the disk.

---

## Arbitrary file write / delete

Where: "rename", "move", "export to", "save as", backup restore, avatar path.

- Write a `.php` into a webroot → RCE.
- Overwrite `authorized_keys` → Critical.
- Delete a file by path → data loss (do not do this on real users' files).
- Symlink attack: upload a symlink to `/etc/passwd`, then download it.

Prove write with a harmless file (`bbh-test.txt`) in a directory you control, and
delete it.

---

## SSRF via file import

"Import from URL" is both file handling and SSRF. See `08-ssrf.md`. A file
import that fetches an internal URL is the same bug for reporting purposes.

---

## XXE via file parse

DOCX, XLSX, PPTX, SVG, RSS, SOAP, SAML. See `07-injection.md`. A file parser that
resolves external entities reads local files or hits your listener.

---

## Zip-slip

```
archive.zip
  ../../../../var/www/html/shell.php
```

If the extractor does not normalise entry names, the file lands outside the
intended directory. Prove by extracting to a known writable path you can then
read.

---

## Content-Disposition and header injection

A filename reflected into `Content-Disposition` without encoding:

```
filename="x";%0d%0aSet-Cookie:admin=1
```

Rare to be exploitable now; note only if it lands in a header you can read.

---

## Storage misconfiguration (S3/GCS/Azure)

- Public list: `GET https://bucket.s3.amazonaws.com/?list-type=2` returns XML of
  keys.
- Public object: a known key is readable without a signature.
- ACL: `?acl` shows grantees; `AllUsers` = world.
- Azure blob: `?restype=container&comp=list`; check container access level.
- GCS: `https://storage.googleapis.com/bucket/` lists if public.

A bucket with customer data public is High. A bucket with only static assets
public is by design — check what is inside before reporting.

**Ownership check.** A bucket named `company-backup` may belong to the company or
to a squatter. Verify it holds their data (their domain in the objects, their
brand assets) before claiming it.

---

## Export and report generation

"Download my data" and "export CSV" endpoints:

- IDOR on the export id → another user's export.
- Injection into the CSV (formula) — usually excluded.
- IDOR on the *file* produced → `/exports/1042.csv`.
- SSRF if the export pulls from a URL.
- Template injection if the export renders a template.

---

## Severity

| What you showed | Severity |
|---|---|
| Read `/etc/passwd` only | Medium–High |
| Read app config with secrets | High |
| Read cloud credentials | Critical |
| Upload executes code | Critical |
| Upload SVG/HTML same-origin | Medium–High |
| Zip-slip write | High |
| Public bucket with customer data | High–Critical |
| Public bucket with static assets | Info |

---

## Evidence hygiene for file bugs

- Read one file, show the first line, redact secrets.
- Delete any file you uploaded, or tell the program where it is.
- Do not download customer files; if a listing shows them, capture one key name
  and stop.
- Never execute a reverse shell against production. `echo 7*7` is enough.
