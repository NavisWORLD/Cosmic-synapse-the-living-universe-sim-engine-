# SIM EARTH // THE LOST COSMOS V3: Cosmic RPG

Native Game Boy Advance action RPG built as a continuation of the verified Lost COSMOS V2 universe. Developed for Delta and compatible `.gba` emulators; This source accompanies the V3 release cartridge that passed a scripted two-boot mGBA run in GitHub Actions 36098528364. Extended manual play and Delta iPhone control feel are still untested.

## World & gameplay

- Full scrolling 64×64-tile world maps and OAM sprites across six explorable regions: Origin Earth, Ember Axis, Tide Memory, Bloom Z, Black Garden, Synapse Crown.
- Top-down 2D exploration, animated player, improved equipment-aware character sprite, collision, hazards, interiors, 3 depth layers, flyable interplanetary ship and contextual events.
- Sword/weapon attacks with animated slash, enemy chase/collision/damage, six monster families, elite Axis guardians, drops, XP and level progression (cap 30).
- HP, MP, STR, DEF, MAG, credits, potions, ether, star shards and quantum cores; equipment includes Rust Blade, Ember Saber, Tide Mail, Bloom Charm and Crown Edge.
- Four spells: Synapse Pulse, Ember Bolt, Tide Ward, Bloom Nova; axis keys unlock corresponding equipment/spells.
- Ten-tab pause menu includes map, buddy, stats, items, equipment, memories, keys, story, settings and save.
- Story, autonomous buddy preferences, player-controlled Crown endings and persistent postgame sandbox remain from V2.

## Controls

| Control | Surface | Space |
| --- | --- | --- |
| D-pad | Walk | Fly/steer |
| B + D-pad | Run | Fly faster |
| A | Interact near objects; talk to COSMOS if nearby and safe; otherwise sword attack | Land near a planet |
| L | Potion (or lower layer at a lift) | — |
| R | Cast equipped spell (or upper layer at a lift) | — |
| Select | Place beacon | — |
| Start | Pause/menu/save | Pause/menu/save |

In PAUSE → ITEMS, use D-pad to select an item and A to consume/refine it. In EQUIPMENT, select a slot and A to cycle available gear/spells. In SETTINGS, choose AUDIO, Q BUDDY, AUTO TALK to toggle them.

## COSMOS and recorded workloads

The COSMOS companion has a visible sprite, persistent memories, autonomous goal scoring/hysteresis and a lightweight 12D→42D→54D state loop. Optional **Quantum Workload Replay** repeatedly consumes 8-byte windows from the complete frozen 8,192-byte tape provided for the earlier cartridge. It computes mean, spread, parity, phase, coherence *proxy* and burst *proxy* features to modulate COSMOS movement, goal selection, contextual dialogue and combat assist. These features are game algorithms, not measured quantum coherence/entanglement. This offline GBA game cannot submit real IBM/Rigetti jobs or provide unconstrained generative speech, and historical tape provenance has not been independently reverified. Disabling Q BUDDY disables the replay's effect on buddy behavior; the game may still use frozen seed bytes in baseline world/state logic.

## Saves

`SRAM_V113` with `LCV3` magic; stats, XP, equipment, inventory, buddy settings, workload summaries and progression are persisted. There is **in-ROM migration logic for valid LCV2 SRAM bytes**. Delta may keep different ROMs in separate save slots—migration will work only if V2 `.sav` data is actually attached/imported to V3. Back up V2 saves before trying.

## Build & tests

Requires clang (ARM7TDMI/arm-none-eabi), LLD, LLVM objcopy, Python 3, and a shell. In this directory run `./build_v3.sh` for the cartridge, `python verify_routes.py` for map/trigger/elite accessibility checks, and `python host_qa_v3.py` to execute the same gameplay C against mapped host RAM across two fresh processes with SRAM persistence. `QA=1 ./build_v3.sh` builds an emulator autorun cartridge, **not the normal playable release ROM**.

`host_qa_v3.py` tests the authored route using internal game functions; it is not a substitute for human control feel, real frame timing or mGBA/Delta testing. See `VERIFICATION_V3.md`.