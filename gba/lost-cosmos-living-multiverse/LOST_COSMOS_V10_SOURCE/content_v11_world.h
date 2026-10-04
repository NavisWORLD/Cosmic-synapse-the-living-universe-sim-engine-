/* Eight additional native regions. Existing authored maps remain authoritative. */
static const char*V11_QUEST_NAMES[15]={"PRIME SIGNAL","REEF SIGNAL","CINDER SIGNAL","VERDANCE SIGNAL","PALE SIGNAL","MERIDIAN SIGNAL","UMBRAL SIGNAL","CROWN SIGNAL","ASTRID'S OATH","REPAIR THE BEACON","FIND THE ELDER","THE OUTCAST'S ROAD","LAY TO REST","HEARTWOOD TRIAL","THE BUILDER'S SET"};
static const char*V11_QUEST_GIVERS[15]={"MIRA","TIDE PRIEST ILYA","HALVOR","THORN MOTHER","JUNA","SEVEN","GLOAM GUIDE","CROWN SENESCHAL","ASTRID","MIRA","BRINDLE ELDER","SABLE","THE CONFESSOR","BRINDLE ELDER","THE TINKER'S WIDOW"};
static const char*V11_QUEST_VOICE[15]={
 "I WILL FIND THE RIFT, CARRY ITS ECHO, AND LIGHT THE BEACON.",
 "THE REEF STILL SINGS. THREE FOES, ONE ECHO, ONE RETURNING LIGHT.",
 "PIM SHOWED ME THE SAFE ASH. I WILL BRING ITS SIGNAL HOME.",
 "I WILL CROSS THE ROOTS GENTLY AND REMEMBER WHO LIVES HERE.",
 "THE ABBESS ASKED FOR HER NAME. I WILL CARRY IT THROUGH THE WHITEOUT.",
 "SEVEN WANTS A SKY. I WILL REPAIR THE LIGHT ABOVE THE MACHINES.",
 "THE GUIDE LISTENS. I WILL BRING AN ECHO OUT OF THE DARK.",
 "THE THRONE HAS WAITED. I WILL LIGHT THE LAST BEACON WITH COSMOS.",
 "ASTRID ASKED ME TO RETURN AFTER THREE PRIME VICTORIES.",
 "MIRA NEEDS A FOUND CORE AND THREE PRIME VICTORIES. THEN THE BEACON.",
 "I WILL FIND THE ELDER AT THE HEARTWOOD GROVE.",
 "SABLE KNOWS THE ROAD. I WILL MEET THE FIRST OUTCAST IN THE DEEP.",
 "I CAN LAY ONE CARRIED ECHO TO REST WITH THE CONFESSOR.",
 "THE GROVE ASKS FOR GENTLENESS. I WILL MEND THE WOUNDED ROOT.",
 "THE WIDOW'S WORKSHOP TEACHES THE HAND, GOGGLES, AND CLASP."};
static const u8 V11_THEME[8]={0,2,1,3,2,1,4,5};
static const u8 V11_CACHE_LOOT[8][8]={
 {1,26,15,40,50,51,70,71},{2,27,16,41,52,72,80,78},
 {3,28,17,42,53,73,80,78},{4,29,18,43,54,74,84,78},
 {5,30,19,44,55,75,64,85},{6,31,20,45,56,76,86,78},
 {7,32,21,57,77,87,48,78},{23,39,68,88,88,88,78,79}};
static const u8 V11_CACHE_X[4]={13,50,16,49},V11_CACHE_Y[4]={45,43,24,25};
static void v11_palette(void){int i;set_world_palette(V11_THEME[v11_world()]);
 if(v11_world()==4){ /* ice and snow have a distinct native palette */
  for(i=0;i<8;i++){BG_PALETTE[i*16+1]=RGB5(8,14,20);BG_PALETTE[i*16+2]=RGB5(15,23,28);
   BG_PALETTE[i*16+3]=RGB5(23,29,31);BG_PALETTE[i*16+4]=RGB5(29,31,31);}}
 if(v11_world()==5){for(i=0;i<8;i++){BG_PALETTE[i*16+1]=RGB5(8,7,7);
  BG_PALETTE[i*16+2]=RGB5(18,12,7);BG_PALETTE[i*16+3]=RGB5(27,18,9);BG_PALETTE[i*16+4]=RGB5(29,24,18);}}
 if(v11_world()==6&&(v11_field_light||v11_passive(57)))for(i=0;i<8*16;i++)BG_PALETTE[i]=brighter5(BG_PALETTE[i],6);
 for(i=0;i<16;i++)OBJ_PALETTE[14*16+i]=V11_FIELD_PALETTE[i];
 /* Five actual brightness levels affect background art, never text contrast. */
 if(v11_brightness!=3)for(i=1;i<12*16;i++)BG_PALETTE[i]=brighter5(BG_PALETTE[i],(v11_brightness-3)*2);
 lc_import_palette();
}
static void v11_actor_art(void){int i;for(i=0;i<v11_npc_count;i++)vram_copy32(OBJ_VRAM32+(128+i*16)*8,V11_FIELD_ART+v11_npc_id[i]*128,128);
 for(i=0;i<10;i++)if(enemies[i].active)vram_copy32(OBJ_VRAM32+(224+i*16)*8,V11_FIELD_ART+v11_enemy_id[i]*128,128);
}
static void v11_resume_art(void){v11_battle_pose=255;make_obj_tiles();lc_upload_import_art();
 if(V11_IS_ROOM){v11_palette();v11_actor_art();}else set_world_palette(current_world);}
