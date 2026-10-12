/* ACT II: THE TRIAL OF MIRRORS (Q10-Q14). See act2_mirrors_state.h for the
   layout. All dialogue is original game-adaptation text for the cartridge. */
#ifndef ACT2_MIRRORS_H
#define ACT2_MIRRORS_H
static void act2_reset(void){int i;a2_flags=0;a2_rounds=0;a2_arena_result=0;a2_slips=0;
 a2_order[0]=3;a2_order[1]=0;a2_order[2]=4;a2_order[3]=1;a2_order[4]=2;
 a2_tide=0;a2_high=0;a2_arena=0;a2_channel=0;a2_kneel=0;a2_jam=0;for(i=0;i<3;i++){a2_kneel_t[i]=0;a2_ring[i]=0;}
 a2_sel=0;a2_pick=255;a2_last=1;a2_mirror=1;a2_wins=0;a2_hp=A2_DUEL_HP;a2_phase=0;a2_timer=0;a2_result=0;
 a2_ring_lock=0;a2_ring_tick=0;a2_slow=0;a2_slow_uses=0;a2_flash=0;a2_notice="";}
static u16 a2_pack_order(void){int i;u16 v=0;for(i=0;i<5;i++)v|=(u16)((a2_order[i]&7u)<<(i*3));return v;}
static int a2_unpack_order(u16 v){int i,seen=0;for(i=0;i<5;i++){int p=(v>>(i*3))&7;if(p>4||(seen&(1<<p)))return 0;seen|=1<<p;}
 for(i=0;i<5;i++)a2_order[i]=(u8)((v>>(i*3))&7);return 1;}
static void act2_save_into(u8*b){int o=A2_SRAM_AT;u16 ord=a2_pack_order();
 b[o]='B';b[o+1]=1;b[o+2]=(u8)a2_flags;b[o+3]=(u8)(a2_flags>>8);b[o+4]=a2_rounds;b[o+5]=(u8)ord;b[o+6]=(u8)(ord>>8);
 b[o+7]=a2_arena_result;b[o+8]=a2_slips;b[o+9]=0;}
static int a2_has(u16 f){return (a2_flags&f)==f;}
static int a2_done(int q){return cq_state[q]==CQ_DONE;}
/* The single ACTIVE Act II node is the first one not yet done. */
static void a2_advance(void){int q,act=0;
 if(!(story_flags&ST_HEART)||cq_state[9]!=CQ_DONE)return;
 for(q=10;q<=14;q++){if(cq_state[q]==CQ_DONE)continue;if(!act){cq_set(q,CQ_ACTIVE);act=1;}else cq_set(q,CQ_LOCKED);}
 if(!act&&cq_state[15]==CQ_LOCKED)cq_set(15,CQ_ACTIVE);}
/* Saves without the 'B' block: credit what the old Hidden City / Dream Veil
   route already earned, one node per story flag. Nothing beyond that. */
static void act2_migrate(void){
 act2_reset();
 if(!(story_flags&ST_HEART)||cq_state[9]!=CQ_DONE)return;
 if(story_flags&ST_CITY){a2_flags|=A2F_ECHOES|A2F_GATE|A2F_LYSARA|A2F_MIGRATED;cq_set(10,CQ_DONE);}
 if(story_flags&ST_COURAGE){a2_flags|=A2F_COURAGE|A2F_MIGRATED;cq_set(11,CQ_DONE);}
 if(story_flags&ST_WISDOM){a2_flags|=A2F_WISDOM|A2F_MIGRATED;cq_set(12,CQ_DONE);{int i;for(i=0;i<5;i++)a2_order[i]=(u8)i;}}
 if(story_flags&ST_DREAM){a2_flags|=A2F_UNITY|A2F_MIGRATED;cq_set(13,CQ_DONE);}
 if((story_flags&ST_CHRONO)&&a2_done(10)&&a2_done(11)&&a2_done(12)&&a2_done(13)){a2_flags|=A2F_KAELEN|A2F_CHRONO|A2F_MIGRATED;cq_set(14,CQ_DONE);}
 a2_advance();}
static void act2_restore_from(const u8*b,int valid){int o=A2_SRAM_AT;
 if(!valid||b[o]!='B'||b[o+1]!=1){act2_migrate();return;}
 act2_reset();a2_flags=(u16)(b[o+2]|((u16)b[o+3]<<8));a2_rounds=b[o+4];
 if(!a2_unpack_order((u16)(b[o+5]|((u16)b[o+6]<<8)))){a2_order[0]=3;a2_order[1]=0;a2_order[2]=4;a2_order[3]=1;a2_order[4]=2;}
 a2_arena_result=(u8)(b[o+7]&63);a2_slips=b[o+8];}
static void a2_go(int room,int tx,int ty){current_room=(u8)room;current_layer=1;player.x=(s16)(tx*8);player.y=(s16)(ty*8);
 cosmos.x=player.x+16;cosmos.y=player.y-12;a2_arena=0;a2_pick=255;a2_tide=0;a2_high=0;generate_surface();refresh_camera();save_game();}
/* ---------- story cards ---------- */
static const ProCard A2_TIDE_ARRIVE[]={
 {"TIDE MEMORY","A GREY SHORE PAST THE NORTHEAST RUNE. THE SEA BREATHES IN AND OUT, AND THE SAND BARS COME AND GO."},
 {"COSMOS","LISTEN. THE WAVES ARE SAYING WORDS. OLD ONES. SOMEONE'S, ONCE."},
 {"ARIN","THEN WE WAIT FOR LOW WATER AND READ THEM. THE CITY GATE IS ON THE FAR SHORE."}};
static const ProCard A2_ECHOES[]={
 {"TIDE MEMORY","HOME. FORGE. TOGETHER. THE THREE WORDS RISE OUT OF THE WATER AT ONCE, AND THE CITY GATE ANSWERS."},
 {"COSMOS","THIS SEA KEEPS WHAT PEOPLE SAY. EVEN WHAT THEY ONLY MEANT TO SAY."}};
static const ProCard A2_CITY_ARRIVE[]={
 {"THE FORGOTTEN CITY","WHITE STREETS UNDER A SKY THAT FORGOT TO MOVE. NOTHING IS BROKEN. NOTHING IS LIVED IN."},
 {"COSMOS","SOMEONE IS STILL ON DUTY HERE. IN THE PLAZA. SHE HAS BEEN WAITING A LONG TIME."}};
static const ProCard A2_LYSARA[]={
 {"LYSARA","I AM LYSARA, LAST SENTINEL OF THE ORDER THAT GUARDED THE FIRST AXES. YOU CARRY ONE OF THEM, SMITH."},
 {"LYSARA","AN AXIS IS NOT A WEAPON. IT IS A PROMISE THAT A WORLD MAY KEEP ITS OWN SHAPE. MY ORDER KEPT THAT PROMISE."},
 {"LYSARA","BEFORE THE CHRONOHEART WILL WAKE FOR YOU, I MUST KNOW WHAT YOU ARE. THREE TRIALS. THREE ROOMS."},
 {"LYSARA","WEST, THE HALL OF WHISPERS: COURAGE. EAST, THE CHAMBER OF ILLUMINATION: WISDOM. NORTHEAST, THE ARENA."},
 {"ARIN","AND IF I FAIL ONE?"},
 {"LYSARA","THEN YOU TRY AGAIN. A TRIAL THAT ENDS YOU TEACHES NOTHING. GO WEST FIRST."}};
static const ProCard A2_MIRROR_MEET[]={
 {"HALL OF WHISPERS","THE LAST MIRROR DOES NOT SHOW THE ROOM. IT SHOWS ARIN, HAMMER IN HAND, WATCHING HIM BACK."},
 {"MIRROR ARIN","I KNOW EVERY SWING YOU HAVE. I LEARNED THEM AS YOU MADE THEM. I WILL ANSWER WITH YOUR LAST ONE."},
 {"COSMOS","IT COPIES YOU, ARIN. IF YOU REPEAT YOURSELF, IT CAN'T LOSE. BEAT THE MOVE YOU JUST MADE."}};
