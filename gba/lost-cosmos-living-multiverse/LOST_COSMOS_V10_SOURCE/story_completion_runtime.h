/* Native interactive adaptation. Nothing here writes emulator memory or
 * grants a victory from a global kill counter. Battle proof is the local actor. */
#ifndef LC_COMPLETION_RUNTIME_H
#define LC_COMPLETION_RUNTIME_H
enum {COMP_TEXT=1,COMP_TURN=2,COMP_BEAT=3,COMP_ANSWER=4,COMP_PEACE=5,COMP_TEAM=6,COMP_CHOICE=7,COMP_RESOLUTION=8};
static int completion_available(int i){
 if(i<0||i>=24||!(story_flags&ST_HEART))return 0;
 if(completion_done&(1u<<i))return 1;
 if(i&&!(completion_done&(1u<<(i-1))))return 0;
 switch(i){
 case 4:return arc_progress>=6;
 case 6:return arc_petals==3;
 case 7:return !!(story_flags&ST_DREAM);
 case 9:return !!(story_flags&ST_HEARTWOOD);
 case 10:return !!(v10_relic&RF_CLARITY);
 case 11:return !!(v10_relic&RF_PASSION);
 case 12:return (v10_relic&RF_TRIPLE)==RF_TRIPLE;
 case 13:return !!(v10_relic&RF_GROVE_RIDDLE);
 case 14:return !!(v10_relic&RF_EARTH);
 case 15:return !!((v10_relic&RF_EARTH)&&(story_flags&ST_DREAM));
 case 16:return !!(element_mask&2);
 case 17:return !!(element_mask&4);
 case 18:return element_mask==15;
 case 19:return !!(v10_relic&RF_FESTIVAL);
 case 20:return !!((story_flags&ST_VOID)&&g7_sigils==15);
 case 21:return !!((story_flags&ST_CHRONO)&&arc_anchors==3);
 case 22:return g7_pillars==3;
 case 23:return !!((story_flags&ST_LATTICE)&&g7_orbs==31);
 default:return 1;
 }
}
static const char *completion_requirement(int i){
 if(!(story_flags&ST_HEART))return "RECLAIM THE HEART IN CRAGSTONE FIRST.";
 if(i&&!(completion_done&(1u<<(i-1))))return "FINISH THE PREVIOUS LIVING CHAPTER FIRST.";
 switch(i){
 case 4:return "ATLAS: REACH AND CHOOSE AT THE WORLD TREE.";
 case 6:return "ATLAS: RESTORE ALL THREE PETALS AT THE PETAL GATE.";
 case 7:return "DREAM VEIL: COMPLETE WISDOM COURAGE AND UNITY.";
 case 9:return "HEARTWOOD: RECOVER THE ORIGINAL BALANCE CRYSTAL.";
 case 10:return "GLACIAL GROTTO: RECOVER CLARITY FROM THE FOUNTAIN.";
 case 11:return "EMBER CAVERNS: EARN PASSION FROM THE PHOENIX BOX.";
 case 12:return "EARN CLARITY PASSION AND CELESTIAL HARMONY SEPARATELY.";
 case 13:return "HOLLOW GROVE: SOLVE THE REAL MIRROR POOL RIDDLE.";
 case 14:return "HOLLOW GROVE: RESTORE ITS GUARDIAN AND EARN EARTH.";
 case 18:return "ELDORIA: EARTH WATER FIRE AND AIR MUST BE RESTORED.";
 case 19:return "DREAM FESTIVAL: FINISH THE ORIGINAL THREE CHIMES.";
 case 20:return "VOIDWARD EXPANSION: EARN ITS FOUR DISTINCT SIGILS.";
 case 21:return "TIDE AND CHRONO ANNEX: RESTORE THE HEART AND BOTH ANCHORS.";
 case 22:return "INFINITY EXPANSION: SECURE THREE PILLARS WITH REAL BATTLES.";
 case 23:return "CROWN AND FINAL EXPANSION: RESTORE LATTICE AND FIVE ORBS.";
 default:return "FOLLOW THE JOURNAL TO THE EARNED REALM PROOF.";
 }
}
static void completion_route(int ax,int ay,int bx,int by){int x,y;
 for(x=mini(ax,bx);x<=maxi(ax,bx);x++)for(y=ay-2;y<=ay+2;y++)map_put(x,y,T_PATH,1,C_FREE,0);
 for(y=mini(ay,by);y<=maxi(ay,by);y++)for(x=bx-2;x<=bx+2;x++)map_put(x,y,T_PATH,1,C_FREE,0);
}
static void completion_generate_map(void){int i,x,y,s=current_room-COMPLETION_FIRST_ROOM;
 int theme=COMPLETION_SCENES[s].theme,ground=theme==1?T_RUIN:theme==2?T_FLOOR:theme==4?T_MOON:theme==5?T_VOID:T_GRASS;
 map_fill(ground,0);map_border();set_world_palette(theme);
 /* Four authored environmental families: terraces, river crossings, broken
  * chambers and starlit shelves. Corridors are carved after solid scenery. */
 for(y=6;y<58;y+=8)for(x=6;x<58;x+=8){
  int h=(x*13+y*7+s*11)&7;
  if(h<3)map_rect(x,y,2+(s&1),3,theme==3?T_TREE:theme==2?T_CRYSTAL:theme==1?T_RUIN:T_PILLAR,3,C_WALL);
 }
 if(s%4==0)for(y=11;y<49;y++)for(x=23;x<27;x++)map_put(x,y,T_WATER,2,C_WALL,0);
 if(s%4==1)for(x=8;x<57;x++)for(y=28;y<31;y++)map_put(x,y,theme==1?T_LAVA:T_WATER,2,C_WALL,0);
 if(s%4==2){map_wall_box(20,8,23,18,4);map_wall_box(36,32,19,16,4);}
 if(s%4==3)for(y=8;y<52;y+=12)for(x=6;x<59;x++)if(x<25||x>38)map_put(x,y,T_HAZARD,7,C_HAZARD,0);
 completion_route(31,52,31,32);
 for(i=0;i<4;i++){
  const CompletionObjective*o=&COMPLETION_OBJECTIVES[s][i];
  completion_route(31,32,o->tx,o->ty);
  map_rect(o->tx-3,o->ty-3,7,7,theme==1?T_RUIN:T_FLOOR,1,C_FREE);
 }
 completion_route(31,32,55,10);completion_route(31,52,10,48);
 map_put(31,54,T_DOOR,5,C_FREE,TR_COMP_EXIT);
 map_put(55,10,T_DOOR,5,C_FREE,TR_COMP_NEXT);
 map_put(10,48,T_CRYSTAL,5,C_FREE,TR_COMP_CACHE);
 for(i=0;i<4;i++){
  const CompletionObjective*o=&COMPLETION_OBJECTIVES[s][i];int tile;
  tile=o->action==COMP_ACT_READ||o->action==COMP_ACT_STORY?T_ARCHIVE:
   o->action==COMP_ACT_BATTLE||o->action==COMP_ACT_BOSS_PHASE||o->action==COMP_ACT_MERCY?T_HAZARD:
   o->action==COMP_ACT_TALK?T_LANTERN:o->action==COMP_ACT_SWITCH?T_CIRCUIT:T_RUNE;
  map_put(o->tx,o->ty,tile,i<completion_step[s]?3:5,C_FREE,TR_COMP_OBJECTIVE+i);
  if(o->action==COMP_ACT_SEQUENCE){int n;
   for(n=0;n<3;n++){
    int xx=o->tx+(n-1)*4,yy=o->ty+4;
    completion_route(o->tx,o->ty,xx,yy);
    map_put(xx,yy,n==0?T_MOON:n==1?T_STAR:T_CRYSTAL,5,C_FREE,TR_COMP_SEQUENCE+n);
   }
  }
 }
 /* Restore ALL interactive tiles after ALL sequence routes have been carved.
  * The original path carver set trigger=TR_NONE over its own initiating rune,
  * making some new chapters impossible to complete by actual controller. */
 for(i=0;i<4;i++){
  const CompletionObjective*o=&COMPLETION_OBJECTIVES[s][i];int tile;
  tile=o->action==COMP_ACT_READ||o->action==COMP_ACT_STORY?T_ARCHIVE:
   o->action==COMP_ACT_BATTLE||o->action==COMP_ACT_BOSS_PHASE||o->action==COMP_ACT_MERCY?T_HAZARD:
   o->action==COMP_ACT_TALK?T_LANTERN:o->action==COMP_ACT_SWITCH?T_CIRCUIT:T_RUNE;
  map_put(o->tx,o->ty,tile,i<completion_step[s]?3:5,C_FREE,TR_COMP_OBJECTIVE+i);
  if(o->action==COMP_ACT_SEQUENCE)for(int n=0;n<3;n++){
   int xx=o->tx+(n-1)*4,yy=o->ty+4;
   map_put(xx,yy,n==0?T_MOON:n==1?T_STAR:T_CRYSTAL,5,C_FREE,TR_COMP_SEQUENCE+n);
  }
 }
 map_put(31,54,T_DOOR,5,C_FREE,TR_COMP_EXIT);
 map_put(55,10,T_DOOR,5,C_FREE,TR_COMP_NEXT);
 map_put(10,48,T_CRYSTAL,5,C_FREE,TR_COMP_CACHE);
}
static void completion_patch_portal(void){int i,x,y;
 if(COMP_IS_ROOM||current_layer!=1)return;
 for(i=0;i<24;i++)if(COMPLETION_SCENES[i].parent_world==current_world&&COMPLETION_SCENES[i].parent_room==current_room&&!(completion_done&(1u<<i))){
  /* The old atlas has a wide central spine; old settlement maps have clear
   * return roads. Do not replace an existing trigger, rune or reward. */
  x=30;y=(ARC_IS_ROOM||G7_IS_ROOM)?49:48;
  if(trigger[mi(x,y)]==TR_NONE&&collision[mi(x,y)]==C_FREE){map_put(x,y,T_CRYSTAL,5,C_FREE,TR_COMP_ENTER);return;}
  for(y=48;y<=51;y++)for(x=28;x<=34;x++)if(trigger[mi(x,y)]==TR_NONE&&collision[mi(x,y)]==C_FREE){map_put(x,y,T_CRYSTAL,5,C_FREE,TR_COMP_ENTER);return;}
 }
 /* Brindlemark is the persistent campaign hub, unlocked by the real Heart. */
 if(current_world==0&&current_room==2&&(story_flags&ST_HEART))map_put(31,49,T_CRYSTAL,5,C_FREE,TR_COMP_ENTER);
}
static void completion_warp(int i){
 if(!completion_available(i)){say(completion_requirement(i));return;}
 completion_pending=completion_sequence_active=0;completion_enemy_scene=completion_enemy_objective=255;
 current_world=0;current_room=(u8)(COMPLETION_FIRST_ROOM+i);current_layer=1;game_mode=MODE_SURFACE;
 player.x=31*8;player.y=51*8;player.hurt=0;generate_surface();refresh_camera();
 if(!(completion_seen&(1u<<i))){completion_seen|=1u<<i;say(COMPLETION_SCENES[i].arrival);}
 else say(COMPLETION_SCENES[i].name);
 save_game();
}
static void completion_objective_done(void){int s=completion_scene,o=completion_objective;
 if(!COMP_IS_ROOM||s!=current_room-COMPLETION_FIRST_ROOM||s>=24||o>=4||completion_step[s]!=o)return;
 completion_pending=completion_sequence_active=0;completion_sub[s]=0;
 completion_enemy_scene=completion_enemy_objective=255;completion_step[s]++;
 say(COMPLETION_SCENES[s].clue[o]);tone((u16)(1300+s*23+o*100));
 if(s==15&&o==3){element_mask|=2;}
 if(s==16&&o==3){element_mask|=4;}
 if(s==17&&o==3){element_mask|=8;if(element_mask==15)story_flags|=ST_ELEMENTS;}
 save_game();
 if(completion_step[s]==4){completion_pending=COMP_RESOLUTION;completion_page=0;}
}
static void completion_local_encounter(void){int s=completion_scene,o=completion_objective;
 const CompletionObjective*d=&COMPLETION_OBJECTIVES[s][o];int type=COMPLETION_SCENES[s].theme%EN_COUNT;
 if(s>=20)type=s==21?EN_TIDE:s==22?EN_CROWN:EN_VOID;
 completion_pending=0;completion_enemy_scene=(u8)s;completion_enemy_objective=(u8)o;
 spawn_enemy(8,d->tx,d->ty,type,1);
 /* Campaign health scales gently with earned attack, bounded for legitimate
  * first visits. Three boss phases have separate anticipation/recovery. */
 enemies[8].maxhp=(u8)clampi(12+s+(d->action==COMP_ACT_BOSS_PHASE?d->operand*5:0),12,58);
 enemies[8].hp=enemies[8].maxhp;enemies[8].windup=45;
 enemies[8].recover=(u8)(s>=20?30:45);
 say(s>=20?"WATCH THE SIGNAL. STRIKE AFTER ITS ATTACK. THE LOCAL PHASE MUST FALL.":"THE GUARDIAN SIGNALS ITS ATTACK. A SWORD R MAGIC L POTION. SELECT+A DUEL.");
}
static void completion_spawn(void){int s;
 completion_enemy_scene=completion_enemy_objective=255;
 if(!COMP_IS_ROOM)return;s=current_room-COMPLETION_FIRST_ROOM;
 /* Encounter activation is an interaction, including after interruption.
  * Leaving or loading never fabricates a completed phase. */
 if(completion_step[s]>=4)return;
}
static int completion_enemy_defeated(Enemy*e){
 if(!COMP_IS_ROOM||e!=&enemies[8]||completion_enemy_scene!=current_room-COMPLETION_FIRST_ROOM||completion_enemy_objective>=4)return 0;
 completion_scene=completion_enemy_scene;completion_objective=completion_enemy_objective;
 if(completion_step[completion_scene]!=completion_objective)return 0;
 e->active=0;kill_count++;add_xp((u16)(12+completion_scene));
 credits=(u8)mini(255,credits+4);drop_item_at(e->x,e->y,ITEM_POTION);
 completion_objective_done();return 1;
}
static const char* completion_riddle_prompt(int s){
 if(s==5)return "LEFT SHOOTING STAR UP CLOUD RIGHT MOON";
 if(s==7)return "LEFT NOON UP MIDNIGHT RIGHT TWILIGHT";
 if(s==8)return "LEFT WIND UP ECHO RIGHT RAIN";
 if(s==13)return "LEFT TAKE ALL UP PROTECT LIFE RIGHT RULE";
 return "LEFT JOIN LIGHT UP CLOSE BOOKS RIGHT BREAK MIRROR";
}
static int completion_riddle_answer(int s){return s==5?1:s==7?3:s==8||s==13?2:1;}
static void completion_perform(void){int s=completion_scene,o=completion_objective;
 int action=COMPLETION_OBJECTIVES[s][o].action;
 switch(action){
 case COMP_ACT_SWITCH:completion_pending=COMP_TURN;completion_setting=0;
  say("ROTATE WITH UP DOWN. SET THE RUNE TO THE INDICATED MARK. A CONFIRM B BACK.");return;
 case COMP_ACT_SEQUENCE:completion_pending=0;completion_sequence_active=1;
  say("WALK THE THREE RUNES: MOON STAR CRYSTAL. START AT THE MARKED FIRST RUNE.");return;
 case COMP_ACT_TIMING:completion_pending=COMP_BEAT;say("THE LIGHT PULSES. PRESS A WHEN IT REACHES THE BRIGHT CENTER. B BACK.");return;
 case COMP_ACT_RIDDLE:completion_pending=COMP_ANSWER;say(completion_riddle_prompt(s));return;
 case COMP_ACT_MERCY:completion_pending=COMP_PEACE;say("LEFT LISTEN AND RELEASE. RIGHT STAND AND DUEL. B LEAVE THE CHOICE OPEN.");return;
 case COMP_ACT_BATTLE:case COMP_ACT_BOSS_PHASE:completion_local_encounter();return;
 case COMP_ACT_SUPPORT:completion_pending=COMP_TEAM;say("LEFT ASK COSMOS TO HELP. RIGHT HOLD THE LINE YOURSELF. B RETURN LATER.");return;
 case COMP_ACT_RESTORE:
  if(s==10 &&!(v10_relic&RF_CLARITY)){say("THE MIRROR NEEDS THE CLARITY YOU EARNED IN THE REAL GROTTO.");completion_pending=0;return;}
  if(s==12 &&(v10_relic&RF_TRIPLE)!=RF_TRIPLE){say("THE LANTERN NEEDS YOUR THREE DISTINCT EARNED CRYSTALS.");completion_pending=0;return;}
  if(s==14 &&!(v10_relic&RF_EARTH)){say("THE BARRIER NEEDS THE EARTH CRYSTAL FROM THE HOLLOW GROVE.");completion_pending=0;return;}
  if(s==21 &&!(story_flags&ST_CHRONO)){say("THE OBELISKS NEED YOUR REAL CHRONOHEART.");completion_pending=0;return;}
  completion_pending=COMP_BEAT;say("HOLD THE RELIC STEADY. PRESS A AT THE BRIGHT CENTER TO COMPLETE THE RESTORATION.");return;
 case COMP_ACT_ORB:
  if(s==23&&g7_orbs!=31){completion_pending=0;say("THE FIVE ORBS MUST BE EARNED AT THE FIVE ORIGINAL PEDESTALS.");return;}
  completion_pending=COMP_BEAT;say("THE EARNED ORB ANSWERS THE OTHER LIGHTS. PRESS A WHEN THE LIGHTS MEET.");return;
 default:completion_objective_done();return;
 }
}
static void completion_apply_choice(int choice){int s=completion_scene,r,a;
 if(s>=24||choice<1||choice>3||completion_step[s]!=4||(completion_done&(1u<<s)))return;
 r=COMPLETION_CHOICES[s].reward[choice-1];a=COMPLETION_CHOICES[s].amount[choice-1];
 completion_choice[s]=(u8)choice;completion_done|=1u<<s;completion_pending=0;
 if(r==COMP_REWARD_TRUST)cosmos.trust=(u8)mini(255,cosmos.trust+a);
 else if(r==COMP_REWARD_GUARD)completion_guard=(u8)mini(4,completion_guard+a);
 else if(r==COMP_REWARD_ATTACK)completion_attack=(u8)mini(4,completion_attack+a);
 else if(r>=COMP_REWARD_ROOTLEAF&&r<=COMP_REWARD_VOID_DUST){int m=r==3?2:r==4?1:r==5?0:r==6?4:3;p4_material[m]=(u8)mini(99,p4_material[m]+a);}
 else if(r>=COMP_REWARD_POTION&&r<=COMP_REWARD_SHARD){int item=r-COMP_REWARD_POTION;inv[item]=(u8)mini(99,inv[item]+a);}
 else if(r==COMP_REWARD_MANA)player_mp=(u8)mini(max_mp,player_mp+a);
 add_xp((u16)(20+s));credits=(u8)mini(255,credits+3);
 player.hp=max_hp;player_mp=max_mp;
 if(s==1)story_flags|=ST_CITY;
 say(COMPLETION_CHOICES[s].reply[choice-1]);tone(1800);save_game();
}
static void completion_input(u16 keys){int s=completion_scene,o=completion_objective,choice=0;
 if(!COMP_IS_ROOM||s>=24){completion_pending=0;return;}
 if(keys&KEY_B){completion_pending=0;say("THE CHOICE REMAINS OPEN. YOUR EARNED OBJECTIVES ARE SAVED.");return;}
 if(completion_pending==COMP_RESOLUTION){if(keys&KEY_A){if(!completion_page){completion_page=1;say(COMPLETION_SCENES[s].resolution);}else{completion_pending=COMP_CHOICE;say(COMPLETION_CHOICES[s].prompt);}}return;}
 if(completion_pending==COMP_CHOICE){
  if(keys&KEY_LEFT)choice=1;else if(keys&KEY_UP)choice=2;else if(keys&KEY_RIGHT)choice=3;
  if(choice)completion_apply_choice(choice);return;
 }
 if(completion_step[s]!=o||o>=4){completion_pending=0;return;}
 if(completion_pending==COMP_TEXT){
  if(!(keys&KEY_A))return;
  if(completion_page<2){const CompletionExchange*x=&COMPLETION_EXCHANGES[s][completion_page];
   if(x->objective==o){completion_page++;say(x->answer);return;}completion_page++;
  }
  completion_perform();return;
 }
 if(completion_pending==COMP_TURN){
  if(keys&KEY_UP)completion_setting=(u8)((completion_setting+1)&3);
  if(keys&KEY_DOWN)completion_setting=(u8)((completion_setting+3)&3);
  if(keys&KEY_A){if(completion_setting==((s+o)&3))completion_objective_done();else say("THE LENS IS MISALIGNED. FOLLOW THE MARK AND TURN IT AGAIN.");}return;
 }
 if(completion_pending==COMP_BEAT){
  if(keys&KEY_A){int beat=(frame>>1)&31;if(beat>=12&&beat<=19)completion_objective_done();else say("A LITTLE EARLY OR LATE. WAIT FOR THE BRIGHT CENTER AND TRY AGAIN.");}return;
 }
 if(completion_pending==COMP_ANSWER){
  if(keys&KEY_LEFT)choice=1;else if(keys&KEY_UP)choice=2;else if(keys&KEY_RIGHT)choice=3;
  if(choice==completion_riddle_answer(s))completion_objective_done();else if(choice)say("THE REFLECTION WAITS. THINK ABOUT THE CLUE AND TRY AGAIN.");return;
 }
 if(completion_pending==COMP_PEACE){
  if(keys&KEY_LEFT){u8 species=s==9?6:s==10?7:3;LcResult result=lc_add_wild(&lc_party,species,0x10800000u+(u32)s);
   if(result==LC_OK){lc_party.slots[lc_party.count-1].bond=80;p4_record_species(species);}
   cosmos.trust=(u8)mini(255,cosmos.trust+8);completion_objective_done();
  }else if(keys&KEY_RIGHT)completion_local_encounter();return;
 }
 if(completion_pending==COMP_TEAM){
  if(keys&(KEY_LEFT|KEY_RIGHT)){
   if(keys&KEY_LEFT){cosmos.trust=(u8)mini(255,cosmos.trust+2);player.hp=(u8)mini(max_hp,player.hp+2);}
   if(s==3||s==14)completion_local_encounter();else{completion_pending=COMP_BEAT;say("KEEP THE GROUP IN TIME. PRESS A WHEN THE LIGHT REACHES THE CENTER.");}
  }return;
 }
}
static void completion_interact(u8 t){int s=current_room-COMPLETION_FIRST_ROOM,i;
 if(t==TR_COMP_ENTER){
  for(i=0;i<24;i++)if(!(completion_done&(1u<<i))){completion_warp(i);return;}completion_warp(23);return;
 }
 if(!COMP_IS_ROOM)return;
 if(t==TR_COMP_EXIT){const CompletionScene*d=&COMPLETION_SCENES[s];
  completion_pending=completion_sequence_active=0;completion_enemy_scene=completion_enemy_objective=255;
  current_world=d->parent_world;current_room=d->parent_room;current_layer=1;game_mode=MODE_SURFACE;
  player.x=31*8;player.y=49*8;generate_surface();
  if(blocked_px(player.x,player.y)){player.x=31*8;player.y=52*8;}
  refresh_camera();say("YOUR EARLIER CHAPTER REMAINS. THE JOURNAL KEEPS YOUR LIVING THREAD.");save_game();return;
 }
 if(t==TR_COMP_NEXT){
  if(!(completion_done&(1u<<s))){
   if(completion_step[s]==4){completion_scene=(u8)s;completion_pending=COMP_CHOICE;say(COMPLETION_CHOICES[s].prompt);}
   else say("COMPLETE THE FOUR MARKED OBJECTIVES BEFORE CROSSING THIS CHAPTER.");return;
  }
  if(s==23){say("THE FULL LIVING THREAD IS RESTORED. RETURN TO THE CROWN FOR YOUR OWN ENDING.");return;}
  completion_warp(s+1);return;
 }
 if(t==TR_COMP_CACHE){
  if(completion_cache&(1u<<s)){say("THIS CACHE WAS ALREADY GIVEN TO YOUR FELLOWSHIP.");return;}
  completion_cache|=1u<<s;inv[ITEM_POTION]=(u8)mini(99,inv[ITEM_POTION]+1);
  inv[ITEM_ETHER]=(u8)mini(99,inv[ITEM_ETHER]+1);p4_material[s%5]=(u8)mini(99,p4_material[s%5]+1);
  say("A LOCAL SUPPLY CACHE: POTION ETHER AND ONE BIOME MATERIAL. CLAIMED ONCE.");save_game();return;
 }
 if(t>=TR_COMP_SEQUENCE&&t<TR_COMP_SEQUENCE+3){int n=t-TR_COMP_SEQUENCE;
  if(!completion_sequence_active||completion_scene!=s||completion_objective>=4)return;
  i=completion_sub[s];
  if(n==((s+completion_objective+i)%3)){completion_sub[s]++;tone((u16)(950+n*200));
   if(completion_sub[s]==3)completion_objective_done();else{say("THE FIRST NOTE HOLDS. WALK TO THE NEXT RUNE IN THE CYCLE.");save_game();}
  }else{completion_sub[s]=0;say("THE NOTES LOST THEIR ORDER. BEGIN AT THE MARKED FIRST RUNE AGAIN.");save_game();}return;
 }
 if(t>=TR_COMP_OBJECTIVE&&t<TR_COMP_OBJECTIVE+4){int o=t-TR_COMP_OBJECTIVE;
  if(completion_done&(1u<<s)){say(COMPLETION_SCENES[s].resolution);return;}
  if(completion_step[s]==4){completion_scene=(u8)s;completion_pending=COMP_CHOICE;say(COMPLETION_CHOICES[s].prompt);return;}
  if(completion_step[s]!=o){say(o<completion_step[s]?"THIS OBJECTIVE IS ALREADY EARNED.":"FOLLOW THE JOURNALS CURRENT OBJECTIVE FIRST.");return;}
  if(completion_enemy_scene==s&&completion_enemy_objective==o&&enemies[8].active){say("THE LOCAL ENCOUNTER IS STILL ACTIVE. EARN ITS RESOLUTION BEFORE CONTINUING.");return;}
  completion_scene=(u8)s;completion_objective=(u8)o;completion_page=0;completion_pending=COMP_TEXT;
  for(i=0;i<2;i++)if(COMPLETION_EXCHANGES[s][i].objective==o){completion_page=(u8)i;say(COMPLETION_EXCHANGES[s][i].line);return;}
  completion_page=2;say(COMPLETION_SCENES[s].clue[o]);return;
 }
}
static void completion_draw_ui(void){int s,i;
 if(!COMP_IS_ROOM)return;s=current_room-COMPLETION_FIRST_ROOM;
 ui_fill_rows(0,0,62,15);ui_text(1,0,"LIVING CHAPTER",13);ui_num(17,0,s+1,15);
 ui_text(21,0,"STEP",14);ui_num(27,0,mini(4,completion_step[s]+1),15);
 if(completion_pending){
  ui_fill_rows(18,19,62,15);
  if(completion_pending==COMP_TEXT||completion_pending==COMP_RESOLUTION)ui_text(2,18,"A CONTINUE    B PAUSE TALK",14);
  else if(completion_pending==COMP_TURN){ui_text(2,18,"TURN",14);ui_num(8,18,completion_setting,15);ui_text(13,18,"MARK",13);ui_num(19,18,(s+completion_objective)&3,15);ui_text(2,19,"UP DOWN ROTATE / A SET",15);}
  else if(completion_pending==COMP_BEAT){int beat=(frame>>1)&31;
   for(i=0;i<16;i++)ui_text(6+i,18,i==beat/2?"*":i>=6&&i<=9?"=":".",i>=6&&i<=9?13:14);
   ui_text(2,19,"A AT CENTER / B LEAVE",15);
  }else ui_text(2,19,"D-PAD CHOICE / B LEAVE",14);
 }else if(!dialogue_timer){ui_fill_rows(19,19,62,15);
  ui_text(1,19,completion_step[s]<4?COMPLETION_OBJECTIVES[s][completion_step[s]].name:
   (completion_done&(1u<<s))?"NORTH EAST GATE / NEXT CHAPTER":"VISIT A RUNE / CHOOSE YOUR PATH",14);
 }
}
#endif
