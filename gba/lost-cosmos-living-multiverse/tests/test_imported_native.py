"""Native host-path acceptance for synthetic BCP1 build-time ROM profile.
The fixture is synthetic: this test is NOT evidence an actual user's BCP1
pack has been imported or that GBA/Delta gameplay has been recorded.
"""
from pathlib import Path
import importlib.util, subprocess, sys, tempfile
BASE=Path(__file__).resolve().parents[1]
GAME=BASE/'LOST_COSMOS_V10_SOURCE'
sys.path.insert(0,str(BASE/'tests'))
from test_bridge import ImportTests,fnv
sys.path.insert(0,str(BASE/'tools'))
from import_beastbox import import_export
with tempfile.TemporaryDirectory() as d:
 root=Path(d); synthetic=root/'synthetic-bcp1.zip'
 ImportTests().setup_export(synthetic)
 receipt=import_export(synthetic,root)
 assert receipt['generator_version']==1
 assert receipt['BCP1_game_profile']['public_identity']==f"{fnv('identity|1|nebula-test'):08x}"
 header=(root/'imported_companion.h').read_text()
 assert 'lc_imported_companion_tiles[8192]' in header
 assert 'lc_imported_companion_field_tiles[2048]' in header
 assert receipt['field_art'].startswith('four native 32x32')
 assert len(bytes.fromhex(receipt['field_tiles_32_sha256']))==32
 source=(GAME/'host_qa_v5.c').read_text().split('\n#ifdef HOST_QA\nint main(',1)[0]
 source+='''
#include <assert.h>
#include <stdio.h>
int main(void){
 init_new_game();init_graphics();intro=0;
 assert(lc_party.count==1&&lc_party.active==0);
 assert(lc_party.slots[0].species==130); /* original seven-family VOID */
 assert(lc_party.slots[0].seed==LC_IMPORT_SEED_HASH);
 assert(lc_party.slots[0].identity==0x%08xu);
 assert(lc_party.slots[0].bond==10); /* no unearned trust */
 save_game();init_new_game();load_game();
 assert(lc_party.count==1&&lc_party.slots[0].identity==0x%08xu);
 puts("PASS synthetic BCP1 -> native original V10 game initialization, seed+identity+family+stats, SRAM save/restore");
 return 0;
}
'''%(fnv('identity|1|nebula-test'),fnv('identity|1|nebula-test'))
 f=root/'host_synthetic_bcp1.c';f.write_text(source)
 subprocess.run(['clang','-DHOST_QA','-DLC_IMPORTED_COMPANION','-O2','-Wno-unused-function','-I',str(root),'-I',str(GAME),str(f),'-o',str(root/'host_synthetic')],cwd=GAME,check=True)
 subprocess.run([str(root/'host_synthetic')],cwd=GAME,check=True,timeout=20)