static const ProCard A2_COURAGE_DONE[]={
 {"MIRROR ARIN","YOU STOPPED DOING WHAT FELT SAFE. THAT IS ALL COURAGE IS. THE MIRROR LOWERS ITS HAMMER."},
 {"ARIN","I WAS AFRAID OF LOSING THEM. BRINDLEMARK. COSMOS. THAT FEAR WAS SWINGING FOR ME."},
 {"LYSARA","THE HALL IS QUIET. COURAGE IS RECORDED. THE CHAMBER OF ILLUMINATION, EAST OF THE PLAZA, IS OPEN."}};
static const ProCard A2_WISDOM_DONE[]={
 {"ILLUMINATION","THE FIVE PANELS BURN IN ORDER. THE CHAMBER READS THEM ALOUD, ONE AFTER ANOTHER."},
 {"FIRST PANEL","THE GUARDIANS GATHER: KEEPERS SWORN TO PROTECT DIFFERENCE, NOT TO RULE IT."},
 {"SECOND PANEL","THE EIGHT AXES ARE SET. DISTANCE, MEMORY, HEAT, GROWTH, COLD, MACHINE, SHADOW, CROWN."},
 {"THIRD PANEL","MALAKAR, YOUNGEST OF THE GUARDIANS, WATCHES THE AXES STRAIN AND PROPOSES ONE SEAL OVER ALL."},
 {"FOURTH PANEL","THE ORDER SPLITS. HALF FOLLOW HIS SEAL, HALF REFUSE. THE FRACTURE IS A QUARREL BEFORE IT IS A WAR."},
 {"FIFTH PANEL","TO SAVE BOTH SIDES FROM EACH OTHER, THE WORLDS ARE PULLED APART AND THE SKY IS STITCHED SHUT."},
 {"LYSARA","SO YOU SEE: MALAKAR WAS ONE OF US. WISDOM IS RECORDED. THE ARENA OF SOULS WAITS NORTHEAST."}};
static const ProCard A2_ARENA_MEET[]={
 {"ARENA OF SOULS","A RING OF STONE SEATS AROUND ONE LEVER. THREE SENTRY GATES. THE SEATS ARE EMPTY AND LISTENING."},
 {"LYSARA","UNITY. YOUR COMPANION HOLDS THE LEVER UNTIL THE ARENA WAKES. YOU KEEP THE SENTRIES OFF IT."},
 {"COSMOS","I'VE GOT THE LEVER. YOU'VE GOT ME. A FALLEN SENTRY KNEELS. SPARE IT BESIDE IT, OR STRIKE AGAIN."}};
static const ProCard A2_UNITY_DONE[]={
 {"ARENA OF SOULS","THE LEVER LOCKS HOME. THE STONE SEATS LIGHT, ONE BY ONE, LIKE A CROWD STANDING UP."},
 {"LYSARA","TWO HANDS ON ONE TASK. THAT IS UNITY, AND IT IS RECORDED. THE CHRONOHEART WILL HEAR YOU NOW."},
 {"COSMOS","SOMEONE ELSE JUST ARRIVED IN THE PLAZA. THEY FEEL... EARLY. OR LATE."}};
static const ProCard A2_PACT[]={
 {"THE SENTRIES","THREE SENTRIES YOU SPARED RISE AND BOW. NO ORDER TOLD THEM TO. THEY CHOSE TO."},
 {"LYSARA","MERCY TO THINGS THAT WERE BUILT TO FIGHT YOU. THE ARENA OFFERS ITS RAREST GIFT: THE SOUL PACT."},
 {"SOUL PACT","THE SENTRIES' VOW BINDS TO COSMOS. MAX HP +2. COSMOS TRUST +20. THEY WILL ANSWER LATER."}};
static const ProCard A2_KAELEN_MEET[]={
 {"KAELEN","A WEAVER OF TIME, AT YOUR SERVICE, MORE OR LESS. I HAVE BEEN ARRIVING HERE FOR NINE HUNDRED YEARS."},
 {"KAELEN","THE CHRONOHEART HOLDS THE CITY'S MEMORY IN ORDER. IT TORE WHEN THE WORLDS WERE SEPARATED."},
 {"KAELEN","I CAN HOLD THE THREADS STILL FOR A BREATH OR TWO. YOU MUST SET THE RINGS. THE SANCTUM IS NORTH."}};
static const ProCard A2_CHRONO_MEET[]={
 {"CHRONOHEART","THREE RINGS OF TORN MEMORY SPIN AROUND A DARK CORE. EACH HAS ONE NOTCH THAT FITS."},
 {"KAELEN","LOCK EACH RING WHEN ITS NOTCH CROSSES THE MARK. PRESS L AND I WILL SLOW THE THREADS. THREE TIMES."}};
static const ProCard A2_CHRONO_DONE[]={
 {"CHRONOHEART","THE RINGS LOCK. THE TORN SEQUENCE PLAYS THROUGH IN ORDER, FOR THE FIRST TIME IN AN AGE."},
 {"MEMORY","A SKY WITH NO SEAMS. EIGHT WORLDS, EACH STRANGE IN ITS OWN WAY. THEN A SILENCE THAT EATS THE STRANGENESS."},
 {"MEMORY","NIHILOS. NOT A MONSTER. AN ABSENCE. WHAT IT TOUCHES FORGETS ITS HISTORY AND TAKES THE SAME SHAPE AS EVERYTHING."},
 {"MEMORY","THE GUARDIANS COULD NOT FIGHT A NOTHING. SO THEY PULLED THE WORLDS APART, TO STARVE IT OF SAMENESS."},
 {"KAELEN","SEPARATION WAS NEVER A PUNISHMENT. IT WAS A WALL. MALAKAR'S ONE SEAL WOULD BUILD NIHILOS A DOOR."},
 {"LYSARA","NOW YOU KNOW WHAT I GUARDED. TAKE THE STABLE ROUTE, SMITH. THE OLD QUARTER LEADS TO THE DREAM VEIL."}};
static const ProCard A2_ACT_DONE[]={
 {"KAELEN","THE ROUTE IS STITCHED. THE OLD QUARTER, SOUTHWEST OF THE PLAZA, OPENS TOWARD THE DREAM VEIL."},
 {"ACT II COMPLETE","COURAGE, WISDOM AND UNITY RECORDED. THE CHRONOHEART BEATS. THE FIRST GUARDIANS' STORY IS YOURS."}};
static const ProCard A2_HARMONY_DONE[]={
 {"HARMONY CLEARING","SONG, ROOT AND LIGHT CIRCLE THE OLD STONE. THE CLEARING REMEMBERS HOW TO BE A CLEARING."},
 {"COSMOS","THEY'RE NOT ASKING FOR ANYTHING. THEY JUST WANTED SOMEONE TO COME BACK. WE CAN REST HERE ANY TIME."},
 {"HARMONY CHIME","MAX MP +2. THE STONE NOW RESTORES HP AND MP AND SAVES WHENEVER YOU RETURN."}};
#define A2_CARDS(a,t) pro_cards_open(PRO_CARD_SET(a),t)
/* ---------- quest steps ---------- */
static void a2_finish(int q){
 cq_set(q,CQ_DONE);
 if(q==10){a2_flags|=A2F_LYSARA;story_flags|=ST_CITY;add_xp(20);cosmos.trust=(u8)mini(255,cosmos.trust+4);}
 else if(q==11){a2_flags|=A2F_COURAGE;story_flags|=ST_COURAGE;inv[ITEM_POTION]=(u8)mini(99,inv[ITEM_POTION]+2);add_xp(40);}
 else if(q==12){a2_flags|=A2F_WISDOM;story_flags|=ST_WISDOM;inv[ITEM_ETHER]=(u8)mini(99,inv[ITEM_ETHER]+2);mag_stat=(u8)mini(99,mag_stat+1);add_xp(40);}
 else if(q==13){a2_flags|=A2F_UNITY;story_flags|=ST_DREAM;cosmos.trust=(u8)mini(255,cosmos.trust+10);credits=(u8)mini(255,credits+25);add_xp(40);}
 else if(q==14){a2_flags|=A2F_CHRONO;story_flags|=ST_CHRONO;inv[ITEM_CORE]=(u8)mini(99,inv[ITEM_CORE]+1);cosmos.memory_flags|=MEM_ANOMALY;add_xp(60);}
 a2_advance();save_game();}
static void a2_duel_open(void){pro_ui=10;a2_sel=0;a2_last=1;a2_mirror=1;a2_wins=0;a2_hp=A2_DUEL_HP;a2_phase=0;a2_timer=0;a2_result=0;
 a2_notice="THE MIRROR WAITS FOR YOUR FIRST MOVE.";dialogue_timer=0;lc_sfx(SFX_CRY);}
