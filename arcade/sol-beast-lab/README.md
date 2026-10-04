# Sol Beast Nursery

Original work for **Cory Davis / NavisWORLD**, continuing LOST COSMOS V11.1.

Open `arcade/sol-beast-lab/index.html` through the existing web server or published Pages site. No build step, external fonts, paid service, or account is required. For local use, run `python3 -m http.server 8765` from the repository root and visit `http://localhost:8765/arcade/sol-beast-lab/`.

Choose an island, a public seed phrase, and three 0–100 game cues. Hatch to keep that immutable companion on this device. Download its receipt to recreate it elsewhere. Stage buttons preview all forms; the displayed level and bond remain the values read from your native game, or the starting values before a game save is read. Nursery gestures are playful animations, not free native XP or bond.

## Lineages

| Island | First light | Growing together | Full bloom | Native import family |
| --- | --- | --- | --- | --- |
| Eridoria Prime | Cinderkip | Hearthpaw | Solwarden | Plasma |
| Hollow Verdance | Leaflet | Mossmew | Verdantwhisk | Memory |
| The Crown | Coronet | Halofox | Crownkeeper | Starlight |
| The Pale Expanse | Flurry | Snowfluff | Glacierbun | Aurora |
| Rust Meridian | Coglet | Coppercub | Gearheart | Signal |
| Cinder Drift | Pipflare | Emberwing | Sunphoenix | Plasma |
| Umbral Deep | Duskdrop | Velvetmoth | Moonveil | Void |
| The Shattered Reef | Bubblefin | Tidepup | Reefwarden | Nebula |

There are eight visual lineages and seven existing native BCP1 families. Prime and Drift intentionally share Plasma's game rules; their art and identities differ. This keeps existing imports and saves compatible.

## Actual mapping

The archive is copied byte-for-byte from the native cartridge's `qseed.h`: 8,192 bytes, SHA-256 `9bcecc3732fe48107554cc2041cff6088f418290fb850ec0c9b89cdc375f54c8`. The page verifies that hash before hatching or exporting. It uses a deterministic 32-byte window with wraparound. The original repository labels these as IBM measurements; original job provenance is not independently verified here. There is no new hardware run or live quantum connection.

The window, island, and public seed phrase establish the balanced genesis. Domain-separated FNV-1a hashes of that genesis plus the three cues establish the public ID and native art seed. These 32-bit identifiers are stable game identifiers, not cryptographic ownership proofs or a promise of universal uniqueness.

Each stat starts within 20–80, and the ten-stat budget always totals 500. For each cue, `trunc((cue-50)/5)` transfers up to ten points per pair, respecting the bounds. Below 50, the direction reverses.

| Cue | Receives points above 50 | Donates those points | Visible gene |
| --- | --- | --- | --- |
| Focus | Signal, Memory | Chaos, Evolution | Full-bloom cyan crest at focus ≥50 |
| Calm | HP, Resonance | Chaos, Curiosity | Rounder body at calm ≥50 |
| Spark | Energy, Agility | Memory, Stability | Fuller Prime ember tail |
| Archived genome | Balanced base stats and temperament | Fixed genesis budget | Tint, width, forehead mark |

Muse mode reuses the existing local Muse client. Its focus/calm/spark cues are beta/alpha/gamma power proportions, not validated psychological measurements. Simulate uses an explicit simulated band window. Receipts include only these derived cues, provenance label, public seed/genome information, and public traits. They never include raw EEG or credentials.

## Native round trip

Starter `.sav` exports are exactly 32,768 bytes. They contain only the existing 644-byte LCX1 record at offset 24,832; remaining bytes are erased (`FF`). The cartridge validates and imports BCP1 itself. The nursery does not author an LCR1 roster or fabricate native levels.

Use a starter save for a new game. To preserve an existing journey of this same creature, export its **battery save** from the emulator, read it in the nursery, and download **Updated journey .sav**. The roster CRC, public ID, native species, and immutable game seed must match. Every byte outside LCX1 is copied unchanged, including journals and all three manual save slots. An emulator save state is a different format and is rejected. Read the matching companion receipt first if using another device.

Custom sprites use the existing 32-byte RGB5 palette and 512-byte, 32×32, 4bpp tile area. Pixels never use palette entries 13–15. Those entries hold a private-to-this-renderer signature and visual genes; they do not add new SRAM fields. A nursery-only native hook regenerates art when the real roster stage changes. C and JavaScript renderers match exactly; unrelated imports retain their original supplied art.

Train in PARTY → A ACTIONS → TRAIN using three Scrap or two campaign Star Shards. XP comes from play. Evolution uses the existing native gates: LV 12 / Bond 55, then LV 28 / Bond 80. A Heartwood Sigil is required when the public Evolution stat is below 50. Native name, identity, seed, level, and bond persist normally. The nursery keeps its lineage names; it reads native growth, not a custom renamed display name.

## Verification

- `node --test arcade/sol-beast-lab/design.test.mjs`: stable births, archived bytes, eight silhouettes, three stages, balanced imports, cue directions, corrupt/wrong-save rejection, byte preservation.
- `python3 tests/test_sol_beast_art.py`: 192 C/JavaScript frame comparisons.
- `python3 tests/test_sol_nursery_native.py`: actual native C import, both evolution stages, save/load identity, read-only drawing, unrelated art preservation (simulated MMIO).
- `python3 tests/test_mgba_sol_nursery.py`: controller-only genuine mGBA import, exact native tiles, and a fresh cold boot, for both cartridge variants.
- Existing full eight-region controller pilgrimage can accept `--starter path.sav`, verifying genuinely earned progression with a nursery creature.

Physical Muse pairing, real GBA hardware, and iPhone Delta device acceptance are not claimed by these automated checks. The beast is a game companion, not a conscious being or a medical device.
