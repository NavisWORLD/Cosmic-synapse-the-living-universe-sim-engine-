#!/usr/bin/env python3
"""Regress LCX1 identity/art/export alongside V11.1 slots and compiled imports."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'LOST_COSMOS_V10_SOURCE'
sys.path.insert(0, str(ROOT / 'tools'))
from lc_mailbox import fixture_save

subprocess.run(['python3', 'host_qa_v5.py'], cwd=SRC, check=True, capture_output=True)
pre = (SRC / 'host_qa_v5.c').read_text().split('\n#ifdef HOST_QA\nint main(', 1)[0]
body = r'''
#include <assert.h>
int main(int argc,char **argv){
 assert(argc==2);FILE*f=fopen(argv[1],"rb");assert(f);
 assert(fread((void*)HOST_SRAM,1,sizeof HOST_SRAM,f)==sizeof HOST_SRAM);fclose(f);
 init_new_game();init_graphics();save_game();
 int count=lc_party.count,ix=lc_party.active,i;
#if defined(LC_IMPORT_HAS_BCP1)
 assert(count==2&&lc_party.slots[0].identity==0xf5a4cb6du);
 assert(!strcmp(v11_creature_name(0),"MIRABY"));
#else
 assert(count==1);
#endif
 LcCreature*c=&lc_party.slots[ix];assert(c->identity==0xb5422fb1u&&c->species==128&&c->bond==14);
 assert(!strcmp(v11_creature_name(ix),"EARTH"));
 v11_portrait(ix+1,168,48,0);assert((OAM16[42*4+1]>>14)==3);
 v11_draw_import_battle(3,91,24,c->identity);assert(OAM16[12]&0x100);
 /* Matrix 4 is 1:1 so the 64px battle canvas stays full size. */
 assert(((OAM16[13]>>9)&31)==4);assert(OAM16[4*16+3]==256);
#if defined(LC_IMPORT_HAS_BCP1)
 v11_portrait(1,168,48,0);
 assert(!memcmp((const void*)(HOST_VRAM+0x10000+LC_IMPORT_OBJ_TILE*32),lc_imported_companion_tiles,2048));
 lc_draw_import_field(42,10,10,0,0,lc_party.slots[0].identity);
 assert(!memcmp((const void*)(HOST_VRAM+0x10000+LC_IMPORT_FIELD_OBJ_TILE*32),lc_imported_companion_field_tiles+(cosmos.mood&3)*512,512));
#endif
 c->bond=60;assert(v11_prepare_export(ix+1));assert(v11_export_valid());
 u8 b[64];for(i=0;i<64;i++)b[i]=SRAM[6224+i];LcProfile p;
 assert(lc_parse_bcp1(b,64,&p)==LC_OK&&p.public_id==c->identity&&p.family==0);
 v11_credits=444;v11_slot_save(0);assert(v11_slot_valid(0));
 init_new_game();load_game();assert(lc_party.count==count);
 assert(lc_party.slots[ix].bond==60&&!strcmp(v11_creature_name(ix),"EARTH"));
 assert(v11_credits==444);assert(v11_import_snapshot());assert(lc_party.count==count);
 assert(lc_party.active==ix&&lc_party.slots[ix].bond==60);
 SRAM[24832+640]^=1;lc_mail_live=0;lc_mailbox_refresh(0);assert(!lc_mail_live);
 puts("PASS LCX1 and V11.1 coexist: identity, name, art, export, CRC slot, resume, no duplicates");
 return 0;
}
'''
with tempfile.TemporaryDirectory(prefix='lc-mailbox-', dir=SRC) as tmp:
    tmp = Path(tmp)
    sav, _ = fixture_save()
    (tmp / 'fixture.sav').write_bytes(sav)
    source = tmp / 'mailbox_host.c'
    source.write_text(pre + body)
    for imported in (False, True):
        exe = tmp / ('compiled' if imported else 'runtime')
        cmd = [os.environ.get('LC_HOST_CC', 'gcc'), '-DQA_AUTORUN', '-DHOST_QA', '-O2', '-I', str(SRC)]
        if imported:
            cmd.append('-DLC_IMPORTED_COMPANION')
        subprocess.run(cmd + [str(source), '-o', str(exe)], check=True)
        subprocess.run([str(exe), str(tmp / 'fixture.sav')], check=True)
