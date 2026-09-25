# LOST COSMOS V5.1 — native GBA cinematic/playtest edition

Preserves original V5 as a separate working edition. Original ROM, all six worlds, NPCs, items, equipment, magic, physics, quests, the archived 8192-byte workload-derived input and its deterministic Q Buddy remain independent from this cinematic branch.

## Verified new features

- Eight deterministic, distinct 960×640 original painterly scene sources converted into authentic 240×160 GBA 4bpp indexed palettes/tiles (≤512 unique tiles per scene). An on-cartridge BG2 cutscene layer drives intro, ship warp, planetary arrival, axis discovery and Crown finale.
- PSG music on GBA square channel 1, effects/dialogue on square channel 2; real mGBA captured non-silent PulseAudio loopback.
- Optional Settings > TOUCH MODE, offering single Select dodge, B+Select beacon and hold-A heavy while retaining original combat chords; off by default and checksum-safe for older saves.
- GBA header `LOSTCOSMOS51`/`LC51` so importing to Delta doesn't silently replace `LOSTCOSMOSV5`. Original internal `LCV5` SRAM save format remains compatible.

**Successful two-boot native mGBA build and real screenshot capture:** https://github.com/NavisWORLD/Cosmic-synapse-the-living-universe-sim-engine-/actions/runs/36107910235

**Successful independent real mGBA/PulseAudio audio capture:** https://github.com/NavisWORLD/Cosmic-synapse-the-living-universe-sim-engine-/actions/runs/36108157580

Exact certified player ROM SHA-256: `53f7731240790bd41fd96fe027d34124b0461ecee98998c9783563e98ba18642`.

Source is editable under `source/` and is regenerated from the hash-verified V5 base with the three scripts stored in `bootstrap/` compressed transport. Release ROM artifact in the green two-boot run; the CI QA ROM must never be distributed as the playable release.

**Status:** native mGBA passes and its audio loopback contains real game sound. Real Delta/iPhone touchscreen, volume and UI positioning are **not remotely testable** and require owner device smoke testing. The screenshots show real graphical advancement with further in-world terrain/HUD artwork polish still desirable; 4K/native 3D and live quantum hardware are not claimed.
