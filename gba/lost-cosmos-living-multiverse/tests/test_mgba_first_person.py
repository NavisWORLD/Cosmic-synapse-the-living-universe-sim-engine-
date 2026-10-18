#!/usr/bin/env python3
"""V11.6 FIRST-PERSON / MODE-7 VIEW on the real cartridge in mGBA, controller only.

For each beast (the Beast Box cage import and the Lost COSMOS Sol starter):
open START > SYSTEM > 3D VIEW in Brindlemark, check the perspective layer
(mode 1, affine BG2 copy of the field map, sky above the horizon), walk and
turn with the D-pad, check that the beast is drawn beside the player and keeps
pace, switch EYE/CAGE cameras, tilt with L/R, then leave with SELECT and check
that the top-down game is exactly as it was: display registers, BG0 map,
collision and triggers, no affine sprites left, 4-way movement and the pause
menu. The view is opened again in the Beast Home and left with START.

The same run checks the V11.6 fixes: the G5 book star in Brindlemark is a
road-backed star (no black square), the SYSTEM page says the current version, and COSMOS
chatter no longer replaces Beast Home care lines.
No memory writes, savestates or warps: every action is a key press.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "tools"))
sys.path.insert(0, str(ROOT))
from mgba import Mgba, sha256
from mgba_navigate import Navigator
import test_mgba_beast_home as bh
from test_mgba_menu_visual import goto_index

MODE_SURFACE, MODE_PAUSE = 0, 2
FP_BG2CNT = 1 | (2 << 2) | (29 << 8) | (2 << 14)
PHI_MIN, PHI_MAX, PHI_CAGE, PHI_EYE, PHI_STEP, TURN = 228, 958, 685, 913, 91, 18
STAR_TILE, TR_G5_BOOK_HOME = 270, 61


def fp(emu):
    r = emu.read_symbol
    return dict(active=r("fp_active", width=1), cam=r("fp_cam", width=1), heading=r("fp_heading", width=2),
                phi=[r("fp_phi", width=2, offset=0, signed=True), r("fp_phi", width=2, offset=2, signed=True)],
                unique=r("fp_unique", width=2), overflow=r("fp_overflow", width=2),
                horizon=r("fp_horizon", width=2, signed=True), walked=r("fp_walked", width=2), turned=r("fp_turned", width=2),
                beast_screen=[r("fp_beast_sx", width=2, signed=True), r("fp_beast_sy", width=2, signed=True)],
                beast_scale=r("fp_beast_scale", width=2, signed=True),
                beast_world=[r("fp_beast_x", width=4, signed=True) >> 8, r("fp_beast_y", width=4, signed=True) >> 8],
                entries=r("fp_entries", width=2), exits=r("fp_exits", width=2))


def display(emu):
    return dict(dispcnt=emu.read16(0x04000000), bg0cnt=emu.read16(0x04000008),
                bg1cnt=emu.read16(0x0400000A), bg2cnt=emu.read16(0x0400000C))


def digest(data):
    return hashlib.sha256(bytes(data)).hexdigest()


def field_state(emu, nav):
    return dict(display=display(emu), bg0_map=digest(emu.read_range(0x06000000 + 24 * 2048, 8192)),
                collision=digest(nav.board()), triggers=digest(nav.triggers()))


def affine_sprites(emu, count=128):
    out = []
    for i in range(count):
        a0 = emu.read16(0x07000000 + i * 8)
        if a0 & 0x0100:
            a1 = emu.read16(0x07000000 + i * 8 + 2); a2 = emu.read16(0x07000000 + i * 8 + 4)
            out.append(dict(oam=i, tile=a2 & 1023, pal=a2 >> 12, x=a1 & 511, y=a0 & 255))
    return out


def pixel(rgb, x, y):
    i = (y * 240 + x) * 3
    return rgb[i], rgb[i + 1], rgb[i + 2]


def open_3d(emu, label, via_first_person=False):
    emu.tap("START", hold=8, release=8)
    bh.wait(emu, lambda: emu.read_symbol("game_mode") == MODE_PAUSE, f"{label} pause", 120, 2)
    goto_index(emu, 9)
    if emu.read_symbol("pause_sel") != 9:
        raise RuntimeError(f"{label}: pause menu did not select SYSTEM")
    emu.tap("A", hold=8, release=8)
    bh.wait(emu, lambda: emu.read_symbol("pause_page") == 9, f"{label} SYSTEM page", 120, 2)
    # V11.10: FIRST PERSON (action 16) is on the first SYSTEM page (row 7 of 7, after BEAST BOX).
    first = [bh.ui_row(emu, r) for r in range(4, 11)]
    if not any("FIRST PERSON" in r and "ENTER" in r for r in first):
        raise RuntimeError(f"{label}: FIRST PERSON is not on the first SYSTEM page: {first}")
    if via_first_person:
        for _ in range(6):
            emu.tap("DOWN", hold=8, release=8); emu.step((), 4)
        if emu.read_symbol("v11_sel") != 16:
            raise RuntimeError(f"{label}: six DOWNs from AUDIO did not select FIRST PERSON")
        return [bh.ui_row(emu, r) for r in range(4, 18)]
    # SYSTEM has 17 rows since V11.10 (UP from AUDIO still wraps to CALL BEAST, LEASH, 3D VIEW); 3D VIEW is action 13.
    for _ in range(3):
        emu.tap("UP", hold=8, release=8); emu.step((), 4)
    if emu.read_symbol("v11_sel") != 13:
        raise RuntimeError(f"{label}: SYSTEM did not reach 3D VIEW")
    rows = [bh.ui_row(emu, r) for r in range(4, 18)]
    if not any("3D VIEW" in r and "ENTER" in r for r in rows):
        raise RuntimeError(f"{label}: no 3D VIEW row: {rows}")
    if not any("V12" in r and "0  OLDER SAVES LOAD" in r for r in rows):
        raise RuntimeError(f"{label}: SYSTEM page does not say V12.0: {rows}")
    return rows


def leash_on(emu, label):
    """V11.8: LEASH OFF (roaming) is the default. This suite checks the V11.6
    follower in the 3D view, so it turns the leash ON with the controller
    (PAUSE > SYSTEM > LEASH). tests/test_mgba_leash.py covers LEASH OFF."""
    emu.tap("START", hold=8, release=8)
    bh.wait(emu, lambda: emu.read_symbol("game_mode") == MODE_PAUSE, f"{label} pause", 120, 2)
    goto_index(emu, 9); emu.tap("A", hold=8, release=8)
    bh.wait(emu, lambda: emu.read_symbol("pause_page") == 9, f"{label} SYSTEM page", 120, 2)
    for _ in range(18):
        if emu.read_symbol("v11_sel") == 14:
            break
        emu.tap("UP", hold=8, release=8); emu.step((), 4)
    if emu.read_symbol("v11_sel") != 14:
        raise RuntimeError(f"{label}: SYSTEM did not reach LEASH")
    emu.tap("A", hold=10, release=10); emu.step((), 8)
    for _ in range(6):
        if emu.read_symbol("game_mode") == 0:
            break
        emu.tap("B", hold=10, release=10); emu.step((), 8)
    if emu.read_symbol("leash_on") != 1 or emu.read_symbol("game_mode") != 0:
        raise RuntimeError(f"{label}: LEASH ON did not take")
    emu.step((), 30)


def confirm_3d(emu, label):
    emu.tap("A", hold=8, release=8)
    bh.wait(emu, lambda: emu.read_symbol("fp_active", width=1) == 1, f"{label} 3D view", 60, 1)
    emu.step((), 6)
    d = display(emu); s = fp(emu)
    if d["dispcnt"] & 7 != 1 or not d["dispcnt"] & 0x0400 or d["dispcnt"] & 0x0100:
        raise RuntimeError(f"{label}: not the mode-1 perspective layer {d}")
    if d["bg2cnt"] != FP_BG2CNT:
        raise RuntimeError(f"{label}: BG2 is not the affine 64x64 map {d}")
    if not 1 <= s["unique"] <= 255:
        raise RuntimeError(f"{label}: affine tile set is empty {s}")
    if emu.read_symbol("game_mode") != MODE_SURFACE:
        raise RuntimeError(f"{label}: menu did not close")
    return d, s


def walk(emu, nav, frames, keys, samples, board):
    x0, y0 = nav.position()
    for _ in range(frames // 3):
        emu.step(keys, 3)
        s = fp(emu); x, y = nav.position()
        if not Navigator.can_stand(board, x, y, avoid_hazards=False):
            raise RuntimeError(f"3D walk entered a wall at {(x, y)}")
        samples.append(dict(x=x, y=y, heading=s["heading"], beast_screen=s["beast_screen"],
                            beast_world=s["beast_world"], scale=s["beast_scale"]))
    x1, y1 = nav.position()
    return x1 - x0, y1 - y0


def forward_ok(dx, dy, heading):
    import math
    a = heading * 2 * math.pi / 4096
    fx, fy = math.sin(a), -math.cos(a)
    d = math.hypot(dx, dy)
    return d >= 30 and (dx * fx + dy * fy) >= 0.8 * d


def run_case(rom, elf, out, label, save_src, record=False):
    sav = out / f"{label}.sav"
    shutil.copyfile(save_src, sav)
    rep = dict(case=label)
    with Mgba(rom, elf=elf, save_path=sav, trace_path=out / f"{label}_inputs.jsonl") as emu:
        nav = Navigator(emu)
        if record:
            emu.start_recording(out / f"{label}_3d.mkv")
        bh.new_game(emu, label)
        p = bh.party(emu)
        if p["count"] < 1:
            raise RuntimeError(f"{label}: no beast in the party")
        rep["beast"] = p
        leash_on(emu, label)
        # G5 book star in Brindlemark: road-backed star tile, trigger kept.
        sb = 24 + (31 >= 32) + ((40 >= 32) << 1)
        entry = emu.read16(0x06000000 + sb * 2048 + ((40 & 31) * 32 + (31 & 31)) * 2)
        trig = nav.triggers()[40 * 64 + 31]
        tile_bytes = emu.read_range(0x06000000 + STAR_TILE * 32, 32)
        holes = sum(1 for b in tile_bytes for n in (b & 15, b >> 4) if n == 0)
        if entry & 1023 != STAR_TILE or entry >> 12 != 1 or trig != TR_G5_BOOK_HOME or holes:
            raise RuntimeError(f"{label}: G5 star is not the road star: entry={entry:#x} trig={trig} holes={holes}")
        rep["star"] = dict(map_entry=entry, tile=entry & 1023, palette=entry >> 12, trigger=trig, backdrop_pixels=holes)
        before = field_state(emu, nav)
        top_beast_tile = emu.read16(0x07000000 + 42 * 8 + 4) & 1023
        emu.screenshot(out / f"{label}_01_topdown.png")
        rep["menu_rows"] = open_3d(emu, label)
        emu.screenshot(out / f"{label}_02_system_3d_view.png")
        d, s = confirm_3d(emu, label)
        rep["entered"] = dict(display=d, state=s)
        emu.step((), 20)
        emu.screenshot(out / f"{label}_03_eye_view.png")
        rgb = emu.rgb(); s = fp(emu)
        sky = pixel(rgb, 120, max(10, s["horizon"] // 2)); floor = pixel(rgb, 60, 150)
        if not (s["horizon"] > 12 and sky[2] > sky[0] and sky[2] > 60):
            raise RuntimeError(f"{label}: no sky above the horizon {s['horizon']} {sky}")
        if floor == sky:
            raise RuntimeError(f"{label}: floor looks like sky {floor}")
        # Every frame, not just one: the perspective must hold while the game
        # loop runs (a late frame must not drop the HBlank tables).
        game0, emu0, bad = emu.read_symbol("frame", width=2), emu.frame, []
        for i in range(120):
            emu.step((), 1)
            rgb = emu.rgb()
            if pixel(rgb, 120, max(10, s["horizon"] // 2)) != sky or pixel(rgb, 60, 150) == sky:
                bad.append(i)
        if bad:
            raise RuntimeError(f"{label}: perspective dropped on {len(bad)} of 120 frames {bad[:10]}")
        rep["pixels"] = dict(horizon=s["horizon"], sky=sky, floor=floor, stable_frames=120,
                             game_frames=(emu.read_symbol("frame", width=2) - game0) & 0xFFFF, emulator_frames=emu.frame - emu0)
        aff = affine_sprites(emu, 16)
        if not any(abs(a["tile"] - top_beast_tile) <= 4 for a in aff):
            raise RuntimeError(f"{label}: beast is not drawn as a scaled sprite {aff} (top-down tile {top_beast_tile})")
        board = nav.board()
        samples = []
        # Walk forward; if something blocks the way, turn a quarter and retry.
        moves = []
        for attempt in range(4):
            h = fp(emu)["heading"]
            dx, dy = walk(emu, nav, 60, ("UP",), samples, board)
            moves.append(dict(heading=h, dx=dx, dy=dy))
            if forward_ok(dx, dy, h):
                break
            walk(emu, nav, 57, ("RIGHT",), samples, board)
        else:
            raise RuntimeError(f"{label}: could not walk forward in the 3D view {moves}")
        emu.screenshot(out / f"{label}_04_walk.png")
        turn0 = fp(emu)
        h0, t0 = turn0["heading"], turn0["turned"]
        walk(emu, nav, 39, ("RIGHT",), samples, board)
        turn1 = fp(emu)
        h1, steps = turn1["heading"], (turn1["turned"] - t0) & 0xFFFF
        # One FP_TURN step per game frame while RIGHT is held, no drift.
        if steps < 10 or (h1 - h0) % 4096 != (steps * TURN) % 4096:
            raise RuntimeError(f"{label}: turning right moved heading {h0}->{h1} over {steps} steps")
        emu.screenshot(out / f"{label}_05_turn.png")
        for attempt in range(4):
            h = fp(emu)["heading"]
            dx, dy = walk(emu, nav, 60, ("UP",), samples, board)
            moves.append(dict(heading=h, dx=dx, dy=dy))
            if forward_ok(dx, dy, h):
                break
            walk(emu, nav, 57, ("LEFT",), samples, board)
        else:
            raise RuntimeError(f"{label}: could not walk after turning {moves}")
        seen = sum(1 for q in samples if 0 <= q["beast_screen"][0] < 240 and 8 <= q["beast_screen"][1] < 160)
        near = sum(1 for q in samples if abs(q["beast_world"][0] - q["x"]) + abs(q["beast_world"][1] - q["y"]) <= 64)
        if seen < 0.8 * len(samples) or near < 0.95 * len(samples):
            raise RuntimeError(f"{label}: beast not beside the player ({seen}/{len(samples)} on screen, {near} near)")
        rep["walk"] = dict(moves=moves, samples=len(samples), beast_on_screen=seen, beast_within_64px=near,
                           walked_px=fp(emu)["walked"])
        # CAGE camera: the Beast Cage orbit; the hero is drawn too.
        emu.tap("A", hold=8, release=8); emu.step((), 10)
        if fp(emu)["cam"] != 1:
            raise RuntimeError(f"{label}: A did not switch to the cage camera")
        aff = affine_sprites(emu, 16)
        if not any(576 <= a["tile"] < 640 for a in aff):
            raise RuntimeError(f"{label}: hero not drawn in the cage camera {aff}")
        walk(emu, nav, 30, ("UP",), samples, board)
        emu.screenshot(out / f"{label}_06_cage_view.png")
        for _ in range(8):
            emu.tap("L", hold=4, release=4)
        lo = fp(emu)["phi"][1]
        for _ in range(3):
            emu.tap("R", hold=4, release=4)
        hi = fp(emu)["phi"][1]
        if lo != PHI_MIN or hi != PHI_MIN + 3 * PHI_STEP:
            raise RuntimeError(f"{label}: tilt is not the cage clamp {lo} {hi}")
        emu.step((), 4)
        emu.screenshot(out / f"{label}_07_cage_tilt.png")
        rep["cage"] = dict(phi_after_8_L=lo, phi_after_3_R=hi, hero_sprite=True)
        emu.tap("A", hold=8, release=8)
        # Leave with SELECT: the top-down game is exactly as it was.
        emu.tap("SELECT", hold=8, release=8); emu.step((), 4)
        after = field_state(emu, nav)
        if fp(emu)["active"] or after != before:
            raise RuntimeError(f"{label}: top-down not restored {before} {after}")
        if affine_sprites(emu):
            raise RuntimeError(f"{label}: affine sprites left after leaving")
        if emu.read_symbol("game_mode") != MODE_SURFACE:
            raise RuntimeError(f"{label}: SELECT did not return to the field")
        emu.step((), 20)
        emu.screenshot(out / f"{label}_08_back_topdown.png")
        moved = None
        for key in ("LEFT", "UP", "RIGHT", "DOWN"):
            x0, y0 = nav.position(); emu.step((key,), 16); emu.step((), 2); x1, y1 = nav.position()
            if (x1, y1) != (x0, y0):
                moved = dict(key=key, dx=x1 - x0, dy=y1 - y0)
                if (key in ("LEFT", "RIGHT") and y1 != y0) or (key in ("UP", "DOWN") and x1 != x0):
                    raise RuntimeError(f"{label}: top-down movement is not 4-way any more {moved}")
                break
        if not moved:
            raise RuntimeError(f"{label}: cannot walk in the top-down view after leaving")
        emu.tap("START", hold=8, release=8)
        if emu.read_symbol("game_mode") != MODE_PAUSE:
            raise RuntimeError(f"{label}: pause menu does not open after leaving")
        emu.tap("B", hold=8, release=8); emu.step((), 4)
        if emu.read_symbol("game_mode") != MODE_SURFACE:
            raise RuntimeError(f"{label}: pause menu does not close")
        rep["restored"] = dict(state=after, topdown_move=moved, pause_ok=True)
        # Beast Home: open the view inside, leave with START (no pause menu).
        nav.goto_trigger(bh.TR_ENTER, max_frames=20000)
        bh.go_home(emu, nav, out, label)
        name = bh.text(emu, "dialogue").split("WELCOME HOME. ", 1)[1].split(" PERKS UP", 1)[0]
        home_before = field_state(emu, nav)
        open_3d(emu, label + " home", via_first_person=True)
        confirm_3d(emu, label + " home")
        emu.step((), 30)
        if not any(abs(a["tile"] - top_beast_tile) <= 4 for a in affine_sprites(emu, 16)):
            raise RuntimeError(f"{label}: beast not drawn in the home 3D view")
        emu.screenshot(out / f"{label}_09_home_3d.png")
        for _ in range(4):
            emu.step(("UP",), 15)
        emu.screenshot(out / f"{label}_10_home_3d_walk.png")
        emu.tap("START", hold=8, release=8); emu.step((), 4)
        if fp(emu)["active"] or emu.read_symbol("game_mode") != MODE_SURFACE:
            raise RuntimeError(f"{label}: START did not leave the 3D view cleanly")
        if field_state(emu, nav) != home_before:
            raise RuntimeError(f"{label}: Beast Home not restored")
        m0 = bh.home(emu)["moved"]
        emu.step((), 240)
        if bh.home(emu)["moved"] - m0 < 4 or not bh.beast_drawn(emu):
            raise RuntimeError(f"{label}: the home beast does not move after leaving 3D")
        emu.screenshot(out / f"{label}_11_home_topdown.png")
        # Care lines stay on screen: no COSMOS chatter in the Beast Home.
        nav.interact(bh.TR_FOOD, max_frames=8000)
        lines = []
        for _ in range(300):
            emu.step((), 2)
            line = bh.text(emu, "dialogue")
            if not lines or lines[-1][1] != line:
                lines.append([emu.frame, line])
            if "LICKS THE BOWL CLEAN" in line:
                break  # the care moment is over; later lines may be anything
        foreign = [l for l in lines if name not in l[1]]
        if not lines or "YOU FILL THE BOWL" not in lines[0][1] or foreign or not any("LICKS THE BOWL CLEAN" in l[1] for l in lines):
            raise RuntimeError(f"{label}: care line replaced {lines}")
        rep["care_lines"] = lines
        rep["fp_final"] = fp(emu)
        if rep["fp_final"]["entries"] != 2 or rep["fp_final"]["exits"] != 2:
            raise RuntimeError(f"{label}: entry/exit count {rep['fp_final']}")
        exported = emu.export_save(out / f"{label}_export.sav")
        if record:
            rep["capture"] = emu.stop_recording()
    recs = bh.saved_records(exported.read_bytes())
    if not any(r["identity"] == p["identity"] for r in recs):
        raise RuntimeError(f"{label}: Beast Home record missing from the save {recs}")
    rep["saved_records"] = recs
    return rep


def run(rom, elf, out, cases, record=False):
    out.mkdir(parents=True, exist_ok=True)
    report = dict(suite="real_mgba_v11_6_first_person", rom_sha256=sha256(rom), elf_sha256=sha256(elf),
                  controller_only=True, memory_writes=False, savestates=False, passed=False)
    if "cage" in cases:
        report["cage_meta"] = bh.charlet_save(out / "cage_src.sav")
        report["cage"] = run_case(rom, elf, out, "cage", out / "cage_src.sav", record)
    if "starter" in cases:
        report["starter_meta"] = bh.starter_save(out / "starter_src.sav")
        report["starter"] = run_case(rom, elf, out, "starter", out / "starter_src.sav", record)
        if report["starter"]["beast"]["identity"] != report["starter_meta"]["id"]:
            raise RuntimeError("starter identity differs from the Sol starter")
    report["passed"] = True
    (out / "first_person_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ("suite", "rom_sha256", "passed")}, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rom", type=Path, default=ROOT.parent / "LOST_COSMOS_V10_SOURCE/LOST_COSMOS_V10_OPENING_QA.gba")
    ap.add_argument("--elf", type=Path, default=ROOT.parent / "LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.elf")
    ap.add_argument("--out", type=Path, default=ROOT.parent / "artifacts/mgba_first_person")
    ap.add_argument("--cases", default="cage,starter")
    ap.add_argument("--record", action="store_true", help="also capture native video+audio (MKV/WAV)")
    a = ap.parse_args()
    run(a.rom.resolve(), a.elf.resolve(), a.out.resolve(), a.cases.split(","), a.record)
