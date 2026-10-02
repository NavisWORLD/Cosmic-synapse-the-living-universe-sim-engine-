/* V10.2 main atlas route: actual triggered gameplay, not auto-marked quest text. */
static void arc_room_change(u8 room,int tx,int ty,const char*line){
 current_world=0;current_room=room;current_layer=1;game_mode=MODE_SURFACE;
 player.x=(s16)(tx*8);player.y=(s16)(ty*8);
 cosmos.x=player.x+12;cosmos.y=player.y-12;
 generate_surface();refresh_camera();say(line);save_game();
}
static void arc_enter(void){
 if(!(story_flags&ST_HEART)){say("THE ATLAS AWAKENS AFTER THE HEART OF ERIDORIA.");return;}
 if(arc_progress>=ARC_STAGES){
  arc_room_change((u8)(ARC_FIRST_ROOM+ARC_STAGES-1),31,52,
    "THE ATLAS IS RESTORED. RETURN ANY TIME.");
 }else arc_room_change((u8)(ARC_FIRST_ROOM+arc_progress),31,52,
    "A NEW PAGE OF ERIDORIA OPENS.");
}
static void arc_return(void){
 arc_room_change(2,39,52,"BACK TO BRINDLEMARK. YOUR ATLAS REMEMBERS.");
}
static void arc_answer(u16 keys){
 int idx;u8 selected=0;
 if(!arc_pending||!ARC_IS_ROOM){arc_pending=0;return;}
 idx=(int)current_room-ARC_FIRST_ROOM;
 if(keys&KEY_LEFT)selected=1;
 else if(keys&KEY_UP)selected=2;
 else if(keys&KEY_RIGHT)selected=3;
 else if(keys&KEY_B){arc_pending=0;say("THE TRIAL WILL WAIT FOR YOU.");return;}
 else return;
 arc_pending=0;
 if(idx==7&&arc_petals!=3){say("FIND THE THREE PETALS: WISDOM COURAGE UNITY.");return;}
 if(idx==13&&arc_anchors!=3){say("STABILIZE BOTH TIME ANCHORS BEFORE ANSWERING.");return;}
 /* The World Tree supports three equally valid original player paths. */
 if(idx==5){arc_route=selected;arc_solved=1;
  say(selected==1?"THE WORLD TREE OPENS A UNITY ROAD.":
   selected==2?"THE TREE OPENS A STRENGTH ROAD.":"THE TREE OPENS A DISCOVERY ROAD.");
 }else if(selected==ARC_ANSWER[idx]){
  arc_solved=1;say(ARC_PASSED[idx]);
 }else{say("THE SYMBOLS DO NOT AGREE. TRY AGAIN.");return;}
 /* A solved gate can release a boss or open a puzzle reward, never auto-complete. */
 spawn_monsters();save_game();
}
static void arc_interact(u8 t){int idx;u16 bit;
 if(t==TR_ARC_ENTER){arc_enter();return;}
 if(t==TR_ARC_EXIT){arc_return();return;}
 if(t==TR_ARC_EPILOGUE){
  say(ending==1?"OPEN: NEW PATHS LINK THE WORLDS. YOUR COMPANIONS CAN ROAM.":
      ending==2?"PRESERVE: THE OLD FORESTS AND THEIR MEMORIES STAY ROOTED.":
      "WANDER: THE SHIP FOLLOWS UNCERTAIN STARS. THE FELLOWSHIP FOLLOWS.");
  return;
 }
 if(!ARC_IS_ROOM)return;
 idx=(int)current_room-ARC_FIRST_ROOM;bit=(u16)(1u<<idx);
 if(t>=TR_ARC_PETAL_W && t<=TR_ARC_PETAL_U){
  if(idx!=7 || arc_progress!=7){say("THIS PETAL BELONGS TO AN EARLIER TRIAL.");return;}
  if(arc_petals>=3){say("THE THREE PETALS ARE ALREADY JOINED.");return;}
  if(t!=(u8)(TR_ARC_PETAL_W+arc_petals)){
   say("THE ORDER IS WISDOM, THEN COURAGE, THEN UNITY.");return;
  }
  arc_petals++;tone((u16)(1050+arc_petals*180));
  say(arc_petals==1?"WISDOM AWAKENS. SEEK THE COURAGE PETAL.":
   arc_petals==2?"COURAGE AWAKENS. FIND THE LAST UNITY PETAL.":
   "UNITY SHINES. THE CENTRAL SHRINE NOW LISTENS.");
  save_game();return;
 }
 if(t==TR_ARC_ANCHOR_W || t==TR_ARC_ANCHOR_E){
  u8 anchor=(u8)(t==TR_ARC_ANCHOR_W?1:2);
  if(idx!=13 || arc_progress!=13){say("THIS CLOCK BELONGS TO ANOTHER HOUR.");return;}
  if(arc_anchors&anchor){say("THIS TIME ANCHOR IS ALREADY STABLE.");return;}
  arc_anchors|=anchor;
  say(arc_anchors==3?"BOTH TIMELINES SYNCHRONIZE. RETURN TO THE SHRINE.":
   "ONE TIMELINE HOLDS. FIND THE OTHER ANCHOR.");
  tone(1330);save_game();return;
 }
 if(t==TR_ARC_SECRET){
  if(arc_secret_mask & bit){say("THIS HIDDEN CACHE HAS BEEN CLAIMED.");return;}
  arc_secret_mask|=bit;
  inv[ITEM_SHARD]=(u8)mini(99,inv[ITEM_SHARD]+2+
   ((arc_progress>=6&&arc_route==3)?1:0));
  say("A HIDDEN CACHE HOLDS TWO STAR SHARDS.");save_game();return;
 }
 if(t==TR_ARC_TRIAL){
  if(idx<arc_progress){say("THIS CHAPTER HAS BEEN RESTORED.");return;}
  if(idx>arc_progress){say("THE EARLIER PAGE MUST BE RESOLVED.");return;}
  if(arc_solved){say(ARC_PASSED[idx]);return;}
  if(idx==7&&arc_petals!=3){say("FIND 3 PETALS: WEST, NORTH, EAST.");return;}
  if(idx==13&&arc_anchors!=3){say("STABILIZE BOTH CHRONO ANCHORS.");return;}
  arc_pending=1;say(ARC_RIDDLES[idx]);return;
 }
 if(t==TR_ARC_BOSS){
  if(!(ARC_BOSSES&bit)){say("NO GUARDIAN WATCHES THIS CROSSING.");return;}
  if(idx!=arc_progress || !arc_solved){say("THE RUNE MUST BE UNDERSTOOD FIRST.");return;}
  if(arc_boss_done){say("THIS GUARDIAN HAS MADE ITS CHOICE.");return;}
  if(!enemies[8].active)spawn_monsters();
  if(enemies[8].active)battle_enter(8);else say("THE GUARDIAN HAS DEPARTED.");
  return;
 }
 if(t==TR_ARC_REWARD){
  if(idx<arc_progress){say("THE RELIC IS ALREADY IN YOUR JOURNAL.");return;}
  if(idx!=arc_progress){say("FOLLOW THE PREVIOUS CHAPTERS FIRST.");return;}
  if(!arc_solved){say("ANSWER THE CENTRAL SHRINE BEFORE TAKING THIS RELIC.");return;}
  if((ARC_BOSSES&bit)&&!arc_boss_done){
   say("THE AREA GUARDIAN STILL WATCHES OVER THIS RELIC.");return;
  }
  /* GUARANTEED progression reward; not dependent on RNG loot slots. */
  arc_progress=(u8)(idx+1);arc_guardians_mask|=(1u<<idx);
  if(idx==15)arc_guardians_mask|=(1u<<16);
  inv[ITEM_SHARD]=(u8)mini(99,inv[ITEM_SHARD]+2);
  if((idx%4)==3)inv[ITEM_ETHER]=(u8)mini(99,inv[ITEM_ETHER]+1);
  credits=(u8)mini(255,credits+6+(idx%4)*3);
  add_xp((u16)(15+idx*3));
  cosmos.trust=(u8)mini(255,cosmos.trust+3);
  arc_solved=0;arc_boss_done=0;arc_pending=0;
  if(idx==15){say("CITADEL RESTORED. ALL 17 GUARDIAN DISCIPLINES ARE DISCOVERABLE.");}
  else say("CHAPTER CLEARED. A GUARDIAN JOINS THE FELLOWSHIP.");
  tone((u16)(1430+idx*16));save_game();return;
 }
 if(t==TR_ARC_NEXT){
  if(idx>=arc_progress && arc_progress<ARC_STAGES){say("RESTORE THIS CHAPTERS RELIC FIRST.");return;}
  if(idx==ARC_STAGES-1){arc_return();return;}
  if(idx+1>arc_progress){say("THE NEXT CHAPTER HAS NOT BEEN UNLOCKED.");return;}
  arc_solved=arc_boss_done=arc_pending=0;
  arc_room_change((u8)(current_room+1),31,52,"THE NEXT REGION IS ALIVE.");return;
 }
}
static void arc_generate_boss(void){int idx;
 if(!ARC_IS_ROOM)return;
 idx=(int)current_room-ARC_FIRST_ROOM;
 /* Regular authored habitat encounters; the boss stays tied to story state. */
 spawn_enemy(0,37,31,(u8)(idx%EN_COUNT),0);
 spawn_enemy(1,43,31,(u8)((idx+1)%EN_COUNT),0);
 if(idx==(int)arc_progress && arc_solved && !arc_boss_done &&
    (ARC_BOSSES&(1u<<idx))){
  spawn_enemy(8,48,24,(u8)((idx+2)%EN_COUNT),1);
  enemies[8].maxhp=(u8)mini(120,14+idx*3+player_level*2);
  enemies[8].hp=enemies[8].maxhp;
 }
}
static int arc_boss_defeated(Enemy *e){int idx;
 if(!ARC_IS_ROOM || e!=&enemies[8]|| !e->elite)return 0;
 idx=(int)current_room-ARC_FIRST_ROOM;
 if(idx!=arc_progress || !arc_solved || !(ARC_BOSSES&(1u<<idx)))return 0;
 e->active=0;arc_boss_done=1;kill_count++;
 inv[ITEM_CORE]=(u8)mini(99,inv[ITEM_CORE]+1);
 credits=(u8)mini(255,credits+5);
 add_xp((u16)(15+idx*3));
 say("THE GUARDIAN FALLS. THE CHAPTER RELIC IS UNLOCKED.");
 tone(1440);save_game();return 1;
}
static int arc_boss_mercy(Enemy *e){int idx;LcResult joined;
 if(!ARC_IS_ROOM || e!=&enemies[8] || !e->elite)return 0;
 idx=(int)current_room-ARC_FIRST_ROOM;
 if(!(ARC_BOSSES&(1u<<idx)) || idx!=arc_progress)return 0;
 if(!(ARC_MERCY&(1u<<idx))){battle_notice="THIS GUARDIAN MUST BE DEFEATED.";return 1;}
 if(!inv[ITEM_ETHER]){battle_notice="ONE ETHER IS NEEDED TO HEAL THIS GUARDIAN.";return 1;}
 inv[ITEM_ETHER]--;e->active=0;arc_boss_done=1;arc_mercy_mask|=(u16)(1u<<idx);
 joined=lc_recruit_mercy((u8)((idx+2)%EN_COUNT),0,current_room);
 add_xp((u16)(12+idx*3));
 cosmos.trust=(u8)mini(255,cosmos.trust+15);
 battle_notice=joined==LC_FULL?"GUARDIAN SPARED. PARTY FULL.":
     "THE GUARDIAN CHOSE TO JOIN YOUR FELLOWSHIP.";
 save_game();return 1;
}
static void arc_open_epilogue(void){
 if(!postgame){say("THE EPILOGUE OPENS AFTER YOUR CROWN DECISION.");return;}
 arc_room_change(ARC_EPILOGUE_ROOM,31,52,
  ending==1?"OPEN: THE WORLDS CREATE NEW CROSSINGS.":
  ending==2?"PRESERVE: THE OLD WAYS STILL HAVE A HOME.":
  "WANDER: EVERY HORIZON IS YOURS TO EXPLORE.");
}
