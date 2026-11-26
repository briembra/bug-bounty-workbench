# Checklist — Injection

## Inputs

- [ ] Numeric path ids tested.
- [ ] Sort/filter params tested.
- [ ] Search params tested.
- [ ] JSON string fields tested.
- [ ] GraphQL arguments tested.
- [ ] Hidden/unused params tested.

## SQL

- [ ] Quote error pattern (`'` breaks, `''` fixes).
- [ ] Boolean pair (`AND 1=1` vs `AND 1=2`) consistent over 3 tries.
- [ ] Time-based delay proportional and repeatable.
- [ ] Control param unaffected.
- [ ] Extraction: one row (`version()`, `user()`, `database()`).
- [ ] No `--dump`, no table enumeration.

## NoSQL

- [ ] `$ne`, `$gt`, `$regex` in JSON auth/query.
- [ ] Bracket syntax in query string.
- [ ] Array injection (`username[]=`).
- [ ] Login bypass if applicable.

## Other

- [ ] Command injection (`; | $() &&`) on file/convert/ping flows.
- [ ] SSTI (`{{7*7}}`, `${7*7}`, `#{7*7}`, `<%= 7*7 %>`).
- [ ] XXE on any XML/SOAP/SAML/SVG/DOCX endpoint.
- [ ] Deserialization magic bytes checked (`rO0AB`, `O:`, `!!java`).

## Evidence

- [ ] One request, one response, one extraction.
- [ ] Exact payload string recorded.
- [ ] Status + body slice captured.
- [ ] Impact stated (data read, command run).

## Negative evidence

- [ ] If blocked, the exact WAF/countermeasure recorded.
- [ ] "Closed" written with the reason.

## Verdict

- [ ] Works / Closed / Inconclusive written.