static void a2_ring_open(void){int i;pro_ui=11;for(i=0;i<3;i++)a2_ring[i]=(u8)(i*7+2);a2_ring_lock=0;a2_ring_tick=0;a2_slow=0;a2_slow_uses=0;a2_flash=0;
 a2_notice="LOCK THE OUTER RING FIRST.";dialogue_timer=0;}
static void a2_arena_begin(void);
static void act2_after_cards(int tag){
 if(tag==40){say("LOW WATER OPENS THE SAND BARS. THREE ECHO STONES. HIGH WATER TAKES THE BARS.");}
 else if(tag==41){a2_flags|=A2F_GATE;save_game();say("THE CITY GATE ON THE EAST SHORE IS OPEN.");}
 else if(tag==42){say("Q10 FIND THE SENTINEL IN THE PLAZA.");}
 else if(tag==43){a2_finish(10);say("Q11 COURAGE: THE HALL OF WHISPERS, WEST DOOR OF THE PLAZA.");}
 else if(tag==44){a2_duel_open();}
 else if(tag==45){a2_finish(11);a2_go(A2_WHISPERS,50,32);say("Q12 WISDOM: THE CHAMBER OF ILLUMINATION, EAST DOOR OF THE PLAZA.");}
 else if(tag==46){a2_finish(12);say("Q13 UNITY: THE ARENA OF SOULS, NORTHEAST DOOR OF THE PLAZA.");}
 else if(tag==47){a2_arena_begin();}
 else if(tag==48){int spared=(a2_arena_result&7)==7;a2_finish(13);
  if(spared){a2_flags|=A2F_PACT;max_hp=(u8)mini(99,max_hp+2);player.hp=max_hp;cosmos.trust=(u8)mini(255,cosmos.trust+20);save_game();A2_CARDS(A2_PACT,49);return;}
  say("Q14 KAELEN WAITS IN THE PLAZA BY THE NORTH DOOR.");}
 else if(tag==49){say("Q14 KAELEN WAITS IN THE PLAZA BY THE NORTH DOOR.");}
 else if(tag==50){a2_flags|=A2F_KAELEN;save_game();say("Q14 THE CHRONOHEART SANCTUM IS THROUGH THE NORTH DOOR.");}
 else if(tag==51){a2_ring_open();}
 else if(tag==52){a2_finish(14);A2_CARDS(A2_ACT_DONE,53);return;}
 else if(tag==53){say("ACT II COMPLETE. THE OLD QUARTER LANE IS OPEN, SOUTHWEST OF THE PLAZA.");}
 else if(tag==54){say("THE HARMONY STONE HUMS. REST HERE ANY TIME.");}
}
/* ---------- rooms ---------- */
static void a2_rect(int x0,int y0,int x1,int y1,int tile,int pal,int col){int x,y;
 for(y=y0;y<=y1;y++)for(x=x0;x<=x1;x++)map_put(x,y,tile,pal,col,TR_NONE);}
static void a2_paint_bars(void){int x,y,low=!a2_high;
 for(x=20;x<=28;x++)for(y=31;y<=33;y++)map_put(x,y,low?T_PATH:T_WATER,1,low?C_FREE:C_WALL,TR_NONE);
 for(x=36;x<=44;x++)for(y=31;y<=33;y++)map_put(x,y,low?T_PATH:T_WATER,1,low?C_FREE:C_WALL,TR_NONE);
 for(x=20;x<=44;x++){if(x>=29&&x<=35)continue;map_put(x,30,(x==24)?T_RUNE:(low?T_FOAM:T_WATER),3,C_WALL,(x==24)?TR_A2_ECHO:TR_NONE);
  map_put(x,34,(x==40)?T_RUNE:(low?T_FOAM:T_WATER),3,C_WALL,(x==40)?TR_A2_ECHO:TR_NONE);}
 for(y=0;y<3;y++)if(a2_flags&(1u<<y))map_put(A2_ECHO_X[y],A2_ECHO_Y[y],T_STAR,3,C_WALL,TR_A2_ECHO);}
static void a2_gen_tide(void){int x,y;
 map_fill(T_WATER,0);map_border();
 for(y=1;y<63;y++)for(x=1;x<63;x++)map_put(x,y,T_WATER,0,C_WALL,TR_NONE);
 /* West shore (Brindlemark side) and east shore (city side). */
 a2_rect(2,18,19,46,T_FLOOR,1,C_FREE);a2_rect(45,18,61,46,T_FLOOR,1,C_FREE);
 for(y=18;y<=46;y+=4){map_put(19,y,T_FOAM,3,C_WALL,TR_NONE);map_put(45,y,T_FOAM,3,C_WALL,TR_NONE);}
 /* The islet between the bars never floods. */
 a2_rect(29,24,35,40,T_GRASS,0,C_FREE);map_put(29,24,T_TREE,3,C_WALL,TR_NONE);map_put(35,40,T_TREE,3,C_WALL,TR_NONE);
 map_put(32,26,T_RUNE,3,C_WALL,TR_A2_ECHO);
 a2_paint_bars();
 /* Doors: Brindlemark west, the Forgotten City east. */
 a2_rect(2,31,4,33,T_PATH,1,C_FREE);map_put(1,32,T_DOOR,2,C_FREE,TR_A2_TO_BRINDLE);
 a2_rect(58,31,61,33,T_PATH,1,C_FREE);map_put(62,32,a2_has(A2F_GATE)?T_DOOR:T_WALL,2,C_FREE,TR_A2_CITY_GATE);
 for(x=6;x<=16;x+=5)map_put(x,22,T_LANTERN,3,C_WALL,TR_NONE);
 for(x=48;x<=58;x+=5)map_put(x,42,T_PILLAR,2,C_WALL,TR_NONE);}
static void a2_gen_city(void){int x,y;
 map_fill(T_RUIN,0);map_border();
 for(y=1;y<63;y++)for(x=1;x<63;x++)map_put(x,y,T_RUIN,2,C_WALL,TR_NONE);
 a2_rect(8,9,55,56,T_FLOOR,2,C_FREE);
 for(x=12;x<=52;x+=8){if(x==32)continue;map_put(x,14,T_PILLAR,2,C_WALL,TR_NONE);map_put(x,50,T_PILLAR,2,C_WALL,TR_NONE);}
 for(y=20;y<=44;y+=8){map_put(14,y,T_LANTERN,3,C_WALL,TR_NONE);map_put(50,y,T_LANTERN,3,C_WALL,TR_NONE);}
 /* Fountain of still water in the plaza; Lysara stands before it. */
 a2_rect(29,34,35,38,T_WATER,1,C_WALL);map_put(32,36,T_FOAM,3,C_WALL,TR_NONE);
 map_put(26,30,T_ARCHIVE,3,C_WALL,TR_A2_MURAL);
 /* Doors. South: Tide Memory. West: Whispers. East: Illumination. North-east: Arena.
    North: Chronoheart Sanctum. North-west: Harmony Clearing. South-west: Old Quarter. */
 a2_rect(31,57,33,58,T_PATH,1,C_FREE);map_put(32,59,T_DOOR,2,C_FREE,TR_A2_TO_TIDE);
 a2_rect(6,31,7,33,T_PATH,1,C_FREE);map_put(5,32,a2_done(10)?T_DOOR:T_WALL,2,C_FREE,TR_A2_TO_WHISPERS);
 a2_rect(56,31,57,33,T_PATH,1,C_FREE);map_put(58,32,a2_done(11)?T_DOOR:T_WALL,2,C_FREE,TR_A2_TO_LIGHT);
 a2_rect(47,7,49,8,T_PATH,1,C_FREE);map_put(48,6,(a2_done(11)&&a2_done(12))?T_DOOR:T_WALL,2,C_FREE,TR_A2_TO_ARENA);
 a2_rect(31,7,33,8,T_PATH,1,C_FREE);map_put(32,6,a2_done(13)?T_DOOR:T_WALL,2,C_FREE,TR_A2_TO_SANCTUM);
 a2_rect(15,7,17,8,T_PATH,1,C_FREE);map_put(16,6,T_DOOR,2,C_FREE,TR_A2_TO_HARMONY);
 a2_rect(9,57,11,58,T_PATH,1,C_FREE);map_put(10,59,a2_done(14)?T_DOOR:T_WALL,2,C_FREE,TR_A2_TO_OLDQ);}
