# SIM EARTH 7.08 — Reality Body Engineering Guide

SIM EARTH 7.08 adds a self-contained WebGL2 **Reality Body** to the existing living-universe engine. The simulation, persistence, sensor fusion, biome logic, and 12D → 42D → 54D state stack remain authoritative; the new renderer gives those systems a three-dimensional surface body.

Canonical LF SHA-256:

`68318f2fc640d49596c49a9a8d8532d378951c34a42d90a5d3f774ba8775d295`

## Architecture

The standalone keeps two rendering paths:

1. `SimRenderer` remains the procedural world/terrain/biome authority and Canvas fallback.
2. `RealityRenderer708` consumes that same state and terrain function to render the surface with raw WebGL2.

No Three.js or runtime CDN is required. The Reality Body therefore travels inside the canonical one-file game.

## 3D surface

The WebGL2 surface includes:

- a generated height-field terrain mesh using the existing terrain function;
- per-vertex normals derived from neighboring terrain samples;
- biome-derived base materials;
- procedural macro/micro material breakup;
- soil mottling and slope-dependent rock exposure;
- directional sun light plus hemispheric fill;
- distance/atmospheric fog;
- tone-mapped terrain response;
- adaptive desktop/mobile mesh density.

The current desktop QA scene generated `112,614` terrain indices. Mobile uses a smaller terrain grid to preserve frame budget.

## Atmosphere and water

The sky shader provides:

- day/night gradient response;
- sun glow;
- atmospheric horizon haze;
- daylight suppression of stars;
- multi-octave procedural cloud structure;
- storm darkening and lightning flashes.

Water uses a translucent surface with animated normal distortion, specular response, Fresnel-style edge behavior, and atmospheric fog integration.

## Vegetation

Vegetation is GPU-instanced where practical. The QA Earth scene generated roughly five thousand grass instances and more than two hundred trees. Grass is rendered as tapered wind-responsive blades. Trees use a trunk plus multiple crossed canopy layers to create lightweight volume without external models or textures.

The older ecology engine still chooses local biomes and remains available as the Canvas fallback.

## Luna — field explorer

Third-person mode renders **Luna** as the in-world field explorer rather than a floating camera. The lightweight procedural EVA body includes:

- rounded suit anatomy;
- white/graphite environmental suit;
- backpack;
- helmet and blue visor;
- cyan suit/chest illumination.

This is a procedural game character built from WebGL geometry. It is not a scanned or externally licensed character asset.

## LUNA-ARC survey vessel

The **LUNA-ARC** is a persistent in-scene exploration vessel with:

- pale ceramic/metal main hull;
- dark lower structure;
- cockpit canopy;
- dorsal body detail;
- broad atmospheric wings;
- emissive engine pods;
- landing legs and ground contact shadow.

The player can approach, board, fly, descend, land, and exit the vessel.

## Controls

### Desktop

- `WASD` — walk / ship thrust and yaw
- Mouse / arrows — look
- `Shift` — sprint / high-speed ship thrust
- `Space` — jump; ascend while flying
- `Ctrl` — descend while flying
- `E` — scan
- `V` — first/third-person view
- `F` — board/exit LUNA-ARC
- `G` — orbit/surface
- `R` — Reality Lens
- `H` — HUD/control panel
- `M` — audio
- `T` — time warp

### Mobile

The touch HUD adds `VIEW` and `SHIP`. When boarded, `JUMP` becomes `ASCEND`, `SCAN` becomes `DESCEND`, and `SHIP` becomes `EXIT`. Labels are restored after disembarking.

## Fallback and performance

If WebGL2 is unavailable, the existing Canvas renderer remains the surface path. Flora density is adaptive and can reduce itself when measured render cost rises. Device pixel ratio is capped, with a lower ceiling on mobile.

## Validation performed

The exact canonical source was subjected to:

- active-script JavaScript syntax checks;
- DOM ID and literal `getElementById` resolution audits;
- preservation checks for the 12D, 42D, and 54D state arrays/classes;
- mocked hostile DOM/WebGL runtime exercising terrain/flora generation, render, view switching, ship boarding, flight, landing, and exit;
- mobile touch-control runtime checks;
- a genuine Chromium WebGL2 shader/program compile and render path using the final source;
- `gl.getError() === 0` in the final Chromium QA path;
- exact SHA-256 reconstruction on a GitHub-hosted runner before the repository source was accepted.

A real shader defect was caught during QA (`patch` is reserved in GLSL) and corrected before release. This is why mocked graphics validation is treated as complementary rather than sufficient.

## Scientific and visual boundary

Reality Body is a procedural visualization/game renderer. It is **not** a satellite-derived digital twin, a literal reconstruction of every real organism, a medical/sentience instrument, proof of additional physical dimensions, or physical control of Earth/remote planets.

Likewise, “Reality Body” describes the visual/game architecture. The current self-contained WebGL implementation is intentionally lightweight and stylized; it should not be represented as cinematic UE5-class photorealism. Its engineering goal is coherent, portable, inspectable 3D world presence while retaining the unusual one-file lineage of SIM EARTH.
