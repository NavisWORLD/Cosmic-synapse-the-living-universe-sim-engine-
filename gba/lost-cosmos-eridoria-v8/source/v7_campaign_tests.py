"""Native-equivalent host tests for authored Eridoria areas and eight-world campaign.
Runs actual C engine logic with isolated GBA register/VRAM/SRAM mocks from host_qa_v5.py.
"""
from pathlib import Path
import subprocess
root=Path(__file__).parent
host=(root/'host_qa_v5.c').read_text().split('\n#ifdef HOST_QA\nint main(',1)[0]
assert '#define ST_HEART' in host
host += r'''
#include <assert.h>
#include <stdio.h>
/* Reachability on real collision[] from each spawn, accepting trigger adjacency.
   4KB queue? 4096 grid nodes with fixed 8192-byte stack is safe on host. */
static int reaches(int sx,int sy,int tx,int ty){
 static u8 seen[4096];static u16 queue[4096];int head=0,tail=0,x,y,k;
 for(k=0;k<4096;k++)seen[k]=0;
 if(collision[mi(sx,sy)]==C_WALL)return 0;
 k=mi(sx,sy);queue[tail++]=(u16)k;seen[k]=1;
 while(head<tail){int pos=queue[head++];x=pos%64;y=pos/64;
  if(iabs(x-tx)+iabs(y-ty)<=1)return 1;
  {static const int dd[4][2]={{0,1},{0,-1},{1,0},{-1,0}};int i;
   for(i=0;i<4;i++){int nx=x+dd[i][0],ny=y+dd[i][1];
     if(nx>0&&nx<63&&ny>0&&ny<63&&(k=mi(nx,ny))>=0&&!seen[k]&&collision[k]!=C_WALL){seen[k]=1;queue[tail++]=(u16)k;}
   }
  }
 }return 0;
}
static void region(int w,int room,int spawnx,int spawny){current_world=w;current_room=room;current_layer=1;generate_surface();
 assert(reaches(spawnx,spawny,spawnx,spawny));}
int main(void){int i;
 init_new_game();init_graphics();sound_init();region(0,0,10,51);
 assert(reaches(10,51,20,48));
 player.x=20*8;player.y=48*8;story_gate();assert(current_room==2);
 assert(reaches(11,52,26,31)&&reaches(11,52,54,8));
 region(0,3,11,52);assert(reaches(11,52,19,39)&&reaches(11,52,30,17)&&reaches(11,52,54,12));
 /* Player cannot walk into the temple before talking to the lord. */
 story_flags=0;player.x=54*8;player.y=12*8;story_gate();assert(current_room==3);
 story_flags|=ST_OAKWOOD;story_gate();assert(current_room==4);
 assert(reaches(31,52,21,22)&&reaches(31,52,28,22)&&reaches(31,52,35,22)&&reaches(31,52,42,22)&&reaches(31,52,32,9));
 rune_touch(1);assert(rune_progress==0);rune_touch(2);rune_touch(0);rune_touch(3);rune_touch(1);
 assert((story_flags&ST_PUZZLE)&&enemies[8].active);
 {u32 before=workload_qi;enemies[8].hp=1;battle_enter(8);intro=0;assert(game_mode==MODE_BATTLE);
  render();assert(((OAM16[2*4+1]>>14)&3)==2);assert((OAM16[2*4+2]&1023)==256);
  battle_cursor=0;player_level=12;str_stat=25;battle_act();assert((story_flags&ST_MALAKAR)&&workload_qi==before);
  battle_timer=0;update_battle(0);assert(game_mode==MODE_SURFACE);
 }
 story_interact(TR_HEART);assert(story_flags&ST_HEART);
 /* Spot check the live market: buy and sell, bounded counters, SRAM persistence. */
 region(0,3,11,52);credits=12;inv[ITEM_SHARD]=1;shop_sel=0;shop_trade();assert(credits==7&&inv[ITEM_POTION]==3);
 shop_sel=1;shop_trade();assert(credits==0&&inv[ITEM_ETHER]==2);
 shop_sel=2;shop_trade();assert(credits==3&&!inv[ITEM_SHARD]);
 save_game();assert(save_valid());assert(SRAM[206]==0x73&&SRAM[207]==(u8)(0xB9+SRAM[200]+SRAM[201]+SRAM[202]+SRAM[203]+SRAM[204]+SRAM[205]));
 story_flags=0;load_game();assert((story_flags&(ST_PUZZLE|ST_MALAKAR|ST_HEART))==(ST_PUZZLE|ST_MALAKAR|ST_HEART));
 /* A corrupt extension cannot invalidate or destroy the legacy base save. */
 SRAM[207]^=1;story_flags=0;load_game();assert(save_valid()&&story_flags==0);
 story_flags=ST_HEART;
 region(0,5,10,52);assert(reaches(10,52,31,17)&&reaches(10,52,54,10));
 region(6,0,10,53);assert(reaches(10,53,15,17)&&reaches(10,53,31,15)&&reaches(10,53,49,17));
 story_interact(TR_WISDOM);assert(riddle_open&&!(story_flags&ST_WISDOM));
 update_surface(KEY_LEFT,KEY_LEFT);assert(!riddle_open&&!(story_flags&ST_WISDOM));
 story_interact(TR_WISDOM);update_surface(KEY_RIGHT,KEY_RIGHT);assert(story_flags&ST_WISDOM);
 for(i=0;i<10;i++)if(enemies[i].active&&enemies[i].elite){enemies[i].hp=1;damage_enemy(&enemies[i],40);break;}
 assert(story_flags&ST_COURAGE);story_interact(TR_UNITY);assert(story_flags&ST_DREAM);
 region(7,0,10,53);
 assert(reaches(10,53,15,17)&&reaches(10,53,26,17)&&reaches(10,53,37,17)&&reaches(10,53,48,17));
 {int shrine[]={15,26,37,48};for(i=0;i<4;i++){
   player.x=(s16)(shrine[i]*8);
   if(i==3){int k;story_interact(TR_ELEMENT);assert(!(element_mask&8));
     for(k=0;k<10;k++)if(enemies[k].active&&enemies[k].elite){enemies[k].hp=1;damage_enemy(&enemies[k],50);break;}}
   story_interact(TR_ELEMENT);
  }assert(element_mask==15&&(story_flags&ST_ELEMENTS));
 }
 /* Original six worlds remain intact and story extension supports all 8 bits. */
 region(2,0,10,52);keys_found=7;story_interact(TR_CHRONO);assert(story_flags&ST_CHRONO);
 region(4,0,11,52);story_interact(TR_VOID_SIGIL);assert(story_flags&ST_VOID);
 assert((story_flags&ST_ALL)==ST_ALL);
 region(5,0,8,54);for(i=0;i<10;i++)if(enemies[i].active&&enemies[i].elite){enemies[i].hp=1;damage_enemy(&enemies[i],50);break;}
 assert(story_flags&ST_LATTICE);save_game();assert((SRAM[200]&ST_HEART)!=0);
 /* All populated story encounters track independently beyond the old 16-bit NPC log. */
 region(0,5,10,52);for(i=0;i<npc_count;i++)if(npc_runtime[i].id==18)npc_speak(i);
 assert(npc_seen&(1u<<18));save_game();npc_seen=0;load_game();assert(npc_seen&(1u<<18));
 puts("PASS V7 native C: map reachability, 4 connected Eridoria areas, 8 worlds, Malakar 32px duel, trading, puzzles, 5-act campaign flags, legacy save isolation and NPC persistence");
 return 0;
}
'''
(root/'v7_campaign_host.c').write_text(host)
subprocess.run(['clang','-DQA_AUTORUN','-DHOST_QA','-O2','-Wno-unused-function','v7_campaign_host.c','-o','v7_campaign_host'],cwd=root,check=True)
subprocess.run([str(root/'v7_campaign_host')],cwd=root,check=True)
