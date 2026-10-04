# LOST COSMOS V11.1 content upgrade — resume checkpoint

Date: 2026-10-04  
Owner: Cory Davis / NavisWORLD  
Target: feature/lost-cosmos-v11-enhanced-001, PR #20  
Confirmed remote source baseline: 1c66388bb41dc7fb0d456025ffdd614560eb41e3

## Status and storage boundary

The Content Bible upgrade has substantial uncommitted implementation and native mGBA evidence in the active development workspace. That workspace became unavailable: the execution service returned environment_offline / Environment is not connected.

**This document preserves the resume instructions, not the uncommitted source or a finished ROM.** Do not treat the existing remote baseline, earlier V11.1.1 Delta Safe artifacts, or this documentation commit as the new Content Bible release. Do not reset or discard the local workspace when access returns.

The working repository is /workspace/scratch/be5fd7869092/lost-cosmos. The game is gba/lost-cosmos-living-multiverse, and the native C game directory is LOST_COSMOS_V10_SOURCE.

## Local implementation to retain and review

- content/v11_1_catalog.json contains 100 items, 100 characters and 100 skills with Bible IDs.
- Generated content_v11_data.h and content_v11_art.h provide catalogs and palette-limited original reference-sheet crops.
- content_v11_state.h, content_v11_core.h, content_v11_world.h, content_v11_combat.h and content_v11_menus.h implement additive progression, eight regions, encounters, content menus, crafting, inventory, party actions and persistence.
- content_v11_import_receipt.h and content/v11_1_import_receipt.json check the recovered public Miraby snapshot. imported_companion.h contains the real public Miraby assets.
- tools/build_content_v11.py and build_content_art_v11.py rebuild catalogs and art. tools/integrate_content_v11.py has already been applied; do not blindly apply it again.
- tools/export_beastbox_v11.py was written but still needs export/import round-trip validation.
- Native main lost_cosmos_v5.c and start_v5.S have new integration hooks and a freestanding ARM division helper.
- Uploaded sheets are copied into content/art_sources. Retain these assets for reproducible builds.

Bible indices: items W 0–24, A 25–49, C 50–69, U 70–89, K 90–99; skills S 0–29, B 30–49, P 50–74, X 75–89, U 90–99. Characters NPC 0–29, common 30–69, elite 70–89, major boss 90–99.

New regions use original world ID 0 and rooms 70–77. Original world IDs and campaigns remain unchanged. Entry is the new Brindlemark signal-road trigger at tile 34,44 in room 2. Eight lit beacons enable return travel. Crown access requires the earned Z Key from Vesper. Quiet requires carried Memory Echoes.

## Last native build and evidence

The last local native build used IMPORTED_BEAST=1. Historical output name is LOST_COSMOS_V10_SOURCE/LOST_COSMOS_V10_OPENING_QA.gba.

- ROM SHA-256: 9334c01dad7265755c63b1b611cc69043f9dae0797be5aaf5d7297cd14a0fde9
- ELF SHA-256: 4f46e44cf35d600c368d17dbcdcda080627b9c02be31be2fc8d90faa7281f369
- Frozen QSEED SHA-256: 9bcecc3732fe48107554cc2041cff6088f418290fb850ec0c9b89cdc375f54c8

Those values describe a local development build. No release file has been packaged or uploaded for the Content Bible upgrade.

Local test progress before the outage:

- Catalog/art contracts passed.
- Native C host tests passed the baseline variant; the newly added imported variant requires a rerun.
- Original native story-completion checks passed.
- Actual mGBA menu pilgrimage passed after menu caching and OAM visibility fixes.
- The new eight-world controller route genuinely earned all eight beacon bits (255), Outcast and Lay to Rest rewards, Vesper's key, most bosses, and reached the Quiet fight.
- **The full new route still fails its all-boss assertion.** It is not a passing end-to-end suite yet.

Do not claim physical iPhone Delta verification or a complete original five-act controller run. Those have not been established for this build.

## Immediate controller-test correction

File: tests/test_mgba_content_v11.py.

The most recent full route failed final v11_boss_done == 1023, with 1021 inferred from the earned boss state: NIHILOS ECHO bit 1 was missing. At the world-6 visit, approaching the requested Nihilos slot started a nearby elite instead; the script earned ordinary elite credits and the major-boss mask did not change.

Correct the QA targeting helper so it verifies battle_index equals the requested slot. Choose a reachable approach position that makes the requested active enemy the nearest eligible enemy, with no interfering trigger or nearby NPC. Use read-only ELF state and ordinary controller input. Alternatively defeat the interfering elite first and then deliberately initiate Nihilos. Never set boss flags or manipulate emulator memory to pass the route.

Rerun from a genuinely fresh save through all eight worlds and all ten major bosses, then cold-boot the earned save. Require beacon mask 255 and boss mask 1023. Keep the controller trace and native framebuffer evidence.

Other legitimate QA lessons already applied:

