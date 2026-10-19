# Lost COSMOS V12.2b: Beast Box ecosystem bridge

The GBA has no network. Both directions travel inside the normal 32 KiB `.sav`. Byte maps are in `LOST_COSMOS_V10_SOURCE/ecosystem_bridge.h`, and the Python reference is `tools/lc_ecosystem.py`.

## Site → game: `LCQ1` (SRAM 25540, 60 bytes)
This record carries the beast's latest Rigetti growth state. **The site's Rigetti loop runs on a QVM, so it is SIMULATED.** flags bit0 = SIMULATED is required, and the cartridge rejects a record without it. The record also has to match the creature's identity and pass an FNV-1a-32 check. Each of the 12 s8 offsets is applied as `value*16` in Q12, clamped to ±0.25, on top of the creature's QSEED-seeded CST-12 state when the first-person companion is seeded. After that, the traits evolve from experience in the normal way. Offsets come from the four SIMULATED counts using `rigetti_offsets()`, which keeps each one within ±0.125.

## Game → site: `LCE1` (SRAM 24704, 128 bytes, previously empty)
The cartridge rewrites this record every 8 companion heartbeats. It holds the identity, all 12 channels, coherence, joy, curiosity, fear, calm and mischief, the needs (trust, energy, curiosity, avoid), the count of quests touched, a 32-entry mood-history ring, the CST step count and an FNV-1a-32 check. `python3 tools/lc_ecosystem.py export game.sav` prints it as JSON.

## Compatibility
Neither record touches LC11, LCM1, LCX1, LCG1, the journal or the LW block. Older ROMs ignore both, and a missing record does nothing.
