/* ACT I: THE FIRST HEART (Q05-Q09). See act1_heart_state.h for the layout.
   All dialogue is original game-adaptation text written for the cartridge. */
#ifndef ACT1_HEART_H
#define ACT1_HEART_H
static void act1_reset(void){a1_flags=0;a1_regent=a1_reply=a1_sentries=0;a1_rune_step=a1_parry=a1_boss=a1_strikes=0;
 a1_sel=a1_choice_tag=a1_deflects=a1_lances=a1_heat=a1_heat_dir=a1_flash=0;a1_notice="";}
static void act1_save_into(u8*b){int o=A1_SRAM_AT;
 b[o]='A';b[o+1]=1;b[o+2]=(u8)a1_flags;b[o+3]=(u8)(a1_flags>>8);b[o+4]=a1_regent;b[o+5]=a1_reply;b[o+6]=a1_sentries;b[o+7]=0;}
static int a1_q(int q){return cq_state[q];}
/* Saves without the 'A' block: rebuild Act I from the story flags the old
   route already earned. Nothing past what the save proves is marked. */
static void act1_migrate(void){int i,done=4;
 act1_reset();
 if(story_flags&ST_HEART)done=9;else if(story_flags&ST_MALAKAR)done=8;else if(story_flags&ST_PUZZLE)done=7;else if(story_flags&ST_OAKWOOD)done=6;
 if(done<5){if(cq_state[5]==CQ_LOCKED&&cq_state[4]==CQ_DONE)cq_set(5,CQ_ACTIVE);return;}
 a1_flags=A1F_MIGRATED|A1F_MET_RAVEN|A1F_PELL_HEALED|A1F_MAP_FOUND|A1F_MAP_RETURNED|A1F_JOURNAL;
 if(done>=7)a1_flags|=A1F_ASCENT|A1F_GUARD|A1F_MOULD|A1F_ORE|A1F_KEY|A1F_VAULT_OPEN|A1F_KEEP|A1F_ORDER;a1_sentries=7;
 if(done>=8)a1_regent=1;
 if(done>=9)a1_flags|=A1F_MALAKAR;
 /* The story flags prove the prologue was behind this save. */
 for(i=0;i<5;i++)if(cq_state[i]!=CQ_DONE){cq_set(i,CQ_DONE);pro_flags|=PF_MIGRATED;}
 for(i=5;i<=done;i++)cq_set(i,CQ_DONE);
 if(done<9)cq_set(done+1,CQ_ACTIVE);else if(cq_state[10]==CQ_LOCKED)cq_set(10,CQ_ACTIVE);}
static void act1_restore_from(const u8*b,int valid){int o=A1_SRAM_AT;
 if(!valid||b[o]!='A'||b[o+1]!=1){act1_migrate();return;}
 act1_reset();a1_flags=(u16)(b[o+2]|((u16)b[o+3]<<8));a1_regent=(u8)(b[o+4]<=2?b[o+4]:0);a1_reply=(u8)(b[o+5]<=2?b[o+5]:0);a1_sentries=(u8)(b[o+6]&7);}
static int a1_has(u16 f){return (a1_flags&f)==f;}
static void a1_go(int room,int tx,int ty){current_room=(u8)room;current_layer=1;player.x=(s16)(tx*8);player.y=(s16)(ty*8);
 cosmos.x=player.x+16;cosmos.y=player.y-12;a1_rune_step=0;generate_surface();refresh_camera();save_game();}
/* ---------- story cards ---------- */
static const ProCard A1_RAVEN_MAP[]={
 {"LORD RAVENSWOOD","YOU FOUND IT. AUREL'S HAND, EVERY LINE OF IT. MY BROTHER DREW THIS MAP THE YEAR HE VANISHED."},
 {"LORD RAVENSWOOD","HE FOUND A TEMPLE THE MOUNTAIN HAD SWALLOWED. HE CAME BACK ONCE. THEN NEVER."},
 {"LORD RAVENSWOOD","OAKWOOD CALLS THE TEMPLE CURSED. AUREL SAID ITS STONE GUARDS KEEP A PROMISE."},
 {"LORD RAVENSWOOD","THEY DEFEND THE HEART FROM ANYONE WHO WANTS TO COMMAND IT. HIS JOURNAL IS ON MY STUDY DESK. READ IT."}};
static const ProCard A1_JOURNAL_CARDS[]={
 {"AUREL'S JOURNAL","DAY 9. THE GUARDIANS ANSWER ORDER, NOT FORCE. THE HALL HAS FOUR SOCKETS AND TWO SEALED SIDE ROOMS."},
 {"AUREL'S JOURNAL","DAY 11. THE WEST GALLERY TESTS THE BLADE. ITS SENTRIES CRACK ONLY AFTER A PARRY."},
 {"AUREL'S JOURNAL","DAY 12. THE EAST VAULT KEY MUST BE CAST, NOT CUT. A SMITH COULD DO IT. I AM NOT A SMITH."},
 {"AUREL'S JOURNAL","DAY 14. THE STONE REGENT IS NOT CURSED. ITS INSTRUCTION IS CHIPPED. THREE RUNES MIGHT MEND IT."},
 {"LORD RAVENSWOOD","THE EAST ROAD CLIMBS TO CRAGSTONE. THE GATE IS YOURS, ARIN. BRING AUREL'S STORY HOME IF NOT AUREL."}};
static const ProCard A1_TEMPLE_ARRIVE[]={
 {"CRAGSTONE TEMPLE","A HALL CUT INTO THE MOUNTAIN. FOUR DARK SOCKETS. A SEALED DOOR. TWO SIDE ROOMS."},
 {"COSMOS","THIS PLACE IS LISTENING. NOT TO US. TO WHATEVER IS BEHIND THAT DOOR."}};
static const ProCard A1_GUARD_CARDS[]={
 {"GALLERY OF BLADES","THE LAST SENTRY KNEELS. THE SEAL ON THE PEDESTAL WARMS: THE RUNE OF GUARD."},
 {"MURAL","FIRST THE SKY THAT WATCHES, THEN THE ROOT THAT HOLDS."}};
static const ProCard A1_KEY_CARDS[]={
 {"COLD VAULT","THE ORE TAKES THE MOULD. THE KEY COOLS WITH A CLEAN RING. AUREL WAS RIGHT: CAST, NOT CUT."},
 {"COSMOS","YOUR HANDS KNEW WHAT TO DO BEFORE YOU DID. THAT IS WHAT A SMITH IS."}};
static const ProCard A1_KEEP_CARDS[]={
 {"COLD VAULT","BEHIND THE VAULT DOOR: THE RUNE OF KEEPING, AND A LINE CUT DEEP INTO THE WALL."},
 {"INSCRIPTION","THE HEART IS SET BEFORE THE STAR, AND BOTH COME AFTER THE ROOT."}};
static const ProCard A1_ORDER_CARDS[]={
 {"TEMPLE HALL","SKY. ROOT. HEART. STAR. THE FOUR SOCKETS BURN TOGETHER AND THE HEART DOOR GRINDS OPEN."},
 {"COSMOS","SOMETHING HUGE JUST WOKE UP IN THERE. IT ISN'T ANGRY. IT'S ON DUTY."}};
static const ProCard A1_REGENT_MEET[]={
 {"THE STONE REGENT","NONE SHALL COMMAND THE HEART. STATE YOUR PURPOSE OR BE TURNED ASIDE."},
 {"ARIN","I DON'T WANT TO COMMAND IT. I WANT TO KEEP IT AWAY FROM SOMEONE WHO DOES."},
 {"THE STONE REGENT","INSTRUCTION DAMAGED. INTENT UNREADABLE. DEFENSE ENGAGED."},
 {"COSMOS","ITS RULES ARE CHIPPED, NOT EVIL. WATCH ITS HANDS. BRACE THE SLAM, ANSWER ITS CORE, OR MEND IT."}};
static const ProCard A1_REGENT_FOUGHT[]={
 {"THE STONE REGENT","STRUCTURE FAILING. THE HEART... IS... STILL... GUARDED..."},
 {"ARIN","IT KEPT ITS PROMISE TO THE END. I'LL KEEP MINE."},
 {"COSMOS","THE REGENT IS RUBBLE, BUT ITS SEAL STILL HUMS. THE HEART IS JUST AHEAD."}};
static const ProCard A1_REGENT_MENDED[]={
 {"THE STONE REGENT","GUARD. KEEPING. ORDER. INSTRUCTION RESTORED. INTENT READ: PROTECT, NOT POSSESS."},
 {"THE STONE REGENT","PASS, SMITH. WHEN THE WORLDS ARE AT THEIR LAST EDGE, CALL. THE STONE WILL ANSWER."},
 {"COSMOS","YOU FIXED IT INSTEAD OF BREAKING IT. I THINK IT WILL REMEMBER THAT LONGER THAN WE WILL."}};
