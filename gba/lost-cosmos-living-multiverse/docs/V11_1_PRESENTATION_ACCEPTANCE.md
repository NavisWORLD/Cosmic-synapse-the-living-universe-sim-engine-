# LOST COSMOS V11.1 — presentation and Quantum Beast UI acceptance

Owner: Cory Davis / NavisWORLD

V11.1 is an in-place presentation pass over the existing V11 integration. It
does not restart the game or replace the V10.8 art, SOL-derived RPG systems,
save lineage, creature roster or Quantum Beast architecture.

## Implemented

- Imported Quantum Beast field art now keeps the verified 32x32 hardware canvas
  but caps the visible silhouette at 20x20 pixels, centered and nearest-neighbor
  sampled from the verified 64x64 Beast Box pixels. Miraby's tested visible
  frame-0 bounding box is 15x20 pixels.
- Exploration HUD is reduced to compact HP/LV/MP information. Region names are
  temporary entry banners instead of permanent debug-style headers.
- The pause landing page is now ten player-facing categories: MAP, QUEST, PARTY,
  ITEMS, EQUIPMENT, ABILITIES, BESTIARY, MEMORIES, BEAST BOX and SYSTEM.
- PARTY / COLLECTION no longer displays the old command wall. A opens a separate
  action panel for SET ACTIVE, TRAIN, EVOLVE, DETAILS and RELEASE.
- Wild release now requires a second confirmation; imported Quantum Beast
  identities remain pinned against accidental release.
- BESTIARY is formatted as a field journal with species list plus HOME, SKILL,
  OBS and evolution requirements.
- ABILITIES has a dedicated equip screen for SYNAPSE PULSE, EMBER BOLT,
  TIDE WARD and BLOOM NOVA with lock/equipped states.
- BEAST BOX is a dedicated page showing BRIDGE READY, VERIFIED SNAPSHOT,
  OFFLINE MODE, BCG1 + BCP1, IDENTITY LOCKED and PUBLIC ONLY memory. This is an
  honest offline import/export bridge; it does not claim live cloud connectivity.
- SYSTEM retains real runtime settings and save rather than exposing creature
  management as development controls.

## Local native verification for the Miraby build

- Native ARM7TDMI build/header/QSEED verification: PASS.
- ROM size: 1,048,576 bytes.
- Local V11.1 Miraby ROM SHA-256:
  `eb8150bce18aedfd50643cbd88c04d9c2a5642f4c97f1f468058a1283b455cd0`
- Local V11.1 engine C SHA-256:
  `279dda14bca36b6264580b94ca35763581477d64cbd786fbb8a098a037ac6b12`
- Compact imported field-art SHA-256:
  `151ae9d0fff76f08a073399bc461112204464ab20361a867a5fc41d1c714d239`
- Miraby public BCP1 identity: `f5a4cb6d`.
- Host two-process RPG/SRAM persistence QA: PASS.
- Imported BCP1 native initialization + save/restore test: PASS.
- Inventory/workshop, guaranteed biome drops and ally-command RPG regressions:
  PASS.
- 351 exact 10px-player-footprint interaction checks across 40 expansion maps
  plus six original novel-realm maps: PASS.

## Still a separate acceptance gate

This development environment did not have a usable local libmGBA runtime for a
fresh V11.1 screenshot recording. The prior V10.8/V11 engine has genuine mGBA
controller evidence, and the user's Delta screenshots directly identified the
UI/scale defects addressed here, but the **new V11.1 visual layout still needs a
fresh Delta/mGBA visual smoke after this commit**. Do not misrepresent compile,
host-C or static layout checks as that device-side visual acceptance.
