"""Verifies every immutable V10 -> V10.1 -> V10.2 -> V10.3 -> V10.6 source checkpoints with actual pinned reconstruction. No overwrites."""
from pathlib import Path
import tempfile,shutil,subprocess,hashlib
r=Path(__file__).resolve().parents[1]
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
v10=r/'lineage/original_v10_lost_cosmos_v5.c'
v101=r/'baseline/v10_1_lost_cosmos_v5.c'
v102=r/'baseline/v10_2_lost_cosmos_v5.c'
v103=r/'baseline/v10_3_lost_cosmos_v5.c'
v104=r/'baseline/v10_4_lost_cosmos_v5.c'
v105=r/'baseline/v10_5_lost_cosmos_v5.c'
v106=r/'baseline/v10_6_lost_cosmos_v5.c'
v107=r/'LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.c'
assert h(v10)=='65880121335c2a32b1e647fed38a745d0b64e3fa001b3744228063ef33d59b4d'
assert h(v101)=='d57e7f84a29a3207790b1974f416de963ffc994b67cb467c97bd461a643462e6'
assert h(v102)=='de5912103418260bbe74c062762571ed88846ce4aa709cc7d959f6db6bac52e1'
assert h(v103)==(r/'tools/engine_v10_3_source.sha256').read_text().strip()
assert h(v104)==(r/'tools/engine_v10_4_source.sha256').read_text().strip()
assert h(v105)==(r/'tools/engine_v10_5_source.sha256').read_text().strip()
assert h(v106)==(r/'tools/engine_v10_6_source.sha256').read_text().split()[0]
assert h(v107)==(r/'tools/engine_v10_7_source.sha256').read_text().split()[0]
with tempfile.TemporaryDirectory(prefix='lc_native_reconstruct_') as td:
 d=Path(td);(d/'tools').mkdir();(d/'baseline').mkdir();g=d/'LOST_COSMOS_V10_SOURCE';g.mkdir()
 shutil.copy2(v101,d/'baseline/v10_1_lost_cosmos_v5.c')
 shutil.copy2(r/'tools/integrate_living_multiverse.py',d/'tools/integrate_living_multiverse.py')
 c=g/'lost_cosmos_v5.c';shutil.copy2(v10,c)
 subprocess.run(['python3',str(d/'tools/integrate_living_multiverse.py')],check=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 assert c.read_bytes()==v101.read_bytes(),'V10 -> V10.1 mismatched historical reproducible engine'
 print('PASS exact V10 -> V10.1 script, SHA',h(c),flush=True)
 for x in ['extend_v10_2.py','patch_v10_2_to_v10_3.py','engine_v10_2_to_v10_3.diff','engine_v10_3_source.sha256']:
  shutil.copy2(r/'tools'/x,d/'tools'/x)
 # Previous version 10.2 is regenerated with the historical exact pinned script, no destructive update to real source.
 shutil.copy2(v101,c)
 p=subprocess.run(['python3',str(d/'tools/extend_v10_2.py')],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 assert p.returncode==0,('historical patch failed',p.stdout[-1800:])
 assert c.read_bytes()==v102.read_bytes(),'V10.1 -> V10.2 source does not match pinned historical engine'
 print('PASS exact V10.1 -> V10.2 script, SHA',h(c),flush=True)
 subprocess.run(['python3',str(d/'tools/patch_v10_2_to_v10_3.py')],check=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 assert c.read_bytes()==v103.read_bytes(),'V10.2 -> V10.3 source patch does not match shipped new engine'
 print('PASS exact V10.2 -> V10.3 diff, SHA',h(c),flush=True)

 # V10.4 is an additional development stage and may never rewrite the V10.3 archive.
 for x in ['patch_v10_3_to_v10_4.py','engine_v10_3_to_v10_4.diff','engine_v10_4_source.sha256']:
  shutil.copy2(r/'tools'/x,d/'tools'/x)
 subprocess.run(['python3',str(d/'tools/patch_v10_3_to_v10_4.py')],check=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 assert c.read_bytes()==v104.read_bytes(),'V10.3 -> V10.4 source patch mismatch'
 print('PASS exact V10.3 -> V10.4 diff, SHA',h(c),flush=True)

 # V10.5 is an additive C patch. Header/map/persistence additions are tracked
 # as separately manifest-checked new files in the reproducible source ZIP.
 for x in ['patch_v10_4_to_v10_5.py','engine_v10_4_to_v10_5.diff','engine_v10_5_source.sha256','engine_v10_4_source.sha256']:
  shutil.copy2(r/'tools'/x,d/'tools'/x)
 subprocess.run(['python3',str(d/'tools/patch_v10_4_to_v10_5.py')],check=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 assert c.read_bytes()==v105.read_bytes(),'V10.4 -> V10.5 native C patch mismatch'
 print('PASS exact V10.4 -> V10.5 preserved historical C',flush=True)
 for x in ['patch_v10_5_to_v10_6.py','engine_v10_5_to_v10_6.diff','engine_v10_6_source.sha256']:
  shutil.copy2(r/'tools'/x,d/'tools'/x)
 subprocess.run(['python3',str(d/'tools/patch_v10_5_to_v10_6.py')],check=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 assert c.read_bytes()==v106.read_bytes(),'V10.5 -> V10.6 actual C patch mismatch'
 print('PASS exact V10.5 -> V10.6 source pinned SHA',h(c),flush=True)
 print('PASS final exact V10.6 source checkpoint after all six stage recoveries, SHA',h(c),flush=True)

 # Exact source diff-only optional upgrade verifies the CURRENT source code,
 # without ever overwriting the frozen prior six historical source snapshots.
 for x in ['patch_v10_6_to_v10_7.py','engine_v10_6_to_v10_7.diff','engine_v10_7_source.sha256']:
  shutil.copy2(r/'tools'/x,d/'tools'/x)
 subprocess.run(['python3',str(d/'tools/patch_v10_6_to_v10_7.py')],check=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 assert c.read_bytes()==v107.read_bytes(),'V10.6 -> V10.7 pinned native source mismatch'
 print('PASS current EXACT V10.7 novel-native source checkpoint SHA',h(c),flush=True)
