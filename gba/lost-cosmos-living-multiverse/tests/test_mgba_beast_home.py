#!/usr/bin/env python3
"""V11.5 BEAST HOME on the real cartridge in mGBA, controller input only.

Two beasts come home through the existing bridge:
- "cage": the Beast Box Spark cage save (scripts/make-charlet-sav.mjs), an
  imported creature with its own 32x32 field art;
- "starter": the Lost COSMOS Sol starter (arcade/sol-beast-lab design.mjs,
  the same save the Sol nursery test uses).

For each: start the game, walk to the cottage door in Brindlemark, go in,
watch the beast move on its own, then FEED (bowl), PLAY (ball), PET (A next
to the beast) and REST (bed), checking each care stat and the bond. Then
exit, re-enter (visit count), read the plaque, cold boot the exported save
and CONTINUE: the same identity must be home with the same care record.
There are no memory writes, savestates or warps: every action is a key press.
"""
from __future__ import annotations
import argparse, json, shutil, subprocess, sys, zlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from mgba import Mgba, sha256
from mgba_navigate import Navigator

BH_ROOM = 90
TR_ENTER, TR_EXIT, TR_FOOD, TR_TOY, TR_BED, TR_PLATE = 202, 203, 204, 205, 206, 207
S_IDLE, S_WALK, S_EAT, S_PLAY, S_SLEEP, S_HAPPY = range(6)
# Where the beast goes for each care action (pixels, beast_home.h).
SPOTS = {S_EAT: (188, 210), S_PLAY: (212, 262), S_SLEEP: (296, 204)}


