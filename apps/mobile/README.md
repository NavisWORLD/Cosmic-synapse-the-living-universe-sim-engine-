# Mobile wrapper

```bash
npm install
npm run sync:web
npx cap add android
npx cap add ios
npx cap sync
```

The wrapper packages the same canonical universe engine used by the single-file and PWA builds. iOS physical-device/App Store distribution requires Apple signing/provisioning; the PWA is the zero-signing iPhone install path.