static const ProCard A1_MALAKAR_CARDS[]={
 {"MALAKAR","SO THE BLACKSMITH CLIMBED THE MOUNTAIN. AND MENDED THE STONE. HOW VERY LIKE YOU."},
 {"MALAKAR","LOOK UP, ARIN. EVERY TEAR IS A WORLD BLEEDING INTO ANOTHER. FEAR. FAMINE. RAIDS."},
 {"MALAKAR","SEAL EVERY BOUNDARY AND THE SUFFERING STOPS. ONE WORLD, ONE ORDER, NO MORE BROKEN SKIES."},
 {"MALAKAR","GIVE ME THE HEART. I WILL END THE PAIN YOU ARE TOO KIND TO END YOURSELF."}};
static const ProCard A1_REPLY_1[]={
 {"ARIN","PAIN ISN'T A REASON TO ERASE THE WORLDS. YOU'D BE SEALING PEOPLE INTO A SILENCE THEY NEVER CHOSE."},
 {"MALAKAR","SPOKEN LIKE A MAN WHO STILL HAS A VILLAGE. THEN DEFEND IT."}};
static const ProCard A1_REPLY_2[]={
 {"ARIN","AND WHO DECIDES WHICH WORLD SURVIVES THE SEALING? YOU? THAT ISN'T MERCY. THAT'S A CROWN."},
 {"MALAKAR","SOMEONE MUST DECIDE. BETTER ME THAN THE TEARING. STAND ASIDE."}};
static const ProCard A1_AXIS_CARDS[]={
 {"MALAKAR","...THE HEART ANSWERS A FORGE AND NOT A CROWN. NOTED. THIS IS NOT FINISHED, SMITH."},
 {"COSMOS","HE'S RETREATING. NOT BEATEN. HE TOOK NOTHING. LET HIM GO, ARIN. THE HEART MATTERS MORE."},
 {"THE HEART OF ERIDORIA","THE FIRST AXIS UNLOCKS. DISTANCE COMES BACK INTO THE WORLD: NEAR IS NEAR AGAIN, AND FAR IS FAR."},
 {"ARIN","NOT A CROWN. I'LL SET IT INTO THE FORGE TOOL. IT REPAIRS THINGS. THAT'S WHAT IT SHOULD DO."},
 {"COSMOS","BROKEN METAL AND BROKEN WORLDS BOTH KEEP THE MARKS OF THEIR MAKERS. MAYBE THAT'S HOW THEY HEAL."},
 {"LUNA-ARC","ABOARD THE SHIP, AN EIGHT-WORLD CHART IGNITES. THE STAR LANES BURN BRIGHT AGAIN."},
 {"ACT I COMPLETE","THE FIRST AXIS IS RECLAIMED. NEXT: THE HIDDEN CITY, PAST BRINDLEMARK'S NE RUNE."}};
#define A1_CARDS(a,t) pro_cards_open(PRO_CARD_SET(a),t)
/* ---------- quest steps ---------- */
static void a1_q05_active(void){if(cq_state[5]==CQ_LOCKED){cq_set(5,CQ_ACTIVE);}}
static void a1_finish_q06(void){a1_flags|=A1F_JOURNAL;story_flags|=ST_OAKWOOD;cq_set(6,CQ_DONE);cq_set(7,CQ_ACTIVE);
 cosmos.trust=(u8)mini(255,cosmos.trust+4);add_xp(10);save_game();}
static void a1_check_q07(void){
 if(cq_state[7]==CQ_ACTIVE&&a1_has(A1F_GUARD|A1F_KEEP|A1F_ORDER)){story_flags|=ST_PUZZLE;cq_set(7,CQ_DONE);cq_set(8,CQ_ACTIVE);add_xp(20);}}
static void a1_finish_regent(int how){a1_regent=(u8)how;cq_set(8,CQ_DONE);cq_set(9,CQ_ACTIVE);add_xp(40);
 if(how==1){credits=(u8)mini(255,credits+20);inv[ITEM_SHARD]=(u8)mini(99,inv[ITEM_SHARD]+2);}
 else cosmos.trust=(u8)mini(255,cosmos.trust+20);save_game();}
static void a1_finish_act(void){a1_flags|=A1F_MALAKAR;
 story_flags|=ST_PUZZLE|ST_MALAKAR|ST_HEART;inv[ITEM_CORE]=(u8)mini(99,inv[ITEM_CORE]+2);cosmos.trust=(u8)mini(255,cosmos.trust+20);
 cosmos.memory_flags|=MEM_SHIP;cq_set(9,CQ_DONE);if(cq_state[10]==CQ_LOCKED)cq_set(10,CQ_ACTIVE);add_xp(60);save_game();}
static void act1_after_cards(int tag){
 if(tag==21){cq_set(5,CQ_DONE);cq_set(6,CQ_ACTIVE);say("Q06 READ AUREL'S JOURNAL ON THE STUDY DESK, EAST SIDE OF THE MANOR.");save_game();}
 else if(tag==22){say("Q07 THE CRAGSTONE ROAD IS OPEN: OAKWOOD'S EAST GATE.");}
 else if(tag==23){say("Q07 WEST: GALLERY OF BLADES. EAST: COLD VAULT. THEN THE FOUR SOCKETS.");}
 else if(tag==24||tag==25||tag==26){a1_check_q07();
  if(cq_state[8]==CQ_ACTIVE&&tag==26)say("Q08 THE HEART DOOR IS OPEN. THE STONE REGENT WAITS INSIDE.");
  else if(!a1_has(A1F_GUARD))say("ONE SEAL LEFT: THE GALLERY OF BLADES, WEST DOOR OF THE HALL.");
  else if(!a1_has(A1F_KEEP))say("ONE SEAL LEFT: THE COLD VAULT, EAST DOOR OF THE HALL.");
  else if(!a1_has(A1F_ORDER))say("BOTH SEALS FOUND. NOW THE FOUR SOCKETS: SKY, ROOT, HEART, STAR.");
  save_game();}
 else if(tag==27){a1_boss=1;a1_rg_max=(s16)(48+player_level*4);a1_rg_hp=a1_rg_max;a1_rg_core=0;a1_rg_phase=0;a1_rg_open=0;a1_rg_runes=0;a1_rg_cursor=0;a1_rg_stagger=0;
  a1_notice="THE REGENT RAISES ITS GUARD.";game_mode=MODE_BATTLE;battle_phase=0;lc_sfx(SFX_CRY);}
 else if(tag==28||tag==29){say("Q09 THE HEART OF ERIDORIA IS AT THE NORTH END OF THE CHAMBER.");}
 else if(tag==30){pro_ui=5;a1_sel=0;a1_choice_tag=2;}
 else if(tag==31){pro_ui=6;a1_deflects=0;a1_lances=0;a1_heat=0;a1_heat_dir=0;a1_flash=0;}
 else if(tag==32){a1_finish_act();say("ACT I COMPLETE. NEXT: THE HIDDEN CITY, BRINDLEMARK'S NORTHEAST RUNE.");}
}
/* ---------- rooms ---------- */
static void act1_place_room3(void){int x,y,i,j;
 /* Orchard detour: west of the market, reached by a lane north of the stalls. */
 for(y=10;y<=30;y++)for(x=4;x<=21;x++)map_put(x,y,T_GRASS,0,C_FREE,TR_NONE);
 for(y=31;y<=39;y++)for(x=11;x<=13;x++)map_put(x,y,T_PATH,1,C_FREE,TR_NONE);
 for(j=0;j<5;j++)for(i=0;i<4;i++){x=6+i*4;y=12+j*4;
  map_put(x,y,(x==A1_SPLIT_TX&&y==A1_SPLIT_TY)?T_VINES:T_TREE,3,C_WALL,TR_A1_TREE);}
 /* The Fallow Inn, south of the market road. */
 map_wall_box(40,44,12,10,3);for(y=45;y<=52;y++)for(x=41;x<=50;x++)map_put(x,y,T_FLOOR,2,C_FREE,TR_NONE);
 for(y=41;y<=45;y++)for(x=43;x<=46;x++)map_put(x,y,T_PATH,1,C_FREE,TR_NONE);
 map_put(49,46,T_LANTERN,3,C_WALL,TR_NONE);map_put(42,52,T_ARCHIVE,3,C_WALL,TR_NONE);
 /* Ravenswood's study desk, in the manor east of the lord. */
 map_put(36,14,T_ARCHIVE,3,C_FREE,TR_A1_JOURNAL);
 /* East gate: the Cragstone road. */
 map_put(54,12,T_RUNE,3,C_FREE,TR_A1_TO_ASCENT);}
