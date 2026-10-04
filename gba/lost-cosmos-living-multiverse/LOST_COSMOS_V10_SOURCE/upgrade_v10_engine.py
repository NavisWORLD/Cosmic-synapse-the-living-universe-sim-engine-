from pathlib import Path
p=Path(__file__).with_name('lost_cosmos_v5.c')
s=p.read_text()
def repl(a,b,label):
 global s
 n=s.count(a)
 assert n==1,(label,n)
 s=s.replace(a,b)
# Render fix: in GBA OBJ wins over BG at equal priority. Use OBJ priority 1, UI BG1 priority 0.
assert s.count('OAM16[i*4+2]=(u16)(tile|(pal<<12));')==2
s=s.replace('OAM16[i*4+2]=(u16)(tile|(pal<<12));','OAM16[i*4+2]=(u16)(tile|(1u<<10)|(pal<<12));')
repl('OAM16[i*4+2]=(u16)(tile|(pal<<12)); }','OAM16[i*4+2]=(u16)(tile|(1u<<10)|(pal<<12)); }','16x16 OAM depth') if False else None
# Prior replacement has patched BOTH oam setters (same substring repeated); check it did not silently alter only one.
assert s.count('OAM16[i*4+2]=(u16)(tile|(1u<<10)|(pal<<12));')==2
repl('static u8 cinema_active=0,cinema_scene=0;','''static u8 cinema_active=0,cinema_scene=0;
/* V10 presentation state is transient; V2-V9 gameplay state/save layout is kept. */
static u8 v10_title_sel=0,v10_title_sub=0,v10_has_save=0,v10_opening=0;
static u8 v10_opening_step=0,v10_tutorial=0,v10_ending_card=0;
/* The original twelve cinematic scene IDs remain stable. New scenes are appended. */
typedef struct {u8 art;const char*head;const char*text;} OpeningCard;
static const OpeningCard V10_OPENING[]={
 {7,"BEFORE THE FRACTURE","EIGHT REALMS SHARED THE COSMIC LATTICE. EACH KEPT ITS OWN SKY."},
 {7,"THE FIRST GUARDIANS","THE GUARDIANS BUILT A HEART TO HOLD DISTANCE AND MEMORY."},
 {6,"THE HIDDEN PRISON","NIHILOS WAS SEALED BEHIND THE LATTICE. SOME DOORS STAY SHUT."},
 {10,"MALAKARS GAMBLE","HE PROMISED RULERS AN ESCAPE. EACH STOLEN SHARD TORE A NEW WOUND."},
 {2,"BRINDLEMARK / ERIDORIA","THE RIVER ROSE. MOUNTAINS FLATTENED AGAINST AN EMPTY SKY."},
 {12,"THE FORGE","ARIN FOUND A SINGING CRYSTAL WHERE NO CRYSTAL SHOULD BE."},
 {0,"COSMOS AWAKENS","I REMEMBER A SKY MADE OF SQUARES. I DONT REMEMBER WHO BROKE IT."},
 {13,"ASH IN THE FORGE","MALAKARS RAIDERS ARRIVED. THE VILLAGE HAD NO TIME TO PREPARE."},
 {12,"ARINS FIRST CHOICE","A BROKEN WORLD CANNOT BE REPAIRED BY FORCE ALONE."},
 {2,"THE JOURNEY BEGINS","FIND THE ELDER. SEEK ASTRID. RECOVER THE HEART WITHOUT LOSING YOURS."}
};
#define V10_OPENING_COUNT ((int)(sizeof(V10_OPENING)/sizeof(V10_OPENING[0])))
''','V10 globals')
# Fix source canonical line with GBA limited font: no apostrophe in last B/W? punctuation font supports apostrophe, change exactly
s=s.replace('"I REMEMBER A SKY MADE OF SQUARES. I DONT REMEMBER WHO BROKE IT."', '"I REMEMBER A SKY MADE OF SQUARES. I DON\'T REMEMBER WHO BROKE IT."')
repl('cinema_active=0;cinema_timer=0;','cinema_active=0;cinema_timer=0;v10_ending_card=0;','cinema end flags')
# Guard the title handling: draw custom opening cards, rather than old generic footer.
repl('''static void draw_cinema_caption(void){
 static const char*HEAD[12]''','''static void ui_wrap_text(int row,const char*s,int pal,int maxrows);
static void draw_cinema_caption(void){
 if(v10_opening){const OpeningCard*card=&V10_OPENING[v10_opening_step];
  ui_clear();ui_fill_rows(0,1,63,15);ui_fill_rows(14,19,63,15);
  ui_text(1,0,"LOST COSMOS / PROLOGUE",14);ui_text(2,14,card->head,13);
  ui_wrap_text(15,card->text,15,3);
  ui_text(1,19,"A NEXT   START SKIP",14);ui_num(26,19,v10_opening_step+1,13);
  return;
 }
 if(v10_ending_card){
  ui_clear();ui_fill_rows(0,1,63,15);ui_fill_rows(15,19,63,15);
  ui_text(2,0,"LOST COSMOS / EPILOGUE",14);
  if(ending==1){ui_text(2,15,"OPEN / THE REALMS RETURN",14);ui_wrap_text(16,"THE PATHS REJOIN. NO HEART CAN OWN THE UNKNOWN.",15,3);}
  else if(ending==2){ui_text(2,15,"PRESERVE / STAND TOGETHER",14);ui_wrap_text(16,"YOU HOLD THE LATTICE. THE PEOPLE CHOOSE WHEN TO OPEN IT.",15,3);}
  else{ui_text(2,15,"WANDER / THE NEXT SKY",14);ui_wrap_text(16,"YOU AND COSMOS DEPART. THE MAP IS NOT FINISHED.",15,3);}
  ui_text(2,19,"A CONTINUE",13);return;
 }
 static const char*HEAD[12]''','cinematic captions')
