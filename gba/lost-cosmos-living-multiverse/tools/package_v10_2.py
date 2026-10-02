#!/usr/bin/env python3
"""Deterministic source ZIP (no private author manuscripts or temporary host binaries)."""
from pathlib import Path
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED
import hashlib
r=Path(__file__).resolve().parents[1]
o=r.parent/'LOST_COSMOS_V10_2_LIVING_MULTIVERSE_EDITABLE_SOURCE.zip'
exclude={'host_qa_v5.c','host_qa_v5','hostqa_v5.sav','lost_cosmos_v5.elf',
 'game_v5.o','start_v5.o','payload_v5.bin','atlas_full_native_qa.c','atlas_full_native_qa',
 'LOST_COSMOS_V10_OPENING_QA.gba','cinema_qa.c','cinema_qa',
 'lm_roster_host_qa.c','lm_roster_host_qa','v10_finale_audio_qa.c',
 'v10_finale_audio_qa','v10_heartwood_qa.c','v10_heartwood_qa',
 'v10_novel_realms_qa.c','v10_novel_realms_qa'}
paths=[p for p in r.rglob('*') if p.is_file() and not (
 any(x in p.parts for x in ('__pycache__','.pytest_cache','.git')) or
 p.name in exclude or p.suffix in ('.o','.elf','.pyc','.sav','.bin') or
 (p.name.endswith('_qa.c') and p.name!='lost_cosmos_v5.c') or
 (p.parent==r/'LOST_COSMOS_V10_SOURCE' and p.name.endswith('_qa')))]
paths.sort(key=lambda p:p.relative_to(r).as_posix())
with ZipFile(o,'w',compression=ZIP_DEFLATED,compresslevel=9) as z:
 for p in paths:
  rel=f'{r.name}/{p.relative_to(r).as_posix()}'
  info=ZipInfo(rel,date_time=(2026,10,2,0,0,0))
  info.compress_type=ZIP_DEFLATED
  info.external_attr=0o644<<16
  z.writestr(info,p.read_bytes(),compress_type=ZIP_DEFLATED,compresslevel=9)
print('ZIP',o,'files',len(paths),'bytes',o.stat().st_size,'sha256',hashlib.sha256(o.read_bytes()).hexdigest())
