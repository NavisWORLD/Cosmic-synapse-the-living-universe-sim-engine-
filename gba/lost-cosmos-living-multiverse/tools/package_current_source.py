#!/usr/bin/env python3
"""Deterministic public-safe editable source from the exact native game checkout.
Private book, author matrix, user .sav, credentials and runtime videos excluded.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]
PREFIX='LOST_COSMOS_V11_1_SOURCE'
INCLUDE=('LOST_COSMOS_V10_SOURCE','baseline','lineage','docs','tests','tools','content')
SUFFIXES={'.c','.h','.s','.py','.sh','.ld','.md','.txt','.diff','.sha256','.json','.yml','.yaml','.webp','.png'}
BANNED=('private','manuscript','credential','secret','.env','.sav','token','personal')
TEMP={'host_qa_v5.c','living_book_v107_native_host_qa.c','guardian_v105_native_host_qa.c',
      'act_threads_v106_native_host_qa.c','test_end_credits_v108_host.c','content_v11_test_host.c'}
def sha(data:bytes)->str:
 return hashlib.sha256(data).hexdigest()
def sources():
 files={}
 for folder in INCLUDE:
  directory=ROOT/folder
  if not directory.is_dir():continue
  for p in sorted(directory.rglob('*')):
   if not p.is_file() or p.suffix.lower() not in SUFFIXES:continue
   relative=p.relative_to(ROOT).as_posix()
   if '__pycache__' in p.parts or p.name in TEMP or p.name.endswith(('_native_host.c','_native_host_qa.c','_host_qa.c')):continue
   if any(term in p.name.lower() for term in BANNED):
    raise ValueError('Refusing suspicious private file in public source: '+relative)
   if p.is_symlink():raise ValueError('Refusing unreviewed symlink: '+relative)
   files[relative]=p.read_bytes()
 must={'LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.c',
       'LOST_COSMOS_V10_SOURCE/qseed.h',
       'LOST_COSMOS_V10_SOURCE/build_v5.sh',
       'LOST_COSMOS_V10_SOURCE/start_v5.S',
       'LOST_COSMOS_V10_SOURCE/credits_v10_8.h',
       'LOST_COSMOS_V10_SOURCE/content_v11_state.h',
       'LOST_COSMOS_V10_SOURCE/content_v11_art.h',
       'LOST_COSMOS_V10_SOURCE/imported_companion.h',
       'content/v11_1_catalog.json'}
 if not must.issubset(files):raise AssertionError('Missing current native engine, QSEED or build components')
 if (ROOT/'README_V11_1.md').exists():files['README_V11_1.md']=(ROOT/'README_V11_1.md').read_bytes()
 workflow=ROOT.parents[1]/'.github/workflows/lost-cosmos-native.yml'
 if workflow.exists():files['ci/lost-cosmos-native.yml']=workflow.read_bytes()
 return files
def package(dest:Path,rom:Path):
 files=sources();native=rom.read_bytes()
 if len(native)<65536 or len(native)&(len(native)-1):raise AssertionError('Bad native ROM size')
 if native[0xAC:0xB0]!=b'ERL8':raise AssertionError('Wrong native ROM game code')
 try:commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
 except (FileNotFoundError,subprocess.CalledProcessError):commit='local-uncommitted-build'
 source=files['LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.c']
 qsource=files['LOST_COSMOS_V10_SOURCE/qseed.h'].decode()
 import re
 nums=[int(n) for n in re.findall(r'\b\d+\b',qsource.split('{',1)[1].rsplit('}',1)[0])]
 if len(nums)!=8192 or sha(bytes(nums))!='9bcecc3732fe48107554cc2041cff6088f418290fb850ec0c9b89cdc375f54c8':
  raise AssertionError('Original 8192-byte QSEED provenance changed')
 receipt={'project':'LOST COSMOS — The Living Multiverse',
  'original_author':'Cory Davis / NavisWORLD',
  'status':'Native V11.1 Content Bible upgrade; acceptance in matching controller evidence',
  'git_commit':commit,'rom_name':'LOST_COSMOS_V11_1_CONTENT.gba',
  'rom_sha256':sha(native),'rom_bytes':len(native),
  'native_engine_sha256':sha(source),'qseed_sha256':sha(bytes(nums)),
  'owner_private_manuscript_included':False,
  'real_mgba_acceptance':'see separate genuine controller CI report',
  'physical_iphone_delta':'not tested',
  'full_original_five_act_acceptance':'not claimed'}
 files['BUILD_RECEIPT.json']=(json.dumps(receipt,sort_keys=True,indent=2)+'\n').encode()
 files['README_SOURCE_PACKAGE.txt']=('Lost COSMOS V11.1 editable native GBA sources\n'
  'Owned by Cory Davis / NavisWORLD. Read README_V11_1.md for play controls and scope.\n'
  'Install clang/lld/llvm and Python 3. To build: cd LOST_COSMOS_V10_SOURCE && IMPORTED_BEAST=1 bash build_v5.sh\n'
  'Check the rebuilt GBA SHA-256 against BUILD_RECEIPT.json.\n'
  'Original private manuscript, owner profiles, and real .sav are NOT included.\n'
  'Prior full ROM revisions remain recoverable in the earlier owner archive.\n'
  'Cartridge code ERL8 and historical SRAM fields remain compatible; attach your backed-up battery save explicitly in an emulator.\n'
  'Host C checks are not recorded human-led gameplay or Delta device acceptance.\n').encode()
 manifest=''.join(f'{sha(data)}  {name}\n' for name,data in sorted(files.items())).encode()
 files['MANIFEST.SHA256.txt']=manifest
 dest.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
  for name,data in sorted(files.items()):
   i=zipfile.ZipInfo(PREFIX+'/'+name,date_time=(2026,10,2,12,0,0))
   i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16
   z.writestr(i,data)
 with zipfile.ZipFile(dest) as z:
  for line in manifest.decode().splitlines():
   digest,name=line.split('  ',1)
   if sha(z.read(PREFIX+'/'+name))!=digest:raise AssertionError('Source manifest failed: '+name)
 print(json.dumps({'package_sha256':sha(dest.read_bytes()),
                   'source_files':len(files)-1,'archive_entries':len(files),
                   'native_rom_sha256':receipt['rom_sha256'],'git_commit':commit},indent=2))
def main():
 a=argparse.ArgumentParser();a.add_argument('--out',type=Path,required=True)
 a.add_argument('--rom',type=Path,default=ROOT/'LOST_COSMOS_V10_SOURCE'/'LOST_COSMOS_V10_OPENING_QA.gba')
 o=a.parse_args();dest=o.out if o.out.is_absolute() else ROOT/o.out
 package(dest,o.rom)
if __name__=='__main__':main()
