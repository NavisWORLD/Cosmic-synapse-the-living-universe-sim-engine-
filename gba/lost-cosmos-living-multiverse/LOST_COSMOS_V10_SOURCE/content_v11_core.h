/* Executable RPG rules and append-only persistence. Included after the engine. */
static int v11_world(void){return V11_IS_ROOM?current_room-V11_FIRST_ROOM:0;}
static int v11_passive(int id){int i;for(i=0;i<4;i++)if(v11_passives[i]==id)return 1;return 0;}
static int v11_charm(int id){return v11_equipment[2]==id;}
static int v11_gear_stat(int n){int i,sum=0;for(i=0;i<3;i++)if(v11_equipment[i]<70){
 const V11Item*e=&V11_ITEMS[v11_equipment[i]];
 int q=n==0?e->str:n==1?e->def:n==2?e->mag:n==3?e->hp:e->mp;
 if(n<3&&v11_durability[i]<25)q/=2;sum+=q;}return sum;}
static int v11_assembly(void){return v11_passive(73)?mini(5,v11_crafted):0;}
static int v11_max_hp(void){return clampi(max_hp*4+v11_gear_stat(3)+v11_perm_hp+(v11_passive(64)?10:0)+v11_assembly(),1,250);}
static int v11_max_mp(void){return clampi(max_mp*4+v11_gear_stat(4)+(v11_passive(63)?10:0)+v11_assembly(),1,250);}
static int v11_str(void){return maxi(1,str_stat*2+v11_gear_stat(0)+v11_assembly()+(v11_charm(59)&&v11_hp*2<v11_max_hp()?2:0));}
static int v11_def(void){return maxi(0,def_stat*2+v11_gear_stat(1)+v11_assembly()+(v11_passive(62)?2:0));}
static int v11_mag(void){return maxi(1,mag_stat*2+v11_gear_stat(2)+v11_assembly()+(v11_charm(60)&&v11_mp*2<v11_max_mp()?2:0));}
static int v11_bond(void){return v11_flare?10:clampi(1+cosmos.trust/26,1,10);}
static void v11_trust(int amount){if(v11_charm(51))amount=(amount*120+99)/100;if(v11_passive(71))amount=(amount*125+99)/100;cosmos.trust=(u8)mini(255,cosmos.trust+amount);}
static void v11_heal(int amount){if(v11_passive(54))amount=amount*110/100;v11_hp=(u16)mini(v11_max_hp(),v11_hp+amount);}
static int v11_slots_used(void){int i,n=0;for(i=0;i<100;i++)n+=v11_qty[i]!=0;return n;}
static int v11_capacity(void){return v11_passive(69)?60:40;}
static void v11_message(const char*text){copystr(v11_notice,text,90);v11_notice_timer=240;}
static int v11_inventory_add(int id,int quantity){
 if(id<0||id>=100||quantity<1)return 0;
 if(!v11_qty[id]&&v11_slots_used()>=v11_capacity()){
  v11_message("BAG FULL. OPEN ITEMS TO DROP OR USE AN ITEM. THIS PICKUP WILL WAIT.");return 0;}
 v11_qty[id]=(u8)mini(99,v11_qty[id]+quantity);return 1;
}
static void v11_grant(int id,int n){if(!v11_inventory_add(id,n))v11_pending[id]=(u8)mini(99,v11_pending[id]+n);}
static void v11_claim_pending(void){int i;for(i=0;i<100;i++)if(v11_pending[i]&&(v11_qty[i]||v11_slots_used()<v11_capacity())){int n=mini(v11_pending[i],99-v11_qty[i]);if(n&&v11_inventory_add(i,n))v11_pending[i]-=n;}}
static int v11_skill_known(int id){return id>=0&&id<100&&((v11_learned[id>>3]>>(id&7))&1);}
static void v11_learn(int id){if(id>=0&&id<100)v11_learned[id>>3]|=(u8)(1u<<(id&7));}
static int v11_gate(int gate){
 if(gate==0)return 1;if(gate==1)return (v11_quest_done&(1u<<9))!=0;
 if(gate==2)return (v11_quest_done&(1u<<13))!=0;
 if(gate==3)return (story_flags&ST_MALAKAR)||(v11_boss_done&1);
 if(gate==4)return postgame||(v11_boss_done&256);
 if(gate==5)return (v11_quest_done&(1u<<12))!=0;
 if(gate==6)return (v11_quest_done&(1u<<14))!=0;
 if(gate==7)return (v11_quest_done&(1u<<11))!=0;
 if(gate==8)return v11_beacons==255;
 if(gate==9)return v11_skill_known(69);if(gate==10)return v11_corvus_trust>=100;
 if(gate==11)return v11_crafted>=20;if(gate==12)return (v11_npc_seen&(1u<<12))!=0;
 if(gate==13)return v11_qty[95]!=0;if(gate==14)return (v11_npc_seen&2)!=0;
 if(gate==15)return (v11_npc_seen&4)!=0;
 if(gate>=20&&gate<30)return (v11_boss_done&(1u<<(gate-20)))!=0;
 return 0;
}
static void v11_unlock(void){int i;v11_claim_pending();for(i=0;i<100;i++){
 const V11Skill*s=&V11_SKILLS[i];if(player_level<s->level||v11_bond()<s->bond)continue;
 if(s->world<8&&!(v11_visited&(1u<<s->world)))continue;if(!v11_gate(s->gate))continue;
 v11_learn(i);
 }if(v11_ultimate==255){for(i=75;i<90;i++)if(v11_skill_known(i)){v11_ultimate=(u8)i;break;}}
}
static void v11_quest_finish(int id){if(id<0||id>=15||v11_quest_done&(1u<<id))return;
 v11_quest_started|=(u16)(1u<<id);v11_quest_done|=(u16)(1u<<id);
 v11_quest[id]=5;v11_trust(8);v11_credits=(u16)mini(65535,v11_credits+35);
 if(id==8){v11_grant(8,1);v11_grant(59,1);}
 if(id==9){v11_grant(9,1);v11_grant(34,1);v11_grant(60,1);}
 if(id==10){v11_grant(33,1);v11_grant(58,1);}
 if(id==11){v11_grant(24,1);v11_grant(46,1);v11_grant(65,1);v11_grant(97,1);}
 if(id==12){v11_grant(66,1);v11_grant(82,1);}
 if(id==13){v11_grant(11,1);v11_grant(36,1);v11_grant(62,1);v11_grant(96,1);}
 if(id==14){v11_grant(22,1);v11_grant(49,1);v11_grant(67,1);}
 v11_unlock();
}
static void v11_reset(void){int i,j;for(i=0;i<100;i++)v11_qty[i]=v11_encounters[i]=v11_pending[i]=0;
 for(i=0;i<13;i++)v11_learned[i]=0;
 for(i=0;i<15;i++)v11_quest[i]=0;
 for(i=0;i<8;i++)v11_world_kills[i]=0;
 for(i=0;i<20;i++)v11_elite_day[i]=65535;
 for(i=0;i<4;i++)v11_shortcuts[i]=v11_passives[i]=255;
 for(i=0;i<12;i++)for(j=0;j<12;j++)v11_names[i][j]=0;
 v11_shortcuts[0]=0;v11_equipment[0]=0;v11_equipment[1]=25;v11_equipment[2]=255;
 v11_qty[0]=v11_qty[25]=v11_qty[99]=1;v11_qty[70]=2;v11_qty[71]=1;
 v11_visited=v11_beacons=v11_echo_found=v11_best_reward=v11_perm_hp=0;
 v11_quest_started=v11_quest_done=v11_boss_done=v11_cores_found=0;
 v11_npc_seen=v11_caches=v11_ticks=0;v11_credits=20;v11_hp=24;v11_mp=24;v11_buddy_hp=22;
 v11_days=v11_day_ticks=v11_scrap=0;v11_herbs=0;
 v11_crafted=0;v11_ultimate=255;v11_track=v11_last_beacon=255;
 v11_ult_charge=v11_xp_boost=v11_corvus_trust=v11_forges=0;
 v11_ninth_day=v11_stay_day=65535;v11_text_speed=1;v11_brightness=3;
 for(i=0;i<3;i++)v11_durability[i]=100;
 v11_dialogue=v11_shop=v11_evolution=v11_gameover=v11_rename=0;
 v11_field_light=v11_field_track=v11_field_scout=0;v11_forage_day=255;
 v11_active_cosmos=v11_export_ready=v11_cosmos_stage=0;v11_battle_pose=255;v11_cosmos_name[0]=0;
 v11_menu_reset();v11_unlock();
}
static void v11_save(void){u8 b[V11_BYTES];int i,j,o=16;u32 crc;
 for(i=0;i<V11_BYTES;i++)b[i]=0;
 b[0]='L';b[1]='C';b[2]='1';b[3]='1';b[4]=1;b[5]=1;
 for(i=0;i<100;i++)b[o++]=v11_qty[i];
 for(i=0;i<100;i++)b[o++]=v11_encounters[i];
 for(i=0;i<13;i++)b[o++]=v11_learned[i];
 for(i=0;i<3;i++)b[o++]=v11_equipment[i];
 for(i=0;i<4;i++)b[o++]=v11_shortcuts[i];
 for(i=0;i<4;i++)b[o++]=v11_passives[i];
 b[o++]=v11_ultimate;b[o++]=v11_visited;b[o++]=v11_beacons;b[o++]=v11_last_beacon;b[o++]=v11_track;
 for(i=0;i<15;i++)b[o++]=v11_quest[i];for(i=0;i<8;i++)b[o++]=v11_world_kills[i];
 for(i=0;i<20;i++){b[o++]=(u8)v11_elite_day[i];b[o++]=(u8)(v11_elite_day[i]>>8);}
 /* Fixed extension schema: additions must occupy reserved bytes after 490. */
 for(i=0;i<4;i++)b[330+i]=(u8)(v11_npc_seen>>(i*8));
 for(i=0;i<4;i++)b[334+i]=(u8)(v11_caches>>(i*8));
 for(i=0;i<4;i++)b[338+i]=(u8)(v11_ticks>>(i*8));
 #define V11_PUT16(at,v) b[at]=(u8)(v);b[(at)+1]=(u8)((v)>>8)
 V11_PUT16(342,v11_quest_started);V11_PUT16(344,v11_quest_done);
 V11_PUT16(346,v11_boss_done);V11_PUT16(348,v11_cores_found);
 V11_PUT16(350,v11_credits);V11_PUT16(352,v11_hp);V11_PUT16(354,v11_mp);
 V11_PUT16(356,v11_buddy_hp);V11_PUT16(358,v11_crafted);
 b[360]=v11_echo_found;b[361]=v11_perm_hp;b[362]=v11_ult_charge;b[363]=v11_xp_boost;
 for(i=0;i<3;i++)b[364+i]=v11_durability[i];
 b[367]=v11_corvus_trust;b[368]=v11_text_speed;b[369]=v11_brightness;b[370]=v11_best_reward;b[371]=v11_forges;
 V11_PUT16(372,v11_ninth_day);V11_PUT16(374,v11_stay_day);
 for(i=0;i<12;i++)for(j=0;j<12;j++)b[376+i*12+j]=(u8)v11_names[i][j];
 V11_PUT16(520,v11_days);V11_PUT16(522,v11_day_ticks);V11_PUT16(524,v11_scrap);b[526]=v11_herbs;
 b[527]=v11_active_cosmos;b[528]=v11_export_ready;b[529]=v11_cosmos_stage;
 for(i=0;i<12;i++)b[530+i]=(u8)v11_cosmos_name[i];b[542]=v11_forage_day;for(i=0;i<100;i++)b[548+i]=v11_pending[i];
 #undef V11_PUT16
 crc=lc_crc32(b,764);for(i=0;i<4;i++)b[764+i]=(u8)(crc>>(i*8));
 for(i=0;i<V11_BYTES;i++)SRAM[V11_SRAM+i]=b[i];
}
static void v11_restore(void){u8 b[V11_BYTES];int i,j,o=16;u32 crc,got;
 for(i=0;i<V11_BYTES;i++)b[i]=SRAM[V11_SRAM+i];
 got=(u32)b[764]|((u32)b[765]<<8)|((u32)b[766]<<16)|((u32)b[767]<<24);crc=lc_crc32(b,764);
 v11_reset();
 if(b[0]!='L'||b[1]!='C'||b[2]!='1'||b[3]!='1'||b[4]!=1||b[5]!=1||crc!=got){
  v11_hp=(u16)(player.hp*4);v11_mp=(u16)(player_mp*4);v11_credits=credits;
  if(V11_IS_ROOM){current_room=2;player.x=160;player.y=344;}return;}
 for(i=0;i<100;i++)v11_qty[i]=(u8)mini(99,b[o++]);for(i=0;i<100;i++)v11_encounters[i]=b[o++];
 for(i=0;i<13;i++)v11_learned[i]=b[o++];
 for(i=0;i<3;i++){int n=b[o++];v11_equipment[i]=(u8)(n<70&&V11_ITEMS[n].kind==i&&v11_qty[n]?n:255);}
 for(i=0;i<4;i++){int n=b[o++];v11_shortcuts[i]=(u8)(n<30&&v11_skill_known(n)?n:255);}
 for(i=0;i<4;i++){int n=b[o++];v11_passives[i]=(u8)(n>=50&&n<75&&v11_skill_known(n)?n:255);}
 v11_ultimate=b[o++];if(v11_ultimate<75||v11_ultimate>=90||!v11_skill_known(v11_ultimate))v11_ultimate=255;
 v11_visited=b[o++];v11_beacons=b[o++]&v11_visited;v11_last_beacon=b[o++];if(v11_last_beacon>7)v11_last_beacon=255;
 v11_track=b[o++];if(v11_track>=15)v11_track=255;
 for(i=0;i<15;i++)v11_quest[i]=(u8)mini(5,b[o++]);for(i=0;i<8;i++)v11_world_kills[i]=b[o++];
 for(i=0;i<20;i++){v11_elite_day[i]=b[o]|((u16)b[o+1]<<8);o+=2;}
 #define V11_GET16(at) ((u16)b[at]|((u16)b[(at)+1]<<8))
 #define V11_GET32(at) ((u32)b[at]|((u32)b[(at)+1]<<8)|((u32)b[(at)+2]<<16)|((u32)b[(at)+3]<<24))
 v11_npc_seen=V11_GET32(330)&0x3fffffffu;v11_caches=V11_GET32(334);v11_ticks=V11_GET32(338);
 v11_quest_started=V11_GET16(342)&32767;v11_quest_done=V11_GET16(344)&32767;
 v11_boss_done=V11_GET16(346)&1023;v11_cores_found=V11_GET16(348)&4095;
 v11_credits=V11_GET16(350);v11_perm_hp=(u8)mini(6,b[361]);
 v11_hp=(u16)mini(v11_max_hp(),V11_GET16(352));v11_mp=(u16)mini(v11_max_mp(),V11_GET16(354));
 v11_buddy_hp=(u16)mini(250,V11_GET16(356));v11_crafted=V11_GET16(358);
 v11_echo_found=b[360];v11_ult_charge=(u8)mini(100,b[362]);v11_xp_boost=(u8)mini(5,b[363]);
 for(i=0;i<3;i++)v11_durability[i]=(u8)mini(100,b[364+i]);
 v11_corvus_trust=(u8)mini(100,b[367]);v11_text_speed=b[368]%3;v11_brightness=(u8)clampi(b[369],1,5);
 v11_best_reward=(u8)mini(4,b[370]);v11_forges=b[371]&7;
 v11_ninth_day=V11_GET16(372);v11_stay_day=V11_GET16(374);
 for(i=0;i<12;i++){for(j=0;j<11;j++){u8 c=b[376+i*12+j];v11_names[i][j]=(char)((c>='A'&&c<='Z')||c==' '||c==0?c:0);}v11_names[i][11]=0;}
 v11_days=V11_GET16(520);v11_day_ticks=V11_GET16(522)%36000;v11_scrap=V11_GET16(524);v11_herbs=b[526];
 v11_active_cosmos=b[527]&1;v11_export_ready=b[528]&1;v11_cosmos_stage=(u8)mini(2,b[529]);v11_forage_day=b[542];for(i=0;i<100;i++)v11_pending[i]=(u8)mini(99,b[548+i]);
 for(i=0;i<11;i++){u8 c=b[530+i];v11_cosmos_name[i]=(char)((c>='A'&&c<='Z')||c==' '||c==0?c:0);}v11_cosmos_name[11]=0;
 #undef V11_GET16
 #undef V11_GET32
 v11_unlock();
}
/* Three sparse manual snapshots live beyond the frozen journal banks. Each is
   committed last and validated before touching the authoritative primary page. */