static void a2_gen_whispers(void){int x,y;
 map_fill(T_RUIN,0);map_border();
 for(y=1;y<63;y++)for(x=1;x<63;x++)map_put(x,y,T_RUIN,2,C_WALL,TR_NONE);
 a2_rect(8,27,55,37,T_FLOOR,2,C_FREE);
 for(x=14;x<=50;x+=6){map_put(x,27,T_CRYSTAL,3,C_WALL,TR_NONE);map_put(x,37,T_CRYSTAL,3,C_WALL,TR_NONE);}
 map_put(30,27,T_MOON,3,C_WALL,TR_A2_WHISPER);map_put(42,37,T_MOON,3,C_WALL,TR_A2_WHISPER);
 a2_rect(56,31,57,33,T_PATH,1,C_FREE);map_put(58,32,T_DOOR,2,C_FREE,TR_A2_TO_CITY);
 map_put(8,32,a2_done(11)?T_STAR:T_CRYSTAL,3,C_WALL,TR_A2_MIRROR);}
static const char*const A2_PANEL_NAME[5]={"THE GUARDIANS GATHER","THE EIGHT AXES ARE SET","MALAKAR PROPOSES A SEAL","THE ORDER SPLITS","THE WORLDS ARE PULLED APART"};
static void a2_paint_panels(void){int i;
 for(i=0;i<5;i++){int ok=a2_order[i]==i||a2_done(12);
  map_put(16+i*8,18,ok?T_STAR:T_LANTERN,3,C_WALL,TR_NONE);
  map_put(16+i*8,20,(a2_pick==i)?T_CRYSTAL:T_ARCHIVE,3,C_WALL,TR_A2_PANEL);}}
static void a2_gen_light(void){int x,y;
 map_fill(T_RUIN,0);map_border();
 for(y=1;y<63;y++)for(x=1;x<63;x++)map_put(x,y,T_RUIN,2,C_WALL,TR_NONE);
 a2_rect(8,14,55,44,T_FLOOR,2,C_FREE);
 a2_paint_panels();
 map_put(32,40,T_ARCHIVE,3,C_WALL,TR_A2_LIGHT_NOTE);
 a2_rect(6,29,7,31,T_PATH,1,C_FREE);map_put(5,30,T_DOOR,2,C_FREE,TR_A2_TO_CITY);
 for(x=12;x<=52;x+=10)map_put(x,44,T_PILLAR,2,C_WALL,TR_NONE);}
static void a2_gen_arena(void){int x,y;
 map_fill(T_RUIN,0);map_border();
 for(y=1;y<63;y++)for(x=1;x<63;x++)map_put(x,y,T_RUIN,2,C_WALL,TR_NONE);
 for(y=10;y<=52;y++)for(x=10;x<=54;x++){int dx=x-32,dy=y-31;if(dx*dx+dy*dy*2<=22*22)map_put(x,y,T_FLOOR,2,C_FREE,TR_NONE);}
 /* Stone seats ring the floor. */
 for(y=10;y<=52;y++)for(x=8;x<=56;x++){int dx=x-32,dy=y-31,d=dx*dx+dy*dy*2;if(d>22*22&&d<=24*24)map_put(x,y,a2_done(13)?T_LANTERN:T_STAIRS,2,C_WALL,TR_NONE);}
 a2_rect(31,46,33,53,T_PATH,1,C_FREE);map_put(32,54,T_DOOR,2,C_FREE,TR_A2_TO_CITY);
 map_put(A2_LEVER_TX,A2_LEVER_TY,a2_done(13)?T_STAR:T_LIFT,3,C_WALL,a2_done(13)?TR_NONE:TR_A2_LEVER);
 map_put(14,31,T_DOOR,2,C_WALL,TR_NONE);map_put(50,31,T_DOOR,2,C_WALL,TR_NONE);map_put(32,17,T_DOOR,2,C_WALL,TR_NONE);}
static void a2_gen_sanctum(void){int x,y;
 map_fill(T_RUIN,0);map_border();
 for(y=1;y<63;y++)for(x=1;x<63;x++)map_put(x,y,T_RUIN,2,C_WALL,TR_NONE);
 a2_rect(16,10,47,54,T_FLOOR,2,C_FREE);
 for(y=14;y<=50;y+=6){map_put(18,y,T_MOON,3,C_WALL,TR_NONE);map_put(45,y,T_MOON,3,C_WALL,TR_NONE);}
 map_put(32,14,a2_done(14)?T_STAR:T_CRYSTAL,3,C_WALL,TR_A2_CHRONOHEART);
 map_put(31,14,T_PILLAR,2,C_WALL,TR_NONE);map_put(33,14,T_PILLAR,2,C_WALL,TR_NONE);
 a2_rect(31,55,33,56,T_PATH,1,C_FREE);map_put(32,57,T_DOOR,2,C_FREE,TR_A2_TO_CITY);}
static void a2_gen_harmony(void){int x,y;
 map_fill(T_TREE,0);map_border();
 for(y=1;y<63;y++)for(x=1;x<63;x++)map_put(x,y,T_TREE,3,C_WALL,TR_NONE);
 for(y=12;y<=54;y++)for(x=10;x<=54;x++){int dx=x-32,dy=y-33;if(dx*dx+dy*dy<=21*21)map_put(x,y,T_GRASS,0,C_FREE,TR_NONE);}
 for(x=16;x<=48;x+=8){map_put(x,46,T_FLOWER,3,C_FREE,TR_NONE);map_put(x+3,20,T_FLOWER,3,C_FREE,TR_NONE);}
 map_put(32,28,a2_has(A2F_HARMONY)?T_STAR:T_RUNE,3,C_WALL,TR_A2_HARMONY_STONE);
 a2_rect(31,54,33,56,T_PATH,1,C_FREE);map_put(32,57,T_DOOR,2,C_FREE,TR_A2_TO_CITY);}
static void act2_generate(void){
 set_world_palette(current_room==A2_TIDE?2:current_room==A2_HARMONY?3:current_room==A2_ARENA?4:current_room==A2_CITY?5:6);
 if(current_room==A2_TIDE)a2_gen_tide();else if(current_room==A2_CITY)a2_gen_city();
 else if(current_room==A2_WHISPERS)a2_gen_whispers();else if(current_room==A2_LIGHT)a2_gen_light();
 else if(current_room==A2_ARENA)a2_gen_arena();else if(current_room==A2_SANCTUM)a2_gen_sanctum();else a2_gen_harmony();}
/* Room 5 is now the city's Old Quarter: a lane back to the plaza. */
static void act2_place_room5(void){
 if(!(story_flags&ST_HEART))return;
 a2_rect(57,30,59,32,T_PATH,1,C_FREE);map_put(60,31,T_DOOR,2,C_FREE,TR_A2_TO_CITY);}
static const char*act2_room_name(void){
 return current_room==A2_TIDE?"TIDE MEMORY":current_room==A2_CITY?"FORGOTTEN CITY":current_room==A2_WHISPERS?"HALL OF WHISPERS":
  current_room==A2_LIGHT?"CHAMBER OF ILLUMINATION":current_room==A2_ARENA?"ARENA OF SOULS":current_room==A2_SANCTUM?"CHRONOHEART SANCTUM":"HARMONY CLEARING";}
static int act2_spawn(void){return A2_IS_ROOM;}
/* ---------- NPC scripts (ids 60-89) ---------- */
static int act2_npc_visible(int id){
 if(id==NPC_A2_KAELEN)return a2_done(13);
 return 1;}
