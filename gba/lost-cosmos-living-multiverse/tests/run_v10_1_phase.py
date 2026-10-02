"""Run complete latest-source QA in two bounded, reproducible phases.
python3 tests/run_v10_1_phase.py early
python3 tests/run_v10_1_phase.py late
"""
import argparse,hashlib,json,subprocess,sys,time,datetime
from pathlib import Path
P=argparse.ArgumentParser();P.add_argument('phase',choices=['early','late']);phase=P.parse_args().phase
root=Path(__file__).resolve().parents[1];g=root/'LOST_COSMOS_V10_SOURCE'
early=[('Native ARM7 build and header/QSEED',['bash','build_v5.sh'],g),('C99 engine and five strict ZIP tests',['bash','tests/run_host_tests.sh'],root),('Actual V10 route registry',['python3','-u','verify_routes.py'],g),('Two-process legacy host SRAM',['python3','-u','host_qa_v5.py'],g),('V6 sprites, combat and story',['python3','-u','v6_slice_tests.py'],g),('V7 8-world/story progression',['python3','-u','v7_campaign_tests.py'],g),('Original 23 GBA cinema/audio',['python3','-u','cinema_tests_v51.py'],g),('V8 story/perks and legibility',['python3','-u','v8_view_story_tests.py'],g),('V9 Riftfall and bonded animal',['python3','-u','v9_riftfall_tests.py'],g)]
late=[('V10 dialogue, title and prologue',['python3','-u','v10_presentation_tests.py'],g),('V10 Heartwood guardian/bridge',['python3','-u','v10_heartwood_tests.py'],g),('V10 original novel regions/fight and mercy',['python3','-u','v10_novel_realms_tests.py'],g),('V10 original three unique endings and five tunes',['python3','-u','v10_finale_audio_tests.py'],g),('V10.1 12-slot capture, XP, stage2 evolution, SRAM',['python3','-u','tests/lm_roster_integration_tests.py'],root),('V10.1 synthetic BCP1 game import/identity/save',['python3','-u','tests/test_imported_native.py'],root),('V10.1 actual authored guardian mercy collection/save',['python3','-u','tests/test_mercy_collection.py'],root)]
path=root/'docs'/f'V10_1_{phase.upper()}_RESULTS.json';results=[];outlog=root/'docs'/f'V10_1_{phase.upper()}_TEST_OUTPUT.log';outlog.write_text('')
for label,cmd,cwd in early if phase=='early' else late:
 t=time.monotonic()
 try:
  process=subprocess.run(cmd,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=50)
  status=process.returncode;output=process.stdout
 except subprocess.TimeoutExpired as e:status=124;output=str(e.stdout or '')+'\nTIMED OUT\n'
 with outlog.open('a') as f:f.write(f'## {label}: exit={status}\n{output}\n')
 result={'test':label,'exit_code':status,'seconds':round(time.monotonic()-t,2),'last_lines':output.splitlines()[-4:]};results.append(result)
 print(('PASS ' if status==0 else 'FAIL ')+label,flush=True)
 if status!=0:print(output[-900:],flush=True)
path.write_text(json.dumps({'phase':phase,'results':results},indent=2)+'\n')
print('PHASE',phase,'PASS',sum(x['exit_code']==0 for x in results),'/',len(results),flush=True)
if any(x['exit_code']!=0 for x in results):sys.exit(1)
