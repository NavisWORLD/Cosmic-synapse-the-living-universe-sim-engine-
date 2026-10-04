#!/usr/bin/env python3
"""Boot the Sol cartridge past BUILDING LOCAL MAP.

Cases: no save, a blank 32 KiB SRAM image, and the Spark cage save
(Phera, traits 30/30/30, recorded run 635). The cage case must show the
imported companion and a recorded Spark Beast, then walk.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from mgba import Mgba, sha256


def wait(emu, pred, label, budget=2400):
    for _ in range((budget + 7) // 8):
        if pred():
            return
        emu.step((), 8)
    raise RuntimeError(f"Timed out waiting for {label}")


def ui_row(emu, row):
    tiles = emu.read_range(0x06000000 + 28 * 2048 + row * 64, 60)
    text = []
    for i in range(0, 60, 2):
        tile = int.from_bytes(tiles[i:i + 2], "little") & 1023
        text.append(chr(65 + tile - 64) if 64 <= tile < 90 else " ")
    return "".join(text)


def oam_size(emu, index):
    attr0 = emu.read16(0x07000000 + index * 8)
    attr1 = emu.read16(0x07000000 + index * 8 + 2)
    if attr0 & 0x0200:
        return None
    return (attr1 >> 14) & 3


def oam_visible32(emu, index):
    return oam_size(emu, index) == 2


def portrait_painted(emu):
    tiles = emu.read_range(0x06010000 + 640 * 32, 2048)
    return any(tiles)


def boot_overworld(emu, out, name):
    emu.step((), 120)
    emu.screenshot(out / f"{name}-title.png")
    if emu.read_symbol("intro") != 1:
        raise RuntimeError(f"{name}: title did not appear")
    emu.tap("A", hold=12, release=12)
    wait(emu, lambda: emu.read_symbol("v10_opening") == 1, f"{name} opening", 400)
    emu.tap("START", hold=12, release=12)

    def map_revealed():
        display = emu.read16(0x04000000)
        # BG0, BG1, BG2 and OBJ. The cover itself enables BG1 only.
        return (emu.read_symbol("v10_opening") == 0
                and emu.read_symbol("current_room") == 2
                and (display & 0x1700) == 0x1700
                and (display & 0x80) == 0)

    wait(emu, map_revealed, f"{name} map reveal")
    revealed = emu.read_symbol("frame", width=2)
    wait(emu, lambda: ((emu.read_symbol("frame", width=2) - revealed) & 0xFFFF) > 4, f"{name} live overworld")
    emu.step((), 12)
    display = emu.read16(0x04000000)
    if display & 0x80:
        raise RuntimeError(f"{name}: LCD still forced blank after map build")
    if (display & 0x0100) == 0:
        raise RuntimeError(f"{name}: overworld background is not enabled")
    row8 = ui_row(emu, 8)
    row10 = ui_row(emu, 10)
    if "TRAVERSING" in row8 or "BUILDING" in row10:
        raise RuntimeError(f"{name}: still on the map-build cover ({row8!r} / {row10!r})")
    emu.screenshot(out / f"{name}-overworld.png")


def actor_xy(emu):
    # Clang splits the static Actor into scalar symbols. player.0 is x, player.1 is y.
    return (emu.read_symbol("player.0", width=2, signed=True),
            emu.read_symbol("player.1", width=2, signed=True))


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


def open_page(emu, index, page, label):
    emu.tap("START", hold=12, release=12)
    wait(emu, lambda: emu.read_symbol("game_mode") == 2 and emu.read_symbol("pause_page") == 0, f"{label} menu")
    goto_index(emu, index)
    emu.tap("A", hold=10, release=10)
    emu.step((), 12)
    if emu.read_symbol("pause_page") != page:
        raise RuntimeError(f"{label} page did not open")


def close_page(emu):
    emu.tap("B", hold=10, release=10)
    emu.step((), 8)
    emu.tap("B", hold=10, release=10)
    emu.step((), 8)
    if emu.read_symbol("game_mode") != 0:
        raise RuntimeError("B did not return to the overworld")


def require_portrait(emu, label):
    if oam_size(emu, 42) != 3:
        raise RuntimeError(f"{label} portrait is not a 64x64 sprite")
    if not portrait_painted(emu):
        raise RuntimeError(f"{label} portrait tiles are blank")


def walk(emu, out):
    x0, y0 = actor_xy(emu)
    for key in ("RIGHT", "RIGHT", "DOWN", "LEFT", "UP", "RIGHT"):
        emu.step((key,), 36)
    x1, y1 = actor_xy(emu)
    emu.screenshot(out / "cage-walk.png")
    if (x0, y0) == (x1, y1):
        raise RuntimeError(f"Player did not move from {(x0, y0)}")
    return {"from": [x0, y0], "to": [x1, y1]}


def charlet_save(path: Path) -> dict:
    proc = subprocess.run(
        ["node", str(REPO / "scripts/make-charlet-sav.mjs"), str(path)],
        cwd=REPO, capture_output=True, text=True, check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout)
    return json.loads(proc.stdout)


def run(rom: Path, elf: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    report = {
        "suite": "sol_cage_overworld",
        "rom_sha256": sha256(rom),
        "elf_sha256": sha256(elf),
        "passed": False,
    }
    try:
        with Mgba(rom, elf=elf) as emu:
            boot_overworld(emu, out, "none")
            report["none"] = {"room": emu.read_symbol("current_room"), "frame": emu.read_symbol("frame", width=2)}
        blank = out / "blank.sav"
        blank.write_bytes(b"\xff" * 32768)
        with Mgba(rom, elf=elf, save_path=blank) as emu:
            boot_overworld(emu, out, "blank")
            report["blank"] = {"room": emu.read_symbol("current_room"), "mail_live": emu.read_symbol("lc_mail_live", width=1)}
            if emu.read_symbol("lc_mail_live", width=1) != 0:
                raise RuntimeError("Blank SRAM published a mailbox beast")
        meta = charlet_save(out / "charlet.sav")
        report["cage_meta"] = meta
        with Mgba(rom, elf=elf, save_path=out / "charlet.sav") as emu:
            boot_overworld(emu, out, "cage")
            if emu.read_symbol("lc_mail_live", width=1) != 1:
                raise RuntimeError("Cage save did not publish the companion")
            if emu.read_symbol("lc_party", width=1) < 1:
                raise RuntimeError("Cage save left the party empty")
            hud = ui_row(emu, 1)
            if meta["callsign"] not in hud:
                raise RuntimeError(f"Companion name {meta['callsign']} missing from HUD {hud!r}")
            if not oam_visible32(emu, 42):
                raise RuntimeError("Imported companion sprite is not on the field")
            if not oam_visible32(emu, 43):
                raise RuntimeError("Recorded Spark Beast sprite is not on the field")
            near = ui_row(emu, 2)
            if "RECORDED" not in near:
                raise RuntimeError(f"Recorded-seed label missing: {near!r}")
            recording = emu.start_recording(out / "spark-sprites.mp4") if shutil.which("ffmpeg") else None
            open_page(emu, 2, 18, "party")
            for _ in range(4):
                if meta["callsign"] in ui_row(emu, 5) or oam_size(emu, 42) == 3:
                    break
                emu.tap("DOWN", hold=8, release=8)
                emu.step((), 8)
            require_portrait(emu, "party")
            emu.screenshot(out / "party-portrait.png")
            close_page(emu)
            open_page(emu, 6, 20, "bestiary")
            require_portrait(emu, "bestiary")
            if meta["callsign"] not in ui_row(emu, 11):
                raise RuntimeError(f"Bestiary did not name the companion: {ui_row(emu, 11)!r}")
            emu.screenshot(out / "bestiary-portrait.png")
            close_page(emu)
            open_page(emu, 8, 26, "beast box")
            require_portrait(emu, "beast box")
            emu.screenshot(out / "beast-box-portrait.png")
            close_page(emu)
            if not oam_visible32(emu, 43):
                raise RuntimeError("Wild Spark Beast disappeared after the menus")
            report["walk"] = walk(emu, out)
            if recording:
                emu.stop_recording()
            report["hud"] = hud.strip()
            report["near"] = near.strip()
            report["portraits"] = "64x64"
        report["passed"] = True
    except Exception as exc:
        report["failure"] = repr(exc)
        report["traceback"] = traceback.format_exc()
        raise
    finally:
        (out / "cage_overworld_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rom", type=Path, default=ROOT / "LOST_COSMOS_V10_SOURCE/LOST_COSMOS_V10_OPENING_QA.gba")
    ap.add_argument("--elf", type=Path, default=ROOT / "LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.elf")
    ap.add_argument("--out", type=Path, default=ROOT / "artifacts/mgba_cage")
    args = ap.parse_args()
    run(args.rom.resolve(), args.elf.resolve(), args.out.resolve())
