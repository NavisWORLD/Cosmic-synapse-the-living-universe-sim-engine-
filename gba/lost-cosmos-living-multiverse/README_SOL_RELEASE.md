# LOST COSMOS · Sol edition

For **Cory Davis / NavisWORLD**. Continues the merged PR #21 V11.1 game.

The original campaign, eight Signal Road regions, creatures, imports, and historical save layout remain playable. This update adds earned contextual goals, an accessible local landmark map, exact workshop costs after discounts, and native art evolution for creatures created in Sol's new nursery. Grok's concurrent Pocket Reality / Synapse OS branch was inspected read-only and was not modified.

## Play

Open `LOST_COSMOS_SOL.gba` in a GBA emulator. The game retains cartridge code `ERL8` and 32 KB battery SRAM. Keep your existing battery save when replacing the ROM. Optional `SOL_CINDERKIP_STARTER.sav` starts a **new** journey with the new Prime companion; do not attach it over an existing journey you intend to keep.

- D-pad: move and navigate menus. Hold B to run; A interacts or attacks. START opens the menu.
- In Brindlemark, use the stone arch at tile **34,44** and press A to enter the eight Signal Road islands.
- MAP → START opens local landmarks immediately. `A` marks you; `C` the Signal Core; `M` the Memory Echo; `F` camp; `B` beacon; `>` east gate; `R` return. The Track skill additionally reveals foes. B returns to the world map.
- The field's `NEXT` line follows earned progress: core, echo, three foes, beacon, gate, and final bosses. Tracked side quests alternate into that line. The action line identifies nearby interactions.
- The workshop shows actual Scrap/Herb/Core costs, including Artisan's Hands and Builder's Clasp discounts, before you build.
- PARTY → A ACTIONS → TRAIN bonds your active creature. EVOLVE opens the existing level/bond gate. Use SETTINGS to save/load any of the three manual slots.

## Create your beast

Visit the **Sol Beast Nursery** at `arcade/sol-beast-lab/` on the published site. Its [design guide](../../arcade/sol-beast-lab/README.md) contains the exact signal/seed mapping, all 24 named forms, and the import/progress round trip.

Hatch a companion, keep its JSON receipt, and download its starter save. After playing, read that companion's battery save in the nursery to see earned growth and export an updated journey without rewriting your roster or manual slots. Nursery pet/play/rest gestures animate the creature; native XP and bond are earned in the game.

The preserved seed is archived replay. Raw EEG is not exported. The game does not imply live entanglement, consciousness, or a medical assessment.

## Acceptance scope

Use the matching automated report for the delivered ROM's exact SHA-256. Genuine mGBA tests use ordinary controller input and read-only state inspection, without memory writes or emulator save states. Host tests use simulated MMIO and are identified separately. Acceptance includes native boot/audio/movement, menus, public imports, the eight-region route, ten bosses, crafting, evolution, save slots, cold boots, and the previously accepted Act I/II, Eldoria and Hollow Grove routes.

This release does not assert a physical iPhone/Delta or Muse hardware test, nor exhaustive manual completion of the original five-act manuscript campaign.
