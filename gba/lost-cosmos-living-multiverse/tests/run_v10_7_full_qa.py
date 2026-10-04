#!/usr/bin/env python3
"""V10.7 honest QA: freestanding real ARM7 compilation and actual native C host.
Host C simulates memory-mapped I/O; NEVER claim it as true mGBA or Delta input.
Use `phase` separately in constrained runners; stop + record any real failure.
"""
from pathlib import Path
import subprocess,json,time,sys,argparse,hashlib,signal,os
p=argparse.ArgumentParser();p.add_argument('phase',choices=('early_a','early_b','late_a','late_b','extended_a','extended_b','latest','early','late','extended'));args=p.parse_args()
r=Path(__file__).resolve().parents[1];g=r/'LOST_COSMOS_V10_SOURCE'
suites={
 'early':[
 ('native_arm7_rom',['bash','build_v5.sh'],g),('native_creature_c99',['bash','tests/run_host_tests.sh'],r),
 ('legacy_routes',['python3','verify_routes.py'],g),('legacy_two_process_sram',['python3','host_qa_v5.py'],g),
 ('v6_combat',['python3','v6_slice_tests.py'],g),('v7_worlds',['python3','v7_campaign_tests.py'],g),
 ('v9_riftfall',['python3','v9_riftfall_tests.py'],g),
 ('original_cinema_audio',['python3','cinema_tests_v51.py'],g),('v8_story',['python3','v8_view_story_tests.py'],g)],
 'late':[
 ('v10_opening',['python3','v10_presentation_tests.py'],g),
 ('v10_heartwood',['python3','v10_heartwood_tests.py'],g),
 ('v10_realms',['python3','v10_novel_realms_tests.py'],g),
 ('v10_finale_audio',['python3','v10_finale_audio_tests.py'],g),
 ('v10_1_roster',['python3','tests/lm_roster_integration_tests.py'],r),
 ('v10_1_synthetic_bcp1',['python3','tests/test_imported_native.py'],r),
 ('v10_1_guardian_mercy',['python3','tests/test_mercy_collection.py'],r)],
 'extended':[
 ('v10_2_atlas',['python3','tests/test_atlas_native.py'],r),
 ('v10_3_ecology',['python3','tests/test_ecology_native.py'],r),
 ('v10_4_tactical_crafting',['python3','tests/test_progression_native.py'],r),
 ('v10_5_guardian_and_act1',['python3','tests/test_guardian_v10_5.py'],r)],
 'latest':[
 ('all_seven_source_checkpoints',['python3','tests/test_patch_reconstruction.py'],r),
 ('v10_6_four_act_threads',['python3','tests/test_act_threads_v10_6.py'],r),
 ('v10_7_living_book',['python3','tests/test_living_book_v10_7.py'],r)]}
suites['early_a']=suites['early'][:5]
suites['early_b']=suites['early'][5:]
suites['late_a']=suites['late'][:4]
suites['late_b']=suites['late'][4:]
suites['extended_a']=suites['extended'][:2]
suites['extended_b']=suites['extended'][2:]
rows=[]
for name,cmd,cwd in suites[args.phase]:
 t=time.monotonic()
 proc=subprocess.Popen(cmd,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,start_new_session=True)
 try:log,_=proc.communicate(timeout=23);code=proc.returncode
 except subprocess.TimeoutExpired:
  os.killpg(proc.pid,signal.SIGKILL);log,_=proc.communicate(timeout=3);code=124;log+='\nTIMEOUT after 23 seconds; entire child process group terminated'
 elapsed=round(time.monotonic()-t,2)
 rows.append({'name':name,'exit_code':code,'seconds':elapsed,'stdout_tail':log[-2200:]})
 print(('PASS' if code==0 else 'FAIL'),name,'%.2fs'%elapsed,flush=True)
 if code:print(log[-1600:],flush=True)
report={'type':'source-derived real native-C simulated-MMIO and ARM7 compile, NOT mGBA or Delta human playthrough',
        'phase':args.phase,'native_c_sha256':hashlib.sha256((g/'lost_cosmos_v5.c').read_bytes()).hexdigest(),
        'passed':sum(x['exit_code']==0 for x in rows),'total':len(rows),'rows':rows}
out=r/'docs'/f'V10_7_{args.phase.upper()}_QA.json';out.write_text(json.dumps(report,indent=2)+'\n')
print('PHASE',args.phase,'PASS',report['passed'],'/',len(rows),flush=True)
if report['passed']!=len(rows):sys.exit(1)
