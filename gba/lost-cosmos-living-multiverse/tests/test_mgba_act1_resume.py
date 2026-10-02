#!/usr/bin/env python3
"""REAL mGBA fresh cold boot of SRAM earned by test_mgba_act1_controller.py.
Requires an actual previous controller-input Act I playthrough on the identical
ROM, including true native boss fight and First Heart; NO fabricated save,
emulated memory writes, flags, or savestate loads.
"""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from mgba import Mgba, sha256

ROOT = Path(__file__).resolve().parents[1]

def run(rom, elf, out):
    out.mkdir(parents=True, exist_ok=True)
    save = out / "act1_fresh.sav"
    previous = out / "act1_controller_report.json"
    if not save.is_file() or not previous.is_file():
        raise RuntimeError("Missing REAL Act I controller save/receipt; no fixtures accepted")
    evidence = json.loads(previous.read_text())
    if not evidence.get("passed") or evidence["rom_sha256"] != sha256(rom):
        raise RuntimeError("Act I did not actually pass on this exact native ROM")
    if evidence["completed_stages"][-1]["stage"] != "08_real_First_Heart":
        raise RuntimeError("No actual controller-earned First Heart in prior run")
    report = {"suite":"real_mgba_act1_two_cold_boots",
              "rom_sha256":sha256(rom), "input_save_sha256":sha256(save),
              "controller_only":True, "memory_writes":False,
              "savestate_loads":False,"passed":False}
    with Mgba(rom, elf=elf, save_path=save,
              trace_path=out / "act1_second_boot_inputs.jsonl") as emu:
        emu.step((),180)
        if emu.read_symbol("intro") != 1 or emu.read_symbol("v10_has_save") != 1:
            raise RuntimeError("Actual second native cold boot does not recognize SRAM")
        emu.screenshot(out / "09_real_Act1_cold_boot.png")
        emu.tap("DOWN",hold=12,release=12)
        if emu.read_symbol("v10_title_sel") != 1:
            raise RuntimeError("CONTINUE not physically selected")
        emu.tap("A",hold=12,release=12)
        for _ in range(200):
            if emu.read_symbol("intro")==0 and emu.read_symbol("current_room")==4:
                break
            emu.step((),8)
        else:
            raise RuntimeError("Real emulator never restored saved Cragstone world")
        emu.step((),12)
        result = {"world":emu.read_symbol("current_world"),
                  "room":emu.read_symbol("current_room"),
                  "story_flags":emu.read_symbol("story_flags"),
                  "rune_progress":emu.read_symbol("rune_progress"),
                  "kill_count":emu.read_symbol("kill_count"),
                  "emulated_frame":emu.frame}
        report["restored_state"] = result
        if result["world"]!=0 or result["room"]!=4 or result["story_flags"]&31!=31:
            raise RuntimeError("Real second-boot SRAM lost a controller-earned Act I milestone")
        if result["kill_count"]<1 or result["rune_progress"]!=0:
            raise RuntimeError("Real second-boot SRAM lost boss victory or original four seals")
        emu.screenshot(out / "10_real_Act1_Heart_restored.png")
        report["passed"] = True
    (out / "act1_second_boot_report.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--rom",type=Path,default=ROOT/"LOST_COSMOS_V10_SOURCE/LOST_COSMOS_V10_OPENING_QA.gba")
    p.add_argument("--elf",type=Path,default=ROOT/"LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.elf")
    p.add_argument("--out",type=Path,default=ROOT/"artifacts/mgba_act1")
    a=p.parse_args()
    run(a.rom.resolve(), a.elf.resolve(), a.out.resolve())
