/* V11.1 encounters: no modification to the legacy Enemy ABI or combat rules. */
enum {VS_BURN=1,VS_FREEZE=2,VS_ROOT=4,VS_BLIND=8,VS_SLOW=16,VS_SILENCE=32,VS_CHARM=64};
static u8 v11_target=0,v11_move_turn=0,v11_last_action=255,v11_command_used=0,v11_tide_phase=0;
static int v11_enemy_def(void){int id=v11_enemy_id[battle_index];
 return id==37||id==54||id==60?8:id>=90?5+v11_world():id>=70?4+v11_world():id==56?4:0;}
static void v11_player_status(int status,int turns){
 if((status&VS_BURN)&&v11_passive(53))status&=~VS_BURN;
 if((status&VS_FREEZE)&&v11_passive(55))status&=~VS_FREEZE;
 if((status&VS_CHARM)&&v11_passive(74))status&=~VS_CHARM;
 v11_status|=(u8)status;if(status)v11_status_turn=(u8)maxi(v11_status_turn,turns);
}
static void v11_take_hit(int damage){if(damage<1||v11_invincible||v11_decoy)return;
 if(v11_guard){v11_guard--;v11_buddy_hp=(u16)maxi(0,v11_buddy_hp-damage);return;}
 if(v11_equipment[1]==27&&v11_world()==1||v11_equipment[1]==28&&v11_world()==2||v11_equipment[1]==30&&v11_world()==4)damage=damage*3/4;
 if(v11_hp<=damage&&v11_stand){v11_hp=1;return;}
 if(v11_hp<=damage&&v11_passive(59)&&!v11_second_wind){v11_second_wind=1;v11_hp=1;return;}
 if(v11_hp<=damage&&v11_charm(62)&&!v11_revived){v11_revived=1;v11_hp=(u16)maxi(1,v11_max_hp()/4);return;}
 v11_hp=(u16)maxi(0,v11_hp-damage);v11_ult_charge=(u8)mini(100,v11_ult_charge+maxi(1,damage/2));
 if(v11_equipment[1]==35&&v11_enemy_hp[battle_index])v11_enemy_hp[battle_index]=(u16)maxi(0,v11_enemy_hp[battle_index]-maxi(1,damage/10));
 if(v11_charm(54)&&(v9_next()%100)<5)v11_enemy_hp[battle_index]=(u16)maxi(0,v11_enemy_hp[battle_index]-v11_str());
}
static void v11_add(int id,int number){int i;for(i=0;i<number&&v11_add_count<3;i++){
 int n=v11_add_count++;v11_add_id[n]=(u8)id;v11_add_hp[n]=V11_CHARACTERS[id].hp;
 v11_mark_seen(id);
 }v11_enemy_buff=(u8)mini(20,v11_enemy_buff+1);}
static void v11_remove_add(int n){int i;if(n<0||n>=v11_add_count)return;
 for(i=n;i+1<v11_add_count;i++){v11_add_id[i]=v11_add_id[i+1];v11_add_hp[i]=v11_add_hp[i+1];}v11_add_count--;
 if(v11_enemy_id[battle_index]==70)v11_enemy_buff=(u8)mini(20,v11_enemy_buff+3);
}
static void v11_tide_anchors(void){v11_add_count=0;v11_add(53,2);v11_add_hp[0]=v11_add_hp[1]=35;
 v11_tide_phase++;v11_message("THE TIDE HAS TWO ANCHORS. BREAK THEM. THE GOD IS ONLY ITS SHADOW.");}
static int v11_element(int id){if(id==1||id==8||id==77)return 1;
 if(id==2||id==9||id==76)return 2;if(id==3||id==10||id==16||id==75||id==78)return 3;
 if(id==4||id==11||id==79)return 4;if(id==5||id==32)return 5;
 if(id==6||id==13||id==25||id==84)return 6;if(id==14||id==18||id==39)return 7;return 0;}
