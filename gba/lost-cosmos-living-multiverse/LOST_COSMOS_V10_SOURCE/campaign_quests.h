/* THE HEART OF ERIDORIA campaign spine and PROLOGUE: ASH IN THE FORGE.
   All dialogue below is original game-adaptation text. It is not quoted
   from the owner's private manuscript. */
#ifndef CAMPAIGN_QUESTS_H
#define CAMPAIGN_QUESTS_H
static void campaign_reset(void){int i;for(i=0;i<CQ_COUNT;i++)cq_state[i]=CQ_LOCKED;
 pro_flags=0;pro_choice=pro_strikes=pro_raid_kills=pro_raid_spared=0;
 pro_ui=pro_sel=pro_seat=pro_heat=pro_heat_dir=pro_flash=0;pro_script=pro_script_n=0;pro_cards=0;pro_card_n=pro_card_i=pro_card_tag=0;}
static void campaign_save_into(u8*b){int i;
 b[CQ_SRAM_AT]='Q';b[CQ_SRAM_AT+1]=1;
 for(i=0;i<10;i++)b[CQ_SRAM_AT+2+i]=0;
 for(i=0;i<CQ_COUNT;i++)b[CQ_SRAM_AT+2+(i>>2)]|=(u8)((cq_state[i]&3u)<<((i&3)*2));
 b[CQ_SRAM_AT+12]=(u8)pro_flags;b[CQ_SRAM_AT+13]=(u8)(pro_flags>>8);
 b[CQ_SRAM_AT+14]=pro_choice;b[CQ_SRAM_AT+15]=pro_strikes;b[CQ_SRAM_AT+16]=pro_raid_kills;b[CQ_SRAM_AT+17]=pro_raid_spared;}
/* Older saves have no campaign block. A save that already shows play beyond
   the opening keeps playing where it was: the prologue is recorded as done
   (PF_MIGRATED) and Q05 is the next node. A save made right at the opening
   starts the prologue at Q00. No later quest is marked complete here. */
static int campaign_old_progress(void){
 return chapter||story_flags||keys_found||ending||postgame||quest_started||kill_count||
  (visited_mask&~1u)||v11_act||v11_visited||v11_quest_started||player_level>1||current_world||
  (current_world==0&&current_room!=2);}
static void campaign_migrate(void){int i;campaign_reset();
 if(campaign_old_progress()){for(i=0;i<5;i++)cq_state[i]=CQ_DONE;cq_state[5]=CQ_ACTIVE;
  pro_flags=PF_MIGRATED|PF_FORGED|PF_COSMOS|PF_RAID_CLEAR|PF_BEACON|PF_LAUNCH;}
 else cq_state[0]=CQ_ACTIVE;}
static void campaign_restore_from(const u8*b,int valid){int i;
 if(!valid||b[CQ_SRAM_AT]!='Q'||b[CQ_SRAM_AT+1]!=1){campaign_migrate();return;}
 campaign_reset();
 for(i=0;i<CQ_COUNT;i++)cq_state[i]=(u8)((b[CQ_SRAM_AT+2+(i>>2)]>>((i&3)*2))&3u);
 pro_flags=(u16)(b[CQ_SRAM_AT+12]|((u16)b[CQ_SRAM_AT+13]<<8));pro_choice=(u8)(b[CQ_SRAM_AT+14]<=2?b[CQ_SRAM_AT+14]:0);
 pro_strikes=(u8)mini(3,b[CQ_SRAM_AT+15]);
 /* A raid in progress restarts whole when the game is loaded. */
 if(cq_state[1]==CQ_ACTIVE&&!(pro_flags&PF_RAID_CLEAR)){pro_raid_kills=pro_raid_spared=0;}
 else{pro_raid_kills=(u8)mini(3,b[CQ_SRAM_AT+16]);pro_raid_spared=(u8)mini(3,b[CQ_SRAM_AT+17]);}}
