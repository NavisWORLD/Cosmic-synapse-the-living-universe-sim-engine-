# Build & Distribution Manual

## Prerequisites
- Standalone/PWA: any modern browser; Python is optional for local serving.
- Packaging: Node.js 22+ and npm.
- Android: Java/Android SDK are needed for local native builds; GitHub Actions provides a reproducible debug APK route.
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

## GitHub Pages — one-time repository switch
For a brand-new repository, GitHub requires an administrator to enable Pages before the Actions token may deploy it. In **Settings → Pages → Build and deployment**, choose **GitHub Actions** once. Then open **Actions → Deploy PWA to Pages → Run workflow**. The workflow verifies the canonical engine before upload.

## Android
Local generation:
```bash
npm run prepare:web
npx cap add android
npx cap sync android
```
Open Android Studio with `npx cap open android`, or build with Gradle. The repository workflow produces a debug APK artifact from `main`, tags, or manual dispatch.

## iOS
```bash
npm run prepare:web
npx cap add ios
npx cap sync ios
npx cap open ios
```
Select your Apple development team in Xcode, set the bundle identifier to `io.github.navisworld.simearth707`, then archive for TestFlight/App Store. CI verifies an unsigned iOS Simulator build; it intentionally does not pretend to create a public device-installable IPA without signing credentials.

## Desktop
```bash
npm run desktop
npm run dist:desktop
```
Electron Builder is configured for DMG/ZIP on macOS, NSIS on Windows, and AppImage/DEB on Linux. GitHub Actions builds all three operating-system targets.

## Release checklist
1. `npm run verify`
2. update version/changelog
3. confirm scientific labels and privacy text
4. run all platform workflows
5. tag the release
6. attach validated build artifacts to a GitHub Release
7. archive the release on Zenodo and update `CITATION.cff` with the SIM EARTH DOI
