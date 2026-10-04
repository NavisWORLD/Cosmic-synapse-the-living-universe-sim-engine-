#!/usr/bin/env python3
"""Actual native cartridge: earned eight-region progress, bosses, menus and SRAM.
All state changes use ordinary buttons. ELF reads guide input; no memory writes
or savestates. Failing paths produce screenshots and an incomplete report.
"""
from pathlib import Path
import argparse,json,struct,sys,traceback,shutil
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from mgba import Mgba,sha256
from mgba_navigate import Navigator
CAT=json.loads((R/'content/v11_1_catalog.json').read_text())
PAGES={1:0,11:1,18:2,4:3,5:4,28:5,20:6,26:8,9:9}
def run(rom,elf,out,starter=None):
 out.mkdir(parents=True,exist_ok=True);save=out/'expedition_earned.sav'
 if starter:shutil.copyfile(starter,save)
 elif save.exists():save.unlink()
 report=dict(rom_sha256=sha256(rom),elf_sha256=sha256(elf),controller_only=True,memory_writes=False,savestates=False,passed=False,stages=[])
 with Mgba(rom,elf=elf,save_path=save,trace_path=out/'controller_inputs.jsonl') as e:
  nav=Navigator(e)
  def val(n,**kw):return e.read_symbol(n,**kw)
  def tap(k):e.tap(k,hold=12,release=12)
  def wait(pred,label,budget=2500):
   for _ in range(budget//8):
    if pred():return
    e.step((),8)
   raise RuntimeError('Timed out: '+label)
  def mark(name):
   e.screenshot(out/(name+'.png'));s=dict(name=name,frame=e.frame,room=val('current_room'),level=val('player_level'),hp=val('v11_hp'),credits=val('v11_credits'),beacons=val('v11_beacons'),bosses=val('v11_boss_done'))
   report['stages'].append(s);print('CONTENT',s,flush=True)
  def menu(page):
   if val('game_mode')!=2:tap('START')
   for _ in range(5):
    if val('pause_page')==0:break
    tap('B')
   if page==40:tap('SELECT')
   else:
    target=PAGES[page]
    for _ in range(16):
     cur=val('pause_sel')
     if cur==target:break
     tap('RIGHT' if target>=5 and cur<5 else 'LEFT' if target<5 and cur>=5 else 'DOWN')
    tap('A')
   wait(lambda:val('pause_page')==page and val('v11_ui_dirty')==0,'menu '+str(page));e.step((),16)
  def close():
   for _ in range(7):
    if val('game_mode')!=2:return
    tap('B')
   raise RuntimeError('B did not close menus')
  def select(symbol,target,count):
   for _ in range(count+2):
    cur=val(symbol)
    if cur==target:return
    tap('DOWN' if (target-cur)%count <= (cur-target)%count else 'UP')
   raise RuntimeError('Could not select '+symbol)
  def listed(id,symbol='v11_sel',battle=False):
   e.step((),16);n=val('v11_list_count');ids=list(e.read_range(e.symbols['v11_list'].address,n))
   if id not in ids:raise RuntimeError('Item/skill absent '+str(id)+' in '+str(ids))
   select(symbol,ids.index(id),n)
  def npc(id,shop=False):
   ids=list(e.read_range(e.symbols['v11_npc_id'].address,val('v11_npc_count')))
   if id not in ids:raise RuntimeError('Missing NPC '+str(id))
   i=ids.index(id);x=val('v11_npc_x',width=2,offset=i*2,signed=True);y=val('v11_npc_y',width=2,offset=i*2,signed=True)
   # Interaction scan prioritizes pickups; approach outside any nearby trigger.
   for xx,yy in [(x,y+16),(x-16,y),(x+16,y),(x,y-16)]:
    try:nav.walk_to(xx,yy,tolerance=2)
    except RuntimeError:continue
    t,_=nav.nearby_trigger(nav.triggers(),*nav.position())
    if not t:break
   tap('A');wait(lambda:val('v11_dialogue')!=0,'NPC dialog')
   for _ in range(30):
    if not val('v11_dialogue'):break
    tap('A')
   if shop:wait(lambda:val('v11_shop')!=0,'shop')
   elif val('game_mode')==2:close()
   if val('v11_shop') and not shop:tap('B')
  def bag_room():
   qty=e.read_range(e.symbols['v11_qty'].address,100)
   while sum(bool(q) for q in qty)>26:
    gear=list(e.read_range(e.symbols['v11_equipment'].address,3))
    item=next((i for i in range(70) if qty[i] and i not in gear),None)
    if item is None:break
    menu(4);listed(item);tap('A');tap('DOWN');tap('A');tap('B');close()
    qty=e.read_range(e.symbols['v11_qty'].address,100)
  def equip(slot,id):
   menu(5);select('v11_sel',slot,3);tap('A');listed(id);tap('A');close()
   assert val('v11_equipment',width=1,offset=slot)==id
  def assign():
   learned=e.read_range(e.symbols['v11_learned'].address,13)
   candidates=[i for i in range(20) if i!=18 and learned[i//8]>>(i%8)&1 and CAT['skills'][i]['power']>0]
   if not candidates:return
   best=max(candidates,key=lambda i:CAT['skills'][i]['power']);menu(28)
   while val('v11_sub'):tap('LEFT')
   listed(best);tap('A');tap('A');close()
  def rest():nav.interact(113,at=(30,53));e.step((),24)
  def field_skill(id,workshop=False):
   menu(28)
   while val('v11_sub')!=4:tap('RIGHT')
   listed(id);tap('A')
   if workshop:
    wait(lambda:val('pause_page')==41,'Assemble workshop')
    if val('v11_detail')==2:tap('B')
   else:tap('B');close()
  def battle(slot):
   foe=next(z for z in nav.enemies() if z.index==slot and z.active)
   foes=[z for z in nav.enemies() if z.active];triggers=nav.triggers()
   npcs=[(val('v11_npc_x',width=2,offset=i*2,signed=True),val('v11_npc_y',width=2,offset=i*2,signed=True)) for i in range(val('v11_npc_count'))]
   def approach(start,board):
    goals=set()
    for x in range(foe.x-46,foe.x+47):
     for y in range(foe.y-46,foe.y+47):
      if x%2!=start[0]%2 or y%2!=start[1]%2 or abs(x-foe.x)+abs(y-foe.y)>=48:continue
      if not nav.can_stand(board,x,y) or nav.nearby_trigger(triggers,x,y)[0]:continue
      if any(abs(x-nx)+abs(y-ny)<28 for nx,ny in npcs):continue
      nearest=min(foes,key=lambda z:(abs(x-z.x)+abs(y-z.y),z.index))
      if nearest.index==slot:goals.add((x,y))
    return goals
   nav._walk(approach)
   tap('A');wait(lambda:val('game_mode')==3,'battle entry')
   assert val('battle_index')==slot,('Wrong native enemy selected',slot,val('battle_index'))
   id=val('v11_enemy_id',width=1,offset=slot);e.screenshot(out/f'battle_{id:03d}.png')
   for turn in range(300):
    if val('v11_gameover'):raise RuntimeError('Defeated by '+str(id)+' after '+str(turn))
    if val('game_mode')!=3:break
    if val('battle_phase')!=0:e.step((),8);continue
    hp=val('v11_hp');mp=val('v11_mp');qty=e.read_range(e.symbols['v11_qty'].address,100)
    if hp<max(14,CAT['characters'][id]['atk']+5) and any(qty[i] for i in [78,79,89,74,72,73,70]):
     select('battle_cursor',2,6) if False else None
     # Cursor grid: vertical advances by two, horizontal changes column.
     action=2
    elif id==99 and qty[94]:action=3
    elif val('v11_ult_charge')==100 and val('v11_ultimate')<90:
     tap('SELECT');continue
    elif id!=92 and val('v11_shortcuts',width=1)<30 and mp>=CAT['skills'][val('v11_shortcuts',width=1)]['mp']:action=1
    else:action=0
    for _ in range(6):
     cur=val('battle_cursor')
     if cur==action:break
     tap('RIGHT' if cur%2!=action%2 else 'DOWN')
    # Cinder Maw rewards moving between decisions.
    if id==93 and val('battle_cursor')==action:tap('RIGHT');tap('LEFT')
    tap('A')
    sub=val('v11_battle_sub')
    if sub==1:tap('A')
    elif sub==2:
     ids=list(e.read_range(e.symbols['v11_list'].address,val('v11_list_count')))
     item=next(i for i in [78,79,89,74,72,73,70] if i in ids);listed(item,'v11_battle_sel',True);tap('A')
    elif sub==4:tap('A')
   else:raise RuntimeError('Battle did not resolve '+str(id))
   wait(lambda:val('game_mode')==0,'battle result');e.step((),24)
   if id>=90:assert val('v11_boss_done')&(1<<(id-90)),('Major boss not earned',id)
  try:
   e.step((),180);tap('A');wait(lambda:val('v10_opening')==1,'opening');tap('START');wait(lambda:any(n.id==14 for n in nav.npcs()) and not val('v10_opening'),'Brindlemark');e.step((),32)
   nav.interact(110,at=(34,44));wait(lambda:val('current_room')==70 and val('v11_npc_count')>0,'new Prime road');e.step((),180);mark('01_prime_field')
   for w in range(7):
    assert val('current_room')==70+w
    bag_room()
    for index,(x,y) in enumerate([(13,45),(50,43),(16,24),(49,25)]):
     nav.interact(115,at=(x,y));e.step((),12)
    nav.interact(116,at=(32,10));nav.interact(117,at=(27,30))
    if w in [0,2,5,6]:nav.interact(116,at=(18,12))
    if w==0:npc(2);nav.interact(119,at=(32,32));equip(0,11);equip(1,36);equip(2,62)
    if w==5:
     npc(19)
     for x in [28,32,36]:nav.interact(118,at=(x,14))
    if w==1:field_skill(94)
    if w==2:
     assert e.read_range(e.symbols['collision'].address+18*64+39,1)==b'\x01';field_skill(95)
     assert e.read_range(e.symbols['collision'].address+18*64+39,1)==b'\x00'
    if w==3:
     npc(12);field_skill(92);menu(1);tap('START');wait(lambda:val('pause_page')==47,'local Track map');mark('04_local_tracking');close()
    if w==6:field_skill(90);assert val('v11_field_light')==1
    for slot in range(3):rest();assign();battle(slot)
    if w==0:npc(0);npc(1);npc(4)
    if w==6:npc(29);npc(21)
    nav.interact(114,at=(45,16));mark(f'{w+2:02d}_beacon_world_{w}')
    if w==6:rest();assign();battle(9);bag_room();assert val('v11_qty',width=1,offset=92)==1
    nav.interact(112,at=(54,52));wait(lambda:val('current_room')==71+w and val('v11_npc_count')>0,'next world');e.step((),80)
   # Crown: three apples and the eighth signal earned through its own fights.
   bag_room()
   for x,y in [(13,45),(50,43),(16,24),(49,25)]:nav.interact(115,at=(x,y))
   nav.interact(116,at=(32,10));nav.interact(117,at=(27,30))
   for slot in range(3):rest();assign();battle(slot)
   nav.interact(114,at=(45,16));assert val('v11_beacons')==255;mark('09_all_eight_signals')
   # Return through lit beacons and defeat every main boss using earned gear.
   for w in [0,1,2,3,4,5,6,7]:
    menu(1);select('v11_sel',w,8);tap('A');wait(lambda:val('game_mode')==0 and val('current_room')==70+w,'lit-beacon travel');e.step((),80)
    rest();assign()
    if w==5:
     for x in [28,32,36]:nav.interact(118,at=(x,14))
    if w==6:
     ids=list(e.read_range(e.symbols['v11_enemy_id'].address,10));slot=ids.index(91);battle(slot)
    if w!=6:battle(9)
    mark(f'10_boss_world_{w}')
   # The Quiet only appears after the Crown and all signals; re-enter legitimately.
   menu(1);select('v11_sel',7,8);tap('A');wait(lambda:val('game_mode')==0,'Crown return');e.step((),80)
   rest();assign();e.start_recording(out/'v11_finale_and_beastbox.mp4');ids=list(e.read_range(e.symbols['v11_enemy_id'].address,10));battle(ids.index(99));assert val('v11_boss_done')==1023;mark('20_true_quiet_defeated')
   # Craft the Builder's set from genuinely earned finite materials.
   bag_room();field_skill(97,workshop=True)
   for recipe in [0,1,2,10]:select('v11_sel',recipe,11);tap('A');tap('B')
   close();assert all(val('v11_qty',width=1,offset=i) for i in [22,49,67]);assert val('v11_quest_done')&(1<<14)
   # Four real equipped passives; a fifth is rejected by the native UI.
   menu(28)
   while val('v11_sub')!=2:tap('RIGHT')
   for id in [50,59,69,74]:listed(id);tap('A')
   before=e.read_range(e.symbols['v11_passives'].address,4);listed(67);tap('A');assert e.read_range(e.symbols['v11_passives'].address,4)==before;tap('B');close()
   assert val('v11_passives',width=1,offset=2)==69
   # Train, evolve and rename the same public identity through ordinary controls.
   menu(18);tap('A');select('v11_sel',1,7)
   for _ in range(2):tap('A');tap('B')
   select('v11_sel',2,7);tap('A');tap('A');wait(lambda:val('pause_page')==18 and not val('v11_evolution'),'earned evolution')
   assert val('lc_party',width=1,offset=5)==1
   tap('A');select('v11_sel',4,7);tap('A')
   for ch in 'STAY':
    target=ord(ch)-ord('A')
    for _ in range(28):
     cur=val('v11_rename_letter')
     if cur==target:break
     tap('RIGHT' if (target-cur)%27<=(cur-target)%27 else 'LEFT')
    tap('A')
   tap('SELECT');tap('A');mark('21_bonded_evolved_renamed')
   select('v11_sel',5,7);tap('A');tap('B');close();assert val('v11_export_ready')==1
   report['slots']=[]
   for slot in range(3):
    menu(9)
    if slot:select('v11_sel',0 if slot==1 else 2,11);tap('A')
    report['slots'].append(dict(slot=slot,audio=val('audio_on'),brightness=val('v11_brightness')))
    select('v11_sel',3,11);tap('A');select('v11_sel',slot,3);tap('A');tap('B');close()
   mark('22_three_manual_saves');e.stop_recording()
   e.export_save(save);report['route_passed']=True;report['beacons']=val('v11_beacons');report['bosses']=val('v11_boss_done');report['level']=val('player_level')
  except Exception as exc:
   report['failure']=repr(exc);report['traceback']=traceback.format_exc();e.screenshot(out/'FAILED.png');raise
  finally:(out/'content_controller_report.json').write_text(json.dumps(report,indent=2)+'\n')
 with Mgba(rom,elf=elf,save_path=save) as e:
  e.step((),180);e.tap('DOWN',hold=12,release=12);e.tap('A',hold=12,release=12);e.step((),600)
  assert e.read_symbol('v11_beacons')==255 and e.read_symbol('v11_boss_done')==1023
  for slot in report['slots']:
   menu(9);select('v11_sel',4,11);tap('A');select('v11_sel',slot['slot'],3);tap('A');tap('A');wait(lambda:val('game_mode')==0,'cold manual slot load');e.step((),180)
   assert val('audio_on')==slot['audio'] and val('v11_brightness')==slot['brightness']
   assert val('v11_beacons')==255 and val('v11_boss_done')==1023
  report['cold_boot_passed']=True;report['manual_slot_loads_passed']=True;report['passed']=True;(out/'content_controller_report.json').write_text(json.dumps(report,indent=2)+'\n');e.screenshot(out/'23_cold_boot_progress.png')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--out',type=Path,default=R/'artifacts/v11_content');a.add_argument('--rom',type=Path,default=R/'LOST_COSMOS_V10_SOURCE/LOST_COSMOS_V10_OPENING_QA.gba');a.add_argument('--elf',type=Path,default=R/'LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.elf');a.add_argument('--starter',type=Path);o=a.parse_args();run(o.rom,o.elf,o.out,o.starter)
