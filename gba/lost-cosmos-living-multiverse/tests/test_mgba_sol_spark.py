#!/usr/bin/env python3
"""Real GBA controller chat, Spark import, animation, audio and cold boot.
No memory writes, cheats, savestate loads or progress fixture injections.
"""
from pathlib import Path
import argparse,json,subprocess,sys,zlib
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];sys.path.insert(0,str(ROOT/'tools'))
from mgba import Mgba,sha256
from test_mgba_mailbox_import import wait,goto_index,ui_row
def run(rom,elf,out):
 out.mkdir(parents=True,exist_ok=True)
 js="""
 import fs from 'node:fs';import{buildGenome}from'./arcade/spark-beasts/genome.mjs';import{sparkRecord}from'./arcade/spark-beasts/trade.mjs';import{sparkSave}from'./arcade/sol-spark-gate/cartridge.mjs';
 const t=JSON.parse(fs.readFileSync('arcade/spark-beasts/data/quantum-runs.json'));const g=buildGenome({focus:65,calm:72,spark:48},t.runs[0],'CORY');const p=sparkRecord(g,0).profile;
 console.log(JSON.stringify({save:[...sparkSave(g,0,t)],id:p.publicId,seed:p.gameSeed,name:p.callsign}));
 """
 f=json.loads(subprocess.check_output(['node','--input-type=module','-e',js],cwd=REPO,text=True));starter=out/'SPARK_STARTER.sav';starter.write_bytes(bytes(f['save']))
 sav=out/'spark-play.sav';sav.write_bytes(starter.read_bytes())
 report=dict(suite='sol_spark_mgba',rom_sha256=sha256(rom),controller_only=True,memory_writes=False,savestates=False,passed=False)
 def party(e):
  e.tap('START',hold=12,release=12);goto_index(e,2);e.tap('A',hold=12,release=12);e.step((),20);assert e.read_symbol('pause_page')==18
 def roster(data):
  r=data[1024:1276];assert r[:4]==b'LCR1' and zlib.crc32(r[:248])==int.from_bytes(r[248:252],'little')
  matches=[r[8+i*20:28+i*20] for i in range(r[5]) if int.from_bytes(r[16+i*20:20+i*20],'little')==f['id']]
  assert len(matches)==1 and int.from_bytes(matches[0][12:16],'little')==f['seed'];return matches[0]
 with Mgba(rom,elf=elf,save_path=sav,trace_path=out/'controller_inputs.jsonl') as e:
  e.step((),180);e.tap('A',hold=12,release=12);wait(e,lambda:e.read_symbol('v10_opening')==1,'opening');e.tap('START',hold=12,release=12)
  wait(e,lambda:e.read_symbol('v10_opening')==0 and e.read_symbol('lc_mail_ready')==1,'Spark import');e.step((),20);party(e)
  assert f['name'] in ui_row(e,5+e.read_symbol('v11_sel')%5)
  wait(e,lambda:e.read_symbol('sol_spark_blink')==0,'open eyes');assert e.read_range(0x06010000+896*32,512)==bytes(f['save'][24960:25472]);e.screenshot(out/'01_spark_party.png')
  
  for _ in range(400):
   if e.read_symbol('sol_spark_blink')==1:break
   e.step((),1)
  assert e.read_symbol('sol_spark_blink')==1; assert e.read_range(0x06010000+896*32,512)!=bytes(f['save'][24960:25472]);report['blink_verified']=True
  e.tap('A',hold=12,release=12);assert e.read_symbol('pause_page')==27
  for _ in range(7):e.tap('DOWN',hold=8,release=8)
  assert e.read_symbol('v11_sel')==7;e.start_recording(out/'SPARK_CHAT.mp4');e.tap('A',hold=8,release=8);assert e.read_symbol('pause_page')==49;e.screenshot(out/'02_chat_keyboard.png')
  for _ in range(7):e.tap('RIGHT',hold=4,release=4)
  e.tap('A',hold=4,release=4);e.tap('RIGHT',hold=4,release=4);e.tap('A',hold=4,release=4)
  a=e.symbols['sol_chat_input'].address;assert e.read_range(a,3)==b'HI\0';e.tap('SELECT',hold=4,release=4);e.step((),120)
  assert 'HELLO ARIN' in ''.join(ui_row(e,r) for r in range(5,9));e.screenshot(out/'03_chat_reply.png');e.tap('B',hold=8,release=8);assert e.read_symbol('pause_page')==18
  e.tap('B',hold=8,release=8);e.tap('B',hold=8,release=8);e.step(('RIGHT',),90);e.step(('LEFT',),90);capture=e.stop_recording();assert capture['audio_nonzero_samples']>0
  report['audio']=capture;report['chat_verified']=True
  earned=e.export_save(out/'SPARK_JOURNEY.sav');p=roster(earned.read_bytes());report['level']=p[2];report['bond']=p[3]
  assert earned.read_bytes()[24704:24832]==starter.read_bytes()[24704:24832] and earned.read_bytes()[31744:]==starter.read_bytes()[31744:]
 with Mgba(rom,elf=elf,save_path=earned) as e:
  e.step((),180);assert e.read_symbol('v10_has_save')==1;e.tap('DOWN',hold=12,release=12);e.tap('A',hold=12,release=12);e.step((),600)
  p=roster(e.read_range(0x0e000000,8192));assert p[2]==report['level'] and p[3]==report['bond'];party(e)
  wait(e,lambda:e.read_symbol('sol_spark_blink')==0,'cold-boot open eyes');assert e.read_range(0x06010000+896*32,512)==bytes(f['save'][24960:25472]);e.screenshot(out/'04_cold_boot.png');report['cold_boot_verified']=True
 report['passed']=True;(out/'spark_report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--rom',type=Path,default=REPO/'arcade/lost-cosmos/rom/lost-cosmos.gba');a.add_argument('--elf',type=Path,default=ROOT/'LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.elf');a.add_argument('--out',type=Path,default=ROOT/'artifacts/sol-spark/controller');o=a.parse_args();run(o.rom,o.elf,o.out)
