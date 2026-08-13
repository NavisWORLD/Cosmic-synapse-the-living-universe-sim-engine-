# Changelog

## 7.08 — 2026-08-12
- added the self-contained raw WebGL2 `RealityRenderer708` while preserving the Canvas renderer as world/terrain authority and fallback;
- added a real 3D terrain mesh with derived normals, biome material shading, macro/micro surface breakup, soil/rock slope response, sun lighting and atmospheric fog;
- added WebGL sky, clouds, daylight-correct stars, storms/lightning and animated water response;
- added GPU-instanced tapered grass and multi-layer crossed tree canopies with adaptive flora density;
- added Luna as a third-person procedural EVA field explorer with first/third-person switching;
- added the LUNA-ARC survey vessel with in-scene hull, canopy, wings, engines, landing gear, boarding, cockpit flight, landing and exit;
- added desktop `V` view and `F` ship controls plus mobile `VIEW`/`SHIP`, `ASCEND`/`DESCEND` flight controls;
- validated the exact final GLSL/WebGL2 path in Chromium, including a final `gl.getError() === 0` QA render;
- advanced the canonical one-file engine to `SIM_EARTH_7_08_REALITY_BODY.html` with LF SHA-256 `68318f2fc640d49596c49a9a8d8532d378951c34a42d90a5d3f774ba8775d295`.

## 7.07 — 2026-08-12
- preserved Genesis Engine ancestry in the canonical standalone file;
- added SIM EARTH 7.07 alien control-center layer;
- added exact 12D → 42D → 54D computational state stack;
- added persistent procedural worlds, surface/orbit/reality modes, mobile controls, audio, sensors, growth ledger, and command deck;
- added PWA, iOS/Android Capacitor, and desktop Electron packaging paths;
- added player manual, teacher guide, engineering docs, validation guide, and publication manuscript;
- visual-realism ecology pass: climate-derived biomes, richer terrain materials, layered atmospheric haze, water shimmer, precipitation, dust/pollen, moon/stars, and cloud-depth rendering;
- deterministic vegetation ecology expanded across broadleaf/conifer forests, rainforest, wetlands, grasslands, scrub, desert, tundra, alpine, shallow water, and barren worlds;
- added procedural morphology families for oak/maple/beech/birch, pine/spruce/cedar, palms, mangroves/willows, ferns, reeds/cattails, flowers/orchids/lilies, mushrooms, vines, cactus/succulents/agave, coral, shrubs and ground grasses;
- added ambient birds/gliders/fireflies, denser ground micro-detail, object shadows, adaptive mobile rendering, gas-giant cloud-deck visuals, and live biome HUD readout.
