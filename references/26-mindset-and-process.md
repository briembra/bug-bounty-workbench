# 26 — Mindset and process

This is the document about how to work, not what to test. It is the difference
between a hunter who finds one bug a year and one who finds them steadily.

---

## Depth beats breadth

The temptation is to run every tool on every host. That produces a thousand
alive hosts and zero findings. The hunter who finds bugs picks **one** app and
understands it:

- What are the objects?
- What are the roles?
- What does the server trust from the client?
- What is the money flow?
- What changed recently?

Ten requests that understand one app beat ten thousand that understand none.

---

## The 80/20 of bug bounty

| Activity | Share of findings |
|---|---|
| Authorization (BOLA/BFLA) | ~30% |
| Auth/session | ~20% |
| Business logic | ~15% |
| SSRF/injection | ~15% |
| Everything else | ~20% |

Spend your time proportionally. If you have spent an hour on missing headers, you
have spent an hour wrong.

---

## The session shape

A good hunting session:

1. **10 min** — re-read scope, pick one asset, open notes.
2. **20 min** — map: routes, roles, objects, JS, API docs.
3. **60 min** — break: test the top five ceiling classes.
4. **20 min** — prove: two accounts, capture evidence.
5. **10 min** — write or park.

Two hours, one asset, one deep pass. Not six hours of scanning.

---

## When you are stuck

Run the list. One of these moves you:

- Re-read the app as three roles: anonymous, user, admin. What changes?
- Diff two accounts on the same request. The server's answer is the bug.
- Look at what the frontend *stops* you from doing. Remove the stop.
- Follow the money: cart, discount, refund, payout, credits.
- Follow the identity: signup, invite, reset, email change, SSO link.
- Follow the file: upload, import, export, preview, share.
- Follow the integration: webhook, OAuth app, API key, chatbot tool.
- Read the changelog and the mobile app. New features ship unhardened.
- Ask: what does the server trust that the client controls?
- Look at the *child* of an object you already tested.
- Look at the *export* of a list you already tested.
- Look at the *old API version* of an endpoint that is hardened now.

If none moves you, change asset, not class. A new host is a new map.

---

## Signal over noise

Every hour, ask: **did the last hour produce a hypothesis I can test, or just
more data?** If data, stop collecting and start testing.

The signals worth following:

- A 401 that becomes 200 with one header changed.
- A response that contains an id you did not send.
- A field in a response the UI never shows.
- An endpoint in the mobile app the web app does not call.
- A parameter the server accepts but the UI removed.
- A version string that matches a known CVE.
- A stage/test host with debug on.

Everything else is inventory.

---

## Failure modes to notice in yourself

| Failure | Fix |
|---|---|
| Endless recon | Set a request budget and a time box |
| Tool worship | Tools find surface; you find bugs |
| Chasing Low XSS | Move to BOLA/logic |
| Reporting a 200 as exposure | Show the data |
| Calling a leak a breach | Check demo data first |
| Arguing with triage | One calm reply, then move |
| Fear of "already found" | Dedup check, then submit anyway |
| Skipping the second account | Two accounts, always |
| Not writing as you go | Evidence file per step |

---

## The evidence habit

Write the request and response to disk **the moment you see it**. Memory lies
after three hours. A finding you cannot reproduce is not a finding; a finding you
did not save is a lesson you will repeat.

---

## Patience and honesty

- Most sessions produce nothing. That is normal. The map you built is the asset.
- A "closed" result is a real result. Write it and move on; do not circle.
- A rejected report is data. Read the reason, adjust, continue.
- Never inflate to feel productive. Inflation is the fastest way to lose standing.

---

## The long game

Reputation compounds:

- Accurate reports → faster triage → better programs → more surface.
- Disclosed reports → other hunters read them → you learn from theirs.
- Relationships with triagers → benefit of the doubt on edge cases.

The hunter who is right and calm beats the hunter who is loud and wrong.

---

## The one-sentence process

**Pick one asset, map it honestly, test what the server trusts, prove it with two
accounts, score it as it is, write it so a stranger can reproduce it in two
minutes, submit, then go one level deeper on the same asset.**

That is the whole method. Everything else in this repository is detail.