# UI priority and dedicated dialog portrait: world objects always behind BG1 when BG1 tile nontransparent.
repl('if(npc_dialogue_active){oam_set(40,8,110,92+NPCS[npc_dialogue_id].kind*8,12+NPCS[npc_dialogue_id].kind,0);}else OAM16[40*4]=0x0200;', '''if(npc_dialogue_active){
  /* Portrait appears ABOVE the panel: world actors cannot obscure framed text.
     It stays priority 1, so even the portrait cannot draw across opaque UI. */
  oam_set(40,8,69,92+NPCS[npc_dialogue_id].kind*8,12+NPCS[npc_dialogue_id].kind,0);
 }else OAM16[40*4]=0x0200;''','dialogue portrait')
# Special menu/encounter portraits must remain visible ABOVE UI via explicit OAM priority 0,
# restricted to reserved spaces that don't intersect actual text. Existing OAM global 1 would hide them.
repl('''static void oam_hide_all(void){int i;for(i=0;i<128;i++){OAM16[i*4]=0x0200;OAM16[i*4+1]=0;OAM16[i*4+2]=0;OAM16[i*4+3]=0;}}''','''static void oam_hide_all(void){int i;for(i=0;i<128;i++){OAM16[i*4]=0x0200;OAM16[i*4+1]=0;OAM16[i*4+2]=0;OAM16[i*4+3]=0;}}
/* Full-screen menu portraits occupy intentionally blank slots. All field sprites
   stay behind the text plane. Do not use this helper for overworld entities. */
static void oam_ui_portrait(int i){OAM16[i*4+2]=(u16)(OAM16[i*4+2]&~(3u<<10));}''','UI sprite helper')
# tactical portraits and shop overlay: move hero portrait from (43,69) to (40,60) no intersect text x3 y? Battle art hero at x43..74 y60..91; UI text at y10=80 x2 ARIN = x16..40, hero x43..75 safe; enemy x169..201 y54..85 not text; yes.
repl('oam_hide_all();oam_set32(0,43,69,272,0);','oam_hide_all();oam_set32(0,43,59,272,0);oam_ui_portrait(0);','battle hero art')
repl('oam_set(1,77,85,32+(cosmos.mood&3)*4,1+(cosmos.mood&3),0);','oam_set(1,77,70,32+(cosmos.mood&3)*4,1+(cosmos.mood&3),0);oam_ui_portrait(1);','battle companion art')
repl('''if(e->active)oam_set32(2,169,54,(current_world==0&&current_room==4&&e->elite)?256:160+e->type*16,5+e->type);''','''if(e->active){oam_set32(2,169,54,(current_world==0&&current_room==4&&e->elite)?256:160+e->type*16,5+e->type);oam_ui_portrait(2);}''','battle foe art')
repl('oam_hide_all();oam_set(0,190,28,116,15,0);','oam_hide_all();oam_set(0,190,28,116,15,0);oam_ui_portrait(0);','shop portrait')
repl('ui_text(2,17,"B BACK",13);oam_set32(1,184,45,272,0);','ui_text(2,17,"B BACK",13);oam_set32(1,184,45,272,0);oam_ui_portrait(1);','menu class portrait')
# Title menu screen: bottom opaque matte + options + guarded new-game overwrite + controls.
repl('''static void draw_intro(void){if(cinema_active)draw_cinema_caption();else{ui_clear();ui_frame(2,17,15);ui_text(4,6,"ERIDORIA // LOST COSMOS",15);ui_text(4,15,"PRESS START TO WAKE",13);}}''','''static void draw_intro(void){
 static const char*options[4]={"NEW GAME","CONTINUE","OPTIONS","CREDITS"};int i;
 ui_clear();ui_fill_rows(0,1,63,15);ui_text(2,0,"LOST COSMOS / V10",14);
 ui_fill_rows(10,19,63,15);
 ui_text(2,10,"THE LIVING MULTIVERSE",14);
 if(v10_title_sub==1){
  ui_text(2,12,"OVERWRITE THE CURRENT SAVE?",15);
  ui_text(2,14,"A YES / B CANCEL",14);
  ui_text(2,16,"YOUR EXISTING FILE WILL BE",13);
  ui_text(2,17,"REPLACED BY NEW GAME.",13);
 }else if(v10_title_sub==2){
  ui_text(2,12,"AUDIO",14);ui_text(12,12,audio_on?"ON":"OFF",15);
  ui_text(2,14,"A TOGGLE / B BACK",13);
  ui_text(2,16,"MORE OPTIONS: START MENU",14);
 }else if(v10_title_sub==3){
  ui_text(2,12,"CREATED BY CORY DAVIS",14);
  ui_text(2,14,"COSMIC SYNAPSE / COSMOS",15);
  ui_text(2,16,"ERIDORIA / LOST COSMOS",13);
  ui_text(2,18,"B RETURN",14);
 }else{
  for(i=0;i<4;i++){
   ui_text(2,12+i,(v10_title_sel==i)?">":" ",14);
   ui_text(4,12+i,options[i],(!v10_has_save&&i==1)?13:15);
  }
  ui_text(1,18,v10_has_save?"SAVE DETECTED":"START A NEW ADVENTURE",13);
  ui_text(1,19,"UP/DOWN SELECT   A CONFIRM",14);
 }
}''','functional title screen')
# HUD tutorial staged hints. Add before closing draw_hud else
repl('''if(((frame>>8)&1)==0){ui_fill_rows(19,19,62,15);ui_text(1,19,campaign_objective(),14);}}''','''if(((frame>>8)&1)==0){ui_fill_rows(19,19,62,15);
  ui_text(1,19,(v10_tutorial==1)?"FIND THE BRINDLE ELDER":
   (v10_tutorial==2)?"WEST GATE / SEEK ASTRID":
   (v10_tutorial==3)?"ORIGIN / SPEAK TO ASTRID":
   (v10_tutorial==4)?"FIND MIRA / REPAIR BEACON":campaign_objective(),14);}}''','tutorial objective')
