"""Native-C host-simulation regression for V8 palette, true indexed UI,
fixed-point parallax, story/codex, character stances and V7 save migration.
Real mGBA emulation is a SEPARATE release gate.
"""
from pathlib import Path
import subprocess
R=Path(__file__).resolve().parent
src=(R/'host_qa_v5.c').read_text().split('\n#ifdef HOST_QA\nint main(',1)[0]
src += r'''
#include <assert.h>
#include <stdio.h>
static int bgpix(int tile,int x,int y){
 volatile u32*t=VRAM32+(0x4000/4)+tile*8;
 return (int)((t[y]>>((x&7)*4))&15);
}
static u16 cell(int x,int y){int b=(x>=32)+((y>=32)<<1);return screenblock(BG_MAP_BASE+b)[(y&31)*32+(x&31)];}
int main(void){int w,i;u16 before[8];
 init_new_game();init_graphics();generate_surface();
 /* Glyph A is raised: white ink and nonzero distinct shadow on opaque ink.
    This cannot visually inherit patterned terrain colors. */
 assert(bgpix(64+font_index('A'),1,1)==1);
 assert(bgpix(64+font_index('A'),2,2)!=0);
 assert(bgpix(62,0,0)==2);
 for(w=0;w<8;w++){
   set_world_palette(w);
   for(i=0;i<8;i++){
     assert(BG_PALETTE[i*16+1]==MATERIAL_RAMP[w][i][0]);
     assert(BG_PALETTE[i*16+2]==MATERIAL_RAMP[w][i][1]);
     assert(BG_PALETTE[i*16+3]==MATERIAL_RAMP[w][i][2]);
   }
   /* Five material groups are distinguishable; no shared aqua fill. */
   assert(BG_PALETTE[1]!=BG_PALETTE[1*16+1]);
   assert(BG_PALETTE[1]!=BG_PALETTE[2*16+1]);
   assert(BG_PALETTE[1]!=BG_PALETTE[4*16+1]);
 }
 current_world=0;set_world_palette(0);
 map_put(1,30,T_FLOOR,0,C_FREE,0);map_put(2,30,T_PATH,0,C_FREE,0);
 map_put(3,30,T_WALL,0,C_WALL,0);map_put(4,30,T_WATER,0,C_FREE,0);
 map_put(5,30,T_GRASS,0,C_FREE,0);map_put(6,30,T_LAVA,0,C_HAZARD,0);
 map_put(7,10,T_FLOOR,0,C_FREE,0);
 assert((cell(1,30)>>12)==0);
 assert((cell(2,30)>>12)==1);
 assert((cell(3,30)>>12)==2);
 assert((cell(4,30)>>12)==4);
 assert((cell(5,30)>>12)==5);
 assert((cell(6,30)>>12)==7);
 assert((cell(7,10)>>12)==6);
 assert(collision[mi(6,30)]==C_HAZARD);
 generate_surface();assert(REG_DISPCNT&BG2_ENABLE);
 assert(REG_BG2CNT==(1|(BG_TILE_CB<<2)|(SPACE_PARALLAX_MAP<<8)));
 state12[0]=255;state12[2]=200;state12[3]=190;state12[4]=100;
 state12[5]=250;state12[10]=90;
 assert(view_projection12()>=0&&view_projection12()<=7);
 refresh_camera();assert(REG_BG2HOFS!=REG_BG0HOFS);
 cinema_start(0,0);assert(REG_BG2CNT==(1|(CINEMA_CB<<2)|(CINEMA_MAP<<8)));
 cinema_end();assert(REG_DISPCNT&BG2_ENABLE);
 for(i=0;i<20;i++){
  assert(CHRONICLE[i].title && CHRONICLE[i].scene && CHRONICLE[i].quest);
 }
 assert(chronicle_unlocked(0)&&!chronicle_unlocked(19));
 assert(current_objective()[0]=='T');
 story_flags=ST_TOWN;assert(current_objective()[0]=='F');
 story_flags=ST_TOWN|ST_OAKWOOD|ST_PUZZLE;assert(current_objective()[0]=='F');
 /* Character stance switch changes attack/magic/defense or dodge recovery. */
 character_style=0;assert(class_melee_bonus()==1);
 character_style=1;dodge_cooldown=0;player_dodge(KEY_RIGHT);assert(dodge_cooldown==23);
 character_style=2;assert(class_magic_bonus()==1);
 character_style=3;assert(class_defense_bonus()==1);
 story_flags=ST_TOWN|ST_OAKWOOD|ST_PUZZLE|ST_MALAKAR|ST_HEART;
 codex_sel=11;character_style=2;save_game();
 assert(save_valid()&&SRAM[208]==0xD8&&SRAM[209]==2&&SRAM[210]==11);
 assert(chronicle_unlocked(4));
 character_style=0;codex_sel=0;load_game();
 assert(character_style==2&&codex_sel==11&&story_flags&ST_HEART);
 SRAM[212]^=1;character_style=3;load_game();
 assert(save_valid()&&character_style==0&&codex_sel==0&&story_flags&ST_HEART);
 /* Actual mGBA-produced V7 save must be accepted without inventing V8 data. */
 {FILE *f=fopen("qa_fixtures/v7_mgba_boot1.sav","rb");assert(f);
 assert(fread((void*)HOST_SRAM,1,32768,f)==32768);fclose(f);}
 assert(save_valid());init_new_game();load_game();
 assert(keys_found&1);assert(character_style==0&&codex_sel==0);
 pause_page=0;pause_sel=14;game_mode=MODE_PAUSE;
 update_pause(KEY_A);assert(pause_page==15);
 update_pause(KEY_A);assert(character_style==1);
 update_pause(KEY_B);assert(pause_page==0);
 pause_sel=13;update_pause(KEY_A);assert(pause_page==14);
 update_pause(KEY_RIGHT);assert(codex_sel==1);
 draw_pause();assert((screenblock(UI_MAP_BASE)[2*32+2]&1023)==64+font_index('E'));
 puts("PASS V8 native C visual/UI: material colors, raised opaque glyphs, parallax, cinema return, 20-page story, quest, character stances, V7 save migration and SRAM extension");
 return 0;
}
'''
(R/'v8_visual_story_host.c').write_text(src)
subprocess.run(['clang','-DQA_AUTORUN','-DHOST_QA','-O2','-Wno-unused-function','v8_visual_story_host.c','-o','v8_visual_story_host'],cwd=R,check=True)
subprocess.run([str(R/'v8_visual_story_host')],cwd=R,check=True)
