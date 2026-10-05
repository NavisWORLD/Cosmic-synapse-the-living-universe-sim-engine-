/* Native 30-column content UI. All modal screens have a reversible B path. */
static u8 v11_page_previous=255,v11_parent=0,v11_map_legacy=0,v11_release_confirm=0;
static u8 v11_assign=0,v11_rename_pos=0,v11_rename_letter=0;
static char v11_name_edit[12];
static const u8 V11_TABS[9]={40,4,5,28,18,20,11,1,9};
static const char*V11_TAB_NAMES[9]={"STATUS","ITEMS","GEAR","SKILLS","PARTY","BEASTS","QUESTS","MAP","SYSTEM"};
static void v11_menu_reset(void){v11_ui_dirty=1;v11_list_kind=255;v11_sel=v11_sub=v11_menu_mode=v11_detail=v11_slot=0;v11_page_previous=255;v11_release_confirm=0;}
static void v11_short(int x,int y,const char*s,int width,int pal){char b[31];int i=0;while(s[i]&&i<width&&i<30){b[i]=s[i];i++;}b[i]=0;ui_text(x,y,b,pal);}
static int v11_text_page(const char*s,int offset,char*out,int width,int rows){
 int n=0,col=0,row=0,i=offset;while(s[i]&&row<rows){
  if(s[i]=='\n'){out[n++]='\n';row++;col=0;i++;continue;}int word=0;while(s[i+word]&&s[i+word]!=' '&&s[i+word]!='\n')word++;
  if(col&&col+word+1>width){out[n++]='\n';row++;col=0;if(row==rows)break;}
  else if(col){out[n++]=' ';col++;}
  while(word--&&s[i]&&n<125){out[n++]=s[i++];col++;if(col==width&&s[i]&&s[i]!=' '){out[n++]='\n';row++;col=0;if(row==rows)break;}}
  while(s[i]==' ')i++;if(n>=125)break;
 }out[n]=0;return i;
}
static void v11_lines(int x,int y,const char*s,int width,int rows,int pal){char b[128],line[31];int i=0,j=0,r=0;v11_text_page(s,0,b,width,rows);
 while(b[i]&&r<rows){if(b[i]=='\n'){line[j]=0;ui_text(x,y+r,line,pal);r++;j=0;}else if(j<30)line[j++]=b[i];i++;}if(r<rows){line[j]=0;ui_text(x,y+r,line,pal);}}
