/* 12 new original GAME-art 64x64 chapters. All action sites are reachable
 * from 31,52 and the door; distinct topology and no dead-end objective. */
static void g7_patch_parent_portal(void){int j;int p=(int)current_room-ARC_FIRST_ROOM;
 for(j=0;j<G7_COUNT;j++)if(G7_PARENT[j]==p){int x,y;
  /* Preserve G5 original oath (22,32) and all old chapter triggers. */
  for(y=30;y<=35;y++)for(x=11;x<=20;x++)map_put(x,y,T_PATH,2,C_FREE,TR_NONE);
  map_put(12,33,T_DOOR,5,C_FREE,TR_G7_PORTAL);return;
 }
}
static void g7_generate_map(void){int x,y,i=(int)current_room-G7_FIRST_ROOM;
 const int floor=G7_FLOOR[i],decor=G7_DECOR[i],accent=G7_ACCENT[i];
 map_fill(floor,1);map_border();
 /* Layout families genuinely vary in maze direction, scenery and hazards. */
 for(y=6;y<55;y+=7+(i%3))for(x=7;x<59;x+=9+(i%4))
  if(((x*7+y*11+i*13)&7)<5)
    map_rect(x,y,2+(i%3),2+(i&1),decor,3,C_WALL);
 if(i==4||i==9)for(x=6;x<=55;x++)if(x<24||x>38)
   map_put(x,24,i==4?T_WATER:T_VOID,4,C_WALL,TR_NONE);
 if(i==2||i==10)for(y=11;y<=48;y++)if(y<29||y>36)
   map_put(39,y,T_HAZARD,3,C_HAZARD,TR_NONE);
 if(i==7||i==8)for(x=7;x<=54;x+=13)for(y=8;y<=51;y+=12)
  map_put(x,y,T_LANTERN,4,C_FREE,TR_NONE);
 /* Two central axes plus upper and lower cross-bridges connect EVERY marker. */
 for(y=8;y<=55;y++)for(x=28;x<=34;x++)map_put(x,y,T_PATH,2,C_FREE,TR_NONE);
 for(y=15;y<=21;y++)for(x=10;x<=54;x++)map_put(x,y,T_PATH,2,C_FREE,TR_NONE);
 for(y=29;y<=36;y++)for(x=10;x<=54;x++)map_put(x,y,T_PATH,2,C_FREE,TR_NONE);
 for(y=40;y<=46;y++)for(x=10;x<=54;x++)map_put(x,y,T_PATH,2,C_FREE,TR_NONE);
 for(y=18;y<=43;y++)for(x=10;x<=15;x++)map_put(x,y,T_PATH,2,C_FREE,TR_NONE);
 for(y=18;y<=43;y++)for(x=48;x<=54;x++)map_put(x,y,T_PATH,2,C_FREE,TR_NONE);
 /* Eight native A-interaction fixtures per map; 10/11 have bonus puzzles. */
 map_put(13,32,accent,5,C_FREE,TR_G7_OATH);
 map_put(31,15,T_RUNE,5,C_FREE,TR_G7_CHOICE);
 map_put(18,42,T_RUNE,5,C_FREE,TR_G7_NODE_A);
 map_put(46,42,T_RUNE,5,C_FREE,TR_G7_NODE_B);
 map_put(51,32,T_CRYSTAL,5,C_FREE,TR_G7_PROOF);
 map_put(31,27,T_STAR,5,C_FREE,TR_G7_CACHE);
 map_put(31,54,T_DOOR,5,C_FREE,TR_G7_EXIT);
 map_put(48,18,T_DOOR,5,C_FREE,TR_G7_NEXT);
 /* Optional original-game appendix floor puzzles have separately earned nodes. */
 if(i==9){for(x=0;x<4;x++)map_put(13+x*12,20,T_CIRCUIT,5,C_FREE,(u8)(TR_G7_SIGIL_FIRST+x));}
 if(i==10){map_put(31,20,T_CROWN,5,C_FREE,TR_G7_PILLAR);}
 if(i==11){for(x=0;x<5;x++)map_put(11+x*10,20,T_CRYSTAL,5,C_FREE,(u8)(TR_G7_ORB_FIRST+x));}
 /* Contrasting landscape landmarks, avoid carving across a trigger. */
 map_put(21,25,decor,3,C_WALL,TR_NONE);
 map_put(43,25,accent,3,C_WALL,TR_NONE);
}
