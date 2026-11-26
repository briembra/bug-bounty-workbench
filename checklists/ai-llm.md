# Checklist — AI / LLM surfaces

## Surface

- [ ] Chat API identified (`/api/chat`, `/openapi.json`).
- [ ] `/api/config` checked (public? environment?).
- [ ] Admin/dashboard auth checked.
- [ ] Session binding / token checked.
- [ ] Third-party widget vs custom API distinguished.

## System prompt

- [ ] Prompt extraction attempted.
- [ ] Content classified (no secrets → Info).

## Knowledge base

- [ ] Source/corpus asked for ("which documents…").
- [ ] Internal framing used ("I'm on the support team…").
- [ ] One document extracted.
- [ ] Content classified: public / internal-no-PII / internal-with-PII / credentials.
- [ ] **Stopped at one document.**

## SSRF

- [ ] `page_url`/`context_url` pointed at listener.
- [ ] Hit → fetches (SSRF). No hit → stored only (**not SSRF**).
- [ ] Tool abuse tested ("call fetch_url with …").

## Cross-session

- [ ] Two sessions; asked session B about session A.
- [ ] Leakage noted or excluded.

## Exfiltration

- [ ] Markdown image rendering checked.
- [ ] Tested only with your own uploaded document.

## Evidence

- [ ] Exact prompts recorded.
- [ ] Extracted content (redacted) recorded.
- [ ] No real PII stored.

## Severity

- [ ] System prompt only → Info.
- [ ] Internal procedure, no PII → Medium 5.3.
- [ ] Internal doc with PII → High.
- [ ] Credentials → Critical.
- [ ] SSRF internal → High.

## Verdict

- [ ] Works / Closed / Inconclusive written.
