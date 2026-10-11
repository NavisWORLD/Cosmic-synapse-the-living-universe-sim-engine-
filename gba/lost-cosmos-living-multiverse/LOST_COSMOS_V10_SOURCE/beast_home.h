/* V11.5 BEAST HOME. See beast_home_state.h for the save layout.
   Original in-game text. The home is a real room (world 0, room 90) with
   its own map, collision and triggers; the player walks in through the
   cottage door in Brindlemark and every care action is a controller press. */
#ifndef BEAST_HOME_H
#define BEAST_HOME_H
/* Interior bounds (tiles) and the spots the beast walks to (pixels). */
#define BH_BOWL_PX 188
#define BH_BOWL_PY 210
#define BH_TOY_PX 212
#define BH_TOY_PY 262
#define BH_BED_PX 296
#define BH_BED_PY 204
static u32 bh_rng=0x2545F491u;
static u8 bh_rand(u8 n){bh_rng=bh_rng*1103515245u+12345u;return (u8)((bh_rng>>16)%n);}
static void bh_reset(void){int i;for(i=0;i<BH_RECORDS;i++){bh_id[i]=0;bh_full[i]=bh_joy[i]=bh_rest[i]=0;bh_visits[i]=0;bh_care[i]=0;bh_flags[i]=0;}bh_cur=-1;}
static void bh_save_into(u8*b){int i,o;
 for(i=678;i<680+BH_RECORDS*12;i++)b[i]=0;
 b[676]='H';b[677]=1;
 for(i=0;i<BH_RECORDS;i++){o=680+i*12;
  b[o]=(u8)bh_id[i];b[o+1]=(u8)(bh_id[i]>>8);b[o+2]=(u8)(bh_id[i]>>16);b[o+3]=(u8)(bh_id[i]>>24);
  b[o+4]=bh_full[i];b[o+5]=bh_joy[i];b[o+6]=bh_rest[i];b[o+7]=bh_visits[i];
  b[o+8]=(u8)bh_care[i];b[o+9]=(u8)(bh_care[i]>>8);b[o+10]=bh_flags[i];
 }}
static void bh_restore_from(const u8*b,int valid){int i,o;
 bh_reset();
 if(!valid||b[676]!='H'||b[677]!=1)return;
 for(i=0;i<BH_RECORDS;i++){o=680+i*12;
  bh_id[i]=(u32)b[o]|((u32)b[o+1]<<8)|((u32)b[o+2]<<16)|((u32)b[o+3]<<24);
  bh_full[i]=(u8)mini(100,b[o+4]);bh_joy[i]=(u8)mini(100,b[o+5]);bh_rest[i]=(u8)mini(100,b[o+6]);
  bh_visits[i]=b[o+7];bh_care[i]=(u16)(b[o+8]|(b[o+9]<<8));bh_flags[i]=b[o+10];
 }}
static LcCreature*bh_creature(void){return lc_party.count?&lc_party.slots[lc_party.active]:0;}
/* The care record for the beast that is home now, keyed by its identity. */
static int bh_find(int create){LcCreature*c=bh_creature();int i,slot=-1;u32 id;
 if(!c)return -1;id=c->identity;
 for(i=0;i<BH_RECORDS;i++)if(bh_id[i]==id&&id)return i;
 if(!create)return -1;
 for(i=0;i<BH_RECORDS;i++)if(!bh_id[i]){slot=i;break;}
 if(slot<0){int best=0;for(i=1;i<BH_RECORDS;i++)if(bh_care[i]+bh_visits[i]<bh_care[best]+bh_visits[best])best=i;slot=best;}
 bh_id[slot]=id;bh_full[slot]=60;bh_joy[slot]=60;bh_rest[slot]=60;bh_visits[slot]=0;bh_care[slot]=0;bh_flags[slot]=0;
 return slot;}
static const char*bh_name(void){LcCreature*c=bh_creature();
 if(!c)return "BEAST";
 if(lc_mail_matches(c->identity)&&lc_mail_name[0])return lc_mail_name;
 return lc_species_name(c->species);}
static void bh_say2(const char*a,const char*b){char line[90];int n=0;
 while(*a&&n<88)line[n++]=*a++;while(*b&&n<88)line[n++]=*b++;line[n]=0;say(line);}
static void bh_say3(const char*a,const char*b,const char*c){char line[90];int n=0;
 while(*a&&n<88)line[n++]=*a++;while(*b&&n<88)line[n++]=*b++;while(*c&&n<88)line[n++]=*c++;line[n]=0;say(line);}
