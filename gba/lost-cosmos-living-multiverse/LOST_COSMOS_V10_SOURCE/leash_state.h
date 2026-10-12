/* V11.8 "remove the leash": state, save layout and the perception-safe
 * observation block. The behaviour lives in leash.h.
 *
 * LCL1 field record: 520 bytes at SRAM 7296..7815 inside the journaled main
 * page (0..8191), right after COMP (7168..7295). Layout in
 * docs/V11_8_LEASH_OFF.md. It only holds what the beast itself did or
 * perceived: its own steps, the map cells it walked, visible points of
 * interest, NPCs and encounters it saw, calls it answered. No story flags,
 * quest state, RNG, enemy stats or hidden triggers are stored or exposed. */
#ifndef LC_LEASH_STATE_H
#define LC_LEASH_STATE_H
#define LF_SRAM 7296
#define LF_BYTES 520
#define LF_SLOTS 48
#define LF_FAV 8
#define LF_EWRAM __attribute__((section(".ewram")))
enum{LFG_IDLE=0,LFG_EXPLORE,LFG_POI,LFG_NPC,LFG_ALERT,LFG_REST,LFG_RETURN,LFG_CHECKIN,LFG_COUNT};
typedef struct{
 u32 moves_ok,moves_blocked;
 u16 cells,pois,npcs,encounters,calls,returns,catchups,checkins,no_path,secs;
 u16 done[LFG_COUNT];
 u8 fav_loc[LF_FAV],fav_cell[LF_FAV];u16 fav_n[LF_FAV];
 u8 slot_loc[LF_SLOTS];u8 slot_mask[LF_SLOTS][8];
 u8 flags; /* bit0 leash on, bit1 record created for an older save */
} LfRecord;
/* What a companion standing at its own tile could perceive this frame.
 * Distances are in tiles (Manhattan), 255 = nothing within sight (12 tiles).
 * sight[] is the 5x5 block around the beast: 0 open, 1 wall, 2 hazard. */
typedef struct{
 u8 version,leash_on,called,goal,loc,cell_new;
 u8 beast_tx,beast_ty,player_tx,player_ty;
 u8 enemy_dist,npc_dist,poi_dist,energy;
 u8 sight[25];
} LfObs;
static LfRecord lf_rec LF_EWRAM;
static volatile LfObs leash_obs;
static u8 leash_on=0;
static void leash_reset(void);
static void leash_save(void);
static void leash_restore(void);
static void leash_tick(void);
static int leash_autonomous(void);
static void leash_call(void);
static void leash_toggle(void);
static void leash_room_reset(void);
static void leash_draw_record(void);
#endif
