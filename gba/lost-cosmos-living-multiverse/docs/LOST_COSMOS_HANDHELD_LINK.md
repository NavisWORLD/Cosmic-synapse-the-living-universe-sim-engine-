# Lost Cosmos handheld link

The Living Universe HANDHELD pane runs one Lost Cosmos cartridge in an isolated emulator and can place the player's living creature into that cartridge's save.

## Which version this follows

This link includes the current **V11.1 Content Bible** from `feature/lost-cosmos-v11-enhanced-001` (pull request #20): 100 items, 100 characters, 100 skills, eight worlds, the upgraded menus, and three CRC-protected save slots. The integration baseline is commit `345dd3c`.

The mailbox coexists with the Content Bible without moving any historical SRAM offsets:

| Region | SRAM bytes | Status |
| --- | --- | --- |
| Main page, including the LCR1 roster at 1024 | 0–8191 | unchanged |
| Journal banks | 8192–24575 | unchanged |
| Journal metadata `LCJ8` | 24576–24703 | unchanged |
| Gap after journal metadata | 24704–24831 | left empty |
| Living-link mailbox `LCX1` | 24832–25475 | new, 644 bytes |
| Synapse OS cage `LCG1` | 25476–25539 | optional 64-byte epoch record, read by the cartridge |
| Gap before the first content-bible slot | 25540–25599 | left empty |
| Content-bible `LCM1` slots | 25600, 27648, 29696 | owned by V11.1 manual saves |
| Content-bible `LCEX` / `LC11` | 6208–6399 and 6400–7167 | owned by V11.1 export and progress |

`save_game` refreshes the mailbox before encoding the roster, `lc_restore_roster` restores local mailbox art, and `init_new_game` resets its runtime flags along with V11.1 progress. The current PARTY and BEAST BOX pages show the mailbox callsign and truthful `BEAST IMPORTED` / `LOCAL MAILBOX` status. The 32px field sprite supplies a 64px menu portrait and an affine battle canvas using reserved matrix 4. Artwork and public exports are selected by identity, so a mailbox creature can coexist with the compiled Miraby snapshot.

## What crosses over

The browser writes a 32 KiB save that is `0xFF` except for the mailbox. It does not write the LCR1 roster. The cartridge parses BCP1, calls the existing `lc_add_import`, and the normal save path writes the roster. Focus, calm, and spark are integers from 0 to 100 derived from band power. Raw samples are not an input to the encoder and are not stored in the save.

A fresh mailbox has flags `1` (pending). After the creature is in the party and the game saves, flags become `4` (consumed). The profile stays in the mailbox so the field sprite can load again on a later boot.

CI tests both builds: the browser cartridge with runtime imports only and the native cartridge with the compiled snapshot. Real mGBA verifies the callsign, portrait, Beast Box status, roster checksum, a V11.1 manual slot, and a second cold boot without duplicate creatures. Native C tests also check battle art and preservation of the exported public identity.

## Run

From the repository root, with `clang`, `lld`, `llvm`, and `python3` available:

```bash
bash scripts/build-lost-cosmos-arcade.sh
npm run prepare:web
npm run serve
```

Open http://127.0.0.1:7070/ , choose ENTER CUTE BEAST POCKET REALITY, then PLAY GBA or MODELS. Consent, use the simulated headband or a Muse headband, then bring a creature in and start the cartridge. Inside the game, start a new game. The creature is on the field, the party page, and the Beast Box page. A world update after Send to handheld keeps the mailbox confirmation on screen.

`arcade/lost-cosmos/index.html?demo=1` uses the shared EARTH fixture and starts the cartridge without a sensor.

The MODELS tab opens Synapse OS. A Beast Box `.qbeast` snapshot, a `quantum-beast export-gba` zip, a BCP1 file, an OpenAI-compatible or Ollama reply, or a checksummed share can become one Lost Cosmos V11.1 creature. The page rebuilds stats from the seed. A model may only suggest a callsign and a public note. Trade uses a checksummed `.qbeast` share, a `#lcqt=` link, or a QR symbol of that link, and the same mailbox the cartridge already imports. Optional passphrase seals stay in the browser.

Synapse OS keeps each beast in a ledger with the permissions sense, world, and memory. Epoch, layer, and points are the unbounded progression. The cartridge stores the epoch in a 32-bit field and the layer and points in 0..999, so the save cannot overflow. Raw sensor samples are not written.

What still needs the owner:

- An OpenAI-compatible or Ollama endpoint must send CORS headers for this site. No API key is stored in the repository. A key typed into the page lives only in that session.
- Muse plug-and-play on the public HTTPS site needs Chrome or Edge and a click on the Muse button. The simulated headband does not need hardware.
- A person can copy a share file before sending it. This static site can refuse a second identity in one save and in one browser ledger. It cannot burn a ticket worldwide.
- Beast Box's 64px tile sheet is checked when the zip includes it, then left out of the 32px mailbox. The cartridge paints a procedural sprite from the verified family and hue.

The ROM at `arcade/lost-cosmos/rom/lost-cosmos.gba` is built from source and is not committed. The header still contains the Nintendo logo bitmap produced by `build_rom_v5.py`. No commercial ROM and no Nintendo BIOS are included. EmulatorJS 4.2.3 is GPL-3.0 and stays under `arcade/third_party/emulatorjs`, loaded only inside the iframe.