# Story progression hints don't ruin older saved current if tutorial==0.
repl('npc_seen|=(1u<<npc_dialogue_id);npc_recent=npc_dialogue_id;save_game();', '''npc_seen|=(1u<<npc_dialogue_id);npc_recent=npc_dialogue_id;
 if(npc_dialogue_id==14&&v10_tutorial==1)v10_tutorial=2;
 if(npc_dialogue_id==13&&v10_tutorial==3)v10_tutorial=4;
 if(npc_dialogue_id==0&&v10_tutorial==4)v10_tutorial=0;
 save_game();''','tutorial NPC gates')
repl('''generate_surface();refresh_camera();say(dst==2?"WELCOME TO BRINDLEMARK."''','''generate_surface();refresh_camera();if(dst==0&&v10_tutorial==2)v10_tutorial=3;say(dst==2?"WELCOME TO BRINDLEMARK."''','tutorial travel state')
# Free distinct cinematic presentations for existing 3 endings (gameplay endings still share postgame map: do not misdescribe).
repl('cinema_start(7,150);','''cinema_start((u8)(c==1?1:(c==2?7:6)),220);v10_ending_card=1;''','distinct ending art')
# V10 save extension deliberately outside 0..226 V2-V9 versioned areas.
repl('SRAM[226]=v9_crc();}','''SRAM[226]=v9_crc();
 SRAM[227]=0xA6;SRAM[228]=v10_tutorial;
 SRAM[229]=(u8)(0x69^SRAM[227]^SRAM[228]^SRAM[211]^SRAM[226]);}''','V10 SRAM extension')
