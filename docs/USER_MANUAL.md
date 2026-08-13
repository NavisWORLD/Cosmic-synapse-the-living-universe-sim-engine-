# User Manual

## Start

Open the Ultimate HTML directly or generate/serve the PWA. Start the engine from its entry screen to unlock permission-gated audio/sensors.

## Views

- **Surface** — walk, jump, scan terrain/resources, seed life and place outposts.
- **Orbit/System** — inspect the current procedural or known planet/system.
- **Cosmic Web** — traverse/select higher-level seeded locations when available in the active engine mode.
- **Reality Lens** — camera-backed visual mode when camera permission exists.
- **APOD** — use NASA Astronomy Picture of the Day as a visual/context layer.
- **Memory Echo** — replay or transmute previous simulation state into an explorable artifact mode.

## Core mechanics

- Fold between named planets or invent a destination.
- Gravity changes walking/jumping behavior.
- Scan generates deterministic local resource values.
- Seed life changes a simulated biosphere state.
- Outposts persist locally.
- Storms/anomalies are explicit game events.
- Time warp accelerates simulation time.
- Missions are generated from world state.
- Saves/ledgers can be exported for inspection.

## Controls

The HTML exposes both keyboard/pointer and mobile touch controls. The native C++ vertical slice documents its own keys in `native/README.md`.

## Sensors

Camera, microphone, orientation and location are optional. If permission is denied, the simulation continues with available/default state.
