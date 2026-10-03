#!/usr/bin/env python3
"""Genuine controller-only native mGBA boot, capture, movement and two-boot QA.

This is a smoke check, not a complete campaign/three-ending certification.
Every gameplay change originates from addKeys/clearKeys controller events.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import struct
import subprocess
import sys
import wave

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from mgba import Mgba, sha256


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def position(emu):
    # Clang -Os can split a static Actor into independently named globals.
    # Resolve the actual rebuilt ELF symbols, not assumed baseline addresses.
    if "player" not in emu.symbols:
        return (emu.read_symbol("player.0", signed=True),
                emu.read_symbol("player.1", signed=True))
    return (emu.read_symbol("player", width=2, signed=True),
            emu.read_symbol("player", width=2, offset=2, signed=True))


def scalar_state(emu):
    names = ("current_world", "current_room", "current_layer", "game_mode", "intro",
             "v10_opening", "keys_found", "ending", "postgame", "kill_count", "player_level")
    return {name: emu.read_symbol(name) for name in names}


def wait(emu, predicate, label, budget=900):
    for _ in range((budget + 7) // 8):
        if predicate():
            return
        emu.step((), 8)
    raise AssertionError(f"Timed out waiting for {label}; state={scalar_state(emu)}")


def verify_png(path):
    raw = path.read_bytes()
    require(raw[:8] == b"\x89PNG\r\n\x1a\n", "Native screenshot is not a PNG")
    require(struct.unpack_from(">II", raw, 16) == (240, 160), "Screenshot must preserve native 240x160 dimensions")


def boot_diagnostics(emu, output, label):
    registers = {}
    for name in ("pc", "sp", "cpsr", "r0", "r1", "r2", "r3", "r14", "r15"):
        try:
            registers[name] = f"0x{emu.read_register(name):08X}"
        except OSError as exc:
            registers[name] = str(exc)
    state = scalar_state(emu)
    state.update({"frame": emu.read_symbol("frame"), "v10_has_save": emu.read_symbol("v10_has_save"),
                  "position": position(emu)})
    report = {"label": label, "metadata": emu.metadata, "emulator_frame": emu.frame,
              "state": state, "cpu_registers": registers,
              "gba_io": {"DISPCNT": emu.read16(0x04000000), "VCOUNT": emu.read16(0x04000006),
                         "KEYINPUT": emu.read16(0x04000130)},
              "cartridge_words": {f"0x{address:08X}": f"0x{emu.read32(address):08X}"
                                  for address in (0x08000000, 0x080000C0, 0x080000C4, 0x080000C8)},
              "timing": emu.timing_report()}
    (output / f"{label}.diagnostics.json").write_text(json.dumps(report, indent=2) + "\n")
    emu.screenshot(output / f"{label}.diagnostics.png")
    return report


def verify_video(path, expected_frames):
    data = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-count_frames", "-show_streams", "-of", "json", str(path)
    ], text=True))
    video = next(s for s in data["streams"] if s["codec_type"] == "video")
    audio = next(s for s in data["streams"] if s["codec_type"] == "audio")
    require((video["width"], video["height"]) == (240, 160), "Video is not native resolution")
    require(int(video["nb_read_frames"]) == expected_frames, "Video dropped or duplicated native frames")
    require(int(audio["sample_rate"]) == 32768 and audio["channels"] == 2, "Native stereo audio missing")
    return data


def run(rom, elf, output):
    output.mkdir(parents=True, exist_ok=True)
    save = output / "controller_two_boot.sav"
    # A previous result is not an authorized seed for the fresh-boot test.
    if save.exists():
        save.unlink()
    report = {"suite": "genuine_mgba_controller_smoke", "rom_sha256": sha256(rom),
              "elf_sha256": sha256(elf), "claims": ["native boot", "controller movement", "native video/audio", "two cold boots"],
              "full_campaign": False, "three_endings": False, "memory_writes": False, "savestate_loads": False}
    with Mgba(rom, elf=elf, save_path=save, trace_path=output / "boot1.inputs.jsonl",
              watch_symbol="frame") as emu:
        emu.start_recording(output / "boot1_native.mkv")
        emu.step((), 180)
        report["boot1_diagnostics"] = boot_diagnostics(emu, output, "boot1_title")
        emu.screenshot(output / "01_title_native.png")
        require(emu.read_symbol("intro") == 1, "Fresh ROM did not show the real title menu")
        require(emu.read_symbol("v10_has_save") == 0, "Fresh boot unexpectedly found a save")
        require(len(set(emu.rgb()[i:i + 3] for i in range(0, 240 * 160 * 3, 3))) >= 8,
                "Native boot video appears blank")
        emu.tap("A", hold=12, release=12)
        wait(emu, lambda: emu.read_symbol("v10_opening") == 1, "New Game opening")
        emu.step((), 60)
        emu.screenshot(output / "02_opening_native.png")
        # Traverse the authored opening using its real A NEXT control.
        opening_steps = []
        for _ in range(40):
            if not emu.read_symbol("v10_opening"):
                break
            opening_steps.append(emu.read_symbol("v10_opening_step"))
            emu.tap("A", hold=12, release=12)
            emu.step((), 12)
        wait(emu, lambda: emu.read_symbol("v10_opening") == 0, "opening completion")
        require(emu.read_symbol("intro") == 0 and emu.read_symbol("game_mode") == 0,
                "Opening did not lead to actual playable surface")
        require(emu.read_symbol("current_world") == 0 and emu.read_symbol("current_room") == 2,
                "New Game did not start in Brindlemark")
        emu.step((), 16)
        require(len(set(emu.rgb()[i:i + 3] for i in range(0, 240 * 160 * 3, 3))) >= 8,
                "Playable Brindlemark framebuffer remained blank after transition")
        emu.screenshot(output / "03_brindlemark_native.png")
        original = position(emu)
        movement = []
        for key in ("RIGHT", "DOWN", "LEFT", "UP"):
            emu.step(key, 24)
            emu.step((), 12)
            movement.append({"key": key, "position": position(emu)})
            if sum(abs(a - b) for a, b in zip(position(emu), original)) >= 8:
                break
        moved = position(emu)
        require(sum(abs(a - b) for a, b in zip(moved, original)) >= 8,
                "Actual controller direction inputs did not move the actor")
        emu.screenshot(output / "04_exploration_native.png")
        # Save through the actual V11.1 player menu: SYSTEM is the right-column
        # fifth entry, then SAVE GAME is the fifth SYSTEM option.
        emu.tap("START", hold=12, release=12)
        wait(emu, lambda: emu.read_symbol("game_mode") == 2, "pause menu")
        emu.tap("RIGHT", hold=10, release=10)
        for _ in range(4):
            emu.tap("DOWN", hold=10, release=10)
        require(emu.read_symbol("pause_sel") == 9, "Real menu did not select SYSTEM")
        emu.tap("A", hold=12, release=12)
        require(emu.read_symbol("pause_page") == 9, "SYSTEM page did not open")
        for _ in range(4):
            emu.tap("DOWN", hold=10, release=10)
        require(emu.read_symbol("setting_sel") == 4, "Real SYSTEM page did not select SAVE GAME")
        save_started_frame = emu.frame
        emu.tap("A", hold=12, release=12)
        # The native two-bank CRC journal is synchronous and can take more than
        # the 24 emulated frames covered by tap(). Wait for the actual save UI,
        # not a guessed clock delay; fail if the transaction never finishes.
        wait(emu, lambda: emu.read_symbol("pause_page") == 10,
             "real dual-bank SAVE journal completion", budget=600)
        report["save_transaction_emulated_frames"] = emu.frame - save_started_frame
        emu.screenshot(output / "05_save_menu_native.png")
        emu.tap("B", hold=12, release=12)
        emu.tap("B", hold=12, release=12)
        wait(emu, lambda: emu.read_symbol("game_mode") == 0, "return from menu")
        first_state = scalar_state(emu)
        report["boot1"] = {"state": first_state, "position": moved, "initial_position": original,
                           "movement": movement, "opening_steps": opening_steps,
                           "timing": emu.timing_report(), "capture": emu.stop_recording()}
    require(save.read_bytes()[:4] == b"LCV5", "Real game did not write its legacy battery save")
    report["battery_save"] = {"path": str(save), "bytes": save.stat().st_size, "sha256_after_boot1": sha256(save)}
    with Mgba(rom, elf=elf, save_path=save, trace_path=output / "boot2.inputs.jsonl",
              watch_symbol="frame") as emu:
        emu.start_recording(output / "boot2_native.mkv")
        emu.step((), 180)
        report["boot2_diagnostics"] = boot_diagnostics(emu, output, "boot2_title")
        require(emu.read_symbol("intro") == 1 and emu.read_symbol("v10_has_save") == 1,
                "Second cold boot did not detect real battery SRAM")
        emu.screenshot(output / "06_second_boot_native.png")
        emu.tap("DOWN", hold=12, release=12)
        require(emu.read_symbol("v10_title_sel") == 1, "Second title did not select CONTINUE")
        emu.tap("A", hold=12, release=12)
        wait(emu, lambda: emu.read_symbol("intro") == 0, "Continue")
        restored = position(emu)
        second_state = scalar_state(emu)
        require(restored == moved, f"Continue failed to restore controller-earned position: {restored} != {moved}")
        for name in ("current_world", "current_room", "current_layer", "keys_found", "ending", "postgame", "kill_count", "player_level"):
            require(second_state[name] == first_state[name], f"Continue did not restore {name}")
        emu.step((), 16)
        require(len(set(emu.rgb()[i:i + 3] for i in range(0, 240 * 160 * 3, 3))) >= 8,
                "CONTINUE restored state but left a blank framebuffer")
        emu.screenshot(output / "07_continue_native.png")
        emu.step((), 104)
        report["boot2"] = {"state": second_state, "restored_position": restored,
                           "timing": emu.timing_report(), "capture": emu.stop_recording()}
    for png in output.glob("*_native.png"):
        verify_png(png)
    for boot in ("boot1", "boot2"):
        capture = report[boot]["capture"]
        require(capture["audio_nonzero_samples"] > 0 and capture["audio_peak_s16"] > 0,
                f"{boot} emitted only silent audio")
        require(abs(capture["audio_minus_video_seconds"]) < 1 / float(emu.frame_rate),
                f"{boot} native audio and video are out of alignment")
        report[boot]["ffprobe"] = verify_video(Path(capture["path"]), capture["captured_frames"])
        with wave.open(capture["audio_path"], "rb") as audio:
            require(audio.getnframes() == capture["audio_samples_per_channel"], "WAV discarded native audio samples")
    report["passed"] = True
    (output / "mgba_controller_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", type=Path, default=ROOT / "LOST_COSMOS_V10_SOURCE/LOST_COSMOS_V10_OPENING_QA.gba")
    parser.add_argument("--elf", type=Path, default=ROOT / "LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.elf")
    parser.add_argument("--out", type=Path, default=ROOT / "artifacts/mgba_controller")
    args = parser.parse_args()
    run(args.rom.resolve(), args.elf.resolve(), args.out.resolve())


if __name__ == "__main__":
    main()
