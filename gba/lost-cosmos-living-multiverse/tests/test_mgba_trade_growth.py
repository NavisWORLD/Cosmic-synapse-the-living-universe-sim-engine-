#!/usr/bin/env python3
"""Headless mGBA check: a traded, grown LCG1 beast appears on the Beast Box page.

The save is the shared EARTH fixture plus one cage record in the gap before
the V11.1 manual slots. The cartridge must import one identity and publish
the trade epoch without rewriting the cage record.
"""
from __future__ import annotations

import argparse
import json
import sys
import traceback
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from lc_mailbox import GROWTH_OFFSET, MAILBOX_OFFSET, attach_growth, build_growth, fixture_save
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


# lc_imported_companion_bcp1 public id, little-endian at byte 24.
# IMPORTED_BEAST=1 new games also keep this baked snapshot. It is a different
# identity from the cage trade, and cold boot must leave it beside the trade.
COMPILED_SNAPSHOT_ID = 0xF5A4CB6D


def roster_entry(data, profile):
    roster = data[1024:1024 + 252]
    if roster[:4] != b"LCR1" or zlib.crc32(roster[:248]) != int.from_bytes(roster[248:252], "little"):
        raise RuntimeError("Imported roster checksum failed")
    entries = [roster[8 + i * 20:28 + i * 20] for i in range(roster[5])]
    matches = [p for p in entries if int.from_bytes(p[8:12], "little") == profile["public_id"]]
    if len(matches) != 1 or matches[0][0] != profile["species"] or matches[0][3] != 14:
        raise RuntimeError("Traded beast identity, species, bond, or duplicate check failed")
    return entries, matches[0]


def trade_roster_ok(entries, profile):
    """The traded identity is already unique. One baked snapshot may sit with it."""
    others = [p for p in entries if int.from_bytes(p[8:12], "little") != profile["public_id"]]
    if not others:
        return True
    if len(others) != 1:
        return False
    extra = others[0]
    return int.from_bytes(extra[8:12], "little") == COMPILED_SNAPSHOT_ID and extra[0] == 128


def ui_row(emu, row):
    tiles = emu.read_range(0x06000000 + 28 * 2048 + row * 64, 60)
    return "".join(
        chr(65 + ((int.from_bytes(tiles[i:i + 2], "little") & 1023) - 64))
        if 64 <= (int.from_bytes(tiles[i:i + 2], "little") & 1023) < 90 else " "
        for i in range(0, 60, 2)
    )


