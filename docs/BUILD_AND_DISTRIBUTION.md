# Build & Distribution Manual

## Prerequisites
- Standalone/PWA: any modern browser; Python is optional for local serving.
- Packaging: Node.js 20+ and npm.
- Android: Java/Android SDK are needed for local native builds; GitHub Actions provides a reproducible debug build route.
- iOS: macOS + Xcode. TestFlight/App Store/device distribution requires Apple signing credentials.

## Verify
```bash
npm install
npm run verify
```

## Prepare PWA
```bash
npm run prepare:web
python tools/serve.py
```
`prepare:web` copies the canonical standalone game into `app/index.html` and injects only the manifest/service-worker/Apple PWA metadata.

## Android
First local generation:
```bash
npm run prepare:web
npx cap add android
npx cap sync android
```
Open Android Studio with `npx cap open android`, or build with Gradle. The repository workflow produces a debug APK artifact automatically.

## iOS
```bash
npm run prepare:web
npx cap add ios
npx cap sync ios
npx cap open ios
```
Select your Apple development team in Xcode, set the bundle identifier to `io.github.navisworld.simearth707`, then archive for TestFlight/App Store. The CI workflow verifies an iOS Simulator build without pretending to produce a signed public `.ipa`.

## Desktop
```bash
npm run desktop
npm run dist:desktop
```
Electron Builder is configured for DMG/ZIP on macOS, NSIS on Windows, and AppImage/DEB on Linux.

## GitHub Pages
The Pages workflow runs `prepare:web` and publishes `app/`. This is the recommended public install surface because camera/microphone/PWA browser capabilities work best from a secure HTTPS context.

## Release checklist
1. `npm run verify`
2. update version/changelog
3. confirm scientific labels and privacy text
4. run all platform workflows
5. tag `v7.0.7` (or next semantic version)
6. attach validated build artifacts to a GitHub Release
7. archive release on Zenodo and update `CITATION.cff` with the new SIM EARTH DOI