static void act2_npc_speak(void){int id=npc_dialogue_id;
 if(current_world!=0||pro_script)return;
 if(id==NPC_A2_LYSARA){
  if(cq_state[10]==CQ_ACTIVE)pro_say_lines(60,"A WOMAN IN WHITE ARMOUR TURNS FROM THE FOUNTAIN. HER SHADOW IS A LITTLE LATE TO FOLLOW HER.",
   "YOU CAME BY THE TIDE. GOOD. THE SEA ONLY LETS THROUGH THOSE WHO LISTEN.","SIT, SMITH. NO. STAND. YOU WILL WANT TO STAND FOR THIS.");
  else if(cq_state[11]==CQ_ACTIVE)pro_say_lines(61,"THE HALL OF WHISPERS IS THROUGH THE WEST DOOR. YOUR REFLECTION IS ALREADY WAITING.",0,0);
  else if(cq_state[12]==CQ_ACTIVE)pro_say_lines(62,"THE CHAMBER OF ILLUMINATION, EAST. THE PANELS ARE TRUE. ONLY THEIR ORDER WAS BROKEN.",0,0);
  else if(cq_state[13]==CQ_ACTIVE)pro_say_lines(63,"THE ARENA, NORTHEAST. TRUST YOUR COMPANION WITH THE LEVER. IT TRUSTS YOU WITH ITS BACK.",0,0);
  else if(cq_state[14]==CQ_ACTIVE)pro_say_lines(64,"KAELEN IS AN OLD FRIEND OF THE ORDER. HE IS ALWAYS ON TIME, EVENTUALLY.",0,0);
  else if(a2_done(14))pro_say_lines(65,"THE CITY'S MEMORY RUNS IN ORDER AGAIN. I WILL KEEP IT. GO, SMITH. KEEP THE WORLDS DIFFERENT.",0,0);
 }else if(id==NPC_A2_KAELEN){
  if(cq_state[14]==CQ_ACTIVE&&!a2_has(A2F_KAELEN))pro_say_lines(66,"A MAN WITH THREADS OF LIGHT KNOTTED AROUND HIS WRISTS LOOKS UP. AH. THIS IS TODAY, THEN.",0,0);
  else if(cq_state[14]==CQ_ACTIVE)pro_say_lines(67,"THE SANCTUM IS THROUGH THE NORTH DOOR. I WILL MEET YOU THERE. I ALREADY HAVE.",0,0);
  else pro_say_lines(68,"THE OLD QUARTER LANE IS STABLE. THE DREAM VEIL GATE STANDS AT ITS NORTH-EAST CORNER.",0,0);
 }else if(id==NPC_A2_KAELEN_SANCTUM){
  if(a2_done(14))pro_say_lines(69,"IT BEATS. LISTEN. NINE HUNDRED YEARS AND I NEVER GET TIRED OF THAT SOUND.",0,0);
  else pro_say_lines(70,"PRESS A AT THE CHRONOHEART. WHEN THE RINGS RUN FAST, PRESS L. I WILL HOLD THEM.",0,0);
 }else if(id==NPC_A2_SPIRIT_SONG){
  if(!a2_has(A2F_SPIRIT1))pro_say_lines(71,"A SMALL LIGHT HUMS THREE NOTES. NO ONE HAS SUNG BACK TO IT IN A VERY LONG TIME.","ARIN HUMS THE NOTES BACK, BADLY. THE SPIRIT DOES NOT MIND.",0);
  else pro_say_lines(72,"THE SONG SPIRIT CIRCLES YOUR HEAD, HUMMING YOUR OFF-KEY VERSION.",0,0);
 }else if(id==NPC_A2_SPIRIT_ROOT){
  if(!a2_has(A2F_SPIRIT2))pro_say_lines(73,"A KNOT OF ROOTS WITH TWO BRIGHT EYES. IT PRESSES SOMETHING INTO YOUR HAND: A HEALER'S DRAUGHT.",0,0);
  else pro_say_lines(74,"THE ROOT SPIRIT IS ASLEEP, MOSTLY. ONE EYE OPENS WHEN COSMOS DRIFTS CLOSE.",0,0);
 }else if(id==NPC_A2_SPIRIT_LIGHT){
  if(!a2_has(A2F_SPIRIT3))pro_say_lines(75,"A SPIRIT MADE OF LATE SUN. IT TOUCHES COSMOS, AND COSMOS GLOWS A LITTLE WARMER.",0,0);
  else pro_say_lines(76,"THE LIGHT SPIRIT FLICKERS. THE CLEARING GETS BRIGHTER WHEN YOU ARE IN IT.",0,0);
 }}
static void a2_check_harmony(void){
 if(a2_has(A2F_SPIRITS)&&!a2_has(A2F_HARMONY))say("ALL THREE SPIRITS GATHER AT THE OLD STONE IN THE MIDDLE OF THE CLEARING.");}
static void act2_script_done(int id){
 if(id==60){A2_CARDS(A2_LYSARA,43);}
 else if(id==66){A2_CARDS(A2_KAELEN_MEET,50);}
 else if(id==71){a2_flags|=A2F_SPIRIT1;inv[ITEM_ETHER]=(u8)mini(99,inv[ITEM_ETHER]+1);say("THE SONG SPIRIT GAVE YOU AN ETHER.");a2_check_harmony();}
 else if(id==73){a2_flags|=A2F_SPIRIT2;inv[ITEM_POTION]=(u8)mini(99,inv[ITEM_POTION]+2);say("THE ROOT SPIRIT GAVE YOU TWO POTIONS.");a2_check_harmony();}
 else if(id==75){a2_flags|=A2F_SPIRIT3;cosmos.trust=(u8)mini(255,cosmos.trust+8);say("COSMOS FEELS WARMER. TRUST +8.");a2_check_harmony();}}
/* ---------- interaction ---------- */
static int a2_door(u8 t){
 if(t==TR_A2_TO_BRINDLE){a2_go(2,50,14);say("BACK IN BRINDLEMARK. THE RUNE HUMS BEHIND YOU.");return 1;}
 if(t==TR_A2_CITY_GATE){if(!a2_has(A2F_GATE)){say(a2_has(A2F_ECHO1)||a2_has(A2F_ECHO2)||a2_has(A2F_ECHO3)?"THE GATE STIRS. NOT ALL THE ECHOES HAVE SPOKEN.":"THE CITY GATE IS SEALED. THREE ECHO STONES SLEEP IN THE WATER.");return 1;}
  {int first=!a2_has(A2F_LYSARA)&&cq_state[10]==CQ_ACTIVE&&!(story_flags&ST_CITY);a2_go(A2_CITY,32,54);if(first)A2_CARDS(A2_CITY_ARRIVE,42);else say("THE FORGOTTEN CITY.");}return 1;}
 if(t==TR_A2_TO_TIDE){a2_go(A2_TIDE,58,32);say("TIDE MEMORY. WATCH THE WATER.");return 1;}
 if(t==TR_A2_TO_WHISPERS){if(!a2_done(10)){say("THE WEST DOOR IS SEALED. THE SENTINEL HOLDS ITS KEY.");return 1;}
  a2_go(A2_WHISPERS,54,32);say(a2_done(11)?"THE HALL OF WHISPERS. QUIET NOW.":"MIRRORS WHISPER YOUR NAME. THE LAST ONE IS AT THE WEST END.");return 1;}
 if(t==TR_A2_TO_LIGHT){if(!a2_done(11)){say("THE EAST DOOR IS DARK. COURAGE FIRST: THE HALL OF WHISPERS.");return 1;}
  a2_go(A2_LIGHT,10,30);say(a2_done(12)?"THE CHAMBER OF ILLUMINATION.":"FIVE PANELS. THEIR HISTORY IS TRUE, BUT IT IS OUT OF ORDER.");return 1;}
 if(t==TR_A2_TO_ARENA){if(!(a2_done(11)&&a2_done(12))){say("THE ARENA GATE WAITS FOR COURAGE AND WISDOM.");return 1;}
  {int first=!a2_done(13);a2_go(A2_ARENA,32,50);if(first)A2_CARDS(A2_ARENA_MEET,0);else say("THE ARENA OF SOULS. THE SEATS ARE LIT.");}return 1;}
 if(t==TR_A2_TO_SANCTUM){if(!a2_done(13)){say("THE SANCTUM DOOR IS STILL. THE THREE TRIALS COME FIRST.");return 1;}
  if(!a2_has(A2F_KAELEN)&&!a2_done(14)){say("THE DOOR IS STILL. THE TIME WEAVER IN THE PLAZA HOLDS ITS THREAD.");return 1;}
  a2_go(A2_SANCTUM,32,52);say(a2_done(14)?"THE CHRONOHEART BEATS.":"THE CHRONOHEART SANCTUM. KAELEN IS ALREADY HERE.");return 1;}
 if(t==TR_A2_TO_HARMONY){a2_go(A2_HARMONY,32,52);say(a2_has(A2F_HARMONY)?"THE HARMONY CLEARING.":"A CLEARING GONE QUIET. THREE SMALL LIGHTS HIDE IN THE GRASS.");return 1;}
 if(t==TR_A2_TO_OLDQ){if(!a2_done(14)){say("THE OLD QUARTER LANE IS TORN. TIME FOLDS BACK ON ITSELF THERE.");return 1;}
  a2_go(5,54,31);say("THE OLD QUARTER. THE DREAM GATE CRYSTAL IS NORTH-EAST.");return 1;}
 if(t==TR_A2_TO_CITY){int from=current_room;
  a2_go(A2_CITY,from==A2_WHISPERS?10:from==A2_LIGHT?53:from==A2_ARENA?48:from==A2_SANCTUM?32:from==A2_HARMONY?16:10,
   (from==A2_WHISPERS||from==A2_LIGHT)?32:(from==5)?54:11);say("THE FORGOTTEN CITY.");return 1;}
 return 0;}
