/* ACT II: THE TRIAL OF MIRRORS (Q10-Q14). REEF identity: Tide Memory, the
   Forgotten City and the Hall of Whispers (kit world registry). The rooms are
   stored in world 0 like Act I so no saved world index changes; the canonical
   labels are kept as aliases in docs/V11_9_ACT2_MIRRORS.md.
   Game adaptation with original in-game dialogue; nothing here is quoted
   from the owner's private manuscript.

   Rooms (world 0): 95 Tide Memory, 96 Forgotten City, 97 Hall of Whispers,
   98 Chamber of Illumination, 99 Arena of Souls, 100 Chronoheart Sanctum,
   101 Harmony Clearing (side area). Room 5 becomes the city's Old Quarter.

   Persistence: LC11 page bytes 736-745 (previously unused and zero in every
   V11.0-V11.8 save, inside the LC11 CRC that covers bytes 0-763).
   736 'B', 737 schema 1, 738-739 flags, 740 mirror rounds won (lifetime),
   741-742 Illumination panel order (5 x 3 bits), 743 arena outcome
   (bits 0-2 spared sentries, bits 3-5 shattered), 744 Chronoheart slips,
   745 reserved. Bytes 746-763 stay free. Saves without the 'B' marker are
   migrated from the story flags the old Dream Veil route already earned. */
#ifndef ACT2_MIRRORS_STATE_H
#define ACT2_MIRRORS_STATE_H
#define A2_SRAM_AT 736
#define A2_TIDE 95
#define A2_CITY 96
#define A2_WHISPERS 97
#define A2_LIGHT 98
#define A2_ARENA 99
#define A2_SANCTUM 100
#define A2_HARMONY 101
#define A2_IS_ROOM (current_world==0&&current_room>=A2_TIDE&&current_room<=A2_HARMONY)
/* Flags. */
#define A2F_ECHO1 0x0001u
#define A2F_ECHO2 0x0002u
#define A2F_ECHO3 0x0004u
#define A2F_GATE 0x0008u
#define A2F_LYSARA 0x0010u
#define A2F_COURAGE 0x0020u
#define A2F_WISDOM 0x0040u
#define A2F_UNITY 0x0080u
#define A2F_PACT 0x0100u
#define A2F_KAELEN 0x0200u
#define A2F_CHRONO 0x0400u
#define A2F_SPIRIT1 0x0800u
#define A2F_SPIRIT2 0x1000u
#define A2F_SPIRIT3 0x2000u
#define A2F_HARMONY 0x4000u
#define A2F_MIGRATED 0x8000u
#define A2F_ECHOES (A2F_ECHO1|A2F_ECHO2|A2F_ECHO3)
#define A2F_SPIRITS (A2F_SPIRIT1|A2F_SPIRIT2|A2F_SPIRIT3)
/* Triggers 232-251. */
#define TR_A2_TO_BRINDLE 232
#define TR_A2_ECHO 233
#define TR_A2_CITY_GATE 234
#define TR_A2_TO_TIDE 235
#define TR_A2_TO_WHISPERS 236
#define TR_A2_TO_LIGHT 237
#define TR_A2_TO_ARENA 238
#define TR_A2_TO_SANCTUM 239
#define TR_A2_TO_HARMONY 240
#define TR_A2_TO_OLDQ 241
#define TR_A2_TO_CITY 242
#define TR_A2_MIRROR 243
#define TR_A2_WHISPER 244
#define TR_A2_PANEL 245
#define TR_A2_LIGHT_NOTE 246
#define TR_A2_LEVER 247
#define TR_A2_SPARE 248
#define TR_A2_CHRONOHEART 249
#define TR_A2_HARMONY_STONE 250
#define TR_A2_MURAL 251
/* NPCs appended to NPCS[] (36-40); the White Sentinel (18) becomes Lysara. */
#define NPC_A2_LYSARA 18
#define NPC_A2_KAELEN 36
#define NPC_A2_KAELEN_SANCTUM 37
#define NPC_A2_SPIRIT_SONG 38
#define NPC_A2_SPIRIT_ROOT 39
#define NPC_A2_SPIRIT_LIGHT 40
/* Tide cycle (frames): low water for A2_TIDE_LOW, then high water. */
#define A2_TIDE_CYCLE 720
#define A2_TIDE_LOW 480
/* Arena. */
#define A2_CHANNEL_MAX 900
#define A2_LEVER_TX 32
#define A2_LEVER_TY 30
#define A2_MIRROR_WINS 3
#define A2_DUEL_HP 6
static u16 a2_flags=0;
static u8 a2_rounds=0,a2_arena_result=0,a2_slips=0;
static u8 a2_order[5]={3,0,4,1,2};
/* Transient (never saved). */
static u16 a2_tide=0,a2_channel=0;
static u8 a2_high=0,a2_arena=0,a2_kneel=0,a2_kneel_t[3]={0,0,0},a2_jam=0;
static u8 a2_sel=0,a2_pick=255,a2_last=1,a2_mirror=1,a2_wins=0,a2_hp=A2_DUEL_HP,a2_phase=0,a2_timer=0,a2_result=0;
static u8 a2_ring[3]={0,0,0},a2_ring_lock=0,a2_ring_tick=0,a2_slow=0,a2_slow_uses=0,a2_flash=0;
static const char*a2_notice="";
static void act2_reset(void);
static void act2_save_into(u8*b);
static void act2_restore_from(const u8*b,int valid);
static void act2_generate(void);
static void act2_place_room5(void);
static int act2_spawn(void);
static int act2_interact(u8 t);
static const char*act2_room_name(void);
static void act2_npc_speak(void);
static int act2_npc_visible(int id);
static void act2_script_done(int id);
static void act2_after_cards(int tag);
static int act2_update(u16 newk);
static int act2_draw(void);
static const char*act2_hud_line(void);
static const char*act2_objective(int q);
static void act2_sprites(void);
static int act2_sentry_hit(Enemy*e,int dmg);
static int act2_beast_busy(void);
static int act2_no_duel(void);
static void act2_frame(void);
static int a2_has(u16 f);
static int a2_done(int q);
static s16 a2_beast_x(void);
static s16 a2_beast_y(void);
static const u8 A2_ECHO_X[3]={24,32,40},A2_ECHO_Y[3]={30,26,34};
#ifdef QA_AUTORUN
static void qa_a2_flush(void);
#endif
#endif
