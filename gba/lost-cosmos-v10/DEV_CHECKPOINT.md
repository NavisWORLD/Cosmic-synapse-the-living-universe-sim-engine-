# LOST COSMOS V10 — VERIFIED LOCAL DEVELOPMENT CHECKPOINT (NOT RELEASE)

Owner: Cory Davis. The historical V7, alternate V8, fixed V8 and independently generated V9 are preserved. This branch is based on `feature/lost-cosmos-v8-framed-text-009`; the locally generated V9 was NOT in this GitHub repo at the time of branching. **The complete V10 game-source archive and reproducible delta are local ChatGPT deliverables. They have not been pushed here. Do not claim this branch's documentation contains the playable engine.**

## Local source and reproducibility receipt

- Immutable V8 framed-text C source: SHA-256 `d8c4fab88a8b48358edd1b606880408b0a7b8352bdec2ce0618918658bcf7b78`.
- V10 standalone local C source: SHA-256 `7d2014d57f39a5409709362b5e92a9dc10b83e09f89db139c29c3bd504c4b016`.
- V10 compiled 512KiB native ARM7TDMI cartridge: SHA-256 `5e9038191eafb40a0aa2d0ac5796906dda49722bb76c84af655e7e48108eafdd`; GBA game code `ERV0`.
- Fully reproducible V8→V10 patch tar.xz: SHA-256 `c82d41883affb6ce080fae25ca2d6ea0b61743f915559009d571e7cf886976bc`, 30,300 bytes.
- Patch applied in separate worktree to exact V8 source, rebuilt under separate LLVM ARM toolchain invocation and compared. Exact C and ROM bytes matched.
- Nine local suites PASS: verify_routes, host_qa_v5, v6_slice_tests, v7_campaign_tests, cinema_tests_v51, v8_view_story_tests, v9_riftfall_tests, v10_presentation_tests, v10_heartwood_tests. Native GBA linker/head/checksum verification PASS. These are host/native-build tests, NOT actual current V10 mGBA screenshots or a human five-act playthrough.

## Implemented local V10 preview code

- GBA BG1 pixel-priority and sprite OAM rules to target the Delta player/NPC dialogue overlap, with host hardware register regression and safe separate portraits (actual phone screenshot retest still required).
- Live title menu with NEW GAME / guarded CONTINUE / OPTIONS AUDIO / CREDITS, older-save overwrite confirmation and ten illustrated cutscene cards; playable Brindlemark Elder→Astrid→Mira onboarding persists independently in SRAM.
- Reused legitimate V9 Riftfall four-wave combat, jump/slam, one tameable active creature, five loot tiers and previous compact eight-world/three-ending campaign; no older release replaced.
- Recovered **the full original 47-page private PDF** `In the land of Eridoria.pdf` in owner's connected Google Drive. It includes ~40 pages of original prose and pp41–47 of a game-design appendix; the shorter edited Bible alone is not the entire original. The PRIVATE PDF is deliberately not included in this public GitHub branch and must not be published absent owner permission.
- Authored one physical 64×64 Heartwood Woods map rooted in the original novel pp20–22. Southeast Brindlemark path unlocks after first Heart; distinct forest palette, impassable river and walkable bridge, Spirit NPC, Western Wisdom rune and Eastern Guardian. Resolve encounter by combat or by Ether heal/bond; restore Crystal of Balance at the north shrine, gain rare gear/core, choice and quest flags persist in validated checksum-protected V10 SRAM. Includes **15th in-cartridge original full-screen GBA indexed cinematic**, completed upon crystal restoration.

## Next release gates

1. Take custody of exact existing local V10 full-source ZIP and 30,300-byte V8→V10 delta; do not recreate original V9 from assumptions. Push source on this isolated branch only if able to transfer ZIP/delta accurately, then open a draft PR. Do NOT expose the private novel PDF publicly.
2. Run real current V10 mGBA native boot and capture true title, dialogue screenshot reproducing the iPhone defect, complete opening and Heartwood route, using human-visible screenshots; run independent two-boot SRAM tests. Local mGBA could not be installed here. Prior passing V8 CI is not V10 evidence.
3. Continue actual novel p22 onward: Glacial Grotto and Clarity, Phoenix and Passion, corrupted Eldoria/Thorne, Hollow Grove, Dreamweaver Festival. Create original new traversable levels and scene-by-scene progression, not alternate book pages.
4. Full final Complete Edition needs substantially deeper classes, multi-creature roster, original lore dungeons, unique later boss encounters, original audio and true controller start-to-credits QA for all canonical endings plus Delta device visual acceptance. Nothing above constitutes the finished full V10 game.
