#!/usr/bin/env python3
"""V11.8 LEASH OFF, controller-only libmGBA test on an earned Act I save.

1. CONTINUE the Act I save (Oakwood). LEASH is OFF by default.
2. Arin stands still for 45 s. Every 4 frames, sample the beast (cosmos.x/y).
   It must never stand on a wall or hazard, it must roam (distinct tiles,
   distance from Arin), and the LCL1 counters must grow. Story, quest and
   inventory state must not change while it roams.
3. START > SYSTEM > CALL BEAST. The beast must come back within 600 frames.
4. PARTY > COSMOS > DETAILS opens the BEAST // FIELD RECORD page.
5. SYSTEM > 3D VIEW. The beast is drawn at its own position and keeps roaming,
   and the HUD shows LEASH OFF. START leaves the view.
6. SYSTEM > LEASH ON: the beast is back beside Arin, the old follower runs, and
   no LCL1 counter moves. Then LEASH OFF again, which saves the game.
7. Cold boot and CONTINUE. The LCL1 record equals the one in SRAM before the
   reboot.
8. Migration: an older V11.7 save (no LCL1 block) loads with an empty record
   and LEASH OFF, keeps its quest state, and the beast roams.
No memory writes and no savestates.
"""
from __future__ import annotations
import argparse, json, shutil, struct, sys, traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"));sys.path.insert(0,str(ROOT/"tests"))
from mgba import Mgba,sha256
import test_mgba_beast_home as bh
from test_mgba_menu_visual import goto_index

LF_SRAM=7296;LF_BYTES=520
REC_FIELDS=("cells","pois","npcs","encounters","calls","returns","catchups","checkins","no_path","secs")
GOALS=("idle","explore","poi","npc","alert","rest","return","checkin")
def rec_ram(emu):
 b=emu.read_range(emu.symbols["lf_rec"].address,512)
 r={"moves_ok":struct.unpack_from("<I",b,0)[0],"moves_blocked":struct.unpack_from("<I",b,4)[0]}
 for i,k in enumerate(REC_FIELDS):r[k]=struct.unpack_from("<H",b,8+i*2)[0]
 r["done"]=dict(zip(GOALS,struct.unpack_from("<8H",b,28)))
 return r
def rec_sram(emu):
 b=emu.read_range(0x0E000000+LF_SRAM,LF_BYTES)
 if b[:4]!=b"LCL1":return {"magic":b[:4].hex()}
 r={"magic":"LCL1","version":b[4],"leash_on":b[5]&1,"older_save":(b[5]>>1)&1,
    "moves_ok":struct.unpack_from("<I",b,8)[0],"moves_blocked":struct.unpack_from("<I",b,12)[0]}
 for i,k in enumerate(REC_FIELDS):r[k]=struct.unpack_from("<H",b,16+i*2)[0]
 r["done"]=dict(zip(GOALS,struct.unpack_from("<8H",b,36)))
 r["favorites"]=[{"loc":b[52+i],"cell":b[60+i],"n":struct.unpack_from("<H",b,68+i*2)[0]} for i in range(8) if struct.unpack_from("<H",b,68+i*2)[0]]
 return r
def beast(emu):return emu.read_symbol("cosmos.0",signed=True),emu.read_symbol("cosmos.1",signed=True)
def arin(emu):return emu.read_symbol("player.0",signed=True),emu.read_symbol("player.1",signed=True)
def coll(emu,x,y):
 if not(0<=x<512 and 0<=y<512):return 1
 return emu.read8(emu.symbols["collision"].address+((y>>3)<<6)+(x>>3))
def state(emu):
 return {"story_flags":emu.read_symbol("story_flags"),"cq":list(emu.read_range(emu.symbols["cq_state"].address,emu.symbols["cq_state"].size)),
  "a1_flags":emu.read_symbol("a1_flags"),"inv":list(emu.read_range(emu.symbols["inv"].address,emu.symbols["inv"].size)),
  "credits":emu.read_symbol("credits"),"keys":emu.read_symbol("keys_found"),"quest_started":emu.read_symbol("quest_started"),
  "quest_completed":emu.read_symbol("quest_completed"),"xp":emu.read_symbol("player_xp")}
def boot_continue(emu,need):
 emu.step((),180);need(emu.read_symbol("intro")==1 and emu.read_symbol("v10_has_save")==1,"title/continue missing")
 emu.tap("DOWN",hold=12,release=12);emu.tap("A",hold=12,release=12)
 bh.wait(emu,lambda:emu.read_symbol("intro")==0 and emu.read_symbol("game_mode")==0,"continue",1200,4)
 emu.step((),30)
