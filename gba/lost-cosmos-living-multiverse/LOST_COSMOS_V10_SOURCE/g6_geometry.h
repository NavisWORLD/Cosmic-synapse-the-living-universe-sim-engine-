/* Four genuinely distinct source-native 64x64 walkable original GAME rooms.
 * Existing old atlas, original world IDs/maps and original 23 paintings untouched. */
static void g6_patch_atlas_portal(void){int idx=(int)current_room-ARC_FIRST_ROOM,i;
 for(i=0;i<G6_COUNT;i++)if(idx==G6_PARENT[i]){
  for(int y=30;y<=35;y++)for(int x=51;x<=56;x++)map_put(x,y,T_PATH,1,C_FREE,TR_NONE);
  map_put(54,32,T_DOOR,5,C_FREE,TR_G6_PORTAL);return;
 }
}
static void g6_generate_map(void){int x,y,i=(int)current_room-G6_FIRST_ROOM;
 static const int floor[4]={T_ARCHIVE,T_GRASS,T_MOON,T_METAL};
 static const int decor[4]={T_PILLAR,T_TREE,T_FLOWER,T_CIRCUIT};
 static const int accent[4]={T_RUNE,T_VINES,T_STAR,T_CRYSTAL};
 map_fill(floor[i],1);map_border();
 /* Island arches, fallen-root blocks, glass circles and circuit gates differ;
  * all have a completely cleared cross-route and north/south trunk. */
 if(i==0){
  for(x=6;x<=56;x+=8)for(y=8;y<=50;y+=11)map_rect(x,y,3,4,decor[i],3,C_WALL);
  for(x=8;x<=53;x++)map_put(x,23,T_WATER,3,C_WALL,TR_NONE);
 }else if(i==1){
  for(x=6;x<=56;x+=9)for(y=8;y<=49;y+=10)map_rect(x,y,4,4,decor[i],3,C_WALL);
  for(x=6;x<=56;x++)if(x<25||x>37)map_put(x,46,T_HAZARD,3,C_HAZARD,TR_NONE);
 }else if(i==2){
  for(x=6;x<=56;x+=11)for(y=7;y<=50;y+=10)map_rect(x,y,3,3,decor[i],4,C_WALL);
  for(y=8;y<=51;y+=11)for(x=8;x<=56;x++)if(x<26||x>37)map_put(x,y,T_MOON,4,C_WALL,TR_NONE);
 }else{
  for(x=7;x<=55;x+=10)for(y=8;y<=51;y+=8)map_rect(x,y,3,2,decor[i],4,C_WALL);
  for(y=13;y<=43;y+=10)for(x=6;x<=56;x++)if(x<21||x>42)map_put(x,y,T_WATER,4,C_WALL,TR_NONE);
 }
 for(y=13;y<=55;y++)for(x=28;x<=34;x++)map_put(x,y,T_PATH,1,C_FREE,TR_NONE);
 for(x=12;x<=54;x++)for(y=29;y<=36;y++)map_put(x,y,T_PATH,1,C_FREE,TR_NONE);
 for(x=14;x<=33;x++)for(y=41;y<=44;y++)map_put(x,y,T_PATH,1,C_FREE,TR_NONE);
 /* Eight actual A-interaction spots, including three different ordered clue
 * stations. West node in the niche; central node in the cross; east on cross. */
 map_put(20,42,T_RUNE,5,C_FREE,TR_G6_NODE_W);
 map_put(31,25,T_STAR,5,C_FREE,TR_G6_NODE_C);
 map_put(48,35,T_RUNE,5,C_FREE,TR_G6_NODE_E);
 /* Five real separate A-interaction spots: oath, choice, proof, cache, exit. */
 map_put(14,33,accent[i],5,C_FREE,TR_G6_OATH);
 map_put(31,18,T_RUNE,5,C_FREE,TR_G6_CHOICE);
 map_put(51,33,T_CRYSTAL,5,C_FREE,TR_G6_PROOF);
 map_put(17,43,T_STAR,5,C_FREE,TR_G6_CACHE);
 map_put(31,54,T_DOOR,5,C_FREE,TR_G6_EXIT);
 /* Each act gets a recognizably different center landmark without blocking. */
 map_put(22,25,accent[i],4,C_WALL,TR_NONE);
 map_put(43,25,decor[i],4,C_WALL,TR_NONE);
}
