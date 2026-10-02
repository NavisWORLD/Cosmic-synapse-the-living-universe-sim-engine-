"""New V10.2 actual C-host map/control/state/save integration; not emulator video."""
from pathlib import Path
import subprocess
root=Path(__file__).resolve().parents[1]
g=root/'LOST_COSMOS_V10_SOURCE'
# Regenerate host MMIO source from the CURRENT native engine, never stale prior QA.
subprocess.run(['python3','-u','host_qa_v5.py'],cwd=g,check=True,capture_output=True,timeout=35)
pre=(g/'host_qa_v5.c').read_text().split('\n#ifdef HOST_QA\nint main(',1)[0]
program=r'''
#include <assert.h>
#include <stdio.h>
#include <string.h>
static int route(int ax,int ay,int bx,int by){
 u8 seen[4096]={0};u16 q[4096];int h=0,t=0,k;
 if(collision[mi(ax,ay)]!=C_FREE || collision[mi(bx,by)]!=C_FREE)return 0;
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
static unsigned long signature(int n,int stage,int phase){unsigned long s=5381;
 for(int i=0;i<128;i++)s=((s<<5)+s)^(unsigned char)HOST_VRAM[0x10000+(384+(n-1)*24+stage*8+phase*4)*32+i];
 return s;
}
static void full_atlas(void){int idx;u8 low[238];
 init_new_game();init_graphics();intro=0;game_mode=MODE_SURFACE;
 current_world=0;current_room=2;current_layer=1;
 generate_surface();
 assert(trigger[mi(40,55)]==TR_ARC_ENTER);
 assert(collision[mi(40,55)]==C_FREE);
 assert(route(31,54,40,55));
 arc_interact(TR_ARC_ENTER); /* must not bypass real Heart of Eridoria. */
 assert(current_room==2&&arc_progress==0);
 story_flags|=ST_HEART;
 arc_interact(TR_ARC_ENTER);
 assert(current_room==13&&arc_progress==0);
 inv[ITEM_ETHER]=25;save_game();
 for(idx=0;idx<ARC_STAGES;idx++){
  int before=arc_progress,b=0;
  assert(current_world==0&&current_room==13+idx&&arc_progress==idx);
  assert(trigger[mi(31,18)]==TR_ARC_TRIAL);
  assert(trigger[mi(45,32)]==TR_ARC_REWARD);
  assert(trigger[mi(53,12)]==TR_ARC_NEXT);
  assert(trigger[mi(31,54)]==TR_ARC_EXIT);
  assert(trigger[mi(16,41)]==TR_ARC_SECRET);
  assert(route(31,52,31,18));
  assert(route(31,52,45,32));
  assert(route(31,52,53,12));
  assert(route(31,52,16,41));
  assert(route(31,52,31,54));
  if(ARC_BOSSES&(1u<<idx)){
    assert(trigger[mi(48,24)]==TR_ARC_BOSS);
    assert(route(31,52,48,24));
  }
  arc_interact(TR_ARC_REWARD);
  assert(arc_progress==before);
  arc_interact(TR_ARC_SECRET);
  assert(arc_secret_mask&(1u<<idx));
  {int shards=inv[ITEM_SHARD];arc_interact(TR_ARC_SECRET);assert(inv[ITEM_SHARD]==shards);}
  if(idx==7){
   assert(trigger[mi(18,41)]==TR_ARC_PETAL_W);
   assert(trigger[mi(31,25)]==TR_ARC_PETAL_C);
   assert(trigger[mi(46,32)]==TR_ARC_PETAL_U);
   assert(route(31,52,18,41));assert(route(31,52,31,25));assert(route(31,52,46,32));
   arc_interact(TR_ARC_TRIAL);assert(!arc_pending); /* Cannot skip real pickups. */
   arc_interact(TR_ARC_PETAL_C);assert(arc_petals==0); /* Wrong order rejected. */
   arc_interact(TR_ARC_PETAL_W);assert(arc_petals==1);
   save_game();init_new_game();load_game();
   assert(arc_progress==7&&arc_petals==1&&current_room==20);
   generate_surface();
   arc_interact(TR_ARC_PETAL_C);assert(arc_petals==2);
   arc_interact(TR_ARC_PETAL_U);assert(arc_petals==3);
   arc_interact(TR_ARC_PETAL_U);assert(arc_petals==3); /* No duplication. */
  }
  if(idx==13){
   assert(trigger[mi(20,41)]==TR_ARC_ANCHOR_W);
   assert(trigger[mi(52,22)]==TR_ARC_ANCHOR_E);
   assert(route(31,52,20,41));assert(route(31,52,52,22));
   arc_interact(TR_ARC_TRIAL);assert(!arc_pending);
   arc_interact(TR_ARC_ANCHOR_E);assert(arc_anchors==2);
   save_game();init_new_game();load_game();
   assert(arc_progress==13 && arc_anchors==2&&current_room==26);
   generate_surface();
   arc_interact(TR_ARC_ANCHOR_W);assert(arc_anchors==3);
   arc_interact(TR_ARC_ANCHOR_E);assert(arc_anchors==3);
  }
  arc_interact(TR_ARC_TRIAL);assert(arc_pending);
  if(idx==5){arc_answer(KEY_RIGHT);assert(arc_route==3);}
  else{
   /* A genuine incorrect controller choice must not clear the trial. */
   u16 want=ARC_ANSWER[idx]==1?KEY_LEFT:ARC_ANSWER[idx]==2?KEY_UP:KEY_RIGHT;
   u16 wrong=want==KEY_LEFT?KEY_RIGHT:KEY_LEFT;
   arc_answer(wrong);assert(!arc_solved&&!arc_pending);
   arc_interact(TR_ARC_TRIAL);arc_answer(want);assert(arc_solved);
  }
  if(idx==1){
   /* Save in middle of actual authored cavern challenge, reopen old SRAM intact. */
   save_game();for(int i=0;i<238;i++)low[i]=SRAM[i];
   init_new_game();load_game();assert(arc_progress==1 && arc_solved==1);
   assert(current_world==0&&current_room==14);
   for(int i=0;i<238;i++)assert(low[i]==SRAM[i]);
   generate_surface();
  }
  if(ARC_BOSSES&(1u<<idx)){
   assert(enemies[8].active&&enemies[8].elite);
   arc_interact(TR_ARC_REWARD);assert(arc_progress==before);
   arc_interact(TR_ARC_BOSS);assert(game_mode==MODE_BATTLE);
   if(ARC_MERCY&(1u<<idx)){
    battle_cursor=3;battle_act();
    assert(arc_boss_done==1 && !enemies[8].active);
    assert(arc_mercy_mask&(1u<<idx));
   }else{
    str_stat=200;battle_cursor=0;enemies[8].hurt=0;
    battle_act();assert(arc_boss_done==1&&!enemies[8].active);
   }
   battle_exit();
  }
  b=(int)inv[ITEM_SHARD];
  arc_interact(TR_ARC_REWARD);
  assert(arc_progress==idx+1);
  assert(arc_guardians_mask&(1u<<idx));
  if(idx==15)assert(arc_guardians_mask&(1u<<16));
  assert(inv[ITEM_SHARD]>=b || inv[ITEM_SHARD]==99);
  assert((u32)SRAM[ARC_SRAM]=='A' && SRAM[ARC_SRAM+1]=='R');
  arc_interact(TR_ARC_REWARD);assert(arc_progress==idx+1);
  arc_interact(TR_ARC_NEXT);
  if(idx<15){assert(current_room==14+idx && arc_progress==idx+1);}
  else assert(current_room==2 && arc_progress==16);
 }
 assert(arc_guardians_mask==0x1ffffu);
 arc_ally=0;assert(arc_guardian_attack()==2);
 arc_ally=4;assert(arc_guardian_guard()==2);
 arc_ally=16;assert(arc_guardian_guard()==1);
 /* Each World Tree decision has an actual persistent gameplay consequence. */
 arc_ally=4;arc_route=1;assert(arc_guardian_guard()==4&&arc_guardian_attack()==0);
 arc_route=2;assert(arc_guardian_attack()==2&&arc_guardian_guard()==2);
 arc_route=3;assert(arc_guardian_attack()==0&&arc_guardian_guard()==2);
 arc_ally=4;save_game();
 init_new_game();load_game();assert(arc_progress==16&&arc_guardians_mask==0x1ffffu);
 assert(arc_ally==4 && arc_route==3 && arc_solved==0);
 assert(arc_petals==3&&arc_anchors==3);
 assert((arc_mercy_mask&(1u<<1))&&arc_secret_mask==0xffffu);
 printf("PASS: 16 real 64x64 linked rooms and reachable objectives, 3 ordered petals, 2 spatial time anchors, 3 mechanically different World Tree routes, 6 elite battles with mercy, 17 unlockable companions, irrepeatable loot and separate CRC SRAM reload\n");
}
static void save_corruption(void){u8 old[238];
 save_game();for(int i=0;i<238;i++)old[i]=SRAM[i];
 SRAM[ARC_SRAM+13]^=0xfe; /* edit extra atlas CRC only */
 init_new_game();load_game();
 assert(save_valid()&&arc_progress==0&&arc_guardians_mask==0);
 for(int i=0;i<238;i++)assert(SRAM[i]==old[i]);
 assert(lc_party.count<=12);
 printf("PASS: corrupt ARC2 discards only optional atlas, preserved original V10 story and creature pages\n");
}
static void epilogues(void){u16 visible[3];
 postgame=1;for(int c=1;c<=3;c++){
  ending=(u8)c;current_world=0;current_room=2;current_layer=1;
  generate_surface();assert(trigger[mi(22,54)]==TR_ARC_EPILOGUE);
  arc_open_epilogue();assert(current_room==ARC_EPILOGUE_ROOM);
  assert(route(31,52,32,15));assert(route(31,52,31,54));
  assert(trigger[mi(32,15)]==TR_ARC_EPILOGUE);
  assert(trigger[mi(31,54)]==TR_ARC_EXIT);
  visible[c-1]=map_read_tile(13,30);
  arc_interact(TR_ARC_EPILOGUE);assert(dialogue_timer>0);
  arc_interact(TR_ARC_EXIT);assert(current_room==2);
 }
 assert(visible[0]!=visible[1] && visible[1]!=visible[2] && visible[0]!=visible[2]);
 printf("PASS: 3 physically distinct OPEN/PRESERVE/WANDER walkable epilogue spaces with real Brindlemark entry and exit\n");
}
static void sprite_uniqueness(void){unsigned long sigs[8];
 init_graphics();for(int i=0;i<8;i++){
  unsigned long forms[3];
  for(int stage=0;stage<3;stage++){
   forms[stage]=signature(i+1,stage,0);assert(forms[stage]!=5381);
   assert(signature(i+1,stage,1)!=forms[stage]);
   for(int j=0;j<stage;j++)assert(forms[stage]!=forms[j]);
  }
  sigs[i]=forms[0];for(int j=0;j<i;j++)assert(sigs[i]!=sigs[j]);
 }
 printf("PASS: eight distinct native species each with 3 independently rendered sprite stages and 2 visibly distinct animation frames (48 native 16x16 art poses)\n");
}
int main(void){full_atlas();save_corruption();epilogues();sprite_uniqueness();return 0;}
'''
(g/'atlas_full_native_qa.c').write_text(pre+program)
subprocess.run(['clang','-DHOST_QA','-DQA_AUTORUN','-O2','-Wno-unused-function','atlas_full_native_qa.c','-o','atlas_full_native_qa'],cwd=g,check=True)
subprocess.run([str(g/'atlas_full_native_qa')],cwd=g,check=True,timeout=28)
