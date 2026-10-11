# Lost Cosmos V11.5: BEAST HOME and a native graphics pass

## Beast Home (world 0, room 90)

A cottage on the west side of Brindlemark (door at tile 8,28, just north of the
main road). Walk up and press A on the door. The beast that lives there is the
**active party creature**: the Sol starter from the Lost COSMOS nursery, a
creature brought in from Beast Box through the existing bridge (mailbox/cage
save), or a wild bond. If the party is empty, the door says so and stays shut.

Inside, the room is one still screen (the camera holds on the whole room):

| Thing | Where (tile) | A does |
|---|---|---|
| Food and water bowls | 22,24 / 23,24 | FEED: the beast walks to the bowl, eats (food emote), **FULL +40** |
| Ball | 24,32 | PLAY: the beast runs to the ball and hops about (note emote), **JOY +30**, REST -10, FULL -5 |
| Bed | 36-37,24-25 | REST: the beast curls up on the bed (Zzz emote), **REST = 100** |
| The beast itself | anywhere | PET (A next to it, nothing else in reach): hearts, **JOY +10** (a short cooldown after) |
| Plaque | 29,22 (wall) | Reads the record: name, FULL, JOY, REST, VISITS, CARE |
| Door | 29,36 | Back to Brindlemark |

Every completed care action also adds **+1 bond** (max 100) to that creature and
saves. Between actions the beast lives on its own: it idles with a small bob,
trots to random spots around the room, and goes to bed by itself when REST
drops under 20. FULL/JOY/REST drift down by one point about every 20 seconds
while you are home. The HUD shows the name, what it is doing, and the three
needs. The beast is drawn with the same art as the field follower: native
species tiles, imported 32x32 field art, or the Sol starter art.

### Identity and saves

Care is kept per creature identity (`LcCreature.identity`), so the same beast
is recognised on every visit and after save/load, and a different active beast
gets its own record. Records live in LC11 page bytes 676-727. They were unused
(zero) in every V11.0-V11.4 save and sit inside the existing LC11 CRC (0-763),
so the manual slots copy them too.

- 676 'H', 677 schema 1, 678-679 reserved
- 680 + 12*n (n = 0..3): identity u32, fullness, joy, rest, visits, care count u16, flags, pad

Older saves have no 'H' marker and start with no records. Saving inside the
home stores room 90, so CONTINUE puts you back in the home with the same beast.

## Graphics pass (all within the existing 4bpp tiles and palettes)

- **Roads**: the road-edge picker read neighbours that had already been
  repainted in the same pass, so one-tile roads got random top/right or
  bottom/left edge tiles (the "planks" look). It now treats painted road tiles
  as road and picks by which sides meet grass: horizontal strip, vertical strip,
  or top/bottom/left/right edge of a wider road. The eight edge tiles were
  redrawn: grass lip with a soft shadow on the lit side, packed earth, a light
  rim on the far side. Road interiors are calmer packed earth.
- **Grass**: the base grass and its four variants were redrawn from a speckle
  on every other pixel to one small tuft or blade pair per tile.
- **Flowers**: the flower tile now sits on the shared ground green (slot 9) with
  white, gold and magenta petals, so it matches the grass whatever bank places
  it. The darker "shade" banks keep slots 9-11 exact for this reason.
- **Field clutter**: world 0 grass no longer gets tan dust squares or copper
  lantern squares; a lantern prop drawn on grass is used instead. The foreground
  bush overlay is a shaded shrub in the grass colours instead of a bright blob.
- **Beast Home art**: 14 new BG tiles at CB0 256-269 (wood floor, bed, bowls,
  ball, rug, window, plant, plaque, mat) and four 16x16 care emotes (heart,
  note, Zzz, food) at OBJ tiles 992-1007 with their own palette (OBJ 12, which
  the Spark field does not use inside the home).

Art source stays in `visual_patterns_v10_8.py`; `visual_assets_v10_8.py`
regenerates `visual_assets_v10_8.h` (`--check` validates it).

## ROM header

The cartridge title now reads `COSMOS V11.5` (it said `COSMOS V11.2` since
V11.2). The game code (`ERL8`), save type and SRAM layout are unchanged, and the
web player and mGBA key saves by file, not by header title, so existing saves
still load.

## Tests

`tests/test_mgba_beast_home.py` (CI release gate, compiled and Pages-style ROM):
two cases, the Beast Box cage import (CHARLET) and the Sol starter (CINDERKIP).
Controller input only: new game, walk to the door, go in, watch the beast move
on its own, FEED, PLAY, PET, REST (each checks the spot it walks to, the stat,
the care count, the bond and the on-screen emote), read the plaque, leave, come
back (visit 2, same record), export the save, cold boot, CONTINUE: the same
identity is home with the same record and bond, and it is moving.
`--record` also captures native video and audio.
