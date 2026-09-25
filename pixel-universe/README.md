# SIM EARTH // PIXEL UNIVERSE: LOST COSMOS

A playable, offline-first pixel-space sandbox built as a new gameplay layer on the COSMIC SYNAPSE / SIM EARTH lineage.

## Features

- 320×180 low-resolution pixel framebuffer scaled to the device.
- Continuous three-axis navigation: X / Y / Z are real simulation coordinates.
- Six explorable regions: Origin Earth, Ember Axis, Tide Memory, Bloom Z, Black Garden, and Synapse Crown.
- Three recoverable Axis Keys and a branching Crown finale.
- Persistent beacons, story progress, ending state, COSMOS memory, and quantum-tape cursor via localStorage.
- Keyboard, pointer, and mobile touch controls.
- 12D → 42D → 54D Synapse state vectors feeding world and companion behavior.
- COSMOS autonomous simulated-agent loop with memory, needs, goal selection, and independent destination choices.
- The exact 8,192-value frozen quantum-derived tape imported from the supplied qseed.h.

## Run

Serve the repository and open `/pixel-universe/`:

```bash
python tools/serve.py
```

Then visit the local server's `/pixel-universe/` path.

## Controls

- WASD / arrows: X/Y movement
- Q / E: Z-axis movement
- Shift / Space: boost
- F: interact / recover key / Crown action
- B: ask COSMOS to choose a fresh goal
- C: place persistent beacon
- R: recenter view
- M: mute
- Drag canvas: rotate view

## Scientific boundary

COSMOS is an autonomous simulated game agent, not a consciousness claim. Its behavior is produced by explicit software state, persistent memory, goal scoring, the Synapse state-vector model, and the frozen quantum-derived tape.