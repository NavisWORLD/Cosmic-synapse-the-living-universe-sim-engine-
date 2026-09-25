# Lost COSMOS V4 — The World Speaks 🌌

Native GBA action-RPG continuation of the **real mGBA-tested V3** game. V4 brings named inhabitants, dialogue, side quests, quest history, world scenery and sprite improvements. V3 gameplay, COSMOS buddy state, levels, magic, items, equipment, ship travel, all six planets, the Crown endings and postgame remain.

## New in V4

- 13 named NPCs: Mira, Ori, Ferrum, Atlas, Neri, Ripple, Kestrel, Moth, Null, Witness, Arbiter, Echo and Archivist. Up to four NPC actors are active per scene, with limited safe wandering and animated sprite archetypes.
- Multi-page speaker dialogue, conditional postgame lore, quest acceptance and turn-in, a potion merchant and healing NPC. COSMOS can comment on completed quest conversations.
- Six real small quests: Star Shard, monster trial, Origin memory, Quantum Core, secret Black Garden memory and restored XYZ axes. The rewards change inventory, credits, HP, MP or COSMOS trust.
- New pause panels **QUESTS** and **NPC LOG**, saved NPC encounters, and quest started/completed flags.
- World-specific tiles and accents: ground texture, plants, lanterns, foam, circuitry, cracks, vines, ruins, furnaces and palette-light animation; map collision/triggers from V3 are protected.

**Controls:** D-pad moves; B + D-pad runs; A interacts with nearby NPCs and mission objects (or attacks); R casts magic; L uses a potion; Start opens pause/menu; Select places a beacon. B leaves dialogue and A advances/accepts it.

## Build and verified tests

Run `./build_v4.sh`; static cartridge checks are part of that script. `python verify_routes.py` checks critical travel and interaction points, while `python host_qa_v4.py` replays two game-logic boots with persisted SRAM. `QA=1 ./build_v4.sh` creates an *autorun QA cartridge*, not the normal playable ROM.

**Hardware-emulator verification: PASS.** CI run [36101469554](https://github.com/NavisWORLD/Cosmic-synapse-the-living-universe-sim-engine-/actions/runs/36101469554) rebuilt this V4 source, passed route and host-C checks, ran real mGBA boot 1 (Mira conversation + quest → Ember/Level2/X/Saber → SRAM `A5`) and boot 2 from the *same SRAM* (XYZ → Crown → ending/postgame + completed quest → `5A`). The CI-built release ROM SHA256 is `01adcec584f22a3ca8435345beaa2ff2556ed557463c35cdb11a300eced2578d`.

**Boundaries:** this is scripted hardware-emulator QA, not proof of exhaustive manual play or Delta-specific iPhone input/audio/graphics. V4 migrates valid V2/V3 SRAM if attached; back up old saves before importing. The optional COSMOS workload mode transforms recorded 8,192-byte tape values in an offline classical game algorithm. It does not run live quantum hardware, provide free-form generated speech or establish consciousness.

The existing V3 branch and release are preserved.