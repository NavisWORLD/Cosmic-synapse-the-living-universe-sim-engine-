#!/usr/bin/env python3
"""Old V11.3 saves still load in the current ROM, and get the right campaign state.

- A V11.3 save made right at the opening -> PROLOGUE starts at Q00.
- A V11.3 save with real progress (Elder spoken to) -> prologue recorded as
  done from an earlier save (PF_MIGRATED), Q05 active, nothing else changed,
  and the prologue-only cast is not spawned.
Controller-only: CONTINUE on the real title screen. Fixtures are copied, never modified.
"""
import argparse, json, shutil, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from mgba import Mgba,sha256
from mgba_navigate import Navigator
R=Path(__file__).resolve().parents[1]
FX=Path(__file__).resolve().parent/"fixtures"

def boot(rom,elf,src,out):
 sav=out/src.name;shutil.copyfile(src,sav)
 with Mgba(rom,elf=elf,save_path=sav,trace_path=out/(src.stem+"_inputs.jsonl")) as emu:
  nav=Navigator(emu)
  emu.step((),180)
  if emu.read_symbol("v10_has_save")!=1:raise RuntimeError(f"{src.name}: title does not see the V11.3 save")
  emu.tap("DOWN",hold=12,release=12);emu.tap("A",hold=12,release=12)
  for _ in range(250):
   if emu.read_symbol("intro")==0 and (emu.read16(0x04000000)&0x0400) and any(n.id==14 for n in nav.npcs()):break
   emu.step((),8)
  else:raise RuntimeError(f"{src.name}: CONTINUE never reached Brindlemark")
  emu.step((),60)
  emu.screenshot(out/(src.stem+"_continue.png"))
  return {"q":[emu.read_symbol("cq_state",width=1,offset=i) for i in range(7)],
          "pro_flags":emu.read_symbol("pro_flags",width=2),"story_flags":emu.read_symbol("story_flags"),
          "loc":list(nav.location()),"pos":list(nav.position()),"npcs":sorted(n.id for n in nav.npcs())}

def run(rom,elf,out):
 out.mkdir(parents=True,exist_ok=True)
 rep={"suite":"real_mgba_v11_3_save_migration","rom_sha256":sha256(rom),"passed":False}
 a=boot(rom,elf,FX/"v11_3_opening.sav",out);rep["opening"]=a
 if a["q"][:6]!=[1,0,0,0,0,0] or a["pro_flags"]&0x2000:raise RuntimeError(f"Opening save should start Q00: {a}")
 if not {14,30,31}<=set(a["npcs"]):raise RuntimeError("Prologue cast missing for a fresh V11.3 save")
 b=boot(rom,elf,FX/"v11_3_elder.sav",out);rep["elder"]=b
 if b["q"][:6]!=[3,3,3,3,3,1] or not b["pro_flags"]&0x2000:raise RuntimeError(f"Progressed save should migrate to Q05: {b}")
 if b["story_flags"]!=1 or b["loc"]!=[0,2,1] or b["pos"]!=[208,276]:raise RuntimeError(f"Old progress changed: {b}")
 if 30 in b["npcs"] or 31 in b["npcs"]:raise RuntimeError("Prologue cast spawned for a migrated save")
 if b["q"][6]!=0:raise RuntimeError("Migration marked a later quest")
 rep["passed"]=True
 (out/"migration_report.json").write_text(json.dumps(rep,indent=2)+"\n");print(json.dumps(rep,indent=2))

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--rom",type=Path,default=R/"LOST_COSMOS_V10_SOURCE/LOST_COSMOS_V10_OPENING_QA.gba")
 p.add_argument("--elf",type=Path,default=R/"LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.elf")
 p.add_argument("--out",type=Path,default=R/"artifacts/mgba_prologue_migration")
 a=p.parse_args();run(a.rom.resolve(),a.elf.resolve(),a.out.resolve())
