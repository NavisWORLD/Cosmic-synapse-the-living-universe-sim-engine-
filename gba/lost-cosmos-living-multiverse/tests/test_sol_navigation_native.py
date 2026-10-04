#!/usr/bin/env python3
"""Real C UI contracts: useful map access, earned goals and visible craft costs.

Simulated GBA MMIO checks remain separate from the real mGBA controller runs.
These assertions catch a locked map, premature objectives, hidden/wrong costs,
and rendering that changes the player's save or resource inventory.
"""
from pathlib import Path
import os
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / 'LOST_COSMOS_V10_SOURCE'
subprocess.run(['python3', 'host_qa_v5.py'], cwd=GAME, check=True, capture_output=True)
pre = (GAME / 'host_qa_v5.c').read_text().split('\n#ifdef HOST_QA\nint main(', 1)[0]
body = r'''
#include <assert.h>
#include <stdio.h>
static void fresh(void) {
 init_new_game(); intro=0; v10_opening=0; cinema_active=0;
 init_graphics(); v11_enter(0); v11_notice[0]=0;
}
static void text_at(int x,int y,const char *s) {
 volatile u16 *map=screenblock(UI_MAP_BASE);
 for(int i=0;s[i];i++) {
  int glyph=font_index(s[i]);
  assert(x+i<30);
  unsigned tile=map[y*32+x+i]&1023;
  if(tile!=(unsigned)(glyph<0?62:64+glyph)&&!(glyph<0&&tile==63)) {
   fprintf(stderr,"Expected %s at %d,%d: offset %d tile %u glyph %d\n",s,x,y,i,tile,glyph);
   assert(0);
  }
 }
}
static void field_goal(const char *s) {
 v11_notice[0]=0; v11_draw_field(); text_at(2,19,s);
}
int main(void) {
 fresh(); enter_pause(); pause_page=1; v11_field_track=0;
 update_pause(KEY_START);
 assert(pause_page==47); /* Local navigation must work before Track is learned. */
 v11_draw_pause(); text_at(2,14,"A YOU  C CORE  M ECHO");
 assert((screenblock(UI_MAP_BASE)[(4+10*10/64)*32+2+32*26/64]&1023)==64+font_index('C'));
 update_pause(KEY_B); assert(pause_page==1);
 update_pause(KEY_B); assert(pause_page==0);
 update_pause(KEY_B); assert(game_mode==MODE_SURFACE);
 field_goal("NEXT: FIND SIGNAL CORE");
 v11_cores_found=1; field_goal("NEXT: CARRY MEMORY ECHO");
 v11_echo_found=1; field_goal("NEXT: FACE THREE FOES");
 v11_world_kills[0]=3; field_goal("NEXT: LIGHT THE BEACON");
 v11_beacons=1; field_goal("NEXT: FOLLOW THE EAST GATE");
 v11_enter(6); v11_beacons|=64; v11_qty[92]=0; keys_found=0;
 field_goal("NEXT: FACE VESPER FOR Z");
 v11_qty[92]=1; field_goal("NEXT: FOLLOW THE EAST GATE");
 v11_enter(7); v11_beacons=255; field_goal("NEXT: FACE THE CROWN");
 v11_boss_done|=256; field_goal("NEXT: FIND THE QUIET");
 v11_boss_done|=512; field_goal("NEXT: FACE REMAINING BOSSES");
 v11_boss_done=1023; field_goal("NEXT: EVERY SIGNAL RESTORED");
 fresh(); player.x=30*8; player.y=53*8; v11_draw_field();
 text_at(2,18,"A REST");
 fresh(); enter_pause(); pause_page=41; v11_sel=0;
 v11_draw_pause(); text_at(2,14,"COST S"); text_at(8,14,"8");
 text_at(11,14,"H"); text_at(13,14,"2"); text_at(17,14,"C"); text_at(19,14,"0");
 v11_learn(50); v11_passives[0]=50; v11_inventory_add(67,1); v11_equipment[2]=67;
 v11_ui_dirty=1; v11_draw_pause(); text_at(8,14,"6"); text_at(13,14,"2");
 u8 old_save[32768],old_qty[100];
 for(int i=0;i<32768;i++)old_save[i]=SRAM[i];
 for(int i=0;i<100;i++)old_qty[i]=v11_qty[i];
 v11_draw_pause();
 for(int i=0;i<32768;i++)assert(SRAM[i]==old_save[i]);
 for(int i=0;i<100;i++)assert(v11_qty[i]==old_qty[i]);
 v11_scrap=6; v11_herbs=2; v11_qty[95]=1;
 v11_craft(); assert(v11_qty[22]==1&&v11_scrap==0&&v11_herbs==0);
 v11_notice[0]=0; v11_detail=0; v11_sel=3; v11_qty[93]=2; v11_scrap=1;
 v11_draw_pause(); text_at(19,14,"2");
 v11_craft(); assert(v11_qty[12]==1&&v11_qty[93]==0&&v11_scrap==0);
 v11_sel=10; v11_draw_pause(); text_at(2,14,"COST 200 CREDITS");
 puts("PASS: accessible landmark map, earned goals, contextual rest, exact discounted recipe costs, read-only rendering");
 return 0;
}
'''
with tempfile.TemporaryDirectory(prefix='sol-native-') as temp:
    source = Path(temp) / 'test.c'
    binary = Path(temp) / 'test'
    source.write_text(pre + body)
    for imported in (False, True):
        command = [os.environ.get('LC_HOST_CC', 'gcc'), '-DQA_AUTORUN', '-DHOST_QA', '-O2', '-I', str(GAME)]
        if imported:
            command.append('-DLC_IMPORTED_COMPANION')
        subprocess.run(command + [str(source), '-o', str(binary)], check=True)
        subprocess.run([str(binary)], check=True)
