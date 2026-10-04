/* Recorded Spark Beasts on the Sol overworld. Tiles are baked from the same
 * renderer and quantum-run table as the web game. Nothing here is live.
 * OBJ palette 12 is unused by field NPCs (they stay on 13 and 14) and by the
 * imported companion (palette 15), so Sol NPC colours stay as they are. */
#ifndef LOST_COSMOS_SPARK_FIELD_H
#define LOST_COSMOS_SPARK_FIELD_H
#include "spark_field_beasts.h"
#define SPARK_OBJ_TILE 912
#define SPARK_OBJ_PAL 12
static s16 spark_fx[SPARK_FIELD_COUNT];
static s16 spark_fy[SPARK_FIELD_COUNT];
static s16 spark_follow_x,spark_follow_y;
static u8 spark_field_ready,spark_follow_init;

static void spark_field_ensure(void){
 int i;
 if(spark_field_ready)return;
 for(i=0;i<SPARK_FIELD_COUNT;i++){
  spark_fx[i]=(s16)(SPARK_FIELD[i].tx*8);
  spark_fy[i]=(s16)(SPARK_FIELD[i].ty*8);
 }
 spark_field_ready=1;
}
static void spark_follow_place(void){
 if(!lc_mail_live){spark_follow_init=0;return;}
 if(!spark_follow_init){
  spark_follow_x=(s16)(player.x-22);
  spark_follow_y=(s16)(player.y+12);
  spark_follow_init=1;
 }
}
static void spark_follow_tick(void){
 s16 tx,ty;int dx,dy;
 spark_follow_place();
 if(!lc_mail_live||game_mode!=MODE_SURFACE)return;
 tx=(s16)(player.x-22);ty=(s16)(player.y+12);
 dx=signi(tx-spark_follow_x);dy=signi(ty-spark_follow_y);
 if(dx&&!buddy_tile_blocked(spark_follow_x+dx,spark_follow_y))spark_follow_x=(s16)(spark_follow_x+dx);
 if(dy&&!buddy_tile_blocked(spark_follow_x,spark_follow_y+dy))spark_follow_y=(s16)(spark_follow_y+dy);
}
static void spark_field_tick(void){
 int i;
 if(game_mode!=MODE_SURFACE)return;
 spark_field_ensure();
 spark_follow_tick();
 if((frame&3)!=0)return;
 for(i=0;i<SPARK_FIELD_COUNT;i++){
  int home_x,home_y,dir,dx,dy,nx,ny;
  if(SPARK_FIELD[i].world!=current_world)continue;
  home_x=SPARK_FIELD[i].tx*8;home_y=SPARK_FIELD[i].ty*8;
  dir=((frame>>3)+i*5)&3;
  dx=dir==0?1:(dir==1?-1:0);
  dy=dir==2?1:(dir==3?-1:0);
  nx=spark_fx[i]+dx;ny=spark_fy[i]+dy;
  if(nx<home_x-28||nx>home_x+28)dx=0;
  if(ny<home_y-28||ny>home_y+28)dy=0;
  if(dx&&!buddy_tile_blocked(spark_fx[i]+dx,spark_fy[i]))spark_fx[i]=(s16)(spark_fx[i]+dx);
  if(dy&&!buddy_tile_blocked(spark_fx[i],spark_fy[i]+dy))spark_fy[i]=(s16)(spark_fy[i]+dy);
 }
}
static const char* spark_field_near_name(void){
 int i,best=80,id=-1;
 spark_field_ensure();
 for(i=0;i<SPARK_FIELD_COUNT;i++){
  int d;
  if(SPARK_FIELD[i].world!=current_world)continue;
  d=iabs(spark_fx[i]-player.x)+iabs(spark_fy[i]-player.y);
  if(d<best){best=d;id=i;}
 }
 return id<0?0:SPARK_FIELD[id].name;
}
static void spark_field_draw(void){
 int i,k,shown[3],rank[3];
 const char*near;
 spark_field_ensure();
 spark_follow_place();
 for(k=0;k<3;k++){shown[k]=-1;rank[k]=9999;}
 for(i=0;i<SPARK_FIELD_COUNT;i++){
  int d,slot;
  if(SPARK_FIELD[i].world!=current_world)continue;
  d=iabs(spark_fx[i]-player.x)+iabs(spark_fy[i]-player.y);
  slot=3;
  while(slot>0&&d<rank[slot-1])slot--;
  if(slot>=3)continue;
  for(k=2;k>slot;k--){rank[k]=rank[k-1];shown[k]=shown[k-1];}
  rank[slot]=d;shown[slot]=i;
 }
 if(shown[0]>=0){int c;for(c=0;c<16;c++)OBJ_PALETTE[SPARK_OBJ_PAL*16+c]=SPARK_WORLD_PAL[current_world&7][c];}
 for(i=0;i<3;i++){
  int oi=43+i,id,sx,sy,b,tile;
  volatile u16*dst;const u8*src;
  if(shown[i]<0){OAM16[oi*4]=0x0200;continue;}
  id=shown[i];
  sx=spark_fx[id]-cam_x-16;sy=spark_fy[id]-cam_y-24;
  if(sx<-32||sx>239||sy<-32||sy>159){OAM16[oi*4]=0x0200;continue;}
  tile=SPARK_OBJ_TILE+i*16;
  dst=(volatile u16*)OBJ_VRAM32;src=SPARK_FIELD_TILES[id];
  for(b=0;b<256;b++)dst[tile*16+b]=(u16)src[b*2]|((u16)src[b*2+1]<<8);
  oam_set32(oi,sx,sy,tile,SPARK_OBJ_PAL);
 }
 if(lc_mail_live&&lc_mail_name[0])ui_text(18,1,lc_mail_name,14);
 near=spark_field_near_name();
 if(near){ui_text(2,2,near,14);ui_text(16,2,"RECORDED/SEED",13);}
}
#endif
