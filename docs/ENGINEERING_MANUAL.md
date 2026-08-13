# Engineering Manual

## Design objective

Build a local-first procedural universe in which observation can condition software state without confusing authored rules with external physical causation.

## Module boundaries

- **Input adapters** — browser sensors, player controls, external public data.
- **Simulation core** — deterministic fixed-step mechanics.
- **CST state engine** — 12D→42D→54D software feature/state vector.
- **Procedural generation** — stars, planets, terrain, resources, ecology and events.
- **Renderer/audio** — multiple visual scales plus state-reactive feedback.
- **Persistence** — world saves, event ledger, export/import.
- **Memory Echo** — replay/artifact representation of previous state.

## Determinism rule

Any randomness that influences replayable state must come from a deterministic PRNG seeded from recorded state, or the resulting random event must itself be logged.

## Network rule

NASA/USGS I/O runs outside the authoritative frame loop. Network failure must never freeze player physics or rendering. Successful external observations become timestamped normalized inputs that can later be replayed offline.

## Rendering rule

Renderer frame rate may vary. Physics/state evolution should not depend on display refresh rate.

## Scientific rule

If a channel is named after a scientific concept, document exactly how the numeric value is computed. Do not rely on the name itself as evidence that the software measured the corresponding physical phenomenon.
