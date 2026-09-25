#!/usr/bin/env python3
"""Recover exact V4 editable source from frozen verified V3 and compact source delta."""
import argparse
import base64
import hashlib
import json
import lzma
import re
import shutil
import zlib
from pathlib import Path

BASE_SHA='3d9b4caf42dded4bf2345a9ced987604cb702e325239dfe79999df16ad31e1cd'
V4_SHA='83bdde8e628ada112f172443336628d988ec977b464d0aadb5249d1e0b6805ca'

def sha(b): return hashlib.sha256(b).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--v3',type=Path,required=True)
    ap.add_argument('--bootstrap',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    v3=a.v3; boot=a.bootstrap; out=a.out
    if out.resolve()==v3.resolve(): raise SystemExit('refuse in-place source overwrite')
    orig=(v3/'lost_cosmos_v3.c').read_bytes()
    assert sha(orig)==BASE_SHA, ('wrong V3 baseline',sha(orig))
    parts=sorted(boot.glob('patch.*.b64'))
    assert [p.name for p in parts]==[f'patch.{i:02d}.b64' for i in range(3)], [p.name for p in parts]
    b64=''.join(p.read_text().strip() for p in parts)
    ops=json.loads(lzma.decompress(base64.b64decode(b64,validate=True)))
    src=orig.decode('utf-8'); pos=0; chunks=[]
    for start,end,replacement in ops:
        if not (pos<=start<=end<=len(src)): raise ValueError('bad or overlapping source delta')
        chunks.extend((src[pos:start],replacement)); pos=end
    chunks.append(src[pos:]); v4=''.join(chunks)
    assert sha(v4.encode('utf-8'))==V4_SHA, ('patch mismatch',sha(v4.encode()))
    out.mkdir(parents=True,exist_ok=True)
    (out/'lost_cosmos_v4.c').write_text(v4)
    for file in ['qseed.h','verify_routes.py']:
        shutil.copy2(v3/file,out/file)
    shutil.copy2(v3/'start_v3.S',out/'start_v4.S')
    shutil.copy2(v3/'linker_v3.ld',out/'linker_v4.ld')
    for file in ['build_v3.sh','build_rom_v3.py','verify_v3.py','host_qa_v3.py']:
        s=(v3/file).read_text().replace('v3','v4').replace('V3','V4')
        if file in ('build_rom_v3.py','verify_v3.py'):
            s=s.replace('header[0xBC]=3','header[0xBC]=4').replace('data[0xBC] != 3','data[0xBC] != 4')
        if file=='verify_v3.py':
            s=s.replace('V4 RPG engine surfaces verified','V4 NPC RPG engine surfaces verified')
            s=s.replace("'save_valid_v2']", "'save_valid_v2','NPC_DEF_COUNT','npc_speak','npc_advance','quest_completed']")
        if file=='host_qa_v3.py':
            s=s.replace('V4 RPG gameplay QA completed','V4 NPC RPG gameplay QA completed')
        (out/file.replace('v3','v4')).write_text(s)
    shutil.copy2(boot/'feature_tests_v4.py',out/'feature_tests_v4.py')
    fixtures=json.loads((boot/'qa_fixtures.json').read_text())
    (out/'qa_fixtures').mkdir(exist_ok=True)
    for name,info in fixtures.items():
        if name not in {'v2_mgba_boot1.sav','v3_mgba_boot1.sav'}: raise ValueError('unexpected fixture')
        payload=zlib.decompress(base64.b64decode(info['zlib_base64'],validate=True))
        assert len(payload)==32768 and sha(payload)==info['sha256'], ('bad fixture',name)
        (out/'qa_fixtures'/name).write_bytes(payload)
    if (boot/'README_V4.md').exists(): shutil.copy2(boot/'README_V4.md',out/'README_V4.md')
    print('PASS exact frozen V3 source:',BASE_SHA)
    print('PASS exact patched V4 source:',V4_SHA)
    print('PASS V2/V3 real-emulator save fixtures recovered and verified')
    print('Generated',out)

if __name__=='__main__': main()