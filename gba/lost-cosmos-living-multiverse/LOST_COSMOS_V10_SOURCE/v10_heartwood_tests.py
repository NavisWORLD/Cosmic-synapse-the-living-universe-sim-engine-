"""New authored Heartwood area/trial host integration against native C game engine.
Exact source location: user's original 'In the land of Eridoria.pdf' pp. 20-23.
The map and battle run through real engine functions; this isn't an emulated
GBA controller run or a replacement for manual Delta testing.
"""
from pathlib import Path
import subprocess
R=Path(__file__).parent
src=(R/'host_qa_v5.c').read_text().split('\n#ifdef HOST_QA\nint main(',1)[0]
src+=r'''
#include <assert.h>
#include <stdio.h>
/* BFS on the actual 4096-tile GBA collision world, NEVER jumping quest flags. */
static int has_route(int sx,int sy,int tx,int ty){static u8 seen[4096];
 static u16 q[4096];int h=0,t=0,x,y,k,steps[4]={1,-1,64,-64};
 for(k=0;k<4096;k++)seen[k]=0;
 k=mi(sx,sy);q[t++]=(u16)k;seen[k]=1;
 while(h<t){k=q[h++];x=k&63;y=k>>6;
  if(x==tx&&y==ty)return 1;
  for(int d=0;d<4;d++){int nx=x+(d==0?1:(d==1?-1:0)),ny=y+(d==2?1:(d==3?-1:0));
   if(nx<1||nx>=63||ny<1||ny>=63)continue;
   int n=mi(nx,ny);
   if(!seen[n]&&collision[n]!=C_WALL){seen[n]=1;q[t++]=(u16)n;}
  }
 }
 return 0;
}
int main(void){u32 original_q;int i,spirit=0;
 init_new_game();init_graphics();intro=0;
 current_world=0;current_room=2;current_layer=1;generate_surface();
 assert(trigger[mi(55,54)]==TR_GATE);
 assert(has_route(20,43,55,54));
 player.x=55*8;player.y=54*8;story_gate();
 assert(current_room==2); /* Sacred path locked until FIRST HEART. */
 story_flags|=ST_HEART;story_gate();assert(current_room==7);
 assert(location_name()[0]=='H' && trigger[mi(10,54)]==TR_GATE);
 assert(trigger[mi(13,31)]==TR_HW_WISDOM);
 assert(trigger[mi(48,31)]==TR_HW_COURAGE);
 assert(trigger[mi(32,13)]==TR_HW_HEART);
 assert(collision[mi(18,24)]==C_WALL && collision[mi(32,24)]==C_FREE);
 assert(has_route(11,52,13,31));
 assert(has_route(11,52,48,31));
 assert(has_route(11,52,32,13));
 for(i=0;i<npc_count;i++)if(npc_runtime[i].id==24)spirit=1;
 assert(spirit);assert(!enemies[8].active);
 story_interact(TR_HW_COURAGE);assert(!(story_flags&ST_HW_COURAGE));
 story_interact(TR_HW_HEART);assert(!(story_flags&ST_HEARTWOOD));
 story_interact(TR_HW_WISDOM);assert(v10_hw_riddle);
 update_surface(0,KEY_LEFT);assert(!v10_hw_riddle&&!(story_flags&ST_HW_WISDOM));
 original_q=workload_qi;story_interact(TR_HW_WISDOM);
 update_surface(0,KEY_RIGHT);assert((story_flags&ST_HW_WISDOM)&&enemies[8].active);
 assert(workload_qi==original_q); /* Trials cannot fabricate quantum-workload data. */
 assert(enemies[8].type==EN_BLOOM&&enemies[8].elite);
 story_interact(TR_HW_COURAGE);assert(game_mode==MODE_BATTLE);
 assert(battle_index==8);
 battle_cursor=0;str_stat=60;enemies[8].hurt=0;
 battle_act();assert(!enemies[8].active);
 assert(story_flags&ST_HW_COURAGE);assert(v10_hw_choice==1);
 battle_exit();story_interact(TR_HW_HEART);assert(story_flags&ST_HEARTWOOD);
 assert(inv[ITEM_CORE]>=1);
 /* Exit and reenter; completion persists and guardian does not respawn. */
 player.x=10*8;player.y=54*8;story_gate();assert(current_room==2);
 assert(player.x==54*8); /* return at the actual southeast Brindlemark road */
 player.x=55*8;player.y=54*8;story_gate();assert(current_room==7);
 assert(!enemies[8].active && (story_flags&ST_HEARTWOOD));
 save_game();v10_hw_choice=0;story_flags=0;load_game();
 assert(v10_hw_choice==1&&(story_flags&ST_HEARTWOOD));
 /* Re-run the SAME real encounter through the nonviolent tactical TALK action.
    Resetting in host only is an integration branch test, NOT campaign play proof. */
 story_flags=ST_HEART|ST_HW_WISDOM;v10_hw_choice=0;v9_bonded=0;
 inv[ITEM_ETHER]=1;generate_surface();assert(enemies[8].active);
 story_interact(TR_HW_COURAGE);assert(game_mode==MODE_BATTLE);
 battle_cursor=3;battle_act();
 assert((story_flags&ST_HW_COURAGE) && v10_hw_choice==2);
 assert(v9_bonded&&v9_bond_type==EN_BLOOM);
 assert(inv[ITEM_ETHER]==0 && !enemies[8].active);
 battle_exit();story_interact(TR_HW_HEART);
 assert(story_flags&ST_HEARTWOOD);save_game();
 v10_hw_choice=0;story_flags=0;v9_bonded=0;load_game();
 assert((story_flags&ST_HEARTWOOD)&&v10_hw_choice==2&&v9_bonded);
 SRAM[232]^=0x11;v10_hw_choice=1;load_game();
 assert(v10_hw_choice==0&&save_valid());
 {FILE*f=fopen("qa_fixtures/v7_mgba_boot1.sav","rb");assert(f);
  assert(fread((void*)HOST_SRAM,1,32768,f)==32768);fclose(f);}
 init_new_game();load_game();assert(v10_hw_choice==0&&!(story_flags&ST_HEARTWOOD));
 printf("PASS V10 Heartwood: exact new 64x64 walkable map and genuine bridge; original novel's Balance crystal/riddle/guardian fight OR Ether-heal bond; boss rewards; 3 flags + separate checksummed choice preserved through save and V7 import; no workload mutation.\n");
 return 0;
}
'''
(R/'v10_heartwood_qa.c').write_text(src)
subprocess.run(['clang','-DQA_AUTORUN','-DHOST_QA','-O2','-Wno-unused-function','v10_heartwood_qa.c','-o','v10_heartwood_qa'],cwd=R,check=True)
subprocess.run([str(R/'v10_heartwood_qa')],cwd=R,check=True)
