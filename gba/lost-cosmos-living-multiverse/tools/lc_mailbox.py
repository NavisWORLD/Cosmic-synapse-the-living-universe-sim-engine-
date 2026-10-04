#!/usr/bin/env python3
"""LCX1 SRAM mailbox for one standard Lost Cosmos ROM.

The cartridge validates BCP1 and adds the creature. This module only writes
the unused mailbox at SRAM 24832. It does not write the LCR1 roster, and it
does not accept raw sensor samples.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from import_beastbox import expected_genesis, fnv

MAILBOX_OFFSET = 24832
MAILBOX_BYTES = 644
MAIL_BODY = 640
GROWTH_OFFSET = 25476
GROWTH_BYTES = 64
SRAM_SIZE = 32768
FAMILIES = ('nebula', 'aurora', 'void', 'plasma', 'memory', 'signal', 'starlight')
LOOKS = {'nebula': 0, 'aurora': 1, 'starlight': 2}
FAMILY_LOOK = ('nebula', 'aurora', 'nebula', 'starlight', 'starlight', 'aurora', 'starlight')
SPECIES = ('NEBULA', 'AURORA', 'VOID', 'PLASMA', 'MEMORY', 'SIGNAL', 'STARLIGHT')
# Living Universe screenshot/test fixture. JS must produce the same save bytes.
FIXTURE = dict(world='EARTH', evolution=0.25, biosphere=0.5, life_events=1, focus=40, calm=70, spark=15)


def floor_div(a: int, b: int) -> int:
    return a // b


def living_seed(world: str, evolution: float, biosphere: float, life_events: int) -> str:
    raw = ''.join(ch for ch in str(world).upper() if ('A' <= ch <= 'Z') or ('0' <= ch <= '9'))
    w = raw or 'WORLD'
    evo = int(max(0.0, float(evolution)) * 1000)
    bio = int(max(0.0, min(1.0, float(biosphere))) * 1000)
    life = int(max(0.0, float(life_events)))
    return f'lu1|{w}|{evo}|{bio}|{life}'


def apply_traits(temper: list[int], focus: int, calm: int, spark: int) -> list[int]:
    shifts = (
        floor_div(calm - 50, 5),
        floor_div(spark - 50, 5),
        floor_div(spark - 40, 6),
        floor_div(calm - 40, 5),
        floor_div(focus - 50, 5),
    )
    return [max(20, min(80, int(v) + int(s))) for v, s in zip(temper, shifts)]


def build_bcp1(family: int, stats: list[int], temper: list[int], hue: int, public_id: int) -> bytes:
    if not 0 <= family <= 6:
        raise ValueError('family out of range')
    if sum(stats) != 500 or any(not 20 <= x <= 80 for x in stats + temper):
        raise ValueError('BCP1 budget/range')
    if not public_id:
        raise ValueError('public id is zero')
    look_name = FAMILY_LOOK[family]
    p = bytearray(64)
    p[:4] = b'BCP1'
    p[4] = 1
    p[5] = family
    p[6] = LOOKS[look_name]
    p[8:18] = bytes(int(x) for x in stats)
    p[18:23] = bytes(int(x) for x in temper)
    p[23] = int(hue) & 0xFF
    struct.pack_into('<I', p, 24, public_id & 0xFFFFFFFF)
    struct.pack_into('<I', p, 60, zlib.crc32(p[:60]) & 0xFFFFFFFF)
    return bytes(p)


def living_profile(world: str, evolution: float, biosphere: float, life_events: int,
                   focus: int, calm: int, spark: int) -> dict:
    for name, value in (('focus', focus), ('calm', calm), ('spark', spark)):
        if not 0 <= int(value) <= 100:
            raise ValueError(f'{name} must be 0..100')
    seed = living_seed(world, evolution, biosphere, life_events)
    family = fnv(seed) % 7
    stats, temper, _name = expected_genesis(seed)
    temper = apply_traits(list(temper), int(focus), int(calm), int(spark))
    hue = max(-32, min(31, floor_div(int(spark) - int(calm), 2)))
    public_id = fnv(f'identity|1|{seed}') or 1
    game_seed = fnv(f'lost-cosmos|{seed}') or 1
    call = ''.join(ch for ch in str(world).upper() if ('A' <= ch <= 'Z') or ('0' <= ch <= '9'))[:12] or 'LIVING'
    bcp = build_bcp1(family, list(stats), temper, hue, public_id)
    return dict(bcp1=bcp, game_seed=game_seed, callsign=call, family=family,
                species=128 + family, species_name=SPECIES[family], public_id=public_id,
                focus=int(focus), calm=int(calm), spark=int(spark), seed=seed, hue=hue)


def beast_profile(seed: str, family_name: str, hue: int = 0, focus: int = 50, calm: int = 50, spark: int = 50) -> dict:
    if family_name not in FAMILIES:
        raise ValueError('unknown family')
    family = FAMILIES.index(family_name)
    stats, temper, name = expected_genesis(seed)
    public_id = fnv(f'identity|1|{seed}') or 1
    game_seed = fnv(f'lost-cosmos|{seed}') or 1
    bcp = build_bcp1(family, list(stats), list(temper), int(hue), public_id)
    call = ''.join(ch for ch in name.upper() if ('A' <= ch <= 'Z') or ('0' <= ch <= '9'))[:12] or 'BEAST'
    return dict(bcp1=bcp, game_seed=game_seed, callsign=call, family=family,
                species=128 + family, species_name=SPECIES[family], public_id=public_id,
                focus=int(focus), calm=int(calm), spark=int(spark), seed=seed, hue=int(hue), name=name)


def build_mailbox(profile: dict) -> bytes:
    buf = bytearray(MAILBOX_BYTES)
    buf[0:4] = b'LCX1'
    buf[4] = 1
    buf[5] = 1
    buf[6] = int(profile['focus']) & 0xFF
    buf[7] = int(profile['calm']) & 0xFF
    buf[8] = int(profile['spark']) & 0xFF
    struct.pack_into('<I', buf, 10, int(profile['game_seed']) & 0xFFFFFFFF)
    call = str(profile['callsign']).encode('ascii')[:12]
    buf[14:14 + len(call)] = call
    bcp = profile['bcp1']
    if len(bcp) != 64:
        raise ValueError('BCP1 must be 64 bytes')
    buf[32:96] = bcp
    struct.pack_into('<I', buf, MAIL_BODY, zlib.crc32(buf[:MAIL_BODY]) & 0xFFFFFFFF)
    return bytes(buf)


def build_save(profile: dict) -> bytes:
    mail = build_mailbox(profile)
    if MAILBOX_OFFSET + len(mail) > GROWTH_OFFSET:
        raise AssertionError('mailbox collides with the cage record')
    sav = bytearray(b'\xff' * SRAM_SIZE)
    sav[MAILBOX_OFFSET:MAILBOX_OFFSET + len(mail)] = mail
    return bytes(sav)


def build_growth(public_id: int, epoch: int = 0, layer: int = 0, points: int = 0,
                 memory_crc: int = 0, chain_crc: int = 0, trade: bool = False, grown: bool = False) -> bytes:
    if not public_id:
        raise ValueError('public id is zero')
    if not 0 <= int(epoch) <= 0xFFFFFFFF:
        raise ValueError('epoch does not fit the cartridge field')
    if not 0 <= int(layer) <= 999 or not 0 <= int(points) <= 999:
        raise ValueError('growth layer')
    buf = bytearray(GROWTH_BYTES)
    buf[0:4] = b'LCG1'
    buf[4] = 1
    buf[5] = (1 if trade else 0) | (2 if grown else 0)
    struct.pack_into('<I', buf, 8, int(epoch) & 0xFFFFFFFF)
    struct.pack_into('<HH', buf, 12, int(layer), int(points))
    struct.pack_into('<III', buf, 16, int(memory_crc) & 0xFFFFFFFF, int(chain_crc) & 0xFFFFFFFF, int(public_id) & 0xFFFFFFFF)
    struct.pack_into('<I', buf, 60, zlib.crc32(buf[:60]) & 0xFFFFFFFF)
    return bytes(buf)


def attach_growth(sav: bytes, growth: bytes) -> bytes:
    if len(sav) != SRAM_SIZE or len(growth) != GROWTH_BYTES:
        raise ValueError('growth size')
    if GROWTH_OFFSET + GROWTH_BYTES > 25600:
        raise AssertionError('growth collides with the reserved LCM1 region')
    out = bytearray(sav)
    out[GROWTH_OFFSET:GROWTH_OFFSET + GROWTH_BYTES] = growth
    return bytes(out)


def fixture_save() -> tuple[bytes, dict]:
    profile = living_profile(**FIXTURE)
    return build_save(profile), profile


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dump', action='store_true', help='print the shared fixture summary as JSON')
    ap.add_argument('--sav', type=Path, help='write the fixture 32 KiB save')
    args = ap.parse_args()
    sav, profile = fixture_save()
    if args.sav:
        args.sav.parent.mkdir(parents=True, exist_ok=True)
        args.sav.write_bytes(sav)
    if args.dump or not args.sav:
        public = {k: profile[k] for k in ('species', 'species_name', 'public_id', 'game_seed', 'seed', 'family', 'callsign', 'hue')}
        public['public_id'] = f'{profile["public_id"]:08x}'
        public['game_seed'] = f'{profile["game_seed"]:08x}'
        public['sha256'] = hashlib.sha256(sav).hexdigest()
        public['mailbox_offset'] = MAILBOX_OFFSET
        print(json.dumps(public, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