static int v11_len(const char*s){int n=0;while(s[n])n++;return n;}
static void v11_dialogue_advance(void){char page[128];const char*s=v11_dialogue_page?V11_NPC_LINES[v11_speaker]:V11_CHARACTERS[v11_speaker].description;
 if(v11_dialogue_page==2){v11_npc_next();return;}
 int end=v11_text_page(s,v11_dialogue_scroll,page,26,3);
 if(v11_dialogue_reveal<120&&v11_dialogue_reveal<(int)v11_len(page)){v11_dialogue_reveal=120;return;}
 if(s[end])v11_dialogue_scroll=(u8)end;else{v11_dialogue_scroll=0;v11_npc_next();}v11_dialogue_reveal=0;
}
static void v11_dialogue_draw(void){char page[128];const char*s=v11_dialogue_page?V11_NPC_LINES[v11_speaker]:V11_CHARACTERS[v11_speaker].description;
 int end=v11_text_page(s,v11_dialogue_scroll,page,26,3);int rate=v11_text_speed==0?4:v11_text_speed==1?2:1;
 if((frame&(rate-1))==0&&v11_dialogue_reveal<120)v11_dialogue_reveal++;
 if(v11_dialogue_reveal<(int)v11_len(page))page[v11_dialogue_reveal]=0;
 v11_lines(2,13,page,26,3,15);if(s[end])ui_text(25,17,">>",13);
}
static void v11_menu_palette(void){int i,j;static const u16 colors[5]={RGB5(22,23,25),RGB5(9,29,16),RGB5(12,22,31),RGB5(26,16,31),RGB5(31,25,8)};
 for(i=0;i<5;i++){for(j=0;j<16;j++)BG_PALETTE[(8+i)*16+j]=BG_PALETTE[15*16+j];BG_PALETTE[(8+i)*16+5]=colors[i];BG_PALETTE[(8+i)*16+1]=colors[i];}
 for(j=0;j<16;j++)BG_PALETTE[7*16+j]=BG_PALETTE[15*16+j];BG_PALETTE[7*16+1]=BG_PALETTE[7*16+5]=RGB5(31,12,12);
}
static void v11_icon(int id,int skill){int i;if(id<0||id>=100)return;
 vram_copy32(OBJ_VRAM32+V11_TILE_ICON*8,(skill?V11_SKILLS_ART:V11_ITEMS_ART)+id*32,32);
 for(i=0;i<16;i++)OBJ_PALETTE[14*16+i]=(skill?V11_SKILLS_PALETTES:V11_ITEMS_PALETTES)[id*16+i];
 oam_set(44,8,96,V11_TILE_ICON,14,0);oam_ui_portrait(44);
}
static int v11_compare_name(const char*a,const char*b){while(*a&&*a==*b){a++;b++;}return (u8)*a-(u8)*b;}
static void v11_items_list(void){static u8 last_qty[100],last_cat=255,last_sort=255;int i,j,same=v11_list_kind==0&&last_cat==v11_cat&&last_sort==v11_sort;
 for(i=0;i<100;i++)if(last_qty[i]!=v11_qty[i])same=0;if(same)return;
 for(i=0;i<100;i++)last_qty[i]=v11_qty[i];last_cat=v11_cat;last_sort=v11_sort;v11_list_kind=0;v11_list_count=0;for(i=0;i<100;i++)if(v11_qty[i]){
 int heal=i==70||i==71||i==72||i==73||i==74||i==75||i==77||i==78||i==79||i==89;
 if(v11_cat==1&&!heal||v11_cat==2&&(i<70||i>=90||heal)||v11_cat==3&&i<90)continue;
 v11_list[v11_list_count++]=(u8)i;}
 for(i=1;i<v11_list_count;i++){u8 v=v11_list[i];j=i;while(j){int p=v11_list[j-1],diff=v11_sort==0?v11_compare_name(V11_ITEMS[p].name,V11_ITEMS[v].name):v11_sort==1?V11_ITEMS[p].kind-V11_ITEMS[v].kind:V11_ITEMS[v].rarity-V11_ITEMS[p].rarity;
 if(!diff)diff=p-v;if(diff<=0)break;v11_list[j]=v11_list[j-1];j--;}v11_list[j]=v;}
 if(v11_sel>=v11_list_count)v11_sel=0;
}
static void v11_skills_list(void){int i;v11_list_kind=2;v11_list_count=0;for(i=0;i<100;i++)if(V11_SKILLS[i].kind==v11_sub)v11_list[v11_list_count++]=(u8)i;if(v11_sel>=v11_list_count)v11_sel=0;}
static void v11_gear_list(void){int i;v11_list_kind=1;v11_list_count=1;v11_list[0]=255;for(i=0;i<70;i++)if(V11_ITEMS[i].kind==v11_slot&&v11_qty[i])v11_list[v11_list_count++]=(u8)i;if(v11_sel>=v11_list_count)v11_sel=0;}
static const char*v11_cosmos_label(void){return v11_cosmos_name[0]?v11_cosmos_name:"COSMOS";}
static void v11_portrait(int pick,int x,int y,int pulse){int xx,yy,i;u32 tile[512];const u32*src;
 u32 seed=pick>0&&pick<=lc_party.count?lc_party.slots[pick-1].seed:0x43534d53u;
 static u8 port_key=255,port_pick=255,port_pulse=255;
 y+=v11_anim_bob(seed)+(pulse?-((pulse&4)?3:0):0);
 if(pick>0&&pick<=lc_party.count&&lc_party.slots[pick-1].species>=LC_SPECIES_IMPORTED){
  if(v11_battle_pose!=255){lc_upload_import_art();v11_battle_pose=255;}lc_draw_import_portrait(x,y,lc_party.slots[pick-1].identity);
  if(pulse){int scale=256-(pulse%20)*3;OAM16[3*16+3]=scale;OAM16[3*16+7]=0;OAM16[3*16+11]=0;OAM16[3*16+15]=scale;OAM16[42*4]|=0x0100;OAM16[42*4+1]|=(3u<<9);}return;}
 int species=pick>0&&pick<=lc_party.count?lc_party.slots[pick-1].species:0;
 int stage=pick>0?lc_party.slots[pick-1].stage:v11_cosmos_stage;
 int key=species|(mini(2,stage)<<4);
 if(port_key!=(u8)key||port_pick!=(u8)pick){
  for(i=0;i<512;i++)tile[i]=0;
  src=species>=1&&species<=8?V108_SPECIES[species-1][mini(2,stage)][0]:0;
  for(yy=0;yy<64;yy++)for(xx=0;xx<64;xx++){
   int sx=xx/4,sy=yy/4,n;
   if(src)n=(src[((sy/8)*2+sx/8)*8+(sy&7)]>>((sx&7)*4))&15;else{volatile u16*obj=(volatile u16*)OBJ_VRAM32;int at=32*16+((sy/8)*2+sx/8)*16+(sy&7)*2+(sx&7)/4;n=(obj[at]>>((sx&3)*4))&15;}
   tile[((yy/8)*8+xx/8)*8+(yy&7)]|=(u32)(n&15)<<((xx&7)*4);
  }
  vram_copy32(OBJ_VRAM32+V11_TILE_PORT*8,tile,512);
  if(src){for(i=0;i<16;i++)OBJ_PALETTE[13*16+i]=OBJ_PALETTE[(5+species-1)*16+i];}
  else for(i=0;i<16;i++)OBJ_PALETTE[13*16+i]=OBJ_PALETTE[16+i];
  port_key=(u8)key;port_pick=(u8)pick;port_pulse=0;
 }
 OAM16[43*4]=(u16)(y&255);OAM16[43*4+1]=(u16)((x&511)|(3u<<14));OAM16[43*4+2]=(u16)(V11_TILE_PORT+(13u<<12));
 if(!pulse&&v11_anim_blink(seed)){OAM16[43*4]|=0x0100;OAM16[43*4+1]|=(2u<<9);
  OAM16[2*16+3]=256;OAM16[2*16+7]=0;OAM16[2*16+11]=0;OAM16[2*16+15]=176;}
 if(pulse){/* Matrix 3 is local to evolution. Battle owns matrix 4. */
 int scale=256-(pulse%20)*3;OAM16[3*16+3]=scale;OAM16[3*16+7]=0;OAM16[3*16+11]=0;OAM16[3*16+15]=scale;
 OAM16[43*4]|=0x0100;OAM16[43*4+1]|=(3u<<9);}
}
/* Cached pages keep their text map and only move sprites each frame. */
static void v11_menu_anim(void){
 if(pause_page==18&&v11_sel<=lc_party.count&&!(v11_sel&&lc_party.slots[v11_sel-1].species>=LC_SPECIES_IMPORTED))v11_portrait(v11_sel,168,40,0);
 else if(pause_page==20&&v11_sel<100&&v11_encounters[v11_sel]){oam_set32(44,8,88+v11_anim_bob((u32)v11_sel*9u),V11_TILE_FACE,14);oam_ui_portrait(44);}
}
static void v11_title_beast(int upload){/* Rebuild art only when the title changes. */
 if(upload){
 int i,x,y;u32 out[128];volatile u16*src=(volatile u16*)OBJ_VRAM32;for(i=0;i<128;i++)out[i]=0;
 for(y=0;y<32;y++)for(x=0;x<32;x++){int sx=x/2,sy=y/2,at=32*16+((sy/8)*2+sx/8)*16+(sy&7)*2+(sx&7)/4;
 int n=(src[at]>>((sx&3)*4))&15;out[((y/8)*4+x/8)*8+(y&7)]|=(u32)n<<((x&7)*4);}
 vram_copy32(OBJ_VRAM32+V11_TILE_FACE*8,out,128);}
 oam_set32(43,188,52+v11_anim_bob(frame),V11_TILE_FACE,1);oam_ui_portrait(43);
}
/* Public export snapshot in reserved bytes 6208..6399. No private memory. */
static int v11_export_valid(void){return SRAM[6208]=='L'&&SRAM[6209]=='C'&&SRAM[6210]=='E'&&SRAM[6211]==1&&SRAM[6399]==0xa5&&sr32(6388)==v11_sram_crc(6208,180);}
static int v11_prepare_export(int pick){u8 b[192];int i;u32 crc,id;LcCreature*c=pick>0&&pick<=lc_party.count?&lc_party.slots[pick-1]:0;
 if((c&&c->bond<55)||(!c&&v11_bond()<2)){v11_message("A BONDED BEAST IS NEEDED TO EXPORT.");return 0;}
 for(i=0;i<192;i++)b[i]=0;b[0]='L';b[1]='C';b[2]='E';b[3]=1;b[4]=(u8)pick;
 b[5]=c?c->level:player_level;b[6]=c?c->bond:(u8)mini(100,cosmos.trust);b[7]=c?c->stage:v11_cosmos_stage;
 const char*name=pick?v11_creature_name(pick-1):v11_cosmos_label();for(i=0;i<11&&name[i];i++)b[144+i]=(u8)name[i];
 b[16]='B';b[17]='C';b[18]='P';b[19]='1';b[20]=1;
 if(c&&lc_mail_matches(c->identity))for(i=0;i<64;i++)b[16+i]=SRAM[LC_MAILBOX_SRAM+32+i];else
#if defined(LC_IMPORT_HAS_BCP1)
 if(c&&lc_compiled_matches(c->identity))for(i=0;i<64;i++)b[16+i]=lc_imported_companion_bcp1[i];else
#endif
 {b[21]=(u8)(c?c->affinity:5);for(i=8;i<23;i++)b[16+i]=50;id=c?c->identity:0x43534d53u;
 for(i=0;i<4;i++)b[40+i]=(u8)(id>>(i*8));crc=lc_crc32(b+16,60);for(i=0;i<4;i++)b[76+i]=(u8)(crc>>(i*8));}
 b[80]='B';b[81]='C';b[82]='G';b[83]='1';b[84]=1;b[85]=b[22];b[156]=c?c->species:0;
 id=c?c->seed:0x43534d53u;for(i=0;i<4;i++)b[160+i]=(u8)(id>>(i*8));
 b[164]=c?(u8)c->xp:0;b[165]=c?(u8)(c->xp>>8):0;
 int hp=c?c->hp:v11_max_hp();b[166]=(u8)hp;b[167]=(u8)(hp>>8);
 b[168]=c?c->attack:(u8)mini(100,v11_str());b[169]=c?c->defense:(u8)maxi(1,mini(100,v11_def()));
 b[170]=c?c->flags:0;b[171]=c?c->affinity:5;
 crc=lc_crc32(b,180);for(i=0;i<4;i++)b[180+i]=(u8)(crc>>(i*8));b[191]=0xa5;
 SRAM[6399]=0;for(i=0;i<191;i++)SRAM[6208+i]=b[i];SRAM[6399]=0xa5;v11_export_ready=1;save_game();
 v11_message("EXPORT AVAILABLE. COPY YOUR BATTERY SAVE TO THE PUBLIC EXPORT TOOL.");return 1;
}
static u32 v11_art_crc(const u8*p,int n){u32 c=0xffffffffu;int i;for(i=0;i<n;i++)c=(c>>8)^journal_crc_table[(c^p[i])&255];return c^0xffffffffu;}
static int v11_snapshot_valid(void){
#if defined(LC_IMPORT_HAS_BCP1)
 static s8 checked=-1;if(checked<0)checked=(s8)(v11_art_crc(lc_imported_companion_tiles,8192)==V11_IMPORT_TILES_CRC&&v11_art_crc(lc_imported_companion_palette,32)==V11_IMPORT_PALETTE_CRC&&v11_art_crc(lc_imported_companion_field_tiles,2048)==V11_IMPORT_FIELD_TILES_CRC&&v11_art_crc(lc_imported_companion_bcp1,60)==V11_IMPORT_BCP1_CRC);return checked;
#else
 return 0;
#endif
}
static int v11_import_snapshot(void){
 lc_mailbox_refresh(0);sol_spark_checked=0;sol_spark_stage=sol_spark_blink=255;
 if(lc_mail_live){int ix;for(ix=0;ix<lc_party.count;ix++)if(lc_mail_matches(lc_party.slots[ix].identity)){
  lc_party.active=(u8)ix;v11_active_cosmos=0;v11_battle_pose=255;save_game();
  v11_message("BEAST IMPORTED FROM THE VERIFIED LOCAL MAILBOX.");return 1;}}
#if defined(LC_IMPORT_HAS_BCP1)
 LcProfile profile;int i;LcResult r=lc_parse_bcp1(lc_imported_companion_bcp1,64,&profile);
 if(r!=LC_OK||!v11_snapshot_valid()){v11_message("THE LOCAL SNAPSHOT FAILED ITS RECEIPT CHECK.");return 0;}
 for(i=0;i<lc_party.count;i++)if(lc_party.slots[i].identity==profile.public_id){lc_party.active=(u8)i;v11_active_cosmos=0;lc_upload_import_art();v11_battle_pose=255;save_game();v11_message("BEAST IMPORTED. YOUR EXISTING BOND AND IDENTITY ARE KEPT.");return 1;}
 r=lc_add_import(&lc_party,&profile,LC_IMPORT_SEED_HASH);if(r==LC_FULL){v11_message("PARTY FULL. MAKE ROOM FOR THIS BEAST IN PARTY.");return 0;}
 if(r!=LC_OK){v11_message("THE PUBLIC PROFILE COULD NOT BE INSTALLED.");return 0;}
 lc_party.active=(u8)(lc_party.count-1);lc_apply_import_progress(&lc_party.slots[lc_party.active]);v11_active_cosmos=0;lc_upload_import_art();save_game();v11_message("BEAST IMPORTED FROM A VERIFIED LOCAL SNAPSHOT.");return 1;
#else
 v11_message("OFFLINE MODE. THIS BUILD HAS NO VERIFIED BEAST SNAPSHOT.");return 0;
#endif
}
static void v11_header(const char*name){int t;{volatile u16*m=screenblock(UI_MAP_BASE);for(t=0;t<30;t++)m[31*32+t]=map_attr(61,15);}lc_ui_tabbed=1;REG_BG1VOFS=252;for(t=0;t<9;t++)if(V11_TABS[t]==pause_page){v11_short(1,0,V11_TAB_NAMES[wrapi(t-1,9)],8,8);ui_text(10,0,V11_TAB_NAMES[t],13);v11_short(20,0,V11_TAB_NAMES[(t+1)%9],8,8);}ui_text(2,2,name,14);ui_text(2,17,"A CHOOSE  B BACK  L/R TABS",13);}
static void v11_row(int row,int selected,const char*name,int pal){ui_text(2,row,selected?">":" ",13);v11_short(4,row,name,22,pal);}
static void v11_menu_notice(void){if(v11_notice_timer&&v11_notice[0]&&v11_detail==2){ui_frame(10,19,15);v11_lines(2,12,v11_notice,26,4,14);ui_text(2,17,"A/B CLOSE",13);}}
static void v11_recipe_cost(int n,int*out){
 static const u8 scrap[10]={8,6,5,1,1,1,1,1,0,2},herb[10]={2,1,1,0,0,0,0,0,5,1},core[10]={0,0,0,3,3,2,4,1,0,0};
 int i;for(i=0;i<3;i++)out[i]=0;if(n<0||n>=10)return;
 out[0]=scrap[n];out[1]=herb[n];out[2]=core[n];
 if(v11_passive(50))for(i=0;i<3;i++)out[i]=(out[i]*80+99)/100;
 if(v11_charm(67)){if(out[2])out[2]--;else if(out[0])out[0]--;else if(out[1])out[1]--;}
}
static void v11_local_mark(int tx,int ty,const char*s,int pal){ui_text(2+tx*26/64,4+ty*10/64,s,pal);}
static void v11_draw_local_map(void){int x,y,i,w=v11_world();
 v11_header("MAP // LOCAL SIGNALS");v11_short(2,3,v11_signal_goal(w),26,14);
 for(y=0;y<10;y++)for(x=0;x<26;x++){int tx=x*64/26,ty=y*64/10;
  ui_text(2+x,4+y,collision[ty*64+tx]==C_WALL?"*":".",8);}
 v11_local_mark(30,53,"F",13);v11_local_mark(45,16,"B",v11_beacons&(1u<<w)?9:13);
 v11_local_mark(54,52,">",14);v11_local_mark(32,55,"R",14);
 if(!(v11_cores_found&(1u<<w)))v11_local_mark(32,10,"C",10);
 if(!(v11_echo_found&(1u<<w)))v11_local_mark(27,30,"M",11);
 if(v11_field_track)for(i=0;i<10;i++)if(enemies[i].active)v11_local_mark(enemies[i].x/8,enemies[i].y/8,"E",7);
 v11_local_mark(player.x/8,player.y/8,"A",14);
 ui_text(2,14,"A YOU  C CORE  M ECHO",13);ui_text(2,15,"F CAMP  B BEACON  > GATE",13);
 ui_text(2,16,v11_field_track?"R RETURN  E FOE  * WALL":"R RETURN  TRACK SHOWS FOES",14);ui_text(2,17,"B BACK TO WORLD MAP",13);
}
#include "sol_beast_chat.h"
static int v11_draw_pause(void){int i,id,start;
 if(pause_page==0)return 0;
 if(pause_page!=40&&pause_page!=4&&pause_page!=5&&pause_page!=28&&pause_page!=18&&pause_page!=20&&pause_page!=11&&pause_page!=1&&pause_page!=9&&pause_page!=26&&pause_page!=27&&pause_page!=41&&pause_page!=42&&pause_page!=44&&pause_page!=45&&pause_page!=46&&pause_page!=47&&pause_page!=48&&pause_page!=49)return 0;
 if(pause_page==45&&v11_evolution){if(V11_IS_ROOM)v11_palette();else set_world_palette(current_world);}
 v11_menu_palette();
 if(pause_page==40){v11_header("ARIN // STATUS");ui_text(23,2,"LV",13);ui_num(26,2,player_level,15);
 ui_text(2,4,"HP",13);ui_num(5,4,V11_IS_ROOM?v11_hp:player.hp,15);ui_text(9,4,"/",15);ui_num(10,4,V11_IS_ROOM?v11_max_hp():max_hp,15);
 ui_text(16,4,"MP",13);ui_num(19,4,V11_IS_ROOM?v11_mp:player_mp,15);ui_text(23,4,"/",15);ui_num(24,4,V11_IS_ROOM?v11_max_mp():max_mp,15);
 ui_text(2,6,"STR",13);ui_num(6,6,V11_IS_ROOM?v11_str():str_stat+weapon_bonus(),15);ui_text(11,6,"DEF",13);ui_num(15,6,V11_IS_ROOM?v11_def():def_stat+armor_bonus(),15);ui_text(20,6,"MAG",13);ui_num(24,6,V11_IS_ROOM?v11_mag():mag_stat,15);
 ui_text(2,8,"XP",13);ui_num(6,8,player_xp,15);ui_text(15,8,"NEXT",13);ui_num(21,8,xp_need()-player_xp,15);
 ui_text(2,9,"KILLS",13);ui_num(8,9,kill_count,15);ui_text(15,9,"CREDITS",13);ui_num(24,9,V11_IS_ROOM?v11_credits:credits,15);
 ui_text(2,10,"PLAYTIME",13);ui_num(12,10,((int)v11_ticks)/216000,15);ui_text(15,10,":",15);ui_num(16,10,(((int)v11_ticks)/3600)%60,15);
 for(i=0;i<3;i++){static const char*n[3]={"WEAPON","ARMOR","CHARM"};ui_text(2,12+i,n[i],13);v11_short(9,12+i,v11_equipment[i]<70?V11_ITEMS[v11_equipment[i]].name:"NO SIGNAL",19,15);}
 ui_text(2,16,"SELECT CAMPAIGN STATUS",14);
 }else if(pause_page==4){static const char*cats[4]={"ALL","HEAL","BATTLE","KEY"};v11_header("ITEMS");ui_text(10,2,cats[v11_cat],13);ui_num(20,2,v11_slots_used(),15);ui_text(23,2,"/",15);ui_num(24,2,v11_capacity(),15);v11_items_list();start=v11_sel/8*8;
 for(i=0;i<100;i++)if(v11_pending[i]){ui_text(2,3,"REWARDS WAITING: FREE A SLOT",14);break;}
 for(i=start;i<mini(start+8,v11_list_count);i++){id=v11_list[i];v11_row(4+i-start,i==v11_sel,V11_ITEMS[id].name,8+V11_ITEMS[id].rarity);ui_text(25,4+i-start,"X",13);ui_num(26,4+i-start,v11_qty[id],15);}
 if(v11_list_count){id=v11_list[v11_sel];v11_icon(id,0);v11_lines(4,13,V11_ITEMS[id].description,24,3,15);}
 else ui_text(4,6,"NO SIGNAL",13);ui_text(2,16,v11_sort==0?"SELECT SORT NAME":v11_sort==1?"SELECT SORT TYPE":"SELECT SORT RARITY",14);
 if(v11_detail==1){ui_frame(12,18,15);ui_text(4,13,"ITEM ACTION",14);v11_row(15,v11_assign==0,"USE / INFO",15);v11_row(16,v11_assign==1,"DROP ONE",15);ui_text(2,18,"A CHOOSE  B CANCEL",13);}
 }else if(pause_page==5){v11_header("GEAR // EXPEDITION");if(!v11_menu_mode){static const char*s[3]={"WEAPON","ARMOR","CHARM"};
 for(i=0;i<3;i++){v11_row(5+i*2,i==v11_sel,s[i],13);v11_short(11,5+i*2,v11_equipment[i]<70?V11_ITEMS[v11_equipment[i]].name:"UNEQUIPPED",17,15);}
 ui_text(2,12,"STR",13);ui_num(7,12,v11_str(),15);ui_text(11,12,"DEF",13);ui_num(16,12,v11_def(),15);ui_text(20,12,"MAG",13);ui_num(25,12,v11_mag(),15);ui_text(2,16,"SELECT CAMPAIGN GEAR",14);
 }else{v11_gear_list();start=v11_sel/6*6;for(i=start;i<mini(start+6,v11_list_count);i++){id=v11_list[i];v11_row(4+i-start,i==v11_sel,id==255?"UNEQUIP":V11_ITEMS[id].name,id==255?15:8+V11_ITEMS[id].rarity);}
 id=v11_list[v11_sel];int before[3]={v11_str(),v11_def(),v11_mag()},after[3],old=v11_equipment[v11_slot];v11_equipment[v11_slot]=(u8)id;after[0]=v11_str();after[1]=v11_def();after[2]=v11_mag();v11_equipment[v11_slot]=(u8)old;
 for(i=0;i<3;i++){ui_text(2,11+i,i==0?"STR":i==1?"DEF":"MAG",13);ui_num(7,11+i,before[i],15);ui_text(12,11+i,"->",13);ui_num(17,11+i,after[i],after[i]>=before[i]?9:7);}
 if(id<70)v11_lines(2,14,V11_ITEMS[id].description,26,2,15);}}
 else if(pause_page==28){static const char*sub[5]={"SPELLS","BUDDY","PASSIVE","ULTIMATE","FIELD"};v11_header("SKILLS");ui_text(11,2,sub[v11_sub],13);v11_skills_list();start=v11_sel/6*6;
 for(i=start;i<mini(start+6,v11_list_count);i++){id=v11_list[i];v11_row(4+i-start,i==v11_sel,V11_SKILLS[id].name,v11_skill_known(id)?15:8);if(V11_SKILLS[id].kind<2)ui_num(26,4+i-start,V11_SKILLS[id].mp,13);}
 id=v11_list[v11_sel];v11_icon(id,1);v11_lines(4,12,v11_skill_known(id)?V11_SKILLS[id].description:V11_SKILLS[id].unlock,24,3,15);
 if(v11_sub==0){ui_text(2,15,"SHORTCUTS",13);for(i=0;i<4;i++){ui_text(13+i*4,15,v11_shortcuts[i]<30?"*":"-",14);}}
 if(v11_sub==2){ui_text(2,15,"EQUIPPED",13);for(i=0;i<4;i++)ui_text(13+i*4,15,v11_passives[i]>=50&&v11_passives[i]<75?"*":"-",14);}
 if(v11_sub==3){ui_text(2,15,"ULT CHARGE",13);ui_num(15,15,v11_ult_charge,15);ui_text(19,15,"/100",15);}
 ui_text(2,16,"LEFT/RIGHT TYPE",14);
 if(v11_menu_mode){ui_frame(10,18,15);ui_text(2,11,"ASSIGN SPELL TO SHORTCUT",14);for(i=0;i<4;i++){ui_text(3,13+i,i==v11_assign?">":" ",13);ui_num(5,13+i,i+1,15);v11_short(8,13+i,v11_shortcuts[i]<30?V11_SKILLS[v11_shortcuts[i]].name:"NO SIGNAL",20,15);}ui_text(2,18,"A ASSIGN  B CANCEL",13);}
 }else if(pause_page==18){v11_header("PARTY // FOUND FAMILY");int n=lc_party.count+1;start=v11_sel/5*5;
 for(i=start;i<mini(start+5,n);i++){ui_text(2,5+i-start,i==v11_sel?">":" ",13);v11_short(4,5+i-start,i?v11_creature_name(i-1):v11_cosmos_label(),15,15);}
 if(n<5)v11_short(4,5+n,"NO SIGNAL",15,8);v11_portrait(v11_sel,168,40,0);
 LcCreature*c=v11_sel?&lc_party.slots[v11_sel-1]:0;ui_text(2,11,"LV",13);ui_num(6,11,c?c->level:player_level,15);ui_text(12,11,"TRUST",13);ui_num(19,11,c?c->bond:cosmos.trust,15);
 ui_text(2,12,"ATK",13);ui_num(6,12,c?c->attack:v11_str(),15);ui_text(12,12,"STAGE",13);ui_num(19,12,c?c->stage:v11_cosmos_stage,15);
 ui_text(2,14,(v11_sel==0&&v11_active_cosmos)||(v11_sel==lc_party.active+1&&!v11_active_cosmos)?"ACTIVE COMPANION":"BONDED COMPANION",14);
 ui_text(2,16,"SELECT BOX  A ACTIONS",13);
 }else if(pause_page==27){static const char*a[8]={"SET ACTIVE","TRAIN","EVOLVE","DETAILS","RENAME","EXPORT TO BEAST BOX","RELEASE","CHAT"};v11_header("COMPANION ACTIONS");for(i=0;i<8;i++)v11_row(4+i,v11_sel==i,a[i],15);v11_short(4,12,v11_assign?v11_creature_name(v11_assign-1):v11_cosmos_label(),24,14);
 if(v11_release_confirm)ui_text(2,15,"A AGAIN TO RELEASE. B KEEP.",13);else ui_text(2,15,"BOND AND NAME CARRY FORWARD",13);
 }else if(pause_page==20){v11_header("BEASTS // SEEN");ui_num(20,2,v11_seen_count(),15);ui_text(23,2,"/100",13);start=v11_sel/6*6;
 for(i=start;i<mini(start+6,100);i++)v11_row(4+i-start,i==v11_sel,v11_encounters[i]?V11_CHARACTERS[i].name:"???",v11_encounters[i]?15:8);
 id=v11_sel;if(v11_encounters[id]){vram_copy32(OBJ_VRAM32+V11_TILE_FACE*8,V11_FIELD_ART+id*128,128);for(i=0;i<16;i++)OBJ_PALETTE[14*16+i]=V11_FIELD_PALETTE[i];oam_set32(44,8,88+v11_anim_bob((u32)id*9u),V11_TILE_FACE,14);oam_ui_portrait(44);
 v11_short(6,12,V11_CHARACTERS[id].world<8?V11_WORLDS[V11_CHARACTERS[id].world]:"ALL WORLDS",22,14);v11_lines(6,13,V11_CHARACTERS[id].description,22,2,15);ui_text(2,16,"ENCOUNTERS",13);ui_num(15,16,v11_encounters[id],15);
 }else ui_text(4,12,"NOT MET ON THE MAP YET.",8);
 if(lc_mail_live){int spark=0;for(i=0;i<lc_party.count;i++)if(lc_mail_matches(lc_party.slots[i].identity))spark=i+1;
  if(spark){v11_portrait(spark,176,96,0);if(lc_mail_name[0])ui_text(22,11,lc_mail_name,14);}}
 }else if(pause_page==11){v11_header(v11_sub?"QUESTS // DONE":"QUESTS // ACTIVE");v11_list_count=0;for(i=0;i<15;i++)if(v11_quest_started&(1u<<i)){if(((v11_quest_done>>i)&1)==(v11_sub&1))v11_list[v11_list_count++]=(u8)i;}if(v11_sel>=v11_list_count)v11_sel=0;start=v11_sel/5*5;
 for(i=start;i<mini(start+5,v11_list_count);i++){id=v11_list[i];v11_row(4+i-start,i==v11_sel,V11_QUEST_NAMES[id],v11_track==id?14:15);}
 if(v11_list_count){id=v11_list[v11_sel];v11_short(2,10,V11_QUEST_GIVERS[id],26,13);v11_lines(2,11,V11_QUEST_VOICE[id],26,3,15);
 if(id<8){ui_text(2,14,"CORE",13);ui_text(7,14,v11_cores_found&(1u<<id)?"+":"-",14);ui_text(10,14,"ECHO",13);ui_text(15,14,v11_echo_found&(1u<<id)?"+":"-",14);ui_text(18,14,"FOES",13);ui_num(23,14,mini(3,v11_world_kills[id]),15);ui_text(24,14,"/3",15);v11_short(2,15,v11_signal_goal(id),26,14);}
 else ui_text(2,14,v11_quest_done&(1u<<id)?"QUEST COMPLETE":"A TO TRACK THIS QUEST",14);}
 else ui_text(4,6,"NO SIGNAL",13);
 ui_text(2,16,v11_act_goal(),14);
 }else if(pause_page==1){v11_header(v11_map_legacy?"MAP // ORIGINAL CAMPAIGN":"MAP // EIGHT SIGNALS");
 for(i=0;i<8;i++){int known=v11_map_legacy?(visited_mask&(1u<<i)):(v11_visited&(1u<<i));ui_text(2,4+i,i==v11_sel?">":" ",13);ui_text(4,4+i,known?(v11_map_legacy?"*":(v11_beacons&(1u<<i))?"*":"."):"-",known?14:8);v11_short(6,4+i,known?(v11_map_legacy?WORLDS[i].name:V11_WORLDS[i]):"???",22,known?15:8);if(!v11_map_legacy&&V11_IS_ROOM&&i==v11_world()&&(frame>>4)&1)ui_text(4,4+i,">",13);}
 ui_text(2,14,"THE MAP FILLS AS YOU RECALL",14);ui_text(2,15,V11_IS_ROOM?"START LOCAL LANDMARK MAP":"* KNOWN WORLD",14);ui_text(2,16,"SELECT CAMPAIGN / SIGNALS",13);
 }else if(pause_page==47){v11_draw_local_map();
 }else if(pause_page==9){static const char*s[13]={"AUDIO","TEXT SPEED","BRIGHTNESS","SAVE GAME","LOAD GAME","BEAST BOX","TOUCH CONTROLS","COSMIC REPLAY","AUTO TALK","HERO","CAMPAIGN PACK","MUSIC","SFX"};v11_header("SYSTEM");start=v11_sel/6*6;for(i=start;i<mini(start+6,13);i++){if(i>=11)ui_text(22,4+i-start,lc_level_name(i==11?snd_music:snd_sfx),14);v11_row(4+i-start,i==v11_sel,s[i],15);if(i==0)ui_text(22,4+i-start,audio_on?"ON":"OFF",14);if(i==1)ui_text(22,4+i-start,v11_text_speed==0?"SLOW":v11_text_speed==1?"NORM":"FAST",14);if(i==2)ui_num(24,4+i-start,v11_brightness,14);if(i==6)ui_text(22,4+i-start,touch_mode?"ON":"OFF",14);if(i==7)ui_text(22,4+i-start,buddy_quantum?"ON":"OFF",14);if(i==8)ui_text(22,4+i-start,buddy_talk?"ON":"OFF",14);}
 ui_text(2,15,"ACT I  SYNAPSE ROAD",13);ui_text(2,16,"V11.2 SAVES STILL LOAD",14);
 }else if(pause_page==44){v11_header(v11_sub?"LOAD // THREE SLOTS":"SAVE // THREE SLOTS");for(i=0;i<3;i++){int o=25600+i*2048;ui_text(2,5+i*3,i==v11_sel?">":" ",13);ui_text(4,5+i*3,"SLOT",15);ui_num(10,5+i*3,i+1,15);
 if(v11_slot_valid(i)){int w=SRAM[o+4],room=SRAM[o+5];v11_short(12,5+i*3,w==0&&room>=70&&room<=77?V11_WORLDS[room-70]:WORLDS[w%8].name,16,14);ui_text(4,6+i*3,"LV",13);ui_num(7,6+i*3,SRAM[o+6],15);ui_text(11,6+i*3,"TIME",13);ui_num(16,6+i*3,((int)sr32(o+8))/216000,15);ui_text(20,6+i*3,"%",13);ui_num(23,6+i*3,SRAM[o+7],15);}
 else ui_text(12,5+i*3,"NO SIGNAL",8);}
 if(v11_menu_mode)ui_text(2,15,v11_sub?"A LOAD THIS SLOT? B CANCEL":"A OVERWRITE SLOT? B CANCEL",14);
 }else if(pause_page==26){v11_header("BEAST BOX // QUANTUM BRIDGE");const char*status="OFFLINE MODE";int pick=0;
#if defined(LC_IMPORT_HAS_BCP1)
 LcProfile p;if(v11_snapshot_valid()&&lc_parse_bcp1(lc_imported_companion_bcp1,64,&p)==LC_OK){status="SNAPSHOT VERIFIED";for(i=0;i<lc_party.count;i++)if(lc_party.slots[i].identity==p.public_id){status="BEAST IMPORTED";pick=i+1;break;}}
#endif
 if(lc_mail_live)for(i=0;i<lc_party.count;i++)if(lc_mail_matches(lc_party.slots[i].identity)){status="BEAST IMPORTED";pick=i+1;break;}
 if(v11_export_ready&&v11_export_valid())status="EXPORT AVAILABLE";ui_text(2,4,status,13);
 v11_short(2,6,pick?v11_creature_name(pick-1):"NO LOCAL BEAST",17,14);ui_text(2,8,"ORIGIN",13);ui_text(2,9,pick&&lc_mail_matches(lc_party.slots[pick-1].identity)?"LOCAL MAILBOX":"LOCAL SNAPSHOT",15);ui_text(2,11,"LINEAGE REMAINS",13);ui_text(2,12,"WITH THE RECEIPT",15);
 if(pick&&lc_mail_matches(lc_party.slots[pick-1].identity)&&(lc_mail_trade||lc_mail_grown||lc_mail_epoch)){ui_text(2,14,lc_mail_trade?"TRADE EPOCH":"CAGE EPOCH",13);ui_num(14,14,lc_mail_epoch>999999u?999999:(int)lc_mail_epoch,15);}
 if(pick)v11_portrait(pick,168,48,0);ui_text(2,15,"PRIVATE MEMORY STAYS OUTSIDE",14);ui_text(2,17,"A IMPORT BEAST   B BACK",13);
 }else if(pause_page==42||pause_page==48){v11_header(pause_page==42?"CAMPAIGN PACK":"CAMPAIGN GEAR");if(pause_page==42){for(i=0;i<4;i++){v11_row(5+i*2,i==v11_sel,item_name(i),15);ui_num(24,5+i*2,inv[i],13);}ui_text(2,15,"SELECT ORIGINAL WORKSHOP",14);}
 else{static const char*n[4]={"WEAPON","ARMOR","CHARM","SPELL"};for(i=0;i<4;i++){v11_row(5+i*2,i==v11_sel,n[i],13);v11_short(12,5+i*2,i==0?weapon_name():i==1?armor_name():i==2?charm_name():spell_name(current_spell),16,15);}}
 }else if(pause_page==41){v11_header("WORKSHOP // THE BUILDER");static const u8 r[11]={22,49,67,12,37,47,63,81,79,83,69};start=v11_sel/6*6;for(i=start;i<mini(start+6,11);i++)v11_row(4+i-start,i==v11_sel,i==10?"PACK MULE / 200C":V11_ITEMS[r[i]].name,15);ui_text(2,12,"SCRAP",13);ui_num(9,12,v11_scrap,15);ui_text(16,12,"HERBS",13);ui_num(24,12,v11_herbs,15);ui_text(2,13,"CORES",13);ui_num(9,13,v11_qty[93],15);ui_text(16,13,"CREDITS",13);ui_num(24,13,v11_credits,15);
 if(v11_sel==10)ui_text(2,14,"COST 200 CREDITS",13);else{int cost[3];v11_recipe_cost(v11_sel,cost);ui_text(2,14,"COST S",13);ui_num(8,14,cost[0],v11_scrap>=cost[0]?9:7);ui_text(11,14,"H",13);ui_num(13,14,cost[1],v11_herbs>=cost[1]?9:7);ui_text(17,14,"C",13);ui_num(19,14,cost[2],v11_qty[93]>=cost[2]?9:7);}
 ui_text(2,15,"A BUILD  SELECT REPAIR 10C",14);
 }else if(pause_page==45){v11_header("EVOLUTION // A HELD SIGNAL");v11_short(2,4,v11_assign?v11_creature_name(v11_assign-1):v11_cosmos_label(),26,13);v11_portrait(v11_assign,88,48,v11_evolution?v11_evo_timer:0);ui_text(2,14,v11_evolution?"THE BOND CARRIES FORWARD":"IS CHANGING. LET IT?",14);ui_text(2,17,v11_evolution?"B BACK":"A YES   B NOT YET",13);
 if(v11_evolution){ui_text(2,5,"STAGE",13);ui_num(8,5,v11_evo_old,15);ui_text(11,5,"->",13);ui_num(15,5,v11_evo_old+1,15);if(v11_evo_timer<12){for(i=0;i<256;i++)BG_PALETTE[i]=brighter5(BG_PALETTE[i],20-v11_evo_timer);}}
 }else if(pause_page==49){sol_chat_draw();
 }else if(pause_page==46){v11_header("RENAME // DISPLAY NAME");ui_text(2,5,v11_name_edit,14);ui_text(2,7,"A ADD LETTER. SELECT DONE.",15);static const char*letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ ";for(i=0;i<27;i++){char b[2]={letters[i],0};ui_text(3+(i%9)*3,10+(i/9)*2,b,i==v11_rename_letter?13:15);if(i==v11_rename_letter)ui_text(2+(i%9)*3,10+(i/9)*2,">",13);}ui_text(2,16,"L ERASE  B CANCEL",14);
 }
 v11_menu_notice();v11_ui_dirty=0;return 1;
}
static void v11_craft(void){static const u8 item[10]={22,49,67,12,37,47,63,81,79,83};int n=v11_sel;
 if(n==10){if(v11_skill_known(69)){v11_message("PACK MULE IS ALREADY LEARNED.");return;}if(v11_credits<200){v11_message("PACK MULE NEEDS 200 CREDITS.");return;}v11_credits-=200;v11_learn(69);v11_message("PACK MULE LEARNED. EQUIP IT FOR 60 SLOTS.");save_game();return;}
 if(!v11_qty[95]){v11_message("THE BUILDER'S KIT IS IN RUST MERIDIAN.");return;}
 int cost[3];v11_recipe_cost(n,cost);int s=cost[0],h=cost[1],c=cost[2];
 if(v11_scrap<s||v11_herbs<h||v11_qty[93]<c){v11_message("MORE MATERIALS NEEDED. CACHES HOLD SCRAP AND HERBS; RIFTS HOLD CORES.");return;}
 if(!v11_inventory_add(item[n],1))return;v11_scrap-=s;v11_herbs-=h;v11_qty[93]-=c;v11_crafted++;
 if(v11_qty[22]&&v11_qty[49]&&v11_qty[67])v11_quest_finish(14);v11_unlock();v11_message("OLD PIECES. MY ASSEMBLY. ITEM CRAFTED.");save_game();
}
static int v11_menu_handled(int p){return p==40||p==4||p==5||p==28||p==18||p==20||p==11||p==1||p==9||p==26||p==27||p==41||p==42||p==44||p==45||p==46||p==47||p==48||p==49;}
static void v11_menu_changed(void){if(v11_page_previous==pause_page)return;v11_ui_dirty=1;v11_list_kind=255;v11_page_previous=pause_page;v11_sel=v11_detail=v11_menu_mode=0;
 if(pause_page==18)v11_sel=v11_active_cosmos?0:lc_party.count?lc_party.active+1:0;if(pause_page==1)v11_sel=(u8)v11_world();}
