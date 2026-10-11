/* V11.6 FIRST-PERSON / MODE-7 VIEW (prototype).

   A reversible way to look at the current field map in perspective. The
   map, collision, triggers, NPCs and saves are the ordinary top-down ones:
   this view only reads them. Entering builds an 8bpp affine copy of the
   BG0 map in VRAM areas that the field does not use (charblock 2, the
   cinema tiles, and screenblocks 29-30, the space parallax/cinema maps;
   cinema and space rebuild both when they start). Leaving restores the
   saved display registers, so the top-down game resumes untouched.

   Camera: the Beast Cage orbit camera (apps/beastbox-cloud components/
   cage-pocket-dimension.tsx): a 46 degree vertical-FOV perspective camera
   placed at  zoom*(sin(phi)sin(theta), cos(phi), sin(phi)cos(theta))
   around a focus and looking at it, with phi clamped to 0.35..1.47 rad,
   default theta 0.7, phi 1.05, zoom 10.6, and key steps of 0.17 rad
   (theta) and 0.14 rad (phi). Here the focus is the player on the ground,
   one cage unit is 8 pixels (one map tile), and theta follows the
   player's heading. EYE puts the camera at the player's eye instead.
   Not saved: nothing about the view is written to SRAM. */
#ifndef FIRST_PERSON_STATE_H
#define FIRST_PERSON_STATE_H
#define FP_CAM_EYE 0
#define FP_CAM_CAGE 1
static u8 fp_active=0,fp_request=0,fp_cam=FP_CAM_EYE;
static u16 fp_entries=0,fp_exits=0;
static u16 fp_unique=0,fp_overflow=0;
static u16 fp_heading=0;        /* 4096 = full turn, 0 = north (map -y) */
static s16 fp_phi[2];          /* polar angle, 4096 = full turn */
static s16 fp_zoom10=106;      /* cage zoom x10 */
static s16 fp_sub_x=0,fp_sub_y=0;
static int fp_beast_x=0,fp_beast_y=0; /* 24.8 px */
static volatile u16 fp_walked=0,fp_turned=0;
/* Read by the emulator test: volatile keeps them in the cartridge. */
static volatile s16 fp_beast_sx=-99,fp_beast_sy=-99,fp_beast_scale=0;
static volatile s16 fp_horizon=0;
static void fp_enter(void);
static void fp_exit(void);
static void fp_update(u16 k,u16 newk);
static void fp_render(void);
static void fp_vblank(void);
#endif