def run(rom: Path, elf: Path, out: Path) -> None:
    header = (ROOT / "LOST_COSMOS_V10_SOURCE/imported_companion.h").read_text()
    snapshot = ", ".join(f"0x{b:02x}" for b in COMPILED_SNAPSHOT_ID.to_bytes(4, "little"))
    if snapshot not in header:
        raise RuntimeError("Compiled snapshot id no longer matches imported_companion.h")
    out.mkdir(parents=True, exist_ok=True)
    base, profile = fixture_save()
    growth = build_growth(profile["public_id"], epoch=4, layer=2, points=10, memory_crc=1, chain_crc=2, trade=True, grown=True)
    sav = attach_growth(base, growth)
    save = out / "trade_growth.sav"
    save.write_bytes(sav)
    report = {
        "suite": "lost_cosmos_trade_growth",
        "rom_sha256": sha256(rom),
        "species_name": profile["species_name"],
        "public_id": f"{profile['public_id']:08x}",
        "epoch": 4,
        "controller_only": True,
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
            if emu.read_symbol("lc_mail_epoch") != 4 or emu.read_symbol("lc_mail_trade") != 1 or emu.read_symbol("lc_mail_grown") != 1:
                raise RuntimeError("Cage epoch was not published")
            emu.tap("START", hold=12, release=12)
            wait(emu, lambda: emu.read_symbol("game_mode") == 2 and emu.read_symbol("pause_page") == 0, "pause menu")
            goto_index(emu, 2)
            emu.tap("A", hold=10, release=10)
            emu.step((), 8)
            if "EARTH" not in ui_row(emu, 5 + (emu.read_symbol("v11_sel") % 5)):
                raise RuntimeError("Party did not show the traded beast")
            emu.screenshot(out / "01_party.png")
            emu.tap("B", hold=10, release=10)
            emu.step((), 8)
            goto_index(emu, 8)
            emu.tap("A", hold=10, release=10)
            emu.step((), 8)
            if emu.read_symbol("pause_page") != 26:
                raise RuntimeError("Beast Box page did not open")
            row4, row6, row14 = ui_row(emu, 4), ui_row(emu, 6), ui_row(emu, 14)
            if "BEAST IMPORTED" not in row4 or "EARTH" not in row6 or "TRADE EPOCH" not in row14:
                raise RuntimeError(f"Beast Box did not show the traded epoch: {row4!r} {row6!r} {row14!r}")
            emu.screenshot(out / "02_trade_epoch.png")
            exported = emu.export_save(out / "trade_after.sav")
            data = exported.read_bytes()
            entries, creature = roster_entry(data, profile)
            if data[GROWTH_OFFSET:GROWTH_OFFSET + 4] != b"LCG1":
                raise RuntimeError("Cage record was not preserved")
            if int.from_bytes(data[GROWTH_OFFSET + 8:GROWTH_OFFSET + 12], "little") != 4:
                raise RuntimeError("Cage epoch changed in SRAM")
            if zlib.crc32(data[GROWTH_OFFSET:GROWTH_OFFSET + 60]) != int.from_bytes(data[GROWTH_OFFSET + 60:GROWTH_OFFSET + 64], "little"):
                raise RuntimeError("Cage checksum failed after play")
            if any(b != 0xFF for b in data[25540:25600]):
                raise RuntimeError("The gap before the manual slots was overwritten")
            flags = data[MAILBOX_OFFSET + 5]
            if flags & 1 or not flags & 4:
                raise RuntimeError(f"Mailbox was not consumed: flags={flags:#x}")
            report["bond"] = creature[3]
            report["party_count"] = len(entries)
        except Exception as exc:
            report["failure"] = repr(exc)
            report["traceback"] = traceback.format_exc()
            try:
                emu.screenshot(out / "FAILED_NATIVE_FRAME.png")
            except Exception:
                pass
            raise
        finally:
            (out / "trade_growth_report.json").write_text(json.dumps(report, indent=2) + "\n")
    with Mgba(rom, elf=elf, save_path=exported) as emu:
        try:
            emu.step((), 180)
            emu.tap("DOWN", hold=12, release=12)
            emu.tap("A", hold=12, release=12)
            wait(emu, lambda: emu.read_symbol("intro") == 0 and emu.read_symbol("lc_mail_epoch") == 4, "cold-boot epoch")
            entries, _creature = roster_entry(emu.read_range(0x0E000000, 8192), profile)
            if not trade_roster_ok(entries, profile):
                ids = [hex(int.from_bytes(p[8:12], "little")) for p in entries]
                raise RuntimeError(f"Cold boot duplicated or removed the traded beast: {ids}")
            emu.screenshot(out / "03_cold_boot.png")
            report["cold_boot_verified"] = True
            report["passed"] = True
        except Exception as exc:
            report["failure"] = repr(exc)
            report["traceback"] = traceback.format_exc()
            raise
        finally:
            (out / "trade_growth_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rom", type=Path, default=ROOT / "LOST_COSMOS_V10_SOURCE/LOST_COSMOS_V10_OPENING_QA.gba")
    ap.add_argument("--elf", type=Path, default=ROOT / "LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.elf")
    ap.add_argument("--out", type=Path, default=ROOT / "artifacts/mgba_trade")
    args = ap.parse_args()
    run(args.rom.resolve(), args.elf.resolve(), args.out.resolve())
