#!/usr/bin/env python3
"""Offline build-time import of a public Beast Box GBA creature ZIP.

BCG1 is NOT a game profile; BCP1 remains an independent optional file.
Only validated public data is emitted. Does not read private COSMOS memory.
"""
from __future__ import annotations
import argparse, hashlib, json, struct, sys, unicodedata, zipfile, zlib
from pathlib import Path

TILES = 'gba/companion_tiles.4bpp'
PALETTE = 'gba/companion_palette.bgr555'
BCG = 'gba/companion_state.bin'
BCP = 'gba/companion_profile.bin'
PROFILE = 'companion.profile.json'

class InvalidExport(ValueError):
    pass

def parse_bcp1(raw: bytes) -> dict:
    if len(raw) != 64 or raw[:4] != b'BCP1' or raw[4] != 1:
        raise InvalidExport('BCP1 format/version mismatch')
    if raw[5] > 6 or raw[6] > 2 or raw[7] or any(raw[28:60]):
        raise InvalidExport('BCP1 enum or reserved-byte mismatch')
    if zlib.crc32(raw[:60]) != struct.unpack_from('<I', raw, 60)[0]:
        raise InvalidExport('BCP1 CRC32 mismatch')
    stats = list(raw[8:18]); temper = list(raw[18:23])
    if sum(stats) != 500 or any(x < 20 or x > 80 for x in stats + temper):
        raise InvalidExport('BCP1 fictional stat budget/range mismatch')
    identity = struct.unpack_from('<I', raw, 24)[0]
    if identity == 0: raise InvalidExport('BCP1 public identity is zero')
    return dict(version=1, family=raw[5], look=raw[6], game_stats=stats,
                temperament=temper, hue=struct.unpack_from('<b', raw, 23)[0],
                public_identity=f'{identity:08x}')

def check_guest_bcg1(raw: bytes) -> None:
    if len(raw) != 60 or raw[:4] != b'BCG1' or raw[4] != 1 or raw[5] > 2 or raw[6:] != b'\0'*54:
        raise InvalidExport('Only non-measured, empty guest BCG1 snapshots allowed')

def checked_read(z: zipfile.ZipFile, name: str, limit: int) -> bytes:
    if name not in z.namelist(): raise InvalidExport('Missing '+name)
    info = z.getinfo(name)
    if info.file_size > limit: raise InvalidExport('Unexpected oversized '+name)
    data = z.read(name)
    if len(data) > limit: raise InvalidExport('Oversized '+name)
    return data

def as_c(name: str, raw: bytes) -> str:
    lines=[f'static const unsigned char {name}[{len(raw)}] = {{']
    for i in range(0,len(raw),16):
        lines.append('  '+', '.join(f'0x{x:02x}' for x in raw[i:i+16])+',')
    return '\n'.join(lines+['};'])

# Exact deterministic generator lineage, mirrored from Beast Box creature-profile.ts v1.
# Never substitute a plausible same-budget stat vector for the real seeded profile.
FAMILIES=('nebula','aurora','void','plasma','memory','signal','starlight')
LOOKS=('nebula','aurora','starlight')
FAMILY_LOOK=('nebula','aurora','nebula','starlight','starlight','aurora','starlight')
STEMS=('Neb','Lum','Ori','Vexa','Astr','Phera','Glima','Zori','Mira','Cosmi')
ENDS=('by','io','ix','a','on','ora','u','ra','yx','iri')
def fnv(text: str) -> int:
    h=2166136261
    for byte in text.encode('utf-8'):
        h=((h^byte)*16777619)&0xffffffff
    return h

def generator(seed: str, domain: str):
    state=fnv(f'1|{domain}|{seed}') or 0x6d2b79f5
    while True:
        state^=(state<<13)&0xffffffff
        state^=state>>17
        state^=(state<<5)&0xffffffff
        state &= 0xffffffff
        yield state / 4294967296.0

def expected_genesis(seed: str):
    rng=generator(seed,'stats'); stats=[50]*10
    for _ in range(270):
        source=int(next(rng)*10); target=int(next(rng)*10)
        if source!=target and stats[source]>20 and stats[target]<80:
            stats[source]-=1;stats[target]+=1
    trng=generator(seed,'temperament')
    temper=[int(20+next(trng)*61) for _ in range(5)]
    naming=generator(seed,'name')
    name=STEMS[int(next(naming)*len(STEMS))]+ENDS[int(next(naming)*len(ENDS))]
    return stats,temper,name

