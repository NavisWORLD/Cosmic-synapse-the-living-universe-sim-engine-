/* THE HEART OF ERIDORIA campaign quest spine (Q00-Q38) and the playable
   PROLOGUE: ASH IN THE FORGE. Game adaptation, original in-game dialogue.

   Persistence: LC11 page bytes 656-679 (previously unused, zero in every
   V11.0-V11.3 save, inside the existing LC11 CRC that covers bytes 0-763).
   656 'Q', 657 schema 1, 658-667 Q00-Q38 states (2 bits each:
   0 LOCKED, 1 ACTIVE, 2 READY, 3 COMPLETE), 668-669 prologue flags,
   670 choice, 671 forge strikes, 672 raid defeated, 673 raid spared.
   Saves without the 'Q' marker are migrated by campaign_migrate(). */
#ifndef CAMPAIGN_QUESTS_STATE_H
#define CAMPAIGN_QUESTS_STATE_H
#define CQ_COUNT 39
#define CQ_LOCKED 0
#define CQ_ACTIVE 1
#define CQ_READY 2
#define CQ_DONE 3
#define CQ_SRAM_AT 656
/* Prologue flags. */
#define PF_FORGED 0x0001u
#define PF_COSMOS 0x0002u
#define PF_RAID_CLEAR 0x0004u
#define PF_CHOICE 0x0008u
#define PF_FUSE 0x0010u
#define PF_BEACON 0x0020u
#define PF_TRAVELER 0x0040u
#define PF_ASTRID 0x0080u
#define PF_MIRA 0x0100u
#define PF_BOUGHT 0x0200u
#define PF_LAUNCH 0x0400u
#define PF_FORGE_KEY 0x0800u
#define PF_MAP 0x1000u
#define PF_MIGRATED 0x2000u
#define MEM_FIRST_FORGE (1u<<8)
#define NPC_PRO_MIRA 30
#define NPC_PRO_TRAVELER 31
#define TR_PRO_BEACON 200
#define TR_PRO_STALL 201
/* Map placements in Brindlemark (world 0, room 2), tile coordinates. */
#define PRO_FORGE_TX 18
#define PRO_FORGE_TY 43
#define PRO_BEACON_TX 33
#define PRO_BEACON_TY 10
#define PRO_STALL_TX 27
#define PRO_STALL_TY 34
static const char*const CQ_NAMES[CQ_COUNT]={
 "Q00 WAKE AT THE FORGE","Q01 SAVE BRINDLEMARK","Q02 FIX THE BEACON","Q03 ASTRID AND MIRA","Q04 LAUNCH LUNA-ARC",
 "Q05 OAKWOOD'S LOST MAP","Q06 RAVENSWOOD'S WORD","Q07 CRAGSTONE RUNES","Q08 STONE REGENT","Q09 THE FIRST AXIS",
 "Q10 CITY SENTINEL","Q11 COURAGE: WHISPERS","Q12 WISDOM: LIGHT","Q13 UNITY: SOULS","Q14 CHRONOHEART",
 "Q15 SEVERED GUARDIAN","Q16 ENTER BLACK GARDEN","Q17 VOIDWARD: GROVE","Q18 VOIDWARD: LIBRARY","Q19 VOIDWARD: CRYPTS",
 "Q20 VOIDWARD: STARS","Q21 KEEP THE REJECTED","Q22 HEARTWOOD BALANCE","Q23 FROST WOLF","Q24 PHOENIX / PASSION",
 "Q25 ELDORIA'S CURSE","Q26 HOLLOW GROVE EARTH","Q27 CELESTIAL HARMONY","Q28 MARK OF TWILIGHT","Q29 DREAMWEAVER FEST",
 "Q30 ZARKHETH","Q31 REFORGE THE KEY","Q32 EIGHT SIGNALS HOME","Q33 ASTRAL SHARD","Q34 RECKONING: MALAKAR",
 "Q35 ASTEROTH","Q36 THE QUIET","Q37 HEART OF ERIDORIA","Q38 WORLD RESTORED"};
static u8 cq_state[CQ_COUNT];
static u16 pro_flags=0;
static u8 pro_choice=0,pro_strikes=0,pro_raid_kills=0,pro_raid_spared=0;
/* Transient UI: 0 none, 1 forge, 2 beacon seats, 3 choice, 4 story cards. */
static u8 pro_ui=0,pro_sel=0,pro_seat=0,pro_heat=0,pro_heat_dir=0,pro_flash=0;
static u8 pro_script=0,pro_script_n=0;static const char*pro_script_lines[4];
typedef struct{const char*speaker;const char*text;}ProCard;
static const ProCard*pro_cards=0;static u8 pro_card_n=0,pro_card_i=0,pro_card_tag=0;
static void campaign_reset(void);
static void campaign_save_into(u8*b);
static void campaign_restore_from(const u8*b,int valid);
static int prologue_active(void);
static void prologue_begin(void);
static int prologue_interact(u8 t);
static int prologue_board_ship(void);
static int prologue_spawn(void);
static void prologue_enemy_down(Enemy*e,int defeated);
static int prologue_npc_visible(int id);
static void prologue_npc_speak(void);
static const char*prologue_npc_line(void);
static int prologue_npc_advance(void);
static int prologue_update(u16 newk);
static int prologue_draw(void);
static const char*prologue_hud_line(void);
static void prologue_place_room2(void);
static void prologue_shop_bought(void);
static int prologue_raid_mercy(Enemy*e);
#endif
