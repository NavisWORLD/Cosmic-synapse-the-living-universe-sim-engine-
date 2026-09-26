# ERIDORIA: A LEGEND REBORN — V8 PLAYABLE CHRONICLE

This is a native GBA adaptation of Cory Davis's supplied Eridoria manuscript integrated with the Lost COSMOS eight-world RPG. The **30 passages below are included in the V8 cartridge**, unlock from real story quest flags, and can be read through **START → ERIDORIA → R (CHRONICLE)**. The 30-page format is a GBA-sized playable adaptation, **not** a claim that every paragraph or all planned boss fights, player guardians, networking, or optional subquests in the original manuscript have been implemented.

Canonical continuity: Arin is the apprentice smith from Brindlemark, Origin Earth; Astrid warns about the Heart's shattered seed, which is distinct from the Great Heart Tree in Hidden City. Malakar is an Act I antagonist. His retreat breaks a deeper seal protecting against Nihilos and Voidborn. The player, their alliances, and COSMOS can help rebuild the Cosmic Lattice. COSMOS is a deterministic software companion; player choices remain authoritative.

## In-cartridge 30-scene narrative

### 1. I. THE BLACKSMITH

Brindlemark has no walls against stars. arin works his forge as the sky flickers and the first shadows take root.

*Unlock requirement:* `0`.

### 2. I. ASTRIDS WARNING

Astrid reveals the hearts fracture. malakar seeks the crystal seed while the great heart tree sleeps beneath the hidden city.

*Unlock requirement:* `0`.

### 3. I. OAKWOOD ROAD

Follow the eastern road to oakwood. the trader knows which lord keeps his brothers map of the cursed cragstone temple.

*Unlock requirement:* `ST_TOWN`.

### 4. I. CRAGSTONE TEMPLE

Ravenswood gives arin the order sky root heart star. four runes hold the sealed chamber beyond its stone guardians.

*Unlock requirement:* `ST_OAKWOOD`.

### 5. I. THE DARK SORCERER

The runes release the seal. malakar stands before the heart. his defeat will break the first shadow, not the entire curse.

*Unlock requirement:* `ST_PUZZLE`.

### 6. I. THE HEART REBORN

Arin reclaims the crystal seed and the great tree answers. malakars flight fractures an older seal. nihilos is stirring.

*Unlock requirement:* `ST_HEART`.

### 7. II. TIDE MEMORIES

The hearts signal echoes through space. arin and cosmos follow the chronohearts call to the flooded archives of tide.

*Unlock requirement:* `ST_HEART`.

### 8. II. SUNKEN LIBRARY

The historians kept a record of worlds unmade. tides reflections warn that memory can outlive the body that first made it.

*Unlock requirement:* `ST_HEART`.

### 9. II. THE CHRONOHEART

The y axis restores distance and the chronoheart stabilizes time. arin realizes the crystals are part of a cosmic lattice.

*Unlock requirement:* `ST_CHRONO`.

### 10. II. TEMPORAL ECHOES

A fractured chronomancers shadow is written into the archive. a new storm gathers beyond the borders of time.

*Unlock requirement:* `ST_CHRONO`.

### 11. II. CHOOSE THE FUTURE

Astrid asks arin to preserve what was learned, not erase the past. cosmos retains the encounter as an explicit memory.

*Unlock requirement:* `ST_CHRONO`.

### 12. II. GATHER THE AXES

The journey turns toward ember and bloom. x y and z must agree before the black garden will relinquish its sigil.

*Unlock requirement:* `ST_CHRONO`.

### 13. III. NIHILOS STIRS

The older seal was damaged by malakars defeat. voidborn signals appear in ruins, ship routes, and the fractured garden.

*Unlock requirement:* `ST_CHRONO`.

### 14. III. THE LOST SIGIL

With the three axis keys arin can walk into the black garden. the voidward sigil is the last defense of its archives.

*Unlock requirement:* `ST_CHRONO`.

### 15. III. VOIDWARD

The sigil protects memory from the voidborn collective. nihilos remains a threat beyond the current shattered seal.

*Unlock requirement:* `ST_VOID`.

### 16. III. A FRACTURED ALLIANCE

Ferrum, neri, and kestrel send their peoples help. the realms cannot survive as islands cut off from one another.

*Unlock requirement:* `ST_VOID`.

### 17. III. THE HIDDEN ROAD

The great heart tree signals from eridorias hidden city. arin returns to origin and seeks the winged white sentinel.

*Unlock requirement:* `ST_VOID`.

### 18. III. THE WHITE SENTINEL

The sentinel offers three trials of heart, mind, and spirit. failure does not erase the hero. each answer opens a new path.

