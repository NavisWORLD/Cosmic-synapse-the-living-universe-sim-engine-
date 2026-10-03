# Lost COSMOS V11 — Quantum Beast world bridge

V11 connects the three previously verified layers without replacing any of them:

1. **SOL V3 RPG systems** — inventory, equipment, XP/levels, enemy drops, spells, ship travel, endings and `SRAM_V113` migration.
2. **Astra V10.8 native presentation** — eight biome palettes, 192 extra background tiles, layered landmarks/terrain, animated scenery, expanded hero/NPC/creature art, story/cinematics and later campaign work.
3. **Quantum Beast Bridge** — a provider-neutral `.qbeast` is verified outside the cartridge, exported to public BCG1/BCP1 + pixel data, then imported at build time.

The cartridge never runs cloud/model inference and never receives private owner memory, credentials or model authority.

## One-command build

Install Quantum Beast Bridge 1.0.1 (or newer compatible v1), then from `gba/lost-cosmos-living-multiverse`:

```bash
python3 tools/build_quantum_beast_v11.py /path/to/my-beast.qbeast --out artifacts/my-beast
```

Or use a previously exported public GBA pack:

```bash
python3 tools/build_quantum_beast_v11.py /path/to/beast-gba.zip --out artifacts/my-beast
```

For a signed Beast, pass the trusted publisher public key with `--trust-key` when using a `.qbeast` input.

Outputs include the native `.gba`, ELF, generated public `imported_companion.h`, import receipt and a V11 build receipt.

## Native world behavior

The imported public profile becomes a genuine `LcCreature` in the 12-slot roster. Its deterministic BCP1 stats seed HP/attack/defense/affinity and its identity/seed survive game save/load. The original four 64×64 Beast Box mood frames remain the collection portrait.

V11 additionally derives four **32×32 hardware-native field frames** from those verified 64×64 pixels. The active imported Beast now uses its own Beast Box art while following the player in exploration and while appearing in tactical battle UI. Native species retain their existing three-stage art and behavior.

The downsample is deterministic nearest-neighbour sampling using only the original 16-color Beast palette; no generated replacement artwork is introduced.

## Authority boundary

`MODEL != MEMORY != CREATURE IDENTITY != STATE != AUTHORITY` remains enforced. The GBA receives only a public snapshot appropriate for the game. Any future re-import of GBA progress must be a new verified event rather than rewriting the external Beast lineage.