static void act1_place_room4(void){int x,y;
 /* Side doors west and east on the cross corridor; the Heart door north. */
 for(y=24;y<=26;y++){for(x=11;x<=14;x++)map_put(x,y,T_PATH,1,C_FREE,TR_NONE);for(x=51;x<=54;x++)map_put(x,y,T_PATH,1,C_FREE,TR_NONE);}
 map_put(10,25,T_DOOR,2,C_FREE,TR_A1_TO_GALLERY);map_put(55,25,T_DOOR,2,C_FREE,TR_A1_TO_VAULT);
 for(y=9;y<=13;y++)for(x=31;x<=33;x++)map_put(x,y,T_PATH,1,C_FREE,TR_NONE);
 map_put(32,9,(story_flags&ST_PUZZLE)?T_DOOR:T_WALL,2,(story_flags&ST_PUZZLE)?C_FREE:C_WALL,TR_A1_HEART_DOOR);
 map_put(32,8,T_WALL,2,C_WALL,TR_NONE);
 /* Sockets light once a rune is aligned for good. */
 if(story_flags&ST_PUZZLE){map_put(21,22,T_STAR,3,C_FREE,TR_RUNE_A);map_put(28,22,T_STAR,3,C_FREE,TR_RUNE_B);map_put(35,22,T_STAR,3,C_FREE,TR_RUNE_C);map_put(42,22,T_STAR,3,C_FREE,TR_RUNE_D);}
 for(x=31;x<=33;x++)for(y=50;y<=54;y++)map_put(x,y,T_PATH,1,C_FREE,TR_NONE);
 map_put(32,55,T_DOOR,2,C_FREE,TR_A1_TO_ASCENT_TOP);}
static void a1_path(int x0,int y0,int x1,int y1){int x,y;
 for(y=y0;y<=y1;y++)for(x=x0;x<=x1;x++)map_put(x,y,T_PATH,1,C_FREE,TR_NONE);}
static void a1_gen_ascent(void){int x,y;
 map_fill(T_RUIN,0);map_border();
 for(y=1;y<63;y++)for(x=1;x<63;x++)map_put(x,y,T_RUIN,2,C_WALL,TR_NONE);
 /* Switchbacks: Oakwood trailhead (south) to the temple gate (north). */
 a1_path(31,49,33,61);a1_path(8,49,33,51);a1_path(8,35,10,51);
 /* The hermit's ledge, a wide shelf halfway up. */
 for(y=34;y<=42;y++)for(x=4;x<=16;x++)map_put(x,y,T_GRASS,0,C_FREE,TR_NONE);
 a1_path(8,35,52,37);a1_path(50,21,52,37);
 /* The crossing: a stone bridge over the chasm on the west traverse. */
 a1_path(20,21,52,23);for(y=17;y<=27;y++)for(x=28;x<=36;x++)if(y<21||y>23)map_put(x,y,T_VOID,0,C_WALL,TR_NONE);
 for(x=28;x<=36;x++)for(y=21;y<=23;y++)map_put(x,y,T_BRIDGE,1,C_FREE,TR_NONE);
 a1_path(20,9,22,23);a1_path(20,9,33,11);a1_path(31,3,33,11);
 map_put(32,2,T_DOOR,2,C_FREE,TR_A1_TO_TEMPLE);
 map_put(32,62,T_DOOR,2,C_FREE,TR_A1_TO_OAKWOOD);map_put(32,61,T_PATH,1,C_FREE,TR_NONE);
 map_put(12,40,T_FURNACE,3,C_FREE,TR_A1_CAMP);map_put(54,22,T_STAR,3,C_FREE,TR_A1_LOOKOUT);
 for(x=53;x<=55;x++)for(y=21;y<=23;y++)if(x!=54||y!=22)map_put(x,y,T_PATH,1,C_FREE,TR_NONE);
 for(x=6;x<=16;x+=5)map_put(x,43,T_TREE,3,C_WALL,TR_NONE);
 for(y=12;y<=46;y+=6)map_put(59,y,T_PILLAR,2,C_WALL,TR_NONE);}
static void a1_gen_gallery(void){int x,y;
 map_fill(T_RUIN,0);map_border();
 for(y=1;y<63;y++)for(x=1;x<63;x++)map_put(x,y,T_RUIN,2,C_WALL,TR_NONE);
 for(y=20;y<=30;y++)for(x=8;x<=55;x++)map_put(x,y,T_FLOOR,2,C_FREE,TR_NONE);
 for(x=12;x<=52;x+=8){map_put(x,20,T_PILLAR,2,C_WALL,TR_NONE);map_put(x,30,T_PILLAR,2,C_WALL,TR_NONE);}
 for(y=24;y<=26;y++)map_put(56,y,T_PATH,1,C_FREE,TR_NONE);
 map_put(57,25,T_DOOR,2,C_FREE,TR_A1_TO_HALL);
 map_put(9,25,a1_has(A1F_GUARD)?T_STAR:T_RUNE,3,C_FREE,TR_A1_GUARD_SEAL);
 map_put(9,21,T_ARCHIVE,3,C_FREE,TR_A1_MURAL);}
static void a1_gen_vault(void){int x,y,open=a1_has(A1F_VAULT_OPEN);
 map_fill(T_RUIN,0);map_border();
 for(y=1;y<63;y++)for(x=1;x<63;x++)map_put(x,y,T_RUIN,2,C_WALL,TR_NONE);
 for(y=18;y<=34;y++)for(x=8;x<=55;x++)map_put(x,y,T_FLOOR,2,C_FREE,TR_NONE);
 for(y=24;y<=28;y++)map_put(7,y,T_PATH,1,C_FREE,TR_NONE);
 map_put(6,26,T_DOOR,2,C_FREE,TR_A1_TO_HALL);
 map_put(20,20,T_ARCHIVE,3,C_FREE,TR_A1_MOULD);
 map_put(24,33,a1_has(A1F_ORE)?T_RUIN:T_CRYSTAL,3,C_FREE,TR_A1_ORE);
 map_put(32,26,T_FURNACE,3,C_FREE,TR_A1_FORGE);
 for(y=18;y<=34;y++)map_put(44,y,T_WALL,2,C_WALL,TR_NONE);
 if(open){for(y=25;y<=27;y++)map_put(44,y,T_PATH,1,C_FREE,TR_NONE);map_put(44,24,T_DOOR,2,C_WALL,TR_NONE);}
 else map_put(44,26,T_DOOR,2,C_WALL,TR_A1_VAULT_DOOR);
 map_put(52,26,a1_has(A1F_KEEP)?T_STAR:T_RUNE,3,C_FREE,TR_A1_KEEP_SEAL);
 map_put(52,20,T_ARCHIVE,3,C_FREE,TR_A1_INSCRIPTION);}
static void a1_gen_chamber(void){int x,y;
 map_fill(T_RUIN,0);map_border();
 for(y=1;y<63;y++)for(x=1;x<63;x++)map_put(x,y,T_RUIN,2,C_WALL,TR_NONE);
 for(y=7;y<=58;y++)for(x=16;x<=47;x++)map_put(x,y,T_FLOOR,2,C_FREE,TR_NONE);
 for(y=8;y<=56;y+=8){map_put(18,y,T_LANTERN,3,C_WALL,TR_NONE);map_put(45,y,T_LANTERN,3,C_WALL,TR_NONE);}
 /* The Regent's ledge splits the chamber; it stands in the only gap. */
 for(x=16;x<=47;x++)for(y=29;y<=31;y++)map_put(x,y,T_WALL,2,C_WALL,TR_NONE);
 if(a1_regent){for(x=30;x<=34;x++)for(y=29;y<=31;y++)map_put(x,y,a1_regent==1?T_CRACK:T_PATH,1,C_FREE,TR_NONE);}
 else{for(x=30;x<=34;x++)for(y=29;y<=31;y++)map_put(x,y,T_PILLAR,2,C_WALL,TR_NONE);map_put(32,32,T_PATH,1,C_FREE,TR_A1_REGENT);}
 map_put(32,10,a1_has(A1F_MALAKAR)?T_STAR:T_CRYSTAL,3,C_FREE,TR_A1_HEART);
 map_put(32,59,T_DOOR,2,C_FREE,TR_A1_TO_HALL);}
static void act1_generate(void){
 set_world_palette(current_room==A1_ASCENT?5:current_room==A1_VAULT?1:current_room==A1_CHAMBER?6:4);
 if(current_room==A1_ASCENT)a1_gen_ascent();else if(current_room==A1_GALLERY)a1_gen_gallery();
 else if(current_room==A1_VAULT)a1_gen_vault();else a1_gen_chamber();}
static const char*act1_room_name(void){
 return current_room==A1_ASCENT?"CRAGSTONE ASCENT":current_room==A1_GALLERY?"GALLERY OF BLADES":current_room==A1_VAULT?"COLD VAULT":"HEART CHAMBER";}
