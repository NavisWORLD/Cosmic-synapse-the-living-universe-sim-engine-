# Lost Cosmos handheld link

The Living Universe HANDHELD pane runs one Lost Cosmos cartridge in an isolated emulator and can place the player's living creature into that cartridge's save.

## Which version this follows

Committed Lost Cosmos **11.1.1** is the branch `feature/lost-cosmos-v11-enhanced-001` (pull request #20, "Lost COSMOS V11.1.1 — full visual QA and Delta-safe polish"). The native pause layout landed in commit `3f4f2c9`. There is no git tag and no GitHub release named 11.1.1. The only published releases are the older Eridoria v7 line.

The uncommitted V11.1 Content Bible described in `docs/V11_1_CONTENT_QA_RESUME.md` is not on any branch, tag, release, or open pull request, and it was not present on disk. This link does not copy that work. It leaves the Bible's SRAM reservations empty so a later rebase can land:

| Region | SRAM bytes | Status |
| --- | --- | --- |
| Main page, including the LCR1 roster at 1024 | 0–8191 | unchanged |
| Journal banks | 8192–24575 | unchanged |
| Journal metadata `LCJ8` | 24576–24703 | unchanged |
| Gap after journal metadata | 24704–24831 | left empty |
| Living-link mailbox `LCX1` | 24832–25475 | new, 644 bytes |
| Gap before the first content-bible slot | 25476–25599 | left empty |
| Content-bible `LCM1` slots | 25600, 27648, 29696 | not used |
| Content-bible `LCEX` / `LC11` | 6208–6399 and 6400–7167 | not used |

The web pane lives in the same change as the cartridge because `main` has the same Living Universe page and no GBA source. Rebase onto a later 11.1.1 by keeping `lc_mailbox.h` and the three call sites in `lost_cosmos_v5.c`: `save_game` refreshes before it encodes, `lc_restore_roster` refreshes without consuming, and `init_new_game` clears the live art flag. Likely conflicts are those functions plus the party page and Beast Box page.

## What crosses over

The browser writes a 32 KiB save that is `0xFF` except for the mailbox. It does not write the LCR1 roster. The cartridge parses BCP1, calls the existing `lc_add_import`, and the normal save path writes the roster. Focus, calm, and spark are integers from 0 to 100 derived from band power. Raw samples are not an input to the encoder and are not stored in the save.

A fresh mailbox has flags `1` (pending). After the creature is in the party and the game saves, flags become `4` (consumed). The profile stays in the mailbox so the field sprite can load again on a later boot.

## Run

From the repository root, with `clang`, `lld`, `llvm`, and `python3` available:

```bash
bash scripts/build-lost-cosmos-arcade.sh
npm run prepare:web
npm run serve
```

Open http://127.0.0.1:7070/ , choose INITIATE SIM EARTH 7.08, then HANDHELD. Consent, use the simulated headband or a Muse headband, then Bring creature in and Start cartridge. Inside the game, start a new game. The creature is on the field, the party page, and the Beast Box page.

`arcade/lost-cosmos/index.html?demo=1` uses the shared EARTH fixture and starts the cartridge without a sensor.

The ROM at `arcade/lost-cosmos/rom/lost-cosmos.gba` is built from source and is not committed. The header still contains the Nintendo logo bitmap produced by `build_rom_v5.py`. No commercial ROM and no Nintendo BIOS are included. EmulatorJS 4.2.3 is GPL-3.0 and stays under `arcade/third_party/emulatorjs`, loaded only inside the iframe.
