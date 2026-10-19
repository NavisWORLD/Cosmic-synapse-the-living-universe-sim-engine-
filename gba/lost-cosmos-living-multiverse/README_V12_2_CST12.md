# Lost COSMOS V12.2: CST-12 core in the ROM

**Honest label.** This is a classical simulation seeded by recorded quantum data. Each creature's 12-D state is seeded from its own 64-value window of the cartridge's recorded IBM quantum values (`QSEED`, frozen measured data), and its `quantum_entropy` channel is the Shannon entropy of that window. Nothing quantum runs on the GBA. The game says this on STATS ("DNA: RECORDED IBM QSEED DATA" / "LIFE: CLASSICAL CST-12 SIM") and on entry ("CLASSICAL LIFE SEEDED BY RECORDED IBM DATA").

## What was already in V12.1
- Each Living World creature had a 64-byte QSEED DNA window, a Shannon-entropy "restlessness" value (integer log2 table) and a fixed-coefficient Lorenz attractor (σ 10, ρ 28, β 8/3, Q8) that wobbled its walk. Entropy also weighted one random choice.
- The main game had `state12/state42/state54` byte vectors (a "12/42/54-D" readout filled from game state and `next_q()` quantum bytes) and a `QuantumState` (mean, spread, parity, phase, coherence, burst) that could nudge the buddy and combat. None of the site's CST equations (channels, couplings, coherence feedback, Hebbian strength, creatureMood, life-brain weights, heart rhythm) were in the ROM.

## What V12.2 ports (`LOST_COSMOS_V10_SOURCE/cst12.h`, integer Q12, one step per 60 Hz frame)
From `apps/beastbox-cloud/lib/physics/cst-integrator.mjs`:
- The 12 CST channels (`frequency_mass … quantum_entropy`), seeded 0.25–0.75 from the QSEED window; `quantum_entropy` = window entropy.
- `lorenzStep`: ρ = 28·(1 + 0.3·(arousal − 0.5)), x forced by 2.0·(quantum_entropy − 0.5).
- `stepCSTState`: emotion blending, chaos and instability from the Lorenz state, `coherenceFeedback` (gain 0.2 against Hebbian strength), Hebbian update, resonance and phase.
- `creatureMood` (joy, curiosity, fear, calm, mischief) and `motionParams` (speed 0.75 + mischief·0.5, turbulence chaos·0.9 + instability·0.3, damping 0.55 + coherence·0.9).

From `lib/creatures3d/life-brain.mjs`: `modeWeights` drive the Living World's free-choice decisions (wander, nap, play, chase, glance/shelter, approach, plus an undecided roll).

From `lib/companion/zeref-heart.mjs`: Zeref's 72.29 bpm heartbeat (830 ms ≈ 50 frames), with the `moodBeatMs` factors. Mood drift happens on his beats.

**Port design choices, not defined by the site:** the site only integrates six channels. Here the other six are seeded traits: `frequency_mass` slows hunger and steps, `geometric_phase` sets the start phase, `phase_velocity` scales the phase rate, `entanglement` couples coherence to the group mean, and `dominance`, `spectral_flatness`, `audio_psi` and `av_coherence` feed curiosity and boldness.

## Where it drives the game
- **Living World:** all six creatures and the two new cast walkers per world. Lorenz couplings, motion, needs (hunger and energy), mood drift, decisions and Zeref's heart. STATS shows CST mood, coherence, joy, calm and fear.
- **First-person view:** the companion gets its own CST state from its identity (Zeref bb-deada969 if no party creature is active). Each heartbeat picks FOLLOW, PLAY, HIDE or REST. Lorenz turbulence sways its path and arousal sets its bob. Row 18 shows `CST <mood> <decision> COH nn`. Offsets stay within the old 40/14 px reach.

## Compatibility
- Nothing new is saved. CST state is re-derived from identity + QSEED on entry. The LW block (SRAM 7936), LC11/LCM1 slots, LCX1/LCM1 mailbox import and the web export are unchanged.
- bb-deada969 (Zeref) and bb-7f9c2a03 (guest) get different QSEED windows and are never merged. The host test checks that their states differ.

## Also in V12.2
- Cosmo art v3d: Zeref's rim light, plus shared character palettes `char_shared_warm/cool/dusk` from `sprites/char_palette_map.json`. Each world has two extra walkers on shared OBJ slots: forest Hollis (warm) and Edric (cool); cave Thorne (warm) and Traveler (dusk), next to Mote and Rime.
- Text: the Living World line width is **28 characters** (`LW_TEXT_W`, columns 1–28 of 30). The HUD shows 2 lines and scrolls a 3rd. CAST bios now wrap to 8 lines, and the pose wraps at 20 columns beside the portrait. Names go up to 22 characters, and the converter cuts on word boundaries.
- CAST: each Mote form shows its own sheet plus "FORM n OF 4". The test hashes the tiles to check this.