static void v11_mark_seen(int id){if(id<0||id>=100)return;v11_encounters[id]=(u8)mini(255,v11_encounters[id]+1);}
static int v11_seen_count(void){int i,n=0;for(i=0;i<100;i++)n+=v11_encounters[i]!=0;return n;}
static void v11_bestiary_rewards(void){int n=v11_seen_count();static const u8 reward[4]={50,57,61,64};
 while(v11_best_reward<4&&n>=(v11_best_reward+1)*25){if(!v11_inventory_add(reward[v11_best_reward],1))break;v11_best_reward++;}}
static void v11_spawn_one(int slot,int id,int tx,int ty){Enemy*e=&enemies[slot];const V11Character*c=&V11_CHARACTERS[id];
 e->x=(s16)(tx*8);e->y=(s16)(ty*8);e->vx=e->vy=0;e->type=c->world%EN_COUNT;e->elite=c->kind>=2;
 e->active=1;e->hurt=e->windup=e->recover=0;e->damage=c->atk;e->hp=e->maxhp=(u8)mini(255,c->hp);
 v11_enemy_id[slot]=(u8)id;v11_enemy_hp[slot]=v11_enemy_max[slot]=c->hp;
}
static void v11_spawn(void){int i,n=0,elite=6,boss=9,w=v11_world();
 static const u8 x[6]={13,22,44,52,15,48},y[6]={39,34,40,29,22,48};
 clear_combat();for(i=30;i<70;i++)if(V11_CHARACTERS[i].world==w&&n<6){v11_spawn_one(n,i,x[n],y[n]);n++;}
 for(i=70;i<90;i++)if(V11_CHARACTERS[i].world==w&&elite<9){
  if(i==85&&!postgame&&!(v11_boss_done&256))continue;
  if(v11_elite_day[i-70]!=65535&&(u16)(v11_days-v11_elite_day[i-70])<3)continue;
  v11_spawn_one(elite,i,elite==6?15:elite==7?48:19,elite==6?16:elite==7?20:28);elite++;}
 for(i=90;i<100;i++)if(V11_CHARACTERS[i].world==w&&!(v11_boss_done&(1u<<(i-90)))){
  if(i==99&&(v11_beacons!=255||!(v11_boss_done&256)))continue;
  if(i==91){ /* Mirror at the west rift; Vesper remains the north arena. */
   if(elite<9)v11_spawn_one(elite++,i,18,12);continue;}
  if(i==99){if(elite<9)v11_spawn_one(elite++,i,45,12);continue;}
  v11_spawn_one(boss,i,32,14);
 }
}
static void v11_path(int x0,int y0,int x1,int y1){int x,y;for(x=mini(x0,x1);x<=maxi(x0,x1);x++)for(y=y0-1;y<=y0+1;y++)map_put(x,y,T_PATH,1,C_FREE,0);
 for(y=mini(y0,y1);y<=maxi(y0,y1);y++)for(x=x1-1;x<=x1+1;x++)map_put(x,y,T_PATH,1,C_FREE,0);}
