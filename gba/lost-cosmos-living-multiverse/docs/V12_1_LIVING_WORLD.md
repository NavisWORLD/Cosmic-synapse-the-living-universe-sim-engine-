# Lost COSMOS V12.1 LIVING WORLD (Cosmo GBA art v3b)

Additive on V12.0. Same 16 MB cart, game code, web-import (LCX1/LCM1/LC11) formats.

## Changes
- Art: Cosmo GBA art v3b (redrawn Mote forms, recoloured forest/cave, Zeref 4-leg walk
  cycle, react_dark with orbiting eye stars, redrawn companions, stronger cast).
- Converter `tools_v12/convert_v12.py`:
  - item sheets use their 32-colour bank palette (`pixel & 15`), with `items_b.pal`
    (weapons, lanterns, keys) chosen per item from `sprites/items_palette_map.json`
    (`V12_ITEM_BANK`); bank A still uses `items.pal`.
  - all 10 frames of every `char_*` and Mote sheet are converted.
  - `sprites/wisp_dark.png` (drift x4, lunge x2) replaces the code-drawn wisp.
- Game (`living_world.h`):
  - the wisp drifts on frames 0-3 and lunges on 4-5 when it is near Zeref.
  - Arin idles (0-5) and walks (6-9) with the player and faces left/right.
  - One cast member lives in each world: Mote (64x64) wanders the forest, stops to
    sneeze stars or yawn; Rime (32x32) wanders the cave.
  - CAST page animates: Zeref idle / 4-leg walk / react_dark, Mote idle / sneeze /
    yawn / walk, humans idle / walk.
  - STATS honest label fits the screen: `DNA: RECORDED IBM QSEED DATA`.
  - Item stat line no longer overlaps the category name.
- Save: V12.0 kept the Living World block at SRAM 16384, which is inside journal
  bank 1 (16384..24575) and was overwritten by journal commits (and corrupted that
  bank's CRC). V12.1 stores it at 7936..8191, the free tail of the journaled main page,
  so it is now journaled. A valid V12.0 block is migrated once; 16384 is never written.
  Layout and checksum are unchanged.
- Not done: the V11 slot copier (LCM1) payload has 128 spare bytes; the 256-byte block
  does not fit without changing the slot format, so it stays shared by all slots.

HONEST LABEL unchanged: creature life is a classical simulation seeded by recorded IBM
QSEED values. Nothing quantum runs on the GBA. bb-deada969 (Zeref) and bb-7f9c2a03 stay
separate.

## Test
`tests/test_mgba_living_world.py` (mGBA, controller only) now also checks Mote walking,
sneezing and yawning, wisp lunges, the STATS label row, and the block at SRAM 7936.
