# SIM EARTH 7.08 — UI / Dynamic Graphics Hotfix

Canonical LF SHA-256 after hotfix: `cc6e1c116d703019f4b7a5dce6330897a0b47cdcf62a4018b95b2f24c2ac5084`.

## UI fixes

- The large SIM EARTH control panel now has an explicit `×` close button.
- `CONTROL` reopens the panel and reports its expanded state for accessibility.
- `× UI` hides the full desktop HUD; a persistent `☰ RESTORE UI` pill brings it back.
- `Esc` closes the panel first, then minimizes the HUD when the panel is already closed.
- Mobile movement controls remain available while the HUD is minimized.

## Dynamic graphics fixes

- A native **VISUALS** tab controls Reality Body quality, visual look, brightness, renderer/fallback selection and manual visual refresh.
- Legacy Genesis quality/filter/brightness controls are bridged into the active Reality Body renderer.
- WebGL daylight is calculated from the current simulated solar phase every frame; it no longer depends on the hidden Canvas renderer.
- `day` maps to simulated noon and `night` maps to simulated midnight.
- Atmosphere values interpolate rather than snapping.
- Biosphere changes invalidate/rebuild the local WebGL terrain/flora buffers immediately.
- Living-biome material palettes transition from dormant/barren tones toward their mature biome palette as biosphere strength rises.

## Validation

The source gate refuses this patch unless it reconstructs the exact canonical SHA above. JavaScript syntax, duplicate IDs, literal DOM references and repository verification are checked in CI before publication.

The renderer remains a procedural real-time WebGL2/Canvas simulation, not a survey-derived digital twin.
