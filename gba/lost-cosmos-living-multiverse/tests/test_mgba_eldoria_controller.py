#!/usr/bin/env python3
"""TRUE native libmGBA continuation from actually controller-earned Act II SRAM.
Input-only flight to Eldoria, physical 4 shrine interactions, actual Storm
Guardian combat and independent second cold boot. NO memory writes/savestates.
This is an ACT III ENTRY test, NOT a completed full novel or all Acts III-V.
"""
import argparse
import json
import shutil
from pathlib import Path
import sys
import traceback
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from mgba import Mgba,sha256
from mgba_navigate import Navigator

R=Path(__file__).resolve().parents[1]

def run(rom,elf,act2,out):
 out.mkdir(parents=True,exist_ok=True)
 previous=json.loads((act2/"act2_controller_report.json").read_text())
 earlier=act2/"act2_real_controller.sav"
 if (not previous["passed"] or not previous["cold_boot_passed"] or
     previous["rom_sha256"]!=sha256(rom) or not earlier.is_file()):
  raise RuntimeError("Genuine same-ROM Act II two-cold-boot save required; no fixtures accepted")
 save=out/"eldoria_real_controller.sav"
 shutil.copy2(earlier,save)  # Never alter previous real progression battery.
 report={"suite":"actual_mGBA_Eldoria_four_element_entry",
         "rom_sha256":sha256(rom),"elf_sha256":sha256(elf),
         "earned_ActII_save_sha256":sha256(earlier),"memory_writes":False,
         "savestates":False,"controller_only":True,"stages":[],"passed":False,
         "cold_boot_passed":False,"partial_scope":True}
 with Mgba(rom,elf=elf,save_path=save,trace_path=out/"eldoria_actual_inputs.jsonl") as emu:
  def wait(pred,label,max_frames=1600):
   for _ in range((max_frames+7)//8):
    if pred():return
    emu.step((),8)
   raise RuntimeError("Real "+label+" wasn't earned with actual input")
  def mark(name):
   emu.screenshot(out/(name+".png"))
   s={"name":name,"frame":emu.frame,"world":emu.read_symbol("current_world"),
      "room":emu.read_symbol("current_room"),"story_flags":emu.read_symbol("story_flags"),
      "element_mask":emu.read_symbol("element_mask")}
   report["stages"].append(s)
   print("REAL_ELDORIA",s,flush=True)
  try:
   emu.step((),180)
   if emu.read_symbol("intro")!=1 or emu.read_symbol("v10_has_save")!=1:
    raise RuntimeError("Genuine prior SRAM not found")
   emu.tap("DOWN",hold=12,release=12);emu.tap("A",hold=12,release=12)
   wait(lambda:emu.read_symbol("intro")==0 and emu.read_symbol("current_world")==6,
        "genuine Dream Veil restore")
   emu.step((),20);nav=Navigator(emu)
   if not emu.read_symbol("story_flags")&512:raise RuntimeError("Dream Unity unearned")
   mark("01_real_prior_Dream_save")
   nav.goto_trigger(1,at=(10,53));nav.board_ship()
   if emu.read_symbol("game_mode")!=1 or emu.read_symbol("cinema_active"):
    raise RuntimeError("Actual LUNA-ARC warp did not finish in playable space")
   emu.step((),8)
   if len(set(emu.rgb()[i:i+3] for i in range(0,240*160*3,3)))<6:
    raise RuntimeError("LUNA-ARC entered space state but framebuffer stayed blank")
   mark("02_actual_LUNA_ARC_flight")
   nav.fly_to(7)
   wait(lambda:nav.location()==(7,0,1),"real Eldoria landing")
   emu.step((),360);nav.wait_cinema()
   mark("03_real_Eldoria_land")
   nav.talk_npc(20,advances=3)
   mark("04_real_Thorne_dialogue")
   for index,tile in enumerate(((15,17),(26,17),(37,17))):
    nav.goto_trigger(21,at=tile)
    before_diag={
     "near_trigger_x":emu.read_symbol("near_trigger_x"),
     "near_trigger_y":emu.read_symbol("near_trigger_y"),
     "last_element_trigger_x":emu.read_symbol("last_element_trigger_x"),
     "last_element_index":emu.read_symbol("last_element_index"),
     "last_element_interact_count":emu.read_symbol("last_element_interact_count"),
     "player_x":emu.read_symbol("player"),
    }
    emu.tap("A",hold=12,release=12)
    after_diag={
     "near_trigger_x":emu.read_symbol("near_trigger_x"),
     "near_trigger_y":emu.read_symbol("near_trigger_y"),
     "last_element_trigger_x":emu.read_symbol("last_element_trigger_x"),
     "last_element_index":emu.read_symbol("last_element_index"),
     "last_element_interact_count":emu.read_symbol("last_element_interact_count"),
     "element_mask":emu.read_symbol("element_mask"),
    }
    report.setdefault("shrine_diagnostics",[]).append({"index":index,"tile":tile,"before":before_diag,"after":after_diag})
    if not emu.read_symbol("element_mask")&(1<<index):
     raise RuntimeError("Actual shrine "+str(index)+" not earned; diagnostic="+repr(after_diag))
    mark("0"+str(5+index)+"_real_element_"+str(index))
   nav.fight_enemy(7)  # Real native guarded last shrine; no forged kill_count.
   mark("08_actual_Storm_Guardian_defeated")
   nav.interact(21,at=(48,17))
   if emu.read_symbol("element_mask")!=15 or not emu.read_symbol("story_flags")&1024:
    raise RuntimeError("Fourth real shrine + ST_ELEMENTS not earned")
   mark("09_all_four_real_elements")
   emu.step((),180)  # Native dual-bank CRC SRAM journal commit.
   report["passed"]=True
  except Exception as e:
   report["failure"]=repr(e);report["traceback"]=traceback.format_exc()
   try:emu.screenshot(out/"FAILED_TRUE_ELDORIA.png")
   except Exception:pass
  finally:
   report["end_frame"]=emu.frame
   (out/"eldoria_controller_report.json").write_text(json.dumps(report,indent=2)+"\n")
 if not report["passed"]:raise RuntimeError(report.get("failure","unknown controller failure"))
 with Mgba(rom,elf=elf,save_path=save,
           trace_path=out/"eldoria_real_second_boot_inputs.jsonl") as emu:
  emu.step((),180)
  if emu.read_symbol("intro")!=1 or emu.read_symbol("v10_has_save")!=1:
   raise RuntimeError("Actual independent Eldoria cold boot lost battery")
  emu.screenshot(out/"10_actual_Eldoria_second_cold_title.png")
  emu.tap("DOWN",hold=12,release=12);emu.tap("A",hold=12,release=12)
  for _ in range(180):
   if emu.read_symbol("intro")==0 and emu.read_symbol("current_world")==7:break
   emu.step((),8)
  else:raise RuntimeError("Independent controller CONTINUE never restored Eldoria")
  emu.step((),25)
  flags=emu.read_symbol("story_flags")
  elements=emu.read_symbol("element_mask")
  if flags&(0xB9F|1024)!=(0xB9F|1024) or elements!=15:
   raise RuntimeError("Eldoria or earlier campaign milestones lost in independent cold boot")
  report["second_boot"]={"world":emu.read_symbol("current_world"),
    "room":emu.read_symbol("current_room"),"story_flags":flags,
    "element_mask":elements,"frame":emu.frame}
  report["cold_boot_passed"]=True
  emu.screenshot(out/"11_real_Eldoria_four_elements_restored.png")
 (out/"eldoria_controller_report.json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps({"passed":True,"second_boot":report["second_boot"],"stages":report["stages"]},indent=2))

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--rom",type=Path,default=R/"LOST_COSMOS_V10_SOURCE/LOST_COSMOS_V10_OPENING_QA.gba")
 p.add_argument("--elf",type=Path,default=R/"LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.elf")
 p.add_argument("--act2",type=Path,default=R/"artifacts/mgba_act2")
 p.add_argument("--out",type=Path,default=R/"artifacts/mgba_eldoria")
 a=p.parse_args();run(a.rom.resolve(),a.elf.resolve(),a.act2.resolve(),a.out.resolve())