static int prologue_active(void){return cq_state[0]!=CQ_LOCKED&&cq_state[4]!=CQ_DONE;}
static void cq_set(int q,u8 s){if(q>=0&&q<CQ_COUNT)cq_state[q]=s;}
static void prologue_begin(void){campaign_reset();cq_set(0,CQ_ACTIVE);}
static int pro_in_brindlemark(void){return current_world==0&&current_room==2&&game_mode!=MODE_SPACE;}
static void pro_cards_open(const ProCard*c,int n,int tag){pro_cards=c;pro_card_n=(u8)n;pro_card_i=0;pro_card_tag=(u8)tag;pro_ui=4;dialogue_timer=0;}
/* ---------- story cards ---------- */
static const ProCard PRO_AWAKEN[]={
 {"THE FORGE","THE BLADE RINGS TRUE. UNDER THE ANVIL, A BURIED CRYSTAL STARTS TO HUM."},
 {"COSMOS","I REMEMBER A SKY MADE OF SQUARES. I DON'T REMEMBER WHO BROKE IT."},
 {"ARIN","THE IRON IS STILL HOT. WHO ARE YOU, AND WHY ARE YOU IN MY FORGE?"},
 {"COSMOS","A VOICE THAT WAS RECORDED BEFORE THE FRACTURE. STAY CLOSE. SOMETHING IS COMING."},
 {"BRINDLEMARK","BELLS AT THE GATE! MALAKAR'S RAIDERS TORE THE SKY OPEN. GLITCHLINGS POUR THROUGH."}};
static const ProCard PRO_RAID_DONE[]={
 {"BRINDLEMARK","THE LAST GLITCHLING IS GONE. SMOKE RISES FROM THE STOREHOUSE."},
 {"VILLAGER","THE INJURED ARE STILL IN THE SQUARE! AND THE STORES ARE BURNING!"}};
static const ProCard PRO_DEFEND[]={
 {"ARIN","HOLD THE DOOR! BUCKETS, NOW!"},
 {"SMITH OREN","YOU SAVED THE WINTER STORES, ARIN. TAKE THIS ETHER AND THESE CREDITS. WE OWE YOU."},
 {"COSMOS","YOU PROTECTED WHAT THEY NEED TO LIVE. I WILL REMEMBER THAT CHOICE."}};
static const ProCard PRO_CARRY[]={
 {"ARIN","LEAN ON ME. ONE STEP, THEN ANOTHER."},
 {"HEALER SELA","EVERY ONE OF THEM IS BREATHING BECAUSE OF YOU. TAKE THESE POTIONS. YOU'LL NEED THEM."},
 {"COSMOS","YOU CARRIED THEM FIRST. THE STORES CAN BE REBUILT. I WILL REMEMBER THAT CHOICE."}};
static const ProCard PRO_BEACON_LIT[]={
 {"THE BEACON","THREE CRYSTAL SEATS CLICK HOME. LIGHT CLIMBS THE TOWER."},
 {"MIRA","LOOK AT THE MOUNTAIN! IT STAYED WHERE IT BELONGS. THE BEACON IS HOLDING THE DISTANCE."},
 {"COSMOS","THAT SIGNAL... SOMETHING OLD JUST ANSWERED IT, SOUTHWEST OF HERE."}};
static const ProCard PRO_LAUNCH[]={
 {"LUNA-ARC","THE BURIED HULL SHRUGS OFF A CENTURY OF MOSS. STAR LANES FLICKER ACROSS ITS DECK."},
 {"COSMOS","I KNOW THIS SHIP. AND IT KNOWS ME. WE WERE BUILT TO KEEP THE WORLDS CONNECTED."},
 {"ASTRID","MALAKAR WANTS THE HEART OF ERIDORIA. WE FIND IT FIRST, BUT WE DON'T BECOME HIM."},
 {"MIRA","THE BEACON WILL HOLD BRINDLEMARK. GO. COME BACK WITH THE REST OF THE SKY."},
 {"ARIN","BEHIND US THE SKY FLICKERS LIKE A FAILING LAMP. THE METAL IS STILL HOT. THERE IS WORK TO DO."}};
