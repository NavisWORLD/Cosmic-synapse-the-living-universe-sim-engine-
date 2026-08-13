# Living Universe Architecture

## Authoritative loop

The simulation is intended to be replayable from a recorded input stream.

```text
poll controls / queued observations
accumulator += frame delta
while accumulator >= 1/60 s:
    update player physics
    update world clock/weather/biosphere
    apply recorded external events
    update CST 12D state
    expand to 42D world state
    update 54D adaptive state
    evaluate game rules
    append meaningful events
    accumulator -= 1/60 s
build render snapshot
render independently
```

## 12D state

The first layer summarizes immediate sensory/dynamical software channels including frequency mass, phase, spectral flatness, phase velocity, audiovisual relationship proxies, valence/arousal/dominance-style control values, audio ψ proxy, φ-harmonic score, audiovisual coherence and an entropy/provenance channel.

## 42D state

The 12D state is extended with Lorenz/chaos values, tension/energy, camera/audio summaries, location/solar phase, simulated gravity/atmosphere/temperature/pressure/wind, terrain slope, water fraction, biosphere, civilization/outposts, radiation, magnetic field, resource field, anomaly field, memory coherence, novelty, instability and overall coherence.

## 54D state

The adaptive extension adds Hebbian strength, plasticity, attention, curiosity, avoidance, flora/black-hole bias controls, memory depth, prediction error, learning rate, resonance and a singularity-control channel.

These are software state dimensions, not a claim of 54 physical spacetime dimensions.

## Generation hierarchy

```text
master seed
  → system seed
    → star/planet properties
      → terrain field
        → local object cells
          → biosphere/ecology events
```

## Scale transitions

The browser ancestry includes local system and cosmic-web concepts. A mature native port should use origin rebasing/floating-origin techniques for large scales rather than forcing one floating-point coordinate system to represent planet-surface and cosmic-web distances simultaneously.

## Memory Echo

A Memory Echo is a persisted/replayed representation of prior simulation state, geometry and/or events. Scientific/reproducibility tests should compare declared invariants, not visual similarity alone.