static void bh_put(int x,int y,int tile,int pal,int col,int trig){
 if((unsigned)x>=MAP_W||(unsigned)y>=MAP_H)return;
 set_map_entry(x,y,map_attr(tile,pal));collision[mi(x,y)]=(u8)col;trigger[mi(x,y)]=(u8)trig;}
static void bh_walk_to(s16 x,s16 y,u8 goal){bh_tx=x;bh_ty=y;bh_goal=goal;bh_state=BHS_WALK;}
static void bh_emote_show(u8 e,u16 frames){bh_emote=e;bh_emote_timer=frames;}
static void bh_place_beast(void){bh_x=29*8+4;bh_y=29*8;bh_state=BHS_IDLE;bh_timer=40;bh_face=0;bh_bowl=0;bh_emote=255;bh_emote_timer=0;}
/* Brindlemark: a small cottage with a door, west of the crossroads. */
static void beast_home_place_room2(void){int x;
 for(x=BH_DOOR_TX-2;x<=BH_DOOR_TX+2;x++){map_put(x,BH_DOOR_TY-2,T_WALL,4,C_WALL,0);map_put(x,BH_DOOR_TY-1,T_WALL,4,C_WALL,0);}
 map_put(BH_DOOR_TX-2,BH_DOOR_TY,T_WALL,4,C_WALL,0);map_put(BH_DOOR_TX-1,BH_DOOR_TY,T_WALL,4,C_WALL,0);
 map_put(BH_DOOR_TX+1,BH_DOOR_TY,T_WALL,4,C_WALL,0);map_put(BH_DOOR_TX+2,BH_DOOR_TY,T_WALL,4,C_WALL,0);
 map_put(BH_DOOR_TX,BH_DOOR_TY,T_DOOR,6,C_FREE,TR_BH_ENTER);
 map_put(BH_DOOR_TX,BH_DOOR_TY+1,T_PATH,1,C_FREE,0);map_put(BH_DOOR_TX,BH_DOOR_TY+2,T_PATH,1,C_FREE,0);}
static void beast_home_generate(void){int x,y,i;
 for(y=0;y<MAP_H;y++)for(x=0;x<MAP_W;x++){
  int h=(x*13+y*17)&3;
  if(x>=BH_X0&&x<=BH_X1&&y>=BH_Y0&&y<=BH_Y1)continue;
  if(((x*37+y*53+x*y*3)&31)==3)bh_put(x,y,T_FLOWER,0,C_WALL,0);
  else bh_put(x,y,224+h,0,C_WALL,0);
 }
 for(y=BH_Y0+1;y<BH_Y1;y++)for(x=BH_X0+1;x<BH_X1;x++)
  bh_put(x,y,V115_HOME_TILE_BASE+(((x*5+y*3)&7)==0?V115_HOME_FLOOR_B:V115_HOME_FLOOR_A),6,C_FREE,0);
 for(x=BH_X0;x<=BH_X1;x++){bh_put(x,BH_Y0,T_WALL,6,C_WALL,0);bh_put(x,BH_Y1,T_WALL,6,C_WALL,0);}
 for(y=BH_Y0;y<=BH_Y1;y++){bh_put(BH_X0,y,T_WALL,6,C_WALL,0);bh_put(BH_X1,y,T_WALL,6,C_WALL,0);}
 for(i=0;i<4;i++)bh_put(i<2?23+i*3:33+(i-2)*3,BH_Y0,V115_HOME_TILE_BASE+V115_HOME_WINDOW,6,C_WALL,0);
 bh_put(29,BH_Y0,V115_HOME_TILE_BASE+V115_HOME_NAMEPLATE,6,C_WALL,TR_BH_PLATE);
 for(y=28;y<=31;y++)for(x=27;x<=32;x++)bh_put(x,y,V115_HOME_TILE_BASE+V115_HOME_RUG,6,C_FREE,0);
 bh_put(36,24,V115_HOME_TILE_BASE+V115_HOME_BED_TL,6,C_WALL,TR_BH_BED);bh_put(37,24,V115_HOME_TILE_BASE+V115_HOME_BED_TR,6,C_WALL,TR_BH_BED);
 bh_put(36,25,V115_HOME_TILE_BASE+V115_HOME_BED_BL,6,C_WALL,TR_BH_BED);bh_put(37,25,V115_HOME_TILE_BASE+V115_HOME_BED_BR,6,C_WALL,TR_BH_BED);
 bh_put(22,24,V115_HOME_TILE_BASE+V115_HOME_FOOD_BOWL,6,C_WALL,TR_BH_FOOD);
 bh_put(23,24,V115_HOME_TILE_BASE+V115_HOME_WATER_BOWL,6,C_WALL,TR_BH_FOOD);
 bh_put(24,32,V115_HOME_TILE_BASE+V115_HOME_TOY_BALL,6,C_WALL,TR_BH_TOY);
 bh_put(BH_X0+1,BH_Y0+1,V115_HOME_TILE_BASE+V115_HOME_PLANT_POT,6,C_WALL,0);bh_put(BH_X1-1,BH_Y0+1,V115_HOME_TILE_BASE+V115_HOME_PLANT_POT,6,C_WALL,0);
 bh_put(BH_X0+1,BH_Y1-1,V115_HOME_TILE_BASE+V115_HOME_PLANT_POT,6,C_WALL,0);bh_put(BH_X1-1,BH_Y1-1,V115_HOME_TILE_BASE+V115_HOME_PLANT_POT,6,C_WALL,0);
 bh_put(29,BH_Y1-1,V115_HOME_TILE_BASE+V115_HOME_DOORMAT,6,C_FREE,0);
 bh_put(29,BH_Y1,T_DOOR,6,C_FREE,TR_BH_EXIT);
 for(i=0;i<4;i++)upload_obj16(BH_EMOTE_TILE+i*4,V115_HOME_EMOTES[i]);
 bh_cur=(s8)bh_find(1);
 if(bh_x<BH_X0*8+8||bh_x>BH_X1*8-8||bh_y<BH_Y0*8+12||bh_y>BH_Y1*8-4)bh_place_beast();
}
static void beast_home_enter(void){
 if(!lc_party.count){say("THE BEAST HOME IS EMPTY. BOND WITH A BEAST OR BRING ONE THROUGH THE BRIDGE.");return;}
 current_room=BH_ROOM;current_layer=1;player.x=29*8+4;player.y=(BH_Y1-2)*8+4;player.face=0;
 cosmos.x=player.x+16;cosmos.y=player.y-12;
 bh_x=-1;bh_place_beast();
 generate_surface();refresh_camera();
 if(bh_cur>=0&&bh_visits[bh_cur]<255)bh_visits[bh_cur]++;
 bh_say3("WELCOME HOME. ",bh_name()," PERKS UP WHEN YOU WALK IN.");
 bh_emote_show(V115_EMOTE_HEART,90);
 save_game();}
