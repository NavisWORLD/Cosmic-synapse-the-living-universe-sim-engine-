# LOST COSMOS V10 — VERIFIED LOCAL DEVELOPMENT CHECKPOINT (NOT RELEASE)

Owner: Cory Davis. Historical V7, V8 and independent V9 remain preserved. Branch is based on `feature/lost-cosmos-v8-framed-text-009`. **This GitHub branch currently contains the checkpoint, not the actual locally generated V10 full source.** Locally generated V9 never reached the repo. Do not claim this remote branch is a buildable full V10 checkout until the tested full-source archive or exact patch is transferred accurately.

## Verified local artifact hashes

- Canonical V8 post-framed-text source C SHA256 `d8c4fab88a8b48358edd1b606880408b0a7b8352bdec2ce0618918658bcf7b78`.
- Compiled V10 C SHA256 `7d2014d57f39a5409709362b5e92a9dc10b83e09f89db139c29c3bd504c4b016`.
- Exact native ARM7 GBA SHA256 `5e9038191eafb40a0aa2d0ac5796906dda49722bb76c84af655e7e48108eafdd`, 524288 bytes, cartridge code `ERV0`.
- Final canonical V8→V10 source delta tar.xz SHA256 **`e65744c7f03a75c1babe083f4d6840867dd745373c9cf050727847a3e342b90c`**, 30244 bytes, 9 files, no self-embedded tarball. This is in the downloadable complete editable source package returned to owner.
- On a separate V8 source checkout, exact delta applied cleanly; independently rebuilt source AND GBA match the hashes above byte-for-byte.
- Nine local tests PASS: `verify_routes.py`, `host_qa_v5.py` (two host SRAM boots), `v6_slice_tests.py`, `v7_campaign_tests.py`, `cinema_tests_v51.py`, `v8_view_story_tests.py`, `v9_riftfall_tests.py`, `v10_presentation_tests.py`, `v10_heartwood_tests.py`. Native linker/header verification PASS.

## Implemented locally in V10 game source

- Corrects game-world object OAM priority behind opaque BG1 dialogue; original user's iPhone screenshot visual retest is still necessary. Separate priority-0 portraits remain outside the dialogue box. Four actually interactive title options, safe new-game confirmation, ten illustrated prologue cards (with optional skip), persistent Brindlemark Elder/Astrid/Mira onboarding.
- Preserves eight-world condensed V8 campaign, older quests/30-page chronicle, three broad ending choices, V9 4-wave Riftfall, jump/smash, one V9 bonded monster and five loot tiers. No previous release erased.
- Recovered original author's private **47-page `In the land of Eridoria.pdf`** from owner's connected Google Drive. It contains literary prose (~pp1–40) plus separate game-design appendix (~pp41–47). The short edited Eridoria story bible was NOT the complete original. **Do not push the private PDF or full literary text to GitHub without the owner's separate explicit authorization.** Local owner-only scene matrix references pages and distinguishes implemented from absent scenes.
- **Heartwood Woods original playable new 64×64 physical map**, accessible off southeast Brindlemark road after acquiring Heart. Forest palette, impassable river and walkable bridge, separate rune and elite guardian arena, guide NPC, combat route OR ether healing/bonding option, Crystal of Balance with core/gear reward and choice-specific persisted/checksummed SRAM. **15 original in-cartridge GBA 4bpp cinema frames**, including original Heartwood restoration, Brindlemark forge and siege.

## Explicit next gates

1. Transfer exact owner-facing local full editable V10 source ZIP/delta (above hashes) into this branch when the available GitHub connector supports verified file transfer. Open draft PR only when actual source is present; avoid placeholder PR claiming a complete game.
2. Run actual V10 mGBA hardware-model boots and inspect title, dialogue screenshot, prologue, Heartwood combat/healing and reload screenshots. mGBA not locally installed/accessible here; past V8 CI screenshots are NOT current V10 evidence. Request independent Delta iPhone visual retest from player.
3. Author actual playable Glacial Grotto, Phoenix/Clarity/Passion, Thorne Eldoria, Hollow Grove, Dreamweaver Festival and remaining 47-page manuscript scenes, plus deeper classes, creature roster, original music and actual distinct postgame consequences. Finish genuine controller start-to-credits playthrough, all three endings, performance and real user acceptance before saying COMPLETE EDITION.
