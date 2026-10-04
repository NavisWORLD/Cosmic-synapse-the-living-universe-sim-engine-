# EmulatorJS 4.2.3 (unmodified, GPL-3.0)

This directory is a pinned, unmodified copy of [EmulatorJS](https://github.com/EmulatorJS/EmulatorJS) 4.2.3 and its mGBA core package. It is **not** part of the Apache-2.0 Living Universe engine.

- License: GNU GPL-3.0. See `LICENSE`.
- Loaded only from `arcade/lost-cosmos/index.html` inside an iframe.
- Cores: `data/cores/mgba-wasm.data` and `data/cores/mgba-legacy-wasm.data` (the non-thread builds, so the page does not need cross-origin isolation).
- No Nintendo BIOS is included. The core uses its own high-level BIOS stand-in.
- Upstream: https://cdn.emulatorjs.org/4.2.3/data/ and https://github.com/EmulatorJS/EmulatorJS

Do not copy these files into `standalone/` or link them from the one-file engine.
