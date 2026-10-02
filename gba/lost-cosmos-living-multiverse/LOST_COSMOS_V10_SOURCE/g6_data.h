/* V10.6 FOUR NEW GAME-ADAPTED OPTIONAL ACT THREADS: original owner's private
 * manuscript inspires gameplay, NEVER reproduce private text in public code.
 * The literary Celestial Harmony and later Ember Passion crystals remain TWO
 * independent earned prerequisites: no silent retcon. Dreamweaver unnamed
 * literary entity != game-appendix Nyssa; Elder Thorne != Technomancer Thorne. */
#ifndef LC_G6_DATA_H
#define LC_G6_DATA_H
#define G6_FIRST_ROOM 30
#define G6_COUNT 4
#define G6_BYTES 32
#define G6_SRAM 5120
#define G6_IS_ROOM (current_world==0 && current_room>=G6_FIRST_ROOM && current_room<G6_FIRST_ROOM+G6_COUNT)
#define TR_G6_PORTAL 62
#define TR_G6_OATH 63
#define TR_G6_CHOICE 64
#define TR_G6_PROOF 65
#define TR_G6_CACHE 66
#define TR_G6_EXIT 67
#define TR_G6_NODE_W 68
#define TR_G6_NODE_C 69
#define TR_G6_NODE_E 70
static u8 g6_done=0,g6_cache=0,g6_pending=0,g6_journal_sel=0;
static u8 g6_step[G6_COUNT]={0},g6_choice[G6_COUNT]={0};
static u8 g6_nodes[G6_COUNT]={0};
/* Ordered, genuinely different three-node spatial puzzles. 0=west 1=center 2=east.
 * Valid saved progress is strictly an ordered prefix (not any arbitrary bitmask). */
static const u8 G6_ORDER[4][3]={{1,0,2},{0,2,1},{2,1,0},{1,2,0}};
static const char*const G6_NODE_DIALOGUE[4][3]={
 {"THE SENTINEL READS THE MIRROR OF MEMORY.",
  "THE CITY ADMITS WHAT ITS GUARDIANS ONCE FEARED.",
  "COURAGE AND MEMORY SEAL THE THREEFOLD RECORD."},
 {"HARMONY RETURNS TO ROOTS LEFT IN SHADOW.",
  "PASSION WARMS THE GROVE WITHOUT CONSUMING IT.",
  "ONE REAL ROOTLEAF HEALS THE FINAL ROOT."},
 {"CLARITY ILLUMINATES THE UNFINISHED DREAM.",
  "THE FESTIVAL RESTORES THE SONG OF SHARED DREAMS.",
  "AN ALLY TRUSTED BEYOND FEAR COMPLETES THE LOOM."},
 {"THE EARLIER THREE PETALS ANCHOR THE RECORD.",
  "THE REFORGED LATTICE CONNECTS THE ARCHIVE.",
  "YOUR ACTUAL CHOSEN ENDING LEAVES A TRACE."}
};
static const u8 G6_PARENT[G6_COUNT]={4,8,12,15};
static const char*const G6_NAME[G6_COUNT]={
 "SENTINEL TESTAMENT","THE DIVIDED GROVE","LOOM OF DREAMS","THE CROWN RECORD"};
static const char*const G6_ACT[G6_COUNT]={"ACT II","ACT III","ACT IV","ACT V"};
static const char*const G6_OATH[G6_COUNT]={
 "WHITE SENTINEL: WHAT SHOULD THE CITY REMEMBER? SEEK THE MIRROR.",
 "THE ROOTS ARE CUT FROM THE VOID. BOTH CRYSTALS MUST ENDURE.",
 "THE FESTIVAL HOLDS UNFINISHED DREAMS. LISTEN TO THE LOOM.",
 "THE LATTICE IS MENDED. WHAT WILL YOU LEAVE IN ITS ARCHIVE?"};
static const char*const G6_QUESTION[G6_COUNT]={
 "SENTINEL: LEFT LISTEN UP CHALLENGE RIGHT RECORD",
 "GROVE: LEFT HEAL UP DEFEND RIGHT REPLANT",
 "LOOM: LEFT REMEMBER UP DREAM RIGHT SHARE",
 "CROWN: LEFT OPEN UP PRESERVE RIGHT WANDER"};
static const char*const G6_HINT[G6_COUNT]={
 "FINISH THE THREE PETALS AND UNITY TRIAL.",
 "RESTORE VOIDWARD PLUS BOTH HARMONY AND PASSION.",
 "RESTORE CLARITY AND FINISH THE DREAM FESTIVAL.",
 "REACH A REAL ENDING AND REFORGE THE LATTICE."};
static const char*const G6_COMPLETED[G6_COUNT]={
 "THE SENTINEL LEAVES THE CITY OPEN TO HONEST MEMORIES.",
 "ROOTS AND SHADOWS MAY SHARE THE SAME GARDEN.",
 "THE DREAMS RETURN TO THOSE WHO CHOSE TO REMEMBER.",
 "YOUR CHOICE IS RECORDED WITHOUT ERASING OTHER ROADS."};
/* A CHOICE has lasting modest optional field value. This is a GAME adaptation,
 * not a ranked preferred decision. All 3 routes can finish each act thread. */
static int g6_attack_bonus(void){int i,n=0;
 for(i=0;i<G6_COUNT;i++)if((g6_done&(1u<<i))&&g6_choice[i]==2)n++;
 return n;
}
static int g6_guard_bonus(void){int i,n=0;
 for(i=0;i<G6_COUNT;i++)if((g6_done&(1u<<i))&&g6_choice[i]==1)n++;
 return n;
}
static void g6_reset(void){int i;g6_done=g6_cache=g6_pending=g6_journal_sel=0;
 for(i=0;i<G6_COUNT;i++){g6_step[i]=0;g6_choice[i]=0;g6_nodes[i]=0;}}
#endif