static int act1_spawn(void){int i;
 if(current_world!=0)return 0;
 if(current_room==4)return 1; /* Malakar now waits at the Heart, not in the hall. */
 if(current_room==A1_ASCENT){spawn_enemy(0,14,50,EN_GLITCH,0);spawn_enemy(1,44,36,EN_GLITCH,0);return 1;}
 if(current_room==A1_GALLERY){for(i=0;i<3;i++)if(!(a1_sentries&(1u<<i))){spawn_enemy(i,44-i*12,25,EN_CROWN,0);
   enemies[i].maxhp=(u8)(8+player_level);enemies[i].hp=enemies[i].maxhp;}return 1;}
 if(A1_IS_ROOM)return 1;
 return 0;}
/* ---------- NPC scripts (ids 40-59) ---------- */
static void act1_npc_speak(void){int id=npc_dialogue_id;
 if(current_world!=0||pro_script)return;
 if(id==16){
  if(cq_state[5]==CQ_ACTIVE&&!a1_has(A1F_MET_RAVEN))
   pro_say_lines(40,"LORD RAVENSWOOD LOWERS A LETTER. THE TEMPLE? YOU'RE THE SECOND PERSON TO ASK. MY BROTHER WAS THE FIRST.",
    "A COURIER, PELL, CARRIED AUREL'S MAP CASE. GLITCHLINGS RAN HIM DOWN IN THE ORCHARD.",
    "PELL RESTS AT THE FALLOW INN, SOUTH OF THE MARKET. BRING ME THAT MAP. THEN WE TALK.");
  else if(cq_state[5]==CQ_ACTIVE&&!a1_has(A1F_MAP_FOUND))pro_say_lines(41,"PELL IS AT THE FALLOW INN. THE MAP CASE IS SOMEWHERE IN THE ORCHARD.",0,0);
  else if(cq_state[5]==CQ_ACTIVE)pro_say_lines(42,"IS THAT... THE CASE? GIVE IT HERE. CAREFULLY. IT'S ALL I HAVE LEFT OF HIM.",0,0);
  else if(cq_state[6]==CQ_ACTIVE)pro_say_lines(43,"AUREL'S JOURNAL IS ON MY DESK, EAST SIDE OF THIS ROOM. READ IT BEFORE YOU CLIMB.",0,0);
  else if(story_flags&ST_HEART)pro_say_lines(44,"YOU CAME BACK. AUREL'S STORY CAME BACK WITH YOU. THANK YOU, SMITH.",0,0);
  else if(cq_state[7]==CQ_ACTIVE||cq_state[8]==CQ_ACTIVE||cq_state[9]==CQ_ACTIVE)pro_say_lines(45,"THE EAST GATE, THEN UP. MIND THE BRIDGE OVER THE CHASM.",0,0);
 }else if(id==NPC_A1_PELL){
  if(a1_has(A1F_MAP_FOUND))pro_say_lines(46,"YOU FOUND IT! THE LORD WILL WEEP. GOOD WEEPING, I MEAN.",0,0);
  else if(a1_has(A1F_PELL_HEALED))pro_say_lines(47,"THE SPLIT OAK. FOURTH ROW FROM THE NORTH, THIRD TREE FROM THE WEST. I STUFFED THE CASE IN ITS CRACK.",0,0);
  else if(a1_has(A1F_MET_RAVEN)&&inv[ITEM_POTION])pro_say_lines(48,"A COURIER WITH A BAD LEG ON A COT. YOU'RE FROM RAVENSWOOD? MY LEG... DO YOU HAVE A POTION?",
   "YOU HAND PELL A POTION. HE DRINKS IT IN ONE GULP AND FLEXES HIS KNEE.",
   "I HID THE CASE FROM THE GLITCHLINGS IN THE SPLIT OAK. FOURTH ROW, THIRD FROM THE WEST.");
  else if(a1_has(A1F_MET_RAVEN))pro_say_lines(49,"I'D TALK BETTER WITHOUT THIS LEG SCREAMING. A POTION? THE TRADER SELLS THEM. ASK BREE.",0,0);
  else pro_say_lines(50,"A COURIER NURSES A BANDAGED LEG. TAKE THE ORCHARD ROAD AT NIGHT, THEY SAID.",0,0);
 }else if(id==NPC_A1_BREE){
  if(cq_state[5]==CQ_ACTIVE&&a1_has(A1F_MET_RAVEN)&&!a1_has(A1F_PELL_HEALED)&&!inv[ITEM_POTION]&&!a1_has(A1F_INN_GIFT))
   pro_say_lines(51,"FOR PELL? TAKE THIS POTION. PAY ME WHEN THE WORLD STOPS ENDING.",0,0);
  else pro_say_lines(52,"WELCOME TO THE FALLOW INN. A BED IS THREE CREDITS. HOT SOUP IS FREE IF YOU LOOK THIS TIRED.",0,0);
 }else if(id==NPC_A1_WYN){
  if(story_flags&ST_HEART)pro_say_lines(53,"THEY SAY A SMITH WALKED OUT OF CRAGSTONE WITH LIGHT IN HIS POCKETS. WAS IT YOU? IT WAS YOU.",0,0);
  else if(cq_state[5]==CQ_ACTIVE)pro_say_lines(54,"PSST. PELL LIMPED IN SHOUTING ABOUT GLITCHLINGS IN THE ORCHARD, WEST OF THE STALLS.",
   "THE LORD HASN'T SMILED SINCE HIS BROTHER CLIMBED THE MOUNTAIN. EVERYBODY'S BUSINESS.",0);
  else pro_say_lines(55,"THE TEMPLE ISN'T CURSED, YOU KNOW. MY GRAN SAID THE STONES THERE ARE JUST... STUBBORN.",0,0);
 }else if(id==NPC_A1_ODA){
  pro_say_lines(56,"AN OLD CLIMBER WARMS HER HANDS. THE TEMPLE STONES HIT HARD BUT HONEST. THEY RAISE THEIR ARMS FIRST.",
   "WHEN A SENTRY WINDS UP, BRACE. B. TURN THE BLOW ASIDE AND THE STONE CRACKS OPEN FOR ONE GOOD STRIKE.",
   "REST BY MY FIRE IF YOU NEED IT. IT'S FREE. MOUNTAINS DON'T TAKE COIN.");
 }else if(id==17){
  if(!(story_flags&ST_PUZZLE))pro_say_lines(57,"THE GUARDIANS ANSWER ORDER, NOT FORCE.","WEST: THE GALLERY OF BLADES. EAST: THE COLD VAULT. EACH KEEPS A SEAL AND HALF A SENTENCE.",
   "BRING BOTH SEALS. THEN SPEAK THE FOUR SOCKETS IN THEIR ORDER.");
 }}
static void act1_script_done(int id){
 if(id==40){a1_flags|=A1F_MET_RAVEN;say("Q05 FIND PELL AT THE FALLOW INN, SOUTH OF THE MARKET.");}
 else if(id==42){a1_flags|=A1F_MAP_RETURNED;pro_cards_open(PRO_CARD_SET(A1_RAVEN_MAP),21);}
 else if(id==48){if(inv[ITEM_POTION])inv[ITEM_POTION]--;a1_flags|=A1F_PELL_HEALED;cosmos.trust=(u8)mini(255,cosmos.trust+4);
  say("Q05 SEARCH THE SPLIT OAK IN THE ORCHARD: FOURTH ROW, THIRD FROM THE WEST.");}
 else if(id==51){a1_flags|=A1F_INN_GIFT;inv[ITEM_POTION]=(u8)mini(99,inv[ITEM_POTION]+1);say("BREE GAVE YOU A POTION FOR PELL.");}
 else if(id==52){pro_ui=5;a1_sel=0;a1_choice_tag=1;}
 else if(id==56){player.hp=max_hp;player_mp=max_mp;say("ODA'S FIRE WARMS YOU. HP AND MP RESTORED.");}}
