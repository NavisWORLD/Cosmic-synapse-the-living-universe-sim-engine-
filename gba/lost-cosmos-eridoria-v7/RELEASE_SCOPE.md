# Lost COSMOS V7 — release scope and verification gates

This branch preserves the verified V6 GBA edition. The exact locally built V7 candidate is a native Game Boy Advance eight-world campaign with Origin Earth's Brindlemark, Oakwood and Cragstone regions, the Dream Veil and Eldoria planets, Malakar's tactical encounter, trading, puzzles, four shrines and the preserved six-world RPG and deterministic archived-workload COSMOS companion.

Candidate ROM SHA-256: 78a707e144fc1bd335200b6586e56f326a3bb2a437af4d2afbeb53b0a3389ccd.
Exact V6→V7 patch archive SHA-256: 7e8ecbf7353f3d80ad4e9771f8b3fd30edab04a674093ca1ae9b259f8955a452.
Preserved 8,192-byte workload-derived tape SHA-256: 9bcecc3732fe48107554cc2041cff6088f418290fb850ec0c9b89cdc375f54c8.

The complete editable source is distributed alongside the V7 local release artifact. GitHub Actions must restore the identical V6→V7 hash-locked patch, rebuild the matching ROM, and pass two separate native mGBA runs with the same SRAM before this GitHub branch is marked emulator-verified. Original V6 code and release remain intact.

Content scope: a condensed playable five-act main chain across eight worlds, not an exhaustive adaptation of the user's full manuscript. Character-specific campaigns for the entire guardian roster and network multiplayer are not implemented and must not be advertised as completed. Delta-on-iPhone and physical cartridge manual playtests require user-side device verification.
