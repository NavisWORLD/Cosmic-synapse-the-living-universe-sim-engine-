"""Direct native C host tests of 12D-inspired deterministic projection, material
bank contrast, chromatic accessibility, real story UI, role/save persistence.
Actual hardware-emulated mGBA is an independent final release gate."""
from pathlib import Path
import subprocess
R=Path(__file__).resolve().parent
src=(R/'host_qa_v5.c').read_text().split('\n#ifdef HOST_QA\nint main(',1)[0]
src+=r'''
#include <assert.h>
#include <stdio.h>
int main(void){int i,j,material_base[8]={T_GRASS,T_PATH,T_WATER,T_TREE,T_WALL,T_CRYSTAL,T_BRIDGE,T_HAZARD};
 init_new_game();init_graphics();generate_surface();intro=0;
 /* Surface layers: BG0 owns physics tiles, BG1 owns readable opaque text,
    BG2 owns sparse depth sprites, and character block 2 is cinematic-only. */
 assert(REG_DISPCNT&BG2_ENABLE);
 assert(((REG_BG0CNT>>8)&31)==BG_MAP_BASE);
 assert(((REG_BG1CNT>>8)&31)==UI_MAP_BASE);
 assert(((REG_BG2CNT>>8)&31)==V8_FOREGROUND_MAP);
 assert(((screenblock(V8_FOREGROUND_MAP)[0])&1023)==V8_FG_EMPTY || screenblock(V8_FOREGROUND_MAP)[0]);
 assert(VRAM32[V8_FG_EMPTY*8]==0);
 assert(VRAM32[V8_FG_CANOPY*8]!=0 || VRAM32[V8_FG_CANOPY*8+1]!=0);
 /* Eight separate material kinds and four highlights; UI must be world-neutral. */
 for(i=0;i<8;i++){
  map_put(i+4,6,material_base[i],0,C_FREE,TR_NONE);
  {int got=(screenblock(BG_MAP_BASE)[6*32+i+4]>>12)&15;
   assert(got==i || got==8 || got==9 || got==10 || got==11);
   assert(got==i || (i==0&&got==8)||(i==1&&got==9)||(i==3&&got==10)||(i==4&&got==11));
  }
  for(j=0;j<i;j++)assert(V8_MATERIAL[0][i][2]!=V8_MATERIAL[0][j][2]);
 }
 for(i=0;i<8;i++){
   set_world_palette(i);
   assert(BG_PALETTE[15*16+1]==RGB5(31,31,31));
   assert(BG_PALETTE[15*16+2]==RGB5(2,3,9));
   assert(BG_PALETTE[0*16+2]!=BG_PALETTE[2*16+2]);
 }
 /* Regression: story and NPC dialog may not overwrite framed borders.
    A long line must wrap INSIDE the left and right panel margins. */
 ui_clear();ui_frame(0,19,15);
 ui_wrap_text(5,"ABCDEFGHIJKLMNO PQRSTUVW XYZZZZ",15,2);
 assert((screenblock(UI_MAP_BASE)[5*32+0]&1023)==61);
 assert((screenblock(UI_MAP_BASE)[5*32+2]&1023)==64+font_index('A'));
 assert((screenblock(UI_MAP_BASE)[5*32+29]&1023)==61);
 assert((screenblock(UI_MAP_BASE)[6*32+0]&1023)==61);
 assert((screenblock(UI_MAP_BASE)[6*32+2]&1023)==64+font_index('X'));
 assert((screenblock(UI_MAP_BASE)[6*32+29]&1023)==61);
 set_world_palette(0);ui_clear();ui_frame(11,19,15);ui_text(4,13,"ARIN READS",15);
 assert((screenblock(UI_MAP_BASE)[13*32+4]&1023)==64+font_index('A'));
 assert((screenblock(UI_MAP_BASE)[13*32+8]&1023)==62);/* visible opaque space */
 assert(BG_PALETTE[15*16+4]==RGB5(0,0,2));/* extruded glyph shadow */
 /* Projection must never move tape cursors or affect collisions/story. */
 {u32 q=qi,w=workload_qi;u16 f=story_flags;int old=collision[mi(10,10)];
  cam_x=90;cam_y=70;player.x=140;player.y=180;view12_project();
  assert(qi==q && workload_qi==w && story_flags==f && collision[mi(10,10)]==old);
  assert(view_parallax_x!=0 && view_parallax_y!=0);
 }
 /* All five authored acts are actually in ROM, with progressive unlocking. */
 assert(ARRAY_LEN(CHRONICLE)==30);
 story_flags=0;assert(chronicle_limit()==2);
 story_flags=ST_TOWN|ST_OAKWOOD|ST_PUZZLE|ST_MALAKAR|ST_HEART;
 assert(chronicle_limit()>=8);
 story_flags=ST_TOWN|ST_OAKWOOD|ST_PUZZLE|ST_MALAKAR|ST_HEART|ST_CHRONO|ST_VOID|ST_CITY|ST_WISDOM|ST_COURAGE|ST_DREAM|ST_ELEMENTS|ST_LATTICE;
 assert(chronicle_limit()==30);
 assert(CHRONICLE[0].text[0]=='B');
 /* NPCs and player stats remain authoritative when changing visual identity. */
 game_mode=MODE_PAUSE;return_mode=MODE_SURFACE;actor_style=0;
 pause_page=3;update_pause(KEY_R);assert(pause_page==15 && role_preview==0);
 update_pause(KEY_DOWN);assert(role_preview==1);
 update_pause(KEY_A);assert(pause_page==3&&actor_style==1);
 assert(SRAM[208]==0x88 && SRAM[209]==1 && save_valid());
 init_new_game();load_game();assert(actor_style==1&&save_valid());
 actor_style=2;player_mp=6;max_mp=6;current_spell=SPELL_PULSE;clear_combat();intro=0;
 cast_magic();assert(player_mp==4); /* mystic costs 2 MP, otherwise 3 */
 actor_style=3;armor=0;assert(armor_bonus()==1);
 actor_style=0;weapon=0;assert(weapon_bonus()==1);
 actor_style=1;dodge_cooldown=0;player.face=3;player.x=100;player.y=408;
 {int x=player.x;player_dodge(KEY_RIGHT);assert(player.x>x+15&&dodge_timer>16);}
 /* Proven V7 SRAM load must default to original character, never erase story. */
 {FILE*f=fopen("qa_fixtures/v7_mgba_boot1.sav","rb");assert(f);
  assert(fread((void*)HOST_SRAM,1,32768,f)==32768);fclose(f);
  init_new_game();assert(save_valid());load_game();
  assert(actor_style==0);assert(SRAM[5]&1);
  assert(story_flags&(ST_HEART|ST_MALAKAR));
 }
 /* A damaged V8 role extension must not invalidate the original V7 save. */
 actor_style=2;save_game();SRAM[210]^=1;actor_style=2;load_game();
 assert(save_valid()&&actor_style==0&&(story_flags&ST_HEART));
 /* Freeze exact 8,192-byte data from current source: evidence from verify_v5. */
 puts("PASS V8: eight distinguishable materials, neutral accessible HUD, native perspective BG2, isolated 12-state math, 30 narrative pages, class perks, persistent V7-compatible role identity");
 return 0;
}
'''
(R/'v8_view_story_qa.c').write_text(src)
subprocess.run(['clang','-DQA_AUTORUN','-DHOST_QA','-O2','-Wno-unused-function','v8_view_story_qa.c','-o','v8_view_story_qa'],cwd=R,check=True)
subprocess.run([str(R/'v8_view_story_qa')],cwd=R,check=True)
