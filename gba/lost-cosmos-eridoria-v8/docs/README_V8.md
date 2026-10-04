# LOST COSMOS V8 — Eridoria, readable depth + story interface

**Native Game Boy Advance ROM**, not a GBC port or 4K/true 12-dimensional simulation. This is a visual-accessibility and authored-story expansion on the verified V7 eight-world campaign. Previous editions remain intact.

### Improvements

- **8 independently authored biome sets of eight real semantic material palettes**: terrain, paths, water/lava, foliage, masonry, crystalline signal, buildings, danger. Four extra shaded material banks create dimension without reducing terrain contrast.
- **12-component integer fixed-point visual projection** feeds a sparse BG2 foreground parallax layer and selective terrain shading. Never consumes new workload bytes or changes gameplay authority. UI is always BG1 with dark opaque matte, framed dialogue and a colored, one-pixel extruded 5x7 font.
- Corrects an older **XP formatter bug**: 10,000+ XP now renders decimal digits instead of invalid font symbols.
- 30 authored unlocked story pages across all **five acts**, exact dynamic current quest objective in the HUD, Story and Eridoria Journal. Main progression, all eight worlds, existing NPC/trader/monster/ship systems and ending remain preserved.
- **Four save-persistent character identities**: Smith, Ranger, Mystic, Warden with small real gameplay bonuses and distinct player colors. Enhanced Items and Equipment panels show actual item effect, quantities, credits and effective stat totals. Historical V2–V7 data is not overwritten when migrated; V8 role extension lives in unused bytes 208–210 and includes its own checksum.

### Controls

START opens menu. Select **STATS** then press **R** to choose character identity with D-pad and A. Select **ERIDORIA** then **R** to open the 30-page STORY BOOK; use left/right to turn pages and B to return. On **STORY**, R also opens the book. Inventory displays selected item's actual effects. The optional Delta-friendly TOUCH MODE is under Settings.

### Build/test

Run `bash build_v5.sh` (historical script filename), `python3 verify_routes.py`, `python3 host_qa_v5.py`, `python3 v6_slice_tests.py`, `python3 v7_campaign_tests.py`, `python3 cinema_tests_v51.py`, `python3 v8_view_story_tests.py`. The resulting ROM is `LOST_COSMOS_ERIDORIA_V8.gba` with game header `ERV8`; base SRAM remains `LCV5` on purpose for compatibility. It is a distinct Delta library game and save import from V7 is **not automatic**. Back up saves before testing.

See `ERIDORIA_V8_CHRONICLE.md` for the in-game text and precise playable-vs-planned five-act campaign scope; see `V8_VIEW_PROJECTION.md` for the mathematical projection and hardware constraints.