typedef struct{u16 offset,length;} V11SaveRange;
static const V11SaveRange V11_SLOT_RANGES[9]={{0,256},{1024,252},{2048,32},{3072,32},{4096,32},{5120,32},{6144,256},{6400,768},{7168,128}};
#define V11_SLOT_BYTES 1920
#define V11_SLOT_PAYLOAD 1888
static u32 v11_sram_crc(int offset,int length){u32 c=0xffffffffu;int i;for(i=0;i<length;i++)c=(c>>8)^journal_crc_table[(c^SRAM[offset+i])&255u];return c^0xffffffffu;}
static int v11_slot_valid(int slot){int o;u32 got;if(slot<0||slot>2)return 0;o=25600+slot*2048;
 if(SRAM[o]!='L'||SRAM[o+1]!='C'||SRAM[o+2]!='M'||SRAM[o+3]!=1||SRAM[o+31]!=0xa5)return 0;
 got=sr32(o+16);return got==v11_sram_crc(o+32,V11_SLOT_PAYLOAD);
}
static void v11_slot_save(int slot){int i,j,o=25600+slot*2048,p=o+32;save_game();SRAM[o+31]=0;
 for(i=0;i<9;i++)for(j=0;j<V11_SLOT_RANGES[i].length;j++)SRAM[p++]=SRAM[V11_SLOT_RANGES[i].offset+j];
 SRAM[o]='L';SRAM[o+1]='C';SRAM[o+2]='M';SRAM[o+3]=1;
 SRAM[o+4]=current_world;SRAM[o+5]=current_room;SRAM[o+6]=player_level;
 SRAM[o+7]=(u8)((completion_count()+pop8(v11_beacons)+pop8((u8)v11_boss_done)+pop8((u8)(v11_boss_done>>8)))*100/42);
 sw32(o+8,v11_ticks);sw32(o+16,v11_sram_crc(o+32,V11_SLOT_PAYLOAD));SRAM[o+31]=0xa5;
 v11_message("SAVE COMPLETE. THIS SLOT CAN BE LOADED AFTER RESTART.");
}
static int v11_slot_load(int slot){int i,j,p=25600+slot*2048+32;
 if(!v11_slot_valid(slot)){v11_message("NO VERIFIED SAVE IN THIS SLOT.");return 0;}
 for(i=0;i<9;i++)for(j=0;j<V11_SLOT_RANGES[i].length;j++)SRAM[V11_SLOT_RANGES[i].offset+j]=SRAM[p++];
 journal_commit();load_game();v11_gameover=0;return_mode=game_mode;
 if(game_mode==MODE_SPACE)generate_space();else generate_surface();refresh_camera();v11_message("YOUR SIGNAL RETURNS.");return 1;
}
static void v11_clock(void){if(intro||v10_opening||cinema_active||game_mode==MODE_PAUSE)return;
 v11_ticks++;if(++v11_day_ticks>=36000){v11_day_ticks=0;v11_days++;}
 if(v11_notice_timer&&!--v11_notice_timer)v11_notice[0]=0;
 if((v11_ticks&255)==0)v11_unlock();}