static const ProCard PRO_REWARD[]={
 {"PROLOGUE COMPLETE","FORGE KEY. ARIN'S MAP. FIRST MEMORY. COSMOS BOND. LUNA-ARC PASSAGE."},
 {"NEXT: ACT I","OAKWOOD LIES ON THE EAST ROAD FROM BRINDLEMARK. ASK FOR LORD RAVENSWOOD."}};
#define PRO_CARD_SET(a) a,(int)(sizeof(a)/sizeof(a[0]))
static void pro_after_cards(int tag){
 if(tag==1){spawn_monsters();say("Q01 DRIVE OFF THE RAID. A STRIKES. SELECT+A OPENS A DUEL: TALK CAN SPARE.");save_game();}
 else if(tag==2){pro_ui=3;pro_sel=0;return;}
 else if(tag==3){cq_set(1,CQ_DONE);cq_set(2,CQ_ACTIVE);say("Q02 MIRA IS AT THE NORTH BEACON. THE ROAD UP THE MIDDLE.");save_game();}
 else if(tag==4){cq_set(2,CQ_DONE);cq_set(3,CQ_ACTIVE);say("Q03 TALK TO MIRA, THE TRAVELER, AND ASTRID PAST THE SOUTHWEST GATE.");save_game();}
 else if(tag==5){pro_cards_open(PRO_CARD_SET(PRO_REWARD),6);return;}
 else if(tag==6){board_ship();return;}
 pro_ui=0;}
/* ---------- Q00 forge ---------- */
static void pro_forge_open(void){pro_ui=1;pro_heat=0;pro_heat_dir=0;pro_flash=0;dialogue_timer=0;}
static void pro_forge_strike(void){
 if(pro_heat>=12&&pro_heat<=15){pro_strikes++;pro_flash=24;lc_sfx(SFX_CRIT);
  if(pro_strikes>=3){pro_flags|=PF_FORGED|PF_COSMOS;str_stat=(u8)mini(99,str_stat+1);
   cosmos.trust=(u8)mini(255,cosmos.trust+10);cosmos.memory_flags|=MEM_FIRST_FORGE;
   cq_set(0,CQ_DONE);cq_set(1,CQ_ACTIVE);save_game();pro_cards_open(PRO_CARD_SET(PRO_AWAKEN),1);}
  else save_game();}
 else{pro_flash=200;lc_sfx(SFX_CANCEL);}}
/* ---------- Q01 raid ---------- */
static const u8 PRO_RAID_X[3]={28,31,37},PRO_RAID_Y[3]={33,24,30};
static int prologue_spawn(void){int i;
 if(!pro_in_brindlemark()||cq_state[1]!=CQ_ACTIVE||(pro_flags&PF_RAID_CLEAR))return 0;
 for(i=0;i<3;i++)spawn_enemy(i,PRO_RAID_X[i],PRO_RAID_Y[i],EN_GLITCH,0);
 pro_raid_kills=pro_raid_spared=0;return 1;}
static void prologue_enemy_down(Enemy*e,int defeated){int i=(int)(e-enemies);
 if(!pro_in_brindlemark()||cq_state[1]!=CQ_ACTIVE||(pro_flags&PF_RAID_CLEAR)||i<0||i>2)return;
 if(defeated)pro_raid_kills=(u8)mini(3,pro_raid_kills+1);else pro_raid_spared=(u8)mini(3,pro_raid_spared+1);}
/* Mercy: in the raid duel, TALK calms a glitchling at any HP. It leaves through
   the tear instead of joining, so a full party never blocks the prologue. */
static int prologue_raid_mercy(Enemy*e){int i=(int)(e-enemies);
 if(!pro_in_brindlemark()||cq_state[1]!=CQ_ACTIVE||(pro_flags&PF_RAID_CLEAR)||i<0||i>2||!e->active)return 0;
 prologue_enemy_down(e,0);e->active=0;cosmos.trust=(u8)mini(255,cosmos.trust+4);add_xp(3);save_game();return 1;}
