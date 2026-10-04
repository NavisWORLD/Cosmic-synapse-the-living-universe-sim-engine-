#!/usr/bin/env python3
"""Native C art, real earned stages, input boundaries and sound registers.
Simulated MMIO unit checks are separate from controller-only mGBA acceptance.
"""
from pathlib import Path
import json,os,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'LOST_COSMOS_V10_SOURCE';REPO=ROOT.parents[1]
js="""
import fs from 'node:fs';import{buildGenome}from'./arcade/spark-beasts/genome.mjs';import{sparkRecord}from'./arcade/spark-beasts/trade.mjs';import{sparkSave,cartridgeSprite}from'./arcade/sol-spark-gate/cartridge.mjs';
const t=JSON.parse(fs.readFileSync('arcade/spark-beasts/data/quantum-runs.json'));const g=buildGenome({focus:65,calm:72,spark:48},t.runs[0],'CORY');const p=sparkRecord(g,0).profile;
console.log(JSON.stringify({id:p.publicId,seed:p.gameSeed,save:[...sparkSave(g,0,t)],forms:[1,2,3].map(s=>[...cartridgeSprite(g,s).tiles])}));
"""
f=json.loads(subprocess.check_output(['node','--input-type=module','-e',js],cwd=REPO,text=True))
subprocess.run(['python3','host_qa_v5.py'],cwd=GAME,check=True,capture_output=True)
pre=(GAME/'host_qa_v5.c').read_text().split('\n#ifdef HOST_QA\nint main(',1)[0]
arrays='static const u8 spark_save[32768]={'+','.join(map(str,f['save']))+'};\n'
for i,data in enumerate(f['forms']):arrays+=f'static const u8 form{i}[512]={{'+','.join(map(str,data))+'};\n'
body=r'''
#include <assert.h>
#include <stdio.h>
static void exact_form(const u8*expected){u8 old[32768];for(int i=0;i<32768;i++)old[i]=SRAM[i];
 sol_spark_clock=20;lc_mail_blit();for(int i=0;i<512;i++)if(lc_mail_tiles[i]!=expected[i]){fprintf(stderr,"art mismatch stage=%u blink=%u ok=%u at=%d actual=%u expected=%u\n",sol_spark_stage,sol_spark_blink,sol_spark_ok,i,lc_mail_tiles[i],expected[i]);abort();}for(int i=0;i<32768;i++)assert(old[i]==SRAM[i]);}
int main(void){
 for(int i=0;i<32768;i++)SRAM[i]=spark_save[i];init_graphics();init_new_game();intro=v10_opening=cinema_active=0;save_game();
 assert(sol_spark_valid());int ix=-1;for(int i=0;i<lc_party.count;i++)if(lc_party.slots[i].identity==SPK_ID)ix=i;assert(ix>=0);LcCreature*c=&lc_party.slots[ix];
 assert(c->seed==SPK_SEED&&c->stage==0);exact_form(form0);assert(lc_evolve(&lc_party,ix,1)==LC_NOT_READY);
 while(c->level<28)assert(lc_reward_xp(&lc_party,ix,65535)==LC_OK);while(c->bond<80)assert(lc_bond(&lc_party,ix,(c->species-128)%3,85)==LC_OK);
 assert(lc_evolve(&lc_party,ix,1)==LC_OK);exact_form(form1);assert(lc_evolve(&lc_party,ix,1)==LC_OK);exact_form(form2);
 sol_spark_clock=0;lc_mail_blit();int changed=0;for(int i=0;i<512;i++)if(lc_mail_tiles[i]!=form2[i])changed++;assert(changed>0);exact_form(form2);
 int moved=0;for(int i=0;i<120;i++){sol_spark_clock=i;moved|=sol_spark_offset(SPK_ID,0)!=0;assert(!sol_spark_offset(SPK_ID^1u,0));}assert(moved);
 save_game();lc_roster_init(&lc_party);load_game();assert(lc_party.slots[ix].stage==2&&lc_party.slots[ix].identity==SPK_ID);exact_form(form2);
 /* Select CHAT through the same native menu handler as a real controller. */
 pause_page=27;v11_page_previous=27;v11_assign=(u8)(ix+1);v11_sel=7;u16 xp=c->xp;u8 bond=c->bond,stage=c->stage;assert(v11_update_pause(KEY_A));assert(pause_page==49);
 for(int i=0;i<40;i++){sol_chat_letter=0;v11_update_pause(KEY_A);}assert(sol_chat_pos==31);v11_update_pause(KEY_L);assert(sol_chat_pos==30);
 sol_chat_open();sol_chat_letter=7;v11_update_pause(KEY_A);sol_chat_letter=8;v11_update_pause(KEY_A);assert(!strcmp(sol_chat_input,"HI"));v11_update_pause(KEY_SELECT);assert(strstr(sol_chat_reply,"HELLO ARIN"));
 assert(c->xp==xp&&c->bond==bond&&c->stage==stage);assert(sol_chat_pos==0);v11_draw_pause();v11_update_pause(KEY_B);assert(pause_page==18);
 assert(strstr(sol_chat_answer("EVOLVE",c),"FINAL FORM"));assert(!strcmp(sol_chat_answer("HELP",c),v11_signal_goal(v11_world())));
 audio_on=1;sol_spark_voice_notes=0;sol_spark_chirp(SPK_ID);sol_spark_sound_step();assert(REG_SOUND2CNT_H&0x8000);assert((REG_SOUND2CNT_H&2047)==(SRAM[24764]|(SRAM[24765]<<8)));
 audio_on=0;REG_SOUND2CNT_L=0;sol_spark_sound_step();assert(!sol_spark_voice_notes&&!REG_SOUND2CNT_L);sol_spark_chirp(SPK_ID);assert(!sol_spark_voice_notes);
 /* Malformed extra art safely falls back to the supplied first form. */
 SRAM[SOL_SPK_META+20]^=1;assert(!sol_spark_valid());exact_form(form0);
 puts("PASS: actual Spark art, earned native forms, blink/gait, identity isolation, save/load, controller chat, bounded typing and muted chirps");return 0;
}
'''
with tempfile.TemporaryDirectory(prefix='sol-spark-') as temp:
 p=Path(temp);(p/'test.c').write_text(pre+f'#define SPK_ID {f["id"]}u\n#define SPK_SEED {f["seed"]}u\n'+arrays+body)
 for imported in (False,True):
  cmd=[os.environ.get('LC_HOST_CC','gcc'),'-DQA_AUTORUN','-DHOST_QA','-O2','-I',str(GAME)]
  if imported:cmd.append('-DLC_IMPORTED_COMPANION')
  subprocess.run(cmd+[str(p/'test.c'),'-o',str(p/'test')],check=True);subprocess.run([str(p/'test')],check=True)
