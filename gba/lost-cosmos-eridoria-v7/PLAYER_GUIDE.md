# LOST COSMOS V7 — Player Guide and Release Notes

**Edition:** *Eridoria: The Eight-World Campaign* — native GBA ROM (240×160). Original V6 remains independent.

## Before playing in Delta
Import the new V7 `.gba` as a separate game. Back up existing save files before trying any migration from older editions. The engine contains legacy migration logic, but the app's ROM/save-file association and touch/audio handling still need real iPhone smoke testing.

## Controls
- D-pad: move, or steer the ship. **B + D-pad:** run.
- **A:** interact with NPCs, doors, runes, treasure, or attack in exploration. **B + A:** heavy attack.
- **R:** cast the selected spell. **L:** use a potion unless standing at a depth lift.
- **Start:** maps, stats, inventory, equipment, quests, Eridoria journal, NPC log, save and settings.
- **Select + A** near an enemy: optional full-screen tactical encounter, with FIGHT / MAGIC / ITEM / TALK / RUN. A confirms and B can guard.
- Dodge: **B + Select**, or **Select alone** if Settings → TOUCH MODE is enabled.
- The player's choices, equipment and quest progress are game-authoritative. Quantum Buddy operates on reproducible offline workload replay, not live quantum hardware.

## Spoiler-light story progression
1. **Origin Earth / Eridoria.** From the Origin landing area, find the Brindlemark gate near the southeast archive area. Meet the residents and speak to Astrid to start Arin's Heart quest.
2. **Oakwood Market.** Meet Lord Ravenswood to unlock the mountain temple. Trade in the real shop: potion 5 credits, ether 7 credits; sell a Star Shard for 3, or a Quantum Core for 12.
3. **Cragstone Temple.** Activate the four carved runes in the order **SKY → ROOT → HEART → STAR**. Confront Malakar in the chamber, then physically claim the Heart of Eridoria.
4. **The Axis planets.** Continue the existing explorable Ember Axis, Tide Memory and Bloom Z adventures for the X, Y and Z relics. On Tide, stabilize the Chronoheart after acquiring Y. The Black Garden's Voidward Sigil requires the Heart and all three Axis relics.
5. **Hidden City and Dream Veil.** Discover the Hidden City on Origin and enter Dream Veil after claiming the Heart. For Wisdom, the answer is **Shooting Star (RIGHT)**. Courage requires defeating Dream's guardian; Unity follows Wisdom and Courage, unlocking Eldoria.
6. **Eldoria.** Restore the Earth, Water, Fire and Air shrines; the fourth shrine is guardian-gated.
7. **Synapse Crown.** With the Heart, Chronoheart, Voidward Sigil, Dream Trials, four elemental shrines and all three Axis Keys, defeat the Crown sentinel to restore the Lattice. **The player—not COSMOS—chooses** OPEN (left), PRESERVE (up) or WANDER (right). Continue in the postgame.
   
## Design and limitations
This release implements a finishable eight-world **condensed five-act campaign**, not every scene in the much longer Eridoria manuscript. The optional encounter system coexists with Zelda-style real-time exploration combat. Full seventeen-guardian playable campaigns, online multiplayer and all proposed standalone act bosses are not implemented; avoid presenting them as if they were.

The 8,192 archived quantum-workload-derived input bytes are unchanged. The accompanying code and verification scripts are included for inspection and reproduction. GitHub's two-boot mGBA script validates authored progression and save persistence. Extended free-roam balance, actual Delta touch/audio response and physical real-hardware compatibility require human device testing.
