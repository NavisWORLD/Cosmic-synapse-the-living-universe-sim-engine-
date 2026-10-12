#!/usr/bin/env python3
"""Real libmGBA menu check on an earned Act I save (controller only).

Continues the act1_complete.sav written by test_mgba_act1_heart.py, then opens
every player-facing pause page (MAP, QUESTS incl. the STORY view, PARTY,
ITEMS, GEAR, SKILLS, BEASTS, MEMORIES, BEAST BOX, SYSTEM), saves to slot 3 from
SYSTEM > SAVE GAME, opens SYSTEM > 3D VIEW in Oakwood and leaves it with START.
Only START/D-pad/A/B/L/R input; no memory writes or savestates.
"""
from __future__ import annotations
import argparse, json, shutil, sys, traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"));sys.path.insert(0,str(ROOT/"tests"))
from mgba import Mgba,sha256
from mgba_navigate import Navigator
import test_mgba_beast_home as bh
from test_mgba_menu_visual import PAGES,goto_index

def run(rom,elf,act1,out):
 out.mkdir(parents=True,exist_ok=True)
 save=out/"world_menus.sav";shutil.copyfile(act1/"act1_complete.sav",save)
 rep={"suite":"v11_7_world_menus_after_act1","rom_sha256":sha256(rom),"elf_sha256":sha256(elf),
      "input_save_sha256":sha256(save),"controller_only":True,"memory_writes":False,"savestates":False,
      "pages":[],"passed":False}
 with Mgba(rom,elf=elf,save_path=save,trace_path=out/"world_menus_inputs.jsonl") as emu:
  r=emu.read_symbol
  def need(c,m):
   if not c:raise RuntimeError(m)
  def pause():
   emu.tap("START",hold=10,release=10)
   bh.wait(emu,lambda:r("game_mode")==2 and r("pause_page")==0,"main menu",240,2)
  def close():
   for _ in range(5):
    if r("game_mode")==0:return
    emu.tap("B",hold=10,release=10);emu.step((),8)
   need(r("game_mode")==0,"pause menu did not close")
  try:
   emu.step((),180);need(r("intro")==1 and r("v10_has_save")==1,"title/continue missing")
   emu.tap("DOWN",hold=12,release=12);emu.tap("A",hold=12,release=12)
   bh.wait(emu,lambda:r("intro")==0 and r("game_mode")==0,"continue",1200,4)
   emu.step((),30)
   rep["location"]=[r("current_world"),r("current_room"),r("current_layer")]
   need(rep["location"][:2]==[0,3],f"Act I save should continue in Oakwood, got {rep['location']}")
   pause();emu.screenshot(out/"00_main_menu.png")
   for name,index in PAGES:
    goto_index(emu,index);emu.tap("A",hold=10,release=10);emu.step((),10)
    page=r("pause_page");rows=[bh.ui_row(emu,i).strip() for i in range(0,18)]
    emu.screenshot(out/f"page_{index:02d}_{name}.png")
    need(page!=0,f"{name}: page did not open")
    entry={"name":name,"pause_page":page,"rows":[x for x in rows if x]}
    if name=="quest":
     for _ in range(4):
      if r("v11_sub")==2:break
      emu.tap("RIGHT",hold=8,release=8);emu.step((),6)
     need(r("v11_sub")==2,"QUESTS STORY view not reached");emu.step((),6)
     entry["story_rows"]=[x for x in (bh.ui_row(emu,i).strip() for i in range(0,18)) if x]
     emu.screenshot(out/f"page_{index:02d}_quest_story.png")
     for _ in range(12):
      if r("v11_sel")==9:break
      emu.tap("DOWN",hold=8,release=8);emu.step((),4)
     emu.step((),6);rows9=[x for x in (bh.ui_row(emu,i).strip() for i in range(0,18)) if x]
     entry["story_rows_q09"]=rows9;emu.screenshot(out/f"page_{index:02d}_quest_story_q09.png")
     need(any(x.startswith("Q09") for x in rows9) and "COMPLETE" in rows9,f"Q09 not COMPLETE in STORY view: {rows9}")
    rep["pages"].append(entry)
    emu.tap("B",hold=10,release=10);emu.step((),8)
    if r("pause_page")!=0:emu.tap("B",hold=10,release=10);emu.step((),8)
    need(r("pause_page")==0 and r("game_mode")==2,f"{name}: B did not return to the main menu")
   # SYSTEM > SAVE GAME > slot 3
   goto_index(emu,9);emu.tap("A",hold=10,release=10);bh.wait(emu,lambda:r("pause_page")==9,"SYSTEM",120,2)
   for _ in range(14):
    if r("v11_sel")==3:break
    emu.tap("DOWN",hold=8,release=8);emu.step((),4)
   need(r("v11_sel")==3,"SAVE GAME row not selected")
   emu.tap("A",hold=10,release=10);emu.step((),8)
   need(r("pause_page")==44 and r("v11_sub")==0,"SAVE page did not open")
   emu.tap("UP",hold=8,release=8);emu.step((),4);need(r("v11_sel")==2,"slot 3 not selected")
   slot=0x0E000000+25600+2*2048
   before=bytes(emu.read_range(slot,64))
   emu.tap("A",hold=10,release=10);emu.step((),8)
   if r("v11_menu_mode"):emu.tap("A",hold=10,release=10)
   emu.step((),60)
   after=bytes(emu.read_range(slot,64))
   rep["slot3_written"]=before!=after or any(after)
   rep["save_rows"]=[x for x in (bh.ui_row(emu,i).strip() for i in range(0,18)) if x]
   emu.screenshot(out/"save_slot3.png")
   need(rep["slot3_written"],"slot 3 save wrote nothing")
   close()
   # SYSTEM > 3D VIEW in Oakwood, then leave with START.
   from test_mgba_first_person import open_3d,confirm_3d
   open_3d(emu,"oakwood");d,s=confirm_3d(emu,"oakwood")
   rep["fp"]={"dispcnt":d["dispcnt"],"unique":s["unique"]};emu.screenshot(out/"3d_view_oakwood.png")
   emu.step("UP",30);emu.screenshot(out/"3d_view_oakwood_walk.png")
   emu.tap("START",hold=8,release=8);emu.step((),6)
   need(r("fp_active",width=1)==0 and r("game_mode")==0,"START did not leave the 3D view")
   rep["after_3d_location"]=[r("current_world"),r("current_room"),r("current_layer")]
   need(rep["after_3d_location"][:2]==[0,3],"3D view changed the room")
   emu.screenshot(out/"99_back_on_foot.png")
   rep["passed"]=True
  except Exception as exc:
   rep["failure"]=repr(exc);rep["traceback"]=traceback.format_exc()
   try:emu.screenshot(out/"FAILED_NATIVE_FRAME.png")
   except Exception:pass
  finally:
   rep["last_frame"]=emu.frame
   (out/"world_menus_report.json").write_text(json.dumps(rep,indent=1)+"\n")
 print(json.dumps({k:v for k,v in rep.items() if k not in("pages","traceback")},indent=1))
 if not rep["passed"]:raise SystemExit(rep.get("failure"))

if __name__=="__main__":
 ap=argparse.ArgumentParser()
 ap.add_argument("--rom",type=Path,default=ROOT/"LOST_COSMOS_V10_SOURCE/LOST_COSMOS_V10_OPENING_QA.gba")
 ap.add_argument("--elf",type=Path,default=ROOT/"LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.elf")
 ap.add_argument("--act1",type=Path,default=ROOT/"artifacts/mgba_act1")
 ap.add_argument("--out",type=Path,default=ROOT/"artifacts/mgba_world_menus")
 a=ap.parse_args();run(a.rom.resolve(),a.elf.resolve(),a.act1.resolve(),a.out.resolve())