def roam(emu,frames,need,label):
 """Arin stands still; sample the beast. Returns measurements."""
 p0=arin(emu);s0=state(emu);r0=rec_ram(emu);tiles=set();maxd=0;bad=[]
 for f in range(0,frames,4):
  emu.step((),4)
  x,y=beast(emu);tiles.add((x>>3,y>>3));maxd=max(maxd,abs(x-p0[0])+abs(y-p0[1]))
  if coll(emu,x,y)!=0:bad.append((emu.frame,x,y,coll(emu,x,y)))
 r1=rec_ram(emu);s1=state(emu)
 out={"frames":frames,"distinct_tiles":len(tiles),"max_dist_px":maxd,"wall_or_hazard_samples":bad,
  "arin_moved":arin(emu)!=p0,"state_changed":[k for k in s0 if s0[k]!=s1[k]],
  "delta":{k:(r1[k]-r0[k]) for k in r1 if k!="done"},"goals_done_delta":{k:r1["done"][k]-r0["done"][k] for k in GOALS}}
 need(not bad,f"{label}: beast stood on a wall/hazard {bad[:3]}")
 need(not out["arin_moved"],f"{label}: Arin moved without input")
 need(not out["state_changed"],f"{label}: story/quest/inventory changed while the beast roamed: {out['state_changed']}")
 return out
def system_row(emu,need,target):
 emu.tap("START",hold=10,release=10);bh.wait(emu,lambda:emu.read_symbol("game_mode")==2 and emu.read_symbol("pause_page")==0,"pause",240,2)
 goto_index(emu,9);emu.tap("A",hold=10,release=10);bh.wait(emu,lambda:emu.read_symbol("pause_page")==9,"SYSTEM",120,2)
 for _ in range(18):
  if emu.read_symbol("v11_sel")==target:break
  emu.tap("UP",hold=8,release=8);emu.step((),4)
 need(emu.read_symbol("v11_sel")==target,f"SYSTEM row {target} not reached")
def close_pause(emu,need):
 for _ in range(6):
  if emu.read_symbol("game_mode")==0:return
  emu.tap("B",hold=10,release=10);emu.step((),8)
 need(emu.read_symbol("game_mode")==0,"pause menu did not close")
def rows(emu):return [x for x in (bh.ui_row(emu,i).strip() for i in range(0,20)) if x]

