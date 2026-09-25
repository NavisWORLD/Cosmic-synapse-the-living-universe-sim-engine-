# Lost COSMOS V3 — Verified GBA action-RPG release

**Status:** GitHub Actions native ARM build + two real scripted mGBA boots **PASS**. Extended player-driven usability and Delta-specific iPhone smoke testing remain device-side checks. No continuous live quantum hardware or free-form generative speech is claimed.

- Repository: `NavisWORLD/Cosmic-synapse-the-living-universe-sim-engine-`
- Branch: `feature/pixel-universe-gba-rpg-003`
- Verified gameplay/source commit: `906e15b02e0601e3d267fe14554ca4ef3699dd72`
- Successful mGBA workflow run: `36098821373`
- Workflow result: `success`
- Compiler/toolchain: GitHub Actions Ubuntu clang ARM7TDMI (freestanding), LLD, LLVM objcopy, Python 3; emulator mGBA SDL.
- Release cartridge: `SIM_EARTH_PIXEL_UNIVERSE_LOST_COSMOS_V3.gba`, 65,536 bytes.
- Exact CI-built release ROM SHA-256: `b35be00de7b370be95431ef677c8a4be7bb56f962c538cf8dd50491833607752`.
- Gameplay C source SHA-256: `3d9b4caf42dded4bf2345a9ced987604cb702e325239dfe79999df16ad31e1cd`.
- Quantum replay tape: exactly 8,192 payload bytes, SHA-256 `9bcecc3732fe48107554cc2041cff6088f418290fb850ec0c9b89cdc375f54c8`.
- Save hardware signature: `SRAM_V113` with `LCV3` save magic and V2 migration support.
- Initialized mutable `.data` is copied into IWRAM at startup; `.bss` is cleared before `gba_main`.
- GBA ARM entry, Nintendo logo/header checksum, SRAM signature, exact QSEED embedding, freestanding link, and zero unresolved ELF symbols: **PASS**.
- World verification: six worlds, authored travel routes, ship/door/lift/key/secret/Crown triggers, and elite Axis guardians reachable: **PASS**.
- Host-native C replay: two fresh processes with the same SRAM, RPG leveling/equipment/ending/postgame: **PASS**.
- Real mGBA boot 1: Origin → ruin → ship → Ember → guardian/combat → X Key → Level 2 → Ember Saber; 32,768-byte SRAM marker `A5`, stage `31`: **PASS**.
- Real mGBA boot 2: same SRAM reloaded → Tide/Y → Bloom/Z → all XYZ → Tide Mail → Bloom Charm → Black Garden → Synapse Crown → Crown Edge → ending → postgame; Level 3, marker `5A`, stage `32`: **PASS**.
- Final boot-2 RPG save state: keys `7`, world `5`, level `3`, gear-owned mask `0x1f`, weapon `2`, armor `1`, charm `1`, ending `3`, postgame `1`.

## Quantum Buddy boundary

V3's Quantum Buddy repeatedly consumes the archived 8,192-byte workload-derived tape and transforms rolling windows into deterministic software features such as mean, spread, parity, phase, a coherence proxy, burst/Hamming activity, and state-vector inputs. Those values can influence COSMOS movement, goal selection, contextual dialogue selection, and combat assistance.

This is **offline classical replay of recorded input**, not a claim that the GBA contacts IBM/Rigetti during play, performs live entanglement, or contains a conscious entity. New hardware workload captures can be incorporated later as new provenance-tracked tapes.

## Remaining device-side checks

The CI proves native GBA execution, the scripted authored route, combat/progression state transitions, and SRAM reboot persistence in mGBA. It does not substitute for extended human playtesting of difficulty balance, combat feel, visual polish, every free-roam collision path, or Delta-specific iPhone input/audio behavior.
