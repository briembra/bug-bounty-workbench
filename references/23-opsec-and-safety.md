# 23 — OpSec and safety

Bug bounty is authorized access within a boundary. OpSec is how you stay inside
it, keep your accounts, and avoid accidentally becoming the incident.

---

## The identity boundary

- Use **one** researcher identity per platform. Do not sybil.
- Use **program-provided test accounts** if the program supplies them.
- If you must register, use a dedicated address (`you+bb@yourdomain`) and a
  unique password per program. Never reuse a personal password.
- Never test with a real customer's account, a colleague's account, or a
  friend's account.
- Never use leaked credentials — not even "just to check." That is unauthorized
  access, full stop.

---

## Request hygiene

| Rule | Why |
|---|---|
| ≤5 req/s, ≤2 concurrent per host | Avoid bans and accidental load |
| Exponential backoff on 429/503 | Respect the service |
| Stop on blanket 403 | You are fingerprinted |
| One proof request per finding, not a loop | Minimum necessary |
| No `--dump`, no `--all`, no full enumeration | Data minimization |
| Unique marker in every test object | Cleanup and attribution |

---

## Data handling

If you encounter real personal data:

1. **Stop enumerating.** One record is enough.
2. **Capture the minimum.** Field names, one redacted value.
3. **Do not store the dataset.** Delete raw dumps after extracting the proof.
4. **Do not share it.** Not with friends, not in a public report.
5. **Tell the program** in the report that you saw N records and stopped.

GDPR and equivalent regimes treat unnecessary retention as a breach. You do not
want to be the researcher who caused one.

---

## Evidence storage

- Keep evidence on an encrypted disk.
- Never commit real target data to a public repo. `.gitignore` your `findings/`
  and `out/`.
- Redact tokens and PII at capture time, not at report time.
- Delete evidence after the program closes the report and the disclosure window
  ends, unless you need it for a dispute.

---

## Out-of-band listeners

- `interactsh` / Burp Collaborator for blind SSRF/XSS/XXE.
- Use a **dedicated** listener per engagement so hits are unambiguous.
- Do not point a listener at a third party; it only receives what the target
  sends.
- Log the source IP and User-Agent of every hit — it is evidence.

---

## Social boundaries

- Never social-engineer employees, support, or other users.
- Never call, email, or message a real person as part of a test.
- Never send a password-reset or verification email to an address you do not
  control.
- Never test a third-party service the program does not own.
- Never access physical premises.

If a bug needs one of those, it is out of bounds — report the technical gap
instead.

---

## Legal frame (know it, do not lecture with it)

Authorization comes from the program's published policy. Common frameworks:

- **US:** CFAA; safe harbor usually granted by the program's policy text.
- **UK:** Computer Misuse Act 1990.
- **EU/NL:** Wetboek van Strafrecht art. 138ab; GDPR for data.
- **Safe harbor:** most large programs publish one; read it, keep a copy.

Authorization is **scope-specific**. A safe harbor for `*.example.com` does not
cover `example.org`, a subsidiary, or an acquired company's domain.

---

## The three things that get researchers banned

1. **Load.** A scan that takes a service down. Never.
2. **Real data.** Enumerating customer records. Stop at one.
3. **Social engineering.** Contacting people.

Everything else is craft. Those three are the line.

---

## If you break something

1. **Stop immediately.**
2. **Tell the program** through the report channel or their security contact.
   Honesty is usually forgiven; hiding is not.
3. **Do not try to fix it** unless asked.
4. **Preserve the evidence** of what happened.

A fast, honest disclosure of an accident has ended far fewer careers than a
quiet cover-up.

---

## Account hygiene

- 2FA on every platform account.
- Unique password per program.
- Do not share API tokens (Intigriti, HackerOne) in screenshots.
- Log out of test accounts when done.
- Delete test objects you created, where the app allows.

---

## The opsec checklist before each engagement

- [ ] Scope saved, rules saved, quoted.
- [ ] Request budget set (count and rate).
- [ ] Listener ready and unique.
- [ ] Two test accounts ready (or a plan if registration is blocked).
- [ ] `findings/` folder created and gitignored.
- [ ] Marker string chosen (`bbtest-<date>-<rand>`).
- [ ] Time box set.

If any box is unchecked, fix it before the first request.
