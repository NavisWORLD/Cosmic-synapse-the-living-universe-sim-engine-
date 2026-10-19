#!/usr/bin/env python3
"""V12.2b Beast Box <-> Lost Cosmos ecosystem bridge records (see
LOST_COSMOS_V10_SOURCE/ecosystem_bridge.h for the byte map).

LCQ1 (site -> game, SRAM 25540, 60 bytes): the beast's latest Rigetti growth
state. The Rigetti loop is a QVM run: SIMULATED. The SIMULATED flag is
mandatory; the cartridge rejects records without it.
LCE1 (game -> site, SRAM 24704, 128 bytes): in-game experience summary.
"""
from __future__ import annotations
import argparse, json, struct, sys
from pathlib import Path

LCQ_OFFSET, LCQ_BYTES = 25540, 60
LCE_OFFSET, LCE_BYTES = 24704, 128
SRAM_SIZE = 32768
CHANNELS = ('frequency_mass', 'geometric_phase', 'spectral_flatness', 'phase_velocity', 'entanglement', 'valence',
            'arousal', 'dominance', 'audio_psi', 'phi_harmonics', 'av_coherence', 'quantum_entropy')
MOODS = ('JOY', 'CURIOUS', 'FEAR', 'CALM', 'MISCHIEF')


def fnv(b: bytes) -> int:
    h = 2166136261
    for x in b:
        h = ((h ^ x) * 16777619) & 0xFFFFFFFF
    return h


def rigetti_offsets(counts: list[int]) -> list[int]:
    """Map SIMULATED Rigetti counts (00,01,10,11) to 12 s8 offsets (Q12/16).
    Same rule as the site's ingest module. Each channel gets a signed bias from
    one pair of outcome probabilities; |offset| <= 32 (= 0.125)."""
    n = sum(counts) or 1
    p = [c / n for c in counts]
    pairs = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    out = []
    for k in range(12):
        a, b = pairs[k % 6]
        d = (p[a] - p[b]) if k < 6 else (p[a] + p[b] - 0.5)
        out.append(max(-32, min(32, int(round(d * 64)))))
    return out


def build_lcq(public_id: int, counts: list[int], cycle: int = 0, offsets: list[int] | None = None) -> bytes:
    if not public_id:
        raise ValueError('public id is zero')
    offs = offsets if offsets is not None else rigetti_offsets(counts)
    if len(offs) != 12 or any(not -64 <= o <= 64 for o in offs) or len(counts) != 4:
        raise ValueError('LCQ1 offsets/counts')
    b = bytearray(LCQ_BYTES)
    b[0:4] = b'LCQ1'; b[4] = 1; b[5] = 1  # SIMULATED
    struct.pack_into('<I', b, 8, public_id & 0xFFFFFFFF)
    struct.pack_into('<12b', b, 12, *offs)
    struct.pack_into('<I4H', b, 24, cycle & 0xFFFFFFFF, *[min(65535, int(c)) for c in counts])
    struct.pack_into('<I', b, 56, fnv(bytes(b[:56])))
    return bytes(b)


def attach_lcq(sav: bytes, rec: bytes) -> bytes:
    if len(sav) != SRAM_SIZE or len(rec) != LCQ_BYTES:
        raise ValueError('size')
    out = bytearray(sav); out[LCQ_OFFSET:LCQ_OFFSET + LCQ_BYTES] = rec
    return bytes(out)


def parse_lce(sav: bytes) -> dict | None:
    r = sav[LCE_OFFSET:LCE_OFFSET + LCE_BYTES]
    if len(r) != LCE_BYTES or r[:4] != b'LCE1' or r[4] != 1:
        return None
    if struct.unpack_from('<I', r, 124)[0] != fnv(r[:124]):
        return None
    head = r[35]
    ring = list(r[36:68])
    hist = [MOODS[m - 1] for m in (ring[head:] + ring[:head]) if 1 <= m <= 5]
    return dict(format='LCE1', lcq_applied=bool(r[5] & 1), heartbeats=struct.unpack_from('<H', r, 6)[0],
                identity=f"{struct.unpack_from('<I', r, 8)[0]:08x}",
                channels={c: round(r[12 + i] / 255, 3) for i, c in enumerate(CHANNELS)},
                mood={k: round(r[24 + i] / 255, 3) for i, k in enumerate(('coherence', 'joy', 'curiosity', 'fear', 'calm', 'mischief'))},
                needs=dict(trust=r[30], energy=r[31], curiosity=r[32], avoid=r[33]), quests_touched=r[34],
                mood_history=hist, cst_steps=struct.unpack_from('<I', r, 68)[0])


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('inject'); a.add_argument('sav'); a.add_argument('--id', required=True); a.add_argument('--counts', required=True); a.add_argument('--cycle', type=int, default=0); a.add_argument('-o', required=True)
    e = sub.add_parser('export'); e.add_argument('sav')
    ns = ap.parse_args()
    if ns.cmd == 'inject':
        rec = build_lcq(int(ns.id, 16), [int(x) for x in ns.counts.split(',')], ns.cycle)
        Path(ns.o).write_bytes(attach_lcq(Path(ns.sav).read_bytes(), rec)); print('LCQ1 written (SIMULATED)')
    else:
        print(json.dumps(parse_lce(Path(ns.sav).read_bytes()), indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
