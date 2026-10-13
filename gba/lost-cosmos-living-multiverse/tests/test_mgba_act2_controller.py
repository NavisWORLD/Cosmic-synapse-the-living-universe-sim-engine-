#!/usr/bin/env python3
"""Controller-earned native V11.9 Act II journey, including two genuine cold boots.

Q10 Tide Memory -> Forgotten City; Q11 mirror Courage; Q12 ordered panels;
Q13 companion-held Arena; Q14 Chronoheart; then the original Dream/Eldoria
handoff. Never inject SRAM, story flags, native symbols, or emulator savestates.
All progress must come from mGBA key presses on the matching compiled ROM.
"""
import argparse
import json
import shutil
from pathlib import Path
import sys
import traceback

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from mgba import Mgba, sha256
from mgba_navigate import Navigator

ROOT = Path(__file__).resolve().parents[1]
CQ_DONE = 3
A2_TIDE, A2_CITY, A2_WHISPERS, A2_LIGHT = 95, 96, 97, 98
A2_ARENA, A2_SANCTUM = 99, 100
ST_ACT2 = 0x0B9F
TR_GATE = 12
TR_ECHO, TR_CITY_GATE, TR_TO_TIDE = 233, 234, 235
TR_WHISPERS, TR_LIGHT, TR_ARENA, TR_SANCTUM = 236, 237, 238, 239
TR_OLDQ, TR_CITY, TR_MIRROR, TR_PANEL = 241, 242, 243, 245
TR_LEVER, TR_CHRONO = 247, 249


