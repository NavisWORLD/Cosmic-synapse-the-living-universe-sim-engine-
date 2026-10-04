/* Each room is a distinct deterministic 64x64 GBA tile/collision composition.
   Three authored traversal corridors stay navigable after decoration. */
static void arc_generate_map(void){
 int i,j,x,y,idx=(int)current_room-ARC_FIRST_ROOM;
 int floors[]={T_GRASS,T_RUIN,T_ARCHIVE,T_MOON,T_ARCHIVE,T_GRASS,T_GRASS,
   T_FLOWER,T_PATH,T_GRASS,T_MOON,T_PATH,T_FLOWER,T_ARCHIVE,T_VOID,T_CROWN};
 int solids[]={T_TREE,T_WALL,T_PILLAR,T_MOON,T_ARCHIVE,T_TREE,T_VINES,
   T_CRYSTAL,T_PILLAR,T_TREE,T_RUIN,T_PILLAR,T_FLOWER,T_CIRCUIT,T_HAZARD,T_PILLAR};
 int scenery[]={T_FLOWER,T_CRACK,T_RUNE,T_STAR,T_ARCHIVE,T_PLANT,T_VINES,
   T_FLOWER,T_LANTERN,T_CRYSTAL,T_STAR,T_RUNE,T_FLOWER,T_CIRCUIT,T_MOON,T_STAR};
 int w=5+(idx%4),height=4+(idx%5);
 map_fill(floors[idx],0);map_border();
 /* Distinct topologies, never a procedural reskin of the existing novel maps. */
 for(i=4;i<59;i+=w)for(j=6;j<58;j+=height){
   int h=(i*i*3+j*17+idx*53+i*j)&15;
   if((h<5 || ((idx&1)&&h==10)) && ((i+j+idx)&3)!=0)
    map_rect(i,j,(idx%3)+1,((idx+2)%3)+1,solids[idx],2,C_WALL);
 }
 if(idx==1||idx==13){for(y=7;y<45;y+=8)for(x=4;x<60;x++)
     if(x<26||x>37)map_put(x,y,T_WATER,3,C_WALL,0);}
 if(idx==8||idx==15){for(x=5;x<60;x+=9)for(y=8;y<52;y++)
     if(y<22||y>38)map_put(x,y,T_WALL,2,C_WALL,0);}
 if(idx==14||idx==10){for(y=10;y<48;y+=12)for(x=4;x<59;x++)
     if(x<18||x>47)map_put(x,y,T_HAZARD,3,C_HAZARD,0);}
 if(idx==5){for(i=0;i<4;i++)map_wall_box(15+i*4,15+i*4,35-i*8,33-i*8,3);}
 if(idx==6||idx==9){for(i=0;i<6;i++)map_rect(5+i*9,9+(i%3)*9,3,5,T_TREE,2,C_WALL);}
 for(i=0;i<110;i++){
   x=3+((i*23+i*i*3+idx*17)%58);y=3+((i*37+i*i*7+idx*11)%58);
   if(collision[mi(x,y)]==C_FREE && trigger[mi(x,y)]==TR_NONE)
     map_put(x,y,scenery[idx],3,C_FREE,0);
 }
 /* Carve and decorate a guaranteed safe T-junction with physically reachable objectives. */
 for(y=11;y<=55;y++)for(x=28;x<=34;x++)map_put(x,y,T_PATH,2,C_FREE,0);
 for(x=29;x<=55;x++)for(y=30;y<=34;y++)map_put(x,y,T_PATH,2,C_FREE,0);
 for(x=30;x<=55;x++)for(y=10;y<=14;y++)map_put(x,y,T_PATH,2,C_FREE,0);
 for(y=12;y<=33;y++)for(x=51;x<=55;x++)map_put(x,y,T_PATH,2,C_FREE,0);
 /* A separate western secret niche: a guaranteed shard, never an impossible rare drop. */
 for(x=15;x<=31;x++)for(y=40;y<=43;y++)map_put(x,y,T_PATH,2,C_FREE,0);
 map_put(16,41,T_CRYSTAL,3,C_FREE,TR_ARC_SECRET);
 /* Two walkable unique guardian-personal quest stations in each existing
  * atlas region. Play the original chapter first; these are OPTIONAL additions. */
 for(y=30;y<=35;y++)for(x=20;x<=31;x++)map_put(x,y,T_PATH,2,C_FREE,0);
 for(y=32;y<=39;y++)for(x=45;x<=52;x++)map_put(x,y,T_PATH,2,C_FREE,0);
 map_put(22,32,T_STAR,4,C_FREE,TR_G5_OATH);
 map_put(49,37,T_CRYSTAL,4,C_FREE,TR_G5_PROOF);
 if(idx==7){ /* Three actual locations in an ordered world-tree trial. */
  map_put(18,41,T_FLOWER,3,C_FREE,TR_ARC_PETAL_W);
  map_put(31,25,T_FLOWER,3,C_FREE,TR_ARC_PETAL_C);
  map_put(46,32,T_FLOWER,3,C_FREE,TR_ARC_PETAL_U);
 }
 if(idx==13){ /* Two physically separated Chrono Annex anchor switches. */
  map_put(20,41,T_CIRCUIT,3,C_FREE,TR_ARC_ANCHOR_W);
  map_put(52,22,T_CIRCUIT,3,C_FREE,TR_ARC_ANCHOR_E);
 }
 /* Physically navigable boss platform (stage-specific). */
 if(ARC_BOSSES&(1u<<idx)){
  for(y=22;y<=26;y++)for(x=46;x<=54;x++)
   map_put(x,y,T_PATH,2,C_FREE,0);
  map_put(48,24,T_HAZARD,3,C_FREE,TR_ARC_BOSS);
 }
 map_put(31,18,T_RUNE,3,C_FREE,TR_ARC_TRIAL);
 map_put(45,32,T_CRYSTAL,3,C_FREE,TR_ARC_REWARD);
 map_put(53,12,T_DOOR,3,C_FREE,TR_ARC_NEXT);
 map_put(31,54,T_DOOR,3,C_FREE,TR_ARC_EXIT);
 /* Four landmarks form a recognizable micro-map even before cinematic production. */
 map_put(25,26,idx&1?T_ARCHIVE:T_TREE,3,C_WALL,0);
 map_put(39,23,idx&1?T_PILLAR:T_CRYSTAL,3,C_WALL,0);
 map_put(13,36,idx&1?T_LANTERN:T_RUNE,3,C_FREE,0);
}
static void arc_generate_epilogue(void){int x,y;
 int floor=ending==1?T_FLOWER:ending==2?T_GRASS:T_MOON;
 map_fill(floor,0);map_border();
 for(x=5;x<59;x+=8)for(y=8;y<53;y+=10)
   map_put(x,y,ending==1?T_STAR:ending==2?T_TREE:T_RUNE,3,C_WALL,0);
 for(y=10;y<56;y++)for(x=29;x<=35;x++)map_put(x,y,T_PATH,2,C_FREE,0);
 for(x=12;x<=52;x++)for(y=27;y<=33;y++)map_put(x,y,T_PATH,2,C_FREE,0);
 for(x=13;x<=51;x+=19)map_put(x,30,ending==1?T_CRYSTAL:ending==2?T_TREE:T_MOON,3,C_FREE,TR_ARC_EPILOGUE);
 map_put(32,15,T_CROWN,3,C_FREE,TR_ARC_EPILOGUE);
 for(y=30;y<=35;y++)for(x=20;x<=31;x++)map_put(x,y,T_PATH,2,C_FREE,0);
 for(y=32;y<=39;y++)for(x=45;x<=52;x++)map_put(x,y,T_PATH,2,C_FREE,0);
 map_put(22,32,T_STAR,4,C_FREE,TR_G5_OATH);
 map_put(49,37,T_CRYSTAL,4,C_FREE,TR_G5_PROOF);
 map_put(31,54,T_DOOR,3,C_FREE,TR_ARC_EXIT);
}