/* ---------- interaction ---------- */
static int a1_door(u8 t){
 if(t==TR_A1_TO_ASCENT){if(!(story_flags&ST_OAKWOOD)){say(cq_state[6]==CQ_ACTIVE?"READ AUREL'S JOURNAL FIRST. RAVENSWOOD WILL OPEN THE GATE.":"THE CRAGSTONE GATE IS LOCKED. LORD RAVENSWOOD HOLDS THE KEY.");return 1;}
  a1_go(A1_ASCENT,32,59);say("THE CRAGSTONE ASCENT. THE TEMPLE IS AT THE TOP.");return 1;}
 if(t==TR_A1_TO_OAKWOOD){a1_go(3,52,14);say("BACK IN OAKWOOD.");return 1;}
 if(t==TR_A1_TO_TEMPLE){int first=!a1_has(A1F_ASCENT);a1_flags|=A1F_ASCENT;a1_go(4,32,52);
  if(first&&!(story_flags&ST_PUZZLE))A1_CARDS(A1_TEMPLE_ARRIVE,23);else say("THE CRAGSTONE TEMPLE HALL.");return 1;}
 if(t==TR_A1_TO_ASCENT_TOP){a1_go(A1_ASCENT,32,5);say("THE WIND ON THE LEDGE. OAKWOOD IS FAR BELOW.");return 1;}
 if(t==TR_A1_TO_GALLERY){a1_go(A1_GALLERY,54,25);say(a1_has(A1F_GUARD)?"THE GALLERY IS QUIET NOW.":"STONE SENTRIES LINE THE GALLERY. THEY ONLY CRACK WHEN YOU PARRY.");return 1;}
 if(t==TR_A1_TO_VAULT){a1_go(A1_VAULT,10,26);say(a1_has(A1F_KEEP)?"THE COLD VAULT.":"A COLD FORGE, A LOCKED VAULT DOOR. AUREL SAID: CAST, NOT CUT.");return 1;}
 if(t==TR_A1_TO_HALL){int from=current_room;a1_go(4,from==A1_GALLERY?13:from==A1_VAULT?51:32,from==A1_CHAMBER?12:25);say("THE TEMPLE HALL.");return 1;}
 if(t==TR_A1_HEART_DOOR){if(!(story_flags&ST_PUZZLE)){say("THE HEART DOOR IS SEALED. FOUR DARK SOCKETS WAIT IN THE HALL.");return 1;}
  a1_go(A1_CHAMBER,32,56);say(a1_regent?"THE HEART CHAMBER.":"THE HEART CHAMBER. A STONE GIANT STANDS IN THE ONLY GAP.");return 1;}
 return 0;}
static int act1_interact(u8 t){
 if(current_world!=0||game_mode!=MODE_SURFACE)return 0;
 if(a1_door(t))return 1;
 if(t==TR_A1_TREE){int tx=near_trigger_x,ty=near_trigger_y;
  if(tx==A1_SPLIT_TX&&ty==A1_SPLIT_TY){
   if(a1_has(A1F_MAP_FOUND)){say("THE SPLIT OAK. THE CRACK IS EMPTY NOW.");return 1;}
   if(!a1_has(A1F_PELL_HEALED)){say("A LIGHTNING-SPLIT OAK. ONLY BARK AND BEETLES IN THE CRACK. OR SO IT SEEMS.");return 1;}
   a1_flags|=A1F_MAP_FOUND;a1_q05_active();lc_sfx(SFX_CONFIRM);add_xp(6);save_game();say("A MAP CASE, WEDGED DEEP IN THE CRACK. AUREL'S MAP! TAKE IT TO RAVENSWOOD.");return 1;}
  say((tx+ty)&1?"ONLY APPLES. A WASP DISAGREES WITH YOU ABOUT THEM.":"THE TREE IS HEAVY WITH APPLES. NO MAP CASE HERE.");return 1;}
 if(t==TR_A1_JOURNAL){
  if(cq_state[6]==CQ_ACTIVE){a1_finish_q06();A1_CARDS(A1_JOURNAL_CARDS,22);return 1;}
  say(a1_has(A1F_JOURNAL)?"AUREL'S JOURNAL. DAY 14: THREE RUNES MIGHT MEND IT.":"A DESK STACKED WITH LETTERS. THE LORD'S PRIVATE STUDY.");return 1;}
 if(t==TR_A1_CAMP){player.hp=max_hp;player_mp=max_mp;save_game();say("YOU REST BY ODA'S FIRE. HP AND MP RESTORED. THE GAME IS SAVED.");return 1;}
 if(t==TR_A1_LOOKOUT){say("OAKWOOD'S ROOFS, BRINDLEMARK'S BEACON, AND A SKY WITH A SEAM IN IT.");return 1;}
 if(t==TR_A1_MURAL){say("MURAL: FIRST THE SKY THAT WATCHES, THEN THE ROOT THAT HOLDS.");return 1;}
 if(t==TR_A1_GUARD_SEAL){
  if(a1_has(A1F_GUARD)){say("THE RUNE OF GUARD IS YOURS.");return 1;}
  if((a1_sentries&7)!=7){say("THE SEAL WON'T WAKE WHILE ITS SENTRIES STAND. DUEL THEM: SELECT+A.");return 1;}
  a1_flags|=A1F_GUARD;map_put(9,25,T_STAR,3,C_FREE,TR_A1_GUARD_SEAL);lc_sfx(SFX_LEVELUP);add_xp(12);save_game();A1_CARDS(A1_GUARD_CARDS,24);return 1;}
 if(t==TR_A1_MOULD){if(a1_has(A1F_MOULD)){say("THE PEDESTAL IS EMPTY.");return 1;}a1_flags|=A1F_MOULD;save_game();say("A STONE KEY MOULD. TWO HALVES, A CHANNEL FOR METAL. NOW: ORE, AND HEAT.");return 1;}
 if(t==TR_A1_ORE){if(a1_has(A1F_ORE)){say("THE VEIN IS WORKED OUT.");return 1;}a1_flags|=A1F_ORE;map_put(24,33,T_RUIN,2,C_FREE,TR_A1_ORE);save_game();say("YOU PRY A FIST OF CRAGSTONE ORE FROM THE VEIN.");return 1;}
 if(t==TR_A1_FORGE){
  if(a1_has(A1F_KEY)){say("THE COLD FORGE TICKS AS IT COOLS.");return 1;}
  if(!a1_has(A1F_MOULD|A1F_ORE)){say(a1_has(A1F_MOULD)?"YOU HAVE THE MOULD. THE ORE VEIN IS IN THE SOUTH WALL.":a1_has(A1F_ORE)?"YOU HAVE ORE. THE KEY MOULD SITS ON THE NORTH PEDESTAL.":"A COLD FORGE. TO CAST A KEY: A MOULD AND ORE.");return 1;}
  pro_ui=7;a1_strikes=0;a1_heat=0;a1_heat_dir=0;a1_flash=0;dialogue_timer=0;return 1;}
 if(t==TR_A1_VAULT_DOOR){
  if(!a1_has(A1F_KEY)){say("A FLAME-SHAPED KEYHOLE. THIS KEY HAS TO BE CAST, NOT CUT.");return 1;}
  a1_flags|=A1F_VAULT_OPEN;save_game();lc_sfx(SFX_CONFIRM);a1_go(A1_VAULT,40,26);say("THE CAST KEY TURNS. THE VAULT DOOR SWINGS OPEN.");return 1;}
 if(t==TR_A1_KEEP_SEAL){
  if(a1_has(A1F_KEEP)){say("THE RUNE OF KEEPING IS YOURS.");return 1;}
  a1_flags|=A1F_KEEP;map_put(52,26,T_STAR,3,C_FREE,TR_A1_KEEP_SEAL);lc_sfx(SFX_LEVELUP);add_xp(12);save_game();A1_CARDS(A1_KEEP_CARDS,25);return 1;}
 if(t==TR_A1_INSCRIPTION){say("THE HEART IS SET BEFORE THE STAR, AND BOTH COME AFTER THE ROOT.");return 1;}
 if(current_room==4&&t>=TR_RUNE_A&&t<=TR_RUNE_D){static const u8 order[4]={2,0,3,1};u8 r=(u8)(t-TR_RUNE_A);
  if(story_flags&ST_PUZZLE){say("THE FOUR SOCKETS BURN STEADILY. THE HEART DOOR IS OPEN.");return 1;}
  if(!a1_has(A1F_GUARD|A1F_KEEP)){say(a1_has(A1F_GUARD)?"THE SOCKETS STAY DARK. ONE SEAL IS MISSING: THE COLD VAULT, EAST.":
   a1_has(A1F_KEEP)?"THE SOCKETS STAY DARK. ONE SEAL IS MISSING: THE GALLERY, WEST.":"THE SOCKETS ARE DARK. THE GALLERY AND THE VAULT KEEP THEIR SEALS.");return 1;}
  if(r!=order[a1_rune_step]){a1_rune_step=0;lc_sfx(SFX_HIT);say("THE SOCKETS FLICKER OUT. WRONG ORDER. THE MURAL AND THE INSCRIPTION TOGETHER.");return 1;}
  a1_rune_step++;lc_sfx(SFX_CONFIRM);
  if(a1_rune_step<4){say(a1_rune_step==1?"ONE SOCKET GLOWS.":a1_rune_step==2?"TWO SOCKETS GLOW.":"THREE SOCKETS GLOW.");return 1;}
  a1_rune_step=0;a1_flags|=A1F_ORDER;story_flags|=ST_PUZZLE;
  map_put(32,9,T_DOOR,2,C_FREE,TR_A1_HEART_DOOR);
  map_put(21,22,T_STAR,3,C_FREE,TR_RUNE_A);map_put(28,22,T_STAR,3,C_FREE,TR_RUNE_B);map_put(35,22,T_STAR,3,C_FREE,TR_RUNE_C);map_put(42,22,T_STAR,3,C_FREE,TR_RUNE_D);
  save_game();A1_CARDS(A1_ORDER_CARDS,26);return 1;}
 if(current_room==4&&t==TR_TERMINAL){say("FOUR SOCKETS. THE GALLERY AND THE VAULT EACH KEEP HALF OF THEIR ORDER.");return 1;}
 if(t==TR_A1_REGENT){if(a1_regent)return 1;A1_CARDS(A1_REGENT_MEET,27);return 1;}
 if(t==TR_A1_HEART){
  if(a1_has(A1F_MALAKAR)){say("THE HEART'S FIRST AXIS HUMS IN YOUR FORGE TOOL. THE CHAMBER IS QUIET.");return 1;}
  if(!a1_regent){say("THE REGENT STILL GUARDS THE GAP.");return 1;}
  A1_CARDS(A1_MALAKAR_CARDS,30);return 1;}
 return 0;}
