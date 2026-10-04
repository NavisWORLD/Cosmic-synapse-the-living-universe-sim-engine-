# LOST COSMOS / ERIDORIA — verified V6 campaign pilot

Native Game Boy Advance game continuing the V5.1 source. This is the first playable Eridoria integration, not the finished five-act RPG or a new PC game.

Verified real mGBA run: https://github.com/NavisWORLD/Cosmic-synapse-the-living-universe-sim-engine-/actions/runs/36150339295
Player ROM SHA-256: cf721688d9d4d6cee4d201ea9bf705663ee2057f96ea8154165e7d9a61d598d1 (262144 bytes).
Exact C source SHA-256: 4d5a6d62659de105d325736d6a204c9c6368850df02b506116fc9e290b8dd0c9.
Archived 8192-byte workload replay input unchanged: 9bcecc3732fe48107554cc2041cff6088f418290fb850ec0c9b89cdc375f54c8. This is classical offline game behavior, not live quantum computation.

WHAT IS PLAYABLE
- Text readability fix: opaque font including spaces, dark framed NPC/COSMOS/battle panels, and separated HUD.
- Playable blacksmith Arin; named Astrid NPC and persistent Heart of Eridoria quest linking Malakar to Ember's first restored Axis.
- Optional turn-based monster duels preserving original real-time action combat: Select+A near a monster. FIGHT / MAGIC / ITEM / TALK / RUN, guarded telegraphed attacks and optional non-lethal mercy outcomes.
- Existing six-world progression, ships, NPC quests, companion, gear, story endings, postgame and backward SRAM migration remain.

ACTUAL VERIFICATION
Native ARM cartridge, structural checks, original action-RPG two-process progression, four generations of actual emulator save migration, cinematic/audio/controller regression tests, actual mGBA title/gameplay frames, and two mGBA boots including Astrid quest/combat/Ember save and reload through Crown/postgame all passed in run 36150339295.

ROADMAP
The exported V6 source bundle includes ERIDORIA_STORY_BIBLE.md, an edited five-act campaign treatment based on Cory Davis's original Arin/Malakar/Heart of Eridoria story: Cragstone Temple, guardian trials, Nihilos, Chronoheart, Voidborn, Zarkheth and Asteroth. Extra planets, large boss illustrations, trading systems, all guardian classes and the complete five-act campaign are planned, NOT implemented in this pilot.

PLATFORM
Real Game Boy Color .gbc would require a separate reduced rewrite and cannot execute this ARM GBA code. Here we retain the proven native .gba game with GBC-inspired high-contrast UI. No manual Delta touchscreen or physical GBA result is claimed.