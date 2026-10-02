"""Exercise REAL V10 authored guardian action flows and assert new roster enrollment.
Uses original author V10 host GBA-MMIO harness; not mGBA controller capture.
"""
from pathlib import Path
import subprocess,tempfile,re
root=Path(__file__).resolve().parents[1];g=root/'LOST_COSMOS_V10_SOURCE'
original=(g/'v10_novel_realms_tests.py').read_text()
payload=re.search(r"s\s*\+=\s*r'''(.*?)'''",original,re.S).group(1)
changes=[
 ('battle_cursor=3;battle_act();assert(!enemies[8].active&&(v10_relic&RF_WOLF));',
  'battle_cursor=3;battle_act();assert(!enemies[8].active&&(v10_relic&RF_WOLF));\n assert(lc_party.count==1&&lc_party.slots[0].bond==80&&lc_party.slots[0].stage==0);'),
 ('battle_cursor=3;inv[ITEM_ETHER]=1;battle_act();assert(v10_relic&RF_GROVE_WRAITH);',
  'battle_cursor=3;inv[ITEM_ETHER]=1;battle_act();assert(v10_relic&RF_GROVE_WRAITH);\n assert(lc_party.count==2&&lc_party.slots[1].bond==80&&lc_party.slots[1].flags&4);'),
 ('assert(v10_relic&(RF_FESTIVAL|RF_EARTH));',
  'assert(v10_relic&(RF_FESTIVAL|RF_EARTH));\n assert(lc_party.count==2&&lc_party.slots[1].flags&4);')
]
for a,b in changes:
 assert payload.count(a)==1,(a,payload.count(a))
 payload=payload.replace(a,b)
payload=payload.replace('puts("PASS V10:','puts("PASS V10.1: authored peaceful guardians genuinely enroll and persist separately; ')
src=(g/'host_qa_v5.c').read_text().split('\n#ifdef HOST_QA\nint main(',1)[0]+payload
with tempfile.TemporaryDirectory() as d:
 c=Path(d)/'mercy_roster_host.c';c.write_text(src)
 subprocess.run(['clang','-DQA_AUTORUN','-DHOST_QA','-O2','-Wno-unused-function','-I',str(g),str(c),'-o',str(Path(d)/'mercy_roster_host')],cwd=g,check=True)
 subprocess.run([str(Path(d)/'mercy_roster_host')],cwd=g,check=True,timeout=20)
