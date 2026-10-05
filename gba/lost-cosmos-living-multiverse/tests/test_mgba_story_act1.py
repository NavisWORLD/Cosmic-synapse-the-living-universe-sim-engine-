#!/usr/bin/env python3
"""Act I on the real cartridge, controller only: the Listener, a flower spark
battle that exercises Fight, Befriend, Potion and Run, the Lys rival battle,
all eight signals, the Quiet and the crown listener. Then a cold boot proves
CONTINUE restores the finished act. ELF reads only guide input; there are no
memory writes or savestates. Optional --record writes a short clip with the
cartridge's own audio of the opening and the first spark battle.
"""
from pathlib import Path
import argparse,json,struct,sys,traceback,shutil
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from mgba import Mgba,sha256
from mgba_navigate import Navigator
CAT=json.loads((R/'content/v11_1_catalog.json').read_text())
PAGES={1:0,11:1,18:2,4:3,5:4,28:5,20:6,26:8,9:9}
def run(rom,elf,out,record=None):
 out.mkdir(parents=True,exist_ok=True);save=out/'act1_story.sav'
 if save.exists():save.unlink()
 report=dict(rom_sha256=sha256(rom),elf_sha256=sha256(elf),controller_only=True,memory_writes=False,savestates=False,passed=False,stages=[],story={})
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
   if 'lc_song' in e.symbols:s['song']=val('lc_song')
   report['stages'].append(s);print('ACT1',s,flush=True)
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
  def note():return e.read_range(e.symbols['v11_notice'].address,90).split(b'\0')[0].decode()
  def flags():return val('v11_story_flags')
  def wsel(t):
   for _ in range(5):
    c=val('v11_wild_sel')
    if c==t:return
    tap('DOWN' if (c^t)&2 else 'RIGHT')
   raise RuntimeError('spark menu cursor')
  def wild_ack():
   if val('v11_wild')==3:tap('A')
  def flower():
   nav.walk_to(8*8+4,58*8+4,tolerance=2);tap('A');wait(lambda:val('v11_wild')!=0,'flower spark')
  def opening():
   S=report['story']
   assert flags()&1 and val('v11_act')>=1 and note().startswith('ACT I'),('Act I intro',flags(),note())
   S['intro']=note();mark('a1_01_intro_journal')
   nav.interact(120,at=(8,46));wait(lambda:val('v11_lore')==1,'listener');mark('a1_02_listener')
   tap('A');tap('A');assert not val('v11_lore');S['listener']=True
   flower();assert not val('v11_wild_rival');mark('a1_03_spark_rises');wild_ack();assert val('v11_wild')==1;mark('a1_04_spark_menu')
   wsel(3);tap('A');assert val('v11_wild')==0 and 'STEPPED OUT' in note(),note();S['run']=note()
   flower();wild_ack();wsel(1);tap('A');assert 'NOT YET' in note(),note();S['befriend_gated']=note();wild_ack()
   for _ in range(12):
    assert val('v11_wild'),'spark fled before it was weak'
    if val('v11_wild_hp')*5<=val('v11_wild_max')*2:break
    wsel(0);tap('A');assert val('v11_wild')==2;mark('a1_05_spark_moves');hp=val('v11_wild_hp');tap('A')
    assert val('v11_wild_hp')<hp or not val('v11_wild'),'Fight did no damage';S['fight']=note();wild_ack()
   pots=val('v11_qty',width=1,offset=70);wsel(2);tap('A')
   assert val('v11_qty',width=1,offset=70)==pots-1 and 'POTION' in note(),note();S['potion']=note();wild_ack()
   wsel(1);tap('A');assert val('v11_wild')==0 and flags()&2,('befriend',note());S['befriend']=note();mark('a1_06_befriended')
   # Rest, then Lys: talk once, press A again on her mark, and win the rival spark battle.
   rest();tap('B')
   nav.interact(121,at=(8,28));wait(lambda:val('v11_lore')==2,'Lys');mark('a1_07_lys');tap('A');tap('A')
   assert val('v11_rival_phase')==1
   nav.interact(121,at=(8,28));wait(lambda:val('v11_wild')!=0 and val('v11_wild_rival'),'Lys battle');mark('a1_08_lys_battle');wild_ack()
   for _ in range(30):
    if not val('v11_wild'):break
    assert not val('v11_gameover'),'Lys won'
    if val('v11_hp')<12 and val('v11_qty',width=1,offset=70):wsel(2);tap('A');wild_ack();continue
    wsel(0);tap('A');wsel(2);tap('A');wild_ack()
   assert flags()&4 and val('v11_rival_phase')==2,('rival',note());S['rival']=note();mark('a1_09_lys_lowers')
  def ending():
   S=report['story']
   assert flags()&16,'The Quiet did not set the story flag';S['quiet']=True
   nav.interact(120,at=(8,46));wait(lambda:val('v11_lore')==1,'crown listener');mark('a1_10_crown_listener')
   assert flags()&32 and val('v11_act')==5,('ending',flags(),val('v11_act'));tap('A');mark('a1_11_act_rests');tap('A');S['ending']=True
  try:
   e.step((),180);tap('A');wait(lambda:val('v10_opening')==1,'opening');tap('START');wait(lambda:any(n.id==14 for n in nav.npcs()) and not val('v10_opening'),'Brindlemark');e.step((),32)
   nav.interact(110,at=(34,44));wait(lambda:val('current_room')==70 and val('v11_npc_count')>0,'new Prime road');e.step((),180);mark('01_prime_field')
   if record:e.start_recording(record)
   opening()
   if record:report['recording']=e.stop_recording()
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
   rest();assign()
   if record:e.start_recording(record.with_name(record.stem+'_quiet'+record.suffix))
   ids=list(e.read_range(e.symbols['v11_enemy_id'].address,10));battle(ids.index(99));assert val('v11_boss_done')==1023;mark('20_true_quiet_defeated')
   ending()
   if record:report['recording_quiet']=e.stop_recording()
   # Music follows the story: overworld, wild spark battle, Lys rival theme, and the calm Crown/Quiet theme.
   songs={st['name']:st.get('song') for st in report['stages']}
   if 'lc_song' in e.symbols:
    want={'01_prime_field':1,'a1_04_spark_menu':2,'a1_08_lys_battle':3,'a1_10_crown_listener':5}
    assert all(songs.get(k)==v for k,v in want.items()),('music context',{k:songs.get(k) for k in want})
    report['music']={k:songs.get(k) for k in want}
   e.export_save(save)
  except Exception as exc:
   report['failure']=repr(exc);report['traceback']=traceback.format_exc();e.screenshot(out/'FAILED.png');raise
  finally:(out/'act1_story_report.json').write_text(json.dumps(report,indent=2,default=str)+'\n')
 # Cold boot: CONTINUE restores the finished act from battery SRAM.
 with Mgba(rom,elf=elf,save_path=save) as e:
  e.step((),180);e.tap('DOWN',hold=12,release=12);e.tap('A',hold=12,release=12);e.step((),300)
  assert e.read_symbol('game_mode')==0 and e.read_symbol('v11_story_flags')&63==63 and e.read_symbol('v11_act')==5
  e.screenshot(out/'a1_12_continue.png')
 report['continue_passed']=True;report['passed']=True;(out/'act1_story_report.json').write_text(json.dumps(report,indent=2,default=str)+'\n')
 print('PASS: Act I listener, flower spark (Fight, Befriend, Potion, Run), Lys, eight signals, the Quiet, crown listener, CONTINUE')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--out',type=Path,default=R/'artifacts/act1_story');a.add_argument('--rom',type=Path,default=R/'LOST_COSMOS_V10_SOURCE/LOST_COSMOS_V10_OPENING_QA.gba');a.add_argument('--elf',type=Path,default=R/'LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.elf');a.add_argument('--record',type=Path);o=a.parse_args();run(o.rom,o.elf,o.out,o.record)
