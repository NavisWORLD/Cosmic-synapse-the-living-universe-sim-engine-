# Build matrix

| Target | Source | Toolchain | Output |
|---|---|---|---|
| Single HTML | root Ultimate file | none | `.html` |
| PWA | `scripts/sync-engine.mjs` + `apps/pwa/` | Node/static server | installable web app |
| Android | `apps/mobile/` | Node + Capacitor + Android SDK | APK/AAB |
| iOS | `apps/mobile/` | Node + Capacitor + Xcode | simulator/device app; distribution requires signing |
| Desktop | `apps/desktop/` | Node + Electron | Windows/macOS/Linux package |
| Native simulation | `native/` | CMake + C++20 + raylib 6 | native executable |
| External data bridge | `native/python/` | Python 3.10+ | NASA/USGS atomic snapshot |