- Exclude once-per-battle Crown Judgment from the repeatedly cast primary shortcut.
- Clear inventory space through ordinary Items/drop controls, including after Vesper, so the queued Z Key can be claimed.
- bag_room() targets fewer than 27 distinct slots; key and equipped gear restrictions remain intact.
- Physical navigation uses the original 2px movement and actual 10px player footprint.

## Persistence and art invariants

- Frozen historical SRAM offsets and original journal banks are retained.
- Additive LC11 CRC content page: SRAM 6400–7167.
- Pending reward counts: additive payload offsets 548–647; rewards must remain claimable after a full bag.
- Three manual LCM1 slots: SRAM 25600, 27648 and 29696, 2048 bytes each, CRC checked and commit marker written last.
- Public LCEX export page: SRAM 6208–6399. No private memory ledger is embedded.
- Imported Miraby public identity f5a4cb6d must remain stable across import, training, rename, evolution and export.
- Portraits remain restricted to PARTY, DIALOGUE, EVOLUTION and BEAST BOX.
- Imported field art is a 32x32 native canvas with a compact silhouette. Battle art is derived from field art, uses affine slot 4, and must not reuse the portrait.
- Beast Box status remains offline-first and must not claim a successful bridge handshake without actual session evidence.
- v11_ui_dirty is volatile for consistent native diagnostics. Preserve redraw caching, cached item sorting, and OAM hiding only when pause UI redraws.
- Existing enemy/NPC ABI sizes stay 16/12 bytes; new wide enemy HP is maintained separately.

## Export round trip still outstanding

tools/export_beastbox_v11.py validates LCEX from an actual SRAM save, emits BCP1/BCG1 and public pixel assets plus a receipt. Its new lost-cosmos-public-beast-v11.1 JSON schema is currently not accepted by tools/import_beastbox.py, which accepts the original beast-cage-creature-v1 genesis format.

Add a separate, strictly validated public Lost COSMOS snapshot path without loosening original deterministic genesis checks. Validate receipt hashes, profile identity/stat/temperament fields, public guest BCG1, exact art sizes/palette, progression ranges and immutable identity. Keep private memory excluded. Make the importer emit a matching content_v11_import_receipt.h proof for subsequent builds and a sanitized display-name macro instead of hardcoding every imported creature name as Miraby.

Exercise export from a legitimately bonded beast through controller UI, parse the actual earned SRAM, then import into an isolated build. Corrupt receipt/profile cases must reject cleanly. This round trip is not yet proved.

## Remaining game polish to inspect

Inspect these actual implementation gaps before calling the full Bible complete:

- Pending inventory rewards currently need a visible 'free a slot' notice.
- Some field utility flags such as Scout, Track and Light need visible/functional field effects.
- Native active-beast field rendering and evolution animation/form changes need review.
- Imported battle positions may overlap the ARIN label; move arena sprites upward if needed.
- Pale King's time skip and Outcast's Stand currently approximate the written mechanics and should be made literal or documented accurately.
- Spawned enemy additions need bestiary encounter recording.

Balance numbers are starting values, as the Bible states; do not disguise missing behavior as tuning.

## Build and verification after recovery

The local ARM/mGBA dependencies are under /workspace/scratch/be5fd7869092/deps/root.

Set PATH to include its usr/bin and LD_LIBRARY_PATH to its usr/lib/x86_64-linux-gnu for every native build and mGBA invocation. From LOST_COSMOS_V10_SOURCE run IMPORTED_BEAST=1 bash build_v5.sh.

Run shared native host-generation suites sequentially because they generate the same host_qa_v5.c. Do not rebuild or replace ROM/ELF while an emulator run is active.

Required current gates include:

- tests/test_content_v11.py
- tests/test_content_v11_native.py, both variants
- tests/test_story_completion_native.py
- tests/test_completion_maps_v10_8.py
- tests/test_act1_pixel_reachability.py
- tests/test_all_story_pixel_routes.py
- tests/test_end_credits_v10_8.py
- tests/test_imported_native.py
- tests/test_save_journal.c
- tests/test_mgba_menu_visual.py
- tests/test_mgba_content_v11.py
- The final-ROM real-controller Act I -> resume -> Act II -> Eldoria -> Hollow Grove save chain.

Preserve original QSEED. Update the cartridge title to the 12-byte COSMOS V11.1 while retaining compatible game/save handling, then use that final unchanged ROM/ELF for verification.

## Delivery checklist

1. Resolve genuine test targeting; finish export round trip and material gameplay gaps.
2. Build the final ROM twice and verify byte identity.
3. Pass native contracts and real-controller gates, including final cold boots.
4. Keep authentic short gameplay recording and sanitized reports/screenshots; exclude actual private SRAM and ledgers.
5. Update tools/package_current_source.py for V11.1, include source catalogs/art and exclude generated host C, binaries, saves and artifacts.
6. Add targeted gitignore rules; update native CI for imported V11.1 and new content gates.
7. Review and commit all uncommitted code/assets; push the development branch without merging PR #20.
8. Produce matching ROM, editable source ZIP, evidence ZIP and concise play/build README.
9. Persist the downloadable artifacts and return their actual download links only after saving succeeds.

This resume document is a record of incomplete work, not release approval or a backup of the inaccessible source.
