#!/usr/bin/env python3
"""REAL mGBA Hollow Grove from prior actually earned Eldoria controller save.
Physically walk the newly accessible forest, solve actual mirror riddle,
defeat the real Hollow Wraith through native player battle controls, claim
the Earth crystal, and prove a wholly separate fresh-emulator battery reload.
No emulated game memory edits, fictional fixture saves, savestate loads,
or proof of unfinished later acts/three complete endings.
"""
import argparse
import json
import shutil
import sys
import traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mgba import Mgba,sha256
from mgba_navigate import Navigator

def run(rom,elf,eldoria,out):
 out.mkdir(parents=True,exist_ok=True)
 prev=json.loads((eldoria/"eldoria_controller_report.json").read_text())
 source=eldoria/"eldoria_real_controller.sav"
 if not prev.get("passed") or not prev.get("cold_boot_passed") or prev.get("rom_sha256")!=sha256(rom) or not source.is_file():
  raise RuntimeError("Identical-ROM genuine controller-earned Eldoria real battery AND second cold boot required")
 save=out/"actual_hollow_grove.sav"
 shutil.copy2(source,save)
 report={"suite":"real_mgba_original_hollow_grove",
         "rom_sha256":sha256(rom),"elf_sha256":sha256(elf),
         "source_earned_Eldoria_battery":sha256(source),
         "controller_only":True,"game_memory_writes":False,"savestates":False,
         "passed":False,"cold_boot_passed":False,"stages":[]}
 with Mgba(rom,elf=elf,save_path=save,trace_path=out/"real_Hollow_Grove_inputs.jsonl") as emu:
  def wait(pred,label,limit=1400):
   for _ in range((limit+7)//8):
    if pred():return
    emu.step((),8)
   raise RuntimeError("Actual GBA "+label+" missing after "+str(limit)+" frames")
  def mark(name):
   emu.screenshot(out/(name+".png"))
   point={"name":name,"frame":emu.frame,"world":emu.read_symbol("current_world"),
          "room":emu.read_symbol("current_room"),"story_flags":emu.read_symbol("story_flags"),
          "relic_flags":emu.read_symbol("v10_relic"),"real_kills":emu.read_symbol("kill_count")}
   report["stages"].append(point)
   print("GENUINE_GROVE",point,flush=True)
  try:
   emu.step((),180)
   if emu.read_symbol("intro")!=1 or emu.read_symbol("v10_has_save")!=1:
    raise RuntimeError("Real Eldoria battery not recognized in fresh emulator")
   emu.tap("DOWN",hold=12,release=12);emu.tap("A",hold=12,release=12)
   wait(lambda:emu.read_symbol("intro")==0 and emu.read_symbol("current_world")==7,
        "genuine old Eldoria CONTINUE")
   emu.step((),32)
   if emu.read_symbol("element_mask")!=15:
    raise RuntimeError("Cannot inherit a fabricated or incomplete elemental trial")
   nav=Navigator(emu)
   mark("01_actual_all_elements_Eldoria")
   nav.interact(12,at=(54,36))
   wait(lambda:nav.location()==(7,10,1),"original Hollow Grove destination")
   # Old 32KB atomic battery write causes the room ID to become visible
   # several emulated frames before generate_surface() finishes. Never
   # confuse a legitimate intermediate blank map with a missing trigger.
   wait(lambda:nav.triggers()[32*64+13]==35,
        "fully constructed, interactive actual Hollow Grove map")
   emu.step((),12);mark("02_true_Hollow_Grove")
   nav.interact(35,at=(13,32))
   if emu.read_symbol("v10_realm_riddle")!=2:
    raise RuntimeError("Actual reflection interaction failed")
   emu.tap("LEFT",hold=12,release=12)
   if not (emu.read_symbol("v10_relic")&128):
    raise RuntimeError("Player riddle did not earn RF_GROVE_RIDDLE")
   mark("03_original_reflection")
   before=emu.read_symbol("kill_count")
   nav.interact(36,at=(48,32))
   if emu.read_symbol("game_mode")!=3:
    raise RuntimeError("Real Hollow Wraith tactical fight did not open")
   nav.battle(max_frames=36000)
   if not (emu.read_symbol("v10_relic")&256) or emu.read_symbol("kill_count")<=before:
    raise RuntimeError("Controller-driven real Hollow Wraith not defeated")
   mark("04_real_Hollow_Wraith")
   nav.interact(37,at=(32,12))
   if not (emu.read_symbol("v10_relic")&512):
    raise RuntimeError("Actual earned Earth Crystal not obtained")
   mark("05_actual_Earth_recovered")
   emu.step((),210)  # Let the actual 32KiB native CRC transaction complete.
   report["passed"]=True
  except Exception as error:
   report["failure"]=repr(error);report["traceback"]=traceback.format_exc()
   try:emu.screenshot(out/"FAILED_REAL_GROVE_FRAME.png")
   except Exception:pass
  finally:
   report["end_frame"]=emu.frame
   (out/"Hollow_Grove_report.json").write_text(json.dumps(report,indent=2)+"\n")
 if not report["passed"]:raise RuntimeError(report["failure"])
 # No savestate: NEW libmGBA instance reopening that genuinely earned battery.
 with Mgba(rom,elf=elf,save_path=save,trace_path=out/"second_cold_boot_inputs.jsonl") as emu:
  emu.step((),180)
  if emu.read_symbol("intro")!=1 or emu.read_symbol("v10_has_save")!=1:
   raise RuntimeError("Second full emulator restart lost battery")
  emu.screenshot(out/"06_real_grove_second_boot_title.png")
  emu.tap("DOWN",hold=12,release=12);emu.tap("A",hold=12,release=12)
  for _ in range(175):
   if emu.read_symbol("intro")==0 and emu.read_symbol("current_room")==10:break
   emu.step((),8)
  else:raise RuntimeError("Actual second controller CONTINUE did not restore Hollow Grove")
  emu.step((),48)
  if len(set(emu.rgb()[i:i+3] for i in range(0,240*160*3,3)))<8:
   raise RuntimeError("Hollow Grove CONTINUE restored state but framebuffer stayed blank")
  restored={"world":emu.read_symbol("current_world"),
            "room":emu.read_symbol("current_room"),
            "relic_flags":emu.read_symbol("v10_relic"),
            "story_flags":emu.read_symbol("story_flags"),
            "actual_enemy_kills":emu.read_symbol("kill_count")}
  if (restored["world"]!=7 or restored["room"]!=10 or
      restored["relic_flags"]&896!=896 or
      restored["story_flags"]&3999!=3999 or restored["actual_enemy_kills"]<1):
   raise RuntimeError("Real independent second cold boot lost earned Grove progress")
  emu.screenshot(out/"07_real_earned_Earth_restored.png")
  report["restored"]=restored
  report["cold_boot_passed"]=True
 (out/"Hollow_Grove_report.json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps({"passed":True,"second_cold_boot":report["restored"],"stages":report["stages"]},indent=2))

if __name__=="__main__":
 ap=argparse.ArgumentParser()
 ap.add_argument("--rom",type=Path,default=ROOT/"LOST_COSMOS_V10_SOURCE/LOST_COSMOS_V10_OPENING_QA.gba")
 ap.add_argument("--elf",type=Path,default=ROOT/"LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.elf")
 ap.add_argument("--eldoria",type=Path,default=ROOT/"artifacts/mgba_eldoria")
 ap.add_argument("--out",type=Path,default=ROOT/"artifacts/mgba_grove")
 a=ap.parse_args();run(a.rom.resolve(),a.elf.resolve(),a.eldoria.resolve(),a.out.resolve())
