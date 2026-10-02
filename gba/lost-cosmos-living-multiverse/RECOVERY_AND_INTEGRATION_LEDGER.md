# LOST COSMOS — Living Multiverse / source recovery and integration gate 011

**Owner:** Cory Davis / NavisWORLD. **Status:** RECOVERY AND NATIVE-INTEGRATION STAGING ONLY — NOT a complete game or new release.

This branch starts from `feature/lost-cosmos-v10-presentation-001` and preserves the earlier native GBA history and V10 development checkpoint. No existing ROM, source, SRAM bytes, versioned map ID or archival 8,192-byte QSEED has been overwritten. This document intentionally contains no copy or quotations of the owner's private 47-page manuscript. The separate author-only page-based adaptation matrix is NOT to be committed publicly without approval.

## Actual recovered baselines

- **V5.1:** User-provided genuine 262,144-byte native `.gba`, title `LOSTCOSMOS51`, game code `LC51`, SHA-256 `53f7731240790bd41fd96fe027d34124b0461ecee98998c9783563e98ba18642`.
- **V7:** `feature/lost-cosmos-eridoria-eight-world-campaign-007` contains editable GBA source and historical mGBA two-boot release evidence. The condensed eight-world five-act campaign is not a complete page-by-page adaptation.
- **V8:** `feature/lost-cosmos-eridoria-12d-visual-story-008` contains source `gba/lost-cosmos-eridoria-v8/source/lost_cosmos_v5.c`, story adaptation docs and host suites. `feature/lost-cosmos-v8-framed-text-009` contains frame-overlap correction.
- **V9:** The V10 checkpoint reports a one-active-creature, four-wave Riftfall gauntlet and action additions. Do not assign uninspected V9 save offsets.
- **V10:** Current branch checkpoint at `gba/lost-cosmos-v10/DEV_CHECKPOINT.md` identifies separate 524,288-byte development ROM SHA-256 `1955616c938ffd376823edf1b2d0f52667bca3a863dc186136fe829d3179e47a`; source ZIP `LOST_COSMOS_V10_NOVEL_REALMS_EDITABLE_SOURCE.zip` SHA-256 `d83adb62f503af21bffeeec45a6bcf1ddf416c472d50dc8f2e97b850825bfe7d`; exact engine C SHA-256 `65880121335c2a32b1e647fed38a745d0b64e3fa001b3744228063ef33d59b4d`. **Those complete updated source/ROM files were delivered as older local ChatGPT artifacts and are not in this branch.** Recover exact matching source BEFORE attempting a real native integration.
- **Beast Box:** Original official `BCG1` is a **60-byte** versioned software-signal visual snapshot; optional `BCP1` is a **distinct 64-byte** versioned *fictional game* companion profile. Their published implementation is under `NavisWORLD/The-beast-box-`, `docs/COSMIC_GENESIS_GBA_BCP1.md` and `apps/beastbox-cloud/public/gba-module/`. The standalone build-time character importer and new allocation-free C99 roster subsystem are available to the author as a separate review/test package; they are NOT claimed to be in this Git branch or linked into a ROM.

## Baseline world IDs that must not change

V8's observed eight native world slots in current source are: `0 Origin Earth/Eridoria`, `1 Ember Axis`, `2 Tide Memory`, `3 Bloom Z`, `4 Black Garden`, `5 Synapse Crown`, `6 Dream Veil`, `7 Eldoria`. Eridoria and Eldoria are different places. Audit the latest V10 room registry and extended SRAM slots before assigning new composite (world, region, version) IDs. Do not create more worlds by renaming old maps.

## Bounded native integration (must be applied to the RECOVERED V10 source)

1. Diff recovered exact V10 C and tests against V8 plus checkpoint; lock source hashes and document true existing features. Recover V9 only to validate chronology, not overwrite V10.
2. Wire an authenticated, **build-time** Beast Box ZIP translator that preserves actual original 4×64×64 GBA 4bpp frames, BGR555 palette, stable BCP1 ID, source seed/gen version and game-only statistics; strictly separate optional BCG1. Reserve genuine OBJ OAM/palette/VRAM via current allocator, not blindly using sample slot 0. No live web download, unexported private memory or model weights on a GBA cartridge.
3. Add independent bounded creature roster to proven native gameplay. Keep current one-active bonded companion and its V9/V10 save fields until compatible migration is verified. Include abilities, distinct species and art, actual world encounters, stats with effects, branching evolution and corruption-guarded persistence.
4. Create distinct region geometry through a reproducible tile/collision/event pipeline and real new quests, bosses, loot/crafting/economy, presentation and story decisions; no fake unlocked flags standing in for the gameplay.
5. Keep author-only PDF outside the public repo. Get explicit author decisions on conflicting literary crystal destinations and identities before publishing final script. Maintain separate manuscript, appendix and game-added dialogue provenance.
6. Verify new GBA ARM7 build and header, exact-hash reproducibility, testable battle/quest/evolution fixtures and old-save migration, real emulator screenshot and two-boot controller evidence, start-to-credits all three endings, and independent Delta iPhone manual retest **before merge or release**.

## Acceptance status (current truth)

- Book: 47/47 pages read; 69 **initial** page/appendix beats privately indexed; exhaustive scene-level adaptation NOT complete.
- New native creature helper: allocation-free C99 host regression checks and ARM7 **object compilation** passed in separate package. Not linked into existing GBA ROM.
- Import: strict standalone ZIP and CRC checks exercised; real user companion ZIP and actual game import/play NOT yet demonstrated.
- Content: 5-act fully extended native campaign, complete atlas and species ecology, soundtrack, crafting, ending-branch playthrough NOT delivered here.
- Verification: older V7 mGBA receipts and historic V10 **reported** host tests must not be presented as current V10 emulator/Delta acceptance. V10 final source still missing from checked remote stores.
- Public/private: no private manuscript or owner signal data in this branch.

**Merge policy:** This branch may remain a staging/draft PR but cannot be merged or called COMPLETE until full latest native source, integrated ROM, authoritative public/private provenance and actual acceptance evidence exist.
