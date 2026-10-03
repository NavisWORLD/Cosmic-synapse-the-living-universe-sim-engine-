#!/usr/bin/env python3
"""Build the definitive Lost COSMOS V11 cartridge with one portable Quantum Beast.

Accept either a provider-neutral .qbeast snapshot (using the installed
`quantum-beast` CLI only to verify/export public GBA data) or an already
exported Beast GBA ZIP. The GBA ROM never receives private memory, model
weights, credentials, or model authority.
"""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
GAME=BASE/'LOST_COSMOS_V10_SOURCE'
sys.path.insert(0,str(BASE/'tools'))
from import_beastbox import import_export, InvalidExport


def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def run_json(argv:list[str],cwd:Path|None=None)->dict:
    p=subprocess.run(argv,cwd=cwd,text=True,capture_output=True)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout or 'command failed').strip())
    try:return json.loads(p.stdout)
    except json.JSONDecodeError as exc:raise RuntimeError('Expected JSON from '+argv[0]) from exc


def main()->int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('beast',type=Path,help='.qbeast snapshot or Beast GBA export ZIP')
    ap.add_argument('--out',type=Path,default=BASE/'artifacts/v11-quantum-beast')
    ap.add_argument('--bridge-cli',default='quantum-beast',help='Quantum Beast Bridge CLI for .qbeast inputs')
    ap.add_argument('--trust-key',help='Optional trusted Ed25519 public key for signed .qbeast verification')
    a=ap.parse_args(); beast=a.beast.resolve(); out=a.out.resolve(); out.mkdir(parents=True,exist_ok=True)
    if not beast.is_file():raise SystemExit('Missing Beast input: '+str(beast))
    source_sha=sha256(beast); bridge_receipt=None
    with tempfile.TemporaryDirectory(prefix='lost-cosmos-v11-qbeast-') as td:
        temp=Path(td)
        if beast.suffix.lower()=='.qbeast':
            store=temp/'beast.qbeast'; export=temp/'beast-gba.zip'
            install=[a.bridge_cli,'install',str(beast),'--store',str(store)]
            if a.trust_key:install += ['--trust-key',a.trust_key]
            bridge_receipt=run_json(install)
            cmd=[a.bridge_cli,'export-gba','--output',str(export),'--store',str(store)]
            if a.trust_key:cmd += ['--trust-key',a.trust_key]
            export_receipt=run_json(cmd); bridge_receipt['gba_export']=export_receipt
            source=export
        else:
            source=beast
        try:import_receipt=import_export(source,GAME)
        except (InvalidExport,OSError,ValueError) as exc:
            raise SystemExit('Quantum Beast GBA import rejected: '+str(exc)) from exc
        env=dict(os.environ);env['IMPORTED_BEAST']='1'
        subprocess.run(['bash','build_v5.sh'],cwd=GAME,env=env,check=True)
        rom=GAME/'LOST_COSMOS_V10_OPENING_QA.gba';elf=GAME/'lost_cosmos_v5.elf'
        target=out/'LOST_COSMOS_V11_QUANTUM_BEAST.gba';shutil.copy2(rom,target)
        shutil.copy2(elf,out/'lost_cosmos_v11_quantum_beast.elf')
        shutil.copy2(GAME/'imported_companion.h',out/'imported_companion.h')
        shutil.copy2(GAME/'import_receipt.json',out/'import_receipt.json')
        receipt={
          'schema':'lost-cosmos-v11-quantum-beast-build-v1',
          'input_file':beast.name,'input_sha256':source_sha,
          'bridge':bridge_receipt,
          'public_game_import':import_receipt,
          'rom':target.name,'rom_sha256':sha256(target),'rom_bytes':target.stat().st_size,
          'elf_sha256':sha256(out/'lost_cosmos_v11_quantum_beast.elf'),
          'qseed_sha256':'9bcecc3732fe48107554cc2041cff6088f418290fb850ec0c9b89cdc375f54c8',
          'engine':'Astra V10.8 visual engine carrying SOL V3 RPG systems',
          'imported_field_art':'32x32 native OBJ frames derived from verified 64x64 Beast export',
          'authority_boundary':'model and private Beast memory are not embedded in the ROM',
        }
        (out/'V11_QUANTUM_BEAST_BUILD_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
        print(json.dumps(receipt,indent=2,sort_keys=True))
    return 0

if __name__=='__main__':raise SystemExit(main())
