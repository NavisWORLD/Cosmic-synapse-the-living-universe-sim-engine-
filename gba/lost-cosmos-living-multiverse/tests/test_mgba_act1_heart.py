#!/usr/bin/env python3
"""ACT I: THE FIRST HEART (Q05-Q09), played in real mGBA with controller input only.

Starts from a controller-earned prologue save (Q04 done, Q05 active) and plays
Oakwood (Ravenswood, the Fallow Inn, Pell, the orchard, the branching market),
Aurel's journal, the Cragstone ascent, the temple's three rooms (Gallery of
Blades parry duels, the Cold Vault forged key, the rune order in the hall),
the Stone Regent (route "restore": three runes plus trust; route "fight":
parry and elemental counters), Malakar at the Heart and the First Axis.
Then it walks back down to Oakwood and cold-boots to CONTINUE.

The harness reads memory to decide when to press; it never writes emulated
state, loads savestates or teleports.
"""
import argparse, json, shutil, sys, traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from mgba import Mgba,sha256
from mgba_navigate import Navigator
sys.path.insert(0,str(Path(__file__).resolve().parent))
from test_mgba_menu_visual import goto_index

R=Path(__file__).resolve().parents[1]
CQ_LOCKED,CQ_ACTIVE,CQ_DONE=0,1,3
A1F={"MET_RAVEN":1,"PELL_HEALED":2,"MAP_FOUND":4,"MAP_RETURNED":8,"JOURNAL":16,"ASCENT":32,"GUARD":64,
     "MOULD":128,"ORE":256,"KEY":512,"VAULT_OPEN":1024,"KEEP":2048,"ORDER":4096,"MALAKAR":8192,"INN_GIFT":16384,"MIGRATED":32768}
TR={"TREE":210,"JOURNAL":211,"TO_ASCENT":212,"TO_OAKWOOD":213,"TO_TEMPLE":214,"CAMP":215,"LOOKOUT":216,"TO_ASCENT_TOP":217,
    "TO_GALLERY":218,"TO_VAULT":219,"HEART_DOOR":220,"TO_HALL":221,"GUARD_SEAL":222,"MURAL":223,"MOULD":224,"ORE":225,
    "FORGE":226,"VAULT_DOOR":227,"KEEP_SEAL":228,"REGENT":229,"HEART":230,"INSCRIPTION":231}

