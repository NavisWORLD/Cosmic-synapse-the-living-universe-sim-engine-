#!/usr/bin/env python3
"""TRUE libmGBA controller Act II from an independently controller-earned Act I save.
No emulated memory writes, injected story flags, or savestates. Separate real
second cold boot verifies Sentinel + Wisdom/Courage/Unity SRAM persistence.
"""
import argparse
import json
import shutil
from pathlib import Path
import sys
import traceback
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from mgba import Mgba, sha256
from mgba_navigate import Navigator

ROOT=Path(__file__).resolve().parents[1]

def run(rom,elf,act1,out):
 out.mkdir(parents=True,exist_ok=True)
 previous=json.loads((act1/"act1_controller_report.json").read_text())
 cold=json.loads((act1/"act1_second_boot_report.json").read_text())
 if (not previous["passed"] or previous["rom_sha256"]!=sha256(rom) or
     previous["completed_stages"][-1]["stage"]!="08_real_First_Heart" or
     not cold["passed"] or cold["rom_sha256"]!=sha256(rom)):
  raise RuntimeError("Require REAL matching-ROM controller Act I + true cold-boot evidence")
 save=out/"act2_real_controller.sav"
 shutil.copy2(act1/"act1_fresh.sav",save)  # Preserve previous Act I save intact.
 report={"suite":"real_mgba_act2_controller_with_two_cold_boots",
         "rom_sha256":sha256(rom),"elf_sha256":sha256(elf),
         "source_ActI_save_sha256":sha256(act1/"act1_fresh.sav"),
         "controller_only":True,"memory_writes":False,"savestates":False,
         "stages":[],"passed":False,"cold_boot_passed":False}
 with Mgba(rom,elf=elf,save_path=save,trace_path=out/"act2_controller_inputs.jsonl") as emu:
  def wait(pred,label,max_frames=1600):
   for _ in range((max_frames+7)//8):
    if pred():return
    emu.step((),8)
   raise RuntimeError("Actual "+label+" not reached using real controller")
  def mark(name):
   emu.screenshot(out/(name+".png"))
   s={"name":name,"frame":emu.frame,"world":emu.read_symbol("current_world"),
      "room":emu.read_symbol("current_room"),"story_flags":emu.read_symbol("story_flags")}
   report["stages"].append(s);print("REAL_ACT2",s,flush=True)
  try:
   emu.step((),180)
   if emu.read_symbol("intro")!=1 or emu.read_symbol("v10_has_save")!=1:
    raise RuntimeError("Real first cold boot failed to recognize earned Act I SRAM")
   emu.tap("DOWN",hold=12,release=12)
   if emu.read_symbol("v10_title_sel")!=1:raise RuntimeError("Cannot select CONTINUE")
   emu.tap("A",hold=12,release=12)
   wait(emu,lambda:False,"noop") if False else None
   wait(lambda:emu.read_symbol("intro")==0 and emu.read_symbol("current_room")==4,"Cragstone continue")
   emu.step((),30)
   if emu.read_symbol("story_flags")&31!=31:raise RuntimeError("Act I real flags not present")
   nav=Navigator(emu);mark("01_ActI_sram_genuinely_reused")
   nav.interact(12,at=(32,55))
   if nav.location()!=(0,3,1):raise RuntimeError("Cragstone->Oakwood real route failed")
   emu.step((),25);mark("02_return_to_Oakwood")
   nav.interact(12,at=(8,54))
   if nav.location()!=(0,2,1):raise RuntimeError("Oakwood->Brindlemark real route failed")
   emu.step((),25);mark("03_return_to_Brindlemark")
   nav.interact(12,at=(52,12))
   if nav.location()!=(0,5,1):raise RuntimeError("Brindlemark->Hidden City real route failed")
   wait(lambda:emu.read_symbol("npc_count")>0 and any(n.id==18 for n in nav.npcs()),"White Sentinel rendered")
   emu.step((),12);mark("04_Hidden_City")
   nav.talk_npc(18,advances=6)
   wait(lambda:bool(emu.read_symbol("story_flags")&2048),"earned White Sentinel ST_CITY")
   mark("05_White_Sentinel_story")
   emu.step((),180)
   nav.interact(12,at=(54,10))
   wait(lambda:emu.read_symbol("current_world")==6,"Dream Veil entry")
   emu.step((),360);nav.wait_cinema()
   if nav.location()!=(6,0,1):raise RuntimeError("Dream Veil wrong native map")
   mark("06_Dream_Veil")
   nav.interact(18,at=(15,17))
   if not emu.read_symbol("riddle_open"):raise RuntimeError("Wisdom puzzle not engaged")
   emu.tap("RIGHT",hold=12,release=12)
   if not emu.read_symbol("story_flags")&128:raise RuntimeError("Wisdom not earned")
   mark("07_real_Wisdom")
   nav.fight_enemy(7)
   if not emu.read_symbol("story_flags")&256:raise RuntimeError("Real Courage boss not defeated")
   mark("08_real_Courage_guardian")
   nav.interact(20,at=(49,17))
   if not emu.read_symbol("story_flags")&512:raise RuntimeError("Unity not earned")
   mark("09_real_Unity")
   emu.step((),180)  # Full native dual-bank SRAM transaction, not presumed synchronous.
   if emu.read_symbol("story_flags")&0x0b9f!=0x0b9f:
    raise RuntimeError("Final native story bitset missing earned Act I/II milestone")
   report["passed"]=True
  except Exception as error:
   report["failure"]=repr(error);report["traceback"]=traceback.format_exc()
   try:emu.screenshot(out/"FAILED_TRUE_ACT2_FRAME.png")
   except Exception:pass
  finally:
   report["end_frame"]=emu.frame
   (out/"act2_controller_report.json").write_text(json.dumps(report,indent=2)+"\n")
 if not report["passed"]:raise RuntimeError(report["failure"])
 # This is a genuinely NEW emulator instance reading the prior battery file.
 with Mgba(rom,elf=elf,save_path=save,trace_path=out/"act2_second_boot_inputs.jsonl") as emu:
  emu.step((),180)
  if emu.read_symbol("intro")!=1 or emu.read_symbol("v10_has_save")!=1:
   raise RuntimeError("Genuine second cold boot lost ACT II earned save")
  emu.screenshot(out/"10_real_ActII_second_cold_title.png")
  emu.tap("DOWN",hold=12,release=12);emu.tap("A",hold=12,release=12)
  for _ in range(180):
   if emu.read_symbol("intro")==0 and emu.read_symbol("current_world")==6:break
   emu.step((),8)
  else:raise RuntimeError("Act II real battery didn't restore actual Dream world")
  emu.step((),20)
  flags=emu.read_symbol("story_flags")
  if flags&0x0b9f!=0x0b9f:raise RuntimeError("Actual second cold boot lost Sentinel or 3 Dream trials")
  report["second_boot"]={"world":emu.read_symbol("current_world"),
    "room":emu.read_symbol("current_room"),"story_flags":flags,"frame":emu.frame}
  emu.screenshot(out/"11_real_ActII_Dream_restored.png")
  report["cold_boot_passed"]=True
 (out/"act2_controller_report.json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps({"passed":True,"second_boot":report["second_boot"],"stages":report["stages"]},indent=2))

if __name__=="__main__":
 parser=argparse.ArgumentParser()
 parser.add_argument("--rom",type=Path,default=ROOT/"LOST_COSMOS_V10_SOURCE/LOST_COSMOS_V10_OPENING_QA.gba")
 parser.add_argument("--elf",type=Path,default=ROOT/"LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.elf")
 parser.add_argument("--act1",type=Path,default=ROOT/"artifacts/mgba_act1")
 parser.add_argument("--out",type=Path,default=ROOT/"artifacts/mgba_act2")
 args=parser.parse_args();run(args.rom.resolve(),args.elf.resolve(),args.act1.resolve(),args.out.resolve())
