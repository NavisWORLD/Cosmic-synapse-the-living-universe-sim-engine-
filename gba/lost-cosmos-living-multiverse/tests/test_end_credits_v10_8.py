"""Run actual current GBA C source through simulated MMIO, NOT emulator footage.
Verify real ending-card handoff to four pages and return to playable postgame.
"""
from pathlib import Path
import subprocess
r=Path(__file__).resolve().parents[1]
g=r/'LOST_COSMOS_V10_SOURCE'
subprocess.run(['python3','host_qa_v5.py'],cwd=g,check=True,capture_output=True,text=True,timeout=45)
src=(g/'host_qa_v5.c').read_text().split('\n#ifdef HOST_QA\nint main(',1)[0]
code=src+r'''
#include <assert.h>
#include <stdio.h>
static void each_ending(void){
 for(int e=1;e<=3;e++){
  init_new_game();init_graphics();intro=0;ending=(u8)e;game_mode=MODE_SURFACE;
  generate_surface();
  assert(v108_credits_active==0);
  cinema_active=1;v10_ending_card=0;cinema_end();
  assert(!v108_credits_active); /* regular cinema never triggers the credits */
  cinema_active=1;v10_ending_card=1;cinema_end();
  assert(v108_credits_active&&v108_credits_page==0&&!cinema_active);
  assert(ending==e&&game_mode==MODE_SURFACE);
  v108_credits_draw();v108_credits_input(KEY_A);
  assert(v108_credits_page==1);
  v108_credits_input(KEY_RIGHT);assert(v108_credits_page==2);
  v108_credits_draw(); /* route-specific text in native GBA BG tilemap */
  v108_credits_input(KEY_LEFT);assert(v108_credits_page==1);
  for(int i=0;i<360;i++)v108_credits_tick();assert(v108_credits_page==2);
  for(int i=0;i<360;i++)v108_credits_tick();assert(v108_credits_page==3);
  for(int i=0;i<720;i++)v108_credits_tick();assert(v108_credits_page==3);
  v108_credits_draw();v108_credits_input(KEY_A);
  assert(!v108_credits_active&&ending==e&&game_mode==MODE_SURFACE);
  v108_credits_begin();v108_credits_input(KEY_START);
  assert(!v108_credits_active);
  v108_credits_begin();init_new_game();assert(!v108_credits_active);
 }
 puts("PASS native source: all 3 endings, 4 credit pages, A/LEFT/START and timer, no false cutscene trigger, old postgame intact");
}
int main(void){each_ending();return 0;}
'''
f=g/'test_end_credits_v108_host.c';f.write_text(code)
binary=g/'test_end_credits_v108_host'
subprocess.run(['clang','-DQA_AUTORUN','-DHOST_QA','-O2','-Wno-unused-function',f.name,'-o',binary.name],cwd=g,check=True,timeout=60)
subprocess.run([str(binary)],cwd=g,check=True,timeout=30)
