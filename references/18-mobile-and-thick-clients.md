# 18 — Mobile and thick clients

Mobile apps and desktop clients ship the same backend as the web app, plus
secrets, endpoints, and sometimes a weaker auth model. They are the fastest way
to find an API the web app hides.

---

## Getting the artifact

### Android

```bash
# from the Play Store (needs a device or an APK mirror)
adb shell pm list packages | grep <vendor>
adb shell pm path com.vendor.app
adb pull /data/app/.../base.apk

# split APKs: pull all, merge with APKEditor
apkeditor m -i base.apk -o merged.apk
```

### iOS

- Decrypt the IPA from a jailbroken device (`frida-ios-dump`, `bagbak`).
- Or use a network capture (mitmproxy) if you cannot decrypt — often enough for
  API work.

### Desktop (Electron)

- Windows: the app is a folder in `%LOCALAPPDATA%\<App>\`; `resources/app.asar`.
- Extract: `npx asar extract app.asar app_out`.
- Then it is JavaScript — same as web.

---

## Static analysis (the map)

### Strings and URLs

```bash
strings -n 8 app.apk | grep -Eo 'https?://[a-zA-Z0-9._/-]+' | sort -u
apktool d app.apk -o app_src
grep -rEo 'https?://[a-zA-Z0-9._/-]+' app_src | sort -u
grep -rEi 'api[_-]?key|secret|token|firebase|aws|s3|graphql' app_src
```

### Manifest

- `AndroidManifest.xml`: exported activities/services/receivers, deep links
  (`intent-filter` with `VIEW` + scheme), `android:debuggable`,
  `android:allowBackup`, `usesCleartextTraffic`.
- Exported components with no permission = attack surface (deep-link hijack,
  intent injection).

### Native libraries

- `lib/arm64-v8a/*.so` — string search for endpoints and keys.
- Hardcoded secrets in JNI are common.

### Obfuscation

- ProGuard/R8 renames classes but **not** strings. String search still works.
- React Native: `index.android.bundle` is JS — beautify it.
- Flutter: `libapp.so` — use `strings`, or `reFlutter` for the snapshot.

---

## Dynamic analysis (the behaviour)

### Proxy the traffic

1. `mitmproxy` or Burp with a CA installed on the device.
2. Android 7+ ignores user CAs for app traffic → need a rooted device with the CA
   in the system store, or `frida` + `objection` to bypass pinning:

```bash
objection -g com.vendor.app explore
android sslpinning disable
```

3. iOS: `objection` `ios sslpinning disable`, or a jailbroken device.

### What to look for in the traffic

- **Endpoints the web app does not expose.** Mobile APIs are often older (v1) and
  less protected.
- **Auth:** a bearer token, a device id, a `X-Signature` header computed from the
  body. The signature is the interesting part — if you can compute it, you can
  replay/modify.
- **Keys:** an `api_key` query param the web app does not need.
- **IDOR:** object ids in mobile calls that the web app filters.

### Frida for logic

```js
// dump a function's arguments
Java.perform(function () {
  var C = Java.use("com.vendor.app.ApiClient");
  C.request.implementation = function (url, body) {
    console.log(url, body);
    return this.request(url, body);
  };
});
```

Use it to read the signature algorithm, the token refresh, the encryption key.

---

## The mobile-specific bug classes

| Class | What to test |
|---|---|
| Hardcoded secrets | API keys, signing keys, Firebase config (public—not a bug) |
| Auth model | Token never expires, weak device binding, no revocation |
| Deep links | `myapp://reset?token=` hijack, intent redirection |
| Exported components | Any app can start your activity with a malicious intent |
| Insecure storage | `SharedPreferences`/Keychain with tokens readable on rooted device (Medium) |
| Certificate pinning bypass | Only matters if it enables a real backend bug |
| WebView | `addJavascriptInterface`, `file://` access, `setAllowUniversalAccessFromFileURLs` |
| Backup | `allowBackup=true` → `adb backup` extracts tokens |
| Clipboard | Sensitive data on the clipboard |

### The ones that pay

- **A mobile API endpoint with worse auth than the web app** → BOLA on the mobile
  path.
- **A hardcoded *live* cloud key** → Critical (see `14-secrets-and-js-analysis.md`).
- **Deep link to a token-bearing URL** → ATO if the token is a reset/verify token.
- **WebView with JS bridge** → RCE-ish on the device, usually Medium.
- **`allowBackup` + token in prefs** → Medium (needs physical access).

---

## Desktop/Electron specifics

- `app.asar` contains the JS — same route extraction as web.
- `nodeIntegration: true` + `contextIsolation: false` + loading remote content =
  RCE on the desktop. Critical if it loads attacker-controlled content.
- Auto-update over HTTP, or unsigned updates → supply chain.
- Local HTTP server on `127.0.0.1:PORT` with no auth → any local process (or a
  website via DNS rebinding) talks to it.
- IPC handlers that trust renderer input.

---

## Severity

| What you showed | Severity |
|---|---|
| Live cloud key from the app | Critical |
| Mobile API BOLA | High |
| Auth token never expires / no revocation | Medium–High |
| Deep link token hijack → ATO | High |
| Electron `nodeIntegration` + remote load | Critical |
| Local unauth HTTP server + rebinding | High |
| Insecure storage on rooted device only | Low–Medium |
| Firebase config in app | Info (public) |
| Certificate pinning absent (alone) | Info |

---

## Discipline

- Use your own device/emulator and your own account.
- Do not repackage and distribute the app.
- Do not modify an app and install it on someone else's device.
- Report the backend bug, not the pinning absence.

---

## What closed looks like

- Mobile API enforces the same object auth as web → closed.
- Tokens expire and revoke → closed.
- Deep links carry single-use, bound tokens → closed.
- WebView has `javascriptEnabled=false` or no bridge → closed.
- Only public keys in the bundle → closed.
