# Lost Cosmos V11.2 Spark

The Sol cartridge keeps its world, maps, story, nursery, lineages, and Beast Box mailbox. This release replaces the tiny imported orb with the Spark Beast renderer.

- Every island line (three stages), the twelve rares, and Charlet's three forms are baked as GBA 4bpp tiles: a 32×32 field sprite with a walk frame, and a 64×64 portrait with its own palette.
- `scripts/bake-spark-gba.mjs` rebuilds those tiles from the web renderer and the recorded quantum-run table. A later beast added to that table flows into the next ROM.
- A cage beast sent over LCX1 uses its baked portrait and walk cycle when its callsign is in the table. Any other cage beast keeps the 32×32 sprite attached to its mailbox record, expanded for the party, bestiary, nursery, and battle. The procedural orb is only the fallback when a record has no art.
- Battle shows the 64×64 portrait at 1:1. Overworld followers and wild encounters keep 32×32 field sprites inside the existing OBJ tile slots.
- Header title `COSMOS V11.2`, software version 22. Saves, LCX1, LCG1, and LCM1 are unchanged.
