# SIM EARTH 7.07 — Visual Realism Ecology

Canonical LF SHA-256 after this pass: `39278ea52ab10d80cf874ccb8fea8f2937cb19b1036f9d5e90007a01a9f53e5b`.

## What changed

The visual renderer now derives scene appearance from the same persistent planet/world state rather than drawing generic decorative objects. The rendering stack includes:

- climate-derived biome selection from temperature, latitude proxy, moisture, elevation, atmosphere and water;
- biome-specific surface palettes and deterministic micro-material grain;
- ocean depth states, wave variation and screen-space water glints;
- layered atmospheric gradients, horizon haze, stars, lunar detail, multi-layer clouds and planet weather shells;
- rain/snow, dust, pollen, lightning and storm-darkening behavior;
- deterministic plant families spanning trees, palms, ferns, reeds, flowers, mushrooms, vines, cacti, succulents, shrubs, grasses and coral;
- near-ground blades, stones and micro-detail for depth;
- ambient birds/gliders and dusk fireflies when biosphere conditions support them;
- gas-giant cloud-deck rendering for Jupiter/Saturn/Uranus/Neptune-like worlds;
- adaptive surface column resolution to preserve mobile frame budget;
- a live biome label in the surface HUD.

## Scientific boundary

These systems increase visual and ecological coherence. They are procedural simulation rules, not a botanical census, satellite-derived digital twin, or proof that CST variables are physical laws. A literal reconstruction of every plant and every square meter would require continuously updated geospatial, ecological, seasonal and species-distribution datasets far beyond a self-contained HTML file.
