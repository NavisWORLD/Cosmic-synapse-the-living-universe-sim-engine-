#!/usr/bin/env python3
"""Assert text is in the actual rendered frame, not just the BG tile map."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from mgba import Mgba, sha256


def readable(emu, rows, minimum=50):
    pixels = emu.rgb()
    bright = sum(max(pixels[(y * 240 + x) * 3:(y * 240 + x) * 3 + 3]) >= 220
                 for row in rows for y in range(row * 8, (row + 1) * 8)
                 for x in range(16, 224))
    assert bright >= minimum, f'Rendered rows {rows} have only {bright} readable pixels'
    return bright


def run(rom, elf, out):
    out.mkdir(parents=True, exist_ok=True)
    report = {'rom_sha256': sha256(rom), 'controller_only': True, 'passed': False}
    with Mgba(rom, elf=elf, trace_path=out / 'title_inputs.jsonl') as emu:
        try:
            emu.step((), 180)
            for gap in (0, 1, 7, 61):
                emu.step((), gap)
                for row in range(12, 16):
                    readable(emu, [row])
            emu.screenshot(out / 'title.png')
            emu.tap('DOWN', hold=12, release=12)
            emu.tap('DOWN', hold=12, release=12)
            emu.tap('A', hold=12, release=12)
            assert emu.read_symbol('v10_title_sub') == 2
            readable(emu, [12])
            audio = emu.read_symbol('audio_on')
            emu.tap('A', hold=12, release=12)
            assert emu.read_symbol('audio_on') != audio
            readable(emu, [12])
            emu.screenshot(out / 'options.png')
            emu.tap('B', hold=12, release=12)
            emu.tap('DOWN', hold=12, release=12)
            emu.tap('A', hold=12, release=12)
            assert emu.read_symbol('v10_title_sub') == 3
            readable(emu, [12, 14, 16], 200)
            emu.screenshot(out / 'credits.png')
            emu.tap('B', hold=12, release=12)
            emu.tap('DOWN', hold=12, release=12)
            emu.tap('A', hold=12, release=12)
            for card in range(10):
                emu.step((), 90)
                assert emu.read_symbol('v10_opening') == 1
                assert emu.read_symbol('v10_opening_step') == card
                readable(emu, [14], 70)
                readable(emu, [15, 16, 17], 150)
                emu.screenshot(out / f'prologue_{card + 1:02d}.png')
                emu.tap('A', hold=12, release=12)
            emu.step((), 600)
            assert emu.read_symbol('v10_opening') == 0
            assert emu.read_symbol('current_room') == 2
            save = emu.export_save(out / 'title_test.sav')
        finally:
            (out / 'title_report.json').write_text(json.dumps(report, indent=2) + '\n')
    # Existing saves must still have the title, a reversible overwrite prompt,
    # and a working CONTINUE; all are exercised through ordinary controls.
    with Mgba(rom, elf=elf, save_path=save) as emu:
        emu.step((), 600)
        assert emu.read_symbol('v10_has_save') == 1
        emu.tap('A', hold=12, release=12)
        assert emu.read_symbol('v10_title_sub') == 1
        readable(emu, [12, 14], 200)
        emu.screenshot(out / 'overwrite.png')
        emu.tap('B', hold=12, release=12)
        assert emu.read_symbol('v10_title_sub') == 0
        emu.tap('DOWN', hold=12, release=12)
        emu.tap('A', hold=12, release=12)
        emu.step((), 600)
        assert emu.read_symbol('intro') == 0
        assert emu.read_symbol('current_room') == 2
    report['passed'] = True
    (out / 'title_report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--rom', type=Path, default=ROOT / 'LOST_COSMOS_V10_SOURCE/LOST_COSMOS_V10_OPENING_QA.gba')
    ap.add_argument('--elf', type=Path, default=ROOT / 'LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.elf')
    ap.add_argument('--out', type=Path, default=ROOT / 'artifacts/mgba_title')
    a = ap.parse_args()
    run(a.rom, a.elf, a.out)