static void v11_generate(void){int x,y,i,w=v11_world(),ground=(w==1?T_DUST:w==2?T_DUST:w==4?T_FLOOR:w==5?T_METAL:w==6?T_FLOOR:w==7?T_PAD:T_GRASS);
 v11_palette();npc_count=0;v11_npc_count=0;v11_visited|=(u8)(1u<<w);v11_quest_started|=(u16)(1u<<w);v11_unlock();
 for(y=0;y<64;y++)for(x=0;x<64;x++){
  int edge=x<3||x>60||y<3||y>60;int h=(x*37+y*53+x*y*3+w*41)&127;
  int t=edge?T_WALL:h<6?(w==5?T_RUIN:w==6?T_CRYSTAL:w==7?T_PILLAR:T_TREE):ground;
  map_put(x,y,t,t==T_TREE?2:0,edge?C_WALL:C_FREE,0);
 }
 /* Reference map landmarks: southwest village, central grove, northeast
    beacon; Verdance root maze/quiet apiary; Pale islands; Rust forge yards. */
 if(w==0||w==3){for(y=25;y<=39;y++)for(x=25;x<=39;x++){
  int dx=x-32,dy=y-32;if(dx*dx+dy*dy<42)map_put(x,y,T_FLOWER,2,C_FREE,0);
  if(dx*dx+dy*dy>=42&&dx*dx+dy*dy<58)map_put(x,y,T_TREE,2,C_WALL,0);}}
 if(w==1||w==4){for(y=7;y<55;y++)for(x=6;x<58;x++)if((x+y*2)%17<4)
  map_put(x,y,w==1?T_WATER:T_CRACK,2,C_WALL,0);
  for(y=18;y<50;y+=9)for(x=12;x<55;x++)map_put(x,y,T_BRIDGE,1,C_FREE,0);}
 if(w==2){for(y=7;y<55;y++)for(x=6;x<58;x++)if((x*3+y)%23<3)
  map_put(x,y,T_LAVA,2,C_HAZARD,0);}
 if(w==3){for(y=38;y<49;y+=4)for(x=36;x<56;x++)map_put(x,y,T_VINES,2,C_WALL,0);
  for(x=39;x<55;x+=7)for(y=36;y<51;y++)map_put(x,y,T_PATH,1,C_FREE,0);}
 if(w==5){for(y=7;y<50;y+=13)for(x=9;x<56;x++)map_put(x,y,T_WALL,1,C_WALL,0);
  for(x=15;x<55;x+=16)for(y=7;y<55;y++)map_put(x,y,T_CIRCUIT,3,C_FREE,0);}
 if(w==6){for(y=12;y<48;y+=12)for(x=7;x<58;x++)if(x%9<5)map_put(x,y,T_RUIN,5,C_WALL,0);}
 if(w==7){for(y=8;y<53;y++)for(x=28;x<=36;x++)map_put(x,y,T_PAD,3,C_FREE,0);
  for(y=12;y<49;y+=8){map_put(26,y,T_PILLAR,3,C_WALL,0);map_put(38,y,T_PILLAR,3,C_WALL,0);}}
 v11_path(32,54,32,10);v11_path(32,52,8,52);v11_path(32,52,56,52);v11_path(13,45,50,43);
 v11_path(16,24,49,25);v11_path(15,16,48,20);
 v11_path(18,12,45,12);v11_path(32,32,16,35);v11_path(32,32,45,16);
 v11_path(32,48,14,49);v11_path(32,48,51,43);v11_path(32,48,31,48);
 for(i=0;i<30&&v11_npc_count<6;i++)if(V11_CHARACTERS[i].world==w&&i!=26&&i!=28){
  int n=v11_npc_count++;static const u8 nx[6]={16,43,32,14,51,30},ny[6]={35,19,34,49,43,48};
  v11_npc_id[n]=(u8)i;v11_npc_x[n]=nx[n]*8;v11_npc_y[n]=ny[n]*8;
  v11_path(32,54,nx[n],ny[n]);
 }
 if(v11_npc_count<6){int n=v11_npc_count++;v11_npc_id[n]=(u8)(w==0&&v11_beacons==255?28:26);
  v11_npc_x[n]=31*8;v11_npc_y[n]=48*8;}
 v11_spawn();for(i=0;i<10;i++)if(enemies[i].active){int tx=enemies[i].x>>3,ty=enemies[i].y>>3;v11_path(32,54,tx,ty);}
 for(i=0;i<4;i++)v11_path(32,54,V11_CACHE_X[i],V11_CACHE_Y[i]);
 for(i=0;i<4;i++){map_put(V11_CACHE_X[i],V11_CACHE_Y[i],(v11_caches&(1u<<(w*4+i)))?T_RUIN:T_ARCHIVE,3,C_FREE,TR_V11_CACHE);}
 if(w==2){map_put(39,18,T_STAIRS,1,C_WALL,0);map_put(39,19,T_STAIRS,1,C_WALL,0);}
 map_put(32,55,T_DOOR,3,C_FREE,TR_V11_EXIT);map_put(54,52,T_DOOR,3,C_FREE,TR_V11_NEXT);
 map_put(30,53,T_FURNACE,3,C_FREE,TR_V11_CAMP);map_put(45,16,T_LANTERN,3,C_FREE,TR_V11_BEACON);
 v11_path(32,30,27,30);map_put(32,10,T_CRYSTAL,5,C_FREE,TR_V11_CORE);map_put(27,30,T_RUNE,3,C_FREE,TR_V11_ECHO);
 map_put(32,32,T_PLANT,2,C_FREE,TR_V11_TRIAL);
 if(w==0||w==2||w==5||w==6)map_put(18,12,T_CRYSTAL,5,C_FREE,TR_V11_CORE);
 if(w==5){for(i=0;i<3;i++)map_put(28+i*4,14,(v11_forges&(1u<<i))?T_RUIN:T_FURNACE,3,C_FREE,TR_V11_FORGE);}
 v11_actor_art();REG_BG0CNT=(u16)(2|(BG_TILE_CB<<2)|(BG_MAP_BASE<<8)|(3u<<14));
 REG_BG1CNT=(u16)((UI_TILE_CB<<2)|(UI_MAP_BASE<<8));REG_DISPCNT=MODE0|BG0_ENABLE|BG1_ENABLE|OBJ_ENABLE|OBJ_1D_MAP;
 location_banner=240;v11_dialogue=v11_shop=0;v11_notice[0]=0;world_build_reveal();
}
static void v11_enter(int world){if(world<0||world>7)return;current_world=0;current_room=(u8)(70+world);current_layer=1;
 game_mode=return_mode=MODE_SURFACE;player.x=32*8;player.y=54*8;cosmos.x=player.x+13;cosmos.y=player.y-12;
 if(!v11_visited){v11_hp=(u16)v11_max_hp();v11_mp=(u16)v11_max_mp();v11_buddy_hp=(u16)v11_max_hp();}
 v11_hp=(u16)mini(v11_max_hp(),v11_hp);v11_mp=(u16)mini(v11_max_mp(),v11_mp);
 make_obj_tiles();lc_upload_import_art();generate_surface();refresh_camera();save_game();
}
static void v11_leave(void){current_world=0;current_room=2;current_layer=1;game_mode=return_mode=MODE_SURFACE;
 player.x=34*8;player.y=44*8;cosmos.x=player.x+13;cosmos.y=player.y-12;v11_resume_art();generate_surface();refresh_camera();save_game();}
