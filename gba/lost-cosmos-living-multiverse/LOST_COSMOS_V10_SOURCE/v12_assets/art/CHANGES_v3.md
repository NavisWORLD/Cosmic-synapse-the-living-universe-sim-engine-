# Cosmo GBA art v3

Source: `cosmo_src/` (build.py, common.py, creatures.py, mote.py, humans.py, items.py). Rebuild: `cd cosmo_src && python3 build.py`
(GBA_OUT env sets the output dir; default /home/box/backups/lost_cosmos/gba_v3/art). Inputs: /workspace/lost_cosmos_art/zeref_reference.png,
bb-main living-core cutouts, /workspace/lost_cosmos_text/*.json.
Dry run of tools_v12/convert_v12.py (d8462353) on a scratch copy: exit 0, art bytes 311008, 65 items, no missing icons.

## Changes vs v2
1. **creature_zeref**: frames 6-11 are now a real 6-phase 4-leg walk cycle (legs redrawn under the side pose, alternating diagonal pairs, pink pads).
   react_dark (12-15) has 14 orbiting stars per eye (white/pink) and a radial iris glow.
2. **creature_kairo/frost/kitten/shardhowl/velvetcoil**: v2 contrast prep + pulsing neon outline (6 idle + 6 walk).
   **companion_***: redrawn: spiders get jointed alternating-gait legs, eight eyes, abdomen glyph. Jellies get a pulsing bell, rim lights, and a blush-eye blink. 4 idle + 4 walk.
3. **NEW `sprites/wisp_dark.png`** (32x32, 6 frames: drift x4, lunge x2 with red eyes and teeth) + `palettes/wisp_dark.*`. Not yet referenced by convert_v12.
4. **char_* (14 humans/NPCs)**: bigger 12px heads, 3-tone shading, hair styles, aprons/belts, ground shadows, and per-character creepy beats.
   Hesper is now a standing ice-blue hooded sentinel: silver plate, spear, legs and shadow, wing-tip eyes, cyan eyes.
   The Counterfeit Angel floats with no outline, no shadow and no legs, has a gold halo and pale aura, and its smile never changes.
5. **Items use 2 palette banks**: `items.pal` = bank A (consumable/food/material/armor/accessory), NEW `items_b.pal` = bank B (weapon/lantern/key).
   Sheet PNGs carry a 32-colour palette (bank A = idx 0-15, bank B = idx 16-31). NEW `sprites/items_palette_map.json` lists the bank per item.
6. **char_mote_still_here**: ears have a lavender rim and pink inner ear, and the feet are rimmed, so it reads on dark BGs.

## Notes for Phera (converter, no code touched)
- convert_v12 nearest-maps ALL item sheets to `items.pal`, so bank-B icons (weapons, lanterns, keys) come out colour-approximated.
  To use the banks: load `items_b` too and use `pixel_index & 15`, with the palette chosen by `items_palette_map.json`.
- The converter still takes only frame 0 of `char_*` and Mote sheets; all 10 frames are in the PNGs.
- `wisp_dark` needs an entry if wanted in the ROM.

## v3b (00:45 CT) — Cosmic Studio concept pass
- **char_mote / char_mote_linework / char_mote_wash / char_mote_still_here** (+ their palettes) redrawn to match `lost_cosmos_art/mote_evolution_concept.jpg`. Same filenames, 64x64, same 10-frame layout (idle0-3, sneeze_stars, yawn_teeth, walk0-3); the yawn is still an idle frame.
  - Mote: fluffy white puff, teal eyes, round ears. Sneeze sprays star sparkles upward; the yawn is a giant toothy mouth.
  - Linework: spiky white fur, pointed ears, hollow dark eyes (right one with a violet glint), purple tear streaks, curled tail, star-sparkle paws. The extra forehead eye opens on idle1, idle3 and walk2.
  - Wash: lavender fluff, 4 teal eyes, bat wings, glowing teal chest gems, shadow a beat late.
  - Still Here: big dark cat silhouette with a rainbow rim (the ears are rimmed too), starfield, ringed planet, potion, telescope, small teal eyes low on the body.
- **bg forest/cave**: palettes `bg_forest.*` / `bg_cave.*` (and the map/tileset PNG colours) retuned from `world_concept.jpg`: indigo night, violet canopy, moss, teal glow; deep-navy cave with cyan/blue crystals and violet rock.
  Same 512x256 maps, same slot roles. Tile counts unchanged: forest 188, cave 138.
- Mode-4 scenes, scene palettes, mockup and contact sheets rebuilt. New preview: `preview/mote_forms_v3b_x3.png`.