static int act2_interact(u8 t){
 if(current_world!=0||game_mode!=MODE_SURFACE)return 0;
 if(current_room==2&&t==TR_GATE&&near_trigger_x==52&&near_trigger_y==12&&(story_flags&ST_HEART)&&cq_state[9]==CQ_DONE){
  int first=!a2_has(A2F_GATE)&&cq_state[10]==CQ_ACTIVE&&!(a2_flags&A2F_ECHOES);a2_go(A2_TIDE,5,32);
  if(first)A2_CARDS(A2_TIDE_ARRIVE,40);else say("TIDE MEMORY.");return 1;}
 if(a2_door(t))return 1;
 if(t==TR_A2_ECHO){int i,k=-1;for(i=0;i<3;i++)if(near_trigger_x==A2_ECHO_X[i]&&near_trigger_y==A2_ECHO_Y[i])k=i;
  if(k<0)return 1;
  if(a2_flags&(1u<<k)){say(k==0?"THE STONE STILL SAYS: HOME.":k==1?"THE STONE STILL SAYS: FORGE.":"THE STONE STILL SAYS: TOGETHER.");return 1;}
  a2_flags|=(u16)(1u<<k);map_put(A2_ECHO_X[k],A2_ECHO_Y[k],T_STAR,3,C_WALL,TR_A2_ECHO);lc_sfx(SFX_CONFIRM);add_xp(4);save_game();
  if(a2_has(A2F_ECHOES)&&!a2_has(A2F_GATE)){map_put(62,32,T_DOOR,2,C_FREE,TR_A2_CITY_GATE);A2_CARDS(A2_ECHOES,41);return 1;}
  say(k==0?"WATER SHAPES A WORD YOU SAID ONCE, LEAVING: HOME. AN ECHO RINGS.":k==1?"WAVES WRITE ON THE ISLET STONE: FORGE. AN ECHO RINGS.":
   "THE FOAM SPELLS ONE WORD BEFORE IT SINKS: TOGETHER. AN ECHO RINGS.");return 1;}
 if(t==TR_A2_MURAL){say("A MURAL OF TEN ROBED KEEPERS AROUND EIGHT STARS. ONE KEEPER HAS BEEN CHISELLED OUT.");return 1;}
 if(t==TR_A2_WHISPER){say(near_trigger_x==30?"A WHISPER: WHAT IF YOU ARE TOO SLOW, AND THE FORGE GOES COLD?":"A WHISPER: WHAT IF THEY ONLY FOLLOW YOU BECAUSE THEY HAVE TO?");return 1;}
 if(t==TR_A2_MIRROR){
  if(a2_done(11)){say("THE MIRROR SHOWS A SMITH AND HIS COMPANION. NOTHING MORE.");return 1;}
  if(cq_state[11]!=CQ_ACTIVE){say("THE MIRROR WAITS. THE SENTINEL HAS NOT OPENED THIS TRIAL.");return 1;}
  A2_CARDS(A2_MIRROR_MEET,44);return 1;}
 if(t==TR_A2_PANEL){int slot=(near_trigger_x-16)>>3;
  if(slot<0||slot>4)return 1;
  if(a2_done(12)){say(A2_PANEL_NAME[slot]);return 1;}
  if(cq_state[12]!=CQ_ACTIVE){say("THE PANELS ARE DARK. THE SENTINEL HAS NOT OPENED THIS TRIAL.");return 1;}
  if(a2_pick==255){a2_pick=(u8)slot;a2_paint_panels();lc_sfx(SFX_MOVE);say(A2_PANEL_NAME[a2_order[slot]]);return 1;}
  if(a2_pick==slot){a2_pick=255;a2_paint_panels();say("YOU SET THE PANEL BACK.");return 1;}
  {u8 tmp=a2_order[slot];int i,ok=0;a2_order[slot]=a2_order[a2_pick];a2_order[a2_pick]=tmp;a2_pick=255;
   for(i=0;i<5;i++)if(a2_order[i]==i)ok++;a2_paint_panels();lc_sfx(ok==5?SFX_LEVELUP:SFX_CONFIRM);save_game();
   if(ok==5){A2_CARDS(A2_WISDOM_DONE,46);return 1;}
   {static char line[40];copystr(line,"PANELS SWAPPED. 0 OF 5 IN PLACE.",40);line[16]=(char)('0'+ok);say(line);}}
  return 1;}
 if(t==TR_A2_LIGHT_NOTE){say("LYSARA'S NOTE: TELL IT AS IT HAPPENED. GATHERING, THEN AXES, THEN THE SEAL, THE SPLIT, THE PARTING.");return 1;}
 if(t==TR_A2_LEVER){
  if(a2_done(13)){say("THE LEVER IS LOCKED HOME.");return 1;}
  if(cq_state[13]!=CQ_ACTIVE){say("THE LEVER IS STUCK FAST. THE SENTINEL HAS NOT OPENED THIS TRIAL.");return 1;}
  if(a2_arena){say("COSMOS IS ALREADY ON THE LEVER. KEEP THE SENTRIES OFF IT.");return 1;}
  a2_arena_begin();return 1;}
 if(t==TR_A2_SPARE){int i;for(i=0;i<3;i++)if((a2_kneel&(1u<<i))&&enemies[i].active&&(enemies[i].x>>3)==near_trigger_x&&(enemies[i].y>>3)==near_trigger_y){
   trigger[mi(near_trigger_x,near_trigger_y)]=TR_NONE;a2_kneel&=(u8)~(1u<<i);enemies[i].active=0;a2_arena_result|=(u8)(1u<<i);
   cosmos.trust=(u8)mini(255,cosmos.trust+3);lc_sfx(SFX_BEFRIEND);say("YOU OFFER A HAND. THE SENTRY BOWS AND STEPS BACK TO ITS GATE.");save_game();return 1;}
  trigger[mi(near_trigger_x,near_trigger_y)]=TR_NONE;return 1;}
 if(t==TR_A2_CHRONOHEART){
  if(a2_done(14)){say("THE CHRONOHEART BEATS, STEADY AS A FORGE BELLOWS.");return 1;}
  if(cq_state[14]!=CQ_ACTIVE)return 1;
  A2_CARDS(A2_CHRONO_MEET,51);return 1;}
 if(t==TR_A2_HARMONY_STONE){
  if(a2_has(A2F_HARMONY)){player.hp=max_hp;player_mp=max_mp;save_game();say("THE HARMONY STONE SINGS. HP AND MP RESTORED. THE GAME IS SAVED.");return 1;}
  if(!a2_has(A2F_SPIRITS)){int n=a2_has(A2F_SPIRIT1)+a2_has(A2F_SPIRIT2)+a2_has(A2F_SPIRIT3);
   say(n==0?"AN OLD STONE, COLD. THREE SPIRITS HIDE IN THE CLEARING. FIND THEM.":n==1?"THE STONE WARMS A LITTLE. TWO SPIRITS ARE STILL HIDING.":"THE STONE IS ALMOST WARM. ONE SPIRIT IS STILL HIDING.");return 1;}
  a2_flags|=A2F_HARMONY;max_mp=(u8)mini(99,max_mp+2);player_mp=max_mp;player.hp=max_hp;map_put(32,28,T_STAR,3,C_WALL,TR_A2_HARMONY_STONE);
  lc_sfx(SFX_LEVELUP);add_xp(20);save_game();A2_CARDS(A2_HARMONY_DONE,54);return 1;}
 return 0;}