static void beast_home_leave(void){
 current_room=2;current_layer=1;player.x=BH_DOOR_TX*8+4;player.y=(BH_DOOR_TY+2)*8;player.face=1;
 cosmos.x=player.x+16;cosmos.y=player.y-12;spark_follow_init=0;bh_emote=255;OAM16[BH_EMOTE_OAM*4]=0x0200;
 generate_surface();refresh_camera();
 bh_say2(bh_name()," WATCHES YOU GO FROM THE WINDOW.");
 save_game();}
static void bh_bond_up(void){LcCreature*c=bh_creature();if(c&&c->bond<100)c->bond++;}
static void bh_care_done(void){if(bh_cur>=0&&bh_care[bh_cur]<65535u)bh_care[bh_cur]++;bh_bond_up();save_game();}
static void bh_show_record(void){char line[90];int n=0;const char*s;int v[5],k;
 static const char*lab[5]={" FULL "," JOY "," REST "," VISITS "," CARE "};
 if(bh_cur<0){say("NO BEAST LIVES HERE YET.");return;}
 v[0]=bh_full[bh_cur];v[1]=bh_joy[bh_cur];v[2]=bh_rest[bh_cur];v[3]=bh_visits[bh_cur];v[4]=bh_care[bh_cur];
 for(s=bh_name();*s&&n<20;)line[n++]=*s++;
 for(k=0;k<5;k++){unsigned d=(unsigned)v[k],p=1;for(s=lab[k];*s;)line[n++]=*s++;
  while(p*10<=d)p*=10;while(p){line[n++]=(char)('0'+d/p%10);p/=10;}}
 line[n]=0;say(line);}
