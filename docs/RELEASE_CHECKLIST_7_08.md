# SIM EARTH 7.08 — Release Readiness Checklist

This file distinguishes completed packaging from publisher-signing requirements that cannot be fabricated by the repository.

## Desktop

- [x] **Windows one-click `.exe` installer** — Electron Builder NSIS, explicit one-click install, desktop shortcut, Start Menu shortcut, user-level install by default.
- [x] **macOS `.dmg` installer** — Electron Builder DMG target.
- [x] **macOS `.app` package** — the macOS ZIP target contains the generated `.app` bundle.
- [x] Linux AppImage and Debian/Ubuntu `.deb` packages.

The currently verified desktop payloads are unsigned. Windows may show SmartScreen warnings and macOS may show Gatekeeper warnings until publisher code-signing/notarization credentials are supplied.

## Mobile application

- [x] **Android native application wrapper** — Capacitor 8 package built from the exact verified 7.08 Reality Body web engine.
- [x] **Installable Android APK for direct testing/sideloading** — verified debug APK is available.
- [x] **Android release-build path** — GitHub Actions builds release APK/AAB surfaces in addition to the installable debug package.
- [x] **iPhone/iPad native application wrapper** — Capacitor 8 + Xcode project path built from the exact verified 7.08 engine.
- [x] **iOS Simulator application** — verified universal Simulator package (`arm64` + `x86_64`).
- [x] **Touch-safe game UI** — mobile view switching, ship boarding/exiting, flight ascend/descend, movement, scan and Reality Body fallback behavior are covered by runtime QA.
- [ ] **Physical-device/TestFlight/App Store `.ipa`** — requires the publisher's Apple Developer certificate, provisioning profile, Team ID and export configuration.
- [ ] **Play Store-signed AAB** — requires the publisher's Android upload/release keystore and signing credentials.

The two unchecked mobile distribution items are credential gates, not missing application code. The repository intentionally does not commit private signing keys.

## GitHub Release

- [x] Release automation exists for `v7.0.8`.
- [x] Release automation packages the canonical standalone HTML and the already-verified Windows, macOS, Linux, Android and iOS Simulator binaries.
- [x] Release automation generates a permanent SHA-256 checksum file.
- [x] Release notes preserve signing/platform boundaries instead of describing unsigned builds as store-signed releases.

## Verified 7.08 build evidence

Source verification and the original cross-platform run are recorded in `BUILD_VERIFICATION_7.08.md`.

Canonical LF SHA-256:

`68318f2fc640d49596c49a9a8d8532d378951c34a42d90a5d3f774ba8775d295`
