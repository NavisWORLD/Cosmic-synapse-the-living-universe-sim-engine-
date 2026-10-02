"""Source-derived actual native C MMIO test. No fake mGBA/device claims.
Simulates five in-game sanctuary routes and battle/party/save decisions against
exact latest source, catches accidental old-quest/ship-trigger overwrites.
"""
from pathlib import Path
import subprocess
root=Path(__file__).resolve().parents[1];g=root/'LOST_COSMOS_V10_SOURCE'
subprocess.run(['python3','-u','host_qa_v5.py'],cwd=g,check=True,capture_output=True,timeout=35)
pre=(g/'host_qa_v5.c').read_text().split('\n#ifdef HOST_QA\nint main(',1)[0]
atlas=(root/'tests/test_atlas_native.py').read_text()
route=atlas.split('static int route(',1)[1].split('static unsigned long signature',1)[0]
source=pre+'\n#include <assert.h>\n#include <stdio.h>\n#include <string.h>\nstatic int route('+route+r'''
static void test_real_world_shrines(void){
 static const int sx[5]={9,10,10,11,8},sy[5]={51,52,51,52,54};
 init_new_game();init_graphics();intro=0;game_mode=MODE_SURFACE;
 for(int idx=0;idx<5;idx++){
  int before=lc_party.count,shards=inv[ITEM_SHARD],cores=inv[ITEM_CORE];
  current_world=(u8)(idx+1);current_room=0;current_layer=1;
  generate_surface();
  assert(trigger[mi(ECO_SHRINE_X[idx],ECO_SHRINE_Y[idx])]==TR_ECO_SHRINE);
  assert(route(sx[idx],sy[idx],ECO_SHRINE_X[idx],ECO_SHRINE_Y[idx]));
  assert(trigger[mi(sx[idx],sy[idx])]==TR_SHIP);
  assert((lc_sanctuary_mask&(1u<<idx))==0);
  eco_shrine_interact();assert(lc_party.count==before);
  assert(inv[ITEM_SHARD]==shards&&inv[ITEM_CORE]==cores);
  if(idx==0)inv[ITEM_SHARD]=2;
  if(idx==1)story_flags|=ST_CHRONO;
  if(idx==2)cosmos.trust=160;/* nonconsumable compassion alternative */
  if(idx==3)story_flags|=ST_VOID;
  if(idx==4)keys_found=7;
  eco_shrine_interact();
  assert(lc_sanctuary_mask&(1u<<idx));assert(lc_party.count==before+1);
  assert(lc_party.slots[before].species==idx+1);
  assert(lc_party.slots[before].bond==70);
  assert(lc_party.active==before);
  assert(lc_party.slots[before].flags&4);
  {int c=lc_party.count,s=inv[ITEM_SHARD],q=inv[ITEM_CORE];
   eco_shrine_interact();assert(lc_party.count==c);
   assert(inv[ITEM_SHARD]==s && inv[ITEM_CORE]==q);}
  assert(SRAM[ARC_SRAM]=='A'&&SRAM[ARC_SRAM+19]==lc_sanctuary_mask);
 }
 assert(lc_party.count==5&&lc_sanctuary_mask==31);
 save_game();u8 low[238],roster[252];
 for(int i=0;i<238;i++)low[i]=SRAM[i];
 for(int i=0;i<252;i++)roster[i]=SRAM[LC_ROSTER_SRAM+i];
 init_new_game();load_game();assert(lc_sanctuary_mask==31&&lc_party.count==5);
 for(int i=0;i<5;i++)assert(lc_party.slots[i].species==i+1);
 for(int i=0;i<238;i++)assert(low[i]==SRAM[i]);
 for(int i=0;i<252;i++)assert(roster[i]==SRAM[LC_ROSTER_SRAM+i]);
 puts("PASS five PHYSICALLY REACHABLE world shrines preserve original ship/gates, require real relics/trust, do not grant before prerequisites, award distinct actual captured species with safe one-time transactions, persist across SAVE LOAD without changing legacy bytes");
}
static void test_story_guardians_and_release(void){
 u8 n=lc_party.count;
 assert(lc_recruit_mercy(EN_TIDE,0,8)==LC_OK);
 assert(lc_party.slots[n].species==6);
 assert(lc_recruit_mercy(EN_EMBER,0,9)==LC_OK);
 assert(lc_party.slots[n+1].species==7);
 assert(lc_recruit_mercy(EN_BLOOM,7,10)==LC_OK);
 assert(lc_party.slots[n+2].species==8);
 for(int i=6;i<=8;i++)assert(eco_capture_count(i)==1);
 for(int i=0;i<lc_party.count;i++){
  lc_party.slots[i].bond=90;
  assert(lc_reward_xp(&lc_party,(u8)i,60000)==LC_OK);
  assert(lc_evolve(&lc_party,(u8)i,1)==LC_OK);
  assert(lc_evolve(&lc_party,(u8)i,2)==LC_OK);
  assert(lc_party.slots[i].stage==2);
 }
 {u8 orig=lc_party.count;lc_party_sel=1;enter_pause();pause_page=18;
  update_pause(KEY_START);assert(lc_release_armed==1&&lc_party.count==orig);
  update_pause(KEY_START);assert(lc_release_armed==0&&lc_party.count==orig-1);
  assert(lc_party.slots[lc_party_sel].species!=2);}
 LcProfile prof={0};prof.family=1;prof.public_id=0x87431122u;prof.stats[0]=70;
 assert(lc_add_import(&lc_party,&prof,0x12340000u)==LC_OK);
 assert(lc_release_wild(&lc_party,(u8)(lc_party.count-1))==LC_NOT_READY);
 save_game();init_new_game();load_game();
 assert(lc_party.slots[lc_party.count-1].identity==prof.public_id);
 puts("PASS actual guardian recruit maps to distinct story animal species 6/7/8; all species reach actual 3-stage evolution; explicit two-press START release only wild, imported identity cannot be released");
}
static void test_old_atlas_migration_and_corruption(void){
 u8 old[238];for(int i=0;i<238;i++)old[i]=SRAM[i];
 /* V10.2 ARC2 used zero in byte19. Rechecksum a complete VALID old-style page. */
 u8 raw[32];for(int i=0;i<32;i++)raw[i]=SRAM[ARC_SRAM+i];raw[19]=0;
 u32 sum=lc_crc32(raw,28);for(int i=0;i<4;i++)raw[28+i]=(u8)(sum>>(8*i));
 for(int i=0;i<32;i++)SRAM[ARC_SRAM+i]=raw[i];
 arc_restore();assert(lc_sanctuary_mask==0);
 assert(lc_party.count>0);
 /* Even CRC-correct corrupted new mask cannot leak impossible sanctuary state. */
 raw[19]=255;sum=lc_crc32(raw,28);
 for(int i=0;i<4;i++)raw[28+i]=(u8)(sum>>(8*i));
 for(int i=0;i<32;i++)SRAM[ARC_SRAM+i]=raw[i];
 arc_restore();assert(lc_sanctuary_mask==0&&arc_progress==0);
 for(int i=0;i<238;i++)assert(old[i]==SRAM[i]);
 puts("PASS old V10.2 ARC2 CRC page migrates with 0 new sanctuary bits; impossible CRC-valid mask is rejected without changing original V10 legacy SRAM");
}
int main(void){test_real_world_shrines();test_story_guardians_and_release();test_old_atlas_migration_and_corruption();return 0;}
'''
(g/'ecology_native_host_qa.c').write_text(source)
subprocess.run(['clang','-DHOST_QA','-DQA_AUTORUN','-O2','-Wno-unused-function','ecology_native_host_qa.c','-o','ecology_native_host_qa'],cwd=g,check=True)
subprocess.run([str(g/'ecology_native_host_qa')],cwd=g,check=True,timeout=30)