/* Old Oakwood gate (54,12) from older saves loading straight into Oakwood is
   replaced at map build time, so story_gate never sends anyone past here. */
/* ---------- field battle hooks: gallery sentries need a parry ---------- */
static int act1_stone_skin(Enemy*e){return current_world==0&&current_room==A1_GALLERY&&e>=&enemies[0]&&e<=&enemies[2];}
static void act1_on_block(Enemy*e){if(act1_stone_skin(e)){a1_parry=1;battle_notice="PARRY! THE SENTRY'S GUARD CRACKS. STRIKE NOW.";}}
/* Returns 1 when the gallery rules handled the command. */
static int act1_battle_fight(Enemy*e){
 if(!act1_stone_skin(e))return 0;
 if(battle_cursor==3){battle_notice="THE SENTRY ONLY ANSWERS THE BLADE.";return 1;}
 if(battle_cursor!=0&&battle_cursor!=1)return 0;
 if(!a1_parry){battle_notice=battle_cursor?"THE SPELL SLIDES OFF THE STONE. BRACE WITH B, THEN STRIKE.":"STONE SKIN! BRACE WITH B WHEN IT WINDS UP, THEN STRIKE.";lc_sfx(SFX_HIT);return 1;}
 a1_parry=0;if(battle_cursor==1){if(player_mp<2){battle_notice="NOT ENOUGH MANA!";return 2;}player_mp-=2;}
 e->hurt=0;damage_enemy(e,2*(str_stat+weapon_bonus())+2);battle_notice="A CLEAN COUNTER! STONE SPLITS.";lc_sfx(SFX_CRIT);
 if(!e->active){a1_sentries|=(u8)(1u<<(e-enemies));save_game();}
 return 1;}
/* ---------- the Stone Regent ---------- */
static const char*const A1_CORE_NAME[4]={"STONE","EMBER","TIDE","BLOOM"};
/* EMBER is answered by TIDE, TIDE by BLOOM, BLOOM by EMBER (the spark cycle). */
static int a1_counter(int core,int spell){return (core==1&&spell==2)||(core==2&&spell==3)||(core==3&&spell==1);}
static int a1_trusted(void){return cosmos.trust>=A1_TRUST_NEEDED||(lc_party.count&&lc_party.slots[lc_party.active].bond>=40);}
static void a1_rg_next_turn(void){
 a1_rg_core=(u8)((a1_rg_core+1+((frame>>3)&1))&3);
 a1_rg_tell=(u8)((a1_rg_runes+a1_rg_core+(a1_rg_hp&1))%3==0);}
static void a1_rg_end(int how){a1_boss=0;game_mode=MODE_SURFACE;battle_phase=0;ui_clear();a1_finish_regent(how);
 a1_go(A1_CHAMBER,32,36);
 if(how==1)A1_CARDS(A1_REGENT_FOUGHT,28);else A1_CARDS(A1_REGENT_MENDED,29);}
static void a1_rg_act(void){int dmg=0,c=a1_rg_cursor;
 if(c==4){if(!inv[ITEM_POTION]){a1_notice="NO POTIONS LEFT.";return;}inv[ITEM_POTION]--;player.hp=(u8)mini(max_hp,player.hp+4);a1_notice="ARIN DRINKS A POTION.";lc_sfx(SFX_POTION);}
 else if(c==5){
  if(!a1_trusted()){a1_notice="COSMOS: IT WON'T LET US CLOSE ENOUGH YET. WE NEED MORE TRUST.";return;}
  if(!a1_rg_open&&!a1_rg_stagger){a1_notice="ITS GUARD IS UP. PARRY THE SLAM OR STAGGER ITS CORE FIRST.";return;}
  a1_rg_runes++;a1_rg_open=0;a1_rg_stagger=0;lc_sfx(SFX_BEFRIEND);
  a1_notice=a1_rg_runes==1?"YOU PRESS THE RUNE OF GUARD INTO ITS CHEST. IT HESITATES.":a1_rg_runes==2?"THE RUNE OF KEEPING. ITS FISTS LOWER.":"THE RUNE OF ORDER. THE INSTRUCTION CLICKS WHOLE.";
  if(a1_rg_runes>=3){a1_rg_phase=3;a1_rg_timer=70;return;}}
 else if(c==0){
  if(a1_rg_open||a1_rg_stagger){dmg=2*(str_stat+weapon_bonus())+2;a1_rg_open=0;a1_rg_stagger=0;a1_notice="COUNTER! THE BLADE BITES INTO OPEN STONE.";lc_sfx(SFX_CRIT);}
  else if(a1_rg_core==0){dmg=0;a1_notice="THE BLADE RINGS OFF ITS STONE CORE. PARRY FIRST.";lc_sfx(SFX_HIT);}
  else{dmg=(str_stat+weapon_bonus()+1)>>1;a1_notice="ARIN STRIKES. THE GLOWING CORE SOAKS MOST OF IT.";lc_sfx(SFX_ATTACK);}}
 else{int spell=c;/* 1 EMBER 2 TIDE 3 BLOOM */
  if(player_mp<2){a1_notice="NOT ENOUGH MANA.";return;}player_mp-=2;
  if(a1_counter(a1_rg_core,spell)){dmg=2*(mag_stat+2+charm_bonus());a1_rg_stagger=1;a1_notice="THE CORE CRACKS! THE REGENT STAGGERS.";lc_sfx(SFX_CRIT);}
  else{dmg=1;a1_notice=a1_rg_core==0?"STONE SHRUGS OFF THE SPELL.":"THE CORE DRINKS THE SPELL. WRONG ELEMENT.";lc_sfx(SFX_HIT);}}
 if(dmg){a1_rg_hp=(s16)(a1_rg_hp-dmg);if(a1_rg_hp<=0){a1_rg_hp=0;a1_rg_phase=4;a1_rg_timer=70;return;}}
 if(a1_rg_stagger){a1_rg_phase=2;a1_rg_timer=40;return;}
 a1_rg_phase=1;a1_rg_timer=55;a1_rg_braced=0;}
static void act1_boss_update(u16 newk){
 if(a1_rg_phase==3||a1_rg_phase==4){if(a1_rg_timer)a1_rg_timer--;else a1_rg_end(a1_rg_phase==3?2:1);return;}
 if(a1_rg_phase==5){if(a1_rg_timer)a1_rg_timer--;else{a1_boss=0;game_mode=MODE_SURFACE;battle_phase=0;ui_clear();a1_go(A1_CHAMBER,32,56);say("COSMOS PULLED YOU BACK TO THE DOOR. THE REGENT RESETS. TRY AGAIN.");}return;}
 if(a1_rg_phase==1){
  if((newk&KEY_B)&&a1_rg_timer<=40&&!a1_rg_braced)a1_rg_braced=1;
  if(a1_rg_timer)a1_rg_timer--;
  if(!a1_rg_timer){
   if(a1_rg_tell==0&&a1_rg_braced){lc_sfx(SFX_CONFIRM);cosmos.trust=(u8)mini(255,cosmos.trust+1);
    if(a1_rg_core==0){a1_rg_open=1;a1_notice="PARRY! THE STONE FIST GLANCES AWAY. ITS GUARD IS OPEN.";}
    else a1_notice="PARRIED, BUT THE CORE STILL GLOWS. HIT IT WITH ITS WEAKNESS.";}
   else{int dmg=a1_rg_tell?1:2;player.hp=(u8)(dmg>=player.hp?0:player.hp-dmg);lc_sfx(SFX_HIT);
    a1_notice=a1_rg_tell?"THE FLOOR HEAVES. NOTHING TO BRACE AGAINST.":"THE SLAM LANDS. BRACE WITH B NEXT TIME.";
    if(!player.hp){player.hp=max_hp;player_mp=max_mp;a1_rg_phase=5;a1_rg_timer=70;a1_notice="ARIN FALLS. COSMOS CATCHES HIS SIGNAL.";return;}}
   a1_rg_next_turn();a1_rg_phase=2;a1_rg_timer=30;}
  return;}
 if(a1_rg_phase==2){if(a1_rg_timer)a1_rg_timer--;else a1_rg_phase=0;return;}
 if(newk&KEY_LEFT)a1_rg_cursor^=1;if(newk&KEY_RIGHT)a1_rg_cursor^=1;
 if(newk&KEY_UP)a1_rg_cursor=(u8)((a1_rg_cursor+4)%6);if(newk&KEY_DOWN)a1_rg_cursor=(u8)((a1_rg_cursor+2)%6);
 if(newk&KEY_A)a1_rg_act();}
