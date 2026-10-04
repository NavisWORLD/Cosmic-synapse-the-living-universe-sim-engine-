#!/usr/bin/env python3
"""Cory Davis' V11.1 Content Bible -> stable public JSON and native ROM tables.

Indices never change; item/skill IDs remain the author's IDs. Original campaign
world numbers are NOT these expedition world numbers. No runtime allocation.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORLDS = ['ERIDORIA PRIME','THE SHATTERED REEF','CINDER DRIFT','HOLLOW VERDANCE',
          'THE PALE EXPANSE','RUST MERIDIAN','UMBRAL DEEP','THE CROWN']
RARITY = ['COMMON','UNCOMMON','RARE','SUPER RARE','LEGENDARY']
ITEMS = []

def item_block(kind, letter, text):
    for line in text.strip().splitlines():
        name, world, rarity, stats, desc, source, effect, price = line.split('|')
        e = dict(id=f'ITM_{letter}{1+sum(x["kind"]==kind for x in ITEMS):03d}',
                 name=name, kind=kind, world=int(world), rarity=RARITY[int(rarity)],
                 description=desc, source=source, effect=effect, price=int(price))
        e.update(dict(zip(['str','def','mag','hp','mp'], map(int,stats.split(',')))))
        ITEMS.append(e)

item_block('weapon','W', """
Brindle Twig|0|0|1,0,0,0,0|A branch that refused to break.|Eridoria Prime, tutorial|blade|8
Gatekeeper's Shiv|0|0|2,0,0,0,0|Taken from the West Gate armory.|Eridoria Prime|blade|16
Reefglass Shard|1|1|2,0,1,0,0|Cuts and hums.|Shattered Reef|blade|24
Cinder Poker|2|0|3,0,0,0,0|Still warm from the Drift.|Cinder Drift|blade|24
Verdant Thorn|3|1|3,0,0,0,0|Grows sharper when you bleed.|Hollow Verdance|blade|28
Pale Icicle|4|1|3,0,1,0,0|Melts only in sunlight.|Pale Expanse|blade|32
Rustworn Cleaver|5|0|4,0,0,0,0|A machine's last argument.|Rust Meridian|blade|32
Umbral Fang|6|2|4,0,0,0,0|Bites the hand that holds it, gently.|Umbral Deep|blade|44
Astrid's Oathblade|0|2|5,1,0,0,0|Sworn, not given.|Quest: Astrid's Oath|blade|60
Mira's Wrenchblade|0|2|4,0,2,0,0|Fixes what it breaks.|Quest: Repair the Beacon|blade|60
Echo Cutlass|6|3|6,0,0,0,0|Strikes twice on even turns.|Umbral Deep, elite drop|double_even|90
Heartwood Brand|0|3|5,0,3,0,0|The grove remembers your name.|Heartwood trial|blade|90
Signal Sabre|5|3|6,0,2,0,0|Glows near beacons.|Craft: 3 signal cores|blade|100
Nihilos Edge|6|4|8,0,0,0,0|A piece of the ECHO, tamed.|Boss: NIHILOS ECHO|blade|160
Malakar's Fall|0|4|9,-1,0,0,0|Victory has a weight.|Boss: MALAKAR|blade|160
Pulse Rod|0|0|0,0,2,0,0|The first spell ever cast left a mark.|Eridoria Prime|staff|12
Tidecaller Staff|1|1|0,0,3,0,0|Remembers the Reef's drowning.|Shattered Reef|staff|24
Ashen Focus|2|1|0,0,4,0,0|Burns mana clean.|Cinder Drift|staff|32
Rootweaver Staff|3|2|0,0,4,4,0|Drinks from deep soil.|Hollow Verdance|staff|44
Frostscribe Quill|4|2|0,0,5,0,0|Writes spells on cold air.|Pale Expanse|staff|50
Meridian Coil|5|2|1,0,5,0,0|Machine logic, wild output.|Rust Meridian|staff|52
Gloam Lantern|6|3|0,0,6,0,0|Its light is a question.|Umbral Deep|staff|90
The Builder's Hand|5|4|0,0,7,0,0|Assembles spells from spare parts.|Craft: Builder's set|staff|160
Crown Scepter|7|4|0,0,9,0,10|Heavy is the head.|The Crown, final chest|staff|180
Outcast's Knuckles|0|3|5,2,0,0,0|For those who stopped asking.|Quest: The Outcast's Road|fist|90
""")
item_block('armor','A', """
Traveler's Cloak|0|0|0,1,0,0,0|Smells like everywhere.|Eridoria Prime|body|8
Gate Watch Tabard|0|0|0,2,0,0,0|Standard issue, extra patches.|Eridoria Prime|body|16
Reefdiver Suit|1|1|0,2,0,0,0|Sheds pressure. Water resist.|Shattered Reef|water_resist|24
Ashcloak|2|1|0,3,0,0,0|Woven from cooled ash. Fire resist.|Cinder Drift|fire_resist|28
Thornweave Vest|3|1|0,3,0,0,0|Itches with intent.|Hollow Verdance|body|28
Pale Parka|4|1|0,3,0,0,0|Warm as a held hand. Ice resist.|Pale Expanse|ice_resist|28
Scrap Plate|5|0|0,4,0,0,0|Ugly, honest, effective.|Rust Meridian|body|32
Gloomshroud|6|2|0,4,0,0,0|Darkness tailored to fit.|Umbral Deep|body|44
Brindle Elder Robe|0|2|0,3,3,0,0|Smells of old rain.|Quest: Find the Elder|body|60
Beaconkeeper Mail|0|2|0,5,0,0,0|Rings faintly near rifts.|Quest: Repair the Beacon|body|60
Echo Plate|6|3|0,6,0,0,0|Reflects 10 percent of damage.|Umbral Deep elite|reflect|90
Heartwood Bark|0|3|0,5,0,8,0|Living armor, still growing.|Heartwood trial|body|90
Signal Mesh|5|3|0,5,2,0,0|Catches stray transmissions.|Craft: 3 signal cores|body|100
Malakar's Carapace|0|4|0,8,0,0,0|The tyrant's shell, hollowed out.|Boss: MALAKAR|body|160
Crown Aegis|7|4|0,9,0,10,0|Worn by no one, until you.|The Crown|body|180
Sturdy Boots|0|0|0,1,0,0,0|Broken in already. Evade +5 percent.|Shop|evade5|12
Reefwalkers|1|1|0,1,0,0,0|No slow in water.|Shattered Reef|tidewalk|24
Cinder Treads|2|1|0,2,0,0,0|Immune to burn tiles.|Cinder Drift|ashwalk|28
Rootstep Moccasins|3|1|0,1,0,0,0|Silent movement.|Hollow Verdance|silent|24
Pale Skates|4|2|0,2,0,0,0|Speed on ice +10 percent.|Pale Expanse|ice_speed|40
Meridian Greaves|5|2|0,3,0,0,0|Magnetic soles.|Rust Meridian|feet|44
Outcast's Wraps|0|1|0,2,1,0,0|Hide the face, keep the eyes.|Quest: The Outcast's Road|head|32
Signal Circlet|5|3|0,2,3,0,0|Tunes out the static.|Craft: 2 signal cores|head|90
The Listening Helm|6|4|0,4,2,0,0|Hears echoes before they form.|Umbral Deep, secret|listen|160
Builder's Goggles|5|4|0,3,0,0,0|Reveals hidden caches.|Craft: Builder's set|reveal|160
""")
item_block('charm','C', """
Pebble of Origin|0|0|0,0,0,0,0|XP +5 percent. A rock from where you started.|Origin|xp|12
Brindle Acorn|0|1|0,0,0,0,0|COSMOS gains trust 20 percent faster.|Heartwood|trust|24
Reef Pearl|1|1|0,0,0,0,0|MP regen +1 per battle turn.|Shattered Reef|regen|24
Cinder Coal|2|1|0,0,0,0,0|Fire spells +15 percent. Warm pocket.|Cinder Drift|fire|24
Thorn Knot|3|1|0,0,0,0,0|Counter 5 percent on hit.|Hollow Verdance|counter|24
Frostbite Charm|4|1|0,0,0,0,0|Ice spells +15 percent.|Pale Expanse|ice|24
Gear Tooth|5|0|0,0,0,0,0|Repair costs halved.|Rust Meridian|repair|12
Gloom Moth Wing|6|2|0,0,0,0,0|Evade +10 percent in darkness.|Umbral Deep|gloom_evade|44
Elder's Blessing|0|2|0,0,0,10,0|A hand on your shoulder.|Quest: Find the Elder|hp|60
Astrid's Ribbon|0|2|0,0,0,0,0|STR +2 below half HP. She believes in you.|Quest: Astrid's Oath|ribbon|60
Mira's Fuse|0|2|0,0,0,0,0|MAG +2 below half MP. Sparks fly.|Quest: Repair the Beacon|fuse|60
Echo Locket|6|3|0,0,0,0,0|10 percent chance to repeat a spell free.|Umbral Deep elite|repeat|90
Heartwood Seed|0|3|0,0,0,0,0|Revive once per battle at 25 percent HP.|Heartwood trial|revive|90
Signal Booster|5|3|0,0,0,0,0|Buddy abilities cost 1 less MP.|Craft: 4 signal cores|buddy_cost|90
The Smallest Star|4|4|1,1,1,1,1|Found, not made.|Pale Expanse, secret|star|160
Outcast's Token|0|3|0,0,0,0,0|Shops give 15 percent discount. One of us.|Quest: The Outcast's Road|discount|90
Memory Vial|6|4|0,0,0,0,0|Store one echo. Release it for a free battle turn.|Quest: Lay to Rest|echo|160
Builder's Clasp|5|4|0,0,0,0,0|Crafting needs one fewer material.|Craft: Builder's set|material|160
Crown Fragment|7|4|0,0,0,0,0|Damage to bosses +15 percent.|The Crown|boss|160
The Ninth Beacon|0|4|0,0,0,0,0|COSMOS stays, even at 0 trust.|Postgame: all beacons lit|stay|180
""")
item_block('consumable','U', """
Potion|0|0|0,0,0,0,0|Restore 20 HP.|Shop 5c|heal20|5
Ether|0|0|0,0,0,0,0|Restore 10 MP.|Shop 7c|mana10|7
Reef Tonic|1|1|0,0,0,0,0|Restore 35 HP. Tastes like low tide.|Shop 12c / Reef|heal35|12
Cinder Draught|2|1|0,0,0,0,0|Restore 20 HP, cure burn.|Shop 12c / Drift|burn_cure|12
Verdant Poultice|3|1|0,0,0,0,0|Restore 50 HP over 3 turns.|Hollow Verdance|regen50|16
Pale Melt|4|1|0,0,0,0,0|Restore 25 MP. Cold going down.|Pale Expanse|mana25|16
Scrap Oil|5|0|0,0,0,0,0|Repair weapon durability +50 percent.|Rust Meridian|oil|10
Gloomcap Tea|6|2|0,0,0,0,0|Cure all status, DEF +2 for 3 turns.|Umbral Deep|tea|24
Starshard|0|3|0,0,0,0,0|Restore full HP. One use, one sky.|Rare drop|fullhp|35
Elixir of Origin|0|3|0,0,0,0,0|Restore full HP and MP.|Craft: 5 rare herbs|elixir|50
Smoke Pellet|0|1|0,0,0,0,0|Guaranteed escape from battle.|Shop 15c|escape|15
Beacon Flare|0|2|0,0,0,0,0|Call COSMOS instantly, max bond for 3 turns.|Craft: signal core|flare|24
Memory Draught|6|2|0,0,0,0,0|Double XP for 5 battles. Bittersweet.|Quest: Lay to Rest|doublexp|24
Builder's Paste|5|2|0,0,0,0,0|Instantly repair all gear.|Craft: Builder's set|paste|24
Thorn Bomb|3|1|0,0,0,0,0|40 damage to all enemies.|Hollow Verdance|bomb40|16
Frost Grenade|4|2|0,0,0,0,0|55 damage, may freeze.|Pale Expanse|bomb55|24
Pulse Cell|5|2|0,0,0,0,0|70 MAG damage, single target.|Rust Meridian|cell70|24
Echo Decoy|6|3|0,0,0,0,0|Enemy targets decoy for 2 turns.|Umbral Deep|decoy|35
Crown Apple|7|4|0,0,0,0,0|Permanent max HP +2. Crisp. Three exist.|The Crown, 3 total|apple|0
The Last Supper|0|4|0,0,0,0,0|Full restore and revive. For the road ahead.|Postgame quest|supper|0
""")
item_block('key','K', """
X Key|0|0|0,0,0,0,0|Opens the West Gate seal.|Story|keyx|0
Y Key|1|0|0,0,0,0,0|Opens the Reef vault.|Story|keyy|0
Z Key|7|0|0,0,0,0,0|Opens the Crown door.|Story|keyz|0
Signal Core|0|2|0,0,0,0,0|Crafting material. Twelve total near rifts.|Rifts|signal|0
Memory Echo|0|2|0,0,0,0,0|Carried echo of the departed. Eight total.|Memory sites|memory|0
Builder's Kit|5|2|0,0,0,0,0|Unlocks the crafting menu.|Rust Meridian|kit|0
Heartwood Sigil|0|3|0,0,0,0,0|Proof of the grove's trial. Opens deep Heartwood.|Heartwood trial|sigil|0
Outcast's Map|0|3|0,0,0,0,0|Reveals all hidden caches on the world map.|The Outcast's Road|map|0
The Ninth Signal|0|4|0,0,0,0,0|Postgame. Unknown purpose. It hums.|All beacons|ninth|0
Arin's Journal|0|0|0,0,0,0,0|Records campaign progress. Opens the quest menu.|Start|journal|0
""")

CHARACTERS=[]
def character_block(kind,text):
    for line in text.strip().splitlines():
        name,world,hp,atk,desc=line.split('|')
        CHARACTERS.append(dict(id=f'CHR_{len(CHARACTERS)+1:03d}',name=name,world=int(world),
                               hp=int(hp),atk=int(atk),kind=kind,description=desc))

character_block('npc',"""
ASTRID|0|0|0|Swordmaster. Blunt, loyal, afraid of still water. Astrid's Oath.
MIRA|0|0|0|Engineer and beaconwright. Talks to machines like people. Repair the Beacon.
BRINDLE ELDER|0|0|0|Grove keeper and tutorial guide. Remembers every name. Find the Elder.
CORVUS THE FENCE|0|0|0|Merchant, ex-smuggler. Prices drop as trust rises.
SABLE|0|0|0|Outcast scout. Knows every hidden path. The Outcast's Road.
TIDE PRIEST ILYA|1|0|0|Reads the drowned spires. Speaks in tide metaphors.
DIVER KESS|1|0|0|Salvage diver. Sells Reef maps. Lost a brother to the deep.
THE DROWNED CHOIR|1|0|0|Echoes of drowned sailors. Give warnings as songs.
EMBER WRIGHT HALVOR|2|0|0|Smith. Forges Cinder gear. Burns his failures as offerings.
ASH CHILD PIM|2|0|0|Orphan guide. Knows safe paths through ash. Collects cool rocks.
THE LAST VOLCANO|2|0|0|Ancient entity. Advice once per visit: always true, always costly.
THORN MOTHER|3|0|0|Verdance guardian. Tests your gentleness. Fails the cruel.
RANGER DUARTE|3|0|0|Beast tracker. Teaches taming. Lost his beast, still tracks.
THE QUIET APIARIST|3|0|0|Beekeeper hermit. Sells poultices. Has not spoken in years; writes notes.
FROSTBITE JUNA|4|0|0|Ice fisher. Her laugh cracks thin ice.
THE CARTOGRAPHER'S GHOST|4|0|0|Maps the Pale Expanse from memory. Fades a little each visit.
PALE ABBESS|4|0|0|Heals free. Asks only that you remember her name.
SCRAP BARON VEX|5|0|0|Merchant lord. Controls Rust markets. Respects only builders.
UNIT 7 (SEVEN)|5|0|0|Retired machine. Chose a name over a number. Wants to see the sky.
THE TINKER'S WIDOW|5|0|0|Teaches advanced crafting. Keeps her husband's tools oiled.
GLOAM GUIDE|6|0|0|Blind navigator. Leads through Umbral Deep. Sees by listening.
THE CONFESSOR|6|0|0|Echo priest. Hears your regrets. Grants absolution buffs.
MOTH KEEPER|6|0|0|Beast handler. Raises gloom moths. Sells light in the dark.
THE HOLLOW SAINT|6|0|0|Fallen hero. Warns against the Deep's bargain. Was once a king.
CROWN SENESCHAL|7|0|0|Throne keeper and final gatekeeper. Polite, immovable, sad.
THE STAR CHILD|7|0|0|Mysterious youth before the final boss. Knows your name unasked.
ECHO OF THE SON|0|0|0|A small echo at story beats. Says little. Means everything.
THE BUILDER'S SHADE|5|0|0|The pieces are old. The assembly is yours.
PRAYER KEEPER|0|0|0|Postgame, all beacons lit. If everyone's happy, nobody prays.
THE FIRST OUTCAST|6|0|0|The one Eridoria cast out first. The road's true beginning.
""")
character_block('mob',"""
Brindle Sprout|0|8|2|Tutorial mob. More scared than you.
Gate Rat|0|10|3|Steals 1 credit on hit.
Reef Nipper|1|14|4|Aquatic. Faster in water tiles.
Drowned Husk|1|18|5|May drop a Memory Echo fragment.
Spire Jelly|1|12|4|Splits into two when killed by fire.
Ash Imp|2|14|5|Leaves burn tiles.
Cinder Hound|2|20|6|Howls raise ally ATK.
Slag Golem|2|30|5|Slow. High DEF.
Thorn Lurker|3|16|5|Ambushes from plant tiles.
Canopy Ape|3|22|6|Throws fruit, ranged.
Root Tangler|3|26|4|Roots the player 1 turn on hit.
Frost Mite|4|12|4|Weak, swarms in threes.
Pale Wolf|4|20|7|Hunts in pairs.
Glacial Wisp|4|10|6|MAG attacker. Drops Pale Melt.
Scrap Spider|5|14|5|Drops Gear Tooth.
Rust Hound|5|22|6|Corrodes armor, temporary DEF -1.
Dead Battery|5|8|8|Explodes at 25 percent HP.
Gloom Bat|6|14|6|Blinds on crit.
Umbral Crawler|6|24|7|Invisible until it attacks.
Sorrow Moth|6|12|5|Drains 2 MP per hit.
Crown Initiate|7|30|8|Fights with ceremony. Bows first.
Throne Wisp|7|18|9|Pure MAG. No mercy.
Gate Deserter|0|16|5|Human enemy. May surrender to TALK.
Reef Eel|1|16|6|Electric. Stuns 10 percent.
Barnacle Brute|1|34|5|Tank. Drops Reefglass.
Magma Tick|2|10|7|Latches and drains HP 3 per turn.
Obsidian Shardling|2|24|7|Reflects 10 percent physical damage.
Spore Mother|3|28|4|Spawns 2 Sprouts at half HP.
Vine Whipper|3|18|8|High crit.
Avalanche Cub|4|26|7|Charges every third turn.
Permafrost Knight|4|40|6|Guards secrets.
Cogling|5|12|5|Repairs other machines mid-battle.
Furnace Hound|5|28|8|Fire aura, 2 HP per turn.
Gloom Stalker|6|22|9|Targets COSMOS first.
The Forgotten|6|30|7|Takes the shape of an NPC.
Crown Lancer|7|36|9|Always charges turn 1.
Brindle Boar|0|20|5|Charges below half HP.
Tide Lurker|1|20|6|Drags the player 1 tile on hit.
Ember Sprite|2|8|8|Dies in one hit. Hits like a truck.
Mossback|3|36|4|Sleeps unless provoked.
""")
character_block('elite',"""
THE GATE TYRANT|0|120|12|Enrages when guards die.
DROWNED CAPTAIN|1|140|13|Summons 2 Husks at 50 percent.
SPIRE MOTHER|1|160|11|Spawns Jellies each turn.
CINDER ALPHA|2|150|14|Howl buffs the pack.
THE SLAG KING|2|200|10|Immune to fire. Slow.
THORN REGENT|3|170|13|Roots the entire party.
CANOPY TYRANT|3|180|15|Drops from above turn 1.
THE WHITEOUT|4|160|14|Blinds all for 2 turns at 50 percent.
PERMAFROST JARL|4|220|12|Shields allies.
SCRAP COLOSSUS|5|240|11|Repairs 10 HP per turn.
THE FOREMAN|5|180|14|Commands Coglings.
GLOOM MATRIARCH|6|190|15|Spawns Bats.
THE CONFESSED|6|170|16|Copies the player's last spell.
CROWN CHAMPION|7|260|16|Duels honorably. No adds.
THE SENESCHAL'S SHADOW|7|200|17|Counters magic.
ECHO OF MALAKAR|0|150|14|Postgame. A memory that fights back.
THE TIDE CALLER|1|175|13|Floods the arena.
ASHEN PROPHET|2|165|15|Marks the player's next move.
THE QUIET ONE|3|185|12|Silences magic for 3 turns.
RUST SAINT|5|210|13|Heals itself with Scrap Oil.
""")
character_block('boss',"""
MALAKAR, THE HOLLOW KING|0|600|22|Two phases. Shatters the arena at 50 percent.
NIHILOS ECHO|6|700|24|Copies the party. The fight is a mirror.
THE DROWNED GOD|1|550|20|Floods the arena in phases. Kill the tide, not the god.
CINDER MAW|2|650|23|Eats the floor. Standing still burns.
THE THORN HEART|3|600|21|Heal it and it grows stronger. Starve it.
THE PALE KING|4|620|22|Freezes time at 33 percent. Skips player turns.
THE MERIDIAN CORE|5|680|21|Rebuilds adds. Destroy the forges first.
VESPER, THE EVENING STAR|6|750|25|Falls as she fights. Beauty as a weapon.
THE CROWN ITSELF|7|800|26|The throne is alive. It has been waiting.
THE QUIET|7|999|28|True final, postgame. The silence between signals. Bring echoes.
""")

SKILLS=[]
def skill_block(kind,letter,text):
    for line in text.strip().splitlines():
        name,mp,power,desc,unlock,level,world,bond,gate=line.split('|')
        SKILLS.append(dict(id=f'SKL_{letter}{1+sum(s["kind"]==kind for s in SKILLS):03d}',
            name=name,kind=kind,mp=int(mp),power=int(power),description=desc,unlock=unlock,
            level=int(level),world=int(world),bond=int(bond),gate=int(gate)))
# gate: 0 ordinary, 1 beacon quest, 2 trial, 3 Malakar, 4 postgame,
# 5 Lay to Rest, 6 Builder set, 7 Outcast, 8 all beacons, 9 pack shop,
# 10 Corvus trust, 11 craft20, 12 Ranger, 13 kit, 14 Mira, 15 Elder;
# 20..29 the ten bosses in author order.
skill_block('spell','S',"""
Pulse|3|15|The first spell. MAG damage.|Start|1|255|0|0
Ember|4|20|Fire damage. May burn.|Level 3|3|255|0|0
Tide|4|20|Water damage. May slow.|Level 3|3|255|0|0
Thorn|4|20|Nature damage. May root.|Level 3|3|255|0|0
Frostbite|6|30|Ice damage. May freeze.|Level 6, Pale Expanse|6|4|0|0
Static|6|30|Lightning damage. May stun.|Level 6, Rust Meridian|6|5|0|0
Gloom|6|30|Dark damage. Blinds.|Level 6, Umbral Deep|6|6|0|0
Starfall|8|45|MAG damage to all enemies.|Level 10|10|255|0|0
Cinder Wave|8|40|Fire to all enemies. Burns ground.|Level 10, Cinder Drift|10|2|0|0
Reef Surge|8|40|Water to all enemies.|Level 10, Shattered Reef|10|1|0|0
Verdant Grasp|7|35|Nature damage. Roots for 2 turns.|Level 9, Hollow Verdance|9|3|0|0
Pale Shroud|7|35|Ice damage. Raises DEF for 2 turns.|Level 9, Pale Expanse|9|4|0|0
Scrap Storm|9|50|Damage spread across random targets.|Level 12, Rust Meridian|12|5|0|0
Umbral Veil|9|50|Dark damage. Evade the next attack.|Level 12, Umbral Deep|12|6|0|0
Beacon Light|10|55|Holy damage. Bonus against dark.|Quest: Repair the Beacon|1|255|0|1
Echo Strike|10|55|Repeats the last spell at half power.|Umbral Deep|1|6|0|0
Heartwood Song|12|60|Nature damage. Heal the party 20 HP.|Heartwood trial|1|255|0|2
Malakar's Lesson|12|70|Learned from defeat.|After beating MALAKAR|1|255|0|3
Crown Judgment|15|90|Holy damage. Once per battle.|The Crown|1|7|0|0
The Quiet Word|20|120|Silences the target after damage.|Postgame|1|255|0|4
Mend|5|30|Heal an ally or self 30 HP.|Level 4|4|255|0|0
Cleanse|5|0|Cure all status, party.|Level 5|5|255|0|0
Haste|6|0|Speed +50 percent for 3 turns.|Level 8|8|255|0|0
Bulwark|6|0|DEF +4 for 3 turns.|Level 8|8|255|0|0
Focus|4|0|Next spell +50 percent.|Level 7|7|255|0|0
Drain|7|30|Heal half the damage dealt.|Umbral Deep|1|6|0|0
Swap|3|0|Swap HP with COSMOS. Desperate.|Bond level 5|1|255|5|0
Overload|12|80|MAG damage. User takes 20 recoil.|Rust Meridian|1|5|0|0
Prayer|8|15|Full party cleanse and 15 HP.|Quest: Lay to Rest|1|255|0|5
Builder's Fix|6|20|Repair all gear and heal 20 HP.|Craft: Builder's set|1|255|0|6
""")
skill_block('buddy','B',"""
Nuzzle|0|10|Heal 10 HP. It missed you.|Bond 1|1|255|1|0
Scout|0|0|Reveal hidden items on screen.|Bond 1|1|255|1|0
Static Bark|2|15|Damage. May stun.|Bond 2|1|255|2|0
Fetch|0|0|Retrieve one dropped item in battle.|Bond 2|1|255|2|0
Warmth|3|0|Cure freeze and burn, party.|Bond 3|1|255|3|0
Echo Howl|4|25|Damage to all enemies.|Bond 3|1|255|3|0
Guard|0|0|Take the next hit for ARIN.|Bond 4|1|255|4|0
Phase Dash|5|0|COSMOS evades all for 2 turns.|Bond 4|1|255|4|0
Memory Share|6|0|Grant ARIN a free spell cast.|Bond 5|1|255|5|0
Beacon Pulse|6|40|Holy damage. Bonus near beacons.|Bond 5|1|255|5|0
Quantum Bite|8|55|Ignores DEF.|Bond 6|1|255|6|0
Comfort|4|25|Full cleanse and 25 HP, one ally.|Bond 6|1|255|6|0
Rift Sniff|0|0|Detect rifts and secrets, field.|Bond 7|1|255|7|0
Star Chase|10|75|Chases the brightest enemy.|Bond 7|1|255|7|0
The Long Wait|0|0|Trust +1 after battle. COSMOS waits.|Bond 8|1|255|8|0
Soul Guard|12|0|Party immune for 1 turn.|Bond 8|1|255|8|0
Unravel|10|0|Dispel enemy buffs.|Bond 9|1|255|9|0
Home Signal|8|0|Teleport to the last beacon, field.|Bond 9|1|255|9|0
The Ninth Bark|15|100|Once per day. It remembers.|Bond 10|1|255|10|0
Stay|0|0|COSMOS stays by your side. Always.|Bond 10|1|255|10|0
""")
skill_block('passive','P',"""
Builder's Hands|0|0|Crafting costs 20 percent less.|Rust Meridian|1|5|0|0
Outcast's Luck|0|0|Rare drops +10 percent.|Quest: The Outcast's Road|1|255|0|7
Tidewalker|0|0|No slow in water.|Shattered Reef|1|1|0|0
Ashborn|0|0|Immune to burn.|Cinder Drift|1|2|0|0
Rootbound|0|0|Healing received +10 percent.|Hollow Verdance|1|3|0|0
Frostblood|0|0|Immune to freeze.|Pale Expanse|1|4|0|0
Scrapwise|0|0|Credits from machines +20 percent.|Rust Meridian|1|5|0|0
Gloomeyed|0|0|See in darkness.|Umbral Deep|1|6|0|0
Crownless|0|0|Damage +10 percent when HP full.|The Crown|1|7|0|0
Second Wind|0|0|Survive lethal damage at 1 HP once per battle.|Level 15|15|255|0|0
Spellsword|0|0|Spell damage +10 percent with a blade.|Level 12|12|255|0|0
Battlemage|0|0|Blade damage +10 percent with a staff.|Level 12|12|255|0|0
Thick Skin|0|0|DEF +2 always.|Level 10|10|255|0|0
Deep Lungs|0|0|Max MP +10.|Level 10|10|255|0|0
Strong Heart|0|0|Max HP +10.|Level 10|10|255|0|0
Quick Hands|0|0|Speed +10 percent.|Level 14|14|255|0|0
Memory Keeper|0|0|Echoes last 2 extra turns.|Quest: Lay to Rest|1|255|0|5
Beacon Attuned|0|0|Damage +15 percent near beacons.|All beacons lit|1|255|0|8
The Listener|0|0|Hear hidden dialogue hints.|Umbral Deep|1|6|0|0
Pack Mule|0|0|Inventory gains 20 slots.|Shop, 200c|1|255|0|9
Haggler|0|0|Shop discount 10 percent.|Corvus trust max|1|255|0|10
Beast Friend|0|0|COSMOS bond gains +25 percent.|Bond 8|1|255|8|0
Prayer Answered|0|0|5 percent chance to fully heal on kill.|Quest: Lay to Rest|1|255|0|5
The Assembly|0|0|All stats +1 per crafted item, max +5.|Craft 20 items|1|255|0|11
Nobody's Fool|0|0|Immune to charm and confusion.|Quest: The Outcast's Road|1|255|0|7
""")
skill_block('ultimate','X',"""
HEARTWOOD'S ANSWER|0|150|Nature. The grove fights with you.|Heartwood trial|1|255|0|2
TIDEFALL|0|150|Water to all enemies.|Boss: Drowned God|1|255|0|22
CINDER REQUIEM|0|160|Fire. Burns the sky.|Boss: Cinder Maw|1|255|0|23
THE VERDANT MAW|0|150|Nature. Devours one ordinary enemy whole.|Boss: Thorn Heart|1|255|0|24
PALE ETERNITY|0|100|Ice. Freeze all enemies for 2 turns.|Boss: Pale King|1|255|0|25
MERIDIAN COLLAPSE|0|170|Destroys all enemy buffs.|Boss: Meridian Core|1|255|0|26
VESPER'S FALL|0|180|The evening star lands.|Boss: Vesper|1|255|0|27
CROWN'S WEIGHT|0|200|The throne answers.|Boss: The Crown Itself|1|255|0|28
MALAKAR'S END|0|160|Finish what the Hollow King started.|After MALAKAR|1|255|0|3
ECHO BREAKER|0|170|Dark. Shatters mirrors.|After NIHILOS ECHO|1|255|0|21
THE BUILDER|0|100|Fully repair party and heal all 100 HP.|Craft: Builder's set|1|255|0|6
OUTCAST'S STAND|0|0|Cannot fall below 1 HP for 3 turns.|Quest: The Outcast's Road|1|255|0|7
MEMORY LANE|0|0|Summon 3 echoes to fight for 3 turns.|Quest: Lay to Rest|1|255|0|5
THE NINTH SIGNAL|0|250|All beacons fire as one.|Postgame: all beacons|1|255|0|8
STAY WITH ME|0|300|ARIN and COSMOS combine. Once per game day.|Bond 10|1|255|10|0
""")
skill_block('utility','U',"""
Light|0|0|Illuminate dark areas, field.|Start|1|255|0|0
Mend Gear|0|0|Field repair, small.|Rust Meridian|1|5|0|0
Track|0|0|Show mob locations on the map.|Ranger Duarte|1|255|0|12
Forage|0|0|Find consumables in wilds.|Hollow Verdance|1|3|0|0
Dive|0|0|Enter deep water tiles.|Shattered Reef|1|1|0|0
Climb|0|0|Scale marked cliffs.|Cinder Drift|1|2|0|0
Listen|0|0|Hear echo dialogue, field.|Umbral Deep|1|6|0|0
Assemble|0|0|Basic field crafting.|Builder's Kit|1|255|0|13
Recall|0|0|Return to the last beacon.|Mira|1|255|0|14
Rest|0|0|Full heal at campfires.|Brindle Elder|1|255|0|15
""")

def cstr(s): return json.dumps(s.upper().replace('%',' PCT'),ensure_ascii=True)
def main():
    assert len(ITEMS)==len(CHARACTERS)==len(SKILLS)==100
    out=ROOT/'content';out.mkdir(exist_ok=True)
    data=dict(version='11.1',author='Cory Davis',worlds=WORLDS,items=ITEMS,
              characters=CHARACTERS,skills=SKILLS)
    (out/'v11_1_catalog.json').write_text(json.dumps(data,indent=2)+'\n')
    kinds=['weapon','armor','charm','consumable','key']
    lines=['/* GENERATED by tools/build_content_v11.py. Stable Content Bible indices. */',
      '#ifndef V11_DATA_H','#define V11_DATA_H',
      'typedef struct {const char *name,*description,*source;s8 str,def,mag,hp,mp;u8 kind,rarity,world;u16 price;} V11Item;',
      'typedef struct {const char *name,*description;u16 hp;u8 atk,kind,world;} V11Character;',
      'typedef struct {const char *name,*description,*unlock;u16 power;u8 mp,kind,level,world,bond,gate;} V11Skill;',
      'static const char *V11_WORLDS[8]={'+','.join(map(cstr,WORLDS))+'};',
      'static const V11Item V11_ITEMS[100]={']
    for e in ITEMS:
        lines.append('{'+','.join([cstr(e['name']),cstr(e['description']),cstr(e['source'])]+[str(e[k]) for k in ['str','def','mag','hp','mp']]+[str(kinds.index(e['kind'])),str(RARITY.index(e['rarity'])),str(e['world']),str(e['price'])])+'},')
    lines+=['};','static const V11Character V11_CHARACTERS[100]={']
    for e in CHARACTERS:
        lines.append('{'+','.join([cstr(e['name']),cstr(e['description']),str(e['hp']),str(e['atk']),str(['npc','mob','elite','boss'].index(e['kind'])),str(e['world'])])+'},')
    lines+=['};','static const V11Skill V11_SKILLS[100]={']
    for e in SKILLS:
        lines.append('{'+','.join([cstr(e['name']),cstr(e['description']),cstr(e['unlock']),str(e['power']),str(e['mp']),str(['spell','buddy','passive','ultimate','utility'].index(e['kind']))]+[str(e[k]) for k in ['level','world','bond','gate']])+'},')
    lines+=['};','#endif','']
    (ROOT/'LOST_COSMOS_V10_SOURCE/content_v11_data.h').write_text('\n'.join(lines))
    print('Generated 100 items, 100 characters, 100 skills; stable native tables.')

if __name__=='__main__': main()
