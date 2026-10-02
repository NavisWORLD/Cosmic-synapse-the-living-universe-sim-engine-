# Lost COSMOS V10.8 native art

These are new original game assets authored for Lost COSMOS with OpenAI Codex, as explicit indexed pixel drawings and small hand-designed pixel geometry. No external game sprites, tiles, screenshots, stock artwork or generated illustrations were used as source art. The established species names and world material colors come from this project's existing data. The drawings and their animation poses are new.

The editable source is `LOST_COSMOS_V10_SOURCE/visual_patterns_v10_8.py`. The compiler is `LOST_COSMOS_V10_SOURCE/visual_assets_v10_8.py`; it emits `visual_assets_v10_8.h` and the asset PNGs in `assets/visual_v10_8/`. PNGs with “asset sheet” or “asset atlas” in their name are labeled inspection aids. They are not gameplay screenshots. Every visible game pixel in these PNGs comes from the same indexed source compiled into the header. Enlargement uses nearest-neighbor sampling.

## Art direction

The traveling hero wears an amber swept hairstyle, copper scarf and teal coat, with a dark outline, readable face and silver clasps. There are four facings and four distinct walking poses per facing. The COSMOS companion has an astral ribbon body and four facial expressions. NPCs have four independent silhouettes: archivist, herbalist, sentinel and seer, with two motion poses each.

The wildlife uses different outlines and color families. Each species has three separately drawn evolution forms and two animated poses for each form:

| Species | First form | Second form | Third form | Animated anatomy |
| --- | --- | --- | --- | --- |
| Forgeling | Furnace cub | Plated hearth guardian | Horned solar guardian | Flame horns and furnace core |
| Tidewisp | Spiral droplet | Fin-bearing wisp | Deep-water crest and flowing tail | Fins, crest and flowing tail |
| Rootkin | Leaf sprout and trunk | Thorn shoulders and bark arms | Root-crowned living tree | Leaves and root feet |
| Voidmoth | Velvet winglets | Crescent eyespots | Large star wings and tails | Wing silhouette |
| Skyspark | Storm chick | Hooked-wing raptor | Feathered storm crown | Wings and lightning tail |
| Frost Wolf | Frost pup | Ice mane and antlers | Crystalline guardian | Mane, paws and tail |
| Ember Phoenix | Fire-crested chick | Flared flame wings | Ash-edged long plumes | Wing span and flame tail |
| Hollow Wraith | Small hooded spirit | Drifting mantle | Veiled lantern keeper | Cloak hem and lantern pose |

The environment artwork includes scalloped oak and hanging willow crowns, a tiled-roof cottage with mullioned amber windows, weathered masonry, moss, rock-framed whitewater, faceted crystals, an anvil and furnace, branched coral, a domed observatory, plank bridge, terrain variants, path edges and small props. All set pieces are built at native resolution from multiple 8×8 tiles. They are not downsampled paintings.

## Header interface and memory limits

The header uses the existing `u8`, `u16` and `u32` typedefs. It defines data only and performs no VRAM writes. Pixels are 4bpp, with the leftmost pixel in the low nibble. 16×16 object data uses the GBA's 1D tile ordering: top-left, top-right, bottom-left, bottom-right. One object frame occupies four 8×8 tiles, 32 words, or 128 bytes.

| Symbol | Shape | Purpose |
| --- | --- | --- |
| `V108_TILES` | 32 × 8 words | Existing semantic tile IDs 0–31 |
| `V108_BG_EXTRA` | 192 × 8 words | Extra tiles uploaded at BG64–255 |
| `V108_BG_ANIM` | 6 × 4 × 8 words | Water, lava, hazard, plant, foam, furnace |
| `V108_ANIM_TILE_TYPES` | 6 bytes | Tile IDs associated with those animations |
| `V108_PLAYER` | 16 × 32 words | Up, down, left, right; four poses each |
| `V108_BUDDY` | 4 × 32 words | COSMOS expressions |
| `V108_ENEMIES` | 6 × 32 words | Glitch, ember, tide, bloom, void, crown |
| `V108_ENEMY_PALETTE` | 6 bytes | Matching enemy palette banks |
| `V108_NPCS` | 8 × 32 words | Four kinds, two poses each |
| `V108_SPECIES` | 8 × 3 × 2 × 32 words | Species minus one, stage, animation frame |
| `V108_BG_PALETTES` | 8 × 12 × 16 colors | Eight worlds; BG banks0–11 |
| `V108_OBJ_PALETTES` | 15 × 16 colors | Native OBJ banks0–14 |
| `V108_DECORS` | 11 descriptors | Base tile, width, height, palette and source semantic |