static int pro_raid_left(void){int i,n=0;for(i=0;i<3;i++)if(enemies[i].active)n++;return n;}
static void pro_choose(int c){pro_choice=(u8)c;pro_flags|=PF_RAID_CLEAR|PF_CHOICE;
 credits=(u8)clampi(credits+10,0,255);
 if(c==1){credits=(u8)clampi(credits+8,0,255);inv[ITEM_ETHER]=(u8)mini(99,inv[ITEM_ETHER]+1);}
 else{inv[ITEM_POTION]=(u8)mini(99,inv[ITEM_POTION]+2);cosmos.trust=(u8)mini(255,cosmos.trust+6);}
 cosmos.memory_flags|=MEM_PLAYER_HELPED;save_game();
 if(c==1)pro_cards_open(PRO_CARD_SET(PRO_DEFEND),3);else pro_cards_open(PRO_CARD_SET(PRO_CARRY),3);}
/* ---------- Q02 beacon seats ---------- */
static const u16 PRO_SEAT_KEYS[3]={KEY_LEFT,KEY_UP,KEY_RIGHT};
/* ---------- NPC scripts ---------- */
static int prologue_npc_visible(int id){
 if(id==NPC_PRO_MIRA)return cq_state[0]!=CQ_LOCKED&&!(pro_flags&PF_MIGRATED)&&cq_state[4]!=CQ_DONE;
 if(id==NPC_PRO_TRAVELER)return cq_state[0]!=CQ_LOCKED&&!(pro_flags&PF_MIGRATED)&&cq_state[4]!=CQ_DONE;
 return 1;}
static void pro_say_lines(int id,const char*a,const char*b,const char*c){
 pro_script=(u8)id;pro_script_lines[0]=a;pro_script_lines[1]=b;pro_script_lines[2]=c;pro_script_n=(u8)(c?3:(b?2:1));}
static void prologue_npc_speak(void){int id=npc_dialogue_id;pro_script=0;pro_script_n=0;
 if(!prologue_active())return;
 if(id==NPC_PRO_MIRA){
  if(cq_state[2]==CQ_ACTIVE&&!(pro_flags&PF_FUSE))
   pro_say_lines(1,"ARIN! THE BEACON BLEW ITS FUSE WHEN THE SKY TORE. WITHOUT IT, THE MOUNTAINS DRIFT.",
    "HERE IS MY SPARE FUSE. THE THREE CRYSTAL SEATS TURN LEFT, THEN UP, THEN RIGHT.",
    "IF IT SPARKS, YOU TURNED ONE WRONG. START OVER. IT CAN'T HURT YOU. MUCH.");
  else if(cq_state[2]==CQ_ACTIVE)pro_say_lines(2,"LEFT, UP, RIGHT. THE SEATS ARE ON THE BEACON JUST WEST OF ME.",0,0);
  else if(cq_state[3]==CQ_ACTIVE&&!(pro_flags&PF_MIRA))
   pro_say_lines(3,"YOU FELT THAT? THE BEACON WOKE SOMETHING AT THE ORIGIN LANDING. AN OLD SHIP.",
    pro_choice==2?"YOU CARRIED SELA'S PATIENTS OUT. I SAW. I'M COMING WITH YOU AS FAR AS THE SHIP.":
                  "YOU KEPT THE STORES FROM BURNING. OREN WON'T STOP TALKING ABOUT IT.",
    "TALK TO THE TRAVELER AND TO ASTRID. THEN WE BOARD LUNA-ARC TOGETHER.");
  else if(cq_state[0]!=CQ_DONE||cq_state[1]==CQ_ACTIVE)
   pro_say_lines(4,"NOT NOW, ARIN! THE BEACON IS DARK AND THE VILLAGE NEEDS YOU.",0,0);
  else pro_say_lines(5,"THE BEACON HOLDS. GO FIND ASTRID AND THE SHIP.",0,0);
 }else if(id==NPC_PRO_TRAVELER){
  if(cq_state[3]==CQ_ACTIVE&&!(pro_flags&PF_TRAVELER))
   pro_say_lines(6,"A ROBED TRAVELER SHAKES ASH FROM HIS HOOD. YOU'RE THE SMITH WHO FOUGHT AT THE GATE.",
    "MALAKAR IS COLLECTING THE OLD ARTIFACTS. HE CALLS IT MERCY: ONE SEALED WORLD, NO MORE FEAR.",
    "IF HE TAKES THE HEART OF ERIDORIA, EVERY ROAD WILL LEAD TO HIM. DON'T LET THEM.");
  else if(cq_state[3]==CQ_ACTIVE)pro_say_lines(7,"THE HEART WAS BUILT TO HOLD DISTANCE AND MEMORY. REMEMBER THAT.",0,0);
  else pro_say_lines(8,"THE TRAVELER WATCHES THE TORN SKY. NOT YET, SMITH. YOUR VILLAGE COMES FIRST.",0,0);
 }else if(id==13&&cq_state[3]==CQ_ACTIVE&&!(pro_flags&PF_ASTRID)){
  pro_say_lines(9,"ARIN. I'VE READ EVERY RECORD OF THE FIRST GUARDIANS. NONE OF THEM MENTION A VOICE IN A FORGE.",
   "COSMOS IS OLDER THAN OUR ARCHIVE. THE HEART OF ERIDORIA HELD THE WORLDS APART AND STILL CONNECTED.",
   "LUNA-ARC IS ON THE LANDING PAD HERE AT THE ORIGIN. WHEN YOU'RE READY, BOARD IT. I'M COMING.");
 }}
