/* V12.0 LIVING WORLD: six website creatures live on their own in a forest and
   a cave (Cosmo GBA art v2), with an item/stat system and a quest journal
   (Emeth text data). Opened from START > SYSTEM > LIVING WORLD.

   V12.2: each creature also carries a 12-D CST state (cst12.h, ported from
   the site's cst-integrator.mjs / life-brain.mjs / zeref-heart.mjs), seeded
   from the same QSEED window. It drives the Lorenz couplings, motion, needs,
   mood and the life-brain mode weights. Not saved; re-derived on entry.

   HONEST LABEL: the creature "life" is a CLASSICAL simulation. Each creature's
   DNA is a 64-byte window of the cartridge's recorded IBM quantum values
   (QSEED, frozen measured data), picked by the creature's identity. The DNA
   seeds its stats, its Lorenz-attractor motion and its PRNG, and its Shannon
   entropy sets how restless it is. Nothing quantum runs on the GBA.

   Identity: Zeref here is bb-deada969 (0xDEADA969). A Beast Box guest
   creature such as bb-7f9c2a03 is a different identity and is never merged
   into this record; the party roster, LCX1/LCM1 mailbox import and LC11 saves
   are untouched.

   Persistence (V12.1): SRAM 7936-8191, the free tail of the journaled main page,
   so the journal banks now snapshot it. V12.0 used 16384-16639, which is inside
   journal bank 1 and got overwritten by journal commits; V12.1 migrates a valid
   V12.0 block once and never writes 16384. Offsets relative to LW_SRAM:
   +0 'L','W',schema 1, version 0; +4 world/flags; +8 65 item counts;
   +76 six 12-byte creature records (hunger, energy, mood, bond, hp, level,
   xp u16, equip[4] as item+1); +156 quest reward claimed bits (5 bytes);
   +252 u32 additive checksum of +0..+251. The block is shared by all
   save slots: the V11 slot copier (LCM1, 1888-byte payload, 128 spare bytes) has
   no room for 256 bytes without a format change, so it is still not included. Saves without the
   marker start fresh. */
#ifndef LIVING_WORLD_STATE_H
#define LIVING_WORLD_STATE_H
typedef signed int s32;
#include "cst12.h"
#define LW_SRAM 7936      /* V12.1: free tail of the journaled main page, after LCL1 7296..7815 */
#define LW_SRAM_V120 16384 /* V12.0 location (inside journal bank 1): read once to migrate, never written */
#define LW_WISP_TILE 512
#define LW_NPC_TILE 528
#define LW_N 6
#define LW_W 512
#define LW_H 256
typedef struct{
 s32 x,y;            /* 24.8 px */
 s32 lx,ly,lz;       /* Lorenz state, Q8 */
 s32 tx,ty;          /* action target, px */
 u32 id,rng;
 u8 dna[64];
 u8 entropy;         /* 0..100 */
 u8 hunger,energy,mood,bond,hp,level,trig,action;
 u16 xp,timer,since;
 u8 equip[4];
 u8 face,frame,moving,found;
 u8 base_hp,base_atk,base_def,base_spd,base_focus,base_luck;
 Cst12 cst;          /* V12.2: 12-D CST state, seeded from dna[], never saved */
}LwBeast;
static LwBeast lw_b[LW_N];
static u8 lw_inv[V12_ITEM_COUNT];
static u8 lw_claimed[5];
static volatile u8 lw_active=0,lw_request=0;
static u8 lw_world=0,lw_focus=0,lw_page=0,lw_sel=0,lw_card=0,lw_dirty_art=1,lw_night=0;
static u16 lw_clock=0,lw_card_timer=0,lw_msg_timer=0;
static s32 lw_px=256<<8,lw_py=160<<8,lw_wx=100<<8,lw_wy=60<<8,lw_wl[3];
static s16 lw_camx=0,lw_camy=0;
static LwBeast lw_npc;
#define LW_WALK_N 2       /* V12.2: two extra cast walkers per world (shared palettes) */
#define LW_WALK_TILE 592
static LwBeast lw_walk[LW_WALK_N];
static u8 lw_walk_f[LW_WALK_N]={255,255};
static volatile u16 lw_walk_frames=0,lw_cst_picks=0,lw_heartbeats=0,lw_hud_scrolls=0;
static volatile u8 lw_cast_form=0;
static u8 lw_pmoving=0,lw_pface=0,lw_arin_f=255,lw_wisp_f=255,lw_npc_f=255,lw_npc_w=255,lw_npc_beat=0,lw_npc_pal_dirty=1,lw_cast_f=0;
static volatile u16 lw_journal_patches=0;
static u8 lw_end_d_flag=0,lw_scene_q=0;static u8 lw_scene_k=0;static volatile u16 lw_scene_reads=0;
static volatile u8 lw_migrated=0,lw_items_migrated=0;
static volatile u16 lw_synapse_hits=0,lw_synapse_swaps=0;
static volatile u16 lw_npc_walk_frames=0,lw_sneezes=0,lw_yawns=0,lw_wisp_lunges=0;
static char lw_msg[88]; /* V12.2: 3 lines of 28 (the HUD shows 2 and scrolls) */
/* Read by the emulator test. */
static volatile u16 lw_entries=0,lw_exits=0,lw_decisions=0,lw_dark_reacts=0,lw_items_used=0,lw_quests_done=0;
static volatile u32 lw_moved_px=0;
static void lw_enter(void);
static void lw_exit(void);
static void lw_update(u16 k,u16 newk);
static void lw_render(void);
#endif
