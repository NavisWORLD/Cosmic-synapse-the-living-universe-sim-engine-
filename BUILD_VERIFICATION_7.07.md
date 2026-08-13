# SIM EARTH 7.07 — Build Verification Receipt

Verified 2026-08-12 America/Chicago / 2026-08-13 UTC.

## Canonical engine identity

Canonical source:
`standalone/SIM_EARTH_7_07_ALIEN_CONTROL_CENTER.html`

Canonical LF-normalized SHA-256:

```text
62a2bb449abc28a0860fdaeec15ba4c5b53ae8199679029f97e7270cb4a90647
```

The repository verifier also checks that the standalone source contains the required 12D, 42D, and 54D state arrays/name maps plus `CSTStateEngine`, `SensorFusion`, `SimEarth707App`, and Genesis `Universe` ancestry.

## Final main verification

- Workflow: **Verify engine**
- Run: `31658824109`
- Result: **SUCCESS**
- Steps passed: checkout, Node setup, `npm run verify`, `npm run prepare:web`.

## Android

- Workflow run: `31658603610`
- Result: **SUCCESS**
- Native path: Capacitor Android → Gradle `assembleDebug`
- Artifact: `SIM-EARTH-7.07-Android-debug-APK`
- Artifact ID: `9165359942`
- Artifact archive digest:
  `sha256:3859a6f282de6185aae71392abfe98dc347401694a9248d4345433a91218fcaf`

## Apple iOS Simulator

- Workflow run: `31658603593`
- Result: **SUCCESS**
- Native path: Capacitor iOS → Xcode project → unsigned iOS Simulator app
- Artifact: `SIM-EARTH-7.07-iOS-Simulator`
- Artifact ID: `9165354300`
- Artifact archive digest:
  `sha256:34472e6e9f8cd82b953f47f1ae693ccb00d6b9a10c2d76fa2a1a91f03c99302b`

This validates the native iOS code/build path. A physical-device, TestFlight, or App Store IPA still requires the publisher's Apple Developer signing certificate/profile and is intentionally not represented as already signed.

## Desktop — Windows / macOS / Linux

Workflow run: `31658662452`

All three operating-system jobs passed verification, PWA preparation, Electron Builder packaging, and artifact upload.

### Windows
- Result: **SUCCESS**
- Target: NSIS installer
- Artifact: `SIM-EARTH-7.07-Windows`
- Artifact ID: `9165381439`
- Artifact archive digest:
  `sha256:a0c178ba0fda72c7e3756e1f4f155f9f0344d9b41221735fcd391b053678ab46`

### macOS
- Result: **SUCCESS**
- Targets: DMG + ZIP
- Artifact: `SIM-EARTH-7.07-macOS`
- Artifact ID: `9165369014`
- Artifact archive digest:
  `sha256:c7f2e54c2fe38a06169e0c8466d2feb62bc189f0fd4b20d7e75a889d7b2b7d26`

### Linux
- Result: **SUCCESS**
- Targets: AppImage + Debian package
- Artifact: `SIM-EARTH-7.07-Linux`
- Artifact ID: `9165393493`
- Artifact archive digest:
  `sha256:7c13ea85ed8322907490b993cde39d0351b62c4861542914264add86a1d913a4`

## Release posture

After validation, the heavy Android/iOS/Desktop workflows were changed to run only by manual dispatch or a version tag. Ordinary documentation/source commits continue to run the lightweight engine verifier without rebuilding every operating-system package.

GitHub Pages is intentionally manual until the repository administrator performs GitHub's one-time **Settings → Pages → Build and deployment → GitHub Actions** enablement. After that, the included Pages workflow can deploy the installable PWA.

## What this receipt proves

It proves that the repository's canonical browser engine passes its declared structural/hash checks and that the configured Android, iOS Simulator, Windows, macOS, and Linux packaging pipelines completed successfully on GitHub-hosted runners.

It does **not** convert simulation variables or CST research hypotheses into validated physical laws; scientific claims remain subject to the research/validation guidance in `docs/RESEARCH_GUIDE.md`.