*Unlock requirement:* `ST_CITY`.

### 19. IV. HALL OF WHISPERS

In the dream veil a mirror reflects arins fear of loss. his companions wait outside: the choice to continue remains his.

*Unlock requirement:* `ST_CITY`.

### 20. IV. THE WISDOM ORB

A brief light crosses the night. answer the riddle of a shooting star to release the first trial and light the eastern path.

*Unlock requirement:* `ST_CITY`.

### 21. IV. THE COURAGE ARENA

The dream guardian takes form as every doubt arin has carried. a clever dodge, a gentle answer, or a brave strike can turn the fight.

*Unlock requirement:* `ST_WISDOM`.

### 22. IV. THE UNITY TRIAL

Strength alone is not enough. arin must choose to share the work with his fellows and the living worlds he has visited.

*Unlock requirement:* `ST_COURAGE`.

### 23. IV. THE OPEN GATE

The three trials awaken the gate to eldoria. the white sentinel reminds arin that even prophecy is not a command.

*Unlock requirement:* `ST_DREAM`.

### 24. IV. THE WIDER SKY

Dream veil is a realm, not a dream to be dismissed. it holds a map of possible futures, each altered by the peoples choices.

*Unlock requirement:* `ST_DREAM`.

### 25. V. ELDORIA WAKES

Thorne welcomes the fellowship to eldoria. earth, water, fire, and air must be restored at four distant shrines.

*Unlock requirement:* `ST_DREAM`.

### 26. V. THE FOUR SHRINES

The forests, rivers, furnaces, and high winds each offer an elemental crystal. one is guarded by the last storm sentinel.

*Unlock requirement:* `ST_DREAM`.

### 27. V. THE COSMIC FATHOM

The four crystals resonate with the heart, chronoheart, and voidward sigil. their combined energy reaches the synapse crown.

*Unlock requirement:* `ST_ELEMENTS`.

### 28. V. THE FINAL GUARD

At the crown, the stellar sentinel holds the lattice. the voidborn cannot decide the destiny of eridoria or its allies.

*Unlock requirement:* `ST_ELEMENTS`.

### 29. V. ONE REALM OF MANY

The lattice has been reforged. open, preserve, or wander: cosmos can share a preference but arin must choose.

*Unlock requirement:* `ST_LATTICE`.

### 30. EPILOGUE. EVER AFTER

The sun rises above the brindlemark forge. the universe still has uncertain roads, and the fellowship can keep exploring.

*Unlock requirement:* `ST_LATTICE`.

## The existing playable five-act campaign

| Act | Main objective | Actual implementation |
|---|---|---|
| I. The Forge and Heart | Astrid → Brindlemark → Oakwood/Ravenswood → Cragstone's four-rune door → Malakar duel → Heart | Native rooms, named NPC dialogue, market purchases/sales, four-symbol puzzle, large tactical Malakar, SRAM flags |
| II. Temporal Distortions | Tide Memory → Y Axis → Chronoheart | Ship navigation, Tide world/elite, recovery trigger and saved Chronoheart flag |
| III. Voidborn | X/Y/Z → Black Garden → Voidward Sigil | Legacy Axis progression, Black Garden secret, Sigil trigger, monsters and persistence |
| IV. Dream trials | Hidden City → White Sentinel → Wisdom riddle → Courage guardian → Unity | Connected Hidden City, Dream Veil planet, literal riddle choice, guardian and trial flags |
| V. Cosmic Fathom | Eldoria Earth/Water/Fire/Air shrines → Crown Sentinel → Lattice → ending | Fourth shrine guardian, all shrines, final Crown, player-selected OPEN/PRESERVE/WANDER and postgame |

The following material remains planned rather than silently invented: a uniquely modeled Chronomancer boss with temporal arena phases, the full Nihilos battle and siege, a separate Zarkheth battle, a separate Asteroth battle and cinematics, seventeen fully playable guardian classes and local/network co-op. The original manuscript includes branching dialogue, alternate quest directions and repeated scenes; this version consolidates the playable main thread without representing those repeats as separate quests.

## Character identities

The character screen offers four persistent identities with gameplay bonuses, without discarding the existing character's XP, inventory, quest flags, COSMOS memory, or story. SMITH improves melee output; RANGER dodges farther and keeps invincibility slightly longer; MYSTIC casts for one less MP; WARDEN adds one point of guarding protection. The extended identity state occupies SRAM bytes 208–210, with its own checksum outside the legacy V5 base and V7 story checksums.

The rest of the named guardian roster from the original manuscript remains narrative canon; new player campaigns for those characters require additional sprites, unique quest writing and balancing.