/* ---------- Arena of Souls: Cosmos holds the lever, sentries go for it ---------- */
static const u8 A2_GATE_X[3]={15,49,32},A2_GATE_Y[3]={31,31,18};
static s16 a2_beast_x(void){return (s16)(A2_LEVER_TX*8+4);}
static s16 a2_beast_y(void){return (s16)((A2_LEVER_TY+2)*8);}
static void a2_arena_begin(void){int i;
 a2_arena=1;a2_channel=0;a2_kneel=0;a2_jam=0;a2_arena_result=0;
 for(i=0;i<3;i++){spawn_enemy(i,A2_GATE_X[i],A2_GATE_Y[i],EN_CROWN,0);enemies[i].maxhp=(u8)(3+player_level/4);enemies[i].hp=enemies[i].maxhp;
  enemies[i].recover=(u8)(40+i*150);a2_kneel_t[i]=0;}
 trigger[mi(A2_LEVER_TX,A2_LEVER_TY)]=TR_NONE;
 lc_sfx(SFX_CONFIRM);say("COSMOS TAKES THE LEVER. THREE SENTRY GATES GRIND OPEN.");}
static int act2_beast_busy(void){return a2_arena==1&&current_world==0&&current_room==A2_ARENA&&game_mode==MODE_SURFACE;}
static int act2_no_duel(void){return act2_beast_busy();}
static void a2_unkneel(int i){int tx=enemies[i].x>>3,ty=enemies[i].y>>3;
 if((unsigned)tx<64u&&(unsigned)ty<64u&&trigger[mi(tx,ty)]==TR_A2_SPARE)trigger[mi(tx,ty)]=TR_NONE;a2_kneel&=(u8)~(1u<<i);}
/* Arin's blows drop a sentry to its knees instead of breaking it. A kneeling
   sentry is spared with A beside it; striking it again shatters it. */
static int act2_sentry_hit(Enemy*e,int dmg){int i=(int)(e-enemies);
 if(!(current_world==0&&current_room==A2_ARENA&&a2_arena==1)||i<0||i>2)return 0;
 if(!e->active||e->hurt)return 1;
 if(a2_kneel&(1u<<i)){a2_unkneel(i);e->active=0;a2_arena_result|=(u8)(8u<<i);lc_sfx(SFX_CRIT);say("THE KNEELING SENTRY SHATTERS. THE SEATS GO QUIET.");save_game();return 1;}
 if(dmg<1)dmg=1;e->hp=(u8)(dmg>=e->hp?0:e->hp-dmg);e->hurt=12;lc_sfx(SFX_HIT);
 if(!e->hp){int tx=e->x>>3,ty=e->y>>3;a2_kneel|=(u8)(1u<<i);a2_kneel_t[i]=240;
  if((unsigned)tx<64u&&(unsigned)ty<64u&&trigger[mi(tx,ty)]==TR_NONE)trigger[mi(tx,ty)]=TR_A2_SPARE;
  say("THE SENTRY DROPS TO ONE KNEE. A BESIDE IT TO SPARE IT. STRIKE TO SHATTER.");}
 return 1;}
static void a2_arena_tick(void){int i,jam=0;s16 bx=a2_beast_x(),by=a2_beast_y();
 /* The companion walks to the lever and holds it. */
 if(cosmos.x<bx)cosmos.x++;else if(cosmos.x>bx)cosmos.x--;
 if(cosmos.y<by)cosmos.y++;else if(cosmos.y>by)cosmos.y--;
 for(i=0;i<3;i++){Enemy*e=&enemies[i];int dx,dy;
  if(!e->active)continue;
  if(e->hurt)e->hurt--;
  if(a2_kneel&(1u<<i)){if(a2_kneel_t[i])a2_kneel_t[i]--;else{a2_unkneel(i);e->hp=e->maxhp;say("A SENTRY RISES AGAIN.");}continue;}
  if(e->recover){e->recover--;continue;}
  dx=bx-e->x;dy=by-e->y;
  if(iabs(dx)+iabs(dy)<=14){jam=1;continue;}
  if(frame&1){if(iabs(dx)>iabs(dy))e->x+=(s16)(dx>0?1:-1);else e->y+=(s16)(dy>0?1:-1);}}
 a2_jam=(u8)jam;
 if(jam){if(a2_channel>=3)a2_channel-=3;else a2_channel=0;if((frame&63)==0)lc_sfx(SFX_HIT);}
 else if(a2_channel<A2_CHANNEL_MAX)a2_channel++;
 if(a2_channel>=A2_CHANNEL_MAX){
  for(i=0;i<3;i++)if(enemies[i].active){a2_unkneel(i);enemies[i].active=0;}
  a2_arena=2;map_put(A2_LEVER_TX,A2_LEVER_TY,T_STAR,3,C_WALL,TR_NONE);lc_sfx(SFX_LEVELUP);save_game();A2_CARDS(A2_UNITY_DONE,48);}}
/* ---------- Hall of Whispers: the mirror copies your last move ---------- */
static const char*const A2_MOVE[3]={"STRIKE","GUARD","FEINT"};
/* STRIKE beats FEINT, GUARD beats STRIKE, FEINT beats GUARD. */
static int a2_beats(int a,int b){return (a==0&&b==2)||(a==1&&b==0)||(a==2&&b==1);}
static void a2_duel_commit(void){int me=a2_sel,mirror=a2_last;
 a2_mirror=(u8)mirror;a2_last=(u8)me;a2_phase=1;a2_timer=45;
 if(a2_beats(me,mirror)){a2_wins++;a2_rounds=(u8)mini(255,a2_rounds+1);a2_result=1;lc_sfx(SFX_CRIT);
  a2_notice=a2_wins>=A2_MIRROR_WINS?"THE MIRROR STAGGERS. IT HAS NO ANSWER LEFT.":"YOUR REFLECTION WAS ONE MOVE BEHIND YOU.";}
 else if(me==mirror){a2_result=0;lc_sfx(SFX_MOVE);a2_notice="THE SAME MOVE, MET HEAD ON. NOTHING GIVES.";}
 else{a2_result=2;lc_sfx(SFX_HIT);if(a2_hp>2)a2_hp-=2;else a2_hp=0;a2_notice="THE MIRROR READ YOU. IT HITS WHERE YOU WERE GOING.";}}
static int a2_duel_update(u16 newk){
 if(a2_phase==1){if(a2_timer)a2_timer--;else{
   if(a2_wins>=A2_MIRROR_WINS){pro_ui=0;save_game();A2_CARDS(A2_COURAGE_DONE,45);return 1;}
   if(!a2_hp){a2_wins=0;a2_hp=A2_DUEL_HP;a2_last=1;a2_notice="ARIN FALLS. THE MIRROR WAITS. TRY AGAIN, FROM THE START.";}
   a2_phase=0;}
  return 1;}
 if(newk&KEY_B){pro_ui=0;a2_wins=0;say("YOU STEP BACK FROM THE MIRROR. IT WILL WAIT.");return 1;}
 if(newk&KEY_LEFT){a2_sel=(u8)(a2_sel?a2_sel-1:2);lc_sfx(SFX_MOVE);}
 if(newk&KEY_RIGHT){a2_sel=(u8)(a2_sel<2?a2_sel+1:0);lc_sfx(SFX_MOVE);}
 if(newk&KEY_A)a2_duel_commit();
 return 1;}
static void a2_duel_draw(void){int i;
 ui_frame(0,19,15);ui_text(2,2,"HALL OF WHISPERS // COURAGE",14);
 ui_text(2,4,"ARIN",14);ui_text(9,4,"HP",13);ui_num(12,4,a2_hp,15);
 ui_text(17,4,"WINS",13);ui_num(22,4,a2_wins,15);ui_text(23,4,"/3",15);
 ui_text(2,10,"MIRROR WILL PLAY",13);ui_text(19,10,A2_MOVE[a2_last%3],14);
 for(i=0;i<3;i++){ui_text(3+i*9,12,(a2_phase==0&&a2_sel==i)?">":" ",13);ui_text(4+i*9,12,A2_MOVE[i],a2_phase==0?15:8);}
 if(a2_phase==1){ui_text(2,14,"YOU",13);ui_text(6,14,A2_MOVE[a2_last%3],15);ui_text(14,14,"MIRROR",13);ui_text(21,14,A2_MOVE[a2_mirror%3],15);}
 else ui_text(2,14,"GUARD>STRIKE>FEINT>GUARD",8);
 ui_wrap_text(15,a2_notice,14,2);
 ui_text(2,18,"LEFT RIGHT  A COMMIT  B LEAVE",14);
 oam_hide_all();oam_set32(0,40,40,272,0);oam_ui_portrait(0);
 OAM16[2*4]=(u16)(40&255);OAM16[2*4+1]=(u16)((168&511)|(2u<<14)|0x1000);OAM16[2*4+2]=(u16)(272|(1u<<10)|(0<<12));oam_ui_portrait(2);}
