"""Actual CURRENT ERL7 native C + simulated memory-mapped host, never emulator footage.
Simulates real GBA control transition functions, real on-map collision, source fights,
all 12 long-game scene chains, 4 earned sigils, 3 pillar victories, 5 genuine
story-gated Orbs, all 3 old endings and byte-identical old 6 SRAM pages.
"""
from pathlib import Path
import subprocess
r=Path(__file__).resolve().parents[1]
g=r/'LOST_COSMOS_V10_SOURCE'
subprocess.run(['python3','host_qa_v5.py'],cwd=g,check=True,capture_output=True,timeout=40)
pre=(g/'host_qa_v5.c').read_text().split('\n#ifdef HOST_QA\nint main(',1)[0]
program=r'''
#include <assert.h>
#include <stdio.h>
#include <string.h>
static int route(int ax,int ay,int bx,int by){
 u8 seen[4096]={0};u16 q[4096];int h=0,t=0,k;
 if(collision[mi(ax,ay)]!=C_FREE||collision[mi(bx,by)]!=C_FREE)return 0;
 k=mi(ax,ay);seen[k]=1;q[t++]=(u16)k;
 while(h<t){int x,y;k=q[h++];x=k&63;y=k>>6;
  if(x==bx&&y==by)return 1;
  for(int d=0;d<4;d++){
   int nx=x+(d==0?1:d==1?-1:0),ny=y+(d==2?1:d==3?-1:0);
   if(nx<=0||nx>=63||ny<=0||ny>=63)continue;
   int n=mi(nx,ny);if(!seen[n]&&collision[n]==C_FREE){seen[n]=1;q[t++]=(u16)n;}
  }
 }return 0;
}
static unsigned long map_sig(void){unsigned long h=2166136261u;
 for(int y=3;y<59;y++)for(int x=3;x<59;x++)
  h=(h^(unsigned long)(collision[mi(x,y)]+7*map_read_tile(x,y)))*16777619u;
 return h;
}
static void map_test(int idx,unsigned long *hashes){
 int targets[][2]={{13,32},{31,15},{18,42},{46,42},
    {51,32},{31,27},{31,54},{48,18}};
 int triggers[]={TR_G7_OATH,TR_G7_CHOICE,TR_G7_NODE_A,TR_G7_NODE_B,
   TR_G7_PROOF,TR_G7_CACHE,TR_G7_EXIT,TR_G7_NEXT};
 current_room=(u8)(G7_FIRST_ROOM+idx);current_world=0;current_layer=1;
 generate_surface();
 for(int j=0;j<8;j++){
  int x=targets[j][0],y=targets[j][1];
  if(trigger[mi(x,y)]!=triggers[j]){fprintf(stderr,"IDX %d TARGET %d HAD %u WANT %d\n",idx,j,trigger[mi(x,y)],triggers[j]);abort();}
  assert(route(31,52,x,y));
 }
 if(idx==9)for(int j=0;j<4;j++){
  assert(trigger[mi(13+j*12,20)]==TR_G7_SIGIL_FIRST+j);
  assert(route(31,52,13+j*12,20));
 }
 if(idx==10){assert(trigger[mi(31,20)]==TR_G7_PILLAR);assert(route(31,52,31,20));}
 if(idx==11)for(int j=0;j<5;j++){
  assert(trigger[mi(11+j*10,20)]==TR_G7_ORB_FIRST+j);
  assert(route(31,52,11+j*10,20));
 }
 hashes[idx]=map_sig();for(int j=0;j<idx;j++)assert(hashes[idx]!=hashes[j]);
}
static void earn_fixture(void){
 /* Only development QA: the real game checks individually earned source flags. */
 arc_progress=ARC_STAGES;arc_route=2;arc_petals=3;arc_anchors=3;
 story_flags|=ST_HEART|ST_CITY|ST_COURAGE|ST_WISDOM|ST_DREAM|
   ST_ELEMENTS|ST_CHRONO|ST_VOID|ST_LATTICE;
 v10_relic|=RF_HARMONY|RF_PASSION|RF_GROVE_WRAITH|RF_EARTH|RF_FESTIVAL;
 p4_material[2]=1;postgame=1;ending=1;
 save_game();
}
static void genuine_enemy_victory(void){int before=kill_count;
 /* Feed genuine source battle input, NOT direct kill_count manipulation. */
 spawn_enemy(0,44,36,EN_VOID,0);enemies[0].hp=1;enemies[0].hurt=0;
 assert(enemies[0].active);battle_enter(0);assert(game_mode==MODE_BATTLE);
 str_stat=200;battle_cursor=0;battle_act();
 assert(!enemies[0].active&&kill_count==before+1);
 battle_exit();str_stat=2;
}
static void whole_story_chain(int ending_choice){
 unsigned long sig[G7_COUNT]={0};
 init_new_game();init_graphics();intro=0;game_mode=MODE_SURFACE;
 /* First check that the physically constructed door cannot bypass its parent. */
 arc_progress=G7_PARENT[0];current_room=(u8)(ARC_FIRST_ROOM+G7_PARENT[0]);
 generate_surface();assert(trigger[mi(12,33)]==TR_G7_PORTAL);
 assert(trigger[mi(22,32)]==TR_G5_OATH); /* Critical regression: do not erase G5. */
 assert(route(31,52,12,33));story_interact(TR_G7_PORTAL);
 assert(current_room==ARC_FIRST_ROOM+G7_PARENT[0]);
 earn_fixture();ending=(u8)ending_choice;save_game();
 for(int i=0;i<G7_COUNT;i++){
  g7_warp(i);assert(current_room==G7_FIRST_ROOM+i);
  map_test(i,sig);
  story_interact(TR_G7_PROOF);assert(!g7_step[i]);
  story_interact(TR_G7_CHOICE);assert(!g7_pending);
  int cache=inv[ITEM_SHARD];story_interact(TR_G7_CACHE);
  assert(inv[ITEM_SHARD]==cache+2);
  cache=inv[ITEM_SHARD];story_interact(TR_G7_CACHE);
  assert(inv[ITEM_SHARD]==cache); /* repeat-safe real shard pickup */
  story_interact(TR_G7_OATH);assert(g7_step[i]==1);
  story_interact(TR_G7_CHOICE);assert(g7_pending);
  if(!i){g7_answer(KEY_B);assert(!g7_pending&&!g7_choice[i]);
    story_interact(TR_G7_CHOICE);}
  g7_answer(ending_choice==1?KEY_LEFT:ending_choice==2?KEY_UP:KEY_RIGHT);
  assert(g7_step[i]==2&&g7_choice[i]==ending_choice);
  int first=(i&1)?1:0;
  story_interact((u8)(TR_G7_NODE_A+1-first));assert(!g7_nodes[i]);
  story_interact((u8)(TR_G7_NODE_A+first));assert(g7_nodes[i]==(1u<<first));
  if(i==6){p4_material[2]=0;
   story_interact((u8)(TR_G7_NODE_A+1-first));
   assert(g7_nodes[i]==(1u<<first));p4_material[2]=1;
  }
  if(i==5){
    /* Restore in the MIDST of an actual entered/partly solved new room. */
    save_game();int old[6][252];
    int off[]={0,LC_ROSTER_SRAM,ARC_SRAM,P4_SRAM,G5_SRAM,G6_SRAM};
    int sizes[]={238,252,32,32,32,32};
    for(int p=0;p<6;p++)for(int j=0;j<sizes[p];j++)old[p][j]=SRAM[off[p]+j];
    init_new_game();load_game();
    assert(current_room==G7_FIRST_ROOM+i&&g7_step[i]==2);
    assert(g7_nodes[i]==(1u<<first));
    for(int p=0;p<6;p++)for(int j=0;j<sizes[p];j++)assert(old[p][j]==SRAM[off[p]+j]);
    generate_surface();
  }
  story_interact((u8)(TR_G7_NODE_A+1-first));assert(g7_nodes[i]==3);
  int before=credits;
  if(i==9){
    story_interact(TR_G7_PROOF);assert(credits==before&&g7_step[i]==2);
    story_interact(TR_G7_SIGIL_FIRST+1);assert(!g7_sigils);
    for(int j=0;j<4;j++){
     story_interact(TR_G7_SIGIL_FIRST+j);
     assert(g7_sigils==((1u<<(j+1))-1));
    }
  }
  if(i==10){
   story_interact(TR_G7_PROOF);assert(g7_step[i]==2);
   story_interact(TR_G7_PILLAR);assert(g7_pillars==1);
   save_game();g7_reset();g7_restore();assert(g7_pillars==1);
   for(int j=1;j<=2;j++){
     story_interact(TR_G7_PILLAR);assert(g7_pillars==j);
     genuine_enemy_victory();
     story_interact(TR_G7_PILLAR);assert(g7_pillars==j+1);
   }
  }
  if(i==11){
    story_interact(TR_G7_PROOF);assert(g7_step[i]==2);
    story_interact(TR_G7_ORB_FIRST+1);assert(!g7_orbs);
    for(int j=0;j<5;j++){
      story_interact(TR_G7_ORB_FIRST+j);
      assert(g7_orbs==((1u<<(j+1))-1));
    }
  }
  before=credits;
  story_interact(TR_G7_PROOF);
  assert(g7_step[i]==3&&(g7_done&(1u<<i))&&credits>before);
  if(i==11)assert(strstr(dialogue,ending_choice==1?"OPEN":ending_choice==2?"PRESERVE":"WANDER")!=NULL);
  int afterxp=player_xp,aftershard=inv[ITEM_SHARD];
  story_interact(TR_G7_PROOF);
  assert(player_xp==afterxp&&inv[ITEM_SHARD]==aftershard);
  save_game();init_new_game();load_game();
  assert(g7_done&(1u<<i));assert(g7_step[i]==3);
  assert(g7_choice[i]==ending_choice&&ending==ending_choice);
  current_room=(u8)(G7_FIRST_ROOM+i);generate_surface();
  if(i+1<G7_COUNT){
    story_interact(TR_G7_NEXT);
    assert(current_room==G7_FIRST_ROOM+i+1);
  }else{
    story_interact(TR_G7_EXIT);
    assert(current_room==ARC_FIRST_ROOM+G7_PARENT[i]);
  }
 }
 assert(g7_done==4095);
 assert(g7_sigils==15&&g7_pillars==3&&g7_orbs==31);
 assert(g7_attack_bonus()==(ending_choice==2?4:0));
 assert(g7_guard_bonus()==(ending_choice==1?4:0));
 printf("PASS 12 unique native 64x64 maps x 8 real reachable controls x three real player-choosable routes; 4 earned sigils, 3 genuine-source battle-gated pillars, 5 prior-milestone-gated Orbs; full source-derived save/load and original ending %d preserved\n",ending_choice);
}
static void journal_and_sram_tamper(void){
 init_new_game();init_graphics();intro=0;game_mode=MODE_SURFACE;
 current_room=2;arc_progress=16;generate_surface();
 enter_pause();pause_page=13;
 update_pause(KEY_DOWN);assert(pause_page==24&&g7_journal_sel==0);
 update_pause(KEY_DOWN);assert(g7_journal_sel==1);
 update_pause(KEY_R);assert(current_room==2); /* prior g7[0] missing */
 update_pause(KEY_UP);assert(g7_journal_sel==0);
 update_pause(KEY_R);assert(current_room==G7_FIRST_ROOM);
 enter_pause();pause_page=24;update_pause(KEY_B);assert(pause_page==13);
 earn_fixture();g7_warp(0);g7_step[0]=2;g7_choice[0]=1;g7_nodes[0]=1;
 save_game();
 int off[]={0,LC_ROSTER_SRAM,ARC_SRAM,P4_SRAM,G5_SRAM,G6_SRAM};
 int sizes[]={238,252,32,32,32,32};
 u8 old[6][252];for(int p=0;p<6;p++)for(int j=0;j<sizes[p];j++)old[p][j]=SRAM[off[p]+j];
 u8 page[64];for(int j=0;j<64;j++)page[j]=SRAM[G7_SRAM+j];
 memset((void*)(HOST_SRAM+G7_SRAM),0,64);g7_restore();
 assert(!g7_done&&!g7_step[0]&&current_room==2);
 for(int p=0;p<6;p++)for(int j=0;j<sizes[p];j++)assert(old[p][j]==SRAM[off[p]+j]);
 memcpy((void*)(HOST_SRAM+G7_SRAM),page,64);
 SRAM[G7_SRAM+33]=2; /* wrong-order node with mathematically valid CRC */
 u8 f[64];for(int j=0;j<64;j++)f[j]=SRAM[G7_SRAM+j];
 u32 crc=lc_crc32(f,60);for(int j=0;j<4;j++)SRAM[G7_SRAM+60+j]=(u8)(crc>>(8*j));
 g7_restore();assert(!g7_done&&!g7_step[0]);
 for(int p=0;p<6;p++)for(int j=0;j<sizes[p];j++)assert(old[p][j]==SRAM[off[p]+j]);
 /* Direct CRC-valid future chapter spoofing: cannot skip 10 chapters. */
 memcpy((void*)(HOST_SRAM+G7_SRAM),page,64);
 SRAM[G7_SRAM+9+11]=3;SRAM[G7_SRAM+21+11]=1;
 SRAM[G7_SRAM+33+11]=3;SRAM[G7_SRAM+5]=0x00;
 SRAM[G7_SRAM+6]=0x08;
 for(int j=0;j<64;j++)f[j]=SRAM[G7_SRAM+j];
 crc=lc_crc32(f,60);for(int j=0;j<4;j++)SRAM[G7_SRAM+60+j]=(u8)(crc>>(8*j));
 g7_restore();assert(!g7_done&&!g7_step[11]);
 for(int p=0;p<6;p++)for(int j=0;j<sizes[p];j++)assert(old[p][j]==SRAM[off[p]+j]);
 puts("PASS native START/ERIDORIA/DOWN chapter controls, old unlocked-map prerequisite, separate GSC7 CRC32 missing/forged/wrong-order/future-source rejection and byte-preserved SIX older SRAM ranges");
}
int main(void){
 for(int choice=1;choice<=3;choice++)whole_story_chain(choice);
 journal_and_sram_tamper();
 puts("PASS actual current source V10.7 Living Book host acceptance (NOT mGBA gameplay capture)");
 return 0;
}
'''
(g/'living_book_v107_native_host_qa.c').write_text(pre+'\n'+program)
subprocess.run(['clang','-DHOST_QA','-DQA_AUTORUN','-O1','-g','-Wno-unused-function','living_book_v107_native_host_qa.c','-o','living_book_v107_native_host_qa'],cwd=g,check=True,timeout=50)
subprocess.run([str(g/'living_book_v107_native_host_qa')],cwd=g,check=True,timeout=65)
