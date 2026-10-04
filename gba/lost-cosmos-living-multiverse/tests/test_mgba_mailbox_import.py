#!/usr/bin/env python3
"""Headless mGBA check: an LCX1 mailbox becomes a living creature on a new game.

Boots the normal (non-QA) ROM with a 32 KiB save whose only authored bytes are
the mailbox. Controller input starts the opening and skips it. The cartridge
must add the creature during the real save and draw it on the party page.
"""
from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from lc_mailbox import MAILBOX_OFFSET, fixture_save
from mgba import Mgba, sha256


def wait(emu, pred, label, budget=1800):
    for _ in range((budget + 7) // 8):
        if pred():
            return
        emu.step((), 8)
    raise RuntimeError(f"Timed out waiting for {label}")


def goto_index(emu, target):
    for _ in range(16):
        cur = emu.read_symbol("pause_sel")
        if cur == target:
            return
        cur_col = 1 if cur >= 5 else 0
        want_col = 1 if target >= 5 else 0
        if cur_col != want_col:
            key = "RIGHT" if want_col else "LEFT"
        else:
            row = cur % 5
            want = target % 5
            down = (want - row) % 5
            up = (row - want) % 5
            key = "DOWN" if down <= up else "UP"
        emu.tap(key, hold=10, release=14)
        emu.step((), 6)
    raise RuntimeError(f"Menu navigation failed: {emu.read_symbol('pause_sel')} != {target}")


def run(rom: Path, elf: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    sav, profile = fixture_save()
    save = out / "mailbox_import.sav"
    save.write_bytes(sav)
    report = {
        "suite": "lost_cosmos_mailbox_import",
        "rom_sha256": sha256(rom),
        "species": profile["species"],
        "species_name": profile["species_name"],
        "public_id": f"{profile['public_id']:08x}",
        "callsign": profile["callsign"],
        "passed": False,
    }
    with Mgba(rom, elf=elf, save_path=save) as emu:
        try:
            emu.step((), 180)
            emu.screenshot(out / "00_title.png")
            if emu.read_symbol("intro") != 1:
                raise RuntimeError("Native title missing")
            emu.tap("A", hold=12, release=12)
            wait(emu, lambda: emu.read_symbol("v10_opening") == 1, "opening")
            emu.tap("START", hold=12, release=12)
            wait(emu, lambda: emu.read_symbol("v10_opening") == 0 and emu.read_symbol("current_room") == 2 and emu.read_symbol("lc_mail_ready") == 1, "imported field")
            emu.step((), 20)
            emu.screenshot(out / "01_field.png")
            if emu.read_symbol("lc_mail_species") != profile["species"]:
                raise RuntimeError("Mailbox species was not published")
            if emu.read_symbol("lc_party", width=1) < 1:
                raise RuntimeError("Party is empty after import")
            emu.tap("START", hold=12, release=12)
            wait(emu, lambda: emu.read_symbol("game_mode") == 2 and emu.read_symbol("pause_page") == 0, "pause menu")
            goto_index(emu, 2)
            emu.tap("A", hold=10, release=10)
            emu.step((), 8)
            if emu.read_symbol("pause_page") != 18:
                raise RuntimeError("Party page did not open")
            emu.screenshot(out / "02_party.png")
            emu.tap("B", hold=10, release=10)
            emu.step((), 8)
            goto_index(emu, 8)
            emu.tap("A", hold=10, release=10)
            emu.step((), 8)
            if emu.read_symbol("pause_page") != 26:
                raise RuntimeError("Beast Box page did not open")
            emu.screenshot(out / "03_beast_box.png")
            exported = emu.export_save(out / "mailbox_after.sav")
            data = exported.read_bytes()
            if data[:4] != b"LCV5":
                raise RuntimeError("Main save header missing")
            roster = data[1024:1024 + 252]
            if roster[:4] != b"LCR1" or roster[5] != 1 or roster[8] != profile["species"]:
                raise RuntimeError(f"Roster did not record the imported species: {roster[:12].hex()}")
            identity = int.from_bytes(roster[16:20], "little")
            if identity != profile["public_id"]:
                raise RuntimeError("Imported public id mismatch")
            if roster[11] != 14:
                raise RuntimeError(f"Bond {roster[11]} did not follow focus/calm")
            flags = data[MAILBOX_OFFSET + 5]
            if data[MAILBOX_OFFSET:MAILBOX_OFFSET + 4] != b"LCX1" or (flags & 1) or not (flags & 4):
                raise RuntimeError(f"Mailbox was not consumed: flags={flags:#x}")
            report["bond"] = roster[11]
            report["passed"] = True
        except Exception as exc:
            report["failure"] = repr(exc)
            report["traceback"] = traceback.format_exc()
            try:
                emu.screenshot(out / "FAILED_NATIVE_FRAME.png")
            except Exception:
                pass
            raise
        finally:
            (out / "mailbox_import_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rom", type=Path, default=ROOT / "LOST_COSMOS_V10_SOURCE/LOST_COSMOS_V10_OPENING_QA.gba")
    ap.add_argument("--elf", type=Path, default=ROOT / "LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.elf")
    ap.add_argument("--out", type=Path, default=ROOT / "artifacts/mgba_mailbox")
    args = ap.parse_args()
    run(args.rom.resolve(), args.elf.resolve(), args.out.resolve())
