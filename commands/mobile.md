---
description: Hunt mobile and thick-client apps — API keys, endpoint extraction, certificate pinning, deep links, insecure storage.
argument-hint: <app name | ipa/apk path | mobile api host>
allowed-tools: Bash, Read, Write, WebFetch
---

# /bbw-mobile

`references/18`.

**Input:** `$ARGUMENTS` — app name, a local `.apk`/`.ipa`, or the API host the app
talks to.

```
/bbw-mobile com.acme.app
/bbw-mobile ~/Downloads/acme.apk
/bbw-mobile api.acme.com
```

The mobile app is usually the **weakest client**: older API version, debug flags,
hardcoded keys, no certificate pinning on the staging build.

---

## Step 1 — Get the binary

```bash
# Android
apkeep -a com.acme.app -d /tmp          # or: adb shell pm path com.acme.app
apktool d acme.apk -o acme-apk
jadx -d acme-jadx acme.apk               # better decompilation than jadx-gui for grepping
# iOS
# download from the App Store on a device you own, then:
unzip -o acme.ipa -d acme-ipa
otool -L acme-ipa/Payload/Acme.app/Acme
```

If you cannot obtain the binary, work from the network side: `/bbw-surface` on the
mobile API host.

## Step 2 — Grep for the good stuff

```bash
grep -rEi 'api[_-]?key|secret|token|password|bearer' acme-jadx/sources | head -50
grep -rEo 'https?://[a-zA-Z0-9.-]+' acme-apk/res/values/strings.xml | sort -u
grep -rEi 'firebase|google_api_key|maps_key|stripe|sentry_dsn' acme-apk
grep -rEi 'debuggable|allowBackup|usesCleartextTraffic' acme-apk/AndroidManifest.xml
```

Also check `res/values/strings.xml`, `assets/`, `google-services.json`,
`GoogleService-Info.plist`.

## Step 3 — Endpoint inventory → hand off

Pull every base URL and path, then test the **mobile** API, not the web one:

```bash
grep -rhoE '"/[a-z0-9/_{}-]+"' acme-jadx/sources | sort -u > mobile-paths.txt
grep -rhoE 'https?://[a-z0-9.-]+/[a-z0-9/_{}-]*' acme-jadx/sources | sort -u
```

Mobile APIs are commonly `/mobile/v1/`, `/app/`, `/rpc/`, with weaker auth checks.
Run `/bbw-api` and `/bbw-idor` against them.

## Step 4 — Storage and transport

| Check | How | Bug if |
|---|---|---|
| Cleartext | `usesCleartextTraffic=true`, `NSAllowsArbitraryLoads` | HTTP allowed in prod |
| Backup | `android:allowBackup="true"` | tokens/DB readable via adb backup |
| Debuggable | `android:debuggable="true"` | `run-as` shell access |
| Pinning | config present but not enforced | MITM possible |
| Keychain | tokens in `SharedPreferences` plaintext | read on rooted device |
| Logs | `Log.d` with tokens | leak via logcat / crash reports |
| WebView | `setJavaScriptEnabled(true)` + `addJavascriptInterface` | JS bridge → RCE-ish |

## Step 5 — Deep links

```bash
# from the manifest
grep -A 20 'intent-filter' acme-apk/AndroidManifest.xml
# universal links
grep -A 30 'applinks' acme-ipa/Payload/Acme.app/Info.plist
```

Test:

```bash
adb shell am start -W -a android.intent.action.VIEW -d "acme://reset?token=bbtest"
adb shell am start -W -a android.intent.action.VIEW -d "https://acme.com/open?next=https://evil.com"
```

A deep link that takes a URL or token without validation → open redirect, token
leak, or auth bypass inside the app. Record what it does.

## Step 6 — Runtime (if you have a test device)

```bash
# proxy traffic
mitmproxy -p 8080     # then set the device proxy
# bypass pinning safely on your own device
objection -g com.acme.app explore -s "android sslpinning disable"
# storage
adb shell run-as com.acme.app ls -la shared_prefs/
```

Only on your device, with your accounts.

## Step 7 — What to report

- Hardcoded server secret → same standard as `/bbw-secrets`
- Mobile API IDOR → same standard as `/bbw-idor`
- Debuggable prod build → Low–Medium depending on data reachable
- Deep link auth bypass → High
- No certificate pinning alone → **not** a finding, note only

---

## Output shape

```
app: <name>   platform: android | ios
endpoints: N   keys found: N (live: N)
storage issues: <list>   deep links: N
worst: <issue> — <what it allows>
next: /bbw-idor or /bbw-secrets or /bbw-score
```

## Stop conditions

- Jailbreak-only impact → usually out of scope, note it.
- Pinning bypass alone → not a bug, do not report.
- Needs a rooted device to be "exploitable" → Low at best.
- Never attack real users' devices; your own test device only.
