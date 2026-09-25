# Lost COSMOS V3 // Verified RPG build

Release candidate completed reproducible native GBA build and two real mGBA autorun boots in GitHub Actions run [36098609241](https://github.com/NavisWORLD/Cosmic-synapse-the-living-universe-sim-engine-/actions/runs/36098609241).

- Tested source commit: `d3b5f0fea80f0d7837b733e0b44191e7f2b6949b`
- Published editable source: `gba/lost-cosmos-v3/` on `feature/pixel-universe-gba-rpg-003`
- ROM SHA-256: `b35be00de7b370be95431ef677c8a4be7bb56f962c538cf8dd50491833607752`
- ROM size: 65,536 bytes; GBA ARM7TDMI; SRAM_V113 / LCV3
- Frozen 8,192-byte input SHA-256: `9bcecc3732fe48107554cc2041cff6088f418290fb850ec0c9b89cdc375f54c8`
- mGBA boot 1: `A5` — Origin/Ember travel, level 2, X key, Ember Saber, persisted SRAM.
- mGBA boot 2: `5A` — SRAM reload, all XYZ keys, level 3, Tide Mail, Bloom Charm, Crown Edge, ending, postgame.

Features: scrolling six-world action RPG, monsters and elite guardians, sword/magic, equipment, consumables, stats/XP, persistent simulated COSMOS companion and optional rolling archived-workload replay influencing behavior/dialogue/combat.

Scope of verification: automated in-game QA executed as an actual GBA ROM in mGBA with SRAM persistence, plus route/trigger validation and two-process host C QA. Manual controller feel, artwork aesthetics, all optional gameplay sequences and iOS Delta operation still require device playtesting. The quantum workload replay uses the frozen recorded byte tape offline; it does not submit live IBM/Rigetti jobs or generate unrestricted speech.
