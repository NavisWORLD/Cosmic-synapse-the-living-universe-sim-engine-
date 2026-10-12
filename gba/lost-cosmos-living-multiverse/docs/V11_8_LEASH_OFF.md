# V11.8 — LEASH OFF (the field companion roams on its own)

Source: `LOST_COSMOS_V10_SOURCE/leash_state.h` (layout, observation block) and
`LOST_COSMOS_V10_SOURCE/leash.h` (behaviour, save/restore, record page).

This is a measurable behaviour plus a counter log. It is not a claim of
intelligence: the beast runs a fixed priority list over a breadth-first path
on the real collision map, and the record counts what happened.

## Behaviour

LEASH OFF is the default (new games and saves from before V11.8). The beast is
autonomous only when LEASH is OFF, the game is on the surface field
(`MODE_SURFACE`), the room is not the Beast Home (room 90), or in the 3D view.
Everywhere else the V11.7 code runs unchanged.

Each frame the beast picks the first goal that applies:

| id | goal (record page text) | when |
|---|---|---|
| 6 | RETURN (COMING BACK) | the player chose CALL BEAST |
| 4 | ALERT (WARNING YOU) | a new enemy is within 96 px of the beast; it goes to Arin |
| 7 | CHECKIN (CHECKING IN) | it has been more than 160 px from Arin for 1200 frames |
| 3 | NPC (MEETING SOMEONE) | an NPC it has not greeted in this room is within 96 px |
| 2 | POI (SNIFFING A SPOT) | a visible point of interest (door, sign, chest, warp; never secrets or anomalies) within 40 path steps, at most 16 per room |
| 5 | REST (RESTING) | energy below 60; goes to its favourite cell in the room |
| 1 | EXPLORE (EXPLORING) | nearest 8x8-tile cell it has not walked, 3..48 path steps away |
| 0 | IDLE (LOOKING AROUND) | otherwise a short random wander |

Movement is tile centre to tile centre, 1 px per frame (2 px when called),
along the path field. Only `collision == C_FREE` tiles are entered. A goal
times out after 900 frames. If the beast is called and has not arrived after
300 frames (120 if there is no path), it hops beside Arin (counted as
`catchups`). On a room or layer change it is placed beside Arin if its tile is
not open or it is more than 48 px away.

Guarantees (gated by `tests/test_leash_native.py` in all 106 locations and by
`tests/test_mgba_leash.py` under controller-only play):

- never stands in a wall or hazard tile;
- never moves Arin, never collides with Arin, never uses a trigger or talks to
  an NPC for the player, never changes story flags, quest state, inventory,
  credits, keys or XP;
- combat assist only while within 72 px of Arin (LEASH ON keeps the V11.7 rule);
- a call brings it back (native max 435 frames, mean 164, over 106 locations).

## Controls

- PAUSE > SYSTEM > `LEASH  ON/OFF` (row 14): toggles. Turning ON places the
  beast beside Arin and switches back to the V11.7 follower. The game saves.
- PAUSE > SYSTEM > `CALL BEAST` (row 15).
- PAUSE > PARTY > the beast > `DETAILS` opens `BEAST // FIELD RECORD`
  (page 50); A on that page calls the beast, B goes back.
- The 3D view HUD shows `LEASH OFF CELLS n SPOT n`.

There is no dedicated field button: every field button and chord is already
used (L potion, R magic, SELECT beacon/dodge). The beast also checks in by
itself (goal 7).

## SRAM: the LCL1 field record

Battery SRAM bytes **7296..7815** (520 bytes), inside the journaled main page
(0..8191, after COMP at 7168..7295). It is written by every save (before the
journal commit) and read by every load. It is per cartridge: the three
V11 slot copies (25600/27648/29696) do not carry it. All integers are
little-endian.

