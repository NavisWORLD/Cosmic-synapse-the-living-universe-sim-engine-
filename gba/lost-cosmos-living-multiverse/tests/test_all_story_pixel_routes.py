"""ALL 40 genuine source-generated narrative maps / actual 10px actor collision.
Unlike tile BFS, verifies actual 2px D-pad step geometry and trigger_near()
precedence. GBA host-MMIO source QA only: NOT human real-mGBA footage.
"""
from pathlib import Path
import subprocess
r=Path(__file__).resolve().parents[1]
g=r/"LOST_COSMOS_V10_SOURCE"
subprocess.run(["python3","host_qa_v5.py"],cwd=g,check=True,capture_output=True,timeout=40)
pre=(g/"host_qa_v5.c").read_text().split("\n#ifdef HOST_QA\nint main(",1)[0]
source=pre+r"""
#include <assert.h>
#include <stdio.h>
#include <string.h>
#define QCAP 65536
static unsigned char seen[QCAP],marks[256];
static unsigned q[QCAP];
static int stand(int x,int y){
 if(x<8||y<8||x>503||y>503)return 0;
 return tile_collision_at(x-5,y-5)!=C_WALL &&
        tile_collision_at(x+5,y-5)!=C_WALL &&
        tile_collision_at(x-5,y+5)!=C_WALL &&
        tile_collision_at(x+5,y+5)!=C_WALL;
}
static int explore(int x,int y){
 memset(seen,0,sizeof(seen));memset(marks,0,sizeof(marks));
 unsigned head=0,tail=0;int ox=player.x,oy=player.y;
 assert(stand(x,y));int k=(y/2)*256+x/2;seen[k]=1;q[tail++]=k;
 while(head<tail){
  k=q[head++];x=(k&255)*2;y=(k>>8)*2;
  player.x=(s16)x;player.y=(s16)y;marks[trigger_near()]=1;
  int dx[4]={2,-2,0,0},dy[4]={0,0,2,-2};
  for(int d=0;d<4;d++){
   int nx=x+dx[d],ny=y+dy[d];
   if(!stand(nx,ny))continue;
   int v=(ny/2)*256+nx/2;
   if(!seen[v]){seen[v]=1;q[tail++]=v;}
  }
 }
 player.x=(s16)ox;player.y=(s16)oy;return tail;
}
static int count=0,fail=0;
static void need(int room,int triggerid,int reached){
 count++;
 if(!marks[triggerid]){fprintf(stderr,"PIXEL SOFTLOCK room=%d trigger=%d reachable_pixels=%d\n",room,triggerid,reached);fail++;}
}
int main(void){
 init_new_game();init_graphics();intro=0;game_mode=MODE_SURFACE;
 for(int i=0;i<24;i++){
  current_world=0;current_room=COMPLETION_FIRST_ROOM+i;current_layer=1;
  completion_step[i]=0;generate_surface();
  int n=explore(31*8,51*8);
  need(current_room,TR_COMP_EXIT,n);
  need(current_room,TR_COMP_NEXT,n);
  need(current_room,TR_COMP_CACHE,n);
  for(int j=0;j<4;j++){
   need(current_room,TR_COMP_OBJECTIVE+j,n);
   if(COMPLETION_OBJECTIVES[i][j].action==COMP_ACT_SEQUENCE)
    for(int k=0;k<3;k++)need(current_room,TR_COMP_SEQUENCE+k,n);
  }
 }
 for(int i=0;i<G6_COUNT;i++){
  current_world=0;current_room=G6_FIRST_ROOM+i;current_layer=1;generate_surface();
  int n=explore(31*8,52*8);
  for(int t=TR_G6_OATH;t<=TR_G6_NODE_E;t++)need(current_room,t,n);
 }
 for(int i=0;i<G7_COUNT;i++){
  current_world=0;current_room=G7_FIRST_ROOM+i;current_layer=1;generate_surface();
  int n=explore(31*8,52*8);
  for(int t=TR_G7_OATH;t<=TR_G7_NEXT;t++)need(current_room,t,n);
  if(i==9)for(int t=TR_G7_SIGIL_FIRST;t<=TR_G7_SIGIL_LAST;t++)need(current_room,t,n);
  if(i==10)need(current_room,TR_G7_PILLAR,n);
  if(i==11)for(int t=TR_G7_ORB_FIRST;t<=TR_G7_ORB_LAST;t++)need(current_room,t,n);
 }
 /* Regress existing real-actor Hollow Grove entry and every quest station.
  * Procedural trees previously blocked the 10px player from its real spawn
  * even though the old one-tile BFS passed this original realm. */
 current_world=7;current_room=10;current_layer=1;generate_surface();
 int grove=explore(10*8,52*8);
 need(current_room,TR_GATE,grove);
 need(current_room,TR_GROVE_MIRROR,grove);
 need(current_room,TR_GROVE_WRAITH,grove);
 need(current_room,TR_EARTH,grove);
 /* Also test ALL five original book chapters, starting at original
  * authentic native door spawn, not tile-BFS fantasy entry points. */
 {const int worlds[5]={0,0,0,0,6},rooms[5]={7,8,9,12,11};
  const int counts[5]={4,4,5,3,4};
  const int targets[5][5]={
    {TR_HW_WISDOM,TR_HW_COURAGE,TR_HW_HEART,TR_GATE,0},
    {TR_ICE_RUNE,TR_ICE_WOLF,TR_ICE_CRYSTAL,TR_GATE,0},
    {TR_FLAME_LEFT,TR_FLAME_RIGHT,TR_PHOENIX,TR_PASSION,TR_GATE},
    {TR_PEAK_RUNE,TR_HARMONY,TR_GATE,0,0},
    {TR_FEST_L,TR_FEST_C,TR_FEST_R,TR_GATE,0}};
  for(int j=0;j<5;j++){
   current_world=worlds[j];current_room=rooms[j];current_layer=1;
   generate_surface();
   int n=explore((j==0?11:10)*8,52*8);
   for(int k=0;k<counts[j];k++)need(current_room,targets[j][k],n);
  }
 }
 printf("TOTAL pixel-footprint native objective checks %d unreachable %d\n",count,fail);
 assert(count==351&&fail==0);
 puts("PASS ALL 40 native expansion maps; actual 10px actor and real trigger_near priority.");
 return 0;
}
"""
(g/"all_story_pixel_routes_host.c").write_text(source)
subprocess.run(["clang","-DHOST_QA","-DQA_AUTORUN","-O2","-Wno-unused-function",
                "all_story_pixel_routes_host.c","-o","all_story_pixel_routes_host"],cwd=g,check=True,timeout=40)
subprocess.run([str(g/"all_story_pixel_routes_host")],cwd=g,check=True,timeout=60)