BG foreground tile IDs40–43 and the font in character block1 remain reserved. Extra assets64–255 consume6,144 bytes and stay entirely in character block0. BG palette banks12–15 remain for the HUD and menus.

The hero's sixteen frames require64 OBJ tiles. The established first32 tiles only hold eight legacy frames; uploading all sixteen there would overlap other objects. A complete hero page fits at OBJ576–639, immediately after the creature page384–575. The imported identity's OBJ tiles640–895 and palette15 are excluded from this package and remain reserved.

| BG stamp | Base | Tile dimensions | Pixel dimensions | Palette |
| --- | ---: | --- | --- | ---: |
| Oak | 64 | 4 × 4 | 32 × 32 | 3 |
| Willow | 80 | 4 × 4 | 32 × 32 | 3 |
| Cottage | 96 | 6 × 5 | 48 × 40 | 6 |
| Ruin arch | 126 | 4 × 4 | 32 × 32 | 4 |
| Waterfall frame0 | 142 | 3 × 5 | 24 × 40 | 2 |
| Waterfall frame1 | 157 | 3 × 5 | 24 × 40 | 2 |
| Crystal spire | 172 | 3 × 3 | 24 × 24 | 5 |
| Forge | 181 | 4 × 3 | 32 × 24 | 6 |
| Coral | 193 | 3 × 3 | 24 × 24 | 3 |
| Observatory | 202 | 4 × 4 | 32 × 32 | 6 |
| Bridge | 218 | 3 × 2 | 24 × 16 | 6 |
| Terrain variants | 224 | Sixteen tiles | Four grass, floor, path, ruin variants each | Semantic material |
| Path edges | 240 | Eight tiles | Top, right, bottom, left, NW, NE, SE, SW | 1 |
| Props | 248 | Eight tiles | Sign, lamp, flowers, moss rock, shrine, crystal, shell, slab | `V108_PROP_PALETTE` |

The opaque ground surrounding stamps uses palette index9. Index10 is the ground shadow and index11 the ground fleck color; this avoids black gaps when placed on the main background plane. Scenic stamping must preserve the existing collision and trigger grids. The descriptor's `source_tile` is placement metadata, not an instruction to change collision.

## Palettes

The first four colors of BG material banks0–7 retain the established world's material ramps. Index0 is transparent. Indices5–8 supply a secondary material ramp, including bark in foliage palettes and blue roof tiles in architecture palettes. Indices9–12 supply ground, ground shadow, ground flecks and accent colors. Index13 is a dark outline,14 a pale glint and15 a warm light. The four shaded banks8–11 retain their established first-four-color ordering while adding corresponding secondary ramps. The compiler stores all colors directly as GBA RGB555.

OBJ palette0 belongs to the hero;1–4 to COSMOS moods;5–12 to species1–8;13 and14 to NPCs. The NPC mapping is `13 + (kind & 1)`. All species use `4 + species`, including frost wolf, phoenix and wraith. The full palettes must be installed: the legacy seven populated colors cannot represent these new drawings. Palette15 belongs to the imported companion and is never emitted here.

## Reproduction and verification

From `LOST_COSMOS_V10_SOURCE`:

```sh
python3 visual_assets_v10_8.py
python3 visual_assets_v10_8.py --check
```

The check validates every indexed pixel and RGB555 color, exact 4bpp encode/decode round trips, the BG and OBJ limits, unique hero frames,48 unique creature frames, distinct silhouettes for each of the24 evolution forms, anatomical differences between paired animation poses, four unique frames for every animated material, and byte-for-byte header reproduction. `assets/visual_v10_8/asset_manifest.json` records tile allocation, dimensions and SHA256 hashes of the source and generated header. Native PNGs preserve original pixel dimensions for direct editing and inspection; the Python pattern source remains the compilation authority.
