# SIM EARTH 7.08 // REALITY BODY

SIM EARTH 7.08 is the packaged Reality Body release of the Cosmic Synapse living-universe simulator.

## Included release assets

- canonical standalone `SIM_EARTH_7_08_REALITY_BODY.html`;
- Windows one-click NSIS `.exe` installer;
- macOS Apple Silicon `.dmg` installer and zipped `.app` bundle;
- Linux x86-64 AppImage and Debian/Ubuntu `.deb`;
- Android installable debug APK for direct testing;
- iOS release-configuration Simulator application archive;
- SHA-256 checksum manifest.

## Reality Body

7.08 adds the raw WebGL2 Reality Body renderer, 3D terrain/flora, Luna field-explorer presence, and the boardable/flyable/landable LUNA-ARC while preserving the existing simulation, persistence, sensors and 12D → 42D → 54D state-engine lineage.

The final source was compiled and rendered in Chromium WebGL2 QA and the final graphics pass returned `gl.getError() === 0`. Cross-platform packages were built from the verified 7.08 source.

## Mobile distribution boundary

The Android APK in this release is suitable for direct testing/sideloading but is not a Play Store production-signed package. The iOS asset is a Simulator application, not a physical-device/TestFlight/App Store `.ipa`. Production store distribution requires the publisher's private Android signing key or Apple Developer signing identity/provisioning profile. Those secrets are deliberately not committed to this public repository.

## Desktop distribution boundary

Windows and macOS packages are currently unsigned. Windows SmartScreen and macOS Gatekeeper may therefore show publisher warnings. Code signing/notarization can be added when publisher certificates are configured.

## Canonical source identity

LF-normalized SHA-256:

`68318f2fc640d49596c49a9a8d8532d378951c34a42d90a5d3f774ba8775d295`

See `BUILD_VERIFICATION_7.08.md` for the full validation and artifact evidence.