def wait(emu, pred, label, budget=2400, step=4):
    for _ in range((budget + step - 1) // step):
        if pred():
            return
        emu.step((), step)
    raise RuntimeError(f"Timed out waiting for {label}")


def ui_row(emu, row):
    tiles = emu.read_range(0x06000000 + 28 * 2048 + row * 64, 60)
    out = []
    for i in range(0, 60, 2):
        t = int.from_bytes(tiles[i:i + 2], "little") & 1023
        out.append(chr(65 + t - 64) if 64 <= t < 90 else (chr(48 + t - 90) if 90 <= t < 100 else " "))
    return "".join(out)


def text(emu, name, size=90):
    raw = emu.read_range(emu.symbols[name].address, size)
    return raw.split(b"\0", 1)[0].decode("ascii", "replace")


def party(emu):
    """lc_party in RAM: count, active, then 20-byte LcCreature slots at +4."""
    base = emu.symbols["lc_party"].address
    count, active = emu.read8(base), emu.read8(base + 1)
    slot = base + 4 + active * 20
    return dict(count=count, active=active, species=emu.read8(slot), stage=emu.read8(slot + 1),
                bond=emu.read8(slot + 3), identity=emu.read32(slot + 8))


def home(emu):
    cur = emu.read_symbol("bh_cur", width=1, signed=True)
    rec = None
    if cur >= 0:
        rec = dict(identity=emu.read_symbol("bh_id", width=4, offset=cur * 4),
                   full=emu.read_symbol("bh_full", width=1, offset=cur),
                   joy=emu.read_symbol("bh_joy", width=1, offset=cur),
                   rest=emu.read_symbol("bh_rest", width=1, offset=cur),
                   visits=emu.read_symbol("bh_visits", width=1, offset=cur),
                   care=emu.read_symbol("bh_care", width=2, offset=cur * 2))
    return dict(cur=cur, record=rec, x=emu.read_symbol("bh_x", width=2, signed=True),
                y=emu.read_symbol("bh_y", width=2, signed=True), state=emu.read_symbol("bh_state", width=1),
                moved=emu.read_symbol("bh_moved", width=2))


def saved_records(save: bytes):
    """Decode the LC11 page (SRAM 6400) Beast Home block and check its CRC."""
    page = save[6400:6400 + 768]
    assert page[:4] == b"LC11", "LC11 page missing"
    assert zlib.crc32(page[:764]) == int.from_bytes(page[764:768], "little"), "LC11 CRC mismatch"
    assert page[676:678] == b"H\x01", "Beast Home marker missing"
    recs = []
    for i in range(4):
        r = page[680 + i * 12:692 + i * 12]
        ident = int.from_bytes(r[0:4], "little")
        if ident:
            recs.append(dict(identity=ident, full=r[4], joy=r[5], rest=r[6], visits=r[7],
                             care=int.from_bytes(r[8:10], "little")))
    return recs


def beast_drawn(emu):
    attr0 = emu.read16(0x07000000 + 42 * 8)
    return not (attr0 & 0x0200)


def emote_drawn(emu):
    return not (emu.read16(0x07000000 + 46 * 8) & 0x0200)


def oam_xy(emu, index):
    a0 = emu.read16(0x07000000 + index * 8); a1 = emu.read16(0x07000000 + index * 8 + 2)
    return (a1 & 511, a0 & 255)


def dismiss(emu, budget=1600):
    """Close prologue story cards and dialogue with A, like a player would."""
    for _ in range(budget // 16):
        if emu.read_symbol("pro_ui") == 0 and emu.read_symbol("npc_dialogue_active") == 0:
            return
        emu.tap("A", hold=8, release=8)


def new_game(emu, label):
    emu.step((), 120)
    if emu.read_symbol("intro") != 1:
        raise RuntimeError(f"{label}: title did not appear")
    emu.tap("A", hold=12, release=12)
    wait(emu, lambda: emu.read_symbol("v10_opening") == 1, f"{label} opening", 400)
    emu.tap("START", hold=12, release=12)
    wait(emu, lambda: emu.read_symbol("v10_opening") == 0 and emu.read_symbol("current_room") == 2
         and (emu.read16(0x04000000) & 0x80) == 0, f"{label} Brindlemark")
    for _ in range(100):
        if emu.read_symbol("lc_mail_ready", width=1) == 1:
            break
        emu.step((), 4)
    emu.step((), 30)
    dismiss(emu)


def continue_game(emu, label):
    emu.step((), 180)
    if emu.read_symbol("v10_has_save") != 1:
        raise RuntimeError(f"{label}: title does not see the save")
    emu.tap("DOWN", hold=12, release=12)
    emu.tap("A", hold=12, release=12)
    wait(emu, lambda: emu.read_symbol("intro") == 0 and (emu.read16(0x04000000) & 0x0400)
         and (emu.read16(0x04000000) & 0x80) == 0, f"{label} CONTINUE")
    emu.step((), 40)


def go_home(emu, nav, shots, label):
    nav.interact(TR_ENTER, max_frames=20000)
    wait(emu, lambda: nav.location() == (0, BH_ROOM, 1), f"{label} Beast Home", 600, 1)
    if "WELCOME HOME" not in text(emu, "dialogue"):
        raise RuntimeError(f"{label}: no welcome line: {text(emu, 'dialogue')!r}")
    emu.step((), 30)
    emu.screenshot(shots / f"{label}_02_welcome_home.png")


def care(emu, nav, shots, label, trigger, state, stat, note):
    before = home(emu)
    p0 = party(emu)
    nav.interact(trigger, max_frames=8000)
    wait(emu, lambda: emu.read_symbol("bh_state", width=1) in (S_WALK, state), f"{label} {note} start", 120, 2)
    wait(emu, lambda: emu.read_symbol("bh_state", width=1) == state, f"{label} {note} arrive", 900, 1)
    arrived = home(emu)
    if (arrived["x"], arrived["y"]) != SPOTS[state]:
        raise RuntimeError(f"{label} {note}: beast is at {(arrived['x'], arrived['y'])}, not {SPOTS[state]}")
    emu.step((), 40)
    emu.screenshot(shots / f"{label}_{note}.png")
    shown = emote_drawn(emu)
    wait(emu, lambda: emu.read_symbol("bh_state", width=1) == S_IDLE, f"{label} {note} done", 1200, 4)
    emu.step((), 4)
    after = home(emu)
    p1 = party(emu)
    rec0, rec1 = before["record"], after["record"]
    if after["record"]["care"] != rec0["care"] + 1:
        raise RuntimeError(f"{label} {note}: care count {rec0['care']} -> {rec1['care']}")
    if stat and not (rec1[stat] > rec0[stat] or rec1[stat] == 100):
        raise RuntimeError(f"{label} {note}: {stat} did not rise {rec0[stat]} -> {rec1[stat]}")
    if not (p1["bond"] == min(100, p0["bond"] + 1)):
        raise RuntimeError(f"{label} {note}: bond {p0['bond']} -> {p1['bond']}")
    if not shown:
        raise RuntimeError(f"{label} {note}: no care emote on screen")
    return dict(note=note, from_xy=[before["x"], before["y"]], arrived_xy=[arrived["x"], arrived["y"]],
                walked_px=arrived["moved"] - before["moved"], stat=stat,
                before=rec0, after=rec1, bond=[p0["bond"], p1["bond"]], line=text(emu, "dialogue"))


def pet(emu, nav, shots, label):
    before = home(emu); p0 = party(emu)
    for attempt in range(6):
        h = home(emu)
        if h["state"] == S_IDLE:
            break
        emu.step((), 30)
    h = home(emu)
    nav.walk_to(h["x"] + 14, h["y"], tolerance=8, max_frames=4000)
    emu.tap("A", hold=8, release=8)
    wait(emu, lambda: emu.read_symbol("bh_state", width=1) == S_HAPPY or emu.read_symbol("bh_pet_cd", width=2) > 0,
         f"{label} pet", 60, 2)
    emu.step((), 20)
    emu.screenshot(shots / f"{label}_05_pet.png")
    after = home(emu); p1 = party(emu)
    if after["record"]["care"] != before["record"]["care"] + 1:
        raise RuntimeError(f"{label} pet: care count did not rise")
    if not (after["record"]["joy"] > before["record"]["joy"] or after["record"]["joy"] == 100):
        raise RuntimeError(f"{label} pet: joy did not rise")
    wait(emu, lambda: emu.read_symbol("bh_state", width=1) != S_HAPPY, f"{label} pet end", 400, 4)
    return dict(note="pet", before=before["record"], after=after["record"], bond=[p0["bond"], p1["bond"]],
                line=text(emu, "dialogue"))


def run_case(rom, elf, out, label, save_src, record=False):
    shots = out
    sav = out / f"{label}.sav"
    shutil.copyfile(save_src, sav)
    rep = dict(case=label)
    with Mgba(rom, elf=elf, save_path=sav, trace_path=out / f"{label}_inputs.jsonl") as emu:
        nav = Navigator(emu)
        if record:
            emu.start_recording(out / f"{label}_play.mkv")
        new_game(emu, label)
        if party(emu)["count"] < 1:
            raise RuntimeError(f"{label}: party is empty, nothing to bring home")
        nav.goto_trigger(TR_ENTER, max_frames=20000)
        emu.step((), 20)
        emu.screenshot(shots / f"{label}_01_brindlemark_door.png")
        go_home(emu, nav, shots, label)
        # The beast at home is the active party creature once the bridge import
        # has landed; it is keyed by identity from here on.
        p = party(emu)
        rep["beast"] = p
        rep["mail"] = dict(live=emu.read_symbol("lc_mail_live", width=1),
                           identity=emu.read_symbol("lc_mail_identity", width=4), name=text(emu, "lc_mail_name", 13))
        h = home(emu)
        if h["cur"] < 0 or h["record"]["identity"] != p["identity"]:
            raise RuntimeError(f"{label}: home record does not match the beast {h} {p}")
        if h["record"]["visits"] != 1:
            raise RuntimeError(f"{label}: first visit not counted {h}")
        if not beast_drawn(emu):
            raise RuntimeError(f"{label}: beast not drawn in the home")
        if "BEAST HOME" not in ui_row(emu, 1) and "BEAST HOME" not in ui_row(emu, 18):
            pass
        # It moves on its own: sample its position for ~8 s without input.
        track = []
        for _ in range(16):
            emu.step((), 30)
            hh = home(emu); track.append([hh["x"], hh["y"], hh["state"], *oam_xy(emu, 42)])
        emu.screenshot(shots / f"{label}_03_idle_wander.png")
        moved = home(emu)["moved"] - h["moved"]
        distinct = len({(t[0], t[1]) for t in track})
        if moved < 8 or distinct < 4:
            raise RuntimeError(f"{label}: beast did not move on its own (moved {moved}, {distinct} spots)")
        rep["idle"] = dict(moved_px=moved, distinct_positions=distinct, track=track)
        steps = []
        steps.append(care(emu, nav, shots, label, TR_FOOD, S_EAT, "full", "04_feed"))
        steps.append(care(emu, nav, shots, label, TR_TOY, S_PLAY, "joy", "04_play"))
        steps.append(pet(emu, nav, shots, label))
        steps.append(care(emu, nav, shots, label, TR_BED, S_SLEEP, "rest", "06_rest"))
        rep["care"] = steps
        if sum(s["walked_px"] for s in steps[:2] + steps[3:]) < 40:
            raise RuntimeError(f"{label}: the beast barely walked between care spots")
        nav.interact(TR_PLATE, max_frames=4000)
        emu.step((), 10)
        plate = text(emu, "dialogue")
        rec = home(emu)["record"]
        for key in ("FULL", "JOY", "REST", "VISITS", "CARE"):
            if key not in plate:
                raise RuntimeError(f"{label}: plaque misses {key}: {plate!r}")
        if f"CARE {rec['care']}" not in plate:
            raise RuntimeError(f"{label}: plaque does not show the care count: {plate!r}")
        emu.screenshot(shots / f"{label}_07_plaque.png")
        rep["plaque"] = plate
        # Out and back in: same record, one more visit.
        nav.interact(TR_EXIT, max_frames=4000)
        wait(emu, lambda: nav.location() == (0, 2, 1), f"{label} back to Brindlemark", 600)
        emu.step((), 20)
        emu.screenshot(shots / f"{label}_08_back_outside.png")
        go_home(emu, nav, shots, label + "_again")
        h2 = home(emu)
        if h2["record"]["identity"] != p["identity"] or h2["record"]["visits"] != 2 or h2["record"]["care"] != rec["care"]:
            raise RuntimeError(f"{label}: second visit did not keep the record {h2} {rec}")
        emu.step((), 60)
        final_party = party(emu)
        exported = emu.export_save(out / f"{label}_export.sav")
        if record:
            rep["capture"] = emu.stop_recording()
    recs = saved_records(exported.read_bytes())
    match = [r for r in recs if r["identity"] == p["identity"]]
    if len(match) != 1:
        raise RuntimeError(f"{label}: saved records do not hold the beast once: {recs}")
    rep["saved_record"] = match[0]
    # Cold boot: a new emulator with the exported save, CONTINUE from the title.
    with Mgba(rom, elf=elf, save_path=exported, trace_path=out / f"{label}_cold_inputs.jsonl") as emu:
        nav = Navigator(emu)
        if record:
            emu.start_recording(out / f"{label}_cold_boot.mkv")
        continue_game(emu, label + " cold boot")
        if nav.location() != (0, BH_ROOM, 1):
            raise RuntimeError(f"{label}: CONTINUE did not return to the Beast Home: {nav.location()}")
        q = party(emu)
        hh = home(emu)
        if q["identity"] != p["identity"] or hh["record"]["identity"] != p["identity"]:
            raise RuntimeError(f"{label}: identity changed through save/load {q} {hh}")
        for k in ("full", "joy", "rest", "visits", "care"):
            if hh["record"][k] != match[0][k]:
                raise RuntimeError(f"{label}: {k} changed through save/load {hh['record']} {match[0]}")
        if q["bond"] != final_party["bond"]:
            raise RuntimeError(f"{label}: bond changed through save/load")
        if not beast_drawn(emu):
            raise RuntimeError(f"{label}: beast not drawn after cold boot")
        m0 = hh["moved"]
        emu.step((), 360)
        if home(emu)["moved"] - m0 < 4:
            raise RuntimeError(f"{label}: beast does not move after cold boot")
        emu.screenshot(shots / f"{label}_09_cold_boot_home.png")
        rep["cold_boot"] = dict(location=list(nav.location()), party=q, record=hh["record"])
        if record:
            rep["cold_capture"] = emu.stop_recording()
    return rep


def charlet_save(path: Path) -> dict:
    proc = subprocess.run(["node", str(REPO / "scripts/make-charlet-sav.mjs"), str(path)],
                          cwd=REPO, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout)
    return json.loads(proc.stdout)


def starter_save(path: Path) -> dict:
    js = """
 import fs from 'node:fs';import{createBeast,exportSave}from'./arcade/sol-beast-lab/design.mjs';
 const a=new Uint8Array(JSON.parse(fs.readFileSync('arcade/sol-beast-lab/archive.json')).bytes);
 const b=createBeast({island:0,nonce:'CORY-SOL-001',focus:65,calm:72,spark:48},a);
 console.log(JSON.stringify({save:[...exportSave(b)],id:b.publicId,species:b.species,callsign:b.callsign}));
 """
    f = json.loads(subprocess.check_output(["node", "--input-type=module", "-e", js], cwd=REPO, text=True))
    path.write_bytes(bytes(f.pop("save")))
    return f


def run(rom, elf, out, cases, record=False):
    out.mkdir(parents=True, exist_ok=True)
    report = dict(suite="real_mgba_v11_5_beast_home", rom_sha256=sha256(rom), elf_sha256=sha256(elf),
                  controller_only=True, memory_writes=False, savestates=False, passed=False)
    if "cage" in cases:
        report["cage_meta"] = charlet_save(out / "cage_src.sav")
        report["cage"] = run_case(rom, elf, out, "cage", out / "cage_src.sav", record)
        cage = report["cage"]
        if not cage["mail"]["live"] or cage["beast"]["identity"] != cage["mail"]["identity"]:
            raise RuntimeError(f"cage: the beast at home is not the bridge import {cage['mail']} {cage['beast']}")
        if cage["mail"]["name"] != report["cage_meta"]["callsign"]:
            raise RuntimeError(f"cage: imported name {cage['mail']['name']!r} is not {report['cage_meta']['callsign']!r}")
    if "starter" in cases:
        report["starter_meta"] = starter_save(out / "starter_src.sav")
        report["starter"] = run_case(rom, elf, out, "starter", out / "starter_src.sav", record)
        if report["starter"]["beast"]["identity"] != report["starter_meta"]["id"]:
            raise RuntimeError("starter identity differs from the Sol starter")
    report["passed"] = True
    (out / "beast_home_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ("suite", "rom_sha256", "passed")}, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rom", type=Path, default=ROOT / "LOST_COSMOS_V10_SOURCE/LOST_COSMOS_V10_OPENING_QA.gba")
    ap.add_argument("--elf", type=Path, default=ROOT / "LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.elf")
    ap.add_argument("--out", type=Path, default=ROOT / "artifacts/mgba_beast_home")
    ap.add_argument("--cases", default="cage,starter")
    ap.add_argument("--record", action="store_true", help="also capture native video+audio (MKV/WAV)")
    a = ap.parse_args()
    run(a.rom.resolve(), a.elf.resolve(), a.out.resolve(), a.cases.split(","), a.record)
