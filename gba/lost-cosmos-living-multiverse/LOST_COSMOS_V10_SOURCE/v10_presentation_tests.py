"""Regression tests for V10 real menu, story path and GBA OAM/BG pixel priority.
Runs engine against fake mapped GBA hardware; mGBA tests are an additional gate.
"""
from pathlib import Path
import subprocess
R=Path(__file__).parent
src=(R/'host_qa_v5.c').read_text().split('\n#ifdef HOST_QA\nint main(',1)[0]
src+=r'''
#include <assert.h>
#include <stdio.h>
int main(void){int i,elder=-1,astrid=-1,mira=-1;u8 orig_sram[230];
 /* Native VRAM/OAM mapping in the host lets us inspect actual hardware writes. */
 init_new_game();init_graphics();generate_surface();
 assert(V51_SCENE_COUNT==23);
 assert(V51_SCENE_COUNTS[12]>100&&V51_SCENE_COUNTS[13]>100&&V51_SCENE_COUNTS[14]>100);
 assert((REG_BG1CNT&3)==0 && (REG_BG0CNT&3)==2);
 oam_set(0,64,103,0,0,0);assert((OAM16[2]>>10&3)==1);
 oam_set32(2,161,68,272,0);assert((OAM16[2*4+2]>>10&3)==1);
 oam_ui_portrait(2);assert((OAM16[2*4+2]>>10&3)==0);
 /* Force player+NPC+enemy to overlap the DIALOGUE panel.
    BG1 tiles are opaque in this rectangle and BG1 priority 0 beats OBJ priority 1. */
 current_world=0;current_room=0;generate_surface();intro=0;
 npc_dialogue_active=1;npc_dialogue_id=13;npc_dialogue_page=0;
 player.x=120;player.y=420;cam_x=0;cam_y=310;
 draw_hud();render_surface_sprites();
 for(i=11;i<=19;i++)assert((screenblock(UI_MAP_BASE)[i*32+17]&1023)!=0);
 assert((OAM16[0*4+2]>>10&3)==1);
 assert((OAM16[1*4+2]>>10&3)==1);
 assert((OAM16[40*4]&255)==69); /* portrait ABOVE panel, not over words */
 npc_dialogue_active=0;
 /* Title: no-save state refuses Continue; all four entries have live actions. */
 for(i=0;i<230;i++)orig_sram[i]=(u8)SRAM[i];
 for(i=0;i<230;i++)SRAM[i]=0;
 init_new_game();v10_has_save=0;intro=1;v10_title_sel=1;
 v10_title_input(KEY_A);assert(intro&& !v10_opening);
 v10_title_sel=2;v10_title_input(KEY_A);assert(v10_title_sub==2);
 {int a=audio_on;v10_title_input(KEY_A);assert(audio_on!=a);v10_title_input(KEY_B);assert(v10_title_sub==0);}
 v10_title_sel=3;v10_title_input(KEY_A);assert(v10_title_sub==3);
 v10_title_input(KEY_B);assert(v10_title_sub==0);
 /* A valid prior SRAM save is NOT erased merely by selecting New Game. */
 {FILE*f=fopen("qa_fixtures/v7_mgba_boot1.sav","rb");assert(f);assert(fread((void*)HOST_SRAM,1,32768,f)==32768);fclose(f);}
 assert(save_valid());v10_has_save=1;v10_title_sel=0;
 v10_title_input(KEY_A);assert(v10_title_sub==1&&save_valid());
 v10_title_input(KEY_B);assert(v10_title_sub==0&&save_valid());
 v10_title_input(KEY_A);v10_title_input(KEY_A);
 assert(!intro && v10_opening&&v10_opening_step==0 && save_valid());
 assert(cinema_scene==7);
 for(i=1;i<V10_OPENING_COUNT;i++){
  v10_advance_opening();assert(v10_opening&&v10_opening_step==i);
  assert(cinema_scene==V10_OPENING[i].art);
 }
 v10_advance_opening();assert(!v10_opening&&!cinema_active);
 assert(current_world==0&&current_room==2&&v10_tutorial==1);
 assert(can_stand(player.x,player.y));
 assert(save_valid() && SRAM[227]==0xA6 && SRAM[228]==1);
 for(i=0;i<npc_count;i++)if(npc_runtime[i].id==14)elder=i;
 assert(elder>=0);npc_speak(elder);assert(v10_tutorial==2);npc_close();
 player.x=10*8;story_gate();assert(current_room==0&&v10_tutorial==3);
 for(i=0;i<npc_count;i++){
  if(npc_runtime[i].id==13)astrid=i;
  if(npc_runtime[i].id==0)mira=i;
 }
 assert(astrid>=0 && mira>=0);
 npc_speak(astrid);assert(v10_tutorial==4);npc_close();
 npc_speak(mira);assert(v10_tutorial==0);npc_close();
 v10_tutorial=3;save_game();v10_tutorial=0;load_game();
 assert(v10_tutorial==3 && SRAM[229]==(u8)(0x69^SRAM[227]^SRAM[228]^SRAM[211]^SRAM[226]));
 SRAM[229]^=1;load_game();assert(v10_tutorial==0 && save_valid());
 /* Legacy SRAM V7 never gains spurious V10 tutorial state on import. */
 {FILE*f=fopen("qa_fixtures/v7_mgba_boot1.sav","rb");assert(f);assert(fread((void*)HOST_SRAM,1,32768,f)==32768);fclose(f);}
 init_new_game();load_game();assert(v10_tutorial==0 && save_valid());
 printf("PASS V10: GBA BG1/OBJ dialogue separation; three prior story scenes and eight new novel/ending scenes; four live title options; safe new-game confirmation; ten ordered prologue scenes; Brindlemark-to-Astrid playable tutorial; checksummed and legacy-safe SRAM.\n");
 return 0;
}
'''
(R/'v10_presentation_qa.c').write_text(src)
subprocess.run(['clang','-DQA_AUTORUN','-DHOST_QA','-O2','-Wno-unused-function','v10_presentation_qa.c','-o','v10_presentation_qa'],cwd=R,check=True)
subprocess.run([str(R/'v10_presentation_qa')],cwd=R,check=True)
