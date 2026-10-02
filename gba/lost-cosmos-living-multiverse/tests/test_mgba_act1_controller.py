#!/usr/bin/env python3
"""Real controller-only native Act I route: Brindlemark -> Oakwood -> Cragstone.
Never writes emulated state, forces quest flags, loads savestates or teleports.
Actual screenshots and input trace are retained even on a genuine failure.
This is a partial Act I test, NOT full Malakar/Heart or five-act acceptance.
"""
import argparse
import json
from pathlib import Path
import sys
import traceback
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from mgba import Mgba,sha256
from mgba_navigate import Navigator

R=Path(__file__).resolve().parents[1]
def wait(emu,predicate,what,max_frames=750):
 for _ in range((max_frames+7)//8):
  if predicate():return
  emu.step((),8)
 raise RuntimeError(f"{what} not reached after {max_frames} frames")

def run(rom,elf,out):
 out.mkdir(parents=True,exist_ok=True)
 save=out/"act1_fresh.sav"
 if save.exists():save.unlink()
 report={"suite":"real_mgba_controller_act1","rom_sha256":sha256(rom),
         "elf_sha256":sha256(elf),"controller_only":True,"state_writes":False,
         "completed_stages":[],"partial_scope":True,"full_five_acts":False}
 with Mgba(rom,elf=elf,save_path=save,trace_path=out/"actual_act1_inputs.jsonl",watch_symbol="frame") as emu:
  def mark(name):
   emu.screenshot(out/(name+".png"))
   report["completed_stages"].append({"stage":name,"frame":emu.frame,
      "world":emu.read_symbol("current_world"),"room":emu.read_symbol("current_room"),
      "story_flags":emu.read_symbol("story_flags"),"position":
       [emu.read_symbol("player",width=2,signed=True),emu.read_symbol("player",width=2,offset=2,signed=True)]
       if "player" in emu.symbols else None})
  try:
   emu.step((),180)
   if emu.read_symbol("intro")!=1:raise RuntimeError("Real mGBA title missing")
   emu.tap("A",hold=12,release=12)
   wait(emu,lambda:emu.read_symbol("v10_opening")==1,"actual opening")
   # Legitimate documented START input skips the visual prologue, not story flags.
   emu.tap("START",hold=12,release=12)
   wait(emu,lambda:emu.read_symbol("v10_opening")==0 and emu.read_symbol("current_room")==2,"Brindlemark arrival")
   nav=Navigator(emu)
   mark("01_true_brindlemark")
   nav.talk_npc(14,advances=3)       # Real village elder with actual NPC dialogue.
   if not emu.read_symbol("story_flags")&1:raise RuntimeError("Brindle elder failed to unlock ST_TOWN")
   mark("02_earned_village_quest")
   nav.interact(12,at=(54,8))       # Real northeast gate to Oakwood.
   if nav.location()!=(0,3,1):raise RuntimeError("Real Oakwood gate did not change map")
   mark("03_true_oakwood")
   nav.talk_npc(16,advances=3)      # Ravenswood's actual real three-page conversation.
   if not emu.read_symbol("story_flags")&2:raise RuntimeError("Ravenswood did not earn ST_OAKWOOD")
   mark("04_earned_ravenswood_map")
   nav.interact(12,at=(54,12))     # Authored Oakwood -> Cragstone route, no forced warp.
   if nav.location()!=(0,4,1):raise RuntimeError("Cragstone remained locked despite earned map")
   mark("05_true_cragstone")
   # Actual native rune locations, original source canonical SKY/ROOT/HEART/STAR order:
   for code,pos in [(15,(35,22)),(13,(21,22)),(16,(42,22)),(14,(28,22))]:
    nav.interact(code,at=pos)
   if not emu.read_symbol("story_flags")&4:raise RuntimeError("Four separate real runes did not earn ST_PUZZLE")
   mark("06_real_four_seal_puzzle")
   report["passed"]=True
  except Exception as exc:
   report["passed"]=False
   report["failure"]=repr(exc)
   report["traceback"]=traceback.format_exc()
   try:emu.screenshot(out/"FAILED_TRUE_FRAME.png")
   except Exception:pass
   raise
  finally:
   report["last_frame"]=emu.frame
   (out/"act1_controller_report.json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps({"passed":report["passed"],"stages":report["completed_stages"],
                  "scope":"true Act I opening route to real four-seal unlock, NOT Malakar boss yet"},indent=2))

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--rom",type=Path,default=R/"LOST_COSMOS_V10_SOURCE/LOST_COSMOS_V10_OPENING_QA.gba")
 p.add_argument("--elf",type=Path,default=R/"LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.elf")
 p.add_argument("--out",type=Path,default=R/"artifacts/mgba_act1")
 a=p.parse_args();run(a.rom.resolve(),a.elf.resolve(),a.out.resolve())