static const char*v11_creature_name(int index){if(index>=0&&index<12&&v11_names[index][0])return v11_names[index];
 if(index>=0&&index<lc_party.count&&lc_party.slots[index].species>=LC_SPECIES_IMPORTED){
#if defined(LC_IMPORT_DISPLAY_NAME)
 return LC_IMPORT_DISPLAY_NAME;
#else
 return "MIRABY";
#endif
 }
 return index>=0&&index<lc_party.count?lc_species_name(lc_party.slots[index].species):"NO SIGNAL";
}
static void v11_draw_import_battle(int oi,int x,int y){
#if defined(LC_IMPORTED_COMPANION)
 int x0,y0,dx;volatile u16*dst=(volatile u16*)OBJ_VRAM32;int pose=cosmos.mood&3;
 /* 64x64 BATTLE art is made from the FIELD frame, never the portrait. Matrix 4
    scales this canvas to 32x32 on-screen; it remains reserved exclusively here. */
 if(v11_battle_pose!=pose){for(y0=0;y0<64;y0++)for(x0=0;x0<64;x0+=4){u16 word=0;
  for(dx=0;dx<4;dx++){int sx=(x0+dx)/2,sy=y0/2;
   int tile=(sy/8)*4+sx/8,at=pose*512+tile*32+(sy&7)*4+(sx&7)/2;
   int n=(lc_imported_companion_field_tiles[at]>>((sx&1)*4))&15;
   word|=(u16)(n<<(dx*4));}
  dst[LC_IMPORT_OBJ_TILE*16+((y0/8)*8+x0/8)*16+(y0&7)*2+(x0&7)/4]=word;
 }v11_battle_pose=(u8)pose;}
 lc_import_palette();OAM16[4*16+3]=512;OAM16[4*16+7]=0;OAM16[4*16+11]=0;OAM16[4*16+15]=512;
 OAM16[oi*4]=(u16)((y&255)|0x0100);OAM16[oi*4+1]=(u16)((x&511)|(3u<<14)|(4u<<9));
 OAM16[oi*4+2]=(u16)(LC_IMPORT_OBJ_TILE+(LC_IMPORT_OBJ_PAL<<12));
#else
 (void)oi;(void)x;(void)y;
#endif
}
