# CST closed loop v1: what changed and what the data shows

- The 54-channel state now drives the world: biosphere growth follows coherence plus Hebbian strength, and storm follows chaos plus instability. Creature mood (joy, curiosity, fear, calm, mischief) is computed from the state. All couplings are unitless, clamped to [0,1], and capped at an effective dt of 5 s, so time-warp cannot run away.
- `quantum_entropy` (channel 11) now replays **RECORDED historical IBM hardware counts** deterministically: 24 public 12-bit runs from The-beast-box `public/spark/runs.json`, each pinned by SHA-256. They are embedded as `#cst-seed-tape`. One Rigetti QVM run is embedded too, labelled **SIMULATED**, and is used only in ablations. No live device is used, nothing is entangled with the player, and no provider calls are made.
- Lorenz is now driven by state (rho by arousal, x forced by the quantum channel) and drives the world (storm). The previous tick's Hebbian strength feeds back into coherence and biosphere.
- The world feeds the state as before (biosphere → valence and memory coherence; storm → arousal, anomaly, instability), so the loop is closed.

`npm run ablate:cst` reproduces `RESULTS.txt`: 20 sensor seeds × 18,000 ticks, using a JS port of `CSTStateEngine.update` with synthetic sensors and the real coupling module.

Honest reading:
- **Recorded IBM counts vs a PRNG that resamples the same histogram: no meaningful world effect** (biosphere 0.0%, storm -8.5% but not significant). What matters is the *shape of the distribution*: the IBM 12-bit histograms are skewed low, with mean ≈0.08. Uniform PRNG, the old sin-hash, a constant and the Rigetti-simulated counts all change curiosity by about 35–48% and mischief by about 14–20%, because their mean is near 0.5. That isn't a quantum effect: the matched PRNG reproduces it.
- The couplings themselves are real and large. Opening the loop (state → world off) changes biosphere by -21% and storm time by +214%. Lorenz input off changes storm by ×20 and fear by +230%. Hebbian → world off changes biosphere by +8% (with Hebbian below 0.25, its term currently slows growth).
- Synthetic sensors, not real mic/camera input.
