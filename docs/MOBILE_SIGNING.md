# Mobile production signing

SIM EARTH 7.08 has native Capacitor application paths for Android and iOS. The repository intentionally does **not** commit publisher private keys.

## Android / Google Play

The CI workflow builds:

- an installable debug APK for direct device testing;
- an unsigned release APK surface;
- an unsigned release AAB surface for Play distribution preparation.

For a stable production Play Store release, configure a private upload/release keystore and keep it outside the public repository. Typical CI secrets are:

- `ANDROID_KEYSTORE_BASE64`
- `ANDROID_KEYSTORE_PASSWORD`
- `ANDROID_KEY_ALIAS`
- `ANDROID_KEY_PASSWORD`

The signing key must be persistent across releases. Do not generate a disposable public-repository key for production because future updates must be signed by the same trusted key (or follow the Play App Signing key-management process).

## iPhone / iPad / App Store

The CI workflow builds a release-configuration iOS Simulator application. A physical-device/TestFlight/App Store `.ipa` requires Apple-issued publisher credentials:

- Apple Developer distribution certificate (`.p12`)
- certificate password
- provisioning profile
- Apple Developer Team ID
- export-options configuration appropriate to App Store Connect/TestFlight or ad-hoc distribution

Recommended GitHub Actions secret names for a future signed export workflow:

- `IOS_CERT_P12_BASE64`
- `IOS_CERT_PASSWORD`
- `IOS_PROVISIONING_PROFILE_BASE64`
- `IOS_TEAM_ID`
- `IOS_EXPORT_OPTIONS_PLIST_BASE64`

Those credentials are publisher secrets and should never be committed to the repository.

## What is already application-complete

The mobile wrappers consume the exact same verified `SIM_EARTH_7_08_REALITY_BODY.html` source used by desktop and standalone builds. The game includes touch movement/look, VIEW switching, SHIP/EXIT boarding state, ASCEND/DESCEND flight controls, scan controls, responsive HUD behavior and WebGL2/Canvas fallback.

Signing changes distribution trust; it does not create the gameplay application itself.
