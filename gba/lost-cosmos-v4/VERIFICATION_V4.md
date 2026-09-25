# Lost COSMOS V4 — immutable verification receipt

**Native GBA V4 CI: PASS** — https://github.com/NavisWORLD/Cosmic-synapse-the-living-universe-sim-engine-/actions/runs/36101469554

- Verification input HEAD: `df58857ebbf696f556a6e23b71c54e3cb4ebc7a7` (workflow fix, same V4 source bytes as initially reconstructed)
- Published editable source commit: `29bcd7601651cb4297bd78b04ba40c9bf088f8f0`
- Gameplay C source SHA256: `83bdde8e628ada112f172443336628d988ec977b464d0aadb5249d1e0b6805ca`
- 64-KiB native GBA release SHA256: `01adcec584f22a3ca8435345beaa2ff2556ed557463c35cdb11a300eced2578d`
- Preserved 8,192-byte tape SHA256: `9bcecc3732fe48107554cc2041cff6088f418290fb850ec0c9b89cdc375f54c8`
- GBA ARM startup, header/logo/checksum, SRAM_V113, freestanding link: PASS
- Inherited V3 route/trigger/guardian accessibility and two-fresh-process host C gameplay checks: PASS
- 13 NPC definitions, multi-page conversations, 6 quest definitions and quest/encounter SRAM flags included.
- mGBA real boot 1 SRAM: magic LCV4, `A5` / stage 31, X Key, Ember, Level 2, Ember Saber, Mira quest started, Mira recorded in NPC log.
- mGBA real boot 2 using same save: `5A` / stage 32, XYZ keys, Crown, Level 3, Crown Edge + Tide Mail + Bloom Charm, quest completion persists, ending selected, postgame active.
- Additional local host-C tests: NPC encounter detection, dialogue UI/portrait OAM, quest reward/persistence, Tide NPCs, migrations from preserved prior mGBA V2 and V3 SRAM fixtures: PASS.

A *real emulator ran the scripted in-ROM route*; manual full-game usability, real GBA console hardware, player-controlled free roaming, and Delta iPhone experience are not asserted. Offline workload-derived features are game algorithms, **not continuous quantum hardware injection**.