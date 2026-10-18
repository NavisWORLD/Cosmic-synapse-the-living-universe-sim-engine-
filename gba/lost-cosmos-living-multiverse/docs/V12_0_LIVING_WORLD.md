# LOST COSMOS V12.0 — LIVING WORLD

Additive upgrade on top of V11.9 (Act II Trial of Mirrors). Nothing in the
V11 campaign, saves (LCV5 / LC11 / LCM1 slots), LCX1/LCM1 web import or the
party roster changes.

## Cartridge
- Title `COSMOS V12.0`, game code `ERL8`, **16 MB** (16,777,216 bytes, padded).
  Real code+data is ~1.38 MB; the rest is reserved room for the heavy art pass.
- Built with the existing clang/ld.lld toolchain. `grit` is not installed on
  the build box or in CI, so `tools_v12/convert_v12.py` is a grit-equivalent
  converter (PNG → 4bpp/8bpp tiles, BGR555 palettes, BG maps; JSON → ROM tables)
  that writes `v12_art.c`/`v12_art.h` and `v12_text.h`. Re-run it after
  changing anything in `v12_assets/`.

## Entering
START › SYSTEM › **LIVING WORLD** (row after FIRST PERSON) while on foot.
A mode-4 256-colour story card (Cosmo's Zeref forest/cave scene) opens it;
A skips. B leaves; the whole VRAM, palettes, OAM, UI map and display
registers are restored from an EWRAM copy, so the field resumes as it was.

Controls: D-pad moves Arin · A pets/wakes the nearest creature · L/R choose
which creature the HUD follows · SELECT forest/cave · START opens the tabs
ITEMS › STATS › QUESTS › CAST (START cycles, B back).

## What lives there
Six website creatures (Zeref, Kairo, Frost, Kitten, Shardhowl, Velvetcoil) as
64×64 sprites with 6-frame idle and walk loops, each with its 32×32 wireframe
companion. Zeref plays his 4-frame `react_dark` loop whenever the darkness
wisp comes close (trigger `dark_nearby` → action `hide_behind`).

**Honest label:** this is a *classical simulation seeded by recorded quantum
data*. Each creature's DNA is a 64-value window of the cartridge's recorded
IBM QSEED table (5-bit values), chosen by its identity. The DNA sets base
stats, the starting point of its Lorenz attractor (σ10, ρ28, β8/3, fixed
point), its xorshift PRNG and its Shannon entropy (restlessness). Hunger,
energy, mood and bond drift over time; every ~2–4 s each creature picks one of
Emeth's 21 moods from its needs and surroundings and performs that mood's
action (seek food, raid the pack, nap, hide, dig, present a found item…).
Nothing quantum runs on the GBA.

Identity: Zeref here is `bb-deada969` (0xDEADA969). A Beast Box guest such as
`bb-7f9c2a03` is a different identity and is never merged into this record.
The other five use local cartridge identities.

## Items and stats
All 65 of Emeth's items with stats and Cosmo's icons (54 16×16 icons with a
second frame, 6 32×16 weapons, 5 16×24 two-frame lanterns). Consumables/food
change HP, hunger, energy and mood; weapons, armour, accessories and lanterns
equip into four slots per creature and add to HP/ATK/DEF/SPD/FOCUS. Key items
and materials are kept. Creatures level up from activity. Found items come
from `dig` → `present_item`.

## Quests
Emeth's 39 quests (Acts II–V) are a journal with rewards. Their state is
derived from the native campaign (`cq_state`, Q10–Q38): a journal quest of act
N opens when that native act starts and completes in proportion to the native
quests completed in that act. Rewards go into the Living World pack once.
Only Act II is natively playable today, so Acts III–V stay LOCKED.

## Save
SRAM 16384–16639 (`'L','W',1`), checksummed; see `living_world_state.h`.
Shared by all save slots.

## Test
`tests/test_mgba_living_world.py` (mGBA, controller only) – screenshots in
`artifacts/mgba_living_world/`.

## Still placeholder
- Emeth's 14 human characters and the item icons are Cosmo's first-pass art.
- The darkness wisp is procedural code art.
- Characters appear in the CAST gallery only (one frame); they don't walk in the world yet.
- Journal quests for Acts III–V wait for those native acts.
