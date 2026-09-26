# GBA V8 — 12-component visual projection, not 12D hardware physics

All projection math is **classical, deterministic, integer fixed-point code** on GBA's ARM7TDMI. It is inspired by the existing `state12` software architecture and recorded quantum-derived workload input; it does not assert mathematically verified 12-dimensional physical space. The qseed payload remains exactly 8192 bytes with the inherited checksum and is never consumed by rendering, sound or text.

## The twelve visual axes

Define `v=(x/32, y/32, world*6, layer*11, qmean/16, qspread/32, trust/32, curiosity/32, avoidance/32, 3*keys, 4*has_memory, 7*indoor)` after integer quantization. For the world scroll camera `c`, the dedicated BG2 foreground uses

`parallax_x = c_x/4 + (dot(v, kx) >> 5)`

`parallax_y = c_y/4 + (dot(v, ky) >> 5)`

with bounded signed integer coefficients `kx,ky` in the source. BG0 remains the original 64x64 collision/quest terrain, BG1 stays a high-contrast, dark, fully opaque UI, and BG2 is a sparse transparent 32x32 scrolling foreground using only three 4bpp tiles (canopy, angled shadow and glints). Cinema temporarily owns BG2 and palette bank 5; on exit, the correct map and material bank are restored. No dynamic VRAM reallocation is required during gameplay.

An additional twelve-input integer dot product uses terrain location, tile kind, biome, layer and bounded character/workload summary to select one of four material shade banks, each associated with a biome-specific semantic material. This is an **illusion of soft depth and colored regions**, not polygonal 3D or a proof of CST. No render routine changes collision, quest decisions, stats, tape cursors or QSEED bytes.

## Native palette budget

GBA Mode 0 4bpp maps use 16 possible background banks × 16 entries. Banks 0–7 are distinct soil, trail, liquid/heat, foliage, masonry, signal, architecture, corruption. Banks 8–11 are shaded variants for specific materials. Bank 12 is reserved. Banks 13–15 are invariant readable UI gold/cyan/white with dark matte and glyph shadows. Cinematics temporarily share bank 5; the previous material palette is restored afterward. Player OBJ palettes are independent and follow the four chosen hero color schemes.

## Practical visual limitations

240x160 native rendering, not 4K. This implementation keeps a bounded CPU/VRAM footprint and does not touch the GBA's expensive bitmap modes. Human aesthetics and Delta inputs require physical iPhone playtesting; scripted CI confirms only the emulator path and automated invariants it exercises.