static int v11_damage_target(int damage,int element,int physical,int all){int id=v11_enemy_id[battle_index],i,total=0;
 if(damage<0)damage=0;
 if(v11_status&VS_BLIND&&physical&&(v9_next()%100)<45){v11_message("THE STRIKE LOST ITS WAY IN THE DARK.");return 0;}
 if(physical)damage=maxi(1,damage-v11_enemy_def());
 if(id==74&&element==1)damage=0;
 if(element==1&&v11_charm(53)||element==4&&v11_charm(55))damage=damage*115/100;
 if(element==7&&V11_CHARACTERS[id].world==6)damage=damage*150/100;
 if(v11_passive(58)&&v11_hp==v11_max_hp())damage=damage*110/100;
 if(v11_passive(67)&&v11_beacons&(1u<<v11_world()))damage=damage*115/100;
 if(id>=90&&v11_charm(68))damage=damage*115/100;
 if(!physical&&v11_passive(60)&&v11_equipment[0]<15)damage=damage*110/100;
 if(physical&&v11_passive(61)&&v11_equipment[0]>=15&&v11_equipment[0]<24)damage=damage*110/100;
 if(v11_echo_turns)damage+=18;
 if(v11_add_count&&(all||v11_target>0||!v11_enemy_hp[battle_index])){
  int start=all?v11_add_count-1:clampi(v11_target? v11_target-1:0,0,v11_add_count-1);
  for(i=start;i>=0;i--){int d=mini(damage,v11_add_hp[i]);v11_add_hp[i]=(u16)(v11_add_hp[i]-d);total+=d;
   if(!v11_add_hp[i])v11_remove_add(i);if(!all)break;}
  if(id==92&&!v11_add_count){int d=v11_enemy_max[battle_index]/3+1;
   v11_enemy_hp[battle_index]=(u16)maxi(0,v11_enemy_hp[battle_index]-d);
   if(v11_enemy_hp[battle_index])v11_tide_anchors();}
 }
 if((v11_target==0||all)&&v11_enemy_hp[battle_index]){
  int d=damage;if(id==92)d=0;if(id==96&&v11_forges!=7)d=0;
  if(id==56&&physical)v11_take_hit(maxi(1,d/10));
  d=mini(d,v11_enemy_hp[battle_index]);v11_enemy_hp[battle_index]=(u16)(v11_enemy_hp[battle_index]-d);total+=d;
  if(id==34&&element==1&&!v11_enemy_hp[battle_index]&&!v11_phase){v11_add(34,2);v11_phase=1;}
  if(id==84&&!physical)v11_take_hit(maxi(1,d/5));
 }
 v11_ult_charge=(u8)mini(100,v11_ult_charge+maxi(1,total/6));
 enemies[battle_index].hp=(u8)mini(255,v11_enemy_hp[battle_index]);return total;
}
static void v11_repair_all(void){int i;for(i=0;i<3;i++)v11_durability[i]=100;}
static void v11_clear_status(void){v11_status=v11_status_turn=0;}
static int v11_consume(int id){int w=v11_world();if(id<70||id>=90||!v11_qty[id])return 0;
 if(game_mode!=MODE_BATTLE&&(id==80||id==81||id>=84&&id<=87)){v11_message("THIS ITEM NEEDS A BATTLE.");return 0;}
 if(id==70)v11_heal(20);if(id==71)v11_mp=(u16)mini(v11_max_mp(),v11_mp+10);
 if(id==72)v11_heal(35);if(id==73){v11_heal(20);v11_status&=~VS_BURN;}
 if(id==74){if(game_mode==MODE_BATTLE)v11_regen=3;else v11_heal(50);}
 if(id==75)v11_mp=(u16)mini(v11_max_mp(),v11_mp+25);
 if(id==76)v11_durability[0]=(u8)mini(100,v11_durability[0]+50);
 if(id==77){v11_clear_status();v11_ward=3;}
 if(id==78)v11_hp=(u16)v11_max_hp();if(id==79||id==89){v11_hp=(u16)v11_max_hp();v11_mp=(u16)v11_max_mp();v11_buddy_hp=(u16)v11_max_hp();}
 if(id==80){v11_qty[id]--;game_mode=MODE_SURFACE;return_mode=MODE_SURFACE;v11_resume_art();save_game();return 2;}
 if(id==81){v11_flare=3;v11_buddy_hp=(u16)v11_max_hp();}
 if(id==82)v11_xp_boost=5;if(id==83)v11_repair_all();
 if(id==84)v11_damage_target(40,3,0,1);
 if(id==85){v11_damage_target(55,4,0,0);if((v9_next()%100)<40){v11_enemy_status|=VS_FREEZE;v11_enemy_status_turn=2;}}
 if(id==86)v11_damage_target(70,0,0,0);if(id==87)v11_decoy=2;
 if(id==88){if(v11_perm_hp>=6){v11_message("THE THREE CROWN APPLES HAVE ALREADY BEEN REMEMBERED.");return 0;}v11_perm_hp+=2;v11_heal(2);}
 v11_qty[id]--;v11_message(V11_ITEMS[id].description);
 if(game_mode!=MODE_BATTLE)save_game();(void)w;return 1;
}
static int v11_use_skill(int id){const V11Skill*s;int cost,power,element,dealt=0,all=0,field=game_mode!=MODE_BATTLE;
 if(id<0||id>=100||!v11_skill_known(id)){v11_message("THIS ABILITY HAS NOT BEEN LEARNED YET.");return 0;}
 s=&V11_SKILLS[id];cost=s->mp;power=s->power;element=v11_element(id);
 if(s->kind==2){v11_message("EQUIP PASSIVES IN THE SKILLS MENU.");return 0;}
 if(s->kind==3){if(field||v11_ult_charge<100){v11_message("THE ULT GAUGE NEEDS A FULL SIGNAL.");return 0;}
  if(id==89&&v11_stay_day==v11_days){v11_message("STAY WITH ME HAS BEEN USED TODAY. REST FIRST.");return 0;}}
 if(id>=30&&id<50){if(v11_bond()<s->bond){v11_message("COSMOS NEEDS A STRONGER BOND FOR THIS ABILITY.");return 0;}
  if(v11_charm(63))cost=maxi(0,cost-1);}
 if(id==48&&v11_ninth_day==v11_days){v11_message("THE NINTH BARK HAS BEEN USED TODAY.");return 0;}
 if(v11_status&VS_SILENCE&&s->kind==0){v11_message("SILENCE HOLDS YOUR SPELL. COSMOS CAN STILL ANSWER.");return 0;}
 if(id==33&&(field||v11_fetch_used)){v11_message("FETCH NEEDS A BATTLE DROP. ONCE PER BATTLE.");return 0;}
 if(id==18&&v11_judgment_used){v11_message("CROWN JUDGMENT IS ONCE PER BATTLE.");return 0;}
 if(field&&power&&id!=20&&id!=28&&id!=29&&id!=30&&id!=41){v11_message("THIS ABILITY NEEDS A BATTLE.");return 0;}
 if((id==47||id==98)&&v11_last_beacon==255){v11_message("NO LIT BEACON TO RECALL YET.");return 0;}
 if(v11_free_cast&&s->kind==0)cost=0;
 if(v11_mp<cost){v11_message("NOT ENOUGH MP. ETHER OR A CAMPFIRE CAN HELP.");return 0;}
 v11_mp=(u16)(v11_mp-cost);if(v11_free_cast&&s->kind==0)v11_free_cast=0;v11_message(s->description);
 if(s->kind==3){v11_ult_charge=0;if(id==89)v11_stay_day=v11_days;}
 if(id<20||id==25||id==27){
  if(v11_focus){power=power*150/100;v11_focus=0;}
  if(id==15&&v11_last_spell<30)power+=V11_SKILLS[v11_last_spell].power/2;
  all=id==7||id==8||id==9||id==12;
  dealt=v11_damage_target(power+v11_mag(),element,0,all);
  if(id==1||id==8){if((v9_next()%100)<35){v11_enemy_status|=VS_BURN;v11_enemy_status_turn=3;}}
  if(id==2||id==9){v11_enemy_status|=VS_SLOW;v11_enemy_status_turn=2;}
  if(id==3||id==10){v11_enemy_status|=VS_ROOT;v11_enemy_status_turn=2;}
  if(id==4&&(v9_next()%100)<35){v11_enemy_status|=VS_FREEZE;v11_enemy_status_turn=2;}
  if(id==5&&(v9_next()%100)<35){v11_enemy_status|=VS_FREEZE;v11_enemy_status_turn=1;}
  if(id==6){v11_enemy_status|=VS_BLIND;v11_enemy_status_turn=2;}
  if(id==11)v11_ward=2;if(id==13)v11_decoy=1;if(id==16)v11_heal(20);
  if(id==18)v11_judgment_used=1;if(id==19){v11_enemy_status|=VS_SILENCE;v11_enemy_status_turn=3;}
  if(id==25)v11_heal(dealt/2);if(id==27)v11_take_hit(20);
  if(v11_charm(61)&&(v9_next()%100)<10)v11_damage_target(power+v11_mag(),element,0,all);
  v11_last_spell=(u8)id;v11_last_power=(u8)mini(255,power);
 }
 if(id==20)v11_heal(30);if(id==21)v11_clear_status();if(id==22)v11_haste=3;
 if(id==23)v11_ward=3;if(id==24)v11_focus=1;
 if(id==26){u16 hp=v11_hp;v11_hp=(u16)mini(v11_max_hp(),v11_buddy_hp);v11_buddy_hp=hp;}
 if(id==28){v11_clear_status();v11_heal(15);}if(id==29){v11_repair_all();v11_heal(20);}
 if(id==30)v11_heal(10);if(id==31||id==42){v11_field_scout=1;}
 if(id==32){v11_damage_target(15,5,0,0);if((v9_next()%100)<35){v11_enemy_status|=VS_FREEZE;v11_enemy_status_turn=1;}}
 if(id==33){v11_fetch_used=1;v11_inventory_add(70,1);v11_message("COSMOS FETCHED A FALLEN POTION.");}
 if(id==34)v11_status&=~(VS_FREEZE|VS_BURN);if(id==35)v11_damage_target(25,0,0,1);
 if(id==36)v11_guard=1;if(id==37)v11_decoy=2;if(id==38)v11_free_cast=1;
 if(id==39)v11_damage_target(40+(v11_beacons&(1u<<v11_world())?15:0),7,0,0);
 if(id==40)v11_damage_target(55,0,0,0);if(id==41){v11_clear_status();v11_heal(25);}
 if(id==43)v11_damage_target(75,0,0,0);if(id==44)v11_trust(1);
 if(id==45)v11_invincible=1;if(id==46)v11_enemy_buff=0;
 if(id==47||id==98){v11_enter(v11_last_beacon);return 2;}
 if(id==48){v11_damage_target(100,0,0,0);v11_ninth_day=v11_days;}
 if(id==49){v11_guard=1;v11_trust(1);}
 if(id>=75&&id<=89){
  if(id==85){v11_repair_all();v11_heal(100);v11_buddy_hp=(u16)v11_max_hp();}
  else if(id==86)v11_stand=3;
  else if(id==87)v11_echo_turns=(u8)(3+(v11_passive(66)?2:0));
  else{v11_damage_target(power,element,0,id==76||id==79||id==80||id==88);
   if(id==78&&v11_enemy_id[battle_index]<70)v11_enemy_hp[battle_index]=0;
   if(id==79){v11_enemy_status|=VS_FREEZE;v11_enemy_status_turn=2;}
   if(id==80)v11_enemy_buff=0;}
 }
 if(id==90){v11_field_light^=1;if(V11_IS_ROOM)v11_palette();}
 if(id==91){int i;for(i=0;i<3;i++)v11_durability[i]=(u8)mini(100,v11_durability[i]+15);}
 if(id==92){v11_field_track=1;v11_message("TRACK IS ACTIVE. MAP / START SHOWS LOCAL FOES.");}
 if(id==93){if(v11_forage_day==(u8)v11_days){v11_message("I HAVE ALREADY FORAGED TODAY. LET THE WILDS REST.");return 0;}
  if(v11_inventory_add(74,1)){v11_forage_day=(u8)v11_days;v11_herbs=(u8)mini(99,v11_herbs+2);}}
 if(id==94||id==95){int x,y;for(y=0;y<64;y++)for(x=0;x<64;x++){
  int sb=BG_MAP_BASE+(x/32)+(y/32)*2;int tile=screenblock(sb)[(y&31)*32+(x&31)]&1023;
  if(id==94&&tile==T_WATER||id==95&&tile==T_STAIRS)collision[mi(x,y)]=C_FREE;}
 }
 if(id==96){v11_field_scout=1;v11_message("THE ECHO SAYS: A REMEMBERED NAME IS A RETURNING PATH.");}
 if(id==97){if(!v11_qty[95]){v11_message("ASSEMBLE NEEDS THE BUILDER'S KIT.");return 0;}game_mode=MODE_PAUSE;return_mode=MODE_SURFACE;pause_page=41;v11_menu_reset();}
 if(id==99){if(V11_IS_ROOM&&trigger_near()==TR_V11_CAMP)v11_field_interact(TR_V11_CAMP);
  else{v11_message("REST NEEDS A CAMPFIRE. COSMOS WILL KEEP WATCH.");return 0;}}
 if(field)save_game();return 1;
}
static void v11_battle_reward(int spared){int id=v11_enemy_id[battle_index],i,w=v11_world(),xp=100+w*35;
 Enemy*e=&enemies[battle_index];if(!e->active)return;e->active=0;
 if(!spared)kill_count++;v11_world_kills[w]=(u8)mini(255,v11_world_kills[w]+1);
 if(v11_world_kills[w]>=3)v11_quest[w]=(u8)maxi(3,v11_quest[w]);
 if(id>=70&&id<90){v11_elite_day[id-70]=v11_days;xp=280+w*40;
  if(w==6){int n=id==81?10:id==82?35:61;v11_inventory_add(n,1);}
  else v11_inventory_add(78,1);}
 if(id>=90){v11_boss_done|=(u16)(1u<<(id-90));xp=850+w*70;
  if(id==90){v11_grant(14,1);v11_grant(38,1);v11_grant(90,1);}
  if(id==91)v11_grant(13,1);if(id==92)v11_grant(91,1);
  if(id==97)v11_grant(92,1);if(id==98)v11_grant(68,1);if(id==99)v11_grant(89,1);
 }
 if(v11_charm(50))xp=xp*105/100;if(v11_xp_boost){xp*=2;v11_xp_boost--;}
 add_xp((u16)xp);v11_credits=(u16)mini(65535,v11_credits+(id>=90?100:id>=70?40:8+w*3)*(w==5&&v11_passive(56)?120:100)/100);
 if(id<70){v11_scrap=(u16)mini(65535,v11_scrap+1+(w==5?2:0));v11_herbs=(u8)mini(99,v11_herbs+(w==3));
  if(id==43)v11_inventory_add(75,1);else if(id==44)v11_inventory_add(56,1);else if(id==54)v11_inventory_add(2,1);
  else if((v9_next()%100)<(v11_passive(51)?45:35))v11_inventory_add(70+(w==1?2:w==2?3:w==3?4:w==4?5:w==5?6:w==6?7:0),1);
 }
 if(v11_passive(72)&&(v9_next()%100)<5)v11_hp=(u16)v11_max_hp();
 if(player_level>v11_buddy_hp)v11_buddy_hp=player_level;
 v11_trust(2);v11_bestiary_rewards();v11_unlock();
 for(i=0;i<3;i++)if(v11_equipment[i]!=255&&v11_durability[i])v11_durability[i]--;
 v11_message(spared?"WE LET THE CREATURE GO. THE ROAD HAS ROOM FOR BOTH OF US.":"VICTORY. XP AND CREDITS RECEIVED. COSMOS WAITS FOR YOU.");
 if(id==99){v11_story_flags|=V11_SF_QUIET;v11_message("THE QUIET RESTS. FIND THE LISTENER AT THE CROWN. ACT I CAN END.");}
 v11_story_sync();
 save_game();battle_phase=3;battle_timer=45;
}
static void v11_start_battle(int index){int id;if(index<0||index>9||!enemies[index].active)return;id=v11_enemy_id[index];
 if(id==99&&v11_qty[94]<3){v11_message("THE QUIET NEEDS THREE CARRIED ECHOES. THE DEAD CAN STILL ANSWER.");return;}
 expand_obj32(272,V108_PLAYER[4],0);v11_battle_pose=255;v11_fetch_used=0;battle_index=(u8)index;battle_cursor=0;battle_phase=0;battle_timer=0;game_mode=MODE_BATTLE;
 v11_battle_sub=v11_battle_sel=v11_turn=v11_target=v11_move_turn=0;
 v11_status=v11_status_turn=v11_enemy_status=v11_enemy_status_turn=0;
 v11_guard=v11_ward=v11_haste=v11_focus=v11_free_cast=v11_decoy=v11_regen=0;
 v11_revived=v11_second_wind=v11_invincible=v11_stand=v11_echo_turns=v11_enemy_buff=v11_phase=0;
 v11_last_spell=255;v11_last_action=255;v11_judgment_used=v11_add_count=v11_command_used=v11_flare=v11_tide_phase=0;
 v11_mark_seen(id);v11_bestiary_rewards();
 vram_copy32(OBJ_VRAM32+384*8,V11_BATTLE_ART+id*128,128);for(int i=0;i<16;i++)OBJ_PALETTE[13*16+i]=V11_BATTLE_PALETTES[id*16+i];
 if(id==92)v11_tide_anchors();else if(id==70)v11_add(52,2);else if(id==80||id==96)v11_add(61,2);
 v11_message(V11_CHARACTERS[id].description);tone(1150);
}
static void v11_end_battle(void){game_mode=return_mode=MODE_SURFACE;battle_phase=0;battle_timer=0;
 v11_status=v11_status_turn=0;v11_battle_sub=0;v11_resume_art();save_game();}
