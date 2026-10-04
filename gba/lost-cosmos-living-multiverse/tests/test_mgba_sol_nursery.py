#!/usr/bin/env python3
"""Real controller-only Sol import, exact custom sprite and cold-boot identity."""
from pathlib import Path
import argparse,json,subprocess,sys,zlib
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];sys.path.insert(0,str(ROOT/'tools'))
from mgba import Mgba,sha256
from test_mgba_mailbox_import import wait,goto_index,ui_row
def run(rom,elf,out):
 out.mkdir(parents=True,exist_ok=True)
 js="""
 import fs from 'node:fs';import{createBeast,exportSave,publicReceipt}from'./arcade/sol-beast-lab/design.mjs';
 const a=new Uint8Array(JSON.parse(fs.readFileSync('arcade/sol-beast-lab/archive.json')).bytes);
 const b=createBeast({island:0,nonce:'CORY-SOL-001',focus:65,calm:72,spark:48},a);
 console.log(JSON.stringify({save:[...exportSave(b)],id:b.publicId,seed:b.gameSeed,bond:b.bond,species:b.species,callsign:b.callsign,receipt:publicReceipt(b)}));
 """
 f=json.loads(subprocess.check_output(['node','--input-type=module','-e',js],cwd=REPO,text=True));starter=out/'sol_starter.sav';starter.write_bytes(bytes(f['save']))
 sav=out/'sol_import.sav';sav.write_bytes(starter.read_bytes())
 (out/'companion_receipt.json').write_text(json.dumps(f['receipt'],indent=2)+'\n')
 report=dict(suite='sol_nursery_mgba',rom_sha256=sha256(rom),controller_only=True,memory_writes=False,savestates=False,passed=False)
 def roster(data):
  r=data[1024:1276];assert r[:4]==b'LCR1' and zlib.crc32(r[:248])==int.from_bytes(r[248:252],'little')
  entries=[r[8+i*20:28+i*20] for i in range(r[5])];matches=[p for p in entries if int.from_bytes(p[8:12],'little')==f['id']]
  assert len(matches)==1 and matches[0][0]==f['species'] and int.from_bytes(matches[0][12:16],'little')==f['seed'];return len(entries),matches[0]
 with Mgba(rom,elf=elf,save_path=sav,trace_path=out/'controller_inputs.jsonl') as e:
  e.step((),180);e.tap('A',hold=12,release=12);wait(e,lambda:e.read_symbol('v10_opening')==1,'opening');e.tap('START',hold=12,release=12)
  wait(e,lambda:e.read_symbol('v10_opening')==0 and e.read_symbol('lc_mail_ready')==1,'Sol import');e.step((),20)
  e.tap('START',hold=12,release=12);goto_index(e,2);e.tap('A',hold=12,release=12);e.step((),20)
  assert e.read_symbol('pause_page')==18
  assert f['callsign'] in ui_row(e,5+e.read_symbol('v11_sel')%5)
  expected=bytes(f['save'][24960:25472])
  assert e.read_range(0x06010000+896*32,512)==expected
  e.screenshot(out/'01_sol_party.png')
  earned=e.export_save(out/'sol_earned.sav');count,creature=roster(earned.read_bytes())
  assert creature[3]==f['bond']
  report['bond']=creature[3];report['party_count']=count
 with Mgba(rom,elf=elf,save_path=earned) as e:
  e.step((),180);assert e.read_symbol('v10_has_save')==1;e.tap('DOWN',hold=12,release=12);e.tap('A',hold=12,release=12);e.step((),600)
  count,creature=roster(e.read_range(0x0e000000,8192));assert count==report['party_count'] and creature[3]==report['bond']
  e.tap('START',hold=12,release=12);goto_index(e,2);e.tap('A',hold=12,release=12);e.step((),20)
  assert e.read_range(0x06010000+896*32,512)==expected;e.screenshot(out/'03_sol_cold_boot.png')
  report['cold_boot_verified']=True;report['passed']=True
 (out/'sol_nursery_report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--rom',type=Path,default=ROOT/'LOST_COSMOS_V10_SOURCE/LOST_COSMOS_V10_OPENING_QA.gba');a.add_argument('--elf',type=Path,default=ROOT/'LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.elf');a.add_argument('--out',type=Path,default=ROOT/'artifacts/sol/nursery');o=a.parse_args();run(o.rom,o.elf,o.out)