static int beast_home_interact(u8 t){
 if(t==TR_BH_ENTER){beast_home_enter();return 1;}
 if(!BH_IS_ROOM)return 0;
 if(t==TR_BH_EXIT){beast_home_leave();return 1;}
 if(t==TR_BH_PLATE){bh_show_record();return 1;}
 if(bh_cur<0||!lc_party.count)return t==TR_BH_FOOD||t==TR_BH_TOY||t==TR_BH_BED;
 if(t!=TR_BH_FOOD&&t!=TR_BH_TOY&&t!=TR_BH_BED)return 0;
 if(bh_state==BHS_SLEEP&&t!=TR_BH_BED){bh_say2(bh_name()," IS ASLEEP. LET IT DREAM.");return 1;}
 if(t==TR_BH_FOOD){bh_bowl=1;bh_walk_to(BH_BOWL_PX,BH_BOWL_PY,BHS_EAT);bh_say3("YOU FILL THE BOWL. ",bh_name()," TROTS OVER.");return 1;}
 if(t==TR_BH_TOY){bh_walk_to(BH_TOY_PX,BH_TOY_PY,BHS_PLAY);bh_say3("YOU ROLL THE BALL. ",bh_name()," CHASES IT.");return 1;}
 if(bh_state==BHS_SLEEP){bh_say2(bh_name()," IS ALREADY CURLED UP.");return 1;}
 bh_walk_to(BH_BED_PX,BH_BED_PY,BHS_SLEEP);bh_say3("YOU FLUFF THE BED. ",bh_name()," CIRCLES AND LIES DOWN.");return 1;}
/* A with nothing else nearby, next to the beast: pet it. */
static int beast_home_pet(void){
 if(!BH_IS_ROOM||bh_cur<0||!lc_party.count)return 0;
 if(iabs(bh_x-player.x)>22||iabs(bh_y-player.y)>22)return 0;
 if(bh_state==BHS_SLEEP){bh_say2(bh_name()," STIRS, SIGHS AND KEEPS SLEEPING.");return 1;}
 if(bh_pet_cd){bh_say2(bh_name()," LEANS INTO YOUR HAND.");bh_emote_show(V115_EMOTE_HEART,40);return 1;}
 bh_joy[bh_cur]=(u8)mini(100,bh_joy[bh_cur]+10);bh_state=BHS_HAPPY;bh_timer=96;bh_face=(u8)(player.x<bh_x);
 bh_pet_cd=240;bh_emote_show(V115_EMOTE_HEART,96);bh_say2(bh_name()," WIGGLES WITH JOY.");bh_care_done();return 1;}
static void beast_home_tick(void){int dx,dy;
 if(!BH_IS_ROOM||game_mode!=MODE_SURFACE||!lc_party.count)return;
 if(bh_cur<0||bh_id[bh_cur]!=lc_party.slots[lc_party.active].identity)bh_cur=(s8)bh_find(1);
 if(bh_cur<0)return;
 bh_tick++;
 if(bh_pet_cd)bh_pet_cd--;
 if(bh_emote_timer){bh_emote_timer--;if(!bh_emote_timer)bh_emote=255;}
 /* Needs drift slowly while you are home (about one point every 20 s). */
 if((bh_tick%1200)==0){
  if(bh_full[bh_cur])bh_full[bh_cur]--;if(bh_joy[bh_cur])bh_joy[bh_cur]--;
  if(bh_state!=BHS_SLEEP&&bh_rest[bh_cur])bh_rest[bh_cur]--;}
 switch(bh_state){
 case BHS_WALK:
  dx=signi(bh_tx-bh_x);dy=signi(bh_ty-bh_y);
  if((bh_tick&1)||bh_goal!=BHS_IDLE){bh_x=(s16)(bh_x+dx);bh_y=(s16)(bh_y+dy);if(dx||dy)bh_moved++;}
  if(dx)bh_face=(u8)(dx<0);
  if(bh_x==bh_tx&&bh_y==bh_ty){bh_state=bh_goal;
   bh_timer=bh_goal==BHS_EAT?150:bh_goal==BHS_PLAY?180:bh_goal==BHS_SLEEP?300:(u16)(50+bh_rand(90));
   if(bh_goal==BHS_EAT)bh_emote_show(V115_EMOTE_FOOD,150);
   if(bh_goal==BHS_PLAY)bh_emote_show(V115_EMOTE_NOTE,180);
   if(bh_goal==BHS_SLEEP)bh_emote_show(V115_EMOTE_SLEEP,300);}
  break;
 case BHS_IDLE:
  if(bh_timer)bh_timer--;
  else if(bh_rest[bh_cur]<20)bh_walk_to(BH_BED_PX,BH_BED_PY,BHS_SLEEP);
  else{s16 x=(s16)((BH_X0+3)*8+bh_rand(14)*8+4),y=(s16)((BH_Y0+4)*8+bh_rand(8)*8);bh_walk_to(x,y,BHS_IDLE);}
  break;
 case BHS_EAT:
  if(bh_timer)bh_timer--;
  else{if(bh_bowl){bh_full[bh_cur]=(u8)mini(100,bh_full[bh_cur]+40);bh_bowl=0;}
   bh_state=BHS_IDLE;bh_timer=60;bh_emote_show(V115_EMOTE_HEART,60);bh_say2(bh_name()," LICKS THE BOWL CLEAN.");bh_care_done();}
  break;
 case BHS_PLAY:
  if(bh_timer)bh_timer--;
  if((bh_timer&31)==0)bh_face^=1;
  bh_x=(s16)(bh_x+((bh_timer&31)<16?1:-1)*((bh_timer&3)==0));
  if(!bh_timer){bh_joy[bh_cur]=(u8)mini(100,bh_joy[bh_cur]+30);
   bh_rest[bh_cur]=(u8)(bh_rest[bh_cur]>10?bh_rest[bh_cur]-10:0);bh_full[bh_cur]=(u8)(bh_full[bh_cur]>5?bh_full[bh_cur]-5:0);
   bh_state=BHS_IDLE;bh_timer=60;bh_emote_show(V115_EMOTE_HEART,60);bh_say2(bh_name()," BRINGS THE BALL BACK, PANTING.");bh_care_done();}
  break;
 case BHS_SLEEP:
  if(bh_timer)bh_timer--;
  else{bh_rest[bh_cur]=100;bh_state=BHS_IDLE;bh_timer=60;bh_emote_show(V115_EMOTE_HEART,60);
   bh_say2(bh_name()," WAKES UP RESTED AND STRETCHES.");bh_care_done();}
  break;
 case BHS_HAPPY:
  if(bh_timer)bh_timer--;else{bh_state=BHS_IDLE;bh_timer=40;}
  break;
 }}