static void v11_cache(void){int i,w=v11_world(),idx=0,best=999,need=0,a,b;
 for(i=0;i<4;i++){int d=iabs(near_trigger_x-V11_CACHE_X[i])+iabs(near_trigger_y-V11_CACHE_Y[i]);if(d<best){best=d;idx=i;}}
 if(v11_caches&(1u<<(w*4+idx))){v11_message("I ALREADY REBUILT THIS CACHE.");return;}
 a=V11_CACHE_LOOT[w][idx*2];b=V11_CACHE_LOOT[w][idx*2+1];need=(!v11_qty[a])+(!v11_qty[b]&&a!=b);
 if(v11_slots_used()+need>v11_capacity()){v11_message("BAG FULL. DROP OR USE AN ITEM IN ITEMS. THIS CACHE WILL WAIT.");return;}
 v11_inventory_add(a,1);v11_inventory_add(b,1);v11_caches|=1u<<(w*4+idx);
 v11_scrap=(u16)mini(65535,v11_scrap+3);v11_herbs=(u8)mini(99,v11_herbs+1);
 map_put(V11_CACHE_X[idx],V11_CACHE_Y[idx],T_RUIN,3,C_FREE,TR_V11_CACHE);
 v11_message(V11_ITEMS[a].name);save_game();
}
static void v11_light_beacon(void){int w=v11_world();if(v11_beacons&(1u<<w)){v11_last_beacon=(u8)w;v11_message("THE SIGNAL IS LIT. COSMOS KNOWS THE WAY HOME.");return;}
 if(v11_world_kills[w]<3||!(v11_echo_found&(1u<<w))||!(v11_cores_found&(1u<<w))){v11_message("BRING THIS RIFT'S CORE AND ECHO. FACE THREE FOES. THE BEACON NEEDS A MEMORY.");return;}
 v11_beacons|=(u8)(1u<<w);v11_last_beacon=(u8)w;v11_quest_finish(w);
 if(w==0){v11_quest_finish(9);}if(v11_beacons==255){v11_inventory_add(69,1);v11_inventory_add(98,1);}
 v11_message("A RETURNING NAME. THE BEACON IS LIT. COSMOS LEANS AGAINST YOU.");v11_unlock();save_game();
}
static void v11_npc_open(int n){int id=v11_npc_id[n];v11_speaker=(u8)id;v11_dialogue=1;v11_dialogue_page=0;v11_dialogue_scroll=v11_dialogue_reveal=0;v11_choice=0;
 v11_npc_seen|=1u<<id;v11_mark_seen(id);v11_bestiary_rewards();
 if(id==0){v11_quest_started|=1u<<8;if(v11_world_kills[0]>=3)v11_quest_finish(8);}
 if(id==1)v11_quest_started|=1u<<9;
 if(id==2)v11_quest_finish(10);
 if(id==4)v11_quest_started|=1u<<11;
 if(id==29&&(v11_npc_seen&(1u<<4)))v11_quest_finish(11);
 if(id==11)v11_quest_started|=1u<<13;
 if(id==16){v11_hp=(u16)v11_max_hp();v11_mp=(u16)v11_max_mp();}
 if(id==18)v11_trust(2);
 if(id==19||id==27){v11_inventory_add(95,1);v11_quest_started|=1u<<14;}
 if(id==21)v11_quest_started|=1u<<12;
 v11_unlock();save_game();
}
static const char*V11_NPC_LINES[30]={
 "AN OATH IS A ROAD YOU KEEP WALKING. RETURN AFTER THREE PRIME VICTORIES. I WILL KNOW YOUR STEP.",
 "A FOUND CORE HAS A VOICE. BRING THIS RIFT'S CORE AND ECHO TO THE BEACON AFTER THREE VICTORIES.",
 "I REMEMBER YOUR NAME, ARIN. THE GROVE ASKS FOR A MENDED ROOT, NEVER A LOUDER SWORD.",
 "EVERY SALE IS A STORY. I KEEP THE PRICES FAIR FOR PEOPLE WHO KEEP COMING BACK.",
 "ERIDORIA CAST US OUT. GO FIND THE FIRST OUTCAST IN THE DEEP. THEN THIS ROAD WILL BE OURS.",
 "THE SPIRES HOLD THEIR BREATH. STRIKE THE TIDE ANCHORS WHEN THE DROWNED GOD FLOODS THE ARENA.",
 "MY BROTHER WENT DOWN WITH THE CHOIR. CARRY THEIR ECHO. YOU DO NOT HAVE TO CARRY IT ALONE.",
 "WE SING THE WAY THROUGH DROWNED STONE. THE TIDE IS LOUDER THAN THE GOD. BREAK ITS ANCHORS.",
 "A FORGE KEEPS THE SHAPE OF EVERY FAILURE. LET ME SEE WHAT YOU HAVE BUILT.",
 "THE ASH THAT LOOKS COOL MAY STILL BITE. THE BRIDGES ARE SAFE. THIS ROCK IS FOR COSMOS.",
 "STAND STILL AND THE MAW WILL EAT YOUR SHADOW. MOVE BETWEEN STRIKES. TRUTH COSTS ONE CREDIT.",
 "SHOW ME GENTLENESS. MEND THE ROOT AT THE GROVE. THE APIARY HAS A PLACE FOR EVERY SMALL THING.",
 "I STILL TRACK THE BEAST I LOST. WEAKEN A CREATURE, THEN TALK. A FRIEND CANNOT BE TAKEN.",
 "THE NOTE READS: TAKE WHAT HEALS. LEAVE THE FLOWERS. THE BEES HAVE WORK TO DO.",
 "MY LAUGH CRACKS THE ICE. WALK THE BRIDGES, ARIN. THE WHITEOUT TAKES NAMES BEFORE FOOTPRINTS.",
 "THE LAND I REMEMBER IS LARGER THAN MY HANDS. YOUR MAP FILLS AS I FADE. KEEP THE BEACON.",
 "MY NAME IS PALE ABBESS. YOUR WOUNDS ARE MENDED. THAT IS ALL I ASK YOU TO REMEMBER.",
 "I RESPECT A BUILDER. BRING SCRAP TO THE WIDOW. THE NAMING WALL IS FOR PEOPLE, NOT INVENTORY.",
 "SEVEN. I CHOSE IT. THE SKY BELONGS TO NO MACHINE, SO MAYBE IT CAN BELONG TO ME AS WELL.",
 "THE TOOLS ARE STILL OILED. TAKE THIS KIT. BUILD THE HAND, GOGGLES, AND CLASP IN THE WORKSHOP.",
 "LIGHT IS A QUESTION HERE. LISTEN BEFORE YOU MOVE. I CAN HEAR THE RIFT BEYOND THE MOTHS.",
 "A MEMORY HAS WEIGHT. IF YOU WISH, I WILL LAY ONE CARRIED ECHO TO REST. THE CHOICE IS YOURS.",
 "THE MOTHS CHOOSE WHAT TO FOLLOW. I SELL LITTLE LIGHTS. YOUR FRIEND ALREADY HAS ONE.",
 "I WAS A KING. THE DEEP OFFERED ME A THRONE THAT FIT MY REGRET. DO NOT TAKE ITS BARGAIN.",
 "THE CROWN REQUIRES THE Z KEY. VESPER CARRIES ITS LAST SIGNAL. I AM SORRY TO STILL BE HERE.",
 "ARIN. COSMOS. I KNOW YOUR NAMES BECAUSE SOMEONE REMEMBERED YOU BEFORE THE STARS WENT QUIET.",
 "THE SMALL ECHO HOLDS OUT ITS HAND. COSMOS SITS BESIDE IT. FOR A MOMENT, NO ONE NEEDS WORDS.",
 "THE PIECES ARE OLD. THE ASSEMBLY IS YOURS. KEEP WHAT YOU CAN MEND. LET SOME THINGS REST.",
 "IF EVERYONE'S HAPPY, NOBODY PRAYS. EIGHT LIGHTS ARE LIT. THERE IS STILL ROOM FOR A NINTH.",
 "THEY CAST ME OUT FIRST. I KEPT WALKING. SABLE WAS RIGHT: THE ROAD WAS NEVER THEIRS TO CLOSE."};
