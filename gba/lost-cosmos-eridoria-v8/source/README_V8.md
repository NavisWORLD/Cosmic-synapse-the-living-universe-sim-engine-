# Lost COSMOS V8 — Eridoria: The Depth & Chronicle Update

This is **native Game Boy Advance**, not a GBC cartridge, HD render, new engine, or claim of actual quantum dimensional physics. The 240×160 GBA frame is intentionally hand-styled. Delta on iPhone remains a separate device test.

V8 preserves the **verified V7 eight-world campaign**, the 11 original indexed cinematic screens, persistent offline COSMOS companion, the exact 8192-byte archival input tape, existing six-world RPG/spaceflight base, Origin's four connected Eridoria areas, trading, Cragstone/Malakar encounter, Dream Veil trials, Eldoria shrines, Crown ending, and SRAM migration.

## Visual repair

- Eight distinct **material palette banks per world**: ground, walking paths, masonry, arcane interactables, water/liquid, vegetation, distant terrain, and hazards. The walkable path is no longer cyan-on-cyan, and water/lava are not the same hue as the ground.
- UI reserves background palettes 13–15 with opaque dark text tiles; glyphs use a 1px shadow extrusion and an optional beveled border. Dialogue, battle cards, inventory and the HUD stay readable over the map.
- A **bounded 12D-to-depth projection** uses existing modeled state values to shift a sparse transparent, non-colliding decorative glint layer in quarter-speed parallax. Camera collision and actual map geometry never change. Terrain above row 24 uses a darker atmospheric material bank.
- Soft dithering-based OBJ contact shadows (behind the player, COSMOS, monsters and NPCs) provide visual grounding without changing enemy hitboxes or map reachability.
- The original 11 GBA-indexed story/planet cinematics are retained. They are pre-rendered images, not runtime 3D.

## Story and progression

- The existing playable, condensed **five-act Eridoria campaign** remains intact: Brindlemark → Oakwood → Cragstone/Malakar → axes/Chronoheart/Void → Dream Veil trials → Eldoria's four shrines → Crown/Lattice → player-authored ending/postgame.
- **New CHRONICLE:** 20 contextual, unlocked pages using Arin, Astrid, the guardians and the original author's world-building. They point to a concrete current quest; progress is gated by real native story flags.
- **Objective tracker:** the HUD's lower band now tells you what to do next when the screen isn't showing dialogue.
- **Character disciplines:** Arin can learn the Forge, Ranger, Rune or Guardian stance via the new CHARACTER menu. Forge grants +1 melee, Ranger recovers dodges faster, Rune grants +1 magic, Guardian grants +1 defense. This is Arin learning allies' abilities, not sixteen new controllable protagonist sprites.
- **Field Pack:** inventory screen now displays four real item quantities with exact effect descriptions. STATS shows the currently equipped discipline and HP/MP meters. Legacy equipment/consumables/shops continue to work.

Controls: START menu → CHRONICLE (left/right 20 pages), CHARACTER (A changes discipline), ITEMS (up/down then A). D-pad walks, B+D-pad runs, A interacts/attacks, R magic, L potion, SELECT+A opens optional full-screen monster battle near an enemy. Optional touch mode stays in Settings.

## Compatibility and provenance

The existing SRAM `LCV5` base checksum, V7 story extension (bytes 200–207), classic QSEED tape and all old quest fields remain unchanged. V8 only adds its **independently checksummed 208–212 extension** for stance, codex page and act log. Corruption resets those cosmetic/new fields without erasing the existing player or V7 campaign. Old valid V7 mGBA saves are exercised in host tests. Keep your backup before attempting import on Delta; V8's unique GBA cartridge header `ERV8` intentionally avoids replacing V7.

The 12D viewer is a deterministic, fixed-point **artistic projection of existing software state features**. No new proof of twelve physical spatial dimensions, real-time quantum entanglement, or consciousness is implied.

## Remaining scope

The user's original long-form manuscript also includes many scenes, named guardians, festivals, additional dungeons, major antagonist encounters and eventually multiplayer. V8 captures its **core five-act narrative** via the existing playable quest gates plus 20 concise chronicle scenes and a narrative adaptation document. It does not falsely represent hundreds of additional unique scenes, a multiplayer system or every named guardian as implemented. V8's distinct visual/gameplay repairs are independently verifiable; actual gameplay balancing and Delta-on-iPhone must be assessed by a human player.

See `ERIDORIA_CAMPAIGN_ADAPTATION_V8.md` and `v8_visual_story_tests.py`.