def run(rom, elf, act1, out):
    out.mkdir(parents=True, exist_ok=True)
    prior = json.loads((act1 / "act1_heart_report.json").read_text())
    if (not prior["passed"] or prior["rom_sha256"] != sha256(rom) or
            prior["stages"][-1]["stage"] != "43_back_in_oakwood" or
            prior.get("cold_boot") != prior.get("final_live")):
        raise RuntimeError("Require controller-earned matching-ROM Act I and its real cold-boot evidence")

    save = out / "act2_real_controller.sav"
    shutil.copy2(act1 / "act1_complete.sav", save)
    report = {"suite": "real_mgba_v119_act2_controller_two_cold_boots",
              "rom_sha256": sha256(rom), "elf_sha256": sha256(elf),
              "source_ActI_save_sha256": sha256(act1 / "act1_complete.sav"),
              "controller_only": True, "memory_writes": False, "savestates": False,
              "stages": [], "passed": False, "cold_boot_passed": False}

    with Mgba(rom, elf=elf, save_path=save,
              trace_path=out / "act2_controller_inputs.jsonl") as emu:
        def value(name, **kwargs):
            return emu.read_symbol(name, **kwargs)

        def quest(q):
            return value("cq_state", width=1, offset=q)

        def wait(pred, label, max_frames=1200):
            for _ in range((max_frames + 3) // 4):
                if pred():
                    return
                emu.step((), 4)
            raise RuntimeError("Actual " + label + " not reached using native controller input")

        def mark(name):
            emu.screenshot(out / (name + ".png"))
            state = {"name": name, "frame": emu.frame, "world": value("current_world"),
                     "room": value("current_room"), "story_flags": value("story_flags"),
                     "a2_flags": value("a2_flags", width=2),
                     "quest": [quest(q) for q in range(10, 15)]}
            report["stages"].append(state)
            print("REAL_V119_ACT2", state, flush=True)

        def cards(name, max_cards=15):
            wait(lambda: value("pro_ui") == 4, name + " story cards")
            count = 0
            while value("pro_ui") == 4:
                emu.step((), 40)
                emu.tap("A", hold=6, release=6)
                count += 1
                if count > max_cards:
                    raise RuntimeError("Native " + name + " cards failed to advance")
            return count

        def ensure_room(room, label):
            if (value("current_world"), value("current_room")) != (0, room):
                raise RuntimeError("Actual " + label + " landed in wrong room")
            # Native warp returns the new room before deferred world-building
            # and triggered map writes are necessarily visible to the host.
            emu.step((), 30)

        try:
            emu.step((), 180)
            if value("intro") != 1 or value("v10_has_save") != 1:
                raise RuntimeError("First cold boot failed to recognize earned Act I SRAM")
            emu.tap("DOWN", hold=12, release=12)
            if value("v10_title_sel") != 1:
                raise RuntimeError("Cannot select CONTINUE")
            emu.tap("A", hold=12, release=12)
            wait(lambda: value("intro") == 0 and value("current_room") == 3,
                 "Oakwood CONTINUE")
            emu.step((), 30)
            if value("story_flags") & 31 != 31 or quest(9) != CQ_DONE:
                raise RuntimeError("Controller-earned Act I state was not retained")
            nav = Navigator(emu)
            mark("01_act1_sram_reused")

            nav.interact(TR_GATE, at=(8, 54))
            ensure_room(2, "Brindlemark")
            mark("02_brindlemark")
            nav.interact(TR_GATE, at=(52, 12))
            ensure_room(A2_TIDE, "Tide Memory")
            cards("Tide Memory opening")
            mark("03_tide_memory")

            # Read all three real tide-gated stones. Native tide changes are
            # never disabled: a flooded or unreachable bar must fail the gate.
            for number, coords in enumerate(((24, 30), (32, 26), (40, 34)), 1):
                nav.interact(TR_ECHO, at=coords)
                if value("a2_flags", width=2) & (1 << (number - 1)) == 0:
                    raise RuntimeError("Tide stone %d did not record its echo" % number)
                mark("04_tide_echo_%d" % number)
            cards("Echo gate")
            nav.interact(TR_CITY_GATE, at=(62, 32))
            ensure_room(A2_CITY, "Forgotten City")
            cards("City arrival")
            mark("05_forgotten_city")

            if not any(n.id == 18 and n.active for n in nav.npcs()):
                raise RuntimeError("Lysara is absent from the real Forgotten City")
            nav.talk_npc(18, advances=6)
            cards("Lysara sentinel")
            if quest(10) != CQ_DONE or not value("story_flags") & 2048:
                raise RuntimeError("Q10 city sentinel milestone was not earned")
            mark("06_lysara_q10_complete")

            nav.interact(TR_WHISPERS, at=(5, 32))
            ensure_room(A2_WHISPERS, "Hall of Whispers")
            nav.interact(TR_MIRROR, at=(8, 32))
            cards("Mirror encounter")
            wait(lambda: value("pro_ui") == 10, "live mirror duel")
            # The mirror copies the prior controller choice. Observe its
            # current move and choose the counter with real pad presses.
            for round_number in range(3):
                wait(lambda: value("a2_phase") == 0, "mirror next round")
                counter = {0: 1, 1: 2, 2: 0}[value("a2_last")]
                for _ in range(3):
                    if value("a2_sel") == counter:
                        break
                    emu.tap("RIGHT", hold=3, release=3)
                if value("a2_sel") != counter:
                    raise RuntimeError("Could not select live mirror counter")
                before = value("a2_wins")
                emu.tap("A", hold=3, release=3)
                if value("a2_wins") != before + 1:
                    raise RuntimeError("Real mirror duel did not award the earned round")
                mark("07_mirror_round_%d" % (round_number + 1))
            wait(lambda: value("pro_ui") == 4, "earned Courage story", 250)
            cards("Courage victory")
            if quest(11) != CQ_DONE or not value("story_flags") & 256:
                raise RuntimeError("Q11 Courage not earned via mirror duel")
            mark("08_courage_earned")

            nav.interact(TR_CITY, at=(58, 32))
            ensure_room(A2_CITY, "return from Whispers")
            nav.interact(TR_LIGHT, at=(58, 32))
            ensure_room(A2_LIGHT, "Chamber of Illumination")
            # Initial physical panel permutation 3,0,4,1,2 -> identity.
            # Each swap uses two on-map controller A interactions.
            for i, j in ((0, 1), (1, 3), (2, 4)):
                nav.interact(TR_PANEL, at=(16 + i * 8, 20))
                nav.interact(TR_PANEL, at=(16 + j * 8, 20))
            cards("Wisdom panels")
            if quest(12) != CQ_DONE or not value("story_flags") & 128:
                raise RuntimeError("Q12 Wisdom panels did not unlock")
            mark("09_wisdom_earned")

            nav.interact(TR_CITY, at=(5, 30))
            ensure_room(A2_CITY, "return from Illumination")
            nav.interact(TR_ARENA, at=(48, 6))
            ensure_room(A2_ARENA, "Arena of Souls")
            cards("Arena of Souls introduction")
            nav.interact(TR_LEVER, at=(32, 30))
            if value("a2_arena") != 1:
                raise RuntimeError("Real companion did not start Arena lever")
            # Stand adjacent to the lever facing the oncoming sentries.
            # Normal A attacks are directed at observed, naturally moving
            # sentries; no HP values, encounter flags, or save data are set.
            nav.walk_to(236, 256, tolerance=6)
            emu.step("RIGHT", 2)
            for _ in range(550):
                if value("a2_arena") != 1:
                    break
                emu.tap("A", hold=2, release=10)
                emu.step((), 2)
            if value("a2_arena") != 2:
                raise RuntimeError("Real companion could not finish Arena channel; sentry handling needed")
            cards("Unity victory")
            if quest(13) != CQ_DONE or not value("story_flags") & 512:
                raise RuntimeError("Q13 Unity was not controller-earned")
            mark("10_unity_earned")

            nav.interact(TR_CITY, at=(32, 54))
            ensure_room(A2_CITY, "return from Arena")
            nav.talk_npc(36, advances=3)
            cards("Kaelen the time weaver")
            if value("a2_flags", width=2) & 0x0200 == 0:
                raise RuntimeError("Kaelen did not grant the native Chronoheart access")
            nav.interact(TR_SANCTUM, at=(32, 6))
            ensure_room(A2_SANCTUM, "Chronoheart Sanctum")
            nav.interact(TR_CHRONO, at=(32, 14))
            cards("Chronoheart encounter")
            wait(lambda: value("pro_ui") == 11, "live Chronoheart rings")
            for ring_number in range(3):
                wait(lambda: value("a2_ring_lock") == ring_number and
                     10 <= value("a2_ring", width=1, offset=ring_number) <= 11,
                     "ring alignment %d" % ring_number, 700)
                emu.tap("A", hold=1, release=1)
                if value("a2_ring_lock") != ring_number + 1:
                    raise RuntimeError("Actual Chronoheart ring %d failed to lock" % ring_number)
            # The history callback immediately queues the Act II finale.
            cards("Chronoheart history and Act II finale")
            if quest(14) != CQ_DONE or value("a2_flags", width=2) & 0x0400 == 0:
                raise RuntimeError("Q14 Chronoheart not earned")
            mark("11_chronoheart_earned")

            nav.interact(TR_CITY, at=(32, 57))
            ensure_room(A2_CITY, "Sanctum return")
            nav.interact(TR_OLDQ, at=(10, 59))
            ensure_room(5, "Old Quarter")
            nav.interact(TR_GATE, at=(54, 10))
            wait(lambda: value("current_world") == 6, "original Dream Veil handoff")
            emu.step((), 360)
            nav.wait_cinema()
            if nav.location() != (6, 0, 1):
                raise RuntimeError("Original Dream Veil handoff is no longer playable")
            if value("story_flags") & ST_ACT2 != ST_ACT2:
                raise RuntimeError("Act II story flags missing after genuine Dream transition")
            mark("12_dream_veil_handoff")
            emu.step((), 180)
            report["passed"] = True
        except Exception as error:
            report["failure"] = repr(error)
            report["traceback"] = traceback.format_exc()
            try:
                emu.screenshot(out / "FAILED_TRUE_ACT2_FRAME.png")
            except Exception:
                pass
        finally:
            report["end_frame"] = emu.frame
            (out / "act2_controller_report.json").write_text(json.dumps(report, indent=2) + "\n")

    if not report["passed"]:
        raise RuntimeError(report["failure"])

    # A new, separate emulator instance reads the exact prior SRAM bytes.
    with Mgba(rom, elf=elf, save_path=save,
              trace_path=out / "act2_second_boot_inputs.jsonl") as emu:
        emu.step((), 180)
        if emu.read_symbol("intro") != 1 or emu.read_symbol("v10_has_save") != 1:
            raise RuntimeError("Second cold boot failed to load Act II SRAM")
        emu.screenshot(out / "13_act2_second_cold_title.png")
        emu.tap("DOWN", hold=12, release=12)
        emu.tap("A", hold=12, release=12)
        for _ in range(180):
            if emu.read_symbol("intro") == 0 and emu.read_symbol("current_world") == 6:
                break
            emu.step((), 8)
        else:
            raise RuntimeError("Actual Act II battery did not restore Dream Veil")
        emu.step((), 20)
        flags = emu.read_symbol("story_flags")
        if flags & ST_ACT2 != ST_ACT2:
            raise RuntimeError("Independent cold boot lost earned Q10-Q14 milestones")
        if emu.read_symbol("a2_flags", width=2) & 0x06F0 != 0x06F0:
            raise RuntimeError("Independent cold boot lost Lysara, trials, Kaelen or Chronoheart")
        report["second_boot"] = {
            "world": emu.read_symbol("current_world"),
            "room": emu.read_symbol("current_room"), "story_flags": flags,
            "a2_flags": emu.read_symbol("a2_flags", width=2), "frame": emu.frame}
        emu.screenshot(out / "14_act2_second_cold_dream.png")
        report["cold_boot_passed"] = True
    (out / "act2_controller_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"passed": True, "second_boot": report["second_boot"],
                      "stages": report["stages"]}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", type=Path,
                        default=ROOT / "LOST_COSMOS_V10_SOURCE/LOST_COSMOS_V10_OPENING_QA.gba")
    parser.add_argument("--elf", type=Path,
                        default=ROOT / "LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.elf")
    parser.add_argument("--act1", type=Path, default=ROOT / "artifacts/mgba_act1")
    parser.add_argument("--out", type=Path, default=ROOT / "artifacts/mgba_act2")
    args = parser.parse_args()
    run(args.rom.resolve(), args.elf.resolve(), args.act1.resolve(), args.out.resolve())
