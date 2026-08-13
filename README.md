# Cosmic Synapse — The Living Universe Simulation Engine

**Procedural universe · playable world simulator · CST 12D→42D→54D state engine · NASA/USGS context · Memory Echo · cross-platform app**

This repository is the focused public engineering release for the **living-universe simulation engine** developed in the Reality Bridge / SIM EARTH 7.07 / COSMOS/CST project lineage.

It deliberately contains **only the universe-simulation part of the work**. The physical Reality Bridge probe hardware belongs in its separate platform repository.

> **Prime rule:** make the simulation as ambitious as possible while keeping measurement, authored game mechanics, hypotheses, and established evidence clearly separated.

## What is here

| Area | Status | Location |
|---|---|---|
| Ultimate single-file universe game | **IMPLEMENTED** | `REALITY_BRIDGE_UNIVERSE_ENGINE_ULTIMATE.html` |
| Historical SIM EARTH 7.07 ancestry | **ARCHIVED** | `archive/` |
| Installable PWA | **IMPLEMENTED PACKAGING** | `apps/pwa/` |
| iPhone / Android wrapper source | **IMPLEMENTED BUILD SCAFFOLD** | `apps/mobile/` |
| Windows/macOS/Linux wrapper source | **IMPLEMENTED BUILD SCAFFOLD** | `apps/desktop/` |
| C++20 native simulation core | **IMPLEMENTED VERTICAL SLICE** | `native/` |
| Python NASA/USGS live-data bridge | **IMPLEMENTED** | `native/python/` |
| Reusable JS engine library | **IMPLEMENTED** | `packages/cosmic-synapse-universe-core/` |
| Deterministic replay / APOD / sensor / Memory Echo protocols | **PROPOSED TESTS — NOT YET RUN** | `research/` |
| Engineering, user, teacher and study manuals | **IMPLEMENTED DOCUMENTATION** | `docs/` |

## Start immediately

After the repository materialization workflow has completed, open:

```text
REALITY_BRIDGE_UNIVERSE_ENGINE_ULTIMATE.html
```

or generate and serve the installable PWA:

```bash
npm run prepare:pwa
python -m http.server 8080 -d apps/pwa
```

Then open `http://localhost:8080`.

## What the engine does

The universe engine combines:

- deterministic procedural world generation;
- known planetary anchors plus invented seeded worlds;
- surface exploration, gravity-dependent movement and jumping;
- orbit, system, cosmic-web, Reality Lens, APOD and Memory Echo views;
- biosphere growth, flora/creature rendering, outposts, resources, storms and anomalies;
- autonomous world events and time warp;
- browser microphone, camera, motion and location summaries where permission is granted;
- NASA APOD, NASA NEO, NASA DONKI and USGS earthquake context;
- a live **12D → 42D → 54D software state vector**;
- persistent local worlds and an event ledger;
- procedural audio and audiovisual feedback;
- save export/import, screenshots, missions and developer telemetry;
- mobile touch controls and desktop keyboard/pointer controls.

## Architecture

```text
phone/browser observations           public context
mic · camera · motion · location     NASA APOD/NEO/DONKI · USGS
             │                                  │
             └──────────────┬───────────────────┘
                            ▼
                    normalized inputs
                            ▼
                 fixed-step simulation
                            ▼
                  CST 12D → 42D → 54D
                            ▼
        ┌───────────────────┼────────────────────┐
        ▼                   ▼                    ▼
 procedural worlds      game mechanics       render/audio
        │                   │                    │
        └───────────────────┼────────────────────┘
                            ▼
                persistence + event ledger
                            ▼
                 snapshot / Memory Echo
                            └───────────────↺
```

The 12D/42D/54D labels describe **software feature/state vectors**. They are not presented here as proof of extra physical dimensions.

## External-data boundary

NASA and USGS feeds are real public data sources. The game can map those observations into visual or procedural behavior. For example, a large earthquake feed entry may be authored to trigger a simulated anomaly.

That means:

```text
real observation → recorded software input → authored simulation response
```

It does **not** mean the real earthquake physically created the simulated anomaly.

## App installation

- **iPhone/iPad:** host the generated PWA on HTTPS and use Safari → Share → Add to Home Screen.
- **Android:** install the PWA or build the Capacitor Android project.
- **Windows/macOS/Linux:** install the PWA or package the Electron wrapper.
- **Native iOS distribution:** the project source is included, but Apple device/App Store distribution requires the distributor's own signing identity and provisioning profile.

See [`docs/APP_INSTALLATION.md`](docs/APP_INSTALLATION.md).

## Native engine

```bash
cmake -S native -B native/build -DCOSMOS_BUILD_GAME=OFF -DCOSMOS_BUILD_TESTS=ON
cmake --build native/build --config Release
```

The native runtime separates Python network I/O from the authoritative C++ simulation clock so live feeds cannot block physics/rendering.

## Research status

The tests under `research/protocols/` are deliberately written **before** results. In this release they are proposed tests, not findings.

The repository does not, by itself, establish:

- a new law of physics;
- consciousness or sentience;
- precognition;
- quantum advantage;
- causal astronomical influence on local physical reality;
- predictive value simply because external data enters a deterministic seed.

## Repository map

```text
apps/       PWA + mobile + desktop packaging
archive/    preserved browser ancestry
docs/       manuals and teaching material
native/     C++ engine + Python NASA/USGS bridge
packages/   reusable deterministic/state helpers
research/   claim registry + preregistered simulation tests
scripts/    canonical-engine packaging scripts
.github/    CI and cross-platform build workflows
```

## Licensing

- Software/code: **Apache-2.0**
- Documentation/teaching material: **CC BY 4.0**

See `LICENSE` and `LICENSES.md`.

## Philosophy

**Be unrestrained in simulation design. Be strict about what the evidence actually shows.**
