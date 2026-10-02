/* V10.2: Book-inspired OPTIONAL atlas, disjoint SRAM extension. Not raw book prose.
   New rooms 0:13..28; older room IDs, legacy save and QSEED are untouched.
   Indices 13..15 are new game adaptation of book appendix, not direct novel scenes. */
#define ARC_FIRST_ROOM 13
#define ARC_STAGES 16
#define ARC_EPILOGUE_ROOM 29
#define ARC_SRAM 2048
#define ARC_SRAM_BYTES 32
#define ARC_IS_ROOM (current_world==0 && current_room>=ARC_FIRST_ROOM && current_room<ARC_FIRST_ROOM+ARC_STAGES)
#define ARC_BOSSES ((u16)((1u<<1)|(1u<<3)|(1u<<6)|(1u<<8)|(1u<<14)|(1u<<15)))
#define ARC_MERCY  ((u16)((1u<<1)|(1u<<6)|(1u<<8)|(1u<<14)))
/* Completed stages use a sequential index to avoid silent early unlocks. */
static u8 arc_progress=0,arc_solved=0,arc_boss_done=0,arc_pending=0;
static u8 arc_route=0,arc_ally=0,arc_petals=0,arc_anchors=0;
static u16 arc_mercy_mask=0,arc_secret_mask=0;
static u32 arc_guardians_mask=0;
static const char* const ARC_NAMES[ARC_STAGES]={
 "FOREST THRESHOLD","TRIAL CAVERN","SENTINEL HALL","WHISPER MIRRORS",
 "SILVER TOMES","THE WORLD TREE","HARMONY GROVE","PETAL GATEWAY",
 "THREE TRIALS","VERDANT ALTAR","TWILIGHT PASS","DAWN DUSK MARK",
 "DREAM MEADOW","CHRONO ANNEX","VOIDWARD RUINS","TWILIGHT CITADEL"};
static const char* const ARC_TASK[ARC_STAGES]={
 "PROVE YOU COME AS AN ALLY.","THE BEAST SEEKS A GENTLE ANSWER.",
 "THE SENTINEL NEEDS REASON.","REFLECT ON YOUR FEAR OF LOSS.",
 "THE TOMES REVEAL A BRIEF LIGHT.","CHOOSE THE WORLD TREES PATH.",
 "RESTORE THE ROOTS OF HARMONY.","PLACE THE THREE PETAL RUNES.",
 "FACE A TRIAL OF MUTUAL TRUST.","LISTEN TO THE WINGED GUIDE.",
 "BALANCE DARKNESS AND LIGHT.","EARN THE MARK OF DUSK.",
 "STEP THROUGH THE DREAM GATE.","STABILIZE THE BROKEN HOUR.",
 "KEEP THE VOID OUT OF MEMORY.","CLOSE THE RIFT AT THE CITADEL."};
/* All riddles are game dialogue adaptations, not claims of verbatim book text.
   Answer ordering: left/up/right; stage 5 is a three-way independent choice. */
static const char* const ARC_RIDDLES[ARC_STAGES]={
 "FOREST: L TAKE U LISTEN R FLEE",
 "BEAST: L FORCE U FEAR R EMPATHY",
 "SENTINEL: L REASON U THREAT R SILENCE",
 "MIRROR: L FORGET U ACCEPT R HIDE",
 "TOMES: L A STAR U A WALL R A SHADOW",
 "TREE: L UNITY U STRENGTH R DISCOVERY",
 "GROVE: L RUPTURE U RESTORE R IGNORE",
 "PETALS: L UNITY U WISDOM R FEAR",
 "TRIALS: L ISOLATE U TRUST R CONQUER",
 "ALTAR: L TURN BACK U BREAK R LISTEN",
 "TWILIGHT: L BALANCE U DARK R LIGHT",
 "MARK: L DENY U EMBRACE R ESCAPE",
 "MEADOW: L FIGHT U LEAVE R EXPLORE",
 "CHRONO: L ERASE U MEND R SHATTER",
 "VOIDWARD: L FORGET U HIDE R REMEMBER",
 "CITADEL: L DESTROY U REJOIN R FLEE"};
static const u8 ARC_ANSWER[ARC_STAGES]={1,3,1,2,1,3,2,2,2,3,1,2,3,2,3,2};
static const char* const ARC_PASSED[ARC_STAGES]={
 "FOREST GUARD OPENS THE ROAD.","THE CAVERN BEAST HAS A CHOICE.",
 "THE WHITE SENTINEL GUIDES YOU.","THE MIRROR CANNOT OWN YOUR FEAR.",
 "THE SILVER TOMES OPEN.","YOUR PATH IS YOUR OWN.",
 "THE GROVE BEGINS TO HEAL.","THE PETAL GATE ANSWERS.",
 "HEART MIND AND SPIRIT UNITE.","THE ALTAR REMEMBERS A NAME.",
 "TWILIGHT RESTORES THE CROSSING.","THE DAWN DUSK MARK AWAKENS.",
 "A WINGED GUIDE OPENS THE VEIL.","THE CHRONO ANNEX STABILIZES.",
 "VOIDWARD KEEPS ITS HISTORY.","THE CITADEL RIFT GOES QUIET."};
/* Guardian appendix names are kept distinct: Elder Thorne != technomancer Thorne;
   dream-festival speaker != Nyssa without the author's confirmation. */
typedef struct {const char*name;const char*discipline;u8 attack;u8 guard;} ArcGuardian;
static const ArcGuardian ARC_GUARDIANS[17]={
 {"ARIN","WARRIOR",2,0},{"ELIRA","ARCHER",1,0},
 {"THALIAN","MAGE",0,0},{"LYRA","HEALER",0,1},
 {"DARIUS","PROTECTOR",0,2},{"SORIN","ELEMENTALIST",1,0},
 {"ANARA","ROGUE",1,0},{"ELYSIA","GEOMANCER",0,1},
 {"KAELEN","TIME WEAVER",0,1},{"SERAPHINA","MYSTIC",0,1},
 {"MARISOL","ENCHANTRESS",1,0},{"RIVEN","SHADOWMANCER",1,0},
 {"NYSSA","DREAMWEAVER",0,1},{"ZEPHRA","SPIRITBINDER",1,0},
 {"THORNE","TECHNOMANCER",1,0},{"MAIA","ARTIFICER",1,1},
 {"ALTAIR","HISTORIAN",0,1}
};
/* Player agency: all 3 routes are playable and change later field/party mechanics.
   Bonus applies only after the World Tree chapter is completed (progress>=6). */
static int arc_guardian_attack(void){int atk=(arc_guardians_mask&(1u<<arc_ally))?ARC_GUARDIANS[arc_ally].attack:0;
 return atk+completion_attack_bonus()+g5_bonus_attack(arc_ally)+g6_attack_bonus()+g7_attack_bonus()+((arc_progress>=6&&arc_route==2)?2:0);
}
static int arc_guardian_guard(void){int guard=(arc_guardians_mask&(1u<<arc_ally))?ARC_GUARDIANS[arc_ally].guard:0;
 return guard+completion_guard_bonus()+g5_bonus_guard(arc_ally)+g6_guard_bonus()+g7_guard_bonus()+((arc_progress>=6&&arc_route==1)?2:0);
}
