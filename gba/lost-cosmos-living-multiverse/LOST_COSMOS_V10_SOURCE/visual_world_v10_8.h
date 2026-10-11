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
static int v115_is_road(int t){return t==T_PATH||(t>=232&&t<=235)||(t>=240&&t<=247)||t==V116_MARK_TILE_BASE+V116_MARK_PATH_STAR;}
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
  if(trigger[mi(x,y)]){
   /* V11.6: a star trigger on open ground gets a road- or grass-backed star
    * instead of the space tile's black square. Trigger and collision stay. */
   if(map_read_tile(x,y)==T_STAR){
    int road=v115_is_road(map_read_tile(x,y-1))||v115_is_road(map_read_tile(x,y+1))||v115_is_road(map_read_tile(x-1,y))||v115_is_road(map_read_tile(x+1,y));
    int grass=!road&&(map_read_tile(x-1,y)==T_GRASS||(map_read_tile(x-1,y)>=224&&map_read_tile(x-1,y)<=227));
    if(road)set_map_entry(x,y,map_attr(V116_MARK_TILE_BASE+V116_MARK_PATH_STAR,1));
    else if(grass)set_map_entry(x,y,map_attr(V116_MARK_TILE_BASE+V116_MARK_GRASS_STAR,0));
   }
   continue;}
  t=map_read_tile(x,y);if(t>=64)continue;
  h=(x*13+y*17+current_room*5+current_world*19)&3;
  if(t==T_GRASS)set_map_entry(x,y,map_attr(224+h,0));
  else if(t==T_FLOOR)set_map_entry(x,y,map_attr(228+h,0));
  else if(t==T_PATH){
   /* V11.5: the neighbours above and to the left were already repainted in
    * this pass, so a painted road tile still counts as road. The edge tile
    * follows which sides meet grass: a one-tile road is a strip, not a
    * random top/right or bottom/left edge (the old "plank" look). */
   int n=!v115_is_road(map_read_tile(x,y-1)),s=!v115_is_road(map_read_tile(x,y+1));
   int w=!v115_is_road(map_read_tile(x-1,y)),e=!v115_is_road(map_read_tile(x+1,y)),k;
   if(n&&s&&!(w&&e))k=240+(h&1);
   else if(w&&e&&!(n&&s))k=242+(h&1);
   else if(n)k=244;else if(s)k=245;else if(w)k=246;else if(e)k=247;
   else k=232+h;
   set_map_entry(x,y,map_attr(k,1));
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
