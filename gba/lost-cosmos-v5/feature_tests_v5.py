from pathlib import Path
import subprocess
root=Path(__file__).resolve().parent
source=(root/'host_qa_v5.c').read_text().split('\n#ifdef HOST_QA\nint main(',1)[0]
source+='''
#include <assert.h>
int main(void){
  int i;init_new_game();init_graphics();generate_surface();
  assert(npc_count>=2); assert(npc_near()==-1);
  player.x=npc_runtime[0].x;player.y=npc_runtime[0].y+8;
  assert(npc_near()>=0);
  npc_speak(npc_near()); assert(npc_dialogue_active==1); assert(npc_seen&1);
  intro=0;render();assert((screenblock(UI_MAP_BASE)[12*32+3]&1023)==64+font_index('M'));
  assert((OAM16[40*4+2]&1023)==92+NPCS[npc_dialogue_id].kind*8);
  npc_advance();npc_advance();npc_advance();assert(quest_started&1);
  inv[ITEM_SHARD]=1;npc_dialogue_page=2;npc_advance();
  assert(quest_completed&1);assert(inv[ITEM_SHARD]==0);assert(inv[ITEM_POTION]>=4);
  npc_close();save_game();assert(save_valid());
  init_new_game();load_game();assert(quest_completed&1);assert(npc_seen&1);
  current_world=2;current_layer=1;current_room=0;generate_surface();assert(npc_count>=2);
  /* Simulate a real prior mGBA-produced V3 SRAM image (do not mutate original). */
  {FILE*f=fopen("qa_fixtures/v3_mgba_boot1.sav","rb");assert(f);
   assert(fread((void*)HOST_SRAM,1,32768,f)==32768);fclose(f);}
  assert(save_valid_v3());assert(!save_valid());
  init_new_game();load_game();assert(save_valid());
  assert(SRAM[3]=='5'&&keys_found==1&&weapon==1&&player_level==2);
  assert(quest_started==0&&quest_completed==0&&npc_seen==0);
  /* Check preserved V2->V5 migration as well. */
  {FILE*f=fopen("qa_fixtures/v2_mgba_boot1.sav","rb");assert(f);
   assert(fread((void*)HOST_SRAM,1,32768,f)==32768);fclose(f);}
  assert(save_valid_v2()); init_new_game();load_game();assert(save_valid());
  assert(keys_found&1);assert(player_level==1);assert(quest_started==0);
  puts("PASS: NPC spawn/dialogue/quest/reward/SRAM, Tide NPCs, real V3 and V2 save migration");
  return 0;
}
'''
(root/'feature_qa.c').write_text(source)
subprocess.run(['clang','-DQA_AUTORUN','-DHOST_QA','-O2','-Wno-unused-function','feature_qa.c','-o','feature_qa'],cwd=root,check=True)
subprocess.run([str(root/'feature_qa')],cwd=root,check=True)