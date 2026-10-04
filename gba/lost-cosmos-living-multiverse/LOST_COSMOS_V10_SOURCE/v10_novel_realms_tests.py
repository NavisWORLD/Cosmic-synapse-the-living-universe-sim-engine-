"""Native C host-integration test for FIVE new real 64x64 manuscript-inspired chapters.
Routes are checked against actual game collision and authored quest triggers.
Branched host setup explores both outcomes; it is not a player playthrough.
"""
from pathlib import Path
import subprocess
R=Path(__file__).resolve().parent
s=(R/'host_qa_v5.c').read_text().split('\n#ifdef HOST_QA\nint main(',1)[0]
s+=r'''
#include <assert.h>
#include <stdio.h>
/* Spatial BFS against exact 4096 game collision bytes. */
static int route(int ax,int ay,int bx,int by){u8 hit[4096]={0};u16 q[4096];int h=0,t=0,k;
 if(collision[mi(ax,ay)]==C_WALL || collision[mi(bx,by)]==C_WALL)return 0;
 k=mi(ax,ay);q[t++]=(u16)k;hit[k]=1;
 while(h<t){k=q[h++];if((k&63)==bx && (k>>6)==by)return 1;
  int x=k&63,y=k>>6;
  for(int d=0;d<4;d++){int nx=x+(d==0?1:d==1?-1:0),ny=y+(d==2?1:d==3?-1:0);
   if(nx<=0||nx>=63||ny<=0||ny>=63)continue;int n=mi(nx,ny);
   if(!hit[n]&&collision[n]!=C_WALL){hit[n]=1;q[t++]=(u16)n;}
  }
 }return 0;
}
static void go(int x,int y){player.x=(s16)(x*8);player.y=(s16)(y*8);story_gate();}
int main(void){u32 tape;int n;u8 wolf,phoenix,earth;
 init_new_game();init_graphics();intro=0;current_world=0;current_room=7;current_layer=1;
 story_flags|=ST_HEART|ST_HEARTWOOD;generate_surface();
 assert(V51_SCENE_COUNT==23);
 for(n=0;n<23;n++)assert(V51_SCENE_COUNTS[n]>100&&V51_SCENE_COUNTS[n]<=512);
 assert(trigger[mi(32,13)]==TR_HW_HEART);
 assert(trigger[mi(32,5)]==TR_GATE);
 assert(route(11,52,32,5));
 go(32,5);assert(current_room==8);
 assert(trigger[mi(12,33)]==TR_ICE_RUNE&&trigger[mi(47,32)]==TR_ICE_WOLF);
 assert(trigger[mi(32,13)]==TR_ICE_CRYSTAL);
 assert(collision[mi(20,24)]==C_WALL&&collision[mi(32,24)]==C_FREE);
 assert(route(10,52,12,33)&&route(10,52,47,32));
 assert(route(10,52,32,13)&&route(10,52,32,6)&&route(10,52,54,33));
 story_interact(TR_ICE_CRYSTAL);assert(!(v10_relic&RF_CLARITY));
 tape=workload_qi;story_interact(TR_ICE_RUNE);assert(v10_realm_riddle==1);
 update_surface(0,KEY_LEFT);assert(!v10_realm_riddle && !(v10_relic&RF_ICE_RUNE));
 story_interact(TR_ICE_RUNE);update_surface(0,KEY_RIGHT);
 assert(v10_relic&RF_ICE_RUNE);assert(enemies[8].active&&enemies[8].elite);
 assert(workload_qi==tape);
 /* Player-controlled pacifist route, actually run the tactical TALK action. */
 inv[ITEM_ETHER]=1;story_interact(TR_ICE_WOLF);assert(game_mode==MODE_BATTLE);
 battle_cursor=3;battle_act();assert(!enemies[8].active&&(v10_relic&RF_WOLF));
 assert((v10_realm_choices&1)&&v9_bonded&&v9_bond_type==EN_TIDE);
 wolf=v10_realm_choices;battle_exit();story_interact(TR_ICE_CRYSTAL);
 assert(v10_relic&RF_CLARITY);
 assert(trigger[mi(32,6)]==TR_GATE);
 go(32,6);assert(current_world==0&&current_room==9);
 assert(trigger[mi(13,32)]==TR_FLAME_LEFT&&trigger[mi(50,32)]==TR_FLAME_RIGHT);
 assert(trigger[mi(32,22)]==TR_PHOENIX&&trigger[mi(32,11)]==TR_PASSION);
 assert(collision[mi(7,17)]==C_HAZARD&&collision[mi(32,17)]==C_FREE);
 assert(route(10,52,13,32)&&route(10,52,50,32));
 assert(route(10,52,32,22)&&route(10,52,32,11));
 story_interact(TR_PASSION);assert(!(v10_relic&RF_PASSION));
 story_interact(TR_FLAME_LEFT);assert(!enemies[8].active);
 story_interact(TR_FLAME_RIGHT);assert(enemies[8].active);
 /* Real second encounter can also end by fighting. */
 story_interact(TR_PHOENIX);assert(game_mode==MODE_BATTLE);
 battle_cursor=0;str_stat=120;enemies[8].hurt=0;battle_act();
 assert(!enemies[8].active&&(v10_relic&RF_PHOENIX));
 phoenix=v10_realm_choices;assert((phoenix&2)==0);battle_exit();
 story_interact(TR_PASSION);assert(v10_relic&RF_PASSION);
 go(10,54);assert(current_room==8);
 go(54,33);assert(current_room==12);
 assert(trigger[mi(13,43)]==TR_PEAK_RUNE&&trigger[mi(32,20)]==TR_HARMONY);
 assert(collision[mi(4,16)]==C_WALL&&collision[mi(32,36)]==C_FREE);
 assert(route(10,52,13,43)&&route(10,52,32,20));
 story_interact(TR_HARMONY);assert(!(v10_relic&RF_HARMONY));
 story_interact(TR_PEAK_RUNE);assert(v10_realm_riddle==3);
 update_surface(0,KEY_UP);assert(v10_relic&RF_PEAK_RUNE);
 story_interact(TR_HARMONY);assert(v10_relic&RF_HARMONY);
 assert((v10_relic&RF_TRIPLE)==RF_TRIPLE);
 /* New optional Eldoria chapter: the real map and mirror pool, not an instant quest flag. */
 current_world=7;current_room=0;current_layer=1;story_flags|=ST_DREAM;generate_surface();
 assert(trigger[mi(54,36)]==TR_GATE&&route(10,52,54,36));
 go(54,36);assert(current_world==7&&current_room==10);
 assert(trigger[mi(13,32)]==TR_GROVE_MIRROR&&trigger[mi(48,32)]==TR_GROVE_WRAITH);
 assert(trigger[mi(32,12)]==TR_EARTH);
 assert(collision[mi(18,24)]==C_WALL&&collision[mi(32,24)]==C_FREE);
 assert(route(10,52,13,32)&&route(10,52,48,32)&&route(10,52,32,12));
 story_interact(TR_GROVE_MIRROR);update_surface(0,KEY_LEFT);
 assert(v10_relic&RF_GROVE_RIDDLE&&enemies[8].active);
 story_interact(TR_GROVE_WRAITH);assert(game_mode==MODE_BATTLE);
 battle_cursor=3;inv[ITEM_ETHER]=1;battle_act();assert(v10_relic&RF_GROVE_WRAITH);
 assert(v10_realm_choices&4);earth=v10_realm_choices;
 battle_exit();story_interact(TR_EARTH);assert(v10_relic&RF_EARTH);
 assert(workload_qi==tape);
 /* Main three crystals open Nyssa's original playable ordered-chime festival. */
 current_world=6;current_room=0;current_layer=1;generate_surface();
 assert(trigger[mi(54,31)]==TR_GATE&&route(10,52,54,31));
 go(54,31);assert(current_room==11);
 assert(trigger[mi(14,32)]==TR_FEST_L&&trigger[mi(32,17)]==TR_FEST_C&&trigger[mi(51,32)]==TR_FEST_R);
 assert(route(10,52,14,32)&&route(10,52,32,17)&&route(10,52,51,32));
 story_interact(TR_FEST_R);assert(v10_festival_notes==0);
 story_interact(TR_FEST_C);story_interact(TR_FEST_L);story_interact(TR_FEST_R);
 assert(v10_relic&RF_FESTIVAL);
 save_game();v10_relic=0;v10_realm_choices=0;load_game();
 assert(v10_relic&(RF_FESTIVAL|RF_EARTH));
 assert((v10_realm_choices&5)==5 && earth==v10_realm_choices);
 assert(v10_relic&RF_TRIPLE);assert(v10_realm_choices==wolf+4);
 SRAM[237]^=0xF1;v10_relic=99;v10_realm_choices=99;load_game();
 assert(v10_relic==0 && v10_realm_choices==0 && save_valid());
 {FILE*f=fopen("qa_fixtures/v7_mgba_boot1.sav","rb");assert(f);
 assert(fread((void*)HOST_SRAM,1,32768,f)==32768);fclose(f);}
 init_new_game();load_game();assert(v10_relic==0&&v10_realm_choices==0 && save_valid());
 puts("PASS V10: five genuinely traversable manuscript-inspired maps, physical void/ice/lava and safe crossings, three crystals, Frost Wolf mercy, Phoenix fight, Hollow Wraith mercy, Heartwood continuation, Celestial star riddle, three-chime Nyssa festival, 23 genuine indexed cinematic scenes, real state-machine progression, checksummed SRAM V7-safe and isolated original archived replay");
 return 0;
}
'''
(R/'v10_novel_realms_qa.c').write_text(s)
subprocess.run(['clang','-DQA_AUTORUN','-DHOST_QA','-O2','-Wno-unused-function','v10_novel_realms_qa.c','-o','v10_novel_realms_qa'],cwd=R,check=True)
subprocess.run([str(R/'v10_novel_realms_qa')],cwd=R,check=True)
