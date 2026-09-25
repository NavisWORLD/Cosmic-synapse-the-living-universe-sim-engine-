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
  intro=0;render();assert((screenblock(UI_MAP_BASE)[12*32+2]&1023)==64+font_index('M'));
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
  /* Import a genuine mGBA V4 boot1 save; keep NPC quest flags and Q cursor. */
  {FILE*f=fopen("qa_fixtures/v4_mgba_boot1.sav","rb");assert(f);
   assert(fread((void*)HOST_SRAM,1,32768,f)==32768);fclose(f);}
  assert(save_valid_v4()); assert(!save_valid());
  init_new_game();load_game();assert(save_valid());
  assert(keys_found&1 && quest_started&1 && npc_seen&1 && weapon==1);
  assert(workload_qi==qi);
  /* Check preserved V2->V5 migration as well. */
  {FILE*f=fopen("qa_fixtures/v2_mgba_boot1.sav","rb");assert(f);
   assert(fread((void*)HOST_SRAM,1,32768,f)==32768);fclose(f);}
  assert(save_valid_v2()); init_new_game();load_game();assert(save_valid());
  assert(keys_found&1);assert(player_level==1);assert(quest_started==0);
  /* A presentation-only audio/dialogue/NPC step can no longer eat archived replay. */
  init_new_game();qi=16;workload_qi=0;audio_on=1;frame=32;
  {u32 gameplay_before=qi;u32 replay_before=workload_qi;
   say("AUDIO REPLAY ISOLATION");music_tick=35;music_step();npc_tick();
   assert(qi==gameplay_before && workload_qi==replay_before);}
  quantum_workload_step();assert(workload_qi==8&&qi==16);
  /* Combat must telegraph before damage and give the player a dodge window. */
  current_world=0;current_layer=1;current_room=0;game_mode=MODE_SURFACE;
  generate_surface();clear_combat();
  {int x,y;for(y=20;y<=24;y++)for(x=18;x<=26;x++)collision[mi(x,y)]=C_FREE;}
  player.x=176;player.y=176;player.hp=max_hp=10;player.hurt=0;
  spawn_enemy(0,20,22,EN_GLITCH,0);
  assert(enemies[0].x==160 && enemies[0].y==176);
  enemy_tick();assert(enemies[0].windup==20&&player.hp==10);
  {int i;for(i=0;i<19;i++)enemy_tick();assert(player.hp==10);
   player_dodge(KEY_B|KEY_RIGHT);assert(dodge_timer>0 && player.x>176);
   enemy_tick();assert(player.hp==10&&enemies[0].recover>0);}
  /* Heavy attack is gated by cooldown and does not mutate replay state. */
  clear_combat();player.x=176;player.y=176;player.face=2;
  spawn_enemy(0,18,22,EN_GLITCH,0);
  {u8 before=enemies[0].hp;u32 replay_before=workload_qi;
   heavy_cooldown=0;player_heavy_attack();assert(enemies[0].hp<before||!enemies[0].active);
   assert(heavy_cooldown>0 && workload_qi==replay_before);}
  puts("PASS: V5 original indexed art, telegraphed combat, dodge/heavy, replay isolation, NPC quests, and genuine V2/V3/V4 save migration");
  return 0;
}
'''
(root/'feature_qa.c').write_text(source)
subprocess.run(['clang','-DQA_AUTORUN','-DHOST_QA','-O2','-Wno-unused-function','feature_qa.c','-o','feature_qa'],cwd=root,check=True)
subprocess.run([str(root/'feature_qa')],cwd=root,check=True)