static void act1_boss_draw(void){static const char*ACT[6]={"FIGHT","EMBER","TIDE","BLOOM","POTION","RESTORE"};int i;
 ui_frame(0,19,15);ui_text(2,2,"CRAGSTONE // GUARDIAN",14);ui_text(3,3,"STONE REGENT",13);
 ui_text(3,4,"HP",15);ui_num(6,4,a1_rg_hp,15);ui_text(10,4,"/",15);ui_num(12,4,a1_rg_max,15);
 ui_text(3,5,"CORE",15);ui_text(8,5,A1_CORE_NAME[a1_rg_core&3],a1_rg_core?14:8);
 ui_text(3,6,"RUNES",15);ui_num(9,6,a1_rg_runes,15);ui_text(10,6,"/3",15);
 if(a1_rg_open)ui_text(3,7,"GUARD OPEN",13);else if(a1_rg_stagger)ui_text(3,7,"STAGGERED",13);
 if(a1_rg_core){static const u8 W[4]={0,2,3,1};ui_text(3,8,"WEAK TO",15);ui_text(11,8,A1_CORE_NAME[W[a1_rg_core&3]],14);}else ui_text(3,8,"PARRY THE SLAM",15);
 ui_text(2,10,"ARIN",14);ui_text(8,10,"LV",15);ui_num(11,10,player_level,15);
 ui_text(2,11,"HP",13);ui_num(5,11,player.hp,15);ui_text(8,11,"/",15);ui_num(10,11,max_hp,15);ui_text(16,11,"MP",13);ui_num(19,11,player_mp,15);
 ui_text(16,10,"TRUST",14);ui_num(22,10,cosmos.trust,15);
 for(i=0;i<6;i++){int x=(i&1)?15:2,y=13+(i>>1);ui_text(x,y,(a1_rg_phase==0&&a1_rg_cursor==i)?">":" ",13);ui_text(x+2,y,ACT[i],a1_rg_phase==0?15:14);}
 if(a1_rg_phase==1){ui_text(2,16,a1_rg_tell?"IT STAMPS: A QUAKE!":"IT RAISES BOTH FISTS!",13);if(!a1_rg_tell)ui_text(2,17,a1_rg_timer<=40?"B BRACE NOW":"WAIT FOR IT",a1_rg_timer<=40?14:8);}
 else ui_wrap_text(16,a1_notice,14,3);
 oam_hide_all();oam_set32(0,43,59,272,0);oam_ui_portrait(0);
 if(a1_rg_phase!=3&&a1_rg_phase!=4){oam_set32(2,169+((a1_rg_phase==1&&a1_rg_timer<=40)?(int)((frame>>1)&1)*2:0),54,160+EN_CROWN*16,5+EN_CROWN);oam_ui_portrait(2);}}
/* ---------- field sprites (Regent and Malakar in the Heart Chamber) ---------- */
static u8 a1_oam_used=0;
static void act1_sprites(void){
 if(!(current_world==0&&current_room==A1_CHAMBER&&game_mode==MODE_SURFACE)){
  if(a1_oam_used){OAM16[A1_REGENT_OAM*4]=0x0200;OAM16[A1_MALAKAR_OAM*4]=0x0200;a1_oam_used=0;}return;}
 a1_oam_used=1;
 if(a1_regent!=1)oam_set32(A1_REGENT_OAM,(a1_regent==2?40:32)*8-cam_x-16,(a1_regent==2?27:30)*8-cam_y-24,160+EN_CROWN*16,5+EN_CROWN);
 else OAM16[A1_REGENT_OAM*4]=0x0200;
 if(a1_regent&&!a1_has(A1F_MALAKAR)&&pro_ui>=4&&cq_state[9]==CQ_ACTIVE)oam_set32(A1_MALAKAR_OAM,32*8-cam_x-16,13*8-cam_y-24,256,5+EN_VOID);
 else OAM16[A1_MALAKAR_OAM*4]=0x0200;}
/* ---------- per-frame UI (pro_ui 5 choice, 6 Malakar's lances, 7 cold forge, 8 market) ---------- */
static void a1_market_buy(int row){
 int potion=pro_choice==2?4:5,ether=(pro_choice==1||cq_state[6]==CQ_DONE);
 if(row==0){if(credits<potion){say("NOT ENOUGH CREDITS.");return;}credits=(u8)(credits-potion);inv[ITEM_POTION]=(u8)mini(99,inv[ITEM_POTION]+1);}
 else if(row==1){if(!ether){say("THE ETHER CARAVAN IS LATE. TRY AGAIN ONCE THE ROAD IS SAFER.");return;}if(credits<7){say("NOT ENOUGH CREDITS.");return;}credits=(u8)(credits-7);inv[ITEM_ETHER]=(u8)mini(99,inv[ITEM_ETHER]+1);}
 else if(row==2){if(!inv[ITEM_SHARD]){say("YOU HAVE NO SHARDS TO SELL.");return;}inv[ITEM_SHARD]--;credits=(u8)mini(255,credits+3);}
 else{if(!inv[ITEM_CORE]){say("YOU HAVE NO CORES TO SELL.");return;}inv[ITEM_CORE]--;credits=(u8)mini(255,credits+12);}
 lc_sfx(SFX_CONFIRM);save_game();}
static int act1_update(u16 newk){
 if(pro_ui==5){
  if(newk&(KEY_UP|KEY_DOWN)){a1_sel^=1;lc_sfx(SFX_MOVE);}
  if(newk&KEY_B&&a1_choice_tag==1){pro_ui=0;return 1;}
  if(newk&KEY_A){pro_ui=0;
   if(a1_choice_tag==1){if(a1_sel){say("BREE: SUIT YOURSELF. THE SOUP'S STILL FREE.");}
    else if(credits<3)say("BREE: THREE CREDITS, LOVE. THE TRADER BUYS SHARDS.");
    else{credits=(u8)(credits-3);player.hp=max_hp;player_mp=max_mp;save_game();say("YOU SLEEP UNDER A QUILT THAT SMELLS OF APPLES. HP AND MP RESTORED. SAVED.");}}
   else if(a1_choice_tag==2){a1_reply=(u8)(a1_sel+1);save_game();if(a1_sel)A1_CARDS(A1_REPLY_2,31);else A1_CARDS(A1_REPLY_1,31);}}
  return 1;}
 if(pro_ui==6){
  if(!a1_heat_dir){if(++a1_heat>=23)a1_heat_dir=1;}else{if(!--a1_heat)a1_heat_dir=0;}
  if(a1_flash&&a1_flash!=200)a1_flash--;
  if(newk&KEY_B){
   if(a1_heat>=17&&a1_heat<=21){a1_deflects++;a1_flash=30;lc_sfx(SFX_CRIT);}
   else{a1_flash=200;lc_sfx(SFX_HIT);if(player.hp>1)player.hp--;}
   a1_lances++;a1_heat=0;a1_heat_dir=0;
   if(a1_deflects>=2){pro_ui=0;add_xp(10);A1_CARDS(A1_AXIS_CARDS,32);}}
  return 1;}
 if(pro_ui==7){
  if(!a1_heat_dir){if(++a1_heat>=17)a1_heat_dir=1;}else{if(!--a1_heat)a1_heat_dir=0;}
  if(a1_flash&&a1_flash!=200)a1_flash--;
  if(newk&KEY_B){pro_ui=0;say("THE FORGE COOLS. THE MOULD AND ORE WILL WAIT.");return 1;}
  if(newk&KEY_A){
   if(a1_heat>=11&&a1_heat<=13){a1_strikes++;a1_flash=24;lc_sfx(SFX_CRIT);
    if(a1_strikes>=3){a1_flags|=A1F_KEY;add_xp(10);save_game();pro_ui=0;A1_CARDS(A1_KEY_CARDS,0);}}
   else{a1_flash=200;lc_sfx(SFX_HIT);}}
  return 1;}
 if(pro_ui==8){
  if(newk&KEY_B){pro_ui=0;return 1;}
  if(newk&KEY_UP){a1_sel=(u8)((a1_sel+3)&3);lc_sfx(SFX_MOVE);}if(newk&KEY_DOWN){a1_sel=(u8)((a1_sel+1)&3);lc_sfx(SFX_MOVE);}
  if(newk&KEY_A)a1_market_buy(a1_sel);return 1;}
 return 0;}
