# App installation

## PWA — iPhone/iPad/Android/desktop

Generate the PWA from the canonical single HTML:

```bash
npm run prepare:pwa
```

Serve `apps/pwa/` from HTTPS for production sensor permissions/service-worker behavior.

### iPhone/iPad
Open the HTTPS PWA in Safari → Share → Add to Home Screen.

### Android
Use the browser's Install App/Add to Home Screen flow, or build the Capacitor wrapper.

## Capacitor mobile wrapper

```bash
cd apps/mobile
npm install
npm run sync:web
npx cap add android
npx cap add ios
npx cap sync
```

Android package builds use the Android SDK/Gradle. iOS simulator builds use Xcode. Physical-device/App Store distribution requires the distributor's Apple signing identity and provisioning profile.

## Desktop Electron wrapper

```bash
cd apps/desktop
npm install
npm start
npm run dist
```

The package configuration targets Windows, macOS and Linux. Production signing/notarization is left to the distributor.