/* ---------- the Chronoheart: three rings of torn memory ---------- */
#define A2_RING_LEN 24
static int a2_ring_in_window(int p){return p>=10&&p<=13;}
static int a2_ring_update(u16 newk){int r=a2_ring_lock;
 if(a2_flash)a2_flash--;
 if(r>=3)return 1;
 if(a2_slow)a2_slow--;
 a2_ring_tick++;
 {static const u8 period[3]={4,3,2};int per=period[r]*(a2_slow?3:1);
  if(a2_ring_tick>=per){a2_ring_tick=0;a2_ring[r]=(u8)(a2_ring[r]+1>=A2_RING_LEN?0:a2_ring[r]+1);}}
 if((newk&KEY_L)&&!a2_slow){if(a2_slow_uses<3){a2_slow_uses++;a2_slow=150;lc_sfx(SFX_POTION);a2_notice="KAELEN PULLS THE THREADS TAUT. THE RING SLOWS.";}
  else a2_notice="KAELEN: THAT'S ALL THE TIME I HAVE TODAY. YOU CAN DO IT.";}
 if(newk&KEY_B){pro_ui=0;say("YOU STEP BACK. THE RINGS KEEP TURNING. KAELEN WAITS.");return 1;}
 if(newk&KEY_A){
  if(a2_ring_in_window(a2_ring[r])){a2_ring_lock++;a2_ring_tick=0;a2_flash=20;lc_sfx(SFX_CRIT);
   a2_notice=a2_ring_lock==1?"THE OUTER RING LOCKS. A MEMORY STEADIES.":a2_ring_lock==2?"THE MIDDLE RING LOCKS. THE CORE FLICKERS.":"THE INNER RING LOCKS.";
   if(a2_ring_lock>=3){pro_ui=0;save_game();A2_CARDS(A2_CHRONO_DONE,52);}}
  else{a2_slips=(u8)mini(255,a2_slips+1);a2_ring[r]=(u8)(a2_ring[r]+7>=A2_RING_LEN?a2_ring[r]+7-A2_RING_LEN:a2_ring[r]+7);lc_sfx(SFX_HIT);
   a2_notice="THE MEMORY SLIPS. WAIT FOR THE NOTCH TO CROSS THE MARK.";}}
 return 1;}
static void a2_ring_draw(void){int r,i;
 ui_frame(8,19,15);ui_text(2,9,"THE CHRONOHEART",14);ui_text(19,9,"SLOW",13);ui_num(24,9,3-a2_slow_uses,15);
 for(r=0;r<3;r++){int y=11+r;ui_text(2,y,r==0?"R1":r==1?"R2":"R3",r<a2_ring_lock?13:(r==a2_ring_lock?14:8));
  for(i=0;i<A2_RING_LEN;i++){const char*c=(i==a2_ring[r])?"*":a2_ring_in_window(i)?"+":"-";
   ui_text(5+i,y,r<a2_ring_lock?(a2_ring_in_window(i)?"=":"-"):c,(i==a2_ring[r]&&r>=a2_ring_lock)?14:a2_ring_in_window(i)?13:8);}}
 ui_wrap_text(15,a2_notice,a2_flash?13:15,2);
 ui_text(2,18,a2_slow?"A LOCK  B LEAVE  SLOWED":"A LOCK  L SLOW  B LEAVE",14);}
static int act2_update(u16 newk){
 if(pro_ui==10)return a2_duel_update(newk);
 if(pro_ui==11)return a2_ring_update(newk);
 return 0;}
static int act2_draw(void){
 if(pro_ui==10){a2_duel_draw();return 1;}
 if(pro_ui==11){a2_ring_draw();return 1;}
 return 0;}
/* ---------- HUD ---------- */
static const char*act2_objective(int q){
 if(q==10){if(!(a2_flags&A2F_ECHOES))return current_world==0&&A2_IS_ROOM?"Q10 ECHOES AT LOW TIDE":"Q10 TIDE MEMORY: NE RUNE";
  if(!a2_has(A2F_ECHOES)){static char l[30];int n=a2_has(A2F_ECHO1)+a2_has(A2F_ECHO2)+a2_has(A2F_ECHO3);copystr(l,"Q10 ECHO STONES 0/3",30);l[16]=(char)('0'+n);return l;}
  return "Q10 MEET THE CITY SENTINEL";}
 if(q==11)return "Q11 HALL OF WHISPERS: WEST";
 if(q==12)return "Q12 ILLUMINATION: EAST DOOR";
 if(q==13)return "Q13 ARENA OF SOULS: NE";
 if(q==14)return a2_has(A2F_KAELEN)?"Q14 SET THE CHRONOHEART":"Q14 KAELEN IN THE PLAZA";
 return 0;}
static const char*act2_hud_line(void){static char l[30];int q;
 if(current_world!=0||game_mode!=MODE_SURFACE||!A2_IS_ROOM)return 0;
 if(current_room==A2_ARENA&&a2_arena==1){int pct=(a2_channel*100)/A2_CHANNEL_MAX;
  copystr(l,a2_jam?"LEVER JAMMED!  000%":"LEVER CHANNEL  000%",30);l[15]=(char)('0'+pct/100);l[16]=(char)('0'+(pct/10)%10);l[17]=(char)('0'+pct%10);return l;}
 if(current_room==A2_TIDE&&!(a2_flags&A2F_GATE)){copystr(l,a2_high?"HIGH WATER  BARS FLOODED":"LOW WATER   BARS OPEN",30);return l;}
 if(current_room==A2_LIGHT&&cq_state[12]==CQ_ACTIVE){int i,ok=0;for(i=0;i<5;i++)if(a2_order[i]==i)ok++;
  copystr(l,a2_pick!=255?"PICK A PANEL TO SWAP  0/5":"PANELS IN PLACE  0/5",30);l[a2_pick!=255?22:17]=(char)('0'+ok);return l;}
 if(current_room==A2_HARMONY&&!a2_has(A2F_HARMONY)){copystr(l,"SPIRITS FOUND 0/3",30);l[14]=(char)('0'+a2_has(A2F_SPIRIT1)+a2_has(A2F_SPIRIT2)+a2_has(A2F_SPIRIT3));return l;}
 for(q=10;q<=14;q++)if(cq_state[q]==CQ_ACTIVE)return act2_objective(q);
 return 0;}
/* ---------- per-frame: tide, arena ---------- */
static void act2_frame(void){
 if(current_world!=0||game_mode!=MODE_SURFACE)return;
 if(current_room==A2_TIDE){int high;
  if(++a2_tide>=A2_TIDE_CYCLE)a2_tide=0;
  high=a2_tide>=A2_TIDE_LOW;
  if(high!=a2_high){int tx=player.x>>3,ty=player.y>>3;a2_high=(u8)high;a2_paint_bars();
   if(high&&ty>=30&&ty<=34&&((tx>=19&&tx<=29)||(tx>=35&&tx<=45))){
    /* Never leave Arin in the sea: the tide lifts him to the nearest dry ground. */
    if(tx<=24){player.x=(s16)(17*8);}else if(tx<=40){player.x=(s16)(32*8);}else player.x=(s16)(47*8);
    player.y=(s16)(32*8);refresh_camera();say("THE TIDE RISES. YOU SCRAMBLE BACK TO DRY GROUND.");}
   else if(high)say("HIGH WATER. THE SAND BARS ARE GONE FOR NOW.");
   else say("LOW WATER. THE SAND BARS ARE BACK.");}}
 else if(current_room==A2_ARENA&&a2_arena==1)a2_arena_tick();}
static void act2_sprites(void){}
#ifdef QA_AUTORUN
static void qa_a2_flush(void){int n=0;while(pro_ui==4&&n++<24)prologue_update(KEY_A);}
#endif
#endif
