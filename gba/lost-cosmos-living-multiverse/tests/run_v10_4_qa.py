"""Rerun all 20 actual native-build/source-host suites; 4 new/progression categories.
Host MMIO tests are NOT emulator/Delta proof. Local original V10 historical SRAM fixtures
are included solely to permit original older-snapshot fixture-based regression.
"""
from pathlib import Path
import subprocess,json,datetime,sys,time
root=Path(__file__).resolve().parents[1];g=root/'LOST_COSMOS_V10_SOURCE'
early=[('native_arm7_rom',['bash','build_v5.sh'],g),('native_creature_c99',['bash','tests/run_host_tests.sh'],root),
 ('legacy_routes',['python3','verify_routes.py'],g),('legacy_two_process_sram',['python3','host_qa_v5.py'],g),
 ('v6_combat',['python3','v6_slice_tests.py'],g),('v7_worlds',['python3','v7_campaign_tests.py'],g),
 ('original_cinema_audio',['python3','cinema_tests_v51.py'],g),('v8_story',['python3','v8_view_story_tests.py'],g),
 ('v9_riftfall',['python3','v9_riftfall_tests.py'],g)]
late=[('v10_opening',['python3','v10_presentation_tests.py'],g),('v10_heartwood',['python3','v10_heartwood_tests.py'],g),
 ('v10_realms',['python3','v10_novel_realms_tests.py'],g),('v10_finale_audio',['python3','v10_finale_audio_tests.py'],g),
 ('v10_1_roster',['python3','tests/lm_roster_integration_tests.py'],root),
 ('v10_1_synthetic_bcp1',['python3','tests/test_imported_native.py'],root),
 ('v10_1_guardian_mercy',['python3','tests/test_mercy_collection.py'],root)]
latest=[('v10_2_atlas',['python3','tests/test_atlas_native.py'],root),('v10_3_ecology',['python3','tests/test_ecology_native.py'],root),
 ('v10_4_history',['python3','tests/test_patch_reconstruction.py'],root),
 ('v10_4_tactical_crafting',['python3','tests/test_progression_native.py'],root)]
results=[]
for name,cmd,cwd in early+late+latest:
 t=time.monotonic()
 try:
  r=subprocess.run(cmd,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=75)
  rc=r.returncode;stdout=r.stdout
 except subprocess.TimeoutExpired as exc:rc=124;stdout=str(exc.stdout)+'\nTIMED OUT'
 row={'suite':name,'exit_code':rc,'seconds':round(time.monotonic()-t,3),'evidence':stdout}
 results.append(row)
 print(('PASS' if rc==0 else 'FAIL'),name,flush=True)
 if rc:print(stdout[-1000:],flush=True)
(root/'docs/V10_4_FULL_REPRODUCIBLE_QA_LAST_RUN.json').write_text(json.dumps({'testing_kind':'Native ARM7 build and actual source-derived host C; NOT new mGBA footage or iPhone Delta','suite_count':len(results),'passed':sum(x['exit_code']==0 for x in results),'results':results},indent=2)+'\n')
print('PASS',sum(x['exit_code']==0 for x in results),'/',len(results))
if any(x['exit_code'] for x in results):sys.exit(1)
