# LOST COSMOS — Living Multiverse / source recovery and integration gate 011

**Owner:** Cory Davis / NavisWORLD. **Status:** EXACT V10 SOURCE/ROM RECOVERED; NATIVE CREATURE INTEGRATED LOCALLY AND HOST TESTED; PUBLIC PR STAGING DOCS ONLY. NOT a complete game or final release.

This branch starts from `feature/lost-cosmos-v10-presentation-001` and preserves the earlier native GBA history and V10 development checkpoint. No existing ROM, source, SRAM bytes, versioned map ID or archival 8,192-byte QSEED has been overwritten. This document intentionally contains no copy or quotations of the owner's private 47-page manuscript. The separate author-only page-based adaptation matrix is NOT to be committed publicly without approval.

## Actual recovered baselines

- **V5.1:** User-provided genuine 262,144-byte native `.gba`, title `LOSTCOSMOS51`, game code `LC51`, SHA-256 `53f7731240790bd41fd96fe027d34124b0461ecee98998c9783563e98ba18642`.
- **V7:** `feature/lost-cosmos-eridoria-eight-world-campaign-007` contains editable GBA source and historical mGBA two-boot release evidence. The condensed eight-world five-act campaign is not a complete page-by-page adaptation.
- **V8:** `feature/lost-cosmos-eridoria-12d-visual-story-008` contains source `gba/lost-cosmos-eridoria-v8/source/lost_cosmos_v5.c`, story adaptation docs and host suites. `feature/lost-cosmos-v8-framed-text-009` contains frame-overlap correction.
- **V9:** The V10 checkpoint reports a one-active-creature, four-wave Riftfall gauntlet and action additions. Do not assign uninspected V9 save offsets.
- **V10:** Current branch checkpoint at `gba/lost-cosmos-v10/DEV_CHECKPOINT.md` identifies separate 524,288-byte development ROM SHA-256 `1955616c938ffd376823edf1b2d0f52667bca3a863dc186136fe829d3179e47a`; source ZIP `LOST_COSMOS_V10_NOVEL_REALMS_EDITABLE_SOURCE.zip` SHA-256 `d83adb62f503af21bffeeec45a6bcf1ddf416c472d50dc8f2e97b850825bfe7d`; exact engine C SHA-256 `65880121335c2a32b1e647fed38a745d0b64e3fa001b3744228063ef33d59b4d`. **Those exact complete source/ROM artifacts have now been recovered from the author's ChatGPT Library and verified SHA-256. They are not currently committed to this GitHub branch.**
- **Beast Box:** Original official `BCG1` is a **60-byte** versioned software-signal visual snapshot; optional `BCP1` is a **distinct 64-byte** versioned *fictional game* companion profile. Their published implementation is under `NavisWORLD/The-beast-box-`, `docs/COSMIC_GENESIS_GBA_BCP1.md` and `apps/beastbox-cloud/public/gba-module/`. A validated offline build-time importer and allocation-free C99 roster are now linked into a separately packaged local V10.1 native development ROM (details below), but that newly built source and ROM are NOT claimed to be present in this documentation-only PR.

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

## Verified author-library recovery and local development integration (2 October 2026)

- **Recovery closure:** Exact original author Library artifact `LOST_COSMOS_V10_NOVEL_REALMS_EDITABLE_SOURCE.zip` SHA-256 `d83adb62f503af21bffeeec45a6bcf1ddf416c472d50dc8f2e97b850825bfe7d` and original 524,288-byte GBA ROM SHA-256 `1955616c938ffd376823edf1b2d0f52667bca3a863dc186136fe829d3179e47a` both matched the historical V10 checkpoint. An untouched original ZIP rebuild of all original 23 cinematic frames and the ARM7 ROM independently reproduced the original SHA byte-for-byte. No historical source or saves were overwritten.
- **Locally integrated actual engine, not pseudocode:** The exact recovered original C hash `65880121335c2a32b1e647fed38a745d0b64e3fa001b3744228063ef33d59b4d` was patched in a fail-closed, repeatable step to staged C hash `663d07b659413f47b0a0291664c7ab839d0070192fbdb687844c3a19c96c703c`. Original V10 native maps, 23 original cinematics, full older tests and archived QSEED stayed in place.
- **Locally built NEW native V10.1 DEV image:** A freestanding ARM7TDMI build with distinct GBA code `ERL1` and title `COSMOS V10LM` produced 524,288-byte development ROM SHA-256 `a60cf352690c5668ec8d4ad5dea651c87d1f8d0f3ee8ef80b7790d54845a0797`. Native header/logo/checksum, SRAM signature, unchanged 8,192-byte QSEED and undefined symbol checks passed. This is a new DEVELOPMENT ROM, not a complete RPG release.
- **Real code additions:** 12-slot fixed-size native party; source-linked weakened-enemy bonding, stat-based battle assist and XP; two-stage conditional evolution; in-game START > COSMOS > R roster UI with activation/trust training; distinct 252-byte CRC32 `LCR1` save at SRAM bytes `1024..1275`, preserving old V10 legacy records `0..237` in host tests; optional validated build-time Beast Box **BCG1+BCP1** import of actual approved four-frame 4bpp artwork and seeded game profiles.
- **Tests:** C99 and five strict ZIP validation tests, existing source-native V10 host tests (V5, V6, V7, cinematics, V8, V9, V10 intro, Heartwood, other novel realms, finale/audio) and an additional direct V10 native host-integration regression for 12 captures, overflow, XP/evolution, save reload and intentionally corrupted extra roster all passed. Also compiled an optional variant with an **actual** author Library BCG1-only Aurora ZIP and separately host-tested a deliberately synthetic BCP1 character through new game initialization and SRAM restore. Synthetic tests are NEVER claimed as actual user-origin BCP1 gameplay.
- **Gates still open:** The updated local engine/source package has not yet been pushed into this PR, the entire manuscript and appendix are not playable, species art/unique combat and deeper quests remain incomplete. New image lacks controller-led mGBA screenshot/playthrough evidence and independent real Delta-on-iPhone/physical-device acceptance. Keep this PR **draft** until full content and emulator/manual evidence exists.
- **True V10 map registry:** Original world IDs `0..7` remain. Existing exact V10 novel room pairs include Origin/Eridoria `(0,7)` Heartwood, `(0,8)` Glacial, `(0,9)` Ember Caverns, `(0,12)` Celestial Peaks, Dream Veil `(6,11)` Nyssa Festival and Eldoria `(7,10)` Hollow Grove. Never claim all novel rooms live in Origin world.

**Only documentation in this public PR; the 47-page original manuscript, private 69-item page matrix, local build-time Aurora ZIP and private user sprites are not posted here.**
