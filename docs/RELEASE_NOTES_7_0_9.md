# SIM EARTH 7.08 // REALITY BODY — 7.0.9 UI + Dynamic Graphics Hotfix

This hotfix keeps the SIM EARTH 7.08 Reality Body simulation/game lineage intact while fixing two user-visible problems: the control UI could not be cleanly dismissed, and several visual/world-state changes did not reliably propagate into the active WebGL2 renderer.

## What changed

- Added an explicit `×` button to close the large SIM EARTH control panel.
- Added `× UI` immersive mode plus a persistent `☰ RESTORE UI` control.
- Kept mobile movement controls available while the HUD is minimized.
- Added a native **VISUALS** tab for active renderer quality, look, brightness, renderer/fallback switching and manual world-visual refresh.
- Bridged the older Genesis quality/filter/brightness controls into the active SIM EARTH renderer.
- Fixed Reality Body daylight so WebGL2 derives the live simulated solar phase directly instead of waiting for the hidden Canvas renderer to update a shared light value.
- Corrected `day` and `night` commands to simulated noon and midnight.
- Smoothed environmental light/atmosphere transitions.
- Made biosphere growth/reset invalidate and rebuild local WebGL terrain/flora immediately.
- Made living-biome material palettes visibly respond to biosphere strength.

## Verification

Canonical LF SHA-256:

`cc6e1c116d703019f4b7a5dce6330897a0b47cdcf62a4018b95b2f24c2ac5084`

The hotfix was reconstructed through an exact SHA gate, audited for duplicate/missing DOM references, parsed across all active JavaScript bodies, and passed `npm run verify` plus `npm run prepare:web` both before and after merge to `main`.

## Distribution notes

Desktop and simulator/test packages in this release are generated from the hotfixed canonical source. Windows/macOS packages remain unsigned unless publisher code-signing credentials are supplied. Android direct testing uses the packaged debug APK. The iOS ZIP is a Simulator build, not a physical-device/App Store IPA. The repository retains a separate publisher-signing workflow for signed Android APK/AAB and iOS IPA creation when private publisher credentials are provided.

## Scientific / visual boundary

Reality Body is a procedural real-time WebGL2/Canvas simulation. This release improves coherent visual state propagation and usability; it does not claim a survey-derived Earth digital twin or cinematic photoreal reconstruction.
