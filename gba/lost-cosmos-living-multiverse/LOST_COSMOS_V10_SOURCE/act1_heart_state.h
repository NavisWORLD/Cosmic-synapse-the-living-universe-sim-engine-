/* ACT I: THE FIRST HEART (Q05-Q09). Oakwood -> Cragstone ascent -> the
   temple's three rooms -> the Stone Regent -> Malakar at the Heart.
   Game adaptation with original in-game dialogue; nothing here is quoted
   from the owner's private manuscript.

   Rooms (world 0): 3 Oakwood (extended: orchard, inn, manor study),
   91 Cragstone Ascent, 4 Temple Hall (rune doors), 92 Gallery of Blades,
   93 Cold Vault, 94 Heart Chamber.

   Persistence: LC11 page bytes 728-735 (previously unused and zero in every
   V11.0-V11.6 save, inside the LC11 CRC that covers bytes 0-763).
   728 'A', 729 schema 1, 730-731 flags, 732 Regent outcome (0 none,
   1 defeated, 2 restored), 733 reply to Malakar (0 none, 1, 2),
   734 cleared gallery sentries (bits 0-2), 735 reserved.
   Saves without the 'A' marker are migrated from story_flags. */
#ifndef ACT1_HEART_STATE_H
#define ACT1_HEART_STATE_H
#define A1_SRAM_AT 728
#define A1_ASCENT 91
#define A1_GALLERY 92
#define A1_VAULT 93
#define A1_CHAMBER 94
#define A1_IS_ROOM (current_world==0&&current_room>=A1_ASCENT&&current_room<=A1_CHAMBER)
/* Flags. */
#define A1F_MET_RAVEN 0x0001u
#define A1F_PELL_HEALED 0x0002u
#define A1F_MAP_FOUND 0x0004u
#define A1F_MAP_RETURNED 0x0008u
#define A1F_JOURNAL 0x0010u
#define A1F_ASCENT 0x0020u
#define A1F_GUARD 0x0040u
#define A1F_MOULD 0x0080u
#define A1F_ORE 0x0100u
#define A1F_KEY 0x0200u
#define A1F_VAULT_OPEN 0x0400u
#define A1F_KEEP 0x0800u
#define A1F_ORDER 0x1000u
#define A1F_MALAKAR 0x2000u
#define A1F_INN_GIFT 0x4000u
#define A1F_MIGRATED 0x8000u
/* Triggers 210-229. */
#define TR_A1_TREE 210
#define TR_A1_JOURNAL 211
#define TR_A1_TO_ASCENT 212
#define TR_A1_TO_OAKWOOD 213
#define TR_A1_TO_TEMPLE 214
#define TR_A1_CAMP 215
#define TR_A1_LOOKOUT 216
#define TR_A1_TO_ASCENT_TOP 217
#define TR_A1_TO_GALLERY 218
#define TR_A1_TO_VAULT 219
#define TR_A1_HEART_DOOR 220
#define TR_A1_TO_HALL 221
#define TR_A1_GUARD_SEAL 222
#define TR_A1_MURAL 223
#define TR_A1_MOULD 224
#define TR_A1_ORE 225
#define TR_A1_FORGE 226
#define TR_A1_VAULT_DOOR 227
#define TR_A1_KEEP_SEAL 228
#define TR_A1_REGENT 229
#define TR_A1_HEART 230
#define TR_A1_INSCRIPTION 231
/* NPCs added to NPCS[] (32-35). */
#define NPC_A1_BREE 32
#define NPC_A1_PELL 33
#define NPC_A1_WYN 34
#define NPC_A1_ODA 35
/* Orchard (Oakwood): trees on a 4x5 grid, the split oak holds the map case. */
#define A1_SPLIT_TX 14
#define A1_SPLIT_TY 24
/* Regent and Malakar field sprites. */
#define A1_REGENT_OAM 44
#define A1_MALAKAR_OAM 45
#define A1_TRUST_NEEDED 110
static u16 a1_flags=0;
static u8 a1_regent=0,a1_reply=0,a1_sentries=0;
/* Transient. */
static u8 a1_rune_step=0,a1_parry=0,a1_boss=0,a1_strikes=0,a1_sel=0,a1_choice_tag=0,a1_deflects=0,a1_lances=0;
static u8 a1_heat=0,a1_heat_dir=0,a1_flash=0;
static s16 a1_rg_hp=0,a1_rg_max=0;
static u8 a1_rg_core=0,a1_rg_tell=0,a1_rg_phase=0,a1_rg_timer=0,a1_rg_open=0,a1_rg_runes=0,a1_rg_cursor=0,a1_rg_braced=0,a1_rg_stagger=0;
static const char*a1_notice="";
static void act1_reset(void);
static void act1_save_into(u8*b);
static void act1_restore_from(const u8*b,int valid);
static void act1_generate(void);
static void act1_place_room3(void);
static void act1_place_room4(void);
static int act1_spawn(void);
static int act1_interact(u8 t);
static const char*act1_room_name(void);
static void act1_npc_speak(void);
static void act1_script_done(int id);
static void act1_after_cards(int tag);
static int act1_update(u16 newk);
static int act1_draw(void);
static const char*act1_hud_line(void);
static const char*act1_objective(int q);
static void act1_sprites(void);
static int act1_stone_skin(Enemy*e);
static void act1_on_block(Enemy*e);
static int act1_battle_fight(Enemy*e);
static void act1_boss_update(u16 newk);
static void act1_boss_draw(void);
static void act1_frame(void);
static int a1_has(u16 f);
static void cq_set(int q,u8 s);
static void a1_market_buy(int row);
static void a1_rg_act(void);
#ifdef QA_AUTORUN
static void qa_a1_talk(int id);
static void qa_a1_flush(void);
#endif
#endif
