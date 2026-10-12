# Lost Cosmos V11.7: Act I "The First Heart" (Q05-Q09)

The campaign quests continue from the V11.6 prologue (Q00-Q04). The dialogue is
all original game text. No manuscript text is in the source.

## Route

| Quest | Where | What the player does |
|---|---|---|
| Q05 OAKWOOD'S LOST MAP | Brindlemark NE road -> Oakwood (room 3) | Meet Lord Ravenswood. At the inn, Pell the courier is hurt. Bring a potion: buy it from the trader, or Bree gives one. Pell remembers the split oak (row 4, tree 3, tile 14,24). The map case is in the crack. |
| Q06 RAVENSWOOD'S WORD | Oakwood | Return the map. Read Aurel's journal at the desk (36,14). Ravenswood then opens the Cragstone east gate (54,12). |
| Q07 CRAGSTONE RUNES | Ascent (91), Gallery of Blades (92), Keeper's Vault (93), temple hall (4) | Climb the ascent past the glitchlings. **Gallery:** three stone sentries. Their stone skin ignores field hits, so duel them with SELECT+A and parry with B to earn the guard seal. **Cold vault:** take the key mould from the north pedestal and ore from the south vein. Cast the key at the cold forge with a timed-heat minigame (three good strikes). Open the vault door to take the Rune of Keeping. **Temple hall:** light the four sockets in the order taught by the seals (2,0,3,1). The Heart door (32,9) stays sealed until then. |
| Q08 STONE REGENT | Heart chamber (94) | **Boss.** HP is 48+4*level. Its core cycles STONE / EMBER / TIDE and the HUD shows WEAK TO. A parried slam opens the guard on the STONE core only. Elemental cores need the matching counter spell, which staggers it. **FIGHT:** wear it down. **RESTORE (peaceful):** while it is open or staggered, use RESTORE three times. That needs COSMOS trust of at least 110, or an active party beast with bond 40 or more. Losing resets the fight; it never soft-locks. |
| Q09 THE FIRST AXIS | Heart chamber | Malakar arrives and argues for sealing the worlds. Your reply is saved. The options are "no erasing" and "who decides". His lance strike is a timed deflect minigame, and then he retreats. You receive the Heart of Eridoria (ST_HEART), the first axis, cores, trust and XP. Q10 HIDDEN CITY is activated. |

The rewards are real inventory and stats: XP at each step, potions, shards and
cores, credits on the fight route, and trust. The Oakwood market prices depend on
the prologue choice. The inn rest costs 3 credits and saves the game.

## State and saves

- The Act I block is in the LC11 save page (SRAM 6400, bytes 728-735). It holds
  a1_flags, the Regent outcome (1 fight, 2 restore), the Malakar reply, and the
  sentries beaten.
- **Older saves load.** A V11.6 save that is past Q04 is migrated from its
  story_flags. Q00-Q04 are marked done. A save that already has ST_HEART keeps
  the Heart, with regent=1. The migration flag is set.
- Fixtures: `tests/fixtures/v11_6_*.sav` (see `README_V11_6_SAVES.md`).

## Tests (all run in CI)

- `tests/test_mgba_act1_heart.py`: a controller-only libmGBA playthrough from an
  earned prologue save to the end of Q09. It then cold-boots, continues, and
  checks the state. CI runs two routes:
  - restore with reply 0 on the compiled ROM;
  - fight with reply 1 on the runtime handheld ROM.
- `tests/test_mgba_act1_migration.py`: the three V11.6 fixtures.
- `tests/test_mgba_world_menus.py`: continues the Act I save. It opens every pause
  page, including the QUESTS STORY view, where Q05-Q09 show COMPLETE. It saves to
  slot 3 from SYSTEM > SAVE GAME, then enters and leaves the 3D VIEW in Oakwood.
- `tests/test_world_sweep.py`: covers every generated map using the real game code
  on the host. Each location is built and flood-filled with the 10 px
  footprint. Every reachable door, warp and lift is used through
  interact()/v11_field_interact()/shift_layer().
  - **Checks:** every arrival is standable (no fake destination), every room has
    a working exit, and every room in the universe list is entered in at least
    one pass.
  - **Passes:** fresh campaign, all-open, and progression seeds for ARC, G7,
    completion and V11.
  - **Result:** 106 locations, 0 problems.
  - Locked doors refuse with the game's own reason, for example "THE CRAGSTONE
    GATE IS LOCKED. LORD RAVENSWOOD HOLDS THE KEY." The sweep records these.

## Known limits

- The Stone Regent reuses the crown-sentinel sprite tile. Dedicated art is still
  to do.
- ROM space: about 40 KB is left of 1 MB. Acts II-V will need text compression
  or a larger ROM.
