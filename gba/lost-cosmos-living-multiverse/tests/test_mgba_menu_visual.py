#!/usr/bin/env python3
"""Real libmGBA V11.1 menu pilgrimage from ordinary controller input.

Fresh boots the real cartridge, starts a new game, reaches Brindlemark and opens
all ten player-facing pause pages using only START/D-pad/A/B/L/R. Captures the
native 240x160 framebuffer for visual review. No memory writes or savestates.
"""
from __future__ import annotations
import argparse, json, sys, traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mgba import Mgba,sha256
from mgba_navigate import Navigator

PAGES=[
 ("map",0),("quest",1),("party",2),("items",3),("equipment",4),
 ("abilities",5),("bestiary",6),("memories",7),("beast_box",8),("system",9),
]

def wait(emu,pred,label,budget=1800):
 for _ in range((budget+7)//8):
  if pred(): return
  emu.step((),8)
 raise RuntimeError(f"Timed out waiting for {label}")

def goto_index(emu,target):
 # Navigate entirely by real D-pad input and tolerate one scan/frame of input
 # settling between submenus. No state writes are used.
 for _ in range(16):
  cur=emu.read_symbol("pause_sel")
  if cur==target:return
  cur_col=1 if cur>=5 else 0;want_col=1 if target>=5 else 0
  if cur_col!=want_col:key="RIGHT" if want_col else "LEFT"
  else:
   row=cur%5;want=target%5
   down=(want-row)%5;up=(row-want)%5
   key="DOWN" if down<=up else "UP"
  emu.tap(key,hold=10,release=14);emu.step((),6)
 raise RuntimeError(f"Menu navigation failed: {emu.read_symbol('pause_sel')} != {target}")

def run(rom,elf,out):
 out.mkdir(parents=True,exist_ok=True)
 save=out/"menu_visual_fresh.sav"
 if save.exists(): save.unlink()
 report={"suite":"v11_1_1_real_mgba_menu_visual_pilgrimage","rom_sha256":sha256(rom),
         "elf_sha256":sha256(elf),"controller_only":True,"memory_writes":False,
         "savestates":False,"captures":[],"passed":False}
 with Mgba(rom,elf=elf,save_path=save,trace_path=out/"menu_visual_inputs.jsonl") as emu:
  try:
   emu.step((),180);emu.screenshot(out/"00_title.png")
   if emu.read_symbol("intro")!=1: raise RuntimeError("Native title missing")
   emu.tap("A",hold=12,release=12)
   wait(emu,lambda:emu.read_symbol("v10_opening")==1,"opening")
   emu.tap("START",hold=12,release=12)
   wait(emu,lambda:emu.read_symbol("v10_opening")==0 and emu.read_symbol("current_room")==2,"Brindlemark")
   nav=Navigator(emu)
   # Room/world IDs and stale NPCs become visible before the intentional
   # TRAVERSING COSMOS build cover is removed. Wait for the actual Elder from
   # the completed Brindlemark map so screenshots never capture a transition.
   wait(emu,lambda:(emu.read16(0x04000000)&0x0400)!=0 and
        any(n.id==14 for n in nav.npcs()),"fully rendered Brindlemark with Elder",budget=1800)
   emu.step((),16);emu.screenshot(out/"01_exploration.png")
   emu.tap("START",hold=12,release=12)
   wait(emu,lambda:emu.read_symbol("game_mode")==2 and emu.read_symbol("pause_page")==0,"main menu")
   emu.step((),8);emu.screenshot(out/"02_main_menu.png")
   for name,index in PAGES:
    goto_index(emu,index);emu.screenshot(out/f"menu_selected_{index:02d}_{name}.png")
    emu.tap("A",hold=10,release=10);emu.step((),8)
    page=emu.read_symbol("pause_page")
    emu.screenshot(out/f"page_{index:02d}_{name}.png")
    report["captures"].append({"name":name,"selector":index,"pause_page":page,"frame":emu.frame,
      "bg1cnt":emu.read16(0x0400000A),"bg1hofs":emu.read16(0x04000014),
      "bg1vofs":emu.read16(0x04000016),"dispcnt":emu.read16(0x04000000)})
    if name=="party" and page==18 and emu.read_symbol("lc_party",width=1)>0:
     emu.tap("A",hold=10,release=10);emu.step((),8)
     emu.screenshot(out/"page_02_party_actions.png")
     emu.tap("B",hold=10,release=10);emu.step((),8)
    emu.tap("B",hold=10,release=10);emu.step((),8)
    if emu.read_symbol("pause_page")!=0:
     raise RuntimeError(f"{name}: B did not return to main menu")
   emu.screenshot(out/"99_main_menu_return.png")
   report["passed"]=True
  except Exception as exc:
   report["failure"]=repr(exc);report["traceback"]=traceback.format_exc()
   try: emu.screenshot(out/"FAILED_NATIVE_FRAME.png")
   except Exception: pass
   raise
  finally:
   report["last_frame"]=emu.frame
   (out/"menu_visual_report.json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps(report,indent=2))

if __name__=="__main__":
 ap=argparse.ArgumentParser()
 ap.add_argument("--rom",type=Path,default=ROOT/"LOST_COSMOS_V10_SOURCE/LOST_COSMOS_V10_OPENING_QA.gba")
 ap.add_argument("--elf",type=Path,default=ROOT/"LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.elf")
 ap.add_argument("--out",type=Path,default=ROOT/"artifacts/mgba_menu_visual")
 a=ap.parse_args();run(a.rom.resolve(),a.elf.resolve(),a.out.resolve())
