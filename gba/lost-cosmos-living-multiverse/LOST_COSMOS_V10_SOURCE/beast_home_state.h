/* V11.5 BEAST HOME: a cottage in Brindlemark where the bonded beast lives.

   The beast that lives here is the active party creature: a Lost COSMOS
   starter from the Sol nursery, a wild bond, or a creature brought in
   through the Beast Box bridge. It is drawn with the same art as the field
   follower and keyed by its creature identity (LcCreature.identity), so the
   same beast is recognised across save/load and across trips home.

   Persistence: LC11 page bytes 676-727 (previously unused, zero in every
   V11.0-V11.4 save, inside the LC11 CRC that covers bytes 0-763).
   676 'H', 677 schema 1, 678-679 reserved, then four 12-byte care records:
   identity u32, fullness, joy, rest, visits, care count u16, flags u8, pad.
   Saves without the 'H' marker start with no records. */
#ifndef BEAST_HOME_STATE_H
#define BEAST_HOME_STATE_H
#define BH_ROOM 90
#define BH_IS_ROOM (current_world==0&&current_room==BH_ROOM)
#define BH_SRAM_AT 676
#define BH_RECORDS 4
/* Home walls (tiles); the camera holds still on the whole room. */
#define BH_X0 20
#define BH_Y0 22
#define BH_X1 39
#define BH_Y1 36
#define TR_BH_ENTER 202
#define TR_BH_EXIT 203
#define TR_BH_FOOD 204
#define TR_BH_TOY 205
#define TR_BH_BED 206
#define TR_BH_PLATE 207
/* Brindlemark (world 0, room 2) cottage door, tile coordinates. */
#define BH_DOOR_TX 8
#define BH_DOOR_TY 28
/* Beast states. */
#define BHS_IDLE 0
#define BHS_WALK 1
#define BHS_EAT 2
#define BHS_PLAY 3
#define BHS_SLEEP 4
#define BHS_HAPPY 5
/* Emote OBJ: tiles 992..1007 (above the Spark field tiles 912..959),
   OAM 46, palette 12 (the Spark field palette, unused inside the home). */
#define BH_EMOTE_TILE 992
#define BH_EMOTE_OAM 46
#define BH_EMOTE_PAL 12
static u32 bh_id[BH_RECORDS];
static u8 bh_full[BH_RECORDS],bh_joy[BH_RECORDS],bh_rest[BH_RECORDS],bh_visits[BH_RECORDS],bh_flags[BH_RECORDS];
static u16 bh_care[BH_RECORDS];
/* Runtime (not saved): which record is home, where the beast is, what it does. */
static s8 bh_cur=-1;
static s16 bh_x,bh_y,bh_tx,bh_ty;
static u8 bh_state=BHS_IDLE,bh_goal=BHS_IDLE,bh_face=0,bh_emote=255,bh_bowl=0;
static u16 bh_timer=0,bh_emote_timer=0,bh_tick=0,bh_pet_cd=0,bh_moved=0;
static void bh_reset(void);
static void bh_save_into(u8*b);
static void bh_restore_from(const u8*b,int valid);
static int beast_home_interact(u8 t);
static int beast_home_pet(void);
static void beast_home_place_room2(void);
static void beast_home_generate(void);
static void beast_home_tick(void);
static void beast_home_sprites(void);
static int beast_home_hud(void);
#endif
