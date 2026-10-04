"""Host-level verification of V6 independent UI background and optional battle flow."""
from pathlib import Path
import subprocess
root=Path(__file__).parent
host=(root/'host_qa_v5.c').read_text().split('\n#ifdef HOST_QA\nint main(',1)[0]
assert 'static void battle_enter' in host
host+='''
#include <assert.h>
#include <stdio.h>
int main(void){
 int i,astrid=0;
 init_new_game();init_graphics();generate_surface();
 /* Every glyph pixel, including its unused corners, must be opaque palette index 2. */
 {u32 glyph=VRAM32[(0x4000/4)+(64*8)];
  assert((glyph&15)==2);
  assert(VRAM32[(0x4000/4)+(62*8)]==0x22222222u);
  ui_clear();ui_text(2,4,"A B",15);
  assert((screenblock(UI_MAP_BASE)[4*32+3]&1023)==62);
 }
 /* First-story Astrid is a real inhabiting NPC with an SRAM-backed quest. */
 for(i=0;i<npc_count;i++)if(npc_runtime[i].id==13){astrid=1;
  npc_speak(i);npc_advance();npc_advance();npc_advance();
  assert((quest_started&(1u<<6))!=0);
  npc_close();break;
 }
 assert(astrid);
 {u32 q=workload_qi;
  clear_combat();spawn_enemy(9,12,51,EN_GLITCH,0);enemies[9].hp=1;
  battle_enter(9);assert(game_mode==MODE_BATTLE);intro=0;
  render();assert((screenblock(UI_MAP_BASE)[1*32+2]&1023)==64+font_index('E'));
  battle_cursor=0;battle_act();assert(battle_phase==3&&!enemies[9].active);
  battle_timer=0;update_battle(0);assert(game_mode==MODE_SURFACE&&workload_qi==q);
 }
 {u8 hp=player.hp;clear_combat();spawn_enemy(9,12,51,EN_GLITCH,0);
  battle_enter(9);battle_cursor=2;battle_act();assert(battle_phase==1);
  update_battle(KEY_B);assert(battle_evade==1);
  for(i=0;i<45;i++)update_battle(0);
  assert(player.hp==hp);
  battle_exit();
 }
 {u32 q=workload_qi;clear_combat();spawn_enemy(9,12,51,EN_GLITCH,0);
  battle_enter(9);enemies[9].hp=1;battle_cursor=3;battle_act();
  assert(battle_phase==3&&!enemies[9].active);battle_timer=0;update_battle(0);
  assert(workload_qi==q);
 }
 {u8 hp=player.hp;save_game();assert(save_valid());
  assert((quest_started&(1u<<6))!=0);
  quest_started=0;load_game();assert(player.hp==hp&&(quest_started&(1u<<6))!=0);
 }
 puts("PASS V6 opaque glyphs, NPC Astrid quest save, full-screen battle victory, guard, mercy, deterministic quantum stream");
 return 0;
}
'''
(root/'v6_slice_host.c').write_text(host)
subprocess.run(['clang','-DQA_AUTORUN','-DHOST_QA','-O2','-Wno-unused-function','v6_slice_host.c','-o','v6_slice_host'],cwd=root,check=True)
subprocess.run([str(root/'v6_slice_host')],cwd=root,check=True)
