#!/usr/bin/env python3
"""Real controller-only native Act I route: Brindlemark -> Oakwood -> Cragstone.
Never writes emulated state, forces quest flags, loads savestates or teleports.
Actual screenshots and input trace are retained even on a genuine failure.
This tests actual complete Act I through Malakar/Heart, not the remaining four acts.
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
   # current_room changes before the slow real map upload and CRC save finish.
   # The earlier experimental run captured a completely blank transition frame
   # and found zero NPCs because it raced generate_surface(). Do not test a
   # fictitious intermediate frame; wait for genuine BG2 + live spawned NPCs.
   nav=Navigator(emu)
   # V10.8+ intentionally keeps an opaque "TRAVERSING COSMOS" cover visible
   # while the expensive native map build runs. npc_count can still describe
   # the previous scene during that cover, so generic npc_count>0 is not a
   # valid readiness signal. Wait for the actual Brindle Elder spawned by the
   # completed local map instead.
   wait(emu,lambda: (emu.read16(0x04000000)&0x0400)!=0 and
        any(n.id==14 for n in nav.npcs()),
        "fully rendered native Brindlemark with real Elder", max_frames=1800)
   emu.step((),12)
   report["initial_real_npc_ids"]=[n.id for n in nav.npcs()]
   mark("01_true_brindlemark")
   nav.talk_npc(14,advances=3)       # Real village elder with actual NPC dialogue.
   if not emu.read_symbol("story_flags")&1:raise RuntimeError("Brindle elder failed to unlock ST_TOWN")
   mark("02_earned_village_quest")
   nav.interact(12,at=(54,8))       # Real northeast gate to Oakwood.
   if nav.location()!=(0,3,1):raise RuntimeError("Real Oakwood gate did not change map")
   # The room ID changes before actual native BG2 map/NPC generation finishes.
   # Never assert absent NPCs against a real transition blank frame.
   wait(emu,lambda: emu.read_symbol("npc_count")>0 and
        any(n.id==16 for n in nav.npcs()) and
        (emu.read16(0x04000000)&0x0400)!=0,
        "fully rendered genuine Oakwood with Ravenswood", max_frames=1500)
   emu.step((),12)
   mark("03_true_oakwood")
   nav.talk_npc(16,advances=6)      # Ravenswood's actual real three-page conversation.
   if not emu.read_symbol("story_flags")&2:raise RuntimeError("Ravenswood did not earn ST_OAKWOOD")
   mark("04_earned_ravenswood_map")
   nav.interact(12,at=(54,12))     # Authored Oakwood -> Cragstone route, no forced warp.
   if nav.location()!=(0,4,1):raise RuntimeError("Cragstone remained locked despite earned map")
   wait(emu,lambda: emu.read_symbol("npc_count")>0 and
        any(n.id==17 for n in nav.npcs()) and
        (emu.read16(0x04000000)&0x0400)!=0,
        "fully generated actual Cragstone temple and Stone Keeper", max_frames=1500)
   emu.step((),12)
   mark("05_true_cragstone")
   # Actual native rune locations, original source canonical SKY/ROOT/HEART/STAR order:
   for code,pos in [(15,(35,22)),(13,(21,22)),(16,(42,22)),(14,(28,22))]:
    nav.interact(code,at=pos)
   if not emu.read_symbol("story_flags")&4:raise RuntimeError("Four separate real runes did not earn ST_PUZZLE")
   mark("06_real_four_seal_puzzle")
   # The legitimate final rune shows a native cinematic; let it finish.
   nav.wait_cinema()
   # This is the REAL native boss (enemy slot 8) and genuine menu combat.
   # No injected kills, memory writes, teleports, or savestate shortcuts.
   nav.fight_enemy(8)
   if not emu.read_symbol("story_flags")&8:
    raise RuntimeError("Genuine Malakar battle did not earn ST_MALAKAR")
   mark("07_real_Malakar_defeated")
   nav.interact(17,at=(32,9))
   if not emu.read_symbol("story_flags")&16:
    raise RuntimeError("Genuine First Heart interaction did not earn ST_HEART")
   # The 8 KiB dual-bank save may still be committing when the interaction
   # returns. Wait for actual native emulated frames before battery export.
   emu.step((),180)
   if (emu.read8(0x0e000000+200)&31)!=31:
    raise RuntimeError("Original SRAM Story Flags did not commit after real Heart")
   report["first_heart_sram"]={
    "primary_story_byte":emu.read8(0x0e000000+200),
    "bank0_story_byte":emu.read8(0x0e000000+8192+200),
    "bank1_story_byte":emu.read8(0x0e000000+16384+200),
    "bank0_commit":emu.read8(0x0e000000+24576+15),
    "bank1_commit":emu.read8(0x0e000000+24576+64+15)}
   mark("08_real_First_Heart")
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
                  "scope":"actual native full Act I through real Malakar combat and First Heart; NOT Acts II-V"},indent=2))

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--rom",type=Path,default=R/"LOST_COSMOS_V10_SOURCE/LOST_COSMOS_V10_OPENING_QA.gba")
 p.add_argument("--elf",type=Path,default=R/"LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.elf")
 p.add_argument("--out",type=Path,default=R/"artifacts/mgba_act1")
 a=p.parse_args();run(a.rom.resolve(),a.elf.resolve(),a.out.resolve())