def run(rom,elf,src_save,old_save,out,record):
 out.mkdir(parents=True,exist_ok=True)
 save=out/"leash.sav";shutil.copyfile(src_save,save)
 rep={"suite":"v11_8_leash_off_controller","rom_sha256":sha256(rom),"elf_sha256":sha256(elf),"input_save_sha256":sha256(save),
      "controller_only":True,"memory_writes":False,"savestates":False,"passed":False}
 def need(c,m):
  if not c:raise RuntimeError(m)
 try:
  with Mgba(rom,elf=elf,save_path=save,trace_path=out/"leash_inputs.jsonl") as emu:
   if record:emu.start_recording(out/"LOST_COSMOS_LEASH_OFF.mp4")
   shot=lambda n:emu.screenshot(out/f"{n}.png")
   boot_continue(emu,need)
   rep["location"]=[emu.read_symbol("current_world"),emu.read_symbol("current_room")]
   need(emu.read_symbol("leash_on")==0,"LEASH should default to OFF");shot("00_continue_leash_off")
   rep["roam_oakwood"]=roam(emu,2700,need,"Oakwood");shot("01_after_45s_roam")
   d=rep["roam_oakwood"]
   need(d["distinct_tiles"]>=12 and d["max_dist_px"]>48,f"beast did not roam: {d['distinct_tiles']} tiles, {d['max_dist_px']}px")
   need(d["delta"]["moves_ok"]>=12 and d["delta"]["cells"]+d["delta"]["pois"]+d["delta"]["npcs"]>=1,f"record did not grow: {d['delta']}")
   # CALL BEAST from SYSTEM (UP from AUDIO wraps to the last row).
   r0=rec_ram(emu);system_row(emu,need,15);rep["call_rows"]=rows(emu);shot("02_system_call_beast")
   emu.tap("A",hold=10,release=10);emu.step((),10);close_pause(emu,need)
   need(emu.read_symbol("lf_called")==1 or rec_ram(emu)["returns"]>r0["returns"],"CALL BEAST did not register")
   t0=emu.frame;back=None
   for _ in range(150):
    emu.step((),4);x,y=beast(emu);p=arin(emu)
    if abs(x-p[0])+abs(y-p[1])<=20 and emu.read_symbol("lf_called")==0:back=emu.frame-t0;break
   r1=rec_ram(emu);rep["call"]={"frames_to_return":back,"calls":r1["calls"]-r0["calls"],"returns":r1["returns"]-r0["returns"],"catchups":r1["catchups"]-r0["catchups"]}
   need(back is not None and r1["calls"]==r0["calls"]+1 and r1["returns"]+r1["catchups"]>r0["returns"]+r0["catchups"],f"beast did not come back: {rep['call']}")
   shot("03_beast_came_back")
   # Field record page: PARTY > COSMOS > A > DETAILS
   emu.tap("START",hold=10,release=10);bh.wait(emu,lambda:emu.read_symbol("game_mode")==2 and emu.read_symbol("pause_page")==0,"pause",240,2)
   goto_index(emu,2);emu.tap("A",hold=10,release=10);bh.wait(emu,lambda:emu.read_symbol("pause_page")==18,"PARTY",120,2)
   for _ in range(8):
    if emu.read_symbol("v11_sel")==0:break
    emu.tap("UP",hold=8,release=8);emu.step((),4)
   emu.tap("A",hold=10,release=10);bh.wait(emu,lambda:emu.read_symbol("pause_page")==27,"COMPANION ACTIONS",120,2)
   for _ in range(8):
    if emu.read_symbol("v11_sel")==3:break
    emu.tap("DOWN",hold=8,release=8);emu.step((),4)
   emu.tap("A",hold=10,release=10);bh.wait(emu,lambda:emu.read_symbol("pause_page")==50,"FIELD RECORD page",120,2);emu.step((),8)
   rep["record_page"]=rows(emu);shot("04_beast_field_record_page")
   need(any("FIELD RECORD" in x for x in rep["record_page"]) and any(x.startswith("LEASH") and "OFF" in x for x in rep["record_page"]) and any("CELLS" in x for x in rep["record_page"]),f"record page rows: {rep['record_page']}")
   close_pause(emu,need)
   # 3D VIEW with the leash off.
   from test_mgba_first_person import open_3d,confirm_3d
   open_3d(emu,"leash");confirm_3d(emu,"leash");emu.step((),4)
   fpx=emu.read_symbol("fp_beast_x",signed=True)>>8;bx,by=beast(emu)
   rep["fp_hud"]=rows(emu)
   need(abs(fpx-bx)<=2,f"3D view beast {fpx} is not at the field beast {bx}")
   need(any("LEASH OFF" in x for x in rep["fp_hud"]),f"3D HUD rows: {rep['fp_hud']}")
   shot("05_3d_view_leash_off");p0=beast(emu);m0=rec_ram(emu)["moves_ok"]
   emu.step((),600);p1=beast(emu);m1=rec_ram(emu)["moves_ok"];shot("06_3d_view_after_10s")
   rep["fp_roam"]={"beast_before":p0,"beast_after":p1,"steps":m1-m0}
   need(m1>m0,"beast stopped roaming in the 3D view")
   emu.tap("START",hold=8,release=8);emu.step((),6);need(emu.read_symbol("fp_active",width=1)==0,"START did not leave 3D view")
   # LEASH ON: old follower, no LCL1 counter moves.
   system_row(emu,need,14);emu.tap("A",hold=10,release=10);emu.step((),8);close_pause(emu,need)
   need(emu.read_symbol("leash_on")==1,"LEASH ON did not toggle");r0=rec_ram(emu);bx,by=beast(emu);p=arin(emu)
   rep["leash_on_snap_px"]=abs(bx-p[0])+abs(by-p[1]);emu.step((),600);r1=rec_ram(emu)
   rep["leash_on_record_delta"]=r1["moves_ok"]-r0["moves_ok"];shot("07_leash_on")
   need(rep["leash_on_snap_px"]<=40 and rep["leash_on_record_delta"]==0,f"LEASH ON: snap {rep['leash_on_snap_px']} delta {rep['leash_on_record_delta']}")
   system_row(emu,need,14);emu.tap("A",hold=10,release=10);emu.step((),8);close_pause(emu,need)
   need(emu.read_symbol("leash_on")==0,"LEASH OFF did not toggle back")
   emu.step((),240)
   # save through SYSTEM > SAVE GAME (slot screen also writes the main page first)
   emu.step((),60);rep["sram_before_reboot"]=rec_sram(emu)
   need(rep["sram_before_reboot"].get("magic")=="LCL1","no LCL1 block in SRAM")
   if record:emu.stop_recording()
  # cold boot
  with Mgba(rom,elf=elf,save_path=save,trace_path=out/"leash_coldboot_inputs.jsonl") as emu:
   boot_continue(emu,need);r=rec_ram(emu);s=rep["sram_before_reboot"]
   rep["cold_boot"]={k:r[k] for k in ("moves_ok","moves_blocked","cells","pois","npcs","calls","returns")}
   rep["cold_boot"]["leash_on"]=emu.read_symbol("leash_on")
   need(all(r[k]==s[k] for k in ("moves_ok","moves_blocked","cells","pois","npcs","calls","returns")) and rep["cold_boot"]["leash_on"]==0,f"cold boot record mismatch {rep['cold_boot']} vs {s}")
   emu.screenshot(out/"08_cold_boot_continue.png")
  # older save migration
  if old_save:
   ms=out/"leash_migration.sav";shutil.copyfile(old_save,ms)
   rep["migration_input_sha256"]=sha256(ms)
   with Mgba(rom,elf=elf,save_path=ms,trace_path=out/"leash_migration_inputs.jsonl") as emu:
    boot_continue(emu,need);r=rec_ram(emu);flags=emu.read_range(emu.symbols["lf_rec"].address+508,1)[0]
    rep["migration"]={"leash_on":emu.read_symbol("leash_on"),"older_save_flag":(flags>>1)&1,"record_at_load":{k:r[k] for k in ("moves_ok","cells","calls")},
                      "cq":list(emu.read_range(emu.symbols["cq_state"].address,11))}
    need(rep["migration"]["leash_on"]==0 and rep["migration"]["older_save_flag"]==1 and r["cells"]==0 and r["calls"]==0,f"migration: {rep['migration']}")
    need(rep["migration"]["cq"][5:10]==[3,3,3,3,3],"migration lost Act I quest state")
    rep["migration_roam"]=roam(emu,1200,need,"migrated save")
    need(rep["migration_roam"]["delta"]["moves_ok"]>0,"migrated beast did not roam")
    # Toggle ON (saves), check SRAM, then OFF again (saves), check SRAM.
    system_row(emu,need,14);emu.tap("A",hold=10,release=10);emu.step((),8);close_pause(emu,need)
    emu.step((),60);rep["migration_sram_on"]=rec_sram(emu)
    need(rep["migration_sram_on"].get("magic")=="LCL1" and rep["migration_sram_on"]["older_save"]==1 and rep["migration_sram_on"]["leash_on"]==1,f"migrated save did not write LCL1 with LEASH ON: {rep['migration_sram_on']}")
    system_row(emu,need,14);emu.tap("A",hold=10,release=10);emu.step((),8);close_pause(emu,need)
    emu.step((),60);rep["migration_sram"]=rec_sram(emu)
    need(rep["migration_sram"].get("magic")=="LCL1" and rep["migration_sram"]["leash_on"]==0 and emu.read_symbol("leash_on")==0,f"LEASH OFF not saved after migration: {rep['migration_sram']}")
    emu.screenshot(out/"09_migrated_save_roaming.png")
  rep["passed"]=True
 except Exception as exc:
  rep["failure"]=repr(exc);rep["traceback"]=traceback.format_exc()
 finally:
  (out/"leash_report.json").write_text(json.dumps(rep,indent=1)+"\n")
 print(json.dumps({k:v for k,v in rep.items() if k not in("traceback",)},indent=1)[:6000])
 if not rep["passed"]:raise SystemExit(rep.get("failure"))

if __name__=="__main__":
 ap=argparse.ArgumentParser()
 ap.add_argument("--rom",type=Path,default=ROOT/"LOST_COSMOS_V10_SOURCE/LOST_COSMOS_V10_OPENING_QA.gba")
 ap.add_argument("--elf",type=Path,default=ROOT/"LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.elf")
 ap.add_argument("--save",type=Path,default=ROOT/"artifacts/mgba_act1/act1_complete.sav")
 ap.add_argument("--old-save",type=Path,default=ROOT/"tests/fixtures/v11_7_act1_complete.sav")
 ap.add_argument("--out",type=Path,default=ROOT/"artifacts/mgba_leash")
 ap.add_argument("--record",action="store_true")
 a=ap.parse_args();run(a.rom.resolve(),a.elf.resolve(),a.save.resolve(),a.old_save.resolve() if a.old_save else None,a.out.resolve(),a.record)