static void beast_home_sprites(void){LcCreature*c=bh_creature();int sx,sy,bob=0,i,tri;
 if(!BH_IS_ROOM||bh_cur<0||!c){OAM16[BH_EMOTE_OAM*4]=0x0200;if(BH_IS_ROOM)OAM16[42*4]=0x0200;return;}
 for(i=0;i<16;i++)OBJ_PALETTE[BH_EMOTE_PAL*16+i]=V115_HOME_EMOTE_PAL[i];
 tri=(bh_timer&15)<8?(bh_timer&7):(7-(bh_timer&7));
 if(bh_state==BHS_SLEEP)bob=(bh_tick>>5)&1;
 else if(bh_state==BHS_PLAY||bh_state==BHS_HAPPY)bob=-tri;
 else if(bh_state==BHS_WALK)bob=-(int)((bh_tick>>3)&1);
 else bob=(bh_tick>>4)&1;
 sx=bh_x-cam_x;sy=bh_y-cam_y+bob;
 {u8 sp=c->species;
  if(sp>=1&&sp<=8){int tile=384+(sp-1)*24+c->stage*8+((bh_state==BHS_SLEEP?0:(bh_tick>>(bh_state==BHS_WALK?3:4))&1)*4);
   oam_set(42,sx-8,sy-12,tile,4+sp,bh_face);}
  else if(lc_has_import_art(c))lc_draw_import_field(42,sx-16,sy-24,bh_face,0,c->identity);
  else{u8 typ=(u8)(sp%EN_COUNT);oam_set(42,sx-8,sy-12,60+typ*4,5+typ,bh_face);}
  if(bh_emote!=255){int up=(bh_emote_timer>>3)&3,top=(sp>=1&&sp<=8)?30:40;
   oam_set(BH_EMOTE_OAM,sx-2,sy-top-up,BH_EMOTE_TILE+bh_emote*4,BH_EMOTE_PAL,0);}
  else OAM16[BH_EMOTE_OAM*4]=0x0200;
 }}
static int beast_home_hud(void){static const char*st[6]={"IS LAZING","IS TROTTING","IS EATING","IS PLAYING","IS ASLEEP","IS HAPPY"};
 if(!BH_IS_ROOM||game_mode!=MODE_SURFACE)return 0;
 ui_fill_rows(18,19,62,15);
 if(bh_cur<0||!lc_party.count){ui_text(2,18,"BEAST HOME",14);ui_text(2,19,"NO BEAST LIVES HERE",15);return 1;}
 ui_text(2,18,bh_name(),14);ui_text(16,18,st[bh_state%6],13);
 ui_text(1,19,"FULL",13);ui_num(6,19,bh_full[bh_cur],15);
 ui_text(10,19,"JOY",13);ui_num(14,19,bh_joy[bh_cur],15);
 ui_text(18,19,"REST",13);ui_num(23,19,bh_rest[bh_cur],15);
 return 1;}
#endif
