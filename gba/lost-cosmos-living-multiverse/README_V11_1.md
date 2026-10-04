# LOST COSMOS V11.1 — The Eight Signals Road

Cory Davis / Cosmic Synapse / Eridoria. Native Game Boy Advance upgrade built from the supplied Content Bible and sprite references.

Open **LOST_COSMOS_V11_1_CONTENT.gba** in a GBA emulator. In Brindlemark, follow the road south of the grove to the signal arch, just east of the central road. Its tile position is 34,44. Press A beside it to enter Eridoria Prime's new road. The original campaign is still available; the return gate leads back to Brindlemark.

## Play

| Button | Field | Battle | Menus |
|---|---|---|---|
| D-pad | Walk | Choose action or target | Choose an entry |
| A | Talk, collect, enter a duel | Confirm | Confirm |
| B | Run with D-pad | Guard; back from a submenu | Back |
| START | Pause | — | Local Track map when offered on MAP |
| L | Use a Potion | — | Previous tab |
| R | Open Skills | — | Next tab |
| SELECT | Scout or Track | Equipped ultimate at full charge | Context action shown on screen |

START opens the familiar two-column landing menu. SELECT there opens STATUS. Inside a content page, L/R visits STATUS, ITEMS, GEAR, SKILLS, PARTY, BEASTS, QUESTS, MAP and SYSTEM. Left/right changes item categories or skill types. The original campaign's pack, equipment, journal and world map remain available through the on-screen context actions.

Each region asks you to find its Signal Core and Memory Echo, face three foes, and return its beacon's light. A lit beacon becomes a fast-travel destination. Vesper holds the Z Key for the Crown. The Meridian Core's forges must be dismantled first; the Drowned God's tide anchors matter more than its body. Keep carried echoes for The Quiet.

Campfires restore HP/MP and advance the game day. The Elder's Heartwood trial rewards gentleness: mend the wounded root. Sable's road leads to the First Outcast. The Confessor lets you choose whether to lay an echo to rest.

## Inventory, abilities and companions

- The bag holds 40 distinct item stacks, or 60 with Pack Mule equipped. Key items and equipped gear cannot be dropped. Quest/boss rewards wait safely when the bag is full; free space to claim them.
- Equip one weapon, armor and charm. Assign four spell shortcuts, four passives and one ultimate. Locked abilities show their actual requirement.
- Rust Meridian's Tinker's Widow gives the Builder's Kit. Assemble opens the workshop. Craft the Hand, Goggles and Clasp to finish the Builder's set; the Clasp saves one material in later recipes.
- PARTY supports active-companion selection, training, rename and eligible evolution. First evolution needs level 12 and bond 55; the next needs level 28 and bond 80. Some imported profiles also need the Heartwood Sigil. Evolution and rename preserve the public identity.
- Field followers remain small. The larger portrait appears in PARTY, dialogue, evolution and Beast Box; battle uses separate field-derived art and reserved affine slot 4.

The catalogs contain all 100 items, 100 characters and 100 skills. Original reference cells are cropped, made transparent and packed as native 4bpp tiles; labels and full sprite sheets are not rendered as actors. The art manifest records adapted cells where a matching supplied character was absent. The eight additional regions use room IDs 70–77, retaining the original campaign's world identities.

## Saves

SYSTEM offers three CRC-checked battery slots. Autosaves follow encounters and story rewards. A game-over retry restores the saved signal; it does not fabricate lost progress.

Historical V10.8 SRAM fields and journal banks retain their offsets. New content is appended in disjoint pages. An emulator may associate saves with a ROM filename, so keep a backup of the original battery save and explicitly import it when moving to this cartridge. Corrupt new content pages fall back without overwriting the historical campaign data.

## Beast Box, offline

This cartridge carries the verified public **Miraby** snapshot. Beast Box is reached from SYSTEM or PARTY/SELECT. Its status describes the local snapshot and import/export state. The ROM has no network handshake and no private memory ledger. Miraby keeps its original public artwork as its game stage advances.

To export, select a bonded companion in PARTY and choose EXPORT TO BEAST BOX. Export the emulator's 32 KiB battery save, then run:

```bash
python3 tools/export_beastbox_v11.py --save your-battery.sav --out beast-public.zip
```

The resulting public package carries BCP1, empty guest BCG1, public pixels, immutable identity, display name and game progress with a receipt. To build it into an isolated copy of the supplied source:

```bash
python3 tools/import_beastbox.py beast-public.zip isolated-source/LOST_COSMOS_V10_SOURCE
cd isolated-source/LOST_COSMOS_V10_SOURCE
IMPORTED_BEAST=1 bash build_v5.sh
```

The importer checks the snapshot receipt and profile. The original Beast Box genesis format still undergoes its exact seeded validation. A matching existing identity keeps its local bond/progress on reimport; importing into a fresh roster restores the public exported progress.

## Build and verification

Install clang, lld, llvm and Python 3. From the source package:

```bash
cd LOST_COSMOS_V10_SOURCE
IMPORTED_BEAST=1 bash build_v5.sh
```

The historical build output filename is LOST_COSMOS_V10_OPENING_QA.gba; its cartridge title is COSMOS V11.1. Compare its SHA-256 with BUILD_RECEIPT.json. The original 8,192-byte QSEED is unchanged.

The evidence package records actual native mGBA controller inputs, framebuffer captures, native contract checks and cold boots for this ROM. The new route covers eight beacons and ten major bosses, crafting, companion evolution/export and all three manual slots. The retained original campaign checks cover Act I, Dream Veil, Eldoria's four shrines and Hollow Grove. This does not claim a full original five-act literary acceptance run or physical iPhone Delta testing. Extended player balance and device control feel remain to be reviewed.
