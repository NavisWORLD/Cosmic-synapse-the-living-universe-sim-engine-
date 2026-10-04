The playable ROM is built from the Lost Cosmos C source. It is not committed.

From the repository root:

```bash
bash scripts/build-lost-cosmos-arcade.sh
```

That writes `lost-cosmos.gba` in this directory. The file is original homebrew (game code `ERL8`). The header still contains the Nintendo logo bitmap produced by the existing `build_rom_v5.py`, which real hardware checks at boot. mGBA and EmulatorJS also boot that header. No commercial ROM and no Nintendo BIOS are used.