static int act1_draw(void){int i;
 if(pro_ui==5){ui_frame(9,19,15);
  if(a1_choice_tag==1){ui_text(2,10,"THE FALLOW INN",14);ui_wrap_text(11,"A WARM BED FOR THREE CREDITS. RESTORES HP AND MP AND SAVES.",15,2);
   ui_text(2,14,a1_sel==0?">":" ",13);ui_text(4,14,"REST  3 CREDITS",a1_sel==0?14:15);ui_text(2,16,a1_sel==1?">":" ",13);ui_text(4,16,"NOT NOW",a1_sel==1?14:15);
   ui_text(2,18,"UP DOWN   A DECIDE",14);}
  else{ui_text(2,10,"ANSWER MALAKAR",14);
   ui_text(2,13,a1_sel==0?">":" ",13);ui_wrap_text_step(13,"  PAIN IS NO REASON TO ERASE THE WORLDS",a1_sel==0?14:15,2,1);
   ui_text(2,16,a1_sel==1?">":" ",13);ui_wrap_text_step(16,"  WHO DECIDES WHICH WORLD SURVIVES",a1_sel==1?14:15,1,1);
   ui_text(2,18,"UP DOWN   A ANSWER",14);}
  return 1;}
 if(pro_ui==6){ui_frame(9,19,15);ui_text(2,10,"MALAKAR'S LANCE",14);ui_text(2,11,"BRACE AS IT LANDS",15);
  for(i=0;i<24;i++){const char*c=(i==a1_heat)?"*":(i>=17&&i<=21)?"+":"-";ui_text(3+i,13,c,(i==a1_heat)?14:(i>=17&&i<=21)?13:8);}
  ui_text(2,15,"DEFLECTED",13);for(i=0;i<2;i++)ui_text(13+i*2,15,i<a1_deflects?"*":"-",i<a1_deflects?14:8);
  ui_text(2,16,a1_flash==200?"THE LANCE GRAZES YOU. AGAIN.":a1_flash?"DEFLECTED! THE HEART FLARES.":"PRESS B IN THE + ZONE.",a1_flash==200?8:15);
  ui_text(2,18,"B BRACE",14);return 1;}
 if(pro_ui==7){ui_frame(9,19,15);ui_text(2,10,"COLD VAULT FORGE",14);ui_text(2,11,"CAST THE KEY IN THE GLOW",15);
  for(i=0;i<18;i++){const char*c=(i==a1_heat)?"*":(i>=11&&i<=13)?"+":"-";ui_text(5+i,13,c,(i==a1_heat)?14:(i>=11&&i<=13)?13:8);}
  ui_text(2,15,"STRIKES",13);for(i=0;i<3;i++)ui_text(11+i*2,15,i<a1_strikes?"*":"-",i<a1_strikes?14:8);
  ui_text(2,16,a1_flash==200?"THE METAL SPITS. AGAIN.":a1_flash?"CLANG! THE KEY TAKES SHAPE.":"WAIT FOR THE + ZONE.",a1_flash==200?8:15);
  ui_text(2,18,"A STRIKE   B STEP AWAY",14);return 1;}
 if(pro_ui==8){int potion=pro_choice==2?4:5,ether=(pro_choice==1||cq_state[6]==CQ_DONE);
  ui_frame(0,19,15);ui_text(2,2,"OAKWOOD MARKET // HALE",14);
  ui_text(2,5,a1_sel==0?">":" ",13);ui_text(4,5,"BUY POTION",15);ui_num(19,5,potion,15);ui_text(22,5,"CR",13);
  ui_text(2,7,a1_sel==1?">":" ",13);ui_text(4,7,"BUY ETHER",ether?15:8);if(ether){ui_num(19,7,7,15);ui_text(22,7,"CR",13);}else ui_text(18,7,"SOLD OUT",8);
  ui_text(2,9,a1_sel==2?">":" ",13);ui_text(4,9,"SELL SHARD  +3",15);
  ui_text(2,11,a1_sel==3?">":" ",13);ui_text(4,11,"SELL CORE  +12",15);
  ui_text(2,13,"CREDITS",13);ui_num(11,13,credits,15);ui_text(16,13,"POTIONS",13);ui_num(24,13,inv[ITEM_POTION],15);
  ui_wrap_text(14,pro_choice==2?"HALE: SELA SAYS YOU CARRIED HER PATIENTS. POTIONS ARE FOUR FOR YOU.":pro_choice==1?"HALE: BRINDLEMARK'S STORES SURVIVED, SO MY ETHER CRATES DID TOO.":
   ether?"HALE: THE ETHER CARAVAN FINALLY MADE IT.":"HALE: ETHER'S STUCK ON THE ROAD. POTIONS I HAVE.",15,2);
  ui_text(2,17,"UP DOWN  A TRADE  B EXIT",13);oam_hide_all();oam_set(0,190,36,116,15,0);oam_ui_portrait(0);return 1;}
 return 0;}
/* ---------- HUD ---------- */
static const char*act1_objective(int q){
 if(q==5){if(!a1_has(A1F_MET_RAVEN))return "Q05 TALK TO RAVENSWOOD";if(a1_has(A1F_MAP_FOUND))return "Q05 MAP TO RAVENSWOOD";
  if(a1_has(A1F_PELL_HEALED))return "Q05 SPLIT OAK: ROW 4 TREE 3";return "Q05 HELP PELL AT THE INN";}
 if(q==6)return "Q06 READ AUREL'S JOURNAL";
 if(q==7){if(!a1_has(A1F_ASCENT))return "Q07 CRAGSTONE: EAST GATE";
  if(!a1_has(A1F_GUARD)&&!a1_has(A1F_KEEP))return "Q07 SEALS: GALLERY + VAULT";
  if(!a1_has(A1F_GUARD))return "Q07 SEAL: GALLERY OF BLADES";
  if(!a1_has(A1F_KEEP))return a1_has(A1F_KEY)?"Q07 OPEN THE VAULT DOOR":"Q07 CAST THE VAULT KEY";
  return "Q07 LIGHT THE FOUR SOCKETS";}
 if(q==8)return "Q08 FACE OR MEND THE REGENT";
 if(q==9)return "Q09 THE HEART OF ERIDORIA";
 return 0;}
static const char*act1_hud_line(void){int q;
 if(current_world!=0||game_mode!=MODE_SURFACE||BH_IS_ROOM)return 0;
 if(!(current_room==2||current_room==3||current_room==4||A1_IS_ROOM))return 0;
 if(current_room==2&&cq_state[5]==CQ_ACTIVE&&!a1_has(A1F_MET_RAVEN))return "Q05 OAKWOOD: NORTHEAST ROAD";
 for(q=5;q<=9;q++)if(cq_state[q]==CQ_ACTIVE)return act1_objective(q);
 if(cq_state[10]==CQ_ACTIVE&&cq_state[9]==CQ_DONE&&!(story_flags&ST_CITY))return "Q10 HIDDEN CITY: NE RUNE";
 return 0;}
static void act1_frame(void){
 if(v10_tutorial&&cq_state[5]!=CQ_LOCKED&&a1_flags)v10_tutorial=0;
 if(current_world==0&&current_room==3&&game_mode==MODE_SURFACE&&cq_state[5]==CQ_LOCKED&&(cq_state[4]==CQ_DONE||cq_state[0]==CQ_LOCKED||(pro_flags&PF_MIGRATED))){
  cq_set(5,CQ_ACTIVE);save_game();}
 if(current_world==0&&current_room==A1_GALLERY&&game_mode==MODE_SURFACE){int i;
  for(i=0;i<3;i++)if(!enemies[i].active&&!(a1_sentries&(1u<<i))){a1_sentries|=(u8)(1u<<i);save_game();}}}
#ifdef QA_AUTORUN
/* Host QA helpers: speak to an NPC already spawned in this room, and click through story cards. */
static void qa_a1_talk(int id){int i,k;for(i=0;i<npc_count;i++)if(npc_runtime[i].id==id){npc_speak(i);
  for(k=0;k<8&&npc_dialogue_active;k++)npc_advance();if(npc_dialogue_active)npc_close();return;}}
static void qa_a1_flush(void){int n=0;while(pro_ui==4&&n++<24)prologue_update(KEY_A);}
#endif
#endif
