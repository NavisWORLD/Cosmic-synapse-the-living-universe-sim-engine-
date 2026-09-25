# SIM EARTH // LOST COSMOS V4 — The Living Worlds

**Native Game Boy Advance (240×160)** cosmic exploration/action-RPG. V4 continues the verified V3 game source without resetting the six-world story, combat, ship, stats, magic, inventory, or the optional offline workload-conditioned COSMOS buddy. V4 saves use `LCV4` SRAM and can import valid V2/V3 save bytes if the emulator actually associates that old `.sav` with the new cartridge. Back up saves before importing.

## What's new in V4

- **Visual world pass:** more differentiated planet palettes, decorated 8×8 landscape tiles, new floor/path/grass motifs, ruins, lamps, flower/crystal and machinery features, animated world-light accents, water/lava/furnace/plant updates and additional sprite detailing. This is intentionally **hardware-feasible 2D GBA pixel art**, not HD or 3D rendering.
- **13 named inhabitants** (bounded by the OAM budget) spread across the six worlds and an interior, with stationary/wandering spawn patterns and four NPC sprite styles.
- **Dialogues:** a visible speaker name, NPC portrait sprite, multi-page lore and contextual lines, A to advance/accept and B to exit; optional COSMOS interjections respond to certain conversations and the archived workload-derived Q-BUDDY features.
- **Six micro-quests:** Beacon Shard, Forge Test, Old Archive, Seed Machine, Lost Future, Three Axes. Quests use persistent started/completed flags and reward items, credits, buddy trust, HP or MP.
- **NPC services:** a potion merchant and an in-world healing interaction. **Menu:** QUESTS journal and NPC LOG alongside the preserved V3 RPG tabs.
- **Preserved gameplay:** six 64×64-tile worlds with interiors, X/Y/Z depth travel, a flyable ship, player sword and magic, six monster families/three guardians, XP/levels, gear, the Crown choice, postgame sandbox and COSMOS's software state/memories.

## Controls

- D-pad: walk or steer ship; **B + D-pad:** run / faster ship.
- **A:** interact with a nearby map object or NPC, advance conversation; otherwise sword attack. In space A lands near a world.
- **R:** equipped spell, or up a layer at an elevator. **L:** potion, or down at an elevator.
- **Select:** place beacon. **Start:** pause and access the RPG menus, including QUESTS and NPC LOG.
- During NPC dialogue: **A** to proceed or accept the displayed prompt; **B** closes dialogue.

## Quantum Buddy is an offline game agent

The optional Q BUDDY loops over the preserved **8,192-byte workload-derived tape** and repeatedly derives classical software features to vary goal scoring, autonomous movement, contextual lines, and combat support. Recorded bytes are neither a connection to live IBM/Rigetti hardware nor evidence of consciousness or physical quantum coherence. Disable Q BUDDY or AUTO TALK independently in SETTINGS. This package does not verify the original tape's hardware provenance.

## Reproducible source and verification

This directory includes ARM7TDMI source, a GBA start/link script, original tape, ROM builder, map/trigger verifier, two-process host C route QA and NPC/dialogue/quest regression tests. Run:

```sh
chmod +x build_v4.sh
./build_v4.sh
python verify_routes.py
python host_qa_v4.py  # generates host_qa_v4.c first
python feature_tests_v4.py
```

`QA=1 ./build_v4.sh` is an **autorun test cartridge**, not the ordinary game. Real mGBA two-boot evidence is tracked in the repository workflow `pixel-universe-gba-v4.yml`; see `VERIFICATION_V4.md` for what was actually checked. Screenshots generated from host VRAM are previews, not substitute mGBA captures.

The previous V3 remains available unchanged. Delta on iPhone still needs manual control, sound, readability and save-import playtesting.