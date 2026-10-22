# Lost COSMOS V12.3 (branch feature/lost-cosmos-v12.3, NOT shipped: waiting on Cory)

Honest label unchanged: classical CST-12 simulation seeded by recorded IBM QSEED data; any Rigetti input is SIMULATED (QVM).

## Canon pass (Emeth, /workspace/lost_cosmos_text, CHANGES_canon.md)
- Item ids renamed: moon_berry→glowcap, void_jerky→golden_wheat, twin_pistol→fiddle_bow; star_candy merged into star_shard. New bible items kneaded_eraser, courage_petal, unity_petal, crys_earth, small_branch (they borrow the nearest existing icon until Cosmo draws theirs).
- **Save migration:** the LW block's byte +3 is now a layout version. 0 = V12.0–V12.2 ids. These are remapped once on load (`V12_ITEM_MIGRATE`, star_candy counts are added to star_shard, equipped items are remapped too). 1 = V12.3. Items 68 and up live at LW+168 (free tail). The checksum rule is unchanged.
- **Journal fix:** the LW block sits inside the journaled 8 KiB page, so V12.1–V12.2 lost Living World progress on every cold boot made after the last game save. Each LW save now patches its 256 bytes into the latest committed bank and re-seals that bank's CRC. Game state is untouched.
- 5 Mote forms: Smudge, Linework, Shading (new, Cosmo's char_mote_shading) and Wash, plus Ink (the sprite file char_mote_still_here maps to mote_ink). CAST shows "FORM n OF 5".
- 6 bible characters (Lord Ravenswood, Spirit of Harmony, Dusk Keeper, Tibbet, Dreamweaver, Fairy Host) have stand-in portraits, and CAST labels them STAND-IN ART. A duplicate mote_ink in characters.json is de-duplicated.
- NPC renames star_frog→frog and sock_merchant→old_pell (npc_lines). Quests show the bible biome and location.
- Secret ending D "The Passenger Seat": requires the crown ending, Zeref at bond 100 (the cartridge's maximum; the bible says 150) and 12 corner_sketch. It unlocks once, grants last_map, and is remembered at LW+164.
- creature_moods `synapse_mood`: the spoken line now comes from a mood whose synapse_mood matches the creature's live CST-12 top mood. The trigger still picks the action.
- Acts II–V scene dialogue (355 boxes from act2–act5_scenes.json). On QUESTS, press SELECT to read them. Bosses with no art yet show "BOSS ART PENDING".

## Boss battles (`boss_battle.h` logic, host-tested; glue in living_world.h)
- QUESTS → A on q2_03/q2_04/q2_05/q2_06 starts a fight. It is labelled practice while the quest is locked.
- One 2 KB frame (64 tiles, 4bpp) is streamed per tick by DMA3 into OBJ tiles 0–63. Each boss has its own palette slot: Grumbleback 9, Forest Guardian 10, Statues 11, Moth Swarm 12.
- Each attack telegraphs on its windup frames. The strike lands on frame 2, and the last frame stays open for a hit. A phase takes 3 hits, then the grow animation plays. Later phases are also drawn bigger (affine 1.0/1.25/1.5×).
- Grumbleback v2.1 (index 14 violet) has 3 phases and ends hum_calm→defeat_attuned. The Forest Guardian (replaces hollow_stag) has 2 phases. The Moth Swarm has 2 phases, its storm is the grow animation, and the lantern is baked into its frames.
- The Guardian Statues use Cosmo's sheet and lane art. There are three 32 px lanes, each built from two 16 px warning tiles. Per sweep: dim 12f, warn 36f (24f in phase 3), windup 12f, imminent 8f, swing 12f (hitbox live on the last 9f), after 8f, recovery 12f. That gives ≥59f of warning and always leaves one safe lane. Phase 1 sweeps one lane, phase 2 sweeps lanes 0 and 2, phase 3 sweeps any two.

## Tests
host: tests/test_boss_battle_host.c, test_cst12_host.c, test_ecosystem_bridge_host.c, host_qa_v5.py, test_content_v11(_native), test_leash_native, test_world_sweep, test_bridge.
mGBA: tests/test_mgba_v12_3.py (migration of a save made by the real V12.2b cartridge, cold-boot persistence, all four bosses won by controller, scenes, cast). With SITE_LC=<site lc-ecosystem.mjs>, test_mgba_first_person checks that the cartridge applies the site-built LCQ1.
