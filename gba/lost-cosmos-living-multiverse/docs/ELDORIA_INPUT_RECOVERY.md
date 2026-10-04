# Eldoria shrine input recovery

The native V11.1.1 game lost the second A press at Eldoria's Water shrine because journal_bank_valid recomputed IEEE CRC32 bit by bit over both 8 KiB snapshot banks. On the actual ARM7TDMI core, the whole ordinary 12-frame press could occur while the main loop was inside that scan.

A 256-entry table performs the same IEEE CRC32 over the same SRAM bytes. Both banks are still validated on each journal operation. The primary page, alternating banks, commit marker, sequence selection, and every historical offset are unchanged.

Before the execution workspace disconnected, a fresh real libmGBA controller chain passed:

- Act I, followed by a separate cold boot.
- Act II and its cold boot.
- Eldoria: Earth, Water, Fire, and Air; all four earned bits survived a cold boot.
- Hollow Grove: mirror, Wraith, and Earth relic; earned state survived a cold boot.
- Hosted journal tests: newest committed save, corrupt newest bank, torn metadata, and legacy saves without a journal.

Controller tests used the unmodified built ROM, normal button presses, and read-only observations. No memory writes or savestates were used. The checked local ROM SHA-256 was 8e36b41223608ebf5f7fdc9213047134827d3dd8f7f39a5aa03e1a0237b520ff.

Commands (from gba/lost-cosmos-living-multiverse):

```sh
python3 tests/test_mgba_act1_controller.py --out artifacts/shrine_fix_act1
python3 tests/test_mgba_act1_resume.py --out artifacts/shrine_fix_act1
python3 tests/test_mgba_act2_controller.py --act1 artifacts/shrine_fix_act1 --out artifacts/shrine_fix_act2
python3 tests/test_mgba_eldoria_controller.py --act2 artifacts/shrine_fix_act2 --out artifacts/shrine_fix_eldoria
python3 tests/test_mgba_hollow_grove_controller.py --eldoria artifacts/shrine_fix_eldoria --out artifacts/shrine_fix_grove
```

## Content pass status

Cory Davis' 2026-10-03 Content Bible is the continuation spec. Local work generated and checked all 100 item, 100 character, and 100 skill catalog entries, individual 4bpp sprite/icon mappings from the ten supplied references, and additive runtime modules. The menu implementation and end-to-end content verification were not complete when the execution service reported `environment_offline: Environment is not connected`.

Only the tested journal fix is included in this commit. This is not the completed V11.1 content release. The incomplete local content work must be recovered and compiled before packaging a new playable ROM. Do not replace the original campaign IDs, SRAM offsets, QSEED, imported identity, or private Beast Box ledger boundaries.
