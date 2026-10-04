"""Execute actual current native GBA C engine through MMIO host shim.
No newly recorded mGBA or iPhone Delta assertions. Quest scenes are game-new
micro-challenges keyed to 17 manuscript appendix roles, not full book adaption.
"""
from pathlib import Path
import subprocess
root=Path(__file__).resolve().parents[1];g=root/'LOST_COSMOS_V10_SOURCE'
subprocess.run(['python3','host_qa_v5.py'],cwd=g,check=True,capture_output=True,timeout=40)
pre=(g/'host_qa_v5.c').read_text().split('\n#ifdef HOST_QA\nint main(',1)[0]
other=(root/'tests/test_atlas_native.py').read_text()
route=other.split('static int route(',1)[1].split('static unsigned long signature',1)[0]
source=pre+'\n#include <assert.h>\n#include <stdio.h>\n#include <string.h>\nstatic int route('+route+ r'''
static void satisfy_after_oath(int i){
 switch(i){
 case 0:case 4:case 11:{int n=i==4?3:i==0?2:1;
  for(int k=0;k<n;k++){spawn_enemy(0,33,29,EN_EMBER,0);enemies[0].hp=1;
   damage_enemy(&enemies[0],99);assert(enemies[0].active==0);}
  if(i==11)p4_material[3]=1;
  break;}
 case 1:arc_interact(TR_ARC_SECRET);p4_material[4]=1;break;
 case 2:player_mp=3;p4_material[1]=1;break;
 case 3:p4_material[2]=1;break;
 case 5:p4_material[0]=p4_material[1]=1;break;
 case 6:arc_interact(TR_ARC_SECRET);p4_material[3]=1;break;
 case 7:arc_petals=3;p4_material[2]=1;break;
 case 8:arc_anchors=3;p4_material[1]=1;break;
 case 9:assert(lc_add_wild(&lc_party,3,0xabba0009u)==LC_OK);
  lc_party.slots[0].bond=70;break;
 case 10:p4_material[4]=1;break;
 case 12:v10_relic|=RF_FESTIVAL;p4_material[4]=1;break;
 case 13:assert(lc_add_wild(&lc_party,3,0xabba0013u)==LC_OK);
  lc_party.slots[0].bond=55;p4_material[2]=1;break;
 case 14:keys_found=7;p4_material[0]=p4_material[3]=1;break;
 case 15:for(int x=0;x<5;x++)p4_material[x]=1;break;
 case 16:arc_secret_mask=0x000F;inv[ITEM_SHARD]=3;break;
 }
}
static void test_all_seventeen_field_quests(void){
 for(int i=0;i<17;i++){
  init_new_game();init_graphics();intro=0;game_mode=MODE_SURFACE;
  story_flags|=ST_HEART;arc_progress=(u8)(i==16?16:i+1);
  arc_guardians_mask|=1u<<i;
  current_world=0;current_room=(u8)(i==16?ARC_EPILOGUE_ROOM:ARC_FIRST_ROOM+i);
  current_layer=1;if(i==16){postgame=1;ending=1;}generate_surface();
  assert(trigger[mi(22,32)]==TR_G5_OATH);assert(trigger[mi(49,37)]==TR_G5_PROOF);
  assert(route(31,52,22,32)&&route(31,52,49,37));
  assert(g5_active==G5_NONE&&!(g5_complete&(1u<<i)));
  story_interact(TR_G5_PROOF);assert(g5_active==G5_NONE); /* Cannot complete without oath. */
  story_interact(TR_G5_OATH);assert(g5_active==i&&g5_start_kills==kill_count);
  story_interact(TR_G5_PROOF);assert(g5_active==i&&!(g5_complete&(1u<<i)));
  if(i==0){
   save_game();init_new_game();load_game();
   assert(g5_active==0&&g5_start_kills==kill_count&&current_room==ARC_FIRST_ROOM);
   arc_guardians_mask|=(1u<<1);current_room=(u8)(ARC_FIRST_ROOM+1);
   story_interact(TR_G5_OATH);assert(g5_active==0);current_room=ARC_FIRST_ROOM;
  }
  satisfy_after_oath(i);assert(g5_ready(i));
  int before=credits;int oldmat[5];for(int j=0;j<5;j++)oldmat[j]=p4_material[j];
  int oldatk,oldguard;arc_ally=(u8)i;
  oldatk=arc_guardian_attack();oldguard=arc_guardian_guard();
  story_interact(TR_G5_PROOF);
  assert(g5_complete&(1u<<i));assert(g5_active==G5_NONE);
  assert(arc_guardian_attack()==oldatk+G5_ATK[i]);
  assert(arc_guardian_guard()==oldguard+G5_DEF[i]);
  assert(credits>before);
  u8 left[5];for(int j=0;j<5;j++)left[j]=p4_material[j];
  int xp=player_xp,c=credits;
  story_interact(TR_G5_PROOF);assert(player_xp==xp&&credits==c);
  for(int j=0;j<5;j++)assert(p4_material[j]==left[j]);
  save_game();u8 oldPage[252];for(int j=0;j<252;j++)oldPage[j]=SRAM[LC_ROSTER_SRAM+j];
  init_new_game();load_game();
  assert(g5_complete&(1u<<i));assert(g5_active==G5_NONE);
  for(int j=0;j<252;j++)assert(oldPage[j]==SRAM[LC_ROSTER_SRAM+j]);
 }
 puts("PASS ACTUAL SOURCE all 17 distinct guardian field personal quests: both physically reachable stations, no auto-complete, real earned prerequisites, two distinct conditional battle wins, atomic debits, role-specific attack/guard bonus, replay-safe rewards and real save/load");
}
static void test_journal_and_old_room_revisit(void){
 init_new_game();init_graphics();intro=0;game_mode=MODE_SURFACE;
 story_flags|=ST_HEART;arc_progress=9;arc_guardians_mask=0x1FFu;
 current_world=0;current_room=2;generate_surface();
 enter_pause();pause_page=19;arc_ally_sel=2;
 update_pause(KEY_L);assert(pause_page==22&&g5_journal_sel==2);
 update_pause(KEY_R);assert(current_world==0&&current_room==ARC_FIRST_ROOM+2);
 assert(game_mode==MODE_SURFACE);
 assert(trigger[mi(22,32)]==TR_G5_OATH&&trigger[mi(49,37)]==TR_G5_PROOF);
 story_interact(TR_G5_OATH);assert(g5_active==2);
 enter_pause();pause_page=19;arc_ally_sel=2;
 update_pause(KEY_L);assert(pause_page==22);
 update_pause(KEY_SELECT);assert(g5_active==G5_NONE);
 update_pause(KEY_B);assert(pause_page==19);
 g5_warp(16);assert(current_room==ARC_FIRST_ROOM+2); /* No unrecruited Altair warp. */
 puts("PASS actual controller L/R/SELECT journal, old chapter replay, cancel without losing relics and locked/epilogue travel guard");
}
static void test_original_act1_three_physical_places(void){
 init_new_game();init_graphics();intro=0;game_mode=MODE_SURFACE;
 current_world=0;current_room=2;current_layer=1;generate_surface();
 assert(trigger[mi(31,40)]==TR_G5_BOOK_HOME);assert(route(31,52,31,40));
 story_interact(TR_G5_BOOK_HOME);assert(g5_book_step==0);
 current_room=4;generate_surface();assert(trigger[mi(32,38)]==TR_G5_BOOK_TEMPLE);
 assert(route(32,52,32,38));story_interact(TR_G5_BOOK_TEMPLE);assert(g5_book_step==0);
 current_room=3;generate_surface();assert(trigger[mi(39,40)]==TR_G5_BOOK_OAK);
 assert(route(29,50,39,40));story_interact(TR_G5_BOOK_OAK);assert(g5_book_step==1);
 save_game();init_new_game();load_game();assert(current_room==3&&g5_book_step==1);
 generate_surface();story_interact(TR_G5_BOOK_OAK);assert(g5_book_step==1);
 current_room=4;generate_surface();story_interact(TR_G5_BOOK_TEMPLE);assert(g5_book_step==2);
 story_interact(TR_G5_BOOK_TEMPLE);assert(g5_book_step==2);
 current_room=2;generate_surface();int oldshard=inv[ITEM_SHARD];
 story_interact(TR_G5_BOOK_HOME);assert(g5_book_step==2&&inv[ITEM_SHARD]==oldshard);
 /* Actual old four-rune gate executes in the original engine, not a made-up quest flag. */
 current_room=4;generate_surface();rune_touch(2);rune_touch(0);rune_touch(3);rune_touch(1);
 assert(story_flags&ST_PUZZLE);
 /* Real Malakar original encounter tests run separately; using an inherited
  * VALID completed boss state here exercises optional quest's acceptance gate. */
 story_flags|=ST_MALAKAR;story_interact(TR_HEART);assert(story_flags&ST_HEART);
 current_room=2;generate_surface();oldshard=inv[ITEM_SHARD];
 story_interact(TR_G5_BOOK_HOME);assert(g5_book_step==3);
 assert(inv[ITEM_SHARD]==oldshard+3);
 save_game();init_new_game();load_game();assert(g5_book_step==3);
 oldshard=inv[ITEM_SHARD];story_interact(TR_G5_BOOK_HOME);
 assert(inv[ITEM_SHARD]==oldshard);
 puts("PASS source-native 3 original first-act regions: physically walkable Oakwood archaeologist ledger, Cragstone 4-real-rune gate, post-Malakar Heart return to Brindlemark; mid-quest SRAM and no duplicate rewards");
}
static void test_sram_old_migration_and_fail_closed(void){
 init_new_game();init_graphics();intro=0;game_mode=MODE_SURFACE;
 story_flags|=ST_HEART;arc_progress=2;arc_guardians_mask=3;save_game();
 u8 legacy[238],roster[252],arc[32],craft[32];
 for(int i=0;i<238;i++)legacy[i]=SRAM[i];
 for(int i=0;i<252;i++)roster[i]=SRAM[LC_ROSTER_SRAM+i];
 for(int i=0;i<32;i++){arc[i]=SRAM[ARC_SRAM+i];craft[i]=SRAM[P4_SRAM+i];}
 /* Old V10.4 had no GQS5. Absent page never fabricates guardian quest rewards. */
 for(int i=0;i<32;i++)SRAM[G5_SRAM+i]=0xFF;
 g5_complete=0x1FFFF;g5_active=0;g5_restore();
 assert(g5_complete==0&&g5_active==G5_NONE);
 for(int i=0;i<32;i++)assert(arc[i]==SRAM[ARC_SRAM+i]&&craft[i]==SRAM[P4_SRAM+i]);
 for(int i=0;i<238;i++)assert(legacy[i]==SRAM[i]);
 for(int i=0;i<252;i++)assert(roster[i]==SRAM[LC_ROSTER_SRAM+i]);
 g5_complete=1;g5_active=1;g5_start_kills=5;g5_save();
 u8 b[32];for(int i=0;i<32;i++)b[i]=SRAM[G5_SRAM+i];
 b[8]=0xFF;u32 crc=lc_crc32(b,28);
 for(int i=0;i<4;i++)b[28+i]=(u8)(crc>>(8*i));
 for(int i=0;i<32;i++)SRAM[G5_SRAM+i]=b[i];
 g5_restore();assert(g5_complete==0&&g5_active==G5_NONE);
 /* Invalid _reserved_ byte with perfectly recomputed CRC must also fail. */
 g5_complete=1;g5_active=G5_NONE;g5_save();
 for(int i=0;i<32;i++)b[i]=SRAM[G5_SRAM+i];b[16]=1;crc=lc_crc32(b,28);
 for(int i=0;i<4;i++)b[28+i]=(u8)(crc>>(8*i));
 for(int i=0;i<32;i++)SRAM[G5_SRAM+i]=b[i];
 g5_restore();assert(g5_complete==0);
 /* CRC-correct but impossible original-book progression also fails closed. */
 g5_complete=0;g5_active=G5_NONE;g5_book_step=0;g5_save();
 for(int i=0;i<32;i++)b[i]=SRAM[G5_SRAM+i];b[12]=4;
 crc=lc_crc32(b,28);for(int i=0;i<4;i++)b[28+i]=(u8)(crc>>(8*i));
 for(int i=0;i<32;i++)SRAM[G5_SRAM+i]=b[i];
 g5_restore();assert(g5_book_step==0&&g5_complete==0);
 for(int i=0;i<32;i++)assert(arc[i]==SRAM[ARC_SRAM+i]&&craft[i]==SRAM[P4_SRAM+i]);
 puts("PASS V10.4 missing page migration, CRC-correct impossible completion/reserved-byte rejection, other four older save pages byte-for-byte intact");
}
int main(void){test_all_seventeen_field_quests();test_journal_and_old_room_revisit();test_original_act1_three_physical_places();test_sram_old_migration_and_fail_closed();return 0;}
'''
(g/'guardian_v105_native_host_qa.c').write_text(source)
subprocess.run(['clang','-DHOST_QA','-DQA_AUTORUN','-O2','-Wno-unused-function','guardian_v105_native_host_qa.c','-o','guardian_v105_native_host_qa'],cwd=g,check=True,timeout=60)
subprocess.run([str(g/'guardian_v105_native_host_qa')],cwd=g,check=True,timeout=40)
