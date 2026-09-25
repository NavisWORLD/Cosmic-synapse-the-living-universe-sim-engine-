# Lost COSMOS V3 — reproducible local verification receipt

**Status:** playable candidate, local structural and executable host QA passed; **independent real-mGBA/Delta boot and interactive feel for this exact V3 ROM not yet verified**. Previous V2 successfully completed two mGBA boots.

- Branch created: `feature/pixel-universe-gba-rpg-003` (note: V3 source publication to this branch not complete at the time of this receipt).
- Compiler: clang ARM7TDMI (freestanding), LLD, LLVM objcopy.
- ROM size: 65,536 bytes.
- Release ROM SHA-256: `0560849a2fd18f725310ff42391bfc7eaaf5a2bae04c1b75149ad24b836811f4`.
- V3 source SHA-256: `b2917a3b0dc64b1fc722bcbe9c7d9ee74f8f9ea3267a520875bfe4070b8f3154`.
- QSEED: 8,192 bytes; SHA-256 `9bcecc3732fe48107554cc2041cff6088f418290fb850ec0c9b89cdc375f54c8`.
- Save signature: `SRAM_V113`; save magic `LCV3`; checksum stored at SRAM offset 190.
- Linker `.data`: IWRAM `0x03000000` (initialized from ROM); `.bss` end: `0x030021c8`.
- Undefined freestanding ELF symbols: none.
- Authored world/route checks: six worlds, ten travel-route checks, thirteen trigger checks, three reachable elite guardian checks — PASS.
- Executable host C QA boot 1: `A5`, Ember, X key, level 2, Ember Saber — PASS.
- Executable host C QA boot 2: `5A`, Tide Y, Bloom Z, Black Garden, Crown Edge, level 3, postgame — PASS.
- Additional C unit QA: melee attacks prioritized near enemies, enemy defeat yields XP, Ether replenishes MP — PASS.
- V2 SRAM migration test using previously mGBA-generated V2 SRAM: imported valid LCV2 into LCV3, retained world 1 and X key, initialized V3 RPG fields — PASS.
- Remaining limitation: no V3 emulator visual/frame-timing pass, no live quantum-hardware input, no runtime connection to external language models.