def import_export(source: Path, output: Path) -> dict:
    with zipfile.ZipFile(source) as z:
        if len(z.namelist()) > 64: raise InvalidExport('Unexpected archive file count')
        tiles = checked_read(z,TILES,8192)
        palette = checked_read(z,PALETTE,32)
        legacy = checked_read(z,BCG,60)
        if len(tiles)!=8192 or len(palette)!=32: raise InvalidExport('4x64x64 4bpp frames / palette length mismatch')
        check_guest_bcg1(legacy)
        profile = None; seed_hash = None; version = None
        if BCP in z.namelist():
            profile_bytes=checked_read(z,BCP,64)
            profile=parse_bcp1(profile_bytes)
            details=json.loads(checked_read(z,PROFILE,8192))
            if not isinstance(details,dict): raise InvalidExport('Invalid profile JSON')
            if details.get('schema')!='beast-cage-creature-v1':
                raise InvalidExport('Unrecognized Beast Cage creature schema')
            if details.get('family') != FAMILIES[profile['family']] or details.get('baseLook') != LOOKS[profile['look']] or details.get('baseLook')!=FAMILY_LOOK[profile['family']]:
                raise InvalidExport('Family/look mismatch between BCP1 and public JSON')
            seed=details.get('seed'); version=details.get('version'); generated_id=details.get('id')
            if not isinstance(seed,str) or not 1<=len(seed)<=64 or any(ord(x)<32 or ord(x)==127 for x in seed) or unicodedata.normalize('NFC',seed.strip())!=seed:
                raise InvalidExport('Invalid public seed')
            if version != 1: raise InvalidExport('Unsupported generator version')
            if not isinstance(generated_id,str) or not generated_id.startswith('bb-') or len(generated_id)!=11:
                raise InvalidExport('Malformed public generator ID')
            try: expected_id = int(generated_id[3:],16)
            except ValueError as exc: raise InvalidExport('Malformed public generator ID') from exc
            if expected_id != int(profile['public_identity'],16):
                raise InvalidExport('Public identity mismatch between JSON and BCP1')
            names=('hp','energy','signal','memory','resonance','agility',
                   'chaos','stability','curiosity','evolution')
            traits=('curiosity','energy','playfulness','caution','independence')
            if [details.get('game',{}).get('stats',{}).get(k) for k in names]!=profile['game_stats']:
                raise InvalidExport('Game stat mismatch between BCP1 and JSON')
            if [details.get('temperament',{}).get(k) for k in traits]!=profile['temperament']:
                raise InvalidExport('Temperament mismatch between BCP1 and JSON')
            correct_stats,correct_temper,correct_name=expected_genesis(seed)
            if profile['game_stats']!=correct_stats or profile['temperament']!=correct_temper or details.get('name')!=correct_name:
                raise InvalidExport('Game stats/temperament/name diverge from exact versioned Beast Box seed generation')
            game=details.get('game',{})
            if game.get('level')!=1 or game.get('experience')!=0:
                raise InvalidExport('Expected initial exported game profile, not modified progress')
            appearance=details.get('appearance',{})
            if not isinstance(appearance,dict) or appearance.get('hueShift')!=profile['hue']:
                raise InvalidExport('Original pixel hue disagrees with BCP1 profile')
            if legacy[5]!=profile['look']:
                raise InvalidExport('BCG1 original look and BCP1 generated palette disagree')
            # FNV-1a: match generator's public identity derivation to detect tampering.
            h=2166136261
            for ch in f'identity|{version}|{seed}'.encode('utf-8'):
                h=((h^ch)*16777619)&0xffffffff
            if h!=expected_id: raise InvalidExport('Public ID does not match generator seed')
            h=2166136261
            for ch in f'lost-cosmos|{seed}'.encode('utf-8'):
                h=((h^ch)*16777619)&0xffffffff
            seed_hash=h
        output.mkdir(parents=True,exist_ok=True)
        content=['#ifndef LOST_COSMOS_IMPORTED_COMPANION_H','#define LOST_COSMOS_IMPORTED_COMPANION_H',
                 '/* Build-time original Beast Cage pixel frames. Allocate OBJ resources in the actual engine. */',
                 as_c('lc_imported_companion_tiles',tiles),as_c('lc_imported_companion_palette',palette)]
        if profile is not None:
            content.append('#define LC_IMPORT_HAS_BCP1 1')
            content.append(f'#define LC_IMPORT_SEED_HASH 0x{seed_hash:08x}u')
            content.append(as_c('lc_imported_companion_bcp1',profile_bytes))
        content.append('#endif\n')
        (output/'imported_companion.h').write_text('\n'.join(content))
        receipt={'schema':'lost-cosmos-beastbox-build-import-v1',
                 'export_zip_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                 'tiles_sha256':hashlib.sha256(tiles).hexdigest(),
                 'palette_sha256':hashlib.sha256(palette).hexdigest(),
                 'BCG1_guest_validated':True,'BCP1_game_profile':profile,
                 'portable_seed_hash':seed_hash,'generator_version':version,
                 'frames':['idle','listening','thinking','celebrating'],
                 'not_included':['owner_memory','real_sensor_data','model_weights','cloud_credentials']}
        (output/'import_receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
        return receipt

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('export_zip',type=Path)
    ap.add_argument('output_folder',type=Path)
    args=ap.parse_args()
    try:
        receipt=import_export(args.export_zip,args.output_folder)
    except (InvalidExport,OSError,ValueError,zipfile.BadZipFile) as exc:
        print('IMPORT REJECTED:',exc,file=sys.stderr);return 1
    print('IMPORT VALIDATED:',receipt['BCP1_game_profile'] or 'legacy sprites only')
    return 0
if __name__=='__main__': sys.exit(main())