static void v11_turn_end(void){if(v11_status_turn&&!--v11_status_turn)v11_status=0;int id=v11_enemy_id[battle_index],i,damage=V11_CHARACTERS[id].atk+v11_enemy_buff,skip=0;
 v11_turn++;
 if(id==31&&v11_credits)v11_credits--;if(id==40)v11_player_status(VS_ROOT,1);
 if(id==45)v11_ward=0;if(id==46&&v11_enemy_hp[battle_index]*4<=v11_enemy_max[battle_index])damage+=8;
 if(id==47&&(v9_next()%100)<20)v11_player_status(VS_BLIND,2);
 if(id==49)v11_mp=(u16)maxi(0,v11_mp-2);
 if(id==53&&(v9_next()%100)<10)v11_player_status(VS_FREEZE,1);
 if(id==55){v11_take_hit(3);}if(id==57&&v11_enemy_hp[battle_index]*2<=v11_enemy_max[battle_index]&&!v11_phase){v11_add(30,2);v11_phase=1;}
 if(id==58&&(v9_next()%100)<25)damage+=6;
 if(id==59&&v11_turn%3==0||id==65&&v11_turn==1||id==66&&v11_enemy_hp[battle_index]*2<v11_enemy_max[battle_index])damage+=5;
 if(id==61){v11_enemy_hp[battle_index]=(u16)mini(v11_enemy_max[battle_index],v11_enemy_hp[battle_index]+5);}
 if(id==62)v11_take_hit(2);if(id==63){v11_buddy_hp=(u16)maxi(0,v11_buddy_hp-damage);damage/=2;}
 if(id==67){player.x=(s16)clampi(player.x-8,16,496);}
 if(id==71&&v11_enemy_hp[battle_index]*2<=v11_enemy_max[battle_index]&&!v11_phase){v11_add(33,2);v11_phase=1;}
 if(id==72)v11_add(34,1);if(id==73&&v11_turn%3==0)v11_enemy_buff=(u8)mini(20,v11_enemy_buff+2);
 if(id==74&&v11_turn%2)skip=1;if(id==75)v11_player_status(VS_ROOT,2);
 if(id==76&&v11_turn==1)damage+=8;
 if(id==77&&v11_enemy_hp[battle_index]*2<=v11_enemy_max[battle_index]&&!v11_phase){v11_player_status(VS_BLIND,2);v11_phase=1;}
 if(id==78&&v11_add_count)v11_enemy_buff=(u8)mini(10,v11_enemy_buff+1);
 if(id==79)v11_enemy_hp[battle_index]=(u16)mini(v11_enemy_max[battle_index],v11_enemy_hp[battle_index]+10);
 if(id==81&&v11_turn%3==1)v11_add(47,1);
 if(id==82||id==91){if(!(v11_enemy_status&VS_SILENCE))damage+=v11_last_power/5;}
 if(id==86)v11_player_status(VS_SLOW,2);
 if(id==87&&v11_last_action==battle_cursor)damage+=8;
 if(id==88&&v11_turn%4==1)v11_player_status(VS_SILENCE,3);
 if(id==89&&v11_turn%3==0&&v11_enemy_hp[battle_index]*2<v11_enemy_max[battle_index])v11_enemy_hp[battle_index]=(u16)mini(v11_enemy_max[battle_index],v11_enemy_hp[battle_index]+20);
 if((id==90||id==85)&&v11_enemy_hp[battle_index]*2<=v11_enemy_max[battle_index]&&!v11_phase){v11_phase=1;v11_enemy_buff+=4;damage+=4;v11_message("THE KING SHATTERS THE ARENA. COSMOS MOVES CLOSER.");}
 if(id==93&&!v11_move_turn)v11_take_hit(3);
 if(id==94)v11_enemy_hp[battle_index]=(u16)maxi(0,v11_enemy_hp[battle_index]-15);
 if(id==95&&v11_enemy_hp[battle_index]*3<=v11_enemy_max[battle_index]&&!v11_phase){v11_phase=1;v11_player_status(VS_FREEZE,1);v11_message("THE PALE KING STOLE YOUR NEXT TURN. COSMOS HELD YOUR SIGNAL.");}
 if(id==96){if(v11_forges!=7){v11_enemy_hp[battle_index]=v11_enemy_max[battle_index];if(v11_turn%3==0)v11_add(61,1);}
  else if(v11_enemy_hp[battle_index]*2<=v11_enemy_max[battle_index]&&!v11_phase){v11_phase=1;v11_add(61,2);}}
 if(id==97){v11_enemy_hp[battle_index]=(u16)maxi(0,v11_enemy_hp[battle_index]-8);damage+=v11_turn/4;}
 if(id==98&&v11_turn%4==0)v11_player_status(VS_CHARM,1);
 if(v11_enemy_status&VS_BURN)v11_enemy_hp[battle_index]=(u16)maxi(0,v11_enemy_hp[battle_index]-5);
 if(v11_enemy_status&VS_FREEZE)skip=1;
 if(v11_enemy_status&VS_ROOT||v11_enemy_status&VS_SLOW)damage=damage*3/4;
 if(v11_enemy_status&VS_BLIND&&(v9_next()%100)<40)skip=1;
 if(!skip){damage=maxi(1,damage-v11_def()/2-(v11_ward?4:0));if(battle_evade)damage=(damage+1)/2;
  if(v11_equipment[1]==40&&(v9_next()%100)<5||v11_charm(57)&&v11_world()==6&&(v9_next()%100)<10)damage=0;
  v11_take_hit(damage);
  for(i=0;i<v11_add_count;i++){if(v11_add_id[i]==61)v11_enemy_hp[battle_index]=(u16)mini(v11_enemy_max[battle_index],v11_enemy_hp[battle_index]+3);
   else v11_take_hit(maxi(1,V11_CHARACTERS[v11_add_id[i]].atk/3));}
 }
 if(v11_status&VS_BURN)v11_take_hit(3);
 if(v11_regen){v11_heal(v11_regen==1?16:17);v11_regen--;}
 if(v11_charm(52))v11_mp=(u16)mini(v11_max_mp(),v11_mp+1);
 if(!v11_command_used&&v11_buddy_hp&&v11_hp){if(v11_hp*2<v11_max_hp())v11_heal(10);
  else if(v11_bond()>=2)v11_damage_target(2+v11_bond(),0,0,0);}
 if(v11_enemy_status_turn&&!--v11_enemy_status_turn)v11_enemy_status=0;

 if(v11_ward)v11_ward--;if(v11_haste)v11_haste--;if(v11_decoy)v11_decoy--;if(v11_invincible)v11_invincible--;
 if(v11_stand)v11_stand--;
 if(v11_echo_turns)v11_echo_turns--;if(v11_flare)v11_flare--;
 v11_command_used=v11_move_turn=0;v11_last_action=battle_cursor;
 if(!v11_enemy_hp[battle_index]&&!v11_add_count){v11_battle_reward(0);return;}
 if(!v11_hp){v11_gameover=1;v11_choice=0;game_mode=MODE_SURFACE;v11_resume_art();return;}
 battle_phase=2;battle_timer=20;v11_message(skip?"THE ENEMY'S SIGNAL STUMBLED. COSMOS IS STILL HERE.":"THE ENEMY STRUCK. COSMOS TOOK ITS OWN TURN.");
}
static void v11_commit_action(void){if(!v11_enemy_hp[battle_index]&&!v11_add_count){v11_battle_reward(0);return;}
 battle_phase=1;battle_timer=24;battle_evade=0;v11_battle_sub=0;}
