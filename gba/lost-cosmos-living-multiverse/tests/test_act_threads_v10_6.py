"""EXECUTE CURRENT native GBA engine C through generated MMIO shim.
Tests 4 genuine physically distinct playable field rooms, distinct act prerequisites,
4×3 player decision continuations, game-only dialogue, reversible routes, SRAM.
This is NOT mGBA/Delta controller-led footage or author review of novel coverage.
"""
from pathlib import Path
import subprocess
r=Path(__file__).resolve().parents[1]
g=r/'LOST_COSMOS_V10_SOURCE'
subprocess.run(['python3','host_qa_v5.py'],cwd=g,check=True,capture_output=True,timeout=40)
pre=(g/'host_qa_v5.c').read_text().split('\n#ifdef HOST_QA\nint main(',1)[0]
a=(r/'tests/test_atlas_native.py').read_text()
route=a.split('static int route(',1)[1].split('static unsigned long signature',1)[0]
source=pre+'\n#include <assert.h>\n#include <stdio.h>\n#include <string.h>\nstatic int route('+route+r'''
static unsigned long map_sig(void){unsigned long h=2166136261u;
 for(int y=4;y<59;y++)for(int x=4;x<59;x++){
  h=(h^(unsigned long)(collision[mi(x,y)]+7*map_read_tile(x,y)))*16777619u;
 }return h;
}
static void stage_map(int idx){
 current_world=0;current_room=(u8)(G6_FIRST_ROOM+idx);current_layer=1;
 generate_surface();
 assert(trigger[mi(14,33)]==TR_G6_OATH);
 assert(trigger[mi(31,18)]==TR_G6_CHOICE);
 assert(trigger[mi(51,33)]==TR_G6_PROOF);
 assert(trigger[mi(17,43)]==TR_G6_CACHE);
 assert(trigger[mi(31,54)]==TR_G6_EXIT);
 assert(trigger[mi(20,42)]==TR_G6_NODE_W);
 assert(trigger[mi(31,25)]==TR_G6_NODE_C);
 assert(trigger[mi(48,35)]==TR_G6_NODE_E);
 int loc[][2]={{14,33},{31,18},{51,33},{17,43},{31,54},
                {20,42},{31,25},{48,35}};
 for(int i=0;i<8;i++)assert(route(31,52,loc[i][0],loc[i][1]));
}
static void earn_specific_act(int idx){
 if(idx==0){arc_progress=9;arc_petals=3;}
 if(idx==1){arc_progress=15;p4_material[2]=1;story_flags|=ST_VOID;
   v10_relic|=RF_HARMONY|RF_PASSION;}
 if(idx==2){arc_progress=13;cosmos.trust=110;v10_relic|=RF_CLARITY|RF_FESTIVAL;}
 if(idx==3){arc_progress=16;arc_petals=3;story_flags|=ST_LATTICE;
   postgame=1;ending=1;}
}
static void four_new_act_rooms_and_real_choices(void){
 unsigned long distinct[4];
 for(int idx=0;idx<4;idx++)for(int choice=1;choice<=3;choice++){
  init_new_game();init_graphics();intro=0;game_mode=MODE_SURFACE;
  story_flags|=ST_HEART;arc_progress=G6_PARENT[idx];
  current_world=0;current_room=(u8)(ARC_FIRST_ROOM+G6_PARENT[idx]);current_layer=1;
  generate_surface();assert(trigger[mi(54,32)]==TR_G6_PORTAL);
  assert(route(31,52,54,32));
  story_interact(TR_G6_PORTAL); /* Must NEVER bypass its parent chapter. */
  assert(current_room==ARC_FIRST_ROOM+G6_PARENT[idx]);
  arc_progress++;
  story_interact(TR_G6_PORTAL);assert(current_room==G6_FIRST_ROOM+idx);
  assert(game_mode==MODE_SURFACE);
  stage_map(idx);
  if(choice==1){distinct[idx]=map_sig();for(int j=0;j<idx;j++)assert(distinct[idx]!=distinct[j]);}
  assert(g6_step[idx]==0&&g6_choice[idx]==0);
  int prioratk=arc_guardian_attack(),priorguard=arc_guardian_guard();
  int original=inv[ITEM_SHARD];
  story_interact(TR_G6_CACHE);assert(inv[ITEM_SHARD]==original+2);
  original=inv[ITEM_SHARD];story_interact(TR_G6_CACHE);assert(inv[ITEM_SHARD]==original);
  story_interact(TR_G6_PROOF);assert(g6_step[idx]==0);
  story_interact(TR_G6_CHOICE);assert(!g6_pending);
  story_interact(TR_G6_OATH);assert(g6_step[idx]==1);
  story_interact(TR_G6_CHOICE);assert(g6_pending);
  if(idx==0&&choice==1){g6_answer(KEY_B);assert(!g6_pending&&g6_step[idx]==1);
   story_interact(TR_G6_CHOICE);assert(g6_pending);}
  g6_answer(choice==1?KEY_LEFT:choice==2?KEY_UP:KEY_RIGHT);
  assert(g6_step[idx]==2&&g6_choice[idx]==choice);
  int cr=credits;story_interact(TR_G6_PROOF);
  assert(g6_step[idx]==2&&credits==cr); /* Original earned later chapter events gate actual rewards. */
  save_game();
  u8 preserved[5][252];int off[]={0,LC_ROSTER_SRAM,ARC_SRAM,P4_SRAM,G5_SRAM};
  int size[]={238,252,32,32,32};
  for(int k=0;k<5;k++)for(int z=0;z<size[k];z++)preserved[k][z]=SRAM[off[k]+z];
  init_new_game();load_game();assert(current_room==G6_FIRST_ROOM+idx&&g6_step[idx]==2&&g6_choice[idx]==choice);
  for(int k=0;k<5;k++)for(int z=0;z<size[k];z++)assert(preserved[k][z]==SRAM[off[k]+z]);
  stage_map(idx);earn_specific_act(idx);
  int previouscredits=credits;story_interact(TR_G6_PROOF);
  assert(g6_step[idx]==2&&credits==previouscredits); /* No free proof before 3 original field clues. */
  /* Each act has an independently ordered spatial three-glyph puzzle; clicking
   * the wrong glyph must not silently advance. */
  assert(!g6_nodes[idx]);
  int first=G6_ORDER[idx][0],wrong=(first+1)%3;
  story_interact((u8)(TR_G6_NODE_W+wrong));assert(!g6_nodes[idx]);
  for(int k=0;k<3;k++){
   int node=G6_ORDER[idx][k];
   if(idx==1&&node==1){p4_material[2]=0;
     story_interact((u8)(TR_G6_NODE_W+node));assert(!(g6_nodes[idx]&(1u<<node)));
     p4_material[2]=1;
   }
   if(idx==2&&node==2){cosmos.trust=99;
     story_interact((u8)(TR_G6_NODE_W+node));assert(!(g6_nodes[idx]&(1u<<node)));
     cosmos.trust=110;
   }
   story_interact((u8)(TR_G6_NODE_W+node));
   assert(g6_nodes[idx]&(1u<<node));
   if(k==1){save_game();u8 puzzle_before=g6_nodes[idx];
      g6_nodes[idx]=0;g6_restore();assert(g6_nodes[idx]==puzzle_before);}
  }
  assert(g6_nodes[idx]==7);
  assert(idx!=1||p4_material[2]==0); /* Real earned rootleaf consumed exactly once. */
  story_interact(TR_G6_PROOF);
  assert(g6_step[idx]==3&&(g6_done&(1u<<idx)));
  assert(credits>previouscredits);
  assert(arc_guardian_attack()==prioratk+(choice==2));
  assert(arc_guardian_guard()==priorguard+(choice==1));
  int rewarded=inv[ITEM_SHARD],earnedxp=player_xp;
  story_interact(TR_G6_PROOF);
  assert(inv[ITEM_SHARD]==rewarded&&player_xp==earnedxp);
  /* Main game SRAM save persists the new optional act without touching 5 earlier pages. */
  save_game();init_new_game();load_game();
  assert(g6_step[idx]==3&&g6_choice[idx]==choice&&g6_done&(1u<<idx));
  assert(arc_guardian_attack()==(choice==2)); /* parent alone has no recruited guardians */
  stage_map(idx);story_interact(TR_G6_EXIT);
  assert(current_room==ARC_FIRST_ROOM+G6_PARENT[idx]);
 }
 puts("PASS native current-source: four genuinely distinct 64x64 maps, every 8-station collision-graph route, 12 ordered live node puzzles, resource/trust proof gating, locked source chapter entry, four independent three-choice paths, earned original-source milestones, old 5-page CRC saves, idempotent bonuses & rewards, real room exit and save/load");
}
static void journal_controls_and_lore_gate(void){
 init_new_game();init_graphics();intro=0;game_mode=MODE_SURFACE;
 current_room=2;arc_progress=8;generate_surface();
 enter_pause();pause_page=13;
 update_pause(KEY_UP);assert(pause_page==23&&g6_journal_sel==0);
 update_pause(KEY_DOWN);assert(g6_journal_sel==1);
 update_pause(KEY_R);assert(current_room==2); /* chapter 8 not complete (needs >=9) */
 update_pause(KEY_UP);assert(g6_journal_sel==0);
 update_pause(KEY_R);assert(current_room==G6_FIRST_ROOM);
 assert(game_mode==MODE_SURFACE);
 assert(trigger[mi(14,33)]==TR_G6_OATH);
 enter_pause();pause_page=23;update_pause(KEY_B);assert(pause_page==13);
 puts("PASS live START > ERIDORIA > UP actual journal, chapter-lock refusal, revisitable already-earned act routes and return input");
}
static void fail_closed_new_page_preserves_old_save(void){
 init_new_game();init_graphics();intro=0;story_flags|=ST_HEART;
 arc_progress=6;current_world=0;current_room=G6_FIRST_ROOM;
 g6_step[0]=2;g6_choice[0]=1;save_game();
 u8 before[5][252];int off[]={0,LC_ROSTER_SRAM,ARC_SRAM,P4_SRAM,G5_SRAM};
 int size[]={238,252,32,32,32};
 for(int k=0;k<5;k++)for(int z=0;z<size[k];z++)before[k][z]=SRAM[off[k]+z];
 u8 newpage[32];for(int i=0;i<32;i++)newpage[i]=SRAM[G6_SRAM+i];
 /* An old save without new page never invents optional act progress. */
 for(int i=0;i<32;i++)SRAM[G6_SRAM+i]=0xff;
 g6_restore();assert(g6_step[0]==0&&g6_done==0&&current_room==2);
 for(int k=0;k<5;k++)for(int z=0;z<size[k];z++)assert(before[k][z]==SRAM[off[k]+z]);
 /* A CRC-correct malicious impossible page with completion but no choice also fails closed. */
 for(int i=0;i<32;i++)newpage[i]=0;
 newpage[0]='G';newpage[1]='A';newpage[2]='C';newpage[3]='6';newpage[4]=1;
 newpage[5]=1;newpage[8]=3;newpage[12]=0;
 u32 crc=lc_crc32(newpage,28);
 for(int i=0;i<4;i++)newpage[28+i]=(u8)(crc>>(8*i));
 for(int i=0;i<32;i++)SRAM[G6_SRAM+i]=newpage[i];
 g6_restore();assert(!g6_done&&!g6_step[0]);
 for(int k=0;k<5;k++)for(int z=0;z<size[k];z++)assert(before[k][z]==SRAM[off[k]+z]);
 /* A structurally invalid 2-of-3 unordered field-record, even with correct
  * CRC, must fail closed while leaving older five pages intact. */
 newpage[5]=0;newpage[8]=2;newpage[12]=1;newpage[16]=
   (u8)((1u<<G6_ORDER[0][0])|(1u<<G6_ORDER[0][2]));
 arc_progress=10;crc=lc_crc32(newpage,28);
 for(int i=0;i<4;i++)newpage[28+i]=(u8)(crc>>(8*i));
 for(int i=0;i<32;i++)SRAM[G6_SRAM+i]=newpage[i];
 g6_restore();assert(!g6_step[0]&&!g6_nodes[0]);
 for(int k=0;k<5;k++)for(int z=0;z<size[k];z++)assert(before[k][z]==SRAM[off[k]+z]);
 newpage[16]=0;
 /* A separate illegal future quest in stage 2 cannot bypass the atlas prerequisite. */
 newpage[5]=0;newpage[8]=2;newpage[12]=1;arc_progress=0;
 crc=lc_crc32(newpage,28);for(int i=0;i<4;i++)newpage[28+i]=(u8)(crc>>(8*i));
 for(int i=0;i<32;i++)SRAM[G6_SRAM+i]=newpage[i];
 g6_restore();assert(!g6_step[0]);
 puts("PASS separate new 32-byte GAC6 page: absent old-save, valid-CRC impossible progression, locked-future-room recovery, preservation of all five prior SRAM ranges");
}
static void preserve_all_three_actual_ending_routes(void){
 for(int ending_id=1;ending_id<=3;ending_id++){
  init_new_game();init_graphics();intro=0;game_mode=MODE_SURFACE;
  story_flags|=ST_HEART|ST_LATTICE;arc_progress=16;
  current_world=0;current_room=33;postgame=1;ending=(u8)ending_id;
  generate_surface();arc_petals=3;g6_step[3]=2;g6_choice[3]=(u8)ending_id;
  /* Puzzle is independently tested through real native node interactions above;
   * epilogue proof fixture starts immediately before the already-earned seal. */
  g6_nodes[3]=7;
  story_interact(TR_G6_PROOF);assert(g6_done&(1u<<3));
  assert(strstr(dialogue,ending_id==1?"OPEN":ending_id==2?"PRESERVE":"WANDER")!=NULL);
  save_game();init_new_game();load_game();assert(ending==ending_id);
  current_room=ARC_EPILOGUE_ROOM;generate_surface();
  assert(route(31,52,32,15)&&trigger[mi(32,15)]==TR_ARC_EPILOGUE);
 }
 puts("PASS existing three distinct native OPEN/PRESERVE/WANDER endings and new associated authentic epilogue records, no choice-overwrite");
}
int main(void){
 four_new_act_rooms_and_real_choices();journal_controls_and_lore_gate();
 fail_closed_new_page_preserves_old_save();preserve_all_three_actual_ending_routes();return 0;
}
'''
(g/'act_threads_v106_native_host_qa.c').write_text(source)
subprocess.run(['clang','-DHOST_QA','-DQA_AUTORUN','-O2','-Wno-unused-function','act_threads_v106_native_host_qa.c','-o','act_threads_v106_native_host_qa'],cwd=g,check=True,timeout=60)
subprocess.run([str(g/'act_threads_v106_native_host_qa')],cwd=g,check=True,timeout=50)
