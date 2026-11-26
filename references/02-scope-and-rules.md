# 02 — Scope and rules

Scope is the only thing standing between a valid finding and a legal problem.
Treat it as a contract you must be able to quote line by line.

## Parse the scope properly

A program scope list is a mix of asset types. Each behaves differently.

| Asset form | Means | Does not mean |
|---|---|---|
| `example.com` | The exact host | Subdomains |
| `*.example.com` | All subdomains | The apex `example.com` |
| `*.example.com` + `example.com` | Both | Other registrable domains |
| `https://app.example.com/api/*` | Path-prefixed API | The whole host |
| `com.example.app` (Android) | The store app | Its backend |
| `123.0.0.0/24` | The range | Adjacent ranges |
| `github.com/org/repo` | Source review | Deployed infra |
| "All assets owned by X" | Ambiguous — ask | Everything with the brand name |

A host that resolves to a third-party provider (`*.zendesk.com`,
`*.herokuapp.com`, `*.cloudfront.net`) is third-party infrastructure. The
customer's *configuration* on it may be in scope; the platform is not. State
this explicitly in the report and let the triager decide.

## Normalize scope before you hunt

```bash
python tools/scope.py --platform intigriti --program <handle> -o scope.json
python tools/scope.py --platform hackerone --handle <handle> -o scope.json
python tools/scope.py --file scope.txt --format text -o scope.json
```

The tool writes:

```json
{
  "program": "...",
  "platform": "...",
  "wildcards": ["*.example.com"],
  "hosts": ["app.example.com"],
  "urls": ["https://api.example.com/v1/*"],
  "mobile": ["com.example.app"],
  "ips": ["203.0.113.0/24"],
  "excluded": ["status.example.com"],
  "rules_notes": ["no automated scanning", "test accounts allowed"]
}
```

Everything you later touch must appear in that file. If a host is not in it, it
does not exist for you.

## Reading rules for the four things that bite

1. **Automated tooling.** Many programs forbid scanners. "No automated
   scanning" usually means no *indiscriminate* scanning; targeted requests are
   normally fine. When in doubt, ask the program in writing and keep the reply.
2. **Rate limits.** Written limits are hard. Unwritten limits: assume 5 req/s
   and 2 concurrent per host.
3. **Test accounts.** If the program requires them, you must not use real user
   accounts. If it does not forbid them, still create your own.
4. **Data handling.** If you find PII, most programs require you to stop, report,
   and delete. Some require encryption of evidence. Read the rule.

## Exclusions that kill findings

These appear in most exclusion lists. Check before you write:

- Self-XSS without a demonstrable chain.
- Missing security headers (CSP, HSTS, X-Frame-Options) on their own.
- Clickjacking on pages with no sensitive action.
- Open redirect without a proven impact.
- Rate limiting absence without a demonstrated attack.
- Email spoofing / SPF / DMARC / DKIM.
- Username or email enumeration with no sensitive data.
- Software version disclosure with no working exploit.
- CSV injection in exports you generated.
- Automated scanner output with no exploitation.
- "Best practice" findings.
- Denial of service, including resource exhaustion.
- Reports about *your own* account only.

Some programs also exclude **all** XSS, or all reports below a severity floor.
A perfect Medium that the program does not pay for is worth zero hours.

## The three questions before every request

1. Is this exact host/path in scope?
2. Does this action violate a written rule?
3. If this breaks something, can I explain why it was necessary?

If any answer is uncomfortable, do not send it.

## Recording scope

Save the raw program page HTML and the parsed JSON in the engagement folder:

```
engagements/<program>/
  scope.raw.html
  scope.json
  rules.md        # your own summary of the rules, with quotes
```

`rules.md` with direct quotes is your defence if a triager later claims you
broke a rule. Write it once, at the start.

## Wildcard expansion

For `*.example.com`, subdomain enumeration is in scope by definition. For
`*.example.com` where the program also excludes `internal.example.com`, the
enumeration is still fine; *touching* the excluded host is not.

Wildcard enumeration itself is a passive activity. It does not touch the target
until you resolve or probe. Keep passive enumeration separate from active
probing so you can stop cleanly at the scope boundary.

## When scope is genuinely ambiguous

Ask. Public program pages have a contact channel; private programs have a
message thread. A one-line question costs a day and saves a ban:

> "Is `api.partner.example.com` covered by `*.example.com`, or is partner
> infrastructure out of scope?"

Write the answer into `rules.md`.
