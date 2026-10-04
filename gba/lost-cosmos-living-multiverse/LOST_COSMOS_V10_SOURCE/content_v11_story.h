/* Act I, the Synapse Road. Additive to the eight-signal campaign.
   Flower tiles are wild sparks. The listener and Lys are new triggers.
   Evolution still uses level 12 / bond 55, then level 28 / bond 80. */
static const char* V11_TYPE_NAME[5]={"NEUTRAL","EMBER","TIDE","BLOOM","VOID"};
static const char* V11_MOVE_NAME[5][4]={
 {"STRIKE","BRACE","FOCUS","NUDGE"},
 {"EMBER HIT","CINDER","FORGE","FLARE"},
 {"TIDE HIT","RILL","WARD","DRIFT"},
 {"BLOOM HIT","ROOT","MEND","THORN"},
 {"VOID HIT","ARC","STEP","HUSH"}
};
static const u8 V11_MOVE_POWER[4]={12,8,18,6};
static const u8 V11_MOVE_ELEM[5][4]={
 {0,0,0,0},{1,1,1,1},{2,2,2,2},{3,3,3,3},{4,4,4,4}
};
static const char* v11_short_world(void){
 static const char* name[8]={"PRIME","REEF","CINDER","VERDANCE","PALE","RUST","UMBRAL","CROWN"};
 return name[v11_world()&7];
}
static const char* v11_act_goal(void){
 if(v11_story_flags&V11_SF_ENDING)return "ACT I RESTS. COSMOS STAYS.";
 if(v11_story_flags&V11_SF_QUIET)return "LISTENER WAITS AT CROWN.";
 if(v11_beacons==255)return "FACE THE QUIET. 3 ECHOES.";
 if(v11_world()==0&&!(v11_story_flags&V11_SF_BEFRIEND))return "ASK A SPARK IN THE FLOWERS.";
 if(v11_world()==0&&v11_rival_phase<2)return "LYS WAITS ON THE WEST SHELF.";
 return v11_signal_goal(v11_world());
}
static void v11_hp_bar(int x,int y,int cur,int max,int n,int pal){
 char bar[12];int i,filled;u32 c,m,nn;
 if(n<1)n=1;if(n>10)n=10;
 if(cur<0)cur=0;if(max<1)max=1;
 c=(u32)cur;m=(u32)max;nn=(u32)n;
 filled=(int)((c*nn)/m);
 if(cur>0&&filled<1)filled=1;
 if(filled>n)filled=n;
 for(i=0;i<n;i++)bar[i]=(char)(i<filled?'=':'-');
 bar[n]=0;ui_text(x,y,bar,pal);
}
static void v11_story_sync(void){
 if((v11_story_flags&V11_SF_INTRO)&&v11_act<1)v11_act=1;
 if((v11_story_flags&V11_SF_BEFRIEND)&&v11_act<2)v11_act=2;
 if((v11_story_flags&V11_SF_RIVAL)&&v11_act<3)v11_act=3;
 if(v11_beacons&&v11_act<3)v11_act=3;
 if(v11_beacons==255){v11_story_flags|=V11_SF_EIGHT;if(v11_act<4)v11_act=4;}
 if(v11_boss_done&512){v11_story_flags|=V11_SF_QUIET;if(v11_act<5)v11_act=5;}
 if((v11_story_flags&V11_SF_ENDING)&&v11_act<5)v11_act=5;
}
static void v11_story_boot(void){
 if(!(v11_story_flags&V11_SF_INTRO)){
  v11_story_flags|=V11_SF_INTRO;
  if(v11_act<1)v11_act=1;
  v11_message("ACT I. THE LATTICE IS A SYNAPSE. FIND THE LISTENER. ASK A SPARK.");
 }
 v11_story_sync();
}
static void v11_story_reseats(void){
 int i,w=v11_world();
 for(i=0;i<4;i++)map_put(V11_CACHE_X[i],V11_CACHE_Y[i],(v11_caches&(1u<<(w*4+i)))?T_RUIN:T_ARCHIVE,3,C_FREE,TR_V11_CACHE);
 map_put(32,55,T_DOOR,3,C_FREE,TR_V11_EXIT);
 map_put(54,52,T_DOOR,3,C_FREE,TR_V11_NEXT);
 map_put(30,53,T_FURNACE,3,C_FREE,TR_V11_CAMP);
 map_put(45,16,T_LANTERN,3,C_FREE,TR_V11_BEACON);
 map_put(32,10,T_CRYSTAL,5,C_FREE,TR_V11_CORE);
 map_put(27,30,T_RUNE,3,C_FREE,TR_V11_ECHO);
 map_put(32,32,T_PLANT,2,C_FREE,TR_V11_TRIAL);
 if(w==0||w==2||w==5||w==6)map_put(18,12,T_CRYSTAL,5,C_FREE,TR_V11_CORE);
 if(w==5){for(i=0;i<3;i++)map_put(28+i*4,14,(v11_forges&(1u<<i))?T_RUIN:T_FURNACE,3,C_FREE,TR_V11_FORGE);}
}
static void v11_story_place(void){
 int w=v11_world();
 /* Paths stay off the beacon, caches, camp, and the east gate. */
 v11_path(8,48,8,58);
 v11_path(32,30,58,18);
 v11_path(32,16,40,8);
 v11_path(32,48,8,46);
 if(w==0)v11_path(8,46,8,28);
 v11_story_reseats();
 map_put(8,58,T_FLOWER,2,C_FREE,0);
 map_put(58,18,T_FLOWER,2,C_FREE,0);
 map_put(40,8,T_FLOWER,2,C_FREE,0);
 map_put(8,46,T_LANTERN,3,C_FREE,TR_V11_LISTENER);
 if(w==0)map_put(8,28,T_RUNE,3,C_FREE,TR_V11_RIVAL);
}
static int v11_on_spark(void){
 int tx=clampi(player.x>>3,0,63),ty=clampi(player.y>>3,0,63);
 int block=(tx>=32)+((ty>=32)<<1);
 int tile=screenblock(BG_MAP_BASE+block)[(ty&31)*32+(tx&31)]&1023;
 return tile==T_FLOWER;
}
static int v11_player_aff(void){
 if(lc_party.count)return lc_party.slots[lc_party.active].affinity%5;
 return 1;
}
static int v11_type_super(int attack,int defend){
 return (attack==1&&defend==3)||(attack==3&&defend==2)||(attack==2&&defend==1);
}
static void v11_wild_finish(const char* text){
 v11_message(text);v11_wild=0;v11_wild_menu=0;v11_story_sync();save_game();
}
static int v11_story_befriend(void){
 u8 species;u32 seed;LcResult result;LcCreature* born;
 if(v11_wild_rival){v11_message("LYS WILL NOT GIVE UP HER SPARK.");return 0;}
 if(!v11_wild_max||v11_wild_hp*5>v11_wild_max*2){v11_message("NOT YET. WEAKEN THE SPARK, THEN BEFRIEND IT.");return 0;}
 species=v11_wild_species;
 if(species<1||species>8)return 0;
 seed=v9_next()^((u32)species<<16)^v11_ticks;if(!seed)seed=1;
 result=lc_add_wild(&lc_party,species,seed);
 if(result==LC_DUPLICATE)result=lc_add_wild(&lc_party,species,seed+1u);
 if(result==LC_FULL){v11_message("THE PARTY IS FULL. TWELVE FRIENDS IS THE LIMIT.");return 0;}
 if(result!=LC_OK){v11_message("THE SPARK KEPT ITS DISTANCE.");return 0;}
 lc_party.active=(u8)(lc_party.count-1);
 lc_party_sel=lc_party.active;
 born=&lc_party.slots[lc_party.active];
 born->bond=55;
 v11_fx_set(3,36);
 v11_story_flags|=V11_SF_BEFRIEND;
 v11_befriend_count=(u8)mini(255,v11_befriend_count+1);
 add_xp((u16)(28+species*4));
 v11_trust(4);
 v11_wild_finish(born->level>=12?"IT WALKS WITH YOU. BOND 55. OPEN PARTY TO EVOLVE.":"IT WALKS WITH YOU. BOND 55. EVOLVE AT LEVEL 12.");
 return 1;
}
static int v11_wild_retaliate(void){
 LcCreature* ally=lc_party.count?&lc_party.slots[lc_party.active]:0;
 int attack=12+v11_wild_species*2+(v11_wild_rival?8:0);
 int defense=ally?ally->defense:6;
 int affinity=ally?(ally->affinity%5):0;
 int damage=lc_damage((u8)mini(255,attack),(u8)mini(255,defense),v11_wild_aff,(u8)affinity);
 damage=maxi(1,(int)((u32)damage>>1));
 v11_fx_set(2,12);
 v11_take_hit(damage);
 if(!v11_hp){
  v11_wild=0;v11_wild_menu=0;v11_gameover=1;v11_choice=0;
  v11_message("THE SPARK WAS LOUDER. THE SIGNAL FADES.");
  return 1;
 }
 return 0;
}
static void v11_wild_strike(int move){
 LcCreature* ally=lc_party.count?&lc_party.slots[lc_party.active]:0;
 int affinity=v11_player_aff();
 int element=V11_MOVE_ELEM[affinity][move&3];
 int power=V11_MOVE_POWER[move&3];
 int attack=ally?ally->attack:14+player_level;
 int defense=10+v11_wild_species*2+(v11_wild_rival?8:0);
 int damage=lc_damage((u8)mini(255,attack),(u8)mini(255,defense),(u8)element,v11_wild_aff);
 int super=v11_type_super(element,v11_wild_aff);
 damage=maxi(1,(int)(((u32)damage*(u32)power)/12u));
 if(v11_wild_hp<=damage){
  v11_wild_hp=0;
  v11_spark_wins=(u8)mini(255,v11_spark_wins+1);
  if(ally&&ally->bond<100)ally->bond=(u8)mini(100,ally->bond+2);
  add_xp((u16)(v11_wild_rival?90:22+v11_wild_species*5));
  if(v11_wild_rival){
   v11_story_flags|=V11_SF_RIVAL;v11_rival_phase=2;v11_trust(6);
   v11_wild_finish(super?"SUPER EFFECTIVE. LYS LOWERS HER SPARK.":"LYS LOWERS HER SPARK. THE ROAD IS SHARED.");
  }else if(ally&&((ally->stage==0&&ally->level>=12&&ally->bond>=55)||(ally->stage==1&&ally->level>=28&&ally->bond>=80))){
   v11_wild_finish("IT YIELDS. OPEN PARTY. THIS FORM IS READY.");
  }else{
   v11_wild_finish(super?"SUPER EFFECTIVE. THE SPARK FLEES.":"THE SPARK FLEES. WEAKEN THE NEXT AND BEFRIEND IT.");
  }
  return;
 }
 v11_wild_hp=(u16)(v11_wild_hp-damage);
 if(v11_wild_retaliate())return;
 v11_fx_set(1,14);
 v11_wild=3;
 v11_message(super?"SUPER EFFECTIVE. IT ANSWERS.":"THE SPARK ANSWERS.");
}
static void v11_wild_begin(int rival){
 static const u8 table[8]={1,2,7,3,6,5,4,8};
 int species;
 v11_wild=1;v11_wild_menu=0;v11_wild_sel=0;v11_wild_rival=(u8)(rival?1:0);
 if(rival){species=5;v11_wild_max=(u16)(48+player_level*3);}
 else{
  species=table[v11_world()&7];
  if(v11_spark_wins&1)species=(species%8)+1;
  v11_wild_max=(u16)(18+species*4+player_level);
 }
 v11_wild_species=(u8)species;
 v11_wild_aff=(u8)((species-1)%5);
 v11_wild_hp=v11_wild_max;
 v11_wild=3;
 /* Both walk frames upload once, outside the battle draw, so a blink cannot stall vblank. */
 expand_obj32(V11_TILE_FOE,V108_SPECIES[species-1][0][0],0);
 expand_obj32(V11_TILE_FOE_B,V108_SPECIES[species-1][0][1],0);
 v11_message(rival?"LYS SENDS HER SKYSPARK.":"A SPARK RISES FROM THE FLOWERS.");
}
static void v11_wild_use_item(void){
 if(!v11_qty[70]){v11_wild=3;v11_message("NO POTION. THE CAMPFIRE WILL WAIT.");return;}
 v11_qty[70]--;v11_heal(20);
 if(v11_wild_retaliate())return;
 v11_wild=3;v11_message("POTION. THE SPARK STILL WATCHES.");
}
static void v11_wild_run(void){
 if(v11_wild_rival){v11_message("LYS BLOCKS THE PATH.");if(!v11_wild_retaliate())v11_wild=3;return;}
 v11_wild_finish("YOU STEPPED OUT OF THE FLOWERS.");
}
static void v11_wild_update(u16 newk){
 if(v11_wild==3){if(newk&(KEY_A|KEY_B)){v11_wild=1;v11_wild_menu=0;}return;}
 if(newk&(KEY_UP|KEY_DOWN))v11_wild_sel^=2;
 if(newk&(KEY_LEFT|KEY_RIGHT))v11_wild_sel^=1;
 v11_wild_sel&=3;
 if(v11_wild==2){
  if(newk&KEY_B){v11_wild=1;v11_wild_sel=0;return;}
  if(newk&KEY_A)v11_wild_strike(v11_wild_sel);
  return;
 }
 if(newk&KEY_B){v11_wild_run();return;}
 if(!(newk&KEY_A))return;
 if(v11_wild_sel==0){v11_wild=2;v11_wild_sel=0;return;}
 if(v11_wild_sel==1){if(!v11_story_befriend())v11_wild=3;return;}
 if(v11_wild_sel==2){v11_wild_use_item();return;}
 v11_wild_run();
}
static void v11_wild_choices(const char* a,const char* b,const char* c,const char* d){
 const char* slot[4];int i;slot[0]=a;slot[1]=b;slot[2]=c;slot[3]=d;
 for(i=0;i<4;i++){int x=(i&1)?16:2,y=13+(i>>1);
  ui_text(x,y,(i==v11_wild_sel)?">":" ",13);ui_text(x+2,y,slot[i],15);}
}
static void v11_wild_draw(void){
 int affinity=v11_player_aff();
 const char* foe=v11_wild_rival?"LYS SKYSPARK":ECO_NAMES[v11_wild_species-1];
 LcCreature* ally=lc_party.count?&lc_party.slots[lc_party.active]:0;
 u32 seed=ally?ally->seed:((u32)v11_wild_species*0x9E3779B9u);
 int blink=v11_anim_blink((u32)v11_wild_species*13u);
 int ax=20,ay=56,fx=148,fy=28;
 oam_hide_all();
 /* Opaque navy first. A transparent clear here let the map show through on torn frames. */
 ui_frame(0,19,15);
 ui_text(2,1,foe,13);ui_text(16,1,V11_TYPE_NAME[v11_wild_aff],14);
 v11_hp_bar(2,2,v11_wild_hp,v11_wild_max,10,15);
 if(v11_fx==1&&v11_fx_t){ax+=10;fx-=v11_fx_t;}
 if(v11_fx==2&&v11_fx_t)ax+=(v11_fx_t&2)?3:-3;
 fy+=v11_anim_bob((u32)v11_wild_species*17u)+(v11_fx==3&&v11_fx_t?-((v11_fx_t&4)?5:1):0);
 ay+=v11_anim_bob(seed);
 v11_fx_tick();
 oam_set32(2,fx,fy,blink?V11_TILE_FOE:(((frame>>4)&1)?V11_TILE_FOE_B:V11_TILE_FOE),5+v11_wild_species-1);
 oam_ui_portrait(2);
 oam_set32(0,16,36,272,0);oam_ui_portrait(0);
 if(ally&&ally->species>=1&&ally->species<=8){
  int av=v11_anim_blink(ally->seed)?0:((frame>>4)&1);
  oam_set(1,ax,ay,384+(ally->species-1)*24+mini(2,ally->stage)*8+av*4,5+ally->species-1,0);
  oam_ui_portrait(1);
  ui_text(2,8,ECO_NAMES[ally->species-1],14);ui_text(16,8,"LV",13);ui_num(19,8,ally->level,15);
 }else{ui_text(2,8,"ARIN",14);ui_text(8,8,"LV",13);ui_num(11,8,player_level,15);}
 v11_hp_bar(2,9,v11_hp,v11_max_hp(),8,13);
 ui_frame(11,19,15);
 if(v11_wild==2)v11_wild_choices(V11_MOVE_NAME[affinity][0],V11_MOVE_NAME[affinity][1],V11_MOVE_NAME[affinity][2],V11_MOVE_NAME[affinity][3]);
 else if(v11_wild==3)ui_wrap_text(13,v11_notice[0]?v11_notice:"THE SPARK WAITS.",15,3);
 else v11_wild_choices("FIGHT","BEFRIEND","POTION","RUN");
 ui_text(2,18,v11_wild==2?"A MOVE    B BACK":v11_wild==3?"A CLOSE":"A CHOOSE   B RUN",14);
}
static int v11_lore_is_ending(void){
 return v11_lore==1&&v11_world()==7&&(v11_story_flags&V11_SF_QUIET);
}
static const char* v11_lore_text(void){
 static const char* nerve[8]={
  "THE LATTICE IS A SYNAPSE. EIGHT WORLDS ARE NERVES. WEAKEN A FLOWER SPARK, THEN BEFRIEND IT.",
  "THE REEF SINGS UNDER THE WATER. CARRY ITS ECHO. BREAK THE TIDE ANCHORS BEFORE THE GOD.",
  "CINDER KEEPS EVERY FAILURE. WALK THE BRIDGES. THE MAW EATS ANYONE WHO STANDS STILL.",
  "THE GROVE ASKS FOR A GENTLE HAND. MEND THE ROOT. SPARKS HERE REMEMBER KINDNESS.",
  "THE WHITEOUT TAKES NAMES BEFORE FOOTPRINTS. WALK THE BRIDGES. KEEP THE BEACON.",
  "QUIET THE FORGES SO THE CORE CAN HEAR YOU. A SKY IS NOT A MACHINE'S PROPERTY.",
  "LISTEN BEFORE YOU STEP. AN ECHO CAN BE LAID TO REST, OR CARRIED. THE CHOICE IS YOURS.",
  "THE CROWN HOLDS ITS BREATH. LIGHT EVERY BEACON. FACE THE QUIET WITH THREE ECHOES."
 };
 if(v11_lore==2){
  return v11_lore_page?"PRESS A AGAIN ON THIS MARK TO BEGIN. I WILL NOT HAND YOU MY SPARK.":
   "I AM LYS. I HEARD THE SYNAPSE FIRST. MY SKYSPARK ANSWERS WHEN I CALL.";
 }
 if(v11_lore_is_ending()){
  return v11_lore_page?"LEVEL 12 AND BOND 55 OPEN THE NEXT FORM. LEVEL 28 AND BOND 80 OPEN THE LAST.":
   "ACT I RESTS. YOU CARRIED THE UNKNOWN. YOU DID NOT OWN IT. COSMOS STAYS.";
 }
 return nerve[v11_world()&7];
}
static void v11_lore_open(int kind){
 v11_lore=(u8)kind;v11_lore_page=0;
 if(kind==2&&v11_rival_phase<1)v11_rival_phase=1;
 if(v11_lore_is_ending()){v11_story_flags|=V11_SF_ENDING;v11_story_sync();save_game();}
}
static void v11_lore_update(u16 newk){
 if(newk&KEY_B){v11_lore=0;return;}
 if(!(newk&KEY_A))return;
 if(!v11_lore_page){v11_lore_page=1;return;}
 v11_lore=0;
}
static void v11_lore_draw(void){
 ui_frame(10,19,15);
 ui_text(2,11,v11_lore==2?"LYS":v11_lore_is_ending()?"ACT I":"LISTENER",13);
 ui_wrap_text(13,v11_lore_text(),15,4);
 ui_text(2,18,"A NEXT    B CLOSE",14);
}