static const char*prologue_npc_line(void){
 if(pro_script&&pro_script_n)return pro_script_lines[npc_dialogue_page<pro_script_n?npc_dialogue_page:pro_script_n-1];
 if(npc_dialogue_id==14&&npc_dialogue_page==0&&pro_choice&&!(pro_flags&PF_MIGRATED)&&cq_state[5]!=CQ_DONE)
  return pro_choice==1?"ARIN, YOU SAVED OUR WINTER STORES. BRINDLEMARK WILL EAT BECAUSE OF YOU.":
                       "ARIN, YOU CARRIED OUR WOUNDED. NO ONE HERE WILL FORGET IT.";
 return 0;}
static void pro_check_q03(void){
 if(cq_state[3]==CQ_ACTIVE&&(pro_flags&(PF_MIRA|PF_TRAVELER|PF_ASTRID))==(PF_MIRA|PF_TRAVELER|PF_ASTRID)){
  cq_set(3,CQ_DONE);cq_set(4,CQ_ACTIVE);say("Q04 BOARD LUNA-ARC AT THE ORIGIN LANDING PAD, PAST THE SOUTHWEST GATE.");}}
static int prologue_npc_advance(void){
 if(!pro_script||!pro_script_n)return 0;
 if(npc_dialogue_page+1<pro_script_n){npc_dialogue_page++;return 1;}
 if(pro_script==1)pro_flags|=PF_FUSE;
 if(pro_script==3)pro_flags|=PF_MIRA;
 if(pro_script==6)pro_flags|=PF_TRAVELER;
 if(pro_script==9)pro_flags|=PF_ASTRID;
 pro_check_q03();pro_script=0;pro_script_n=0;save_game();npc_dialogue_active=0;npc_dialogue_page=0;return 1;}
/* ---------- interaction hooks ---------- */
static int prologue_interact(u8 t){
 if(!pro_in_brindlemark())return 0;
 if(t==TR_TERMINAL&&near_trigger_x==PRO_FORGE_TX&&near_trigger_y==PRO_FORGE_TY&&cq_state[0]==CQ_ACTIVE){pro_forge_open();return 1;}
 if(t==TR_PRO_BEACON){
  if(pro_flags&PF_BEACON){say("THE BEACON HUMS. THE MOUNTAINS STAY WHERE THEY BELONG.");return 1;}
  if(cq_state[2]!=CQ_ACTIVE){say("THE NORTH BEACON IS DARK. ITS FUSE IS BLOWN.");return 1;}
  if(!(pro_flags&PF_FUSE)){say("THE BEACON NEEDS A FUSE. MIRA IS STANDING RIGHT THERE.");return 1;}
  pro_ui=2;pro_seat=0;pro_flash=0;dialogue_timer=0;return 1;}
 if(t==TR_PRO_STALL){shop_open=1;shop_sel=0;return 1;}
 return 0;}
