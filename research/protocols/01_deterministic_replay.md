# Protocol 01 — Deterministic replay

**Status: PROPOSED TEST — NOT YET RUN**

Record engine commit, seeds, fixed-step player command stream and normalized external-event snapshots for a 10-minute run. Save canonical checkpoints every 600 fixed steps. Replay five times on the same platform and at least one second platform.

Primary metric: percentage of discrete checkpoints/events with matching canonical hash. Same-platform discrete event sequence target: 100%. Cross-platform numeric tolerance must be specified before inspecting results.