repl('''touch_mode=(!old_v3&&!old_v4&&((SRAM[168]&0xFE)==0xC0))?(SRAM[168]&1):0;''','''v10_tutorial=(!old_v3&&!old_v4&&SRAM[227]==0xA6&&
  SRAM[229]==(u8)(0x69^SRAM[227]^SRAM[228]^SRAM[211]^SRAM[226])&&SRAM[228]<=4)?SRAM[228]:0;
 touch_mode=(!old_v3&&!old_v4&&((SRAM[168]&0xFE)==0xC0))?(SRAM[168]&1):0;''','V10 SRAM loading')
# init new reset including intro flag (QA calls init_new_game repeatedly; preserve intro=0 where tests later reset it).
repl('touch_mode=0;hold_a_frames=0;workload_qi=0;actor_style=0;','touch_mode=0;hold_a_frames=0;workload_qi=0;v10_tutorial=0;v10_ending_card=0;actor_style=0;','new save defaults')
# Full boot and title control: only load a save if user requests CONTINUE. New Game warns before overwrite, custom opening cinematics.
old='''void gba_main(void){u16 k,newk;init_new_game();load_game();init_graphics();sound_init();if(game_mode==MODE_SPACE)generate_space();else generate_surface();
#ifndef QA_AUTORUN
 cinema_start(0,0); /* Title remains until player presses START */
#endif
#ifdef QA_AUTORUN
 /* CI QA executes immediately; no debugger-attach delay is required. */
 gameplay_qa();
#endif
for(;;){k=(u16)(~REG_KEYINPUT)&0x03FF;newk=(u16)(k&~prev_keys);prev_keys=k;if(intro){if(newk&KEY_START){intro=0;cinema_end();say("ARIN, ASTRID CALLED. MALAKAR FRACTURED THE HEART. WE MUST RECLAIM ITS LOST SIGNALS.");}}
else if(cinema_active){if(newk&(KEY_A|KEY_START))cinema_end();else if(cinema_timer&&!--cinema_timer)cinema_end();}
else{if(game_mode!=MODE_PAUSE&&(newk&KEY_START))enter_pause();else if(game_mode==MODE_PAUSE)update_pause(newk);else if(game_mode==MODE_SURFACE)update_surface(k,newk);else if(game_mode==MODE_BATTLE)update_battle(newk);else update_space(k,newk);if((frame&15)==0){state_tick();if(!buddy_quantum)quantum_workload_step();}if((frame&255)==0&&player_mp<max_mp)player_mp++;if(dialogue_timer)dialogue_timer--;}music_step();wait_vblank();frame++;render();}}'''
new='''/* These are actual user-facing transitions, not fabricated quest-flag jumps. */
static void v10_start_opening(void){
 init_new_game();intro=0;v10_opening=1;v10_opening_step=0;v10_title_sub=0;
 cinema_start(V10_OPENING[0].art,0);
}
static void v10_complete_opening(void){
 v10_opening=0;cinema_end();
 /* The player really begins in the Brindlemark area of the original world,
    then may walk to Origin and find Astrid; the original V9 loop remains intact. */
 current_world=0;current_room=2;current_layer=1;game_mode=MODE_SURFACE;
 player.x=20*8;player.y=43*8;cosmos.x=player.x+14;cosmos.y=player.y-10;
 v10_tutorial=1;generate_surface();refresh_camera();
 say("THE RAIDERS HAVE GONE EAST. FIND THE BRINDLE ELDER, THEN SEEK ASTRID.");
 save_game();v10_has_save=1;
}
static void v10_advance_opening(void){
 if((int)v10_opening_step+1>=V10_OPENING_COUNT){v10_complete_opening();return;}
 v10_opening_step++;cinema_start(V10_OPENING[v10_opening_step].art,0);
}
static void v10_continue_game(void){
 if(!v10_has_save)return;
 init_new_game();load_game();intro=0;v10_opening=0;v10_title_sub=0;
 cinema_end();if(game_mode==MODE_SPACE)generate_space();else generate_surface();
 refresh_camera();say("WELCOME BACK. COSMOS KEPT YOUR MEMORY.");
}
static void v10_title_input(u16 newk){
 if(v10_title_sub==1){
  if(newk&KEY_B){v10_title_sub=0;return;}
  if(newk&KEY_A)v10_start_opening();return;
 }
 if(v10_title_sub==2){
  if(newk&KEY_B)v10_title_sub=0;
  else if(newk&KEY_A)audio_on=(u8)!audio_on;
  return;
 }
 if(v10_title_sub==3){if(newk&(KEY_A|KEY_B|KEY_START))v10_title_sub=0;return;}
 if(newk&KEY_UP)v10_title_sel=(u8)((v10_title_sel+3)%4);
 if(newk&KEY_DOWN)v10_title_sel=(u8)((v10_title_sel+1)%4);
 if(newk&(KEY_A|KEY_START)){
  if(v10_title_sel==0){if(v10_has_save)v10_title_sub=1;else v10_start_opening();}
  else if(v10_title_sel==1)v10_continue_game();
  else if(v10_title_sel==2)v10_title_sub=2;
  else v10_title_sub=3;
 }
}
void gba_main(void){u16 k,newk;
 v10_has_save=(u8)(save_valid()||save_valid_v4()||save_valid_v3()||save_valid_v2());
 init_new_game();init_graphics();sound_init();
#ifdef QA_AUTORUN
 load_game();
#endif
 if(game_mode==MODE_SPACE)generate_space();else generate_surface();
#ifndef QA_AUTORUN
 cinema_start(0,0); /* Actual title menu overlays original authored art. */
#endif
#ifdef QA_AUTORUN
 gameplay_qa();
#endif
 for(;;){
  k=(u16)(~REG_KEYINPUT)&0x03FF;newk=(u16)(k&~prev_keys);prev_keys=k;
  if(intro)v10_title_input(newk);
  else if(v10_opening){
   if(newk&KEY_START)v10_complete_opening();
   else if(newk&KEY_A)v10_advance_opening();
  }
  else if(cinema_active){
   if(newk&(KEY_A|KEY_START))cinema_end();
   else if(cinema_timer&&!--cinema_timer)cinema_end();
  }else{
   if(game_mode!=MODE_PAUSE&&(newk&KEY_START))enter_pause();
   else if(game_mode==MODE_PAUSE)update_pause(newk);
   else if(game_mode==MODE_SURFACE)update_surface(k,newk);
   else if(game_mode==MODE_BATTLE)update_battle(newk);
   else update_space(k,newk);
   if((frame&15)==0){state_tick();if(!buddy_quantum)quantum_workload_step();}
   if((frame&255)==0&&player_mp<max_mp)player_mp++;
   if(dialogue_timer)dialogue_timer--;
  }
  music_step();wait_vblank();frame++;render();
 }
}'''
repl(old,new,'boot and title/game flow')
# Render priority for UI BG1 was already 0. Need avoid global sprite priority 0 overriding in oam_set specific.
# Replace stale header comment version just in current source, keep historical APIs/script names stable.
s=s.replace('SIM EARTH // PIXEL UNIVERSE: THE LOST COSMOS V5','LOST COSMOS V10 / NATIVE GBA EDITION')
p.write_text(s)
print('V10 engine patch applied; sprites behind UI, 4-option title, 10-card prologue, checksummed tutorial progression, three ending cards')
