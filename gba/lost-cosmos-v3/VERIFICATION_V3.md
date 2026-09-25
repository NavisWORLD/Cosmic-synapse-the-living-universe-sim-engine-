# Lost COSMOS V3 — Verified GBA action-RPG release

**Status:** GitHub Actions native ARM build + two real scripted mGBA boots **PASS**. Extended player-driven usability and Delta-specific iPhone smoke test remain unverified; no continuous live quantum hardware or free-form generative speech is implemented.

- Repository: `NavisWORLD/Cosmic-synapse-the-living-universe-sim-engine-`
- Branch: `feature/pixel-universe-gba-rpg-003`
- Verified GitHub Actions commit: `e81085d5d9461dee128c496efaf4165a81fb1c84`
- Successful mGBA workflow: https://github.com/NavisWORLD/Cosmic-synapse-the-living-universe-sim-engine-/actions/runs/36098528364
- Compiler/toolchain: GitHub Actions Ubuntu clang ARM7TDMI (freestanding), LLD, LLVM objcopy, Python3; emulator mGBA SDL.
- Release cartridge: `SIM_EARTH_PIXEL_UNIVERSE_LOST_COSMOS_V3.gba`, 65,536 bytes.
- Exact GitHub CI-built release ROM SHA-256: `b35be00de7b370be95431ef677c8a4be7bb56f962c538cf8dd50491833607752`.
- Gameplay C source SHA-256: `3d9b4caf42dded4bf2345a9ced987604cb702e325239dfe79999df16ad31e1cd` (same source Git blob as verified branch).
- Quantum replay tape: exactly 8,192 bytes, SHA-256 `9bcecc3732fe48107554cc2041cff6088f418290fb850ec0c9b89cdc375f54c8`.
- Save hardware signature: `SRAM_V113` with `LCV3` save magic; on-ROM valid V2 SRAM migration path verified locally using a prior real-mGBA-produced V2 save.
- Source `.data` relocated/copies into IWRAM 0x03000000, `.bss` cleared, ARM entry, logo and header checksum verified; freestanding undefined ELF symbols: none.
- World verification: six worlds; 10 routes, 13 interaction triggers and all three elite guardians accessible — PASS.
- Host-native C tests: scripted two fresh-process gameplay boots with SRAM persistence; RPG leveling/equipment/ending/postgame — PASS.
- mGBA boot 1: in-ROM scripted walk, interior, ship, space, Ember/X, level 2, weapon 1; actual SRAM 32,768 bytes, LCV3 magic, marker `A5`, stage `31` — PASS.
- mGBA boot 2: same SRAM reloaded; all XYZ keys, Crown, level 3, sword 2, armor 1, charm 1, postgame, marker `5A`, stage `32` — PASS.
- Extra local unit checks: melee priority against nearby monsters, XP on defeat, Ether MP recovery — PASS.

**Precision:** scripted emulator QA exercises native GBA code and SRAM; it is not proof of extended player-controlled combat feel, complete cosmetic quality, collision-free unconstrained travel, or correctness of archived quantum provenance. Offline tape replay is deterministic classical behavior using recorded bytes. No hardware entanglement or online IBM/Rigetti jobs occur while playing.

**Build reproducibility note:** the included qseed.h is text-formatted from the original seed; its 8,192 payload bytes match the GitHub CI qseed byte-for-byte by SHA-256. The official downloadable ROM is the *exact* CI-built artifact, which may have a different SHA from locally compiled builds due to LLVM/toolchain versions. For byte-identical source formatting and current CI workflow, use the linked branch.