static void prologue_shop_bought(void){if(prologue_active()&&!(pro_flags&PF_BOUGHT)){pro_flags|=PF_BOUGHT;}}
static int prologue_board_ship(void){
 if(cq_state[4]!=CQ_ACTIVE||(pro_flags&PF_LAUNCH))return 0;
 pro_flags|=PF_LAUNCH|PF_FORGE_KEY|PF_MAP;cosmos.memory_flags|=MEM_SHIP|MEM_FIRST_FORGE;
 cosmos.trust=(u8)mini(255,cosmos.trust+15);cq_set(4,CQ_DONE);cq_set(5,CQ_ACTIVE);save_game();
 pro_cards_open(PRO_CARD_SET(PRO_LAUNCH),5);return 1;}
static void prologue_place_room2(void){
 map_put(PRO_BEACON_TX,PRO_BEACON_TY,(pro_flags&PF_BEACON)?T_STAR:T_CRYSTAL,3,C_FREE,TR_PRO_BEACON);
 map_put(PRO_STALL_TX,PRO_STALL_TY,T_LANTERN,3,C_FREE,TR_PRO_STALL);}
/* ---------- per-frame input (returns 1 when the prologue owns the pad) ---------- */
static int prologue_update(u16 newk){
 if(pro_ui==1){
  if(!pro_heat_dir){if(++pro_heat>=19)pro_heat_dir=1;}else{if(!--pro_heat)pro_heat_dir=0;}
  if(pro_flash&&pro_flash!=200)pro_flash--;
  if(newk&KEY_B){pro_ui=0;say("THE IRON COOLS. THE FURNACE WILL WAIT FOR YOU.");return 1;}
  if(newk&KEY_A)pro_forge_strike();return 1;}
 if(pro_ui==2){
  if(newk&KEY_B){pro_ui=0;pro_seat=0;say("THE SEATS SNAP BACK. MIRA SAID LEFT, UP, RIGHT.");return 1;}
  if(newk&(KEY_LEFT|KEY_RIGHT|KEY_UP|KEY_DOWN)){
   if(newk&PRO_SEAT_KEYS[pro_seat]){pro_seat++;pro_flash=0;lc_sfx(SFX_CONFIRM);
    if(pro_seat>=3){pro_flags|=PF_BEACON;cosmos.trust=(u8)mini(255,cosmos.trust+6);
     map_put(PRO_BEACON_TX,PRO_BEACON_TY,T_STAR,3,C_FREE,TR_PRO_BEACON);save_game();
     pro_cards_open(PRO_CARD_SET(PRO_BEACON_LIT),4);}}
   else{pro_seat=0;pro_flash=1;lc_sfx(SFX_HIT);}}
  return 1;}
 if(pro_ui==3){
  if(newk&(KEY_UP|KEY_DOWN))pro_sel^=1;
  if(newk&KEY_A)pro_choose(pro_sel?2:1);
  return 1;}
 if(pro_ui==4){
  if(newk&(KEY_A|KEY_B)){if(pro_card_i+1<pro_card_n)pro_card_i++;else{int tag=pro_card_tag;pro_ui=0;pro_after_cards(tag);}}
  return 1;}
 if(pro_in_brindlemark()&&cq_state[1]==CQ_ACTIVE&&cq_state[0]==CQ_DONE&&!(pro_flags&PF_RAID_CLEAR)&&!pro_raid_left()&&
    pro_raid_kills+pro_raid_spared>=3){pro_cards_open(PRO_CARD_SET(PRO_RAID_DONE),2);return 1;}
 return 0;}