static void v11_npc_next(void){int id=v11_speaker;
 if(v11_dialogue_page==0){v11_dialogue_page=1;return;}
 if(id==3||id==6||id==8||id==13||id==17||id==22){v11_dialogue=0;v11_shop=1;v11_shop_sel=0;v11_shop_sell=0;return;}
 if(id==19||id==27){v11_dialogue=0;game_mode=MODE_PAUSE;return_mode=MODE_SURFACE;pause_page=41;v11_menu_reset();return;}
 if(id==21&&!(v11_quest_done&(1u<<12))){if(!v11_qty[94]){v11_message("NO CARRIED ECHO YET. THE MEMORY SITES WILL WAIT.");v11_dialogue=0;return;}
  if(v11_dialogue_page==1){v11_dialogue_page=2;v11_choice=0;return;}
  if(v11_choice==0){v11_qty[94]--;v11_quest_finish(12);v11_message("I LAID ONE ECHO TO REST. THE EMPTY SPACE HAS WEIGHT TOO.");save_game();}
 }
 if(id==10&&v11_credits){v11_credits--;v11_message("THE VOLCANO'S TRUTH COST ONE CREDIT. KEEP MOVING IN THE MAW'S ARENA.");save_game();}
 v11_dialogue=0;
}
static void v11_field_interact(u8 t){int w=v11_world();if(t==TR_V11_EXIT){v11_leave();return;}
 if(t==TR_V11_NEXT){if(!(v11_beacons&(1u<<w))){v11_message("LIGHT THIS BEACON FIRST. THE ROAD NEEDS ITS SIGNAL.");return;}
  if(w==7){v11_leave();return;}if(w==6&&!v11_qty[92]&&keys_found!=7){v11_message("THE CROWN DOOR NEEDS Z. VESPER HOLDS THE KEY.");return;}
  v11_enter(w+1);return;}
 if(t==TR_V11_CAMP){v11_days++;v11_day_ticks=0;v11_hp=(u16)v11_max_hp();v11_mp=(u16)v11_max_mp();v11_buddy_hp=(u16)v11_max_hp();
  v11_trust(2);v11_unlock();save_game();v11_message("WE RESTED THROUGH THE NIGHT. COSMOS KEPT WATCH. HP AND MP RESTORED.");return;}
 if(t==TR_V11_BEACON){v11_light_beacon();return;}
 if(t==TR_V11_CACHE){v11_cache();return;}
 if(t==TR_V11_CORE){int bit=w;if(near_trigger_x<24)bit=8+(w==0?0:w==2?1:w==5?2:3);
  if(v11_cores_found&(1u<<bit)){v11_message("THIS RIFT'S CORE HAS ALREADY BEEN CARRIED.");return;}
  if(v11_inventory_add(93,1)){v11_cores_found|=(u16)(1u<<bit);v11_message("A BROKEN SIGNAL CORE. TWELVE PIECES, NEVER A NEW THIRTEENTH.");save_game();}return;}
 if(t==TR_V11_ECHO){if(v11_echo_found&(1u<<w)){v11_message("I REMEMBER THE ONE WHO WAITED HERE.");return;}
  if(v11_inventory_add(94,1)){v11_echo_found|=(u8)(1u<<w);v11_message("I CARRY AN ECHO OF THE DEPARTED. COSMOS WALKS A LITTLE CLOSER.");v11_trust(3);save_game();}return;}
 if(t==TR_V11_FORGE){int n=clampi((near_trigger_x-28+1)/4,0,2);if(v11_forges&(1u<<n)){v11_message("THIS FORGE IS ALREADY QUIET.");return;}v11_forges|=(u8)(1u<<n);v11_scrap+=4;
  map_put(28+n*4,14,T_RUIN,3,C_FREE,TR_V11_FORGE);v11_message("THE FORGE IS QUIET. THE MERIDIAN CORE CANNOT REBUILD THIS ONE.");save_game();return;}
 if(t==TR_V11_TRIAL&&(w==0||w==3)){
  if(v11_quest_done&(1u<<13)){v11_message("THE MENDED ROOT REMEMBERS MY HANDS.");return;}
  if(v11_skill_known(20)&&v11_mp>=5){v11_mp-=5;v11_quest_finish(13);v11_message("I MENDED THE WOUNDED ROOT. THE GROVE ANSWERED GENTLY.");save_game();}
  else if(v11_qty[70]){v11_qty[70]--;v11_quest_finish(13);v11_message("A POTION FOR THE ROOT. ITS BRANCHES OPEN A QUIET ROAD.");save_game();}
  else v11_message("THE ROOT NEEDS MEND OR A POTION. A SWORD WILL NOT HELP.");return;}
 v11_message("COSMOS NUDGES YOUR HAND. IT IS LISTENING.");
}
static void v11_start_battle(int i);
static int v11_shop_input(u16 newk);
static void v11_draw_shop(void);
static int v11_use_skill(int id);
static void v11_update_field(u16 k,u16 newk){int dx=0,dy=0,i,t,speed=(k&KEY_B)?3:2;
 if(v11_gameover){if(newk&KEY_UP||newk&KEY_DOWN)v11_choice^=1;
  if(newk&KEY_A){if(v11_choice==0){load_game();v11_gameover=0;generate_surface();refresh_camera();}
   else{v11_gameover=0;intro=1;v10_has_save=(u8)save_valid();cinema_start(0,0);}}return;}
 if(v11_shop){v11_shop_input(newk);return;}
 if(v11_dialogue){if(newk&KEY_B){v11_dialogue=0;return;}
  if(v11_dialogue_page==2&&(newk&(KEY_UP|KEY_DOWN)))v11_choice^=1;
  if(newk&KEY_A)v11_dialogue_advance();return;}
 if(k&KEY_LEFT)dx=-speed;if(k&KEY_RIGHT)dx=speed;if(k&KEY_UP)dy=-speed;if(k&KEY_DOWN)dy=speed;
 if(dx&&dy){if(frame&1)dx=0;else dy=0;}move_player(dx,dy,speed==3);
 if(player.hurt)player.hurt--;buddy_tick();t=trigger_near();
 if(newk&KEY_A){if(t){v11_field_interact((u8)t);return;}
  for(i=0;i<v11_npc_count;i++)if(iabs(v11_npc_x[i]-player.x)+iabs(v11_npc_y[i]-player.y)<28){v11_npc_open(i);return;}
  i=nearest_battle_enemy(48);if(i>=0){v11_start_battle(i);return;}
  v11_message("COSMOS NUDGES YOUR HAND. IT MISSED YOU.");}
 if(newk&KEY_R){game_mode=MODE_PAUSE;return_mode=MODE_SURFACE;pause_page=28;v11_menu_reset();v11_sub=0;}
 if(newk&KEY_L){if(v11_qty[70]){v11_qty[70]--;v11_heal(20);save_game();v11_message("POTION USED. HP RESTORED.");}else v11_message("NO POTIONS. THE CAMPFIRE WILL WAIT.");}
 if(newk&KEY_SELECT){v11_use_skill(v11_skill_known(92)?92:30+1);}
}
static void v11_draw_field(void){int i;ui_clear();oam_hide_all();
 if(location_banner){ui_fill_rows(0,0,63,15);ui_text(1,0,V11_WORLDS[v11_world()],13);location_banner--;}
 ui_fill_rows(1,1,63,15);ui_text(1,1,"HP",14);ui_num(4,1,v11_hp,15);ui_text(7,1,"/",15);ui_num(8,1,v11_max_hp(),15);
 ui_text(13,1,"LV",13);ui_num(16,1,player_level,15);ui_text(20,1,"MP",14);ui_num(23,1,v11_mp,15);
 ui_fill_rows(18,19,63,15);ui_text(2,18,"A TALK/DUEL  START MENU",14);
 if(v11_track<15&&(((int)v11_ticks)/480)&1)ui_text(2,19,v11_track<8?"FIND CORE/ECHO; FACE 3 FOES":v11_track==8?"RETURN TO ASTRID AFTER 3":v11_track==11?"FIND THE FIRST OUTCAST":v11_track==12?"LAY AN ECHO TO REST":v11_track==13?"MEND THE WOUNDED ROOT":"FOLLOW THE JOURNAL",13);
 else ui_text(2,19,"B RUN  L POTION  R SKILLS",15);
 oam_set(0,player.x-cam_x-8,player.y-cam_y-12,576+(player.face*4+(player.anim&3))*4,0,0);
 oam_set(1,cosmos.x-cam_x-8,cosmos.y-cam_y-8,32+(cosmos.mood&3)*4,1,0);
 if(!v11_active_cosmos&&lc_party.count){LcCreature*c=&lc_party.slots[lc_party.active];if(c->species>=1&&c->species<=8){vram_copy32(OBJ_VRAM32+416*8,V108_SPECIES[c->species-1][mini(2,c->stage)][(frame>>4)&1],32);oam_set(42,cosmos.x-cam_x+7,cosmos.y-cam_y-8,416,5+c->species-1,0);}}
#if defined(LC_IMPORTED_COMPANION)
 if(!v11_active_cosmos&&lc_party.count&&lc_party.slots[lc_party.active].species>=LC_SPECIES_IMPORTED)
  lc_draw_import_field(42,cosmos.x-cam_x-14,cosmos.y-cam_y-18,cosmos.vx<0,0,lc_party.slots[lc_party.active].identity);
#endif
 for(i=0;i<10;i++)if(enemies[i].active){oam_set32(2+i,enemies[i].x-cam_x-16,enemies[i].y-cam_y-24,224+i*16,14);
  if(enemies[i].x-cam_x<-32||enemies[i].x-cam_x>272||enemies[i].y-cam_y<-32||enemies[i].y-cam_y>192)OAM16[(2+i)*4]=0x0200;}
 for(i=0;i<v11_npc_count;i++){int xx=v11_npc_x[i]-cam_x-16,yy=v11_npc_y[i]-cam_y-24; if(xx>-32&&xx<240&&yy>-32&&yy<160)oam_set32(16+i,xx,yy-(int)((frame>>5)&1),128+i*16,14);}
 if(v11_field_scout||v11_equipment[1]==49||v11_qty[97])for(i=0;i<4;i++)if(!(v11_caches&(1u<<(v11_world()*4+i)))){int x=(V11_CACHE_X[i]*8-cam_x)/8,y=(V11_CACHE_Y[i]*8-cam_y)/8;if(x>=0&&x<30&&y>=3&&y<18)ui_text(x,y,"*",13);}
 if(v11_gameover){ui_pause_canvas();ui_text(3,6,"THE SIGNAL FADES...",13);ui_text(5,11,v11_choice?"  RETRY":"> RETRY",15);
  ui_text(5,13,v11_choice?"> TITLE":"  TITLE",15);ui_text(4,17,"A CONFIRM",14);oam_set(1,164,72,32,1,0);oam_ui_portrait(1);return;}
 if(v11_dialogue){int id=v11_speaker;ui_frame(12,19,15);ui_text(2,12,V11_CHARACTERS[id].name,13);
  if(v11_dialogue_page==2){ui_wrap_text(13,"LAY ONE ECHO TO REST?",15,2);ui_text(2,16,v11_choice?"  LET IT REST":"> LET IT REST",14);ui_text(2,17,v11_choice?"> KEEP CARRYING":"  KEEP CARRYING",15);}
  else v11_dialogue_draw();
  ui_text(2,18,"A NEXT    B CLOSE",14);
  vram_copy32(OBJ_VRAM32+400*8,V11_BATTLE_ART+id*128,128);for(i=0;i<16;i++)OBJ_PALETTE[13*16+i]=V11_BATTLE_PALETTES[id*16+i];
  oam_set32(43,8,62,400,13);oam_ui_portrait(43);
 }else if(v11_notice[0]){ui_frame(13,19,15);ui_text(2,14,"ARIN'S JOURNAL",13);ui_wrap_text(15,v11_notice,15,3);}
 if(v11_shop){oam_hide_all();v11_draw_shop();}
}
