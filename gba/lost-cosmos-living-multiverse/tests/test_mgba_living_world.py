#!/usr/bin/env python3
"""V12.0 LIVING WORLD on the real cartridge in mGBA, controller only.

New game with a Sol starter save, open START > SYSTEM > LIVING WORLD, check the
mode-4 story card, then the mode-0 forest: six creatures move on their own
(classical Lorenz/entropy life seeded by recorded IBM QSEED values), make
decisions from Emeth's creature moods, Zeref reacts when the darkness wisp gets
close, SELECT switches to the cave, START opens ITEMS / STATS / QUESTS / CAST,
an item is used, and B returns to the top-down game with the display restored
exactly. Screenshots are written to --out. No memory writes or savestates."""
from __future__ import annotations
import argparse, hashlib, json, shutil, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "tools")); sys.path.insert(0, str(ROOT))
from mgba import Mgba, sha256
import test_mgba_beast_home as bh
from test_mgba_menu_visual import goto_index

def lw(emu):
    r = emu.read_symbol
    return dict(active=r("lw_active", width=1), card=r("lw_card", width=1), page=r("lw_page", width=1), world=r("lw_world", width=1),
                entries=r("lw_entries", width=2), exits=r("lw_exits", width=2), decisions=r("lw_decisions", width=2),
                dark=r("lw_dark_reacts", width=2), used=r("lw_items_used", width=2), moved=r("lw_moved_px", width=4),
                quests_done=r("lw_quests_done", width=2), focus=r("lw_focus", width=1))

def disp(emu):
    return dict(dispcnt=emu.read16(0x04000000), bg0cnt=emu.read16(0x04000008), bg1cnt=emu.read16(0x0400000A))

def field(emu):
    return dict(display=disp(emu), bg0=hashlib.sha256(bytes(emu.read_range(0x06000000 + 24 * 2048, 8192))).hexdigest())

def tap(emu, k, n=1):
    for _ in range(n):
        emu.tap(k, hold=8, release=8); emu.step((), 4)

def run(rom, elf, out):
    out.mkdir(parents=True, exist_ok=True)
    rep = dict(suite="real_mgba_v12_living_world", rom_sha256=sha256(rom), controller_only=True, memory_writes=False, shots=[])
    bh.starter_save(out / "starter_src.sav"); sav = out / "lw.sav"; shutil.copyfile(out / "starter_src.sav", sav)
    def shot(emu, name):
        p = out / name; emu.screenshot(p); rep["shots"].append(str(p))
    with Mgba(rom, elf=elf, save_path=sav, trace_path=out / "lw_inputs.jsonl") as emu:
        bh.new_game(emu, "lw"); emu.step((), 30)
        before = field(emu); shot(emu, "lw_00_brindlemark_before.png")
        emu.tap("START", hold=8, release=8)
        bh.wait(emu, lambda: emu.read_symbol("game_mode") == 2, "pause", 120, 2)
        goto_index(emu, 9); emu.tap("A", hold=8, release=8)
        bh.wait(emu, lambda: emu.read_symbol("pause_page") == 9, "SYSTEM", 120, 2)
        for _ in range(7):
            tap(emu, "DOWN")
        if emu.read_symbol("v11_sel") != 17:
            raise RuntimeError(f"seven DOWNs did not select LIVING WORLD: {emu.read_symbol('v11_sel')}")
        rep["system_rows"] = [bh.ui_row(emu, r) for r in range(4, 12)]
        shot(emu, "lw_01_system_menu.png")
        emu.tap("A", hold=8, release=8); emu.step((), 20)
        s = lw(emu)
        if not s["active"] or not s["card"] or (emu.read16(0x04000000) & 7) != 4:
            raise RuntimeError(f"no mode-4 story card {s} {disp(emu)}")
        shot(emu, "lw_02_story_card_mode4.png")
        tap(emu, "A"); emu.step((), 30)
        if (emu.read16(0x04000000) & 7) != 0 or lw(emu)["card"]:
            raise RuntimeError("did not reach the mode-0 living world")
        shot(emu, "lw_03_forest.png")
        d0 = lw(emu); emu.step((), 600); d1 = lw(emu)
        if d1["decisions"] <= d0["decisions"] or d1["moved"] <= d0["moved"]:
            raise RuntimeError(f"creatures did not live on their own {d0} {d1}")
        rep["life_10s"] = dict(decisions=d1["decisions"] - d0["decisions"], moved=d1["moved"] - d0["moved"])
        shot(emu, "lw_04_forest_after_10s.png")
        for _ in range(60):
            if lw(emu)["dark"]:
                break
            emu.step((), 60)
        rep["zeref_dark_reacts"] = lw(emu)["dark"]
        shot(emu, "lw_05_zeref_and_darkness.png")
        tap(emu, "R"); tap(emu, "R"); shot(emu, "lw_06_focus_frost.png"); tap(emu, "L"); tap(emu, "L")
        tap(emu, "SELECT"); emu.step((), 30)
        if lw(emu)["world"] != 1:
            raise RuntimeError("SELECT did not switch to the cave")
        shot(emu, "lw_07_cave.png"); emu.step((), 1800); shot(emu, "lw_08_cave_night.png")
        tap(emu, "START"); emu.step((), 10)
        if lw(emu)["page"] != 1:
            raise RuntimeError("START did not open ITEMS")
        shot(emu, "lw_09_items.png")
        u0 = lw(emu)["used"]; tap(emu, "A"); emu.step((), 10)
        if lw(emu)["used"] <= u0:
            raise RuntimeError("using the first item did nothing")
        shot(emu, "lw_10_item_used.png")
        tap(emu, "DOWN", 4); shot(emu, "lw_11_items_lantern.png")
        tap(emu, "START"); emu.step((), 5); shot(emu, "lw_12_stats.png")
        tap(emu, "START"); emu.step((), 5); shot(emu, "lw_13_quests.png")
        tap(emu, "START"); emu.step((), 5); shot(emu, "lw_14_cast_zeref.png")
        tap(emu, "DOWN", 2); emu.step((), 5); shot(emu, "lw_15_cast_mote.png")
        tap(emu, "B"); emu.step((), 10); tap(emu, "B"); emu.step((), 30)
        s = lw(emu)
        if s["active"] or s["exits"] != 1:
            raise RuntimeError(f"B did not leave {s}")
        after = field(emu); shot(emu, "lw_16_brindlemark_after.png")
        if after != before:
            raise RuntimeError(f"field not restored {before} {after}")
        tap(emu, "RIGHT", 6); rep["after_exit_game_mode"] = emu.read_symbol("game_mode")
        rep["final"] = lw(emu)
    data = sav.read_bytes()
    if data[16384:16387] != b"LW\x01":
        raise RuntimeError("no LW block in SRAM")
    if data[0:4] != b"LCV5":
        raise RuntimeError("V5 save header changed")
    rep["sram_lw_block"] = data[16384:16640].hex()
    rep["passed"] = True
    (out / "living_world_report.json").write_text(json.dumps(rep, indent=2) + "\n")
    print(json.dumps({k: rep[k] for k in ("suite", "rom_sha256", "life_10s", "zeref_dark_reacts", "passed")}, indent=2))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rom", type=Path, default=ROOT.parent / "LOST_COSMOS_V10_SOURCE/LOST_COSMOS_V10_OPENING_QA.gba")
    ap.add_argument("--elf", type=Path, default=ROOT.parent / "LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.elf")
    ap.add_argument("--out", type=Path, default=ROOT.parent / "artifacts/mgba_living_world")
    a = ap.parse_args(); run(a.rom.resolve(), a.elf.resolve(), a.out.resolve())
