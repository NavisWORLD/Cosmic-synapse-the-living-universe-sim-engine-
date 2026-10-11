# Lost Cosmos V11.4: PROLOGUE "Ash in the Forge"

The first playable part of THE HEART OF ERIDORIA campaign spine (Q00-Q38), built
natively into the existing 240x160 cartridge. It uses the same art, music,
controls, creature collection and saves. The dialogue is original game-adaptation
text, written for the cartridge. It is not quoted from the owner's private manuscript.

## What you play (Brindlemark, then the Origin landing)

| Node | What happens | How it is earned |
|---|---|---|
| Q00 Wake at the Forge | Arin's furnace (18,43). A timed forge minigame: strike 3 times in the `+` zone. COSMOS wakes up under the anvil. | A at the furnace, then A in the zone. B steps away. |
| Q01 Save Brindlemark | Malakar's raid: three glitchlings appear near the square. | Field attacks or a SELECT+A duel. In the duel, TALK spares a glitchling at any HP (it flees and does not join). |
| (choice) | **Defend the storehouse** (credits +18, 1 ether) or **Carry the injured** (credits +10, 2 potions, more COSMOS trust). The Elder and Mira remember the choice. | UP/DOWN, then A. |
| Q02 Fix the Beacon | Mira (37,12) gives you her spare fuse. Turn the beacon's three crystal seats (33,10) LEFT, UP, RIGHT. A wrong turn sparks and resets the seats. | D-pad in the beacon panel. |
| Q03 Meet Astrid and Mira | Talk to Mira, the robed Traveler (23,28), and Astrid at the Origin (through the southwest gate). | The HUD objective tracks all three. |
| Q04 Launch LUNA-ARC | Board the ship on the Origin pad. Launch cards play, then the rewards: Forge Key, Arin's map, First Memory, COSMOS bond, LUNA-ARC passage. Q05 (Oakwood) becomes active. | A on the pad. |

The pause menu's QUESTS page now has a third view, **STORY** (LEFT/RIGHT cycles
ACTIVE / DONE / STORY). It lists every campaign node reached, with its state,
the live objective, and the prologue choice.

The prologue does not gate any existing route. The ship, gates and rooms behave
as they did in V11.3.

## Persistence

The state lives in LC11 page bytes 656-673. Those bytes were unused and zero in
every V11.0-V11.3 save, and they sit inside the existing CRC (0-763), so they
are copied by the three manual slots too.

- 656 'Q', 657 schema 1
- 658-667: Q00-Q38, 2 bits each (0 locked, 1 active, 2 ready, 3 complete)
- 668-669 prologue flags, 670 choice, 671 forge strikes, 672/673 raid defeated/spared

If a raid is still in progress when you load, it restarts whole.

### Older saves

A save without the `Q` marker is migrated on load:

- **Opening save** (no progress at all): the prologue starts at Q00.
- **Any real progress** (story flags, chapter, kills, other rooms, level > 1, ...):
  Q00-Q04 are recorded as complete *from an earlier save* (`PF_MIGRATED`, shown
  in the STORY view), and Q05 becomes active. No later node is marked, and no
  other byte changes.

## Tests (real mGBA, controller only, no memory writes)

- `tests/test_mgba_prologue.py --choice 1|2` plays Q00-Q04 and opens the QUESTS STORY view. It then cold-boots, uses CONTINUE, and checks the campaign state is identical.
- `tests/test_mgba_prologue_migration.py` loads two real V11.3 saves (`tests/fixtures/`, made by the shipped V11.3 ROM).

Both run in `lost-cosmos-native.yml`.

## Not done yet

Acts I-V as campaign nodes (Q05-Q38) are listed but not wired. The existing Act
I-IV content still plays as before. The three endings, the companion voice and
the new audio are not part of this release.
