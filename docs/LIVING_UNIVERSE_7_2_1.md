# SIM EARTH 7.2.1 — Living Universe

This release candidate extends SIM EARTH from a surface/planetary simulation into an observationally grounded living-universe navigation layer.

## Fidelity model

SIM EARTH uses five provenance classes for astronomical content:

- **MEASURED** — values taken from an observational or mission dataset.
- **CATALOG** — catalogued object positions/identifiers and published properties.
- **DERIVED** — values calculated from catalog/physical parameters.
- **INFERRED** — physically constrained reconstruction where direct measurement is incomplete.
- **PROCEDURAL** — synthetic continuation used only where no observational data is available or where density is required for gameplay.

The project does **not** claim to contain an exact copy of every object in the Universe. The goal is an **observational living-universe digital twin**: use measured/catalogued structure wherever available, derive what can be derived, label inference, and reserve procedural content for observational gaps.

## Universe ancestry restored

The original COSMOS/Genesis ancestry used a large Three.js universe with dense star fields, a cosmic-web transition, free spacecraft navigation, black holes, nebulae, atmospheric shaders, stellar photospheres/coronas, post-processing, and multi-view flight. 7.2.1 restores that scale/depth philosophy while keeping the later SIM EARTH surface, WebGL2 Reality Body, mobile shell, LUNA-ARC, Luna explorer, persistence, and 12D → 42D → 54D state engine.

## 7.2.1 navigation stack

`GALAXY → SYSTEM → ORBIT → ATMOSPHERIC DESCENT → SURFACE → ASCENT → ORBIT`

The galaxy layer uses a compact offline astronomical reference catalog and physically constrained filler. The ship observer position is three-dimensional; changing position changes projected stellar geometry/parallax. Named deep-space anchors retain provenance instead of being randomly scattered.

## Atmospheric continuity

Atmospheric entry is continuous rather than a scene cut. The simulation tracks altitude-dependent pressure, density, temperature, optical depth, Rayleigh/Mie-style scattering, an Earth ozone profile, stellar extinction, drag/heating proxies, and surface blending. Ozone is not used as the cause of a blue sky; Rayleigh/Mie-style scattering controls the visible sky transition.

## Hosted observational bridge

The standalone engine remains offline-first. A hosted bridge is the intended production path for authoritative data sources such as JPL Horizons, Gaia, NASA Exoplanet Archive, NED, and HEASARC. This keeps API/network behavior out of the raw `file://` iPhone HTML path and lets the game cache/normalize catalog data without exposing service credentials.

## QA boundary

Static source verification is required before publication. The current container environment cannot provide a trustworthy Chromium GPU frame because its EGL/ANGLE backend fails during local headless rendering. Therefore 7.2.1 is **not** described as visually certified in that environment. Browser/device runtime testing remains a separate QA gate.