static void v11_fight(void){int damage=v11_str();if(v11_status&VS_ROOT)damage=damage*3/4;
 v11_damage_target(damage,0,1,0);if(v11_equipment[0]==10&&v11_turn%2==0)v11_damage_target(damage,0,1,0);
 v11_message("ARIN STRUCK. COSMOS WATCHES THE OPENING.");v11_commit_action();}
static void v11_talk(void){int id=v11_enemy_id[battle_index];
 if(id==99&&v11_qty[94]){v11_qty[94]--;v11_damage_target(335,0,0,1);v11_echo_turns=3;v11_message("AN ECHO ANSWERED THE QUIET. I REMEMBER YOUR NAME.");v11_commit_action();return;}
 if(id==94){v11_enemy_hp[battle_index]=(u16)mini(v11_enemy_max[battle_index]+100,v11_enemy_hp[battle_index]+50);v11_enemy_buff+=2;
  v11_message("THE HEART GREW STRONGER FROM YOUR OFFER. STARVE ITS HUNGER.");v11_commit_action();return;}
 if(id==52||id==69){v11_battle_reward(1);return;}
 if(id<70&&v11_enemy_hp[battle_index]*2<=v11_enemy_max[battle_index]){
  u8 species=eco_species_for_enemy(enemies[battle_index].type);LcResult r=lc_add_wild(&lc_party,species,v9_next());
  if(r==LC_OK){lc_party.slots[lc_party.count-1].bond=55;v11_trust(5);v11_battle_reward(1);return;}
  v11_message(r==LC_FULL?"THE PARTY IS FULL. THE CREATURE CAN STILL BE SPARED.":"THE CREATURE KEPT ITS DISTANCE.");
  v11_battle_reward(1);return;
 }
 if(v11_charm(66)&&v11_qty[94]){v11_qty[94]--;v11_echo_turns=(u8)(1+(v11_passive(66)?2:0));v11_free_cast=1;v11_message("THE VIAL RELEASED AN ECHO. YOUR NEXT SPELL IS FREE.");return;}
 v11_message("IT IS NOT READY TO LISTEN. WEAKEN AN ORDINARY CREATURE FIRST.");
}
static void v11_update_battle(u16 newk){int i,id=v11_enemy_id[battle_index];
 if(battle_phase==3){if(battle_timer)battle_timer--;if(!battle_timer||newk&KEY_A)v11_end_battle();return;}
 if(battle_phase==1){if(newk&KEY_B)battle_evade=1;if(battle_timer)battle_timer--;if(!battle_timer)v11_turn_end();return;}
 if(battle_phase==2){if(battle_timer)battle_timer--;if(!battle_timer){battle_phase=0;v11_message("CHOOSE YOUR NEXT ACTION.");}return;}
 if(v11_battle_sub){if(newk&KEY_B){v11_battle_sub=0;return;}
  int n=v11_battle_sub==1?4:v11_battle_sub==4?1+v11_add_count:v11_list_count;
  if(newk&KEY_UP)v11_battle_sel=(u8)wrapi(v11_battle_sel-1,maxi(1,n));
  if(newk&KEY_DOWN)v11_battle_sel=(u8)wrapi(v11_battle_sel+1,maxi(1,n));
  if(newk&KEY_A){if(v11_battle_sub==4){v11_target=v11_battle_sel;v11_fight();return;}
   if(v11_battle_sub==1){i=v11_shortcuts[v11_battle_sel];if(v11_use_skill(i)==1)v11_commit_action();}
   if(v11_battle_sub==2){i=n?v11_list[v11_battle_sel]:255;int r=v11_consume(i);if(r==1)v11_commit_action();}
   if(v11_battle_sub==3){i=n?v11_list[v11_battle_sel]:255;int r=v11_use_skill(i);if(r==1){v11_command_used=1;v11_commit_action();}}
  }return;
 }
 if(newk&KEY_SELECT){if(v11_use_skill(v11_ultimate)==1)v11_commit_action();return;}
 if(newk&KEY_B){battle_evade=1;v11_message("ARIN GUARDS. COSMOS STAYS CLOSE.");battle_phase=1;battle_timer=24;return;}
 if(newk&KEY_UP){battle_cursor=(u8)((battle_cursor+4)%6);v11_move_turn=1;}
 if(newk&KEY_DOWN){battle_cursor=(u8)((battle_cursor+2)%6);v11_move_turn=1;}
 if(newk&(KEY_LEFT|KEY_RIGHT)){battle_cursor^=1;v11_move_turn=1;}
 if(!(newk&KEY_A))return;
 if(v11_status&VS_FREEZE||v11_status&VS_CHARM){v11_message("YOUR SIGNAL IS HELD. COSMOS WILL TAKE ITS TURN.");v11_commit_action();return;}
 if(battle_cursor==0){if(v11_add_count){v11_battle_sub=4;v11_battle_sel=1;}else{v11_target=0;v11_fight();}}
 else if(battle_cursor==1){v11_battle_sub=1;v11_battle_sel=0;v11_target=0;}
 else if(battle_cursor==2){v11_battle_sub=2;v11_battle_sel=0;v11_list_count=0;for(i=70;i<90;i++)if(v11_qty[i])v11_list[v11_list_count++]=(u8)i;}
 else if(battle_cursor==3)v11_talk();
 else if(battle_cursor==4){if(id>=70)v11_message("THIS FOE HOLDS THE ROAD. A SMOKE PELLET STILL WORKS.");
  else if((v9_next()%100)<75||v11_haste){v11_end_battle();v11_message("WE ESCAPED TOGETHER.");}else{v11_message("THE ESCAPE FAILED.");v11_commit_action();}}
 else{v11_battle_sub=3;v11_battle_sel=0;v11_target=0;v11_list_count=0;for(i=30;i<50;i++)if(v11_skill_known(i))v11_list[v11_list_count++]=(u8)i;}
}
static void v11_draw_battle(void){int i,id=v11_enemy_id[battle_index];static const char*act[6]={"FIGHT","MAGIC","ITEM","TALK","RUN","ALLY"};
 ui_clear();ui_frame(0,19,15);oam_hide_all();ui_text(2,1,"ERIDORIA // DUEL",14);
 ui_text(2,3,V11_CHARACTERS[id].name,13);ui_text(2,4,"HP",15);ui_num(5,4,v11_enemy_hp[battle_index],15);
 ui_text(9,4,"/",15);ui_num(11,4,v11_enemy_max[battle_index],15);if(v11_add_count){ui_text(18,4,"ADDS",13);ui_num(24,4,v11_add_count,15);}
 oam_set32(0,32,40,272,0);oam_ui_portrait(0);oam_set32(2,169,40,384,13);oam_ui_portrait(2);
 if(!v11_active_cosmos&&lc_party.count&&lc_party.slots[lc_party.active].species>=LC_SPECIES_IMPORTED)v11_draw_import_battle(3,104,8,lc_party.slots[lc_party.active].identity);
 else{oam_set(1,90,53,32+(cosmos.mood&3)*4,1,0);oam_ui_portrait(1);
  if(!v11_active_cosmos&&lc_party.count){LcCreature*c=&lc_party.slots[lc_party.active];if(c->species>=1&&c->species<=8){vram_copy32(OBJ_VRAM32+416*8,V108_SPECIES[c->species-1][mini(2,c->stage)][0],32);oam_set(3,62,53,416,5+c->species-1,0);oam_ui_portrait(3);}}}
 for(i=0;i<v11_add_count;i++){int x,y;u32 art[32];const u32*src=V11_FIELD_ART+v11_add_id[i]*128;for(x=0;x<32;x++)art[x]=0;
  for(y=0;y<16;y++)for(x=0;x<16;x++){int sx=x*2,sy=y*2,n=(src[((sy/8)*4+sx/8)*8+(sy&7)]>>((sx&7)*4))&15;art[((y/8)*2+x/8)*8+(y&7)]|=(u32)n<<((x&7)*4);}
  vram_copy32(OBJ_VRAM32+(480+i*4)*8,art,32);oam_set(5+i,i==0?146:i==1?207:224,55,480+i*4,14,0);oam_ui_portrait(5+i);}
 ui_text(2,9,"ARIN",14);ui_text(8,9,"LV",15);ui_num(11,9,player_level,15);
 ui_text(16,9,"BOND",13);ui_num(23,9,v11_bond(),15);
 ui_text(2,10,"HP",13);ui_num(5,10,v11_hp,15);ui_text(8,10,"/",15);ui_num(9,10,v11_max_hp(),15);
 ui_text(16,10,"MP",13);ui_num(20,10,v11_mp,15);ui_text(24,10,"/",15);ui_num(25,10,v11_max_mp(),15);
 if(v11_battle_sub){int n=v11_battle_sub==1?4:v11_battle_sub==4?1+v11_add_count:v11_list_count;
  int start=(v11_battle_sel/4)*4;for(i=start;i<mini(start+4,n);i++){
   const char*name;int item=v11_battle_sub==1?v11_shortcuts[i]:v11_battle_sub==4?255:v11_list[i];
   name=v11_battle_sub==4?(i==0?V11_CHARACTERS[id].name:id==92?"TIDE ANCHOR":V11_CHARACTERS[v11_add_id[i-1]].name):
      item==255?"NO SIGNAL":v11_battle_sub==2?V11_ITEMS[item].name:V11_SKILLS[item].name;
   ui_text(2,12+i-start,i==v11_battle_sel?">":" ",13);ui_text(4,12+i-start,name,15);
   if(item<100&&v11_battle_sub!=2){ui_num(26,12+i-start,V11_SKILLS[item].mp,14);}
  }
  if(!n)ui_text(4,13,"NO SIGNAL",13);
 }else for(i=0;i<6;i++){int x=i%2?16:2,y=12+i/2;ui_text(x,y,battle_phase==0&&i==battle_cursor?">":" ",13);ui_text(x+2,y,act[i],15);}
 ui_wrap_text(16,v11_notice,14,2);ui_text(2,18,v11_battle_sub?"A CHOOSE   B BACK":v11_ult_charge==100?"SELECT ULT   B GUARD":"A ACT  B GUARD  ULT",13);
 if(!v11_battle_sub&&v11_ult_charge<100)ui_num(24,18,v11_ult_charge,14);
}
