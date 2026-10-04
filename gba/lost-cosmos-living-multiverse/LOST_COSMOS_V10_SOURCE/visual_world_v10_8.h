/* Layered original pixel landmarks. Geometry stays authoritative: stamps never
 * replace authored paths, portals, quest stations, NPCs or spawn footprints. */
#ifndef LC_VISUAL_WORLD_V108_H
#define LC_VISUAL_WORLD_V108_H
static int v108_stamp(int id,int xx,int yy){int x,y,i,t;const V108Decor*d=&V108_DECORS[id];
 if(xx<2||yy<3||xx+d->w>=61||yy+d->h>=60)return 0;
 for(y=yy-1;y<=yy+d->h;y++)for(x=xx-1;x<=xx+d->w;x++){
  t=map_read_tile(x,y);
  if(trigger[mi(x,y)]||t==T_PATH||t==T_BRIDGE||t==T_PAD||t>=V108_BG_EXTRA_BASE||
    iabs(x*8-player.x)+iabs(y*8-player.y)<32)return 0;
  for(i=0;i<npc_count;i++)if(iabs(x*8-npc_runtime[i].x)+iabs(y*8-npc_runtime[i].y)<24)return 0;
 }
 /* Background imagery preserves every existing collision cell. Crown foliage
  * can cover open ground; its established trunk remains the actual obstacle. */
 for(y=0;y<d->h;y++)for(x=0;x<d->w;x++)set_map_entry(xx+x,yy+y,map_attr(d->base+y*d->w+x,d->palette));
 return 1;
}
static void v108_paint_world(void){int x,y,t,h,theme;
 theme=COMP_IS_ROOM?COMPLETION_SCENES[current_room-COMPLETION_FIRST_ROOM].theme:
  current_world==0?(current_room==7?3:current_room==8?2:current_room==9?1:current_room==12?5:0):current_world;
 /* Multi-tile landforms are deterministic, with each biome's own language. */
 for(y=5;y<55;y+=9)for(x=5;x<55;x+=10){
  t=map_read_tile(x,y);h=(x*11+y*7+current_room*13)&15;
  if(t==T_TREE||t==T_PLANT)v108_stamp((theme==2||theme==7)?V108_DECOR_WILLOW:V108_DECOR_OAK,x-1,y-2);
  else if(t==T_WATER&&h<5)v108_stamp(theme==2?V108_DECOR_CORAL:V108_DECOR_WATERFALL_0,x,y);
  else if(t==T_CRYSTAL||t==T_PILLAR&&theme==2)v108_stamp(V108_DECOR_CRYSTAL_SPIRE,x,y-1);
  else if(t==T_WALL||t==T_RUIN&&h<4)v108_stamp(V108_DECOR_RUIN_ARCH,x,y);
  else if(h==1&&t==T_GRASS&&current_room==2)v108_stamp(V108_DECOR_COTTAGE,x,y);
  else if(h==2&&t==T_GRASS&&current_room==3)v108_stamp(V108_DECOR_COTTAGE,x,y);
  else if(h==1&&t==T_FLOOR&&theme==1)v108_stamp(V108_DECOR_FORGE,x,y);
  else if(h==2&&(theme==4||theme==5))v108_stamp(V108_DECOR_OBSERVATORY,x,y);
 }
 /* Rich surface variations and path edges retain original collision/trigger
  * data. Every old mandatory corridor stays exactly as wide as authored. */
 for(y=2;y<62;y++)for(x=2;x<62;x++){
  if(trigger[mi(x,y)])continue;t=map_read_tile(x,y);if(t>=64)continue;
  h=(x*13+y*17+current_room*5+current_world*19)&3;
  if(t==T_GRASS)set_map_entry(x,y,map_attr(224+h,0));
  else if(t==T_FLOOR)set_map_entry(x,y,map_attr(228+h,0));
  else if(t==T_PATH){int edge=0;
   if(map_read_tile(x,y-1)!=T_PATH)edge=1;
   else if(map_read_tile(x,y+1)!=T_PATH)edge=2;
   else if(map_read_tile(x-1,y)!=T_PATH)edge=3;
   set_map_entry(x,y,map_attr(edge?240+(edge-1)*2+(h&1):232+h,1));
  }else if(t==T_RUIN)set_map_entry(x,y,map_attr(236+h,4));
 }
}
/* Two waterfall pages exchange in place; collision and map entries stay put. */
static void v108_waterfall_tick(void){int i,p=(frame>>5)&1;
 const V108Decor*a=&V108_DECORS[V108_DECOR_WATERFALL_0];
 const V108Decor*b=&V108_DECORS[V108_DECOR_WATERFALL_1];
 for(i=0;i<15;i++)upload_bg_tile(a->base+i,V108_BG_EXTRA[(p?b->base:a->base)-64+i]);
}
#endif
