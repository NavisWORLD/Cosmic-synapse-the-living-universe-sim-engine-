#!/usr/bin/env python3
"""PROLOGUE: ASH IN THE FORGE, played in real mGBA with controller input only.

Covers Q00-Q04: forge minigame, Brindlemark raid (one fight, one or more
mercies), the storehouse/injured choice (branch selectable), Mira's fuse,
the beacon seats, the traveler, Astrid at the Origin, LUNA-ARC launch and
its rewards, then a native cold boot that CONTINUEs the saved campaign.
The harness reads memory to decide when to press; it never writes emulated
state, loads savestates or teleports.
"""
import argparse, json, sys, traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from mgba import Mgba,sha256
from mgba_navigate import Navigator
sys.path.insert(0,str(Path(__file__).resolve().parent))
from test_mgba_menu_visual import goto_index

R=Path(__file__).resolve().parents[1]
CQ_ACTIVE,CQ_DONE=1,3
PF={"FORGED":1,"COSMOS":2,"RAID_CLEAR":4,"CHOICE":8,"FUSE":16,"BEACON":32,"TRAVELER":64,
    "ASTRID":128,"MIRA":256,"LAUNCH":1024,"FORGE_KEY":2048,"MAP":4096,"MIGRATED":8192}

def wait(emu,pred,what,max_frames=900):
 for _ in range((max_frames+7)//8):
  if pred():return
  emu.step((),8)
 raise RuntimeError(f"{what} not reached after {max_frames} frames")

def cq(emu,i):return emu.read_symbol("cq_state",width=1,offset=i)
def flags(emu):return emu.read_symbol("pro_flags",width=2)

def read_cards(emu,shots=None,prefix=""):
 """Advance real story cards with A, capturing each one."""
 n=0
 wait(emu,lambda:emu.read_symbol("pro_ui")==4,"story cards",600)
 while emu.read_symbol("pro_ui")==4:
  emu.step((),40)
  if shots is not None:shots(f"{prefix}_{n:02d}")
  emu.tap("A",hold=6,release=6);n+=1
  if n>12:raise RuntimeError("Story card loop did not end")
 return n

def forge(emu,mark):
 if emu.read_symbol("pro_ui")!=1:raise RuntimeError("A at the furnace did not open the forge")
 emu.step((),20);mark("02_forge_minigame")
 for strike in range(3):
  before=emu.read_symbol("pro_strikes")
  for _ in range(200):
   if emu.read_symbol("pro_heat")==11 and emu.read_symbol("pro_heat_dir")==0:break
   emu.step((),1)
  emu.step("A",2);emu.step((),6)
  if emu.read_symbol("pro_strikes")!=before+1:raise RuntimeError(f"Timed strike {strike+1} missed")
  if strike==1:mark("03_forge_second_strike")
 # The third strike saves to SRAM before the awakening cards open.
 wait(emu,lambda:emu.read_symbol("pro_ui")==4,"COSMOS awakening cards",600)

def battle_mercy(emu,nav,index):
 for _ in range(12):
  e=nav.enemies()[index]
  if not e.active:return
  nav.walk_to(e.x,e.y,tolerance=26)
  e=nav.enemies()[index];x,y=nav.position()
  if abs(x-e.x)+abs(y-e.y)>=46:continue
  emu.tap(("A","SELECT"),hold=8,release=4)
  if emu.read_symbol("game_mode")!=3:raise RuntimeError("A+SELECT did not open a duel")
  for _ in range(8):
   if emu.read_symbol("battle_cursor")==3:break
   emu.tap("RIGHT" if emu.read_symbol("battle_cursor")%2==0 else "DOWN",hold=4,release=4)
  if emu.read_symbol("battle_cursor")!=3:raise RuntimeError("TALK not selected")
  emu.tap("A",hold=4,release=4);emu.step((),10)
  return
 raise RuntimeError("Could not reach glitchling for mercy")

def run(rom,elf,out,choice,record):
 out.mkdir(parents=True,exist_ok=True)
 save=out/"prologue.sav"
 if save.exists():save.unlink()
 rep={"suite":"real_mgba_prologue_q00_q04","rom_sha256":sha256(rom),"elf_sha256":sha256(elf),
      "controller_only":True,"state_writes":False,"choice":choice,"stages":[],"passed":False}
 with Mgba(rom,elf=elf,save_path=save,trace_path=out/"prologue_inputs.jsonl",watch_symbol="frame") as emu:
  nav=Navigator(emu)
  def mark(name):
   emu.screenshot(out/(name+".png"))
   rep["stages"].append({"stage":name,"frame":emu.frame,"q":[cq(emu,i) for i in range(6)],
     "pro_flags":flags(emu),"loc":list(nav.location()),"pos":list(nav.position())})
  try:
   if record:emu.start_recording(out/"prologue.mkv")
   emu.step((),180)
   emu.tap("A",hold=12,release=12)
   wait(emu,lambda:emu.read_symbol("v10_opening")==1,"opening")
   emu.tap("START",hold=12,release=12)
   wait(emu,lambda:(emu.read16(0x04000000)&0x0400)!=0 and any(n.id==14 for n in nav.npcs()),"Brindlemark",1800)
   emu.step((),30)
   if cq(emu,0)!=CQ_ACTIVE:raise RuntimeError("New game did not start Q00")
   ids={n.id for n in nav.npcs()}
   if not {14,30,31}<=ids:raise RuntimeError(f"Prologue cast missing in Brindlemark: {ids}")
   mark("01_ash_in_the_forge_q00")
   # Q00 forge
   nav.interact(8,at=(18,43))
   forge(emu,mark)
   if cq(emu,0)!=CQ_DONE or cq(emu,1)!=CQ_ACTIVE or not flags(emu)&PF["COSMOS"]:raise RuntimeError("Forge did not complete Q00")
   read_cards(emu,mark if record else None,"04_cosmos_awakens")
   wait(emu,lambda:[e.active for e in nav.enemies()[:3]]==[1,1,1],"three raid glitchlings",600)
   emu.step((),30)
   mark("05_raid_q01")
   # Q01 raid: one fought in a duel, the rest spared with TALK
   nav.fight_enemy(0);mark("06_raid_fought")
   battle_mercy(emu,nav,1)
   wait(emu,lambda:emu.read_symbol("game_mode")==0,"mercy exit",600)
   mark("07_raid_mercy")
   battle_mercy(emu,nav,2)
   wait(emu,lambda:emu.read_symbol("pro_ui")==4,"raid aftermath",900)
   rep["raid"]={"defeated":emu.read_symbol("pro_raid_kills"),"spared":emu.read_symbol("pro_raid_spared")}
   if rep["raid"]!={"defeated":1,"spared":2}:raise RuntimeError(f"Raid tally wrong {rep['raid']}")
   read_cards(emu)
   if emu.read_symbol("pro_ui")!=3:raise RuntimeError("Choice did not open")
   if choice==2:emu.tap("DOWN",hold=6,release=6)
   emu.step((),10);mark("08_first_choice")
   cred=emu.read_symbol("credits");emu.tap("A",hold=6,release=6)
   rep["credits_gain"]=emu.read_symbol("credits")-cred
   read_cards(emu,mark if record else None,"09_choice_outcome")
   if emu.read_symbol("pro_choice")!=choice or cq(emu,1)!=CQ_DONE or cq(emu,2)!=CQ_ACTIVE:raise RuntimeError("Choice did not finish Q01")
   # Q02 beacon
   nav.interact(200,at=(33,10))
   if emu.read_symbol("pro_ui")==2:raise RuntimeError("Beacon opened without the fuse")
   emu.step((),30)
   nav.talk_npc(30,advances=3,read_frames=60 if record else 0)
   if not flags(emu)&PF["FUSE"]:raise RuntimeError("Mira did not hand over the fuse")
   nav.interact(200,at=(33,10))
   if emu.read_symbol("pro_ui")!=2:raise RuntimeError("Beacon seats did not open")
   emu.tap("RIGHT",hold=6,release=6)  # a real wrong turn: seats must reset
   if emu.read_symbol("pro_seat")!=0:raise RuntimeError("Wrong seat was accepted")
   mark("10_beacon_sparks")
   for k in ("LEFT","UP"):emu.tap(k,hold=6,release=6)
   mark("11_beacon_two_seats")
   emu.tap("RIGHT",hold=6,release=6)
   if not flags(emu)&PF["BEACON"]:raise RuntimeError("Beacon not lit")
   read_cards(emu,mark if record else None,"12_beacon_lit")
   if cq(emu,2)!=CQ_DONE or cq(emu,3)!=CQ_ACTIVE:raise RuntimeError("Beacon did not finish Q02")
   # Q03
   nav.talk_npc(30,advances=3,read_frames=60 if record else 0)
   nav.talk_npc(31,advances=3,read_frames=60 if record else 0)
   mark("13_q03_mira_traveler")
   if flags(emu)&(PF["MIRA"]|PF["TRAVELER"])!=PF["MIRA"]|PF["TRAVELER"]:raise RuntimeError("Mira/traveler not recorded")
   nav.interact(12,at=(8,54))
   wait(emu,lambda:nav.location()==(0,0,1) and any(n.id==13 for n in nav.npcs()),"Origin with Astrid",1800)
   emu.step((),20)
   nav.talk_npc(13,advances=3,read_frames=60 if record else 0)
   if cq(emu,3)!=CQ_DONE or cq(emu,4)!=CQ_ACTIVE:raise RuntimeError("Q03 not complete after Astrid")
   mark("14_q04_origin_pad")
   # The campaign is visible in the real pause menu: QUESTS -> STORY.
   emu.tap("START",hold=12,release=12)
   wait(emu,lambda:emu.read_symbol("game_mode")==2 and emu.read_symbol("pause_page")==0,"pause menu")
   goto_index(emu,1);emu.tap("A",hold=10,release=10);emu.step((),8)
   if emu.read_symbol("pause_page")!=11:raise RuntimeError("QUESTS page did not open")
   for _ in range(2):emu.tap("RIGHT",hold=8,release=8)
   emu.step((),8)
   if emu.read_symbol("v11_sub")!=2:raise RuntimeError("STORY quest view not reached")
   mark("14b_quests_story_view")
   for _ in range(4):
    emu.tap("B",hold=10,release=10);emu.step((),8)
    if emu.read_symbol("game_mode")==0:break
   if emu.read_symbol("game_mode")!=0:raise RuntimeError("Could not close the pause menu")
   # Q04 launch
   nav.interact(1)
   if emu.read_symbol("pro_ui")!=4:raise RuntimeError("Launch cards did not open")
   read_cards(emu,mark if record else None,"15_launch")
   wait(emu,lambda:emu.read_symbol("game_mode")==1,"LUNA-ARC in space",900)
   nav.wait_cinema(max_frames=2400)
   emu.step((),30)
   if cq(emu,4)!=CQ_DONE or cq(emu,5)!=CQ_ACTIVE:raise RuntimeError("Q04 not complete")
   need=PF["LAUNCH"]|PF["FORGE_KEY"]|PF["MAP"]
   if flags(emu)&need!=need:raise RuntimeError("Rewards missing")
   mark("16_luna_arc_space")
   rep["final_live"]={"q":[cq(emu,i) for i in range(6)],"pro_flags":flags(emu),"choice":emu.read_symbol("pro_choice")}
   emu.step((),120)
   if record:rep["recording"]=emu.stop_recording()
  except Exception as exc:
   rep["failure"]=repr(exc);rep["traceback"]=traceback.format_exc()
   try:emu.screenshot(out/"FAILED_FRAME.png")
   except Exception:pass
   (out/"prologue_report.json").write_text(json.dumps(rep,indent=2)+"\n");raise
 # Cold boot: CONTINUE must restore the campaign from SRAM.
 with Mgba(rom,elf=elf,save_path=save,trace_path=out/"prologue_coldboot_inputs.jsonl") as emu:
  emu.step((),180)
  if emu.read_symbol("v10_has_save")!=1:raise RuntimeError("Cold boot sees no save")
  emu.tap("DOWN",hold=12,release=12);emu.tap("A",hold=12,release=12)
  wait(emu,lambda:emu.read_symbol("intro")==0,"continue",1600);emu.step((),120)
  got={"q":[cq(emu,i) for i in range(6)],"pro_flags":flags(emu),"choice":emu.read_symbol("pro_choice")}
  rep["cold_boot"]=got
  emu.screenshot(out/"17_cold_boot_continue.png")
  if got!=rep["final_live"]:raise RuntimeError(f"Cold boot lost campaign: {got} vs {rep['final_live']}")
 rep["passed"]=True
 (out/"prologue_report.json").write_text(json.dumps(rep,indent=2)+"\n")
 print(json.dumps({"passed":True,"choice":choice,"raid":rep["raid"],"cold_boot":rep["cold_boot"]},indent=2))

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--rom",type=Path,default=R/"LOST_COSMOS_V10_SOURCE/LOST_COSMOS_V10_OPENING_QA.gba")
 p.add_argument("--elf",type=Path,default=R/"LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.elf")
 p.add_argument("--out",type=Path,default=R/"artifacts/mgba_prologue")
 p.add_argument("--choice",type=int,choices=(1,2),default=1)
 p.add_argument("--record",action="store_true")
 a=p.parse_args();run(a.rom.resolve(),a.elf.resolve(),a.out.resolve(),a.choice,a.record)
