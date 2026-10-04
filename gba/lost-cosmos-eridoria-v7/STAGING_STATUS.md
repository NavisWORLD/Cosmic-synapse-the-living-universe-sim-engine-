# LOST COSMOS V7 — Eridoria Eight-World Campaign (staging branch)

This branch was created from the verified V6 baseline `8e28a0001ba81d49696c41346e6734f533045d11` to isolate an expanded native GBA campaign. **V6 remains preserved and this branch is not yet the published V7 game source.**

The V7 candidate has been built and tested in the project's working environment. Its packaged source and reproducible V6→V7 hash-locked patch archive must be uploaded before GitHub-hosted native mGBA CI can verify this exact revision.

Candidate features: native 8-world star map (Dream Veil, Eldoria additions); Brindlemark/Oakwood/Cragstone/Hidden City linked Origin subareas; Oakwood buy/sell market; four visually distinct temple runes and interactive SKY→ROOT→HEART→STAR sequence; 32×32 Malakar tactical battle; interactive Dream riddle, guardian and three trials; four Eldoria element shrines; eleven native indexed cinematic scenes; persistent campaign flags with isolated SRAM extension. The condensed five-act objective chain preserves the six original worlds and original Crown choice.

**Verification boundary:** Original V6 passed GitHub Actions real mGBA. The candidate V7 passes local freestanding ARM compilation, clean source ZIP rebuild/hash identity, two fresh-process host QA boots and regression tests. Neither GitHub Actions mGBA on the V7 ROM nor Delta device testing has been completed. Do not mark V7 as a verified public release yet.

Provenance: original V6 source Git blob `6917e0875be1a1b3ac94dee3e5873053336f1c48`; frozen 8192-byte workload-derived tape SHA-256 `9bcecc3732fe48107554cc2041cff6088f418290fb850ec0c9b89cdc375f54c8`.

When the candidate source is uploaded, install/extend the V6 GBA CI workflow to rebuild the exact V7 artifact, run all new host tests, then execute two independent real mGBA boots against the same SRAM before creating a release.