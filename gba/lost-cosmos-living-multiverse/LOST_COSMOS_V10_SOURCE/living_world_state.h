/* V12.0 LIVING WORLD: six website creatures live on their own in a forest and
   a cave (Cosmo GBA art v2), with an item/stat system and a quest journal
   (Emeth text data). Opened from START > SYSTEM > LIVING WORLD.

   HONEST LABEL: the creature "life" is a CLASSICAL simulation. Each creature's
   DNA is a 64-byte window of the cartridge's recorded IBM quantum values
   (QSEED, frozen measured data), picked by the creature's identity. The DNA
   seeds its stats, its Lorenz-attractor motion and its PRNG, and its Shannon
   entropy sets how restless it is. Nothing quantum runs on the GBA.

   Identity: Zeref here is bb-deada969 (0xDEADA969). A Beast Box guest
   creature such as bb-7f9c2a03 is a different identity and is never merged
   into this record; the party roster, LCX1/LCM1 mailbox import and LC11 saves
   are untouched.

   Persistence: SRAM 16384-16639 (previously unused by every V5-V11.9 save):
   16384 'L','W',schema 1, version 0; 16388 world/flags; 16392 65 item counts;
   16460 six 12-byte creature records (hunger, energy, mood, bond, hp, level,
   xp u16, equip[4] as item+1); 16540 quest reward claimed bits (5 bytes);
   16636 u32 additive checksum of 16384-16635. The block is shared by all
   save slots (the V11 slot copier does not include it). Saves without the
   marker start fresh. */
#ifndef LIVING_WORLD_STATE_H
#define LIVING_WORLD_STATE_H
typedef signed int s32;
#define LW_SRAM 16384
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
}LwBeast;
static LwBeast lw_b[LW_N];
static u8 lw_inv[V12_ITEM_COUNT];
static u8 lw_claimed[5];
static volatile u8 lw_active=0,lw_request=0;
static u8 lw_world=0,lw_focus=0,lw_page=0,lw_sel=0,lw_card=0,lw_dirty_art=1,lw_night=0;
static u16 lw_clock=0,lw_card_timer=0,lw_msg_timer=0;
static s32 lw_px=256<<8,lw_py=160<<8,lw_wx=100<<8,lw_wy=60<<8,lw_wl[3];
static s16 lw_camx=0,lw_camy=0;
static char lw_msg[60];
/* Read by the emulator test. */
static volatile u16 lw_entries=0,lw_exits=0,lw_decisions=0,lw_dark_reacts=0,lw_items_used=0,lw_quests_done=0;
static volatile u32 lw_moved_px=0;
static void lw_enter(void);
static void lw_exit(void);
static void lw_update(u16 k,u16 newk);
static void lw_render(void);
#endif