/* ---------- drawing ---------- */
static int prologue_draw(void){int i;
 if(pro_ui==1){ui_frame(9,19,15);ui_text(2,10,"BRINDLEMARK FORGE",14);ui_text(2,11,"STRIKE WHILE THE IRON GLOWS",15);
  for(i=0;i<20;i++){const char*c=(i==pro_heat)?"*":(i>=12&&i<=15)?"+":"-";ui_text(5+i,13,c,(i==pro_heat)?14:(i>=12&&i<=15)?13:8);}
  ui_text(2,15,"STRIKES",13);for(i=0;i<3;i++)ui_text(11+i*2,15,i<pro_strikes?"*":"-",i<pro_strikes?14:8);
  ui_text(2,16,pro_flash==200?"TOO COLD OR TOO HOT. AGAIN.":pro_flash?"CLANG! A TRUE STRIKE.":"WAIT FOR THE + ZONE.",pro_flash==200?8:15);
  ui_text(2,18,"A STRIKE   B STEP AWAY",14);return 1;}
 if(pro_ui==2){ui_frame(9,19,15);ui_text(2,10,"NORTH BEACON // FUSE",14);ui_text(2,11,"TURN THE CRYSTAL SEATS",15);
  for(i=0;i<3;i++){ui_text(4+i*7,13,"SEAT",13);ui_num(9+i*7,13,i+1,13);ui_text(5+i*7,14,i<pro_seat?"SET":"...",i<pro_seat?14:8);}
  ui_text(2,16,pro_flash?"SPARKS! THE SEATS RESET.":"MIRA: LEFT, UP, RIGHT.",pro_flash?8:15);
  ui_text(2,18,"D-PAD TURN   B STEP AWAY",14);return 1;}
 if(pro_ui==3){ui_frame(9,19,15);ui_text(2,10,"ARIN'S FIRST CHOICE",14);
  ui_wrap_text(11,"THE STOREHOUSE BURNS. THE INJURED CALL FROM THE SQUARE.",15,3);
  ui_text(2,14,pro_sel==0?">":" ",13);ui_text(4,14,"DEFEND THE STOREHOUSE",pro_sel==0?14:15);
  ui_text(2,16,pro_sel==1?">":" ",13);ui_text(4,16,"CARRY THE INJURED",pro_sel==1?14:15);
  ui_text(2,18,"UP DOWN CHOOSE   A DECIDE",14);return 1;}
 if(pro_ui==4&&pro_cards){const ProCard*c=&pro_cards[pro_card_i];ui_frame(11,19,15);ui_text(2,12,c->speaker,14);
  ui_wrap_text(13,c->text,15,4);ui_text(2,18,pro_card_i+1<pro_card_n?"A NEXT":"A CONTINUE",14);return 1;}
 return 0;}
static const char*prologue_hud_line(void){static char line[30];
 if(!prologue_active())return 0;
 if(cq_state[0]==CQ_ACTIVE)return "Q00 FORGE: A AT THE FURNACE";
 if(cq_state[1]==CQ_ACTIVE){if(pro_flags&PF_RAID_CLEAR)return "Q01 BRINDLEMARK IS SAFE";
  copystr(line,"Q01 DRIVE OFF THE RAID 0/3",30);line[23]=(char)('0'+mini(3,pro_raid_kills+pro_raid_spared));return line;}
 if(cq_state[2]==CQ_ACTIVE)return (pro_flags&PF_FUSE)?"Q02 TURN THE BEACON SEATS":"Q02 FIND MIRA AT N BEACON";
 if(cq_state[3]==CQ_ACTIVE){copystr(line,"Q03 MIRA- TRAVELER- ASTRID-",30);
  if(pro_flags&PF_MIRA)line[8]='+';if(pro_flags&PF_TRAVELER)line[18]='+';if(pro_flags&PF_ASTRID)line[26]='+';return line;}
 if(cq_state[4]==CQ_ACTIVE)return "Q04 BOARD LUNA-ARC / ORIGIN";
 return 0;}
#endif