| offset | size | field |
|---|---|---|
| 0 | 4 | magic `LCL1` |
| 4 | 1 | version = 1 |
| 5 | 1 | flags: bit0 LEASH ON, bit1 record was created when an older save (no LCL1) was loaded |
| 6 | 2 | reserved, 0 |
| 8 | u32 | `moves_ok`: tiles stepped onto |
| 12 | u32 | `moves_blocked`: frames with a goal but no open neighbour on the path |
| 16 | u16 | `cells`: new 8x8-tile cells walked |
| 18 | u16 | `pois`: points of interest reached |
| 20 | u16 | `npcs`: NPCs greeted |
| 22 | u16 | `encounters`: enemies noticed (ALERT) |
| 24 | u16 | `calls`: CALL BEAST used |
| 26 | u16 | `returns`: calls answered by walking back |
| 28 | u16 | `catchups`: calls answered by the hop |
| 30 | u16 | `checkins` |
| 32 | u16 | `no_path`: goals with no reachable tile |
| 34 | u16 | `secs`: seconds spent roaming |
| 36 | 8 x u16 | `done[goal id]`: goals completed, indexed by the goal ids above |
| 52 | 8 x u8 | favourite `loc` |
| 60 | 8 x u8 | favourite `cell` |
| 68 | 8 x u16 | favourite count (0 = empty entry) |
| 84 | u32 | CRC-32 (IEEE, reflected, poly 0xEDB88320, init/xorout 0xFFFFFFFF) of bytes 0..519 with bytes 84..87 taken as zero |
| 88 | 48 x u8 | visited slot `loc` (255 = empty) |
| 136 | 48 x 8 | visited slot cell mask: cell `c` is bit `c & 7` of byte `c >> 3` |

Counters saturate as plain u16/u32 wrap in C; a reader should treat them as
monotonic within one record.

- `loc` id: world 0 rooms are `room & 127`; other worlds are
  `128 + ((world - 1) << 4) + (room & 15)`.
- `cell` = `(tile_y >> 3) * 8 + (tile_x >> 3)` on the 64x64-tile room map, 0..63.
- Visited slots are least-recently-entered; when all 48 are used the slot with
  the fewest walked cells is reused.
- Favourites are a space-saving top-8 of cells where the beast stopped for a
  POI, an NPC or a rest.

Load rules: missing magic, wrong version or a bad CRC -> the record is reset,
bit1 is set and LEASH is OFF. Nothing else in the save depends on LCL1, so a
damaged record never blocks a load.

Reader example (Python):

```python
import struct, zlib
b = open("game.sav", "rb").read()[7296:7816]
assert b[:4] == b"LCL1" and b[4] == 1
crc = struct.unpack_from("<I", b, 84)[0]
assert zlib.crc32(b[:84] + b"\0\0\0\0" + b[88:]) == crc
moves_ok, moves_blocked = struct.unpack_from("<II", b, 8)
cells, pois, npcs, enc, calls, returns, catchups, checkins, no_path, secs = struct.unpack_from("<10H", b, 16)
```

## Live observation block (`leash_obs`)

`static volatile LfObs leash_obs` in IWRAM, 39 bytes; take its address from
the ELF symbol table (`leash_obs`), not a fixed address. It is refreshed every
autonomous frame and holds only what the beast could perceive from its own
tile:

| offset | field |
|---|---|
| 0 | version = 1 |
| 1 | leash_on |
| 2 | called (CALL BEAST pending) |
| 3 | current goal id |
| 4 | loc id |
| 5 | cell_new (1 on the frame a new cell was walked) |
| 6, 7 | beast tile x, y |
| 8, 9 | Arin tile x, y |
| 10 | nearest active enemy, Manhattan tiles, 255 = none within 12 |
| 11 | nearest active NPC, same rule |
| 12 | nearest visible point of interest, same rule (refreshed every 8 frames) |
| 13 | beast energy (shown on its status page) |
| 14..38 | `sight[25]`: 5x5 collision classes around the beast, row major, 0 open, 1 wall (also off-map), 2 hazard |

Perception rule for tooling (e.g. a read-only RAWRPHOS observation bridge):
read only the LCL1 bytes and `leash_obs`. Do not read `lf_dist`, `lf_q`,
`lf_rng`, enemy HP/AI state, triggers, story or quest flags as observations;
those are not things the companion perceives.

## Tests and evidence

- `tests/test_leash_native.py`: host build of the real `leash.h` over every
  location in `artifacts/world_sweep/world_sweep.json`; 3600 frames roaming +
  a call; save round-trip, CRC reject, older-save migration, LEASH ON follow.
  Output `artifacts/leash_native/leash_native.json`.
- `tests/test_mgba_leash.py`: libmGBA, controller input only. Continue an
  earned Act I save, 45 s roam, CALL BEAST, FIELD RECORD page, 3D view, LEASH
  ON/OFF, cold boot, and migration of `tests/fixtures/v11_7_act1_complete.sav`.
  Output `artifacts/mgba_leash/leash_report.json` and screenshots.
