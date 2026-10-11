# Lost Cosmos V11.6: first-person / Mode-7 view (prototype)

A second way to look at the field, built on the Beast Box **Beast Cage** camera
(`apps/beastbox-cloud/components/cage-pocket-dimension.tsx`). The top-down game
is the real game; this view is a reversible lens over the same world.

## Turning it on and off

- **On:** START -> SYSTEM page -> `3D VIEW` (last item, shows `ENTER`) -> A.
  Works on any surface map: Brindlemark, other field worlds, rooms and the
  Beast Home. It is refused (the item does nothing) during cinematics, the
  intro, credits, V11 battles/shops/dialogue/lore/game over, NPC dialogue and
  shops.
- **Off:** SELECT or START. You are back in the top-down view at the place you
  walked to, with the display registers, BG0 map, collision and triggers
  exactly as before (the test hashes them).

SELECT+L was not used as the toggle: SELECT+L is already the bond chord and
every field button has a single-press action, so a menu item is the only way
in that does not change an existing control.

## Controls in the view

| Button | Does |
|---|---|
| UP / DOWN | walk forward / back (B held: run). Movement goes through `move_player`, so walls, water and hazards work as in the top-down view |
| LEFT / RIGHT | turn (18/4096 of a turn per frame) |
| A | switch camera: EYE (first person, beast walking ahead-right of you) / CAGE (the Beast Cage orbit camera behind you, hero drawn too) |
| L / R | tilt (the cage polar angle, clamped to the cage limits 0.35..1.47 rad) |
| SELECT / START | back to the top-down view |

The HUD shows `EYE VIEW` / `CAGE VIEW`, the location and a compass letter on
top, and the controls on the bottom row.

## Beast Cage math in the game

| Cage (three.js) | Game |
|---|---|
| FOV 46 deg | focal length D = 188 px for a 160 px screen |
| camera = zoom*(sin(phi)sin(theta), cos(phi), sin(phi)cos(theta)) around the focus | CAGE camera: R = zoom*8 px, height H = R cos(phi), back B = R sin(phi) |
| phi clamp 0.35..1.47, default 1.05, step 0.14 | 228..958, default 685, step 91 (4096 units per turn) |
| zoom 10.6 | fp_zoom10 = 106 (1 cage unit = 8 px) |
| (no first person) | EYE camera: H = 14 px, B = 0, phi default 1.40 rad |

Rendering: video mode 1, BG2 affine 64x64 (CB2, SB29-30) holds an 8bpp copy of
the BG0 world map (4bpp tiles converted on entry, up to 255 unique tile/palette
pairs, near tiles first). HBlank DMA0 writes BG2 PA-PD/X/Y per scanline and
HBlank DMA1 writes the sky gradient into palette 0. The per-scanline distance
terms are cached per (camera, tilt) so a frame is a few multiplies per line;
the view runs at the full 60 fps in mGBA (120 game frames per 120 emulator
frames, walking or idle). The tables are repeated 4x so a late frame never
lets the DMA run off the end. The beast, hero (CAGE) and NPCs are affine
double-size sprites scaled by distance, nearest first.

## Limits (prototype)

- The canopy/foreground layer (BG SB31) is not drawn in 3D; decor is flat.
- The world is paused while the view is open (NPCs, wild encounters, COSMOS
  chatter): only you and your beast move. Nothing is saved from the view
  itself; moving and then leaving keeps your new position like normal walking.
- Interactions (A on signs/doors) are top-down only; A switches the camera.

## Small fixes in V11.6

- The Brindlemark G5 book star (tile 31,40) was a black-backed tile. It is now
  a road-backed star tile (`V116_MARK_TILES`, tiles 270/271, road or grass
  backing by neighbour), trigger unchanged.
- SYSTEM page footer says `V11.6  OLDER SAVES LOAD`; the arcade page says V11.6.
- COSMOS idle chatter (both the classic buddy lines and the quantum workload
  lines) no longer replaces a line on screen and stays quiet inside the Beast
  Home, so "YOU FILL THE BOWL ..." is followed by "... LICKS THE BOWL CLEAN."
  with nothing in between.

## Test

`tests/test_mgba_first_person.py` (real mGBA, controller input only, no memory
writes or savestates) runs a Beast Box cage import and a Sol starter. It checks
the star tile, opens the view from the menu, checks sky/floor pixels and 120
stable frames at full speed, that the beast is an affine sprite of the same
art beside the player while walking and turning, the CAGE camera and tilt
clamp, that SELECT restores the field state exactly, normal 4-way top-down
movement and the pause menu afterwards, the view inside the Beast Home with
START to leave, that the home beast keeps moving, the care lines, and that the
exported save still holds the Beast Home record. CI runs it on the compiled ROM
and on the Pages ROM (`artifacts/mgba_first_person/`).