def wait(emu,pred,what,max_frames=900):
 for _ in range((max_frames+7)//8):
  if pred():return
  emu.step((),8)
 raise RuntimeError(f"{what} not reached after {max_frames} frames")
def cq(emu,i):return emu.read_symbol("cq_state",width=1,offset=i)
def a1(emu):return emu.read_symbol("a1_flags",width=2)
def snapshot(emu):
 return {"q":[cq(emu,i) for i in range(11)],"a1_flags":a1(emu),"regent":emu.read_symbol("a1_regent"),
         "reply":emu.read_symbol("a1_reply"),"sentries":emu.read_symbol("a1_sentries"),
         "story_flags":emu.read_symbol("story_flags"),"cores":emu.read_symbol("inv",width=1,offset=3),
         "world":emu.read_symbol("current_world"),"room":emu.read_symbol("current_room")}

def read_cards(emu,shots=None,prefix=""):
 n=0
 wait(emu,lambda:emu.read_symbol("pro_ui")==4,"story cards",600)
 while emu.read_symbol("pro_ui")==4:
  emu.step((),40)
  if shots is not None:shots(f"{prefix}_{n:02d}")
  emu.tap("A",hold=6,release=6);n+=1
  if n>12:raise RuntimeError("Story card loop did not end")
 return n

def settle(emu,nav,npc=None,max_frames=1800):
 """Wait for a fully built room (BG2 on, build cover gone, optional NPC)."""
 nav.wait_cinema(max_frames=2400)
 wait(emu,lambda:(emu.read16(0x04000000)&0x0400)!=0 and (npc is None or any(n.id==npc for n in nav.npcs())),
      f"room build (npc {npc})",max_frames)
 emu.step((),20);nav.wait_cinema(max_frames=2400)

def run(rom,elf,src_save,out,route,reply,record):
 out.mkdir(parents=True,exist_ok=True)
 save=out/"act1_heart.sav"
 shutil.copy2(src_save,save)
 rep={"suite":"real_mgba_act1_first_heart","rom_sha256":sha256(rom),"elf_sha256":sha256(elf),
      "source_save":str(src_save),"source_save_sha256":sha256(src_save),"route":route,"reply":reply,
      "controller_only":True,"state_writes":False,"savestates":False,"stages":[],"passed":False}
 with Mgba(rom,elf=elf,save_path=save,trace_path=out/"act1_heart_inputs.jsonl",watch_symbol="frame") as emu:
  nav=Navigator(emu)
  def mark(name):
   emu.screenshot(out/(name+".png"))
   s={"stage":name,"frame":emu.frame,**snapshot(emu)}
   rep["stages"].append(s);print("ACT1",json.dumps(s),flush=True)
  def need(cond,msg):
   if not cond:raise RuntimeError(msg+" :: "+json.dumps(snapshot(emu)))
  def go(value,at,room,npc=None,what=""):
   nav.interact(value,at=at)
   wait(emu,lambda:emu.read_symbol("current_room")==room,f"room {room} {what}",900)
   settle(emu,nav,npc)
  try:
   if record:emu.start_recording(out/"LOST_COSMOS_ACT1_FIRST_HEART.mp4")
   emu.step((),180)
   need(emu.read_symbol("v10_has_save")==1,"prologue save not recognised")
   emu.tap("DOWN",hold=12,release=12);emu.tap("A",hold=12,release=12)
   wait(emu,lambda:emu.read_symbol("intro")==0,"continue",1600);emu.step((),90)
   need(cq(emu,4)==CQ_DONE and cq(emu,5)==CQ_ACTIVE,"save is not at Q05")
   mark("00_continue_q05_active")
   if emu.read_symbol("game_mode")==1:
    nav.fly_to(0);settle(emu,nav)
   mark("01_landed_eridoria")
   if emu.read_symbol("current_room")==0:
    go(12,(20,48),2,14,"Brindlemark")
   mark("02_brindlemark")
   nav.talk_npc(14,advances=3,read_frames=60 if record else 0)
   go(12,(54,8),3,16,"Oakwood")
   need(cq(emu,5)==CQ_ACTIVE,"Q05 not active in Oakwood")
   mark("03_oakwood_market")
   # ---- Q05 Oakwood's Missing Map ----
   nav.talk_npc(16,advances=4,read_frames=90 if record else 0)
   need(a1(emu)&A1F["MET_RAVEN"],"Ravenswood did not ask about the map")
   mark("04_ravenswood_asks_for_the_map")
   nav.interact(TR["TREE"],at=(14,24))
   need(not a1(emu)&A1F["MAP_FOUND"],"map found before Pell's clue")
   mark("05_orchard_split_oak_before_clue")
   rep["potions_before_pell"]=emu.read_symbol("inv",width=1,offset=0)
   if rep["potions_before_pell"]==0:
    nav.talk_npc(32,advances=2,read_frames=60 if record else 0)
    need(a1(emu)&A1F["INN_GIFT"],"Bree did not give a potion for Pell")
   nav.talk_npc(33,advances=4,read_frames=90 if record else 0)
   need(a1(emu)&A1F["PELL_HEALED"],"Pell was not healed")
   mark("06_pell_healed_clue")
   nav.talk_npc(34,advances=3,read_frames=60 if record else 0)
   mark("07_gossip_wyn")
   nav.interact(TR["TREE"],at=(6,12))
   need(not a1(emu)&A1F["MAP_FOUND"],"wrong tree yielded the map")
   nav.interact(TR["TREE"],at=(14,24))
   need(a1(emu)&A1F["MAP_FOUND"],"split oak did not yield the map")
   mark("08_orchard_map_case")
   nav.talk_npc(16,advances=2,read_frames=60 if record else 0)
   read_cards(emu,mark if record else None,"09_raven_testimony")
   need(cq(emu,5)==CQ_DONE and cq(emu,6)==CQ_ACTIVE,"Q05 not completed")
   mark("10_q06_active")
   # ---- Q06 Ravenswood's Testimony ----
   nav.interact(TR["TO_ASCENT"],at=(54,12))
   need(emu.read_symbol("current_room")==3,"Cragstone gate opened before the journal")
   nav.interact(TR["JOURNAL"],at=(36,14))
   read_cards(emu,mark if record else None,"11_aurel_journal")
   need(cq(emu,6)==CQ_DONE and cq(emu,7)==CQ_ACTIVE and emu.read_symbol("story_flags")&2,"Q06 not completed")
   mark("12_q07_active")
   # Branching market (choice-dependent price list) and the inn.
   cr=emu.read_symbol("credits");pots=emu.read_symbol("inv",width=1,offset=0)
   nav.talk_npc(15,advances=3,read_frames=40 if record else 0)
   wait(emu,lambda:emu.read_symbol("pro_ui")==8,"Oakwood market",300)
   emu.step((),30);mark("13_oakwood_market_branch")
   emu.tap("A",hold=8,release=8);emu.step((),10)
   rep["market"]={"credits_before":cr,"credits_after":emu.read_symbol("credits"),
                  "potions_before":pots,"potions_after":emu.read_symbol("inv",width=1,offset=0),
                  "choice":emu.read_symbol("pro_choice")}
   need(rep["market"]["potions_after"]==pots+1 or cr<5,"market purchase failed")
   emu.tap("B",hold=8,release=8);emu.step((),10)
   need(emu.read_symbol("pro_ui")==0,"market did not close")
   # ---- Q07 Cragstone ----
   go(TR["TO_ASCENT"],(54,12),91,35,"ascent")
   mark("14_cragstone_ascent")
   nav.talk_npc(35,advances=4,read_frames=60 if record else 0)
   nav.interact(TR["LOOKOUT"],at=(54,22))
   mark("15_ascent_lookout_bridge")
   go(TR["TO_TEMPLE"],(32,2),4,17,"temple hall")
   read_cards(emu,mark if record else None,"16_temple_arrival")
   nav.interact(16,at=(42,22))
   need(not emu.read_symbol("story_flags")&4,"sockets accepted input before the seals")
   mark("17_sockets_dark")
   nav.interact(TR["HEART_DOOR"],at=(32,9))
   need(emu.read_symbol("current_room")==4,"heart door opened early")
   # West: Gallery of Blades.
   go(TR["TO_GALLERY"],(10,25),92,None,"gallery")
   mark("18_gallery_of_blades")
   nav.interact(TR["GUARD_SEAL"],at=(9,25))
   need(not a1(emu)&A1F["GUARD"],"guard seal woke with sentries standing")
   duels=[]
   for i in range(3):
    e=nav.enemies()[i];need(e.active,f"sentry {i} missing")
    nav.fight_enemy(i)
    duels.append({"sentry":i,"active_after":nav.enemies()[i].active})
    if i==0:mark("19_first_sentry_parried")
   rep["gallery_duels"]=duels
   need(emu.read_symbol("a1_sentries")==7,"sentries not all cleared")
   nav.interact(TR["MURAL"],at=(9,21));emu.step((),60 if record else 4)
   mark("20_gallery_mural")
   nav.interact(TR["GUARD_SEAL"],at=(9,25))
   read_cards(emu,mark if record else None,"21_rune_of_guard")
   need(a1(emu)&A1F["GUARD"],"rune of guard not taken")
   go(TR["TO_HALL"],(57,25),4,17,"hall from gallery")
   # East: Cold Vault.
   go(TR["TO_VAULT"],(55,25),93,None,"vault")
   mark("22_cold_vault")
   nav.interact(TR["FORGE"],at=(32,26))
   need(emu.read_symbol("pro_ui")==0,"forge opened without mould and ore")
   nav.interact(TR["VAULT_DOOR"],at=(44,26))
   need(not a1(emu)&A1F["VAULT_OPEN"],"vault door opened without a key")
   nav.interact(TR["MOULD"],at=(20,20))
   nav.interact(TR["ORE"],at=(24,33))
   need(a1(emu)&A1F["MOULD"] and a1(emu)&A1F["ORE"],"mould/ore not collected")
   nav.interact(TR["FORGE"],at=(32,26))
   need(emu.read_symbol("pro_ui")==7,"cold forge minigame did not open")
   emu.step((),20);mark("23_cold_forge_minigame")
   for strike in range(3):
    before=emu.read_symbol("a1_strikes")
    for _ in range(200):
     if emu.read_symbol("a1_heat")==11 and emu.read_symbol("a1_heat_dir")==0:break
     emu.step((),1)
    emu.step("A",2);emu.step((),6)
    need(emu.read_symbol("a1_strikes")==before+1 or emu.read_symbol("pro_ui")==4,f"forge strike {strike+1} missed")
   read_cards(emu,mark if record else None,"24_key_cast")
   need(a1(emu)&A1F["KEY"],"vault key not cast")
   nav.interact(TR["VAULT_DOOR"],at=(44,26))
   need(a1(emu)&A1F["VAULT_OPEN"],"vault door did not open with the key")
   settle(emu,nav)
   mark("25_vault_open")
   nav.interact(TR["INSCRIPTION"],at=(52,20));emu.step((),60 if record else 4)
   mark("26_vault_inscription")
   nav.interact(TR["KEEP_SEAL"],at=(52,26))
   read_cards(emu,mark if record else None,"27_rune_of_keeping")
   need(a1(emu)&A1F["KEEP"],"rune of keeping not taken")
   go(TR["TO_HALL"],(6,26),4,17,"hall from vault")
   # Rune order: one wrong attempt resets, then SKY ROOT HEART STAR.
   nav.interact(13,at=(21,22))
   need(emu.read_symbol("a1_rune_step")==0,"wrong first socket was accepted")
   mark("28_wrong_order_resets")
   for code,pos in [(15,(35,22)),(13,(21,22)),(16,(42,22)),(14,(28,22))]:
    nav.interact(code,at=pos)
   read_cards(emu,mark if record else None,"29_heart_door_opens")
   need(emu.read_symbol("story_flags")&4 and cq(emu,7)==CQ_DONE and cq(emu,8)==CQ_ACTIVE,"Q07 not completed")
   mark("30_q08_active")
   # ---- Q08 The Stone Regent ----
   go(TR["HEART_DOOR"],(32,9),94,None,"heart chamber")
   mark("31_heart_chamber_regent")
   nav.interact(TR["REGENT"],at=(32,32))
   read_cards(emu,mark if record else None,"32_regent_meets_arin")
   wait(emu,lambda:emu.read_symbol("game_mode")==3 and emu.read_symbol("a1_boss")==1,"Regent battle",300)
   emu.step((),30);mark("33_regent_battle")
   rep["regent_turns"]=regent_battle(emu,route,mark if record else None)
   read_cards(emu,mark if record else None,"34_regent_outcome")
   need(emu.read_symbol("a1_regent")==(2 if route=="restore" else 1),"Regent outcome wrong")
   need(cq(emu,8)==CQ_DONE and cq(emu,9)==CQ_ACTIVE,"Q08 not completed")
   mark("35_q09_active")
   # ---- Q09 The First Axis / Malakar ----
   nav.interact(TR["HEART"],at=(32,10))
   read_cards(emu,mark if record else None,"36_malakar")
   wait(emu,lambda:emu.read_symbol("pro_ui")==5,"reply to Malakar",300)
   if reply:emu.tap("DOWN",hold=8,release=8)
   emu.step((),20);mark("37_reply_to_malakar")
   emu.tap("A",hold=8,release=8)
   read_cards(emu,mark if record else None,"38_malakar_answers")
   wait(emu,lambda:emu.read_symbol("pro_ui")==6,"Malakar's lance",300)
   emu.step((),20);mark("39_malakar_lance")
   for k in range(2):
    before=emu.read_symbol("a1_deflects")
    for _ in range(200):
     if emu.read_symbol("a1_heat")==19 and emu.read_symbol("a1_heat_dir")==0:break
     emu.step((),1)
    emu.step("B",2);emu.step((),6)
    need(emu.read_symbol("a1_deflects")==before+1 or emu.read_symbol("pro_ui")==4,f"deflect {k+1} missed")
   read_cards(emu,mark if record else None,"40_first_axis")
   emu.step((),30)
   sf=emu.read_symbol("story_flags")
   need(sf&31==31 and cq(emu,9)==CQ_DONE and cq(emu,10)==CQ_ACTIVE and a1(emu)&A1F["MALAKAR"],"Act I not complete")
   rep["reward_cores"]=emu.read_symbol("inv",width=1,offset=3)
   mark("41_act1_complete")
   # The QUESTS page shows Act I done.
   emu.tap("START",hold=12,release=12)
   wait(emu,lambda:emu.read_symbol("game_mode")==2 and emu.read_symbol("pause_page")==0,"pause menu")
   goto_index(emu,1);emu.tap("A",hold=10,release=10);emu.step((),8)
   for _ in range(2):emu.tap("RIGHT",hold=8,release=8)
   emu.step((),20);mark("42_quests_story_view")
   for _ in range(4):
    emu.tap("B",hold=10,release=10);emu.step((),8)
    if emu.read_symbol("game_mode")==0:break
   # Walk back down to Oakwood through the real doors.
   go(TR["TO_HALL"],(32,59),4,17,"hall from chamber")
   go(TR["TO_ASCENT_TOP"],(32,55),91,35,"ascent top")
   go(TR["TO_OAKWOOD"],(32,62),3,16,"Oakwood return")
   nav.talk_npc(16,advances=2,read_frames=60 if record else 0)
   mark("43_back_in_oakwood")
   emu.step((),120)
   rep["final_live"]=snapshot(emu)
   if record:rep["recording"]=emu.stop_recording()
  except Exception as exc:
   rep["failure"]=repr(exc);rep["traceback"]=traceback.format_exc()
   try:emu.screenshot(out/"FAILED_FRAME.png")
   except Exception:pass
   (out/"act1_heart_report.json").write_text(json.dumps(rep,indent=2)+"\n");raise
 # Cold boot: CONTINUE restores Act I from SRAM.
 with Mgba(rom,elf=elf,save_path=save,trace_path=out/"act1_heart_coldboot_inputs.jsonl") as emu:
  emu.step((),180)
  if emu.read_symbol("v10_has_save")!=1:raise RuntimeError("Cold boot sees no save")
  emu.tap("DOWN",hold=12,release=12);emu.tap("A",hold=12,release=12)
  wait(emu,lambda:emu.read_symbol("intro")==0,"continue",1600);emu.step((),120)
  got=snapshot(emu);rep["cold_boot"]=got
  emu.screenshot(out/"44_cold_boot_continue.png")
  if got!=rep["final_live"]:raise RuntimeError(f"Cold boot lost Act I: {got} vs {rep['final_live']}")
 shutil.copy2(save,out/"act1_complete.sav")
 rep["passed"]=True
 (out/"act1_heart_report.json").write_text(json.dumps(rep,indent=2)+"\n")
 print(json.dumps({"passed":True,"route":route,"reply":reply,"cold_boot":rep["cold_boot"]},indent=2))

def regent_battle(emu,route,shots):
 """Drive the Regent with the d-pad, A and B. Restore route: parry the slam,
 then RESTORE with a rune (three times). Fight route: parry or counter the
 core element, then strike."""
 turns=[];begin=emu.frame;shot=0
 COUNTER={1:2,2:3,3:1}
 def to_cursor(target):
  for _ in range(8):
   c=emu.read_symbol("a1_rg_cursor")
   if c==target:return
   if (c&1)!=(target&1):emu.tap("RIGHT",hold=4,release=4)
   elif (c>>1)<(target>>1):emu.tap("DOWN",hold=4,release=4)
   else:emu.tap("UP",hold=4,release=4)
  if emu.read_symbol("a1_rg_cursor")!=target:raise RuntimeError("Regent menu cursor failed")
 braced=False
 while emu.read_symbol("a1_boss")==1 or emu.read_symbol("game_mode")==3:
  if emu.frame-begin>40000:raise RuntimeError("Regent battle exceeded its input budget")
  ph=emu.read_symbol("a1_rg_phase")
  if ph==0:
   braced=False
   opened=emu.read_symbol("a1_rg_open") or emu.read_symbol("a1_rg_stagger")
   core=emu.read_symbol("a1_rg_core");mp=emu.read_symbol("player_mp");hp=emu.read_symbol("player",width=1,offset=7) if False else None
   if route=="restore":
    act=5 if opened else (0 if core==0 else ((COUNTER[core]%3)+1 if mp>=2 else 0))
   else:
    act=0 if opened or core==0 or mp<2 else COUNTER[core]
   to_cursor(act);emu.tap("A",hold=4,release=4);emu.step((),4)
   turns.append({"frame":emu.frame,"action":["FIGHT","EMBER","TIDE","BLOOM","POTION","RESTORE"][act],"core":core,
                 "opened":bool(opened),"regent_hp":emu.read_symbol("a1_rg_hp",signed=True,width=2),
                 "runes":emu.read_symbol("a1_rg_runes")})
   if shots and shot<3 and act in (5,COUNTER.get(core,9)):shots(f"33_regent_turn_{shot}");shot+=1
  elif ph==1:
   if not braced and emu.read_symbol("a1_rg_tell")==0 and emu.read_symbol("a1_rg_timer")<=36:
    emu.tap("B",hold=3,release=2);braced=True
   else:emu.step((),2)
  else:emu.step((),4)
  if emu.read_symbol("game_mode")!=3 and emu.read_symbol("a1_boss")==0:break
 return turns

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--rom",type=Path,default=R/"LOST_COSMOS_V10_SOURCE/LOST_COSMOS_V10_OPENING_QA.gba")
 p.add_argument("--elf",type=Path,default=R/"LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.elf")
 p.add_argument("--save",type=Path,required=True,help="controller-earned prologue save (Q05 active)")
 p.add_argument("--out",type=Path,default=R/"artifacts/mgba_act1_heart")
 p.add_argument("--route",choices=("restore","fight"),default="restore")
 p.add_argument("--reply",type=int,choices=(0,1),default=0)
 p.add_argument("--record",action="store_true")
 a=p.parse_args();run(a.rom.resolve(),a.elf.resolve(),a.save.resolve(),a.out.resolve(),a.route,a.reply,a.record)
