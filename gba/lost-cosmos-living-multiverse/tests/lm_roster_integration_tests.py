"""Real author V10 C integration checks using the repo's same host-mapped MMIO harness.
NOT a controller-driven mGBA or iPhone QA replacement.
"""
from pathlib import Path
import subprocess
r=Path(__file__).resolve().parents[1]/'LOST_COSMOS_V10_SOURCE'
s=(r/'host_qa_v5.c').read_text().split('\n#ifdef HOST_QA\nint main(',1)[0]
s+='''
#include <assert.h>
#include <stdio.h>
int main(void){
 unsigned i;u8 original[238];
 init_new_game();init_graphics();game_mode=MODE_SURFACE;intro=0;
 assert(lc_party.count==0);
 spawn_enemy(0,21,21,EN_EMBER,0);
 enemies[0].hp=1;
 v9_bond(&enemies[0]);
 assert(v9_bonded==1&&enemies[0].active==0);
 assert(lc_party.count==1&&lc_party.slots[0].bond==65);
 assert(lc_party.slots[0].species==1); /* V10.3 correct Ember biome mapping, unlike original V10.1 mismatch */
 assert(SRAM[LC_ROSTER_SRAM]=='L' && SRAM[LC_ROSTER_SRAM+1]=='C');
 for(i=1;i<12;i++){
  frame=(u16)(100+i*13);v9_rng+=(u32)(i*10007);
  spawn_enemy(0,15+(int)i,20+(int)i,(u8)(i%EN_COUNT),0);
  enemies[0].hp=1;v9_bond(&enemies[0]);
  assert(lc_party.count==i+1&&lc_party.active==i);
 }
 frame+=7;spawn_enemy(0,27,27,EN_VOID,0);enemies[0].hp=1;
 v9_bond(&enemies[0]);
 assert(lc_party.count==12&&enemies[0].active==1); /* never silently overwrite */
 lc_party.active=0;u8 lvl=lc_party.slots[0].level;
 add_xp(40);assert(lc_party.slots[0].level>=lvl);
 for(i=0;i<30;i++)lc_reward_xp(&lc_party,0,2500);
 assert(lc_party.slots[0].level>=28);
 assert(lc_evolve(&lc_party,0,1)==LC_OK);
 assert(lc_party.slots[0].stage==1);
 lc_party.slots[0].bond=85;
 assert(lc_evolve(&lc_party,0,3)==LC_OK);
 assert(lc_party.slots[0].stage==2);
 save_game();for(i=0;i<238;i++)original[i]=SRAM[i];
 init_new_game();load_game();
 assert(lc_party.count==12&&lc_party.active==0&&lc_party.slots[0].stage==2);
 for(i=0;i<238;i++)assert(SRAM[i]==original[i]);
 /* Corrupted NEW 252B page must not erase already validated original V10 save. */
 SRAM[LC_ROSTER_SRAM+12]^=0xff;
 init_new_game();load_game();
 assert(save_valid()&&v9_bonded==1);
 assert(lc_party.count==1&&lc_party.slots[0].bond==65); /* V9 fallback */
 for(i=0;i<238;i++)assert(SRAM[i]==original[i]);
 puts("PASS V10.1: native V9 capture ->12-slot roster -> cap -> stat-linked XP -> stage2 evolution -> independent CRC save restore; corrupted roster preserves original story SRAM and migrates original bonded beast");
 return 0;
}
'''
(r/'lm_roster_host_qa.c').write_text(s)
subprocess.run(['clang','-DHOST_QA','-O2','-Wno-unused-function','lm_roster_host_qa.c','-o','lm_roster_host_qa'],cwd=r,check=True)
subprocess.run([str(r/'lm_roster_host_qa')],cwd=r,check=True,timeout=20)
