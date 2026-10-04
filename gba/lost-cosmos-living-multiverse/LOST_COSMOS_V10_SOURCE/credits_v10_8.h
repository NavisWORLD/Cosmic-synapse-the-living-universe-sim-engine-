/* LOST COSMOS — genuine four-page, controller-driven credits and postgame return.
 * Rendering only: no chapter flag, score, private manuscript, API or save writes.
 * Ends the original three-ending cinematic before handing control back to game. */
#ifndef LC_CREDITS_V10_8_H
#define LC_CREDITS_V10_8_H
static u8 v108_credits_active=0,v108_credits_page=0;
static u16 v108_credits_clock=0;
static void v108_credits_begin(void){
 v108_credits_active=1;v108_credits_page=0;v108_credits_clock=0;
}
static void v108_credits_reset(void){
 v108_credits_active=0;v108_credits_page=0;v108_credits_clock=0;
}
static void v108_credits_advance(void){
 if(v108_credits_page<3)v108_credits_page++;
 else v108_credits_active=0;
 v108_credits_clock=0;
}
static void v108_credits_input(u16 keys){
 if(keys&(KEY_START|KEY_B)){v108_credits_reset();return;}
 if(keys&(KEY_A|KEY_RIGHT))v108_credits_advance();
 else if(keys&KEY_LEFT){if(v108_credits_page)v108_credits_page--;v108_credits_clock=0;}
}
static void v108_credits_tick(void){
 if(!v108_credits_active||v108_credits_page>=3)return;
 if(++v108_credits_clock>=360)v108_credits_advance();
}
static void v108_credits_draw(void){
 oam_hide_all();ui_clear();ui_fill_rows(0,19,63,15);
 ui_text(3,1,"LOST COSMOS",14);
 ui_text(3,2,"THE LIVING MULTIVERSE",15);
 if(v108_credits_page==0){
  ui_text(3,5,"AN ERIDORIA ADVENTURE",14);
  ui_text(3,7,"ORIGINAL STORY AND WORLD",13);
  ui_text(3,9,"CORY DAVIS",15);
  ui_text(3,12,"NAVISWORLD / COSMOS",14);
 }else if(v108_credits_page==1){
  ui_text(3,5,"THE PEOPLE OF ERIDORIA",14);
  ui_text(3,8,"ARIN AND THE FELLOWSHIP",15);
  ui_text(3,10,"THE GUARDIANS AND BEASTS",15);
  ui_text(3,12,"THE PATHS THEY PROTECTED",15);
 }else if(v108_credits_page==2){
  ui_text(3,5,"YOUR CHOSEN PATH",14);
  ui_text(3,8,ending==1?"OPEN":ending==2?"PRESERVE":"WANDER",15);
  ui_text(3,11,ending==1?"THE REALMS CAN CONNECT":
          ending==2?"THE REALMS REMAIN SAFE":"NEW ROADS STILL AWAIT",13);
 }else{
  ui_text(3,5,"THANK YOU FOR PLAYING",14);
  ui_text(3,8,"THE ADVENTURE CONTINUES",15);
  ui_text(3,10,"IN YOUR CHOSEN WORLD",15);
  ui_text(3,12,"YOUR COMPANIONS REMAIN",13);
 }
 ui_text(3,16,"A NEXT   LEFT PREVIOUS",14);
 ui_text(3,18,"START OR B RETURN TO GAME",13);
}
#endif
