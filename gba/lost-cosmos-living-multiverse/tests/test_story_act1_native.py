#!/usr/bin/env python3
"""Act I synapse road: flowers, befriend, evolution thresholds, rival, V11.2 migration."""
from pathlib import Path
import os, subprocess
R = Path(__file__).resolve().parents[1]
G = R / 'LOST_COSMOS_V10_SOURCE'
subprocess.run(['python3', 'host_qa_v5.py'], cwd=G, check=True, capture_output=True)
pre = (G / 'host_qa_v5.c').read_text().split('\n#ifdef HOST_QA\nint main(', 1)[0]
body = r'''
#include <assert.h>
#include <stdio.h>
static void fresh(void){init_new_game();intro=0;v10_opening=0;cinema_active=0;init_graphics();}
static int count_trigger(int id){int i,n=0;for(i=0;i<4096;i++)if(trigger[i]==id)n++;return n;}
int main(void){
 int before,i,w;LcCreature*c;u8 act,flags,wins,friends,phase;
 fresh();v11_enter(0);
 assert(v11_act>=1&&(v11_story_flags&V11_SF_INTRO));
 assert(count_trigger(TR_V11_LISTENER)==1&&count_trigger(TR_V11_RIVAL)==1);
 assert(map_read_tile(8,58)==T_FLOWER&&trigger[58*64+8]==0);
 assert(map_read_tile(58,18)==T_FLOWER&&map_read_tile(40,8)==T_FLOWER);
 assert(trigger[46*64+8]==TR_V11_LISTENER&&trigger[28*64+8]==TR_V11_RIVAL);
 for(w=0;w<8;w++){int counts[10]={0};v11_enter(w);
  for(i=0;i<4096;i++)if(trigger[i]>=110&&trigger[i]<=119)counts[trigger[i]-110]++;
  assert(counts[5]==4&&counts[7]==1&&counts[4]==1&&counts[3]==1&&counts[1]==1&&counts[2]==1);
  assert(counts[6]==(w==0||w==2||w==5||w==6?2:1));if(w==5)assert(counts[8]==3);
  assert(count_trigger(TR_V11_LISTENER)==1);
  assert(count_trigger(TR_V11_RIVAL)==(w==0));
 }
 fresh();v11_enter(0);before=lc_party.count;
 v11_wild_begin(0);assert(v11_wild&&!v11_wild_rival&&v11_wild_species==1);
 v11_wild_hp=1;assert(v11_story_befriend()==1);
 assert(lc_party.count==before+1);
 c=&lc_party.slots[lc_party.active];
 assert(c->bond==55&&c->level==1&&c->species>=1&&c->species<=8);
 assert(lc_evolve(&lc_party,lc_party.active,0)==LC_NOT_READY);
 for(i=0;i<80&&c->level<12;i++)assert(lc_reward_xp(&lc_party,lc_party.active,1000)==LC_OK);
 assert(c->level>=12&&c->bond>=55);
 assert(lc_evolve(&lc_party,lc_party.active,0)==LC_OK&&c->stage==1);
 for(i=0;i<400&&c->level<28;i++)assert(lc_reward_xp(&lc_party,lc_party.active,1000)==LC_OK);
 assert(c->level>=28);c->bond=79;
 assert(lc_evolve(&lc_party,lc_party.active,0)==LC_NOT_READY&&c->stage==1);
 c->bond=80;assert(lc_evolve(&lc_party,lc_party.active,0)==LC_OK&&c->stage==2);
 v11_wild_begin(1);assert(v11_wild_rival&&v11_wild_species==5);
 v11_wild_hp=1;v11_wild_strike(0);
 assert((v11_story_flags&V11_SF_RIVAL)&&v11_rival_phase==2&&v11_act>=3&&v11_spark_wins>=1);
 act=v11_act;flags=v11_story_flags;wins=v11_spark_wins;friends=v11_befriend_count;phase=v11_rival_phase;
 v11_save();v11_act=0;v11_story_flags=0;v11_spark_wins=0;v11_befriend_count=0;v11_rival_phase=0;
 v11_restore();
 assert(v11_act==act&&v11_story_flags==flags&&v11_spark_wins==wins);
 assert(v11_befriend_count==friends&&v11_rival_phase==phase);
 /* A V11.2 page stored zeros in the story bytes. Beacons still advance the act. */
 fresh();v11_enter(0);v11_visited=255;v11_beacons=255;v11_act=0;v11_story_flags=0;v11_save();
 v11_act=0;v11_story_flags=0;v11_beacons=0;v11_restore();
 assert(v11_beacons==255&&v11_act>=4&&(v11_story_flags&V11_SF_EIGHT));
 v11_act=5;v11_story_flags=0;v11_beacons=0;v11_boss_done=0;v11_story_sync();assert(v11_act==5);
 puts("PASS Act I flowers, befriend, evolution, rival, and V11.2 story migration");
 return 0;
}
'''
src = G / 'content_v11_story_test_host.c'
src.write_text(pre + body)
exe = G / 'content_v11_story_test_host'
cc = os.environ.get('LC_HOST_CC', 'gcc')
subprocess.run([cc, '-DQA_AUTORUN', '-DHOST_QA', '-O2', '-Wno-unused-function',
                str(src), '-o', str(exe)], check=True)
subprocess.run([str(exe)], check=True)
