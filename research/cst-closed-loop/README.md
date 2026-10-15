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

## v1.1 combined loop (2026-10-15)
- **New real hardware run:** IBM job `db8iu85ckpjs73b13msg` on **ibm_marrakesh**. It is one owner-authorized Open Plan job: Bell |Φ+> measured at the four CHSH settings, 4×1024 shots. Correlators were E = 0.703, 0.689, 0.646, -0.719, giving **S = 2.758 ± 0.045**. That is 16.8 SE above the local-hidden-variable bound of 2, and near the Tsirelson limit of 2.828. Usage went from 186 to 189 Open-Plan seconds, so about 3 s. This is not a loophole-free Bell test.
- **Live engine:** the engine now replays this run in a Bell channel. The state picks the measurement setting each tick (arousal → Alice, curiosity → Bob), and the outcome product drives storm and biosphere.
- **Training:** `combined.mjs` trains the Hebbian weights and memory on **all** archived workloads: 5,614 IBM hardware runs (186 jobs, about 25.3M shots, including the CHSH job) plus 32 SIMULATED Rigetti runs (18 diary-loop ticks and 14 archived QVM runs). It then ablates world outcomes. Results are in `COMBINED_RESULTS.txt`.
- **Result:**
  - A classical PRNG that resamples the same joint per-setting tables gives the same world as the real hardware: biosphere -0.2%, not significant.
  - The closest *local-hidden-variable* model (|S| ≤ 2) does differ: biosphere -6.0%. This is the one place the hardware's Bell-violating correlation structure measurably changes the world. It is a difference no LHV model can reproduce, but a classical PRNG matched on the joint per-setting tables can.
  - For the 12-bit qe channel, marginal-only and joint-matched PRNGs both match the recorded counts within about 0.4%.
