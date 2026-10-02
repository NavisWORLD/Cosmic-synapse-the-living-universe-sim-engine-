"""Actual V10.8 native C simulated-MMIO geometry and CRC isolation regression.
The artificially unlocked prerequisite mask is a unit-test fixture, NOT proof of
a real player's full campaign completion or manuscript acceptance.
"""
from pathlib import Path
import subprocess

r=Path(__file__).resolve().parents[1]
g=r/'LOST_COSMOS_V10_SOURCE'
subprocess.run(['python3','host_qa_v5.py'],cwd=g,check=True,capture_output=True,timeout=45)
pre=(g/'host_qa_v5.c').read_text().split('\n#ifdef HOST_QA\nint main(',1)[0]
source=pre+r'''
#include <assert.h>
#include <stdio.h>
#include <string.h>
static int route(int sx,int sy,int tx,int ty){
 u8 seen[4096]={0};u16 q[4096];int head=0,tail=0;
 int n=mi(sx,sy);assert(collision[n]!=C_WALL);seen[n]=1;q[tail++]=n;
 while(head<tail){int v=q[head++],x=v&63,y=v>>6;
  if(x==tx&&y==ty)return 1;
  const int dx[4]={0,0,-1,1},dy[4]={1,-1,0,0};
  for(int d=0;d<4;d++){
   int nx=x+dx[d],ny=y+dy[d];
   if(nx<=1||ny<=1||nx>=62||ny>=62)continue;
   n=mi(nx,ny);
   if(!seen[n]&&collision[n]!=C_WALL){seen[n]=1;q[tail++]=n;}
  }
 }return 0;
}
static void test_rooms(void){
 init_new_game();init_graphics();intro=0;game_mode=MODE_SURFACE;
 assert(!completion_available(0));story_flags=ST_HEART;
 assert(completion_available(0));assert(!completion_available(1));
 /* Explicit C TEST prerequisite setup, NOT fabricated real player evidence. */
 story_flags|=ST_DREAM|ST_HEARTWOOD|ST_VOID|ST_CHRONO|ST_LATTICE|ST_CITY;
 arc_progress=16;arc_petals=3;arc_anchors=3;element_mask=15;
 v10_relic=RF_CLARITY|RF_PASSION|RF_HARMONY|RF_GROVE_RIDDLE|RF_EARTH|RF_FESTIVAL;
 g7_sigils=15;g7_pillars=3;g7_orbs=31;
 for(int i=0;i<24;i++){
  completion_done=(1u<<i)-1u;
  assert(completion_available(i));completion_warp(i);
  assert(COMP_IS_ROOM&&current_room==COMPLETION_FIRST_ROOM+i);
  assert(trigger[mi(31,54)]==TR_COMP_EXIT&&trigger[mi(55,10)]==TR_COMP_NEXT);
  assert(trigger[mi(10,48)]==TR_COMP_CACHE);
  assert(route(31,51,31,54)&&route(31,51,55,10)&&route(31,51,10,48));
  for(int j=0;j<4;j++){
   const CompletionObjective*o=&COMPLETION_OBJECTIVES[i][j];
   if(trigger[mi(o->tx,o->ty)]!=TR_COMP_OBJECTIVE+j){
    fprintf(stderr,"SOFTLOCK: chapter=%d objective=%d actual_trigger=%u\n",
            i,j,trigger[mi(o->tx,o->ty)]);assert(0);
   }
   assert(route(31,51,o->tx,o->ty));
  }
  int before=inv[ITEM_POTION];completion_interact(TR_COMP_CACHE);
  assert(inv[ITEM_POTION]==mini(99,before+1));
  before=inv[ITEM_POTION];completion_interact(TR_COMP_CACHE);
  assert(inv[ITEM_POTION]==before);
  assert(!(completion_done&(1u<<i)));
 }
 puts("PASS actual 24 native map geometries, 96 triggered and collision-reachable objectives, 72 safe exits/caches, chapter gates, and repeat-safe pickups");
}
static void test_crc_isolation(void){
 completion_reset();current_world=0;current_room=2;story_flags=0;
 int start[6]={0,1024,2048,3072,4096,5120};
 int count[6]={238,252,32,32,32,32};u8 old[6][252];
 for(int p=0;p<6;p++)for(int k=0;k<count[p];k++)old[p][k]=SRAM[start[p]+k];
 completion_save();
 for(int p=0;p<6;p++)for(int k=0;k<count[p];k++)assert(old[p][k]==SRAM[start[p]+k]);
 completion_seen=1;completion_save();SRAM[COMP_SRAM+20]=255;
 completion_restore();assert(!completion_seen&&!completion_done);
 for(int p=0;p<6;p++)for(int k=0;k<count[p];k++)assert(old[p][k]==SRAM[start[p]+k]);
 puts("PASS strict independent V10.8 128-byte CRC32 page and malformed progress; six legacy save regions untouched");
}
int main(void){test_rooms();test_crc_isolation();return 0;}
'''
(g/'completion_map_regression_host.c').write_text(source)
subprocess.run(['clang','-DHOST_QA','-DQA_AUTORUN','-O2',
 '-Wno-unused-function','completion_map_regression_host.c',
 '-o','completion_map_regression_host'],cwd=g,check=True,timeout=60)
subprocess.run([str(g/'completion_map_regression_host')],cwd=g,check=True,timeout=45)
