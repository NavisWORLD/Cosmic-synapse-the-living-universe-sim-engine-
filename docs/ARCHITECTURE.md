# Architecture

## Canonical rule
`standalone/SIM_EARTH_7_07_ALIEN_CONTROL_CENTER.html` is the canonical game artifact. Packaging layers copy or wrap it; they do not become a second source of truth.

## Runtime layers
1. **Genesis ancestry:** event bus, telemetry, sensors, procedural systems, universe renderer, audio, legacy Three.js implementation preserved in-file.
2. **SIM EARTH 7.07 overlay:** `SensorFusion`, `CSTStateEngine`, `SimEarth707App`, persistent world/game systems, HUD, command deck, surface/orbit/reality modes.
3. **Persistence:** browser local storage for world/session growth plus explicit export paths.
4. **Packaging:** PWA preparation script, Capacitor mobile container, Electron desktop container.

## Data flow
```text
microphone ─┐
camera ─────┼─> SensorFusion ─> 12D CST state ─> 42D world state ─> 54D adaptive state
location ───┤                         │                    │                 │
motion ─────┘                         └──── rendering / audio / growth / UI ┘

planet seed ─> terrain + climate + physics + resources ─> persistent world state
```

## Determinism
Named procedural worlds use deterministic hash/PRNG ancestry so the same world name can regenerate the same base world. Session history then adds persistent local evolution.

## Security model
The standalone engine runs client-side. Native and desktop wrappers deliberately disable Node integration in game content and restrict permission grants to needed browser capabilities.
