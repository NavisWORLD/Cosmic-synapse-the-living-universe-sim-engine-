# Build & Distribution Manual — SIM EARTH 7.08

## Prerequisites

- Standalone/PWA: a modern browser with WebGL2 for Reality Body; Canvas fallback remains available.
- Packaging: Node.js 22+ and npm.
- Android: Java/Android SDK for local native builds; GitHub Actions provides the reproducible debug-APK route.
- iOS: macOS + Xcode. TestFlight/App Store/device distribution requires Apple signing credentials.
- Desktop: Electron/Electron Builder dependencies are installed by `npm install`.

## Canonical source

`standalone/SIM_EARTH_7_08_REALITY_BODY.html`

LF-normalized SHA-256:

`68318f2fc640d49596c49a9a8d8532d378951c34a42d90a5d3f774ba8775d295`

## Verify

```bash
npm install
npm run verify
```

The verifier checks the exact canonical hash, Genesis/state ancestry, WebGL2 Reality Body, Luna/LUNA-ARC controls, packaging surfaces, and cleanup invariants.

## Prepare PWA

```bash
npm run prepare:web
python tools/serve.py
```

`prepare:web` copies the canonical Reality Body standalone into `app/index.html` and injects only manifest/service-worker/Apple PWA metadata.

## GitHub Pages — one-time repository switch

For a brand-new repository, GitHub requires an administrator to enable Pages before the Actions token may deploy it. In **Settings → Pages → Build and deployment**, choose **GitHub Actions** once. Then open **Actions → Deploy PWA to Pages → Run workflow**.

## Android

```bash
npm run prepare:web
npx cap add android
npx cap sync android
```

Open Android Studio with `npx cap open android`, or run the Gradle debug build. The permanent GitHub workflow uploads `SIM-EARTH-7.08-Android-debug-APK` on manual dispatch/version tags. This is a debug package, not a Play Store release-signed AAB.

## iOS

```bash
npm run prepare:web
npx cap add ios
npx cap sync ios
npx cap open ios
```

Keep the stable bundle/application identifier `io.github.navisworld.simearth707` so 7.08 remains the same application lineage. Select your Apple development team in Xcode for device/TestFlight/App Store distribution.

CI intentionally validates an **unsigned iOS Simulator** build. It does not claim to produce a public device-installable `.ipa` without the publisher's signing certificate/profile.

## Desktop

```bash
npm run desktop
npm run dist:desktop
```

Electron Builder targets:

- Windows — NSIS installer
- macOS — DMG + ZIP
- Linux — AppImage + DEB

The current macOS CI host determines the architecture of the produced package; signing/notarization are separate distribution steps.

## Reality Body packaging rule

All wrappers package the generated `app/index.html`, and that file is regenerated from the exact canonical 7.08 standalone before builds. Do not hand-edit `app/index.html` as a source of truth.

## Release checklist

1. run `npm run verify`;
2. run `npm run prepare:web`;
3. inspect Reality Body in a real WebGL2 browser;
4. update version/changelog/citation metadata;
5. run Android, iOS Simulator, Windows, macOS and Linux workflows;
6. record run IDs/artifact digests in the 7.08 verification receipt;
7. squash/review/merge the release branch;
8. re-run the verifier on production `main`;
9. tag/create a formal GitHub Release when desired;
10. archive the release on Zenodo only through the actual Zenodo publication flow; never invent a DOI.
