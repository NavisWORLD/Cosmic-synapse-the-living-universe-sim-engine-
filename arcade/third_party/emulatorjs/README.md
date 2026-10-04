# EmulatorJS 4.2.3 (unmodified, GPL-3.0)

This directory is a pinned, unmodified copy of [EmulatorJS](https://github.com/EmulatorJS/EmulatorJS) 4.2.3 and its mGBA core package. It is **not** part of the Apache-2.0 Living Universe engine.

- License: GNU GPL-3.0. See `LICENSE`. The compression README and localization README from the same tag are kept beside those files.
- Loaded only from `arcade/lost-cosmos/index.html` inside an iframe.
- Cores: `data/cores/mgba-wasm.data` and `data/cores/mgba-legacy-wasm.data` (the non-thread builds, so the page does not need cross-origin isolation). Both packages are 7z archives. Unpacking them needs `data/compression/extract7z.js`. `extractzip.js`, `libunrar.js`, and `libunrar.wasm` are the other workers that same release loads for zip and rar payloads.
- Core report fetched before the archive: `data/cores/reports/mgba.json`.
- Localization JSON from tag v4.2.3 lives in `data/localization/`. The Lost Cosmos player sets `EJS_disableAutoLang` to false, which is the value that stops this loader from fetching a locale. The files are still self-hosted for any page that leaves automatic language on.
- Shader presets are embedded in `data/emulator.min.js` as `window.EJS_SHADERS`. The loader does not HTTP-fetch them.
- No Nintendo BIOS is included. The core uses its own high-level BIOS stand-in.
- Boot does not depend on a CDN. These files are the EmulatorJS 4.2.3 tag, copied unmodified. The emulator binary still contains an optional version notice that runs only on localhost, and a core fallback aimed at cdn.emulatorjs.org that runs only when the local core file is missing.
- Upstream: https://github.com/EmulatorJS/EmulatorJS/tree/v4.2.3/data

Do not copy these files into `standalone/` or link them from the one-file engine.
