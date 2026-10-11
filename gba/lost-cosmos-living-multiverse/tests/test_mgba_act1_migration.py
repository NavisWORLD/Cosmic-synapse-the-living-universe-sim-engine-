#!/usr/bin/env python3
"""V11.6 saves load in the V11.7 ROM and land on the right ACT I quest.

Fixtures (tests/fixtures, real SRAM written by the V11.6 ROM from main
5531862 in libmGBA with controller input; see README_V11_6_SAVES.md):
- v11_6_prologue_done.sav: prologue finished, Q05 active, never in Oakwood.
- v11_6_mid_ravenswood.sav: old route, Ravenswood spoken to (ST_TOWN|ST_OAKWOOD).
- v11_6_old_act1_heart.sav: old route, First Heart taken (story_flags 31).
Each is copied, CONTINUEd on the real title screen, checked, then played a
little with the controller through the new Act I rooms, and cold-booted again
to prove the new 'A' block was written. Fixtures are never modified.
"""
import argparse, json, shutil, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from mgba import Mgba,sha256
from mgba_navigate import Navigator
R=Path(__file__).resolve().parents[1]
FX=Path(__file__).resolve().parent/"fixtures"
A1_SRAM=0x0e000000+6400+728

def wait(emu,pred,what,max_frames=1600):
 for _ in range((max_frames+7)//8):
  if pred():return
  emu.step((),8)
 raise RuntimeError(f"{what} not reached after {max_frames} frames")

def state(emu,nav):
 return {"q":[emu.read_symbol("cq_state",width=1,offset=i) for i in range(11)],
         "a1_flags":emu.read_symbol("a1_flags",width=2),"regent":emu.read_symbol("a1_regent"),
         "pro_flags":emu.read_symbol("pro_flags",width=2),"story_flags":emu.read_symbol("story_flags"),
         "loc":list(nav.location()),"sram_A":emu.read8(A1_SRAM),"sram_schema":emu.read8(A1_SRAM+1)}

def cont(emu,nav,name):
 emu.step((),180)
 if emu.read_symbol("v10_has_save")!=1:raise RuntimeError(f"{name}: title does not see the save")
 emu.tap("DOWN",hold=12,release=12);emu.tap("A",hold=12,release=12)
 wait(emu,lambda:emu.read_symbol("intro")==0 and (emu.read16(0x04000000)&0x0400)!=0,f"{name} continue")
 emu.step((),60);nav.wait_cinema(max_frames=2400)

def go(emu,nav,value,at,room):
 nav.interact(value,at=at)
 wait(emu,lambda:emu.read_symbol("current_room")==room,f"room {room}",900)
 wait(emu,lambda:(emu.read16(0x04000000)&0x0400)!=0,"room build");emu.step((),30)

def run(rom,elf,out):
 out.mkdir(parents=True,exist_ok=True)
 rep={"suite":"real_mgba_v11_6_act1_migration","rom_sha256":sha256(rom),"fixtures":{},"passed":False}
 # 1. Prologue finished in V11.6: Q05 active, Act I untouched, Ravenswood scripts the new quest.
 src=FX/"v11_6_prologue_done.sav";sav=out/src.name;shutil.copyfile(src,sav)
 rep["fixtures"][src.name]=sha256(src)
 with Mgba(rom,elf=elf,save_path=sav,trace_path=out/"prologue_done_inputs.jsonl") as emu:
  nav=Navigator(emu);cont(emu,nav,src.name)
  a=state(emu,nav);rep["prologue_done"]=a
  if a["q"][:7]!=[3,3,3,3,3,1,0] or a["a1_flags"]!=0:raise RuntimeError(f"prologue save should sit at Q05: {a}")
  emu.screenshot(out/"m1_prologue_done_continue.png")
 # 2. Old route mid-way: Ravenswood had opened Cragstone. Q05/Q06 recorded, Q07 active, ascent open.
 src=FX/"v11_6_mid_ravenswood.sav";sav=out/src.name;shutil.copyfile(src,sav)
 rep["fixtures"][src.name]=sha256(src)
 with Mgba(rom,elf=elf,save_path=sav,trace_path=out/"mid_inputs.jsonl") as emu:
  nav=Navigator(emu);cont(emu,nav,src.name)
  b=state(emu,nav);rep["mid_continue"]=b
  if b["q"][:8]!=[3,3,3,3,3,3,3,1] or b["story_flags"]!=3 or b["loc"]!=[0,3,1]:raise RuntimeError(f"mid save migration wrong: {b}")
  if not b["a1_flags"]&0x8000 or b["a1_flags"]&0x40:raise RuntimeError(f"mid save flags wrong: {b}")
  emu.screenshot(out/"m2_mid_continue_oakwood.png")
  go(emu,nav,212,(54,12),91)
  emu.screenshot(out/"m3_mid_ascent_open.png")
  go(emu,nav,214,(32,2),4)
  if emu.read_symbol("pro_ui")==4:
   while emu.read_symbol("pro_ui")==4:emu.step((),30);emu.tap("A",hold=6,release=6)
  emu.step((),200);rep["mid_after_play"]=state(emu,nav)
  emu.screenshot(out/"m4_mid_temple_hall.png")
 with Mgba(rom,elf=elf,save_path=sav,trace_path=out/"mid_coldboot_inputs.jsonl") as emu:
  nav=Navigator(emu);cont(emu,nav,"mid cold boot")
  c=state(emu,nav);rep["mid_cold_boot"]=c
  if c["sram_A"]!=ord("A") or c["sram_schema"]!=1 or c["loc"]!=[0,4,1] or c["q"][:8]!=[3,3,3,3,3,3,3,1] or not c["a1_flags"]&0x20:
   raise RuntimeError(f"mid save did not persist the new Act I block: {c}")
 # 3. Old route finished: the Heart was taken. Act I recorded done, Q10 active; the new rooms are walkable.
 src=FX/"v11_6_old_act1_heart.sav";sav=out/src.name;shutil.copyfile(src,sav)
 rep["fixtures"][src.name]=sha256(src)
 with Mgba(rom,elf=elf,save_path=sav,trace_path=out/"heart_inputs.jsonl") as emu:
  nav=Navigator(emu);cont(emu,nav,src.name)
  d=state(emu,nav);rep["heart_continue"]=d
  if d["q"][:11]!=[3]*10+[1] or d["story_flags"]&31!=31 or not d["a1_flags"]&0x2000 or d["regent"]!=1 or d["loc"]!=[0,4,1]:
   raise RuntimeError(f"finished save migration wrong: {d}")
  emu.screenshot(out/"m5_heart_continue_hall.png")
  go(emu,nav,220,(32,9),94)
  emu.screenshot(out/"m6_heart_chamber_after_migration.png")
  nav.interact(230,at=(32,10));emu.step((),30)
  if emu.read_symbol("pro_ui")!=0 or emu.read_symbol("story_flags")&31!=31:raise RuntimeError("migrated Heart replayed Malakar")
  go(emu,nav,221,(32,59),4)
  go(emu,nav,217,(32,55),91)
  go(emu,nav,213,(32,62),3)
  emu.step((),200);rep["heart_after_play"]=state(emu,nav)
  emu.screenshot(out/"m7_heart_back_to_oakwood.png")
 with Mgba(rom,elf=elf,save_path=sav,trace_path=out/"heart_coldboot_inputs.jsonl") as emu:
  nav=Navigator(emu);cont(emu,nav,"heart cold boot")
  e=state(emu,nav);rep["heart_cold_boot"]=e
  if e["sram_A"]!=ord("A") or e["loc"]!=[0,3,1] or e["q"][:11]!=[3]*10+[1]:raise RuntimeError(f"finished save lost Act I: {e}")
 rep["passed"]=True
 (out/"act1_migration_report.json").write_text(json.dumps(rep,indent=2)+"\n");print(json.dumps(rep,indent=2))

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--rom",type=Path,default=R/"LOST_COSMOS_V10_SOURCE/LOST_COSMOS_V10_OPENING_QA.gba")
 p.add_argument("--elf",type=Path,default=R/"LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.elf")
 p.add_argument("--out",type=Path,default=R/"artifacts/mgba_act1_migration")
 a=p.parse_args();run(a.rom.resolve(),a.elf.resolve(),a.out.resolve())
