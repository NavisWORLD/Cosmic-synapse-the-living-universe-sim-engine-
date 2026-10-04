"""21 genuine source/native build and MMIO host suites across prior 20 and V10.5.
Run early, late, extended separately to respect individual runtime limits; no
emulator/controller claims. Every result contains executed output and return code.
"""
from pathlib import Path
import subprocess,json,datetime,time,sys,argparse
P=argparse.ArgumentParser();P.add_argument('phase',choices=('early','late','extended','all'));args=P.parse_args()
r=Path(__file__).resolve().parents[1];g=r/'LOST_COSMOS_V10_SOURCE'
early=[('native_arm7_rom',['bash','build_v5.sh'],g),('native_creature_c99',['bash','tests/run_host_tests.sh'],r),
 ('legacy_routes',['python3','verify_routes.py'],g),('legacy_two_process_sram',['python3','host_qa_v5.py'],g),
 ('v6_combat',['python3','v6_slice_tests.py'],g),('v7_worlds',['python3','v7_campaign_tests.py'],g),
 ('original_cinema_audio',['python3','cinema_tests_v51.py'],g),('v8_story',['python3','v8_view_story_tests.py'],g),
 ('v9_riftfall',['python3','v9_riftfall_tests.py'],g)]
late=[('v10_opening',['python3','v10_presentation_tests.py'],g),('v10_heartwood',['python3','v10_heartwood_tests.py'],g),
 ('v10_realms',['python3','v10_novel_realms_tests.py'],g),('v10_finale_audio',['python3','v10_finale_audio_tests.py'],g),
 ('v10_1_roster',['python3','tests/lm_roster_integration_tests.py'],r),
 ('v10_1_synthetic_bcp1',['python3','tests/test_imported_native.py'],r),
 ('v10_1_guardian_mercy',['python3','tests/test_mercy_collection.py'],r)]
extended=[('v10_2_atlas',['python3','tests/test_atlas_native.py'],r),
 ('v10_3_ecology',['python3','tests/test_ecology_native.py'],r),
 ('v10_5_history_5_exact_checkpoints',['python3','tests/test_patch_reconstruction.py'],r),
 ('v10_4_tactical_crafting',['python3','tests/test_progression_native.py'],r),
 ('v10_5_seventeen_guardians_and_act1',['python3','tests/test_guardian_v10_5.py'],r)]
labels={'early':early,'late':late,'extended':extended,'all':early+late+extended}
rows=[];folder=r/'docs';folder.mkdir(exist_ok=True)
for name,cmd,cwd in labels[args.phase]:
 start=time.monotonic()
 try:
  run=subprocess.run(cmd,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=110)
  exitcode=run.returncode;output=run.stdout
 except subprocess.TimeoutExpired as exc:
  exitcode=124;output=str(exc.stdout)+'\nTIMEOUT'
 rows.append({'name':name,'exit_code':exitcode,'seconds':round(time.monotonic()-start,2),'output':output[-5000:]})
 print(('PASS' if not exitcode else 'FAIL'),name,'%.2fs'%rows[-1]['seconds'],flush=True)
 if exitcode:print(output[-1800:],flush=True)
folder.joinpath(f'V10_5_{args.phase.upper()}_TEST_OUTPUT.json').write_text(json.dumps({
 'test_kind':'genuine freestanding ARM7 native compilation and source-executing native C simulated MMIO; NOT new mGBA/Delta manual video',
 'phase':args.phase,'passed':sum(v['exit_code']==0 for v in rows),'total':len(rows),'rows':rows},indent=2)+'\n')
print('PHASE',args.phase.upper(),'PASSED',sum(v['exit_code']==0 for v in rows),'/',len(rows),flush=True)
if any(x['exit_code'] for x in rows):sys.exit(1)