static void v11_back(void){v11_sel=v11_detail=v11_menu_mode=0;v11_release_confirm=0;
 if(pause_page==45){if(V11_IS_ROOM)v11_palette();else set_world_palette(current_world);}
 if(pause_page==47){pause_page=1;v11_page_previous=255;return;}
 if(pause_page==27||pause_page==45||pause_page==46||pause_page==49)pause_page=18;
 else if(pause_page==44||pause_page==42||pause_page==48)pause_page=9;
 else if(pause_page==26)pause_page=v11_parent==18?18:0;else pause_page=0;v11_page_previous=255;}
static int v11_update_pause(u16 k){int i,id,n;
 if(pause_page==0){if(k&KEY_A&&pause_sel==8)v11_parent=0;if(k&KEY_SELECT){pause_page=40;v11_menu_reset();return 1;}if(k&KEY_B)v11_resume_art();return 0;}
 if(!v11_menu_handled(pause_page))return 0;if(k||pause_page==45||(pause_page==1&&(frame&31)==0))v11_ui_dirty=1;v11_menu_changed();
 if(v11_detail==2){if(k&(KEY_A|KEY_B)){v11_detail=0;v11_notice_timer=0;}return 1;}
 if(pause_page==45&&v11_evolution){if(v11_evo_timer<60)v11_evo_timer++;v11_ui_dirty=1;if(v11_evo_timer>=60||k&KEY_B){v11_evolution=0;v11_back();}return 1;}
 if(!k)return 1;
 if(k&KEY_B){if(v11_menu_mode||v11_detail){v11_menu_mode=v11_detail=0;v11_sel=0;}else v11_back();return 1;}
 if(pause_page!=27&&pause_page!=41&&pause_page!=42&&pause_page!=44&&pause_page!=45&&pause_page!=46&&pause_page!=48&&pause_page!=49&&pause_page!=26&&!v11_menu_mode&&!v11_detail&&(k&(KEY_L|KEY_R))){for(i=0;i<9;i++)if(V11_TABS[i]==pause_page){pause_page=V11_TABS[wrapi(i+((k&KEY_R)?1:-1),9)];v11_sub=0;v11_menu_reset();return 1;}}
 if(pause_page==40){if(k&KEY_SELECT){pause_page=3;v11_sel=0;}return 1;}
 if(pause_page==4){v11_items_list();n=v11_list_count;
 if(!v11_detail){if(k&KEY_UP)v11_sel=(u8)wrapi(v11_sel-1,maxi(1,n));if(k&KEY_DOWN)v11_sel=(u8)wrapi(v11_sel+1,maxi(1,n));if(k&KEY_LEFT){v11_cat=(v11_cat+3)%4;v11_sel=0;}if(k&KEY_RIGHT){v11_cat=(v11_cat+1)%4;v11_sel=0;}if(k&KEY_SELECT){v11_sort=(v11_sort+1)%3;v11_sel=0;}if(k&KEY_A&&n){v11_detail=1;v11_assign=0;}}
 else{if(k&(KEY_UP|KEY_DOWN))v11_assign^=1;if(k&KEY_A&&n){id=v11_list[v11_sel];
 if(v11_assign){if(id>=90||v11_equipment[0]==id||v11_equipment[1]==id||v11_equipment[2]==id)v11_message("KEY ITEMS AND EQUIPPED GEAR STAY WITH ARIN.");else{v11_qty[id]--;v11_claim_pending();save_game();v11_message("I LEFT ONE ITEM FOR THE NEXT TRAVELER.");}}
 else if(id>=70&&id<90){if(!V11_IS_ROOM&&(id==70||id==71)){if((id==70&&player.hp==max_hp)||(id==71&&player_mp==max_mp))v11_message("THIS STAT IS ALREADY FULL.");else{v11_qty[id]--;if(id==70)player.hp=(u8)mini(max_hp,player.hp+5);else player_mp=(u8)mini(max_mp,player_mp+3);v11_message("RESTORED. CAMPAIGN SCALE IS KEPT.");save_game();}}else v11_consume(id);}else v11_message(V11_ITEMS[id].description);v11_detail=2;}}
 }else if(pause_page==5){if(v11_menu_mode)v11_gear_list();n=v11_menu_mode?v11_list_count:3;if(k&KEY_UP)v11_sel=(u8)wrapi(v11_sel-1,n);if(k&KEY_DOWN)v11_sel=(u8)wrapi(v11_sel+1,n);
 if(k&KEY_SELECT&&!v11_menu_mode){pause_page=48;v11_menu_reset();return 1;}if(k&KEY_A){if(!v11_menu_mode){v11_slot=v11_sel;v11_sel=0;v11_menu_mode=1;v11_gear_list();}else{v11_equipment[v11_slot]=v11_list[v11_sel];v11_hp=(u16)mini(v11_hp,v11_max_hp());v11_mp=(u16)mini(v11_mp,v11_max_mp());v11_menu_mode=0;v11_sel=v11_slot;save_game();}}
 }else if(pause_page==28){v11_skills_list();n=v11_list_count;
 if(v11_menu_mode){if(k&KEY_UP)v11_assign=(v11_assign+3)%4;if(k&KEY_DOWN)v11_assign=(v11_assign+1)%4;if(k&KEY_A){v11_shortcuts[v11_assign]=v11_list[v11_sel];v11_menu_mode=0;save_game();}return 1;}
 if(k&KEY_UP)v11_sel=(u8)wrapi(v11_sel-1,n);if(k&KEY_DOWN)v11_sel=(u8)wrapi(v11_sel+1,n);if(k&KEY_LEFT){v11_sub=(v11_sub+4)%5;v11_sel=0;}if(k&KEY_RIGHT){v11_sub=(v11_sub+1)%5;v11_sel=0;}
 if(k&KEY_A){v11_skills_list();id=v11_list[v11_sel];if(!v11_skill_known(id)){v11_message(V11_SKILLS[id].unlock);v11_detail=2;}else if(v11_sub==0){v11_menu_mode=1;v11_assign=0;}
 else if(v11_sub==1||v11_sub==4){if(!V11_IS_ROOM)v11_message("USE THESE ABILITIES ON THE EIGHT SIGNALS ROAD. CAMPAIGN SPELLS REMAIN IN CAMPAIGN GEAR.");else{int old=game_mode;game_mode=MODE_SURFACE;v11_use_skill(id);if(game_mode==MODE_SURFACE)game_mode=(u8)old;}v11_detail=2;}
 else if(v11_sub==2){int found=-1,free=-1;for(i=0;i<4;i++){if(v11_passives[i]==id)found=i;if(v11_passives[i]==255&&free<0)free=i;}if(found>=0){if(id==69&&v11_slots_used()>40){v11_message("USE OR DROP ITEMS UNTIL THE BAG FITS 40 SLOTS.");v11_detail=2;}else v11_passives[found]=255;}else if(free>=0)v11_passives[free]=(u8)id;else{v11_message("FOUR PASSIVES MAX. UNEQUIP ONE FIRST.");v11_detail=2;}save_game();}else{v11_ultimate=(u8)id;save_game();}}
 }else if(pause_page==18){n=lc_party.count+1;if(k&KEY_UP)v11_sel=(u8)wrapi(v11_sel-1,n);if(k&KEY_DOWN)v11_sel=(u8)wrapi(v11_sel+1,n);if(k&KEY_SELECT){v11_parent=18;pause_page=26;v11_page_previous=255;return 1;}if(k&KEY_A){v11_assign=v11_sel;if(v11_sel)lc_party_sel=v11_sel-1;pause_page=27;v11_sel=0;v11_page_previous=27;}}
 else if(pause_page==27){if(k&KEY_UP){v11_sel=(v11_sel+7)%8;v11_release_confirm=0;}if(k&KEY_DOWN){v11_sel=(v11_sel+1)%8;v11_release_confirm=0;}
 if(k&KEY_A){LcCreature*c=v11_assign?&lc_party.slots[v11_assign-1]:0;
 if(v11_sel==0){v11_active_cosmos=(u8)(!v11_assign);if(c){lc_party.active=v11_assign-1;v9_bonded=c->bond>=55;v9_bond_type=c->species%EN_COUNT;}save_game();v11_back();}
 if(v11_sel==1){if(v11_scrap<3&&inv[ITEM_SHARD]<2){v11_message("TRAIN WITH THREE SCRAP OR TWO CAMPAIGN SHARDS.");v11_detail=2;}else{if(v11_scrap>=3)v11_scrap-=3;else inv[ITEM_SHARD]-=2;if(c)lc_bond(&lc_party,v11_assign-1,(c->species>=128?c->species-128:c->species)%3,85);else v11_trust(8);v11_unlock();save_game();v11_message("WE TRAINED TOGETHER. THE BOND GREW.");v11_detail=2;}}
 if(v11_sel==2){pause_page=45;v11_page_previous=45;v11_evolution=0;v11_evo_old=c?c->stage:v11_cosmos_stage;}if(v11_sel==3)v11_back();if(v11_sel==4){pause_page=46;v11_page_previous=46;v11_name_edit[0]=0;v11_rename_pos=v11_rename_letter=0;}
 if(v11_sel==7){pause_page=49;v11_page_previous=49;sol_chat_open();sol_spark_chirp(c?c->identity:0x43534d53u);}
 if(v11_sel==5){v11_prepare_export(v11_assign);v11_detail=2;}if(v11_sel==6){if(!c||c->species>=LC_SPECIES_IMPORTED){v11_message("COSMOS AND IMPORTED PUBLIC IDENTITIES STAY WITH YOU.");v11_detail=2;}else if(!v11_release_confirm)v11_release_confirm=1;else{int ix=v11_assign-1;if(lc_release_wild(&lc_party,ix)==LC_OK){for(i=ix;i<11;i++)copystr(v11_names[i],v11_names[i+1],12);v11_names[11][0]=0;save_game();v11_back();}}}}}
 else if(pause_page==45){if(k&KEY_A){LcCreature*c=v11_assign?&lc_party.slots[v11_assign-1]:0;int ok;if(c)ok=lc_evolve(&lc_party,v11_assign-1,(u8)(v11_qty[96]?1:0))==LC_OK;else{ok=v11_cosmos_stage<2&&v11_bond()>=(v11_cosmos_stage==0?5:10);if(ok)v11_cosmos_stage++;}if(ok){v11_evolution=1;v11_evo_timer=0;save_game();}else{v11_message("NOT YET. FIRST: LV12/BOND55. NEXT: LV28/BOND80. IMPORTS ALSO NEED HEARTWOOD SIGIL.");v11_detail=2;}}}
 else if(pause_page==49){sol_chat_input_step(k);}
 else if(pause_page==46){if(k&KEY_LEFT)v11_rename_letter=(u8)wrapi(v11_rename_letter-1,27);if(k&KEY_RIGHT)v11_rename_letter=(u8)wrapi(v11_rename_letter+1,27);if(k&KEY_UP)v11_rename_letter=(u8)wrapi(v11_rename_letter-9,27);if(k&KEY_DOWN)v11_rename_letter=(u8)wrapi(v11_rename_letter+9,27);if(k&KEY_A&&v11_rename_pos<11){v11_name_edit[v11_rename_pos++]=v11_rename_letter==26?' ':'A'+v11_rename_letter;v11_name_edit[v11_rename_pos]=0;}if(k&KEY_L&&v11_rename_pos)v11_name_edit[--v11_rename_pos]=0;if(k&KEY_SELECT){if(v11_name_edit[0])copystr(v11_assign?v11_names[v11_assign-1]:v11_cosmos_name,v11_name_edit,12);save_game();v11_back();}}
 else if(pause_page==20){if(k&KEY_UP)v11_sel=(u8)wrapi(v11_sel-1,100);if(k&KEY_DOWN)v11_sel=(u8)wrapi(v11_sel+1,100);}
 else if(pause_page==11){if(k&(KEY_LEFT|KEY_RIGHT)){v11_sub^=1;v11_sel=0;}if(k&KEY_UP)v11_sel=(u8)wrapi(v11_sel-1,maxi(1,v11_list_count));if(k&KEY_DOWN)v11_sel=(u8)wrapi(v11_sel+1,maxi(1,v11_list_count));if(k&KEY_A&&v11_list_count){id=v11_list[v11_sel];v11_track=v11_track==id?255:id;save_game();}if(k&KEY_SELECT){pause_page=13;v11_page_previous=255;}}
 else if(pause_page==1){if(k&KEY_UP)v11_sel=(v11_sel+7)%8;if(k&KEY_DOWN)v11_sel=(v11_sel+1)%8;if(k&KEY_SELECT)v11_map_legacy^=1;if(k&KEY_START&&V11_IS_ROOM){pause_page=47;v11_page_previous=255;return 1;}if(k&KEY_A){if(v11_map_legacy)v11_message("THE ORIGINAL WORLDS ARE REACHED WITH LUNA-ARC.");else if(v11_beacons&(1u<<v11_sel))v11_enter(v11_sel);else v11_message("THIS BEACON IS NOT LIT. WALK THERE AND RETURN ITS SIGNAL.");v11_detail=2;}}
 else if(pause_page==9){if(k&KEY_UP)v11_sel=(v11_sel+12)%13;if(k&KEY_DOWN)v11_sel=(v11_sel+1)%13;if(v11_sel>=11&&(k&(KEY_A|KEY_LEFT|KEY_RIGHT))){lc_audio_option(v11_sel-10,(k&KEY_LEFT)?-1:(k&KEY_RIGHT)?1:0);return 1;}if(k&KEY_A){if(v11_sel==0)audio_on^=1;if(v11_sel==1)v11_text_speed=(v11_text_speed+1)%3;if(v11_sel==2)v11_brightness=v11_brightness%5+1;
 if(v11_sel==3||v11_sel==4){v11_sub=v11_sel==4;pause_page=44;v11_sel=0;v11_page_previous=44;}else if(v11_sel==5){pause_page=26;v11_parent=9;v11_page_previous=255;}else if(v11_sel==6){touch_mode^=1;save_game();}else if(v11_sel==7){buddy_quantum^=1;save_game();}else if(v11_sel==8){buddy_talk^=1;save_game();}else if(v11_sel==9){pause_page=15;role_preview=actor_style;}else if(v11_sel==10){pause_page=42;v11_menu_reset();}else save_game();}}
 else if(pause_page==44){if(!v11_menu_mode){if(k&KEY_UP)v11_sel=(v11_sel+2)%3;if(k&KEY_DOWN)v11_sel=(v11_sel+1)%3;}if(k&KEY_A){if(!v11_menu_mode&&v11_slot_valid(v11_sel))v11_menu_mode=1;else{if(v11_sub)v11_slot_load(v11_sel);else v11_slot_save(v11_sel);v11_menu_mode=0;if(game_mode==MODE_PAUSE)v11_detail=2;}}}
 else if(pause_page==26){if(k&KEY_A){v11_import_snapshot();v11_detail=2;}}
 else if(pause_page==41){if(k&KEY_UP)v11_sel=(v11_sel+10)%11;if(k&KEY_DOWN)v11_sel=(v11_sel+1)%11;if(k&KEY_A){v11_craft();v11_detail=2;}if(k&KEY_SELECT){int cost=v11_charm(56)?5:10;if(v11_credits>=cost){v11_credits-=cost;v11_repair_all();save_game();v11_message("ALL GEAR REPAIRED.");}else v11_message("REPAIR NEEDS TEN CREDITS, FIVE WITH GEAR TOOTH.");v11_detail=2;}}
 else if(pause_page==42||pause_page==48){if(k&KEY_UP)v11_sel=(v11_sel+3)%4;if(k&KEY_DOWN)v11_sel=(v11_sel+1)%4;if(pause_page==42){if(k&KEY_A)use_item(v11_sel);if(k&KEY_SELECT){pause_page=21;p4_craft_sel=0;}}else if(k&KEY_A){if(v11_sel==0){if(weapon==0&&gear_owned&2)weapon=1;else if(weapon==1&&gear_owned&16)weapon=2;else weapon=0;}if(v11_sel==1)armor=(u8)((gear_owned&4)?!armor:0);if(v11_sel==2)charm=(u8)((gear_owned&8)?!charm:0);if(v11_sel==3){u8 s=current_spell;do{s=(s+1)%4;}while(s>0&&!(keys_found&(1u<<(s-1))));current_spell=s;}refresh_player_frames();save_game();}}
 return 1;
}
static const u8 V11_SHOP_ITEMS[8]={70,71,72,73,75,80,40,76};
static int v11_shop_price(int id,int sell){int p=V11_ITEMS[id].price;if(p<1)p=id>=70?12:20+V11_ITEMS[id].rarity*15;if(sell)return maxi(1,p/3);int discount=(v11_charm(65)?15:0)+(v11_passive(70)?10:0)+(v11_speaker==3?v11_corvus_trust/10:0);return maxi(1,p*(100-mini(35,discount))/100);}
static void v11_shop_list(void){int i;v11_list_count=0;if(v11_shop_sell){for(i=0;i<90;i++)if(v11_qty[i]&&v11_equipment[0]!=i&&v11_equipment[1]!=i&&v11_equipment[2]!=i)v11_list[v11_list_count++]=(u8)i;}else for(i=0;i<8;i++)v11_list[v11_list_count++]=V11_SHOP_ITEMS[i];if(v11_shop_sel>=v11_list_count)v11_shop_sel=0;}
static int v11_shop_input(u16 k){int id,p;v11_shop_list();if(k&KEY_B){v11_shop=0;v11_resume_art();return 1;}if(k&(KEY_LEFT|KEY_RIGHT)){v11_shop_sell^=1;v11_shop_sel=0;}if(k&KEY_UP)v11_shop_sel=(u8)wrapi(v11_shop_sel-1,maxi(1,v11_list_count));if(k&KEY_DOWN)v11_shop_sel=(u8)wrapi(v11_shop_sel+1,maxi(1,v11_list_count));if(k&KEY_A&&v11_list_count){id=v11_list[v11_shop_sel];p=v11_shop_price(id,v11_shop_sell);if(v11_shop_sell){v11_qty[id]--;v11_credits=(u16)mini(65535,v11_credits+p);v11_message("SOLD. ALL SALES ARE STORIES.");}else if(v11_qty[id]>=99)v11_message("THIS STACK IS FULL. USE OR SELL ONE FIRST.");else if(v11_credits<p)v11_message("NOT ENOUGH CREDITS. THE ROAD WILL PROVIDE.");else if(v11_inventory_add(id,1)){v11_credits-=p;if(v11_speaker==3)v11_corvus_trust=(u8)mini(100,v11_corvus_trust+5);v11_message("PURCHASE COMPLETE.");}v11_unlock();save_game();}return 1;}
static void v11_draw_shop(void){int i,start;ui_frame(0,19,15);v11_menu_palette();v11_short(2,2,V11_CHARACTERS[v11_speaker].name,24,14);ui_text(2,3,"CREDITS",13);ui_num(11,3,v11_credits,15);ui_text(20,3,v11_shop_sell?"SELL":"BUY",14);v11_shop_list();start=v11_shop_sel/6*6;for(i=start;i<mini(start+6,v11_list_count);i++){int id=v11_list[i];v11_row(5+i-start,i==v11_shop_sel,V11_ITEMS[id].name,8+V11_ITEMS[id].rarity);ui_num(24,5+i-start,v11_shop_price(id,v11_shop_sell),15);}if(v11_notice[0])v11_lines(2,12,v11_notice,26,3,14);ui_text(2,17,"A TRADE   B EXIT   L/R",13);}
