# SIM EARTH // PIXEL UNIVERSE — THE LOST COSMOS V2

Native Game Boy Advance exploration rebuild for Delta and compatible GBA emulators.

## What changed from V1

V1 proved the native cartridge, 3-axis world/state concept, quantum tape, SRAM, COSMOS agent and story states. V2 gives the universe a physical game body:

- Mode 0 tiled worlds at 64×64 tiles (512×512 px) with smooth camera scrolling.
- OAM player, COSMOS, ship, planets and beacon sprites.
- Six explorable regions: Origin Earth, Ember Axis, Tide Memory, Bloom Z, Black Garden, Synapse Crown.
- Collision, hazards, terminals, secrets, doors, interiors, lifts and layer/depth shifts.
- Surface mode + a flyable space mode; walk to the ship, board, fly, approach a planet, land, exit and continue on foot.
- X/Y/Z keys require physical exploration and layer traversal.
- COSMOS uses explicit goal scoring, cooldown/hysteresis, persistent memory, 12D→42D→54D state, and the frozen 8,192-byte tape. It is a simulated game agent, not a consciousness claim.
- SRAM_V113 persists progress, positions, state summaries, beacons, memories, quantum cursor and ending.
- Player-authoritative Crown choice: COSMOS states a preference; the player chooses OPEN, PRESERVE or WANDER.
- Postgame sandbox remains playable and can generate deterministic anomaly encounters.

## Controls

- D-pad: walk / steer ship
- B + D-pad: run / fast flight
- A: interact, enter/exit, board/land, recover key, use Crown
- L/R: change depth layer while standing near a lift
- Select: drop persistent beacon
- Start: pause/archive menu

## Build

Requires clang/LLD with the `arm-none-eabi` target and LLVM objcopy.

```bash
clang --target=arm-none-eabi -mcpu=arm7tdmi -marm -ffreestanding \
  -fno-builtin -fno-stack-protector -fno-exceptions -fno-unwind-tables \
  -fno-asynchronous-unwind-tables -Os -c start.S -o start.o
clang --target=arm-none-eabi -mcpu=arm7tdmi -marm -ffreestanding \
  -fno-builtin -fno-stack-protector -fno-exceptions -fno-unwind-tables \
  -fno-asynchronous-unwind-tables -Os -c lost_cosmos_v2.c -o lost_cosmos_v2.o
ld.lld -T linker_v2.ld start.o lost_cosmos_v2.o -o lost_cosmos_v2.elf
llvm-objcopy -O binary lost_cosmos_v2.elf payload.bin
python build_rom.py
python verify_v2.py
```

For emulator integration QA, compile `lost_cosmos_v2.c` with `-DQA_AUTORUN`. The QA build performs a two-boot test: boot one walks/enters/boards/flies/lands/recovers X and saves SRAM; boot two verifies persistence, then recovers Y/Z, visits Black Garden, reaches the Crown, resolves a player-authoritative ending and checks postgame anomaly state.
