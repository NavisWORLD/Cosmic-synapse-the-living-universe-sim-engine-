"""Real GBA emulation, controller input, native capture, and read-only diagnosis.

No emulator memory-writing or savestate-loading operation is exposed. The ROM
executes unchanged inside libmGBA. See docs/MGBA_CONTROLLER_QA.md.
"""
from __future__ import annotations

import argparse
import csv
import ctypes as C
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import time
import wave
import zlib

KEYS = {name: 1 << bit for bit, name in enumerate(
    ("A", "B", "SELECT", "START", "RIGHT", "LEFT", "UP", "DOWN", "R", "L"))}


def key_mask(keys=()) -> int:
    """Accept an integer mask, one key, 'A+RIGHT', or an iterable of names."""
    if isinstance(keys, int):
        if not 0 <= keys <= 1023:
            raise ValueError("GBA key mask must be in [0, 1023]")
        return keys
    if isinstance(keys, str):
        keys = keys.replace(",", "+").split("+") if keys else ()
    result = 0
    for key in keys:
        try:
            result |= KEYS[key.strip().upper()]
        except KeyError as exc:
            raise ValueError(f"Unknown GBA key: {key!r}") from exc
    return result


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True)
class Symbol:
    address: int
    size: int
    kind: int


class ElfSymbols(dict):
    """Read ELF32 little-endian ARM symbols without loading ELF into mGBA."""
    def __init__(self, path):
        super().__init__()
        self.path = Path(path).resolve()
        data = self.path.read_bytes()
        if len(data) < 52 or data[:7] != b"\x7fELF\x01\x01\x01":
            raise ValueError("Expected a 32-bit little-endian ELF file")
        if struct.unpack_from("<H", data, 18)[0] != 40:
            raise ValueError("Expected an ARM ELF file")
        offset = struct.unpack_from("<I", data, 32)[0]
        entry_size, count = struct.unpack_from("<HH", data, 46)
        if entry_size < 40 or offset + count * entry_size > len(data):
            raise ValueError("Invalid ELF section table")
        sections = [struct.unpack_from("<10I", data, offset + i * entry_size)
                    for i in range(count)]
        for section in sections:
            if section[1] != 2:  # SHT_SYMTAB
                continue
            start, size, link, stride = section[4], section[5], section[6], section[9]
            if stride < 16 or link >= count or start + size > len(data):
                raise ValueError("Invalid ELF symbol table")
            strings = sections[link]
            names = data[strings[4]:strings[4] + strings[5]]
            for pos in range(start, start + size, stride):
                name, value, length, info, _other, index = struct.unpack_from("<IIIBBH", data, pos)
                if not name or index == 0 or (info & 15) == 4 or name >= len(names):
                    continue
                end = names.find(b"\0", name)
                if end < 0:
                    raise ValueError("Unterminated ELF symbol name")
                text = names[name:end].decode("utf-8", errors="strict")
                if not text.startswith("$"):
                    self[text] = Symbol(value, length, info & 15)


class _Frame(C.Structure):
    _fields_ = [("emulator_frame", C.c_uint32), ("keys", C.c_uint32),
                ("audio_samples", C.c_uint32), ("watched_value", C.c_uint32),
                ("runframe_ns", C.c_uint64)]


def _load_bridge():
    folder = Path(__file__).resolve().parent
    override = os.environ.get("MGBA_BRIDGE_PATH")
    library = Path(override).resolve() if override else folder / "mgba_bridge.so"
    source = folder / "mgba_bridge.c"
    if override and not library.exists():
        raise FileNotFoundError(library)
    if not override and (not library.exists() or library.stat().st_mtime < source.stat().st_mtime):
        subprocess.run(["bash", str(folder / "mgba_build.sh")], check=True)
    lib = C.CDLL(str(library))
    ptr = C.c_void_p
    signatures = {
        "qa_open": ([C.c_char_p, C.c_char_p, C.c_char_p, C.c_size_t], ptr),
        "qa_close": ([ptr], None),
        "qa_step": ([ptr, C.c_uint32, C.c_uint32, C.POINTER(_Frame)], C.c_int),
        "qa_rgb": ([ptr], C.POINTER(C.c_uint8)),
        "qa_start_capture": ([ptr, C.c_int, C.c_char_p], C.c_int),
        "qa_stop_capture": ([ptr], None),
        "qa_export_save": ([ptr, C.c_char_p], C.c_int),
        "qa_watch": ([ptr, C.c_uint32, C.c_int], None),
        "qa_sample_rate": ([], C.c_uint),
        "qa_capture_sumsq": ([ptr], C.c_double),
    }
    for name in ("qa_width", "qa_height", "qa_frame_counter", "qa_capture_peak"):
        signatures[name] = ([ptr], C.c_uint32)
    for name in ("qa_sample_count", "qa_capture_frames", "qa_capture_samples", "qa_capture_nonzero"):
        signatures[name] = ([ptr], C.c_uint64)
    for name in ("qa_frequency", "qa_frame_cycles", "qa_capture_error"):
        signatures[name] = ([ptr], C.c_int32)
    for name in ("qa_read8", "qa_read16", "qa_read32"):
        signatures[name] = ([ptr, C.c_uint32], C.c_uint32)
    for name, (args, result) in signatures.items():
        function = getattr(lib, name)
        function.argtypes = args
        function.restype = result
    return lib


def _png_rgb(width, height, rgb):
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    scanlines = b"".join(b"\0" + rgb[y * width * 3:(y + 1) * width * 3]
                         for y in range(height))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(scanlines, 6)) + chunk(b"IEND", b""))


class Mgba:
    """A cold-booted GBA session. step() is the only gameplay mutation API.

    If save_path exists, it is loaded as battery SRAM before boot. On close,
    real cartridge SRAM is exported there atomically. No path means erased
    SRAM and no automatic save export. Supplying elf only reads its symbols.
    """
    def __init__(self, rom, *, elf=None, save_path=None, trace_path=None, watch_symbol=None):
        self.rom = Path(rom).resolve()
        if not self.rom.is_file():
            raise FileNotFoundError(self.rom)
        self.save_path = Path(save_path).resolve() if save_path else None
        if self.save_path:
            self.save_path.parent.mkdir(parents=True, exist_ok=True)
        self.symbols = ElfSymbols(elf) if elf else {}
        self.lib = _load_bridge()
        self._core = None
        self._recording = None
        self._trace = self._timing_file = None
        self._watch_symbol = watch_symbol
        self._frame_records = []
        self._step_host_ns = 0
        self._start_ns = time.monotonic_ns()
        self.metadata = {
            "backend": "libmGBA", "control": "addKeys/clearKeys + runFrame",
            "memory_writes": False, "savestate_loads": False,
            "rom_path": str(self.rom), "rom_sha256": sha256(self.rom),
            "elf_path": str(self.symbols.path) if elf else None,
            "elf_sha256": sha256(self.symbols.path) if elf else None,
            "save_input_path": str(self.save_path) if self.save_path and self.save_path.exists() else None,
            "save_input_sha256": sha256(self.save_path) if self.save_path and self.save_path.exists() else None,
        }
        try:
            self.metadata["mgba_version"] = C.c_char_p.in_dll(self.lib, "projectVersion").value.decode()
        except ValueError:
            self.metadata["mgba_version"] = "unknown (system libmGBA)"
        error = C.create_string_buffer(1024)
        self._core = self.lib.qa_open(os.fsencode(self.rom),
                                     os.fsencode(self.save_path) if self.save_path else None,
                                     error, len(error))
        if not self._core:
            raise RuntimeError(error.value.decode())
        self.width = self.lib.qa_width(self._core)
        self.height = self.lib.qa_height(self._core)
        self.frame_rate = Fraction(self.lib.qa_frequency(self._core), self.lib.qa_frame_cycles(self._core))
        self.sample_rate = self.lib.qa_sample_rate()
        self.metadata.update({"native_width": self.width, "native_height": self.height,
                              "native_frame_rate": str(self.frame_rate), "audio_sample_rate": self.sample_rate,
                              "timing_watch_symbol": watch_symbol})
        if watch_symbol:
            symbol = self.symbols[watch_symbol]
            if symbol.size not in (1, 2, 4):
                self.close()
                raise ValueError("Timing watch requires a scalar 8-, 16-, or 32-bit symbol")
            self.lib.qa_watch(self._core, symbol.address, symbol.size)
        if trace_path:
            trace_path = Path(trace_path).resolve()
            trace_path.parent.mkdir(parents=True, exist_ok=True)
            self._trace = trace_path.open("w", encoding="utf-8")
            self._timing_file = trace_path.with_suffix(".frames.csv").open("w", newline="", encoding="utf-8")
            self._timing_writer = csv.writer(self._timing_file)
            self._timing_writer.writerow(["emulator_frame", "key_mask", "runframe_ns", "audio_samples", "watched_value"])
            self._event("boot", **self.metadata)

    def _open(self):
        if not self._core:
            raise RuntimeError("mGBA session is closed")
        return self._core

    def _event(self, kind, **fields):
        if self._trace:
            self._trace.write(json.dumps({"event": kind, **fields}, sort_keys=True) + "\n")
            self._trace.flush()

    @property
    def frame(self):
        return self.lib.qa_frame_counter(self._open())

    def step(self, keys=(), frames=1):
        """Set the complete held-key set, then emulate exactly `frames` frames."""
        if not isinstance(frames, int) or not 0 <= frames <= 1_000_000:
            raise ValueError("frames must be an integer in [0, 1000000]")
        mask = key_mask(keys)
        before = self.frame
        records = (_Frame * frames)()
        start = time.monotonic_ns()
        error = self.lib.qa_step(self._open(), mask, frames, records)
        elapsed = time.monotonic_ns() - start
        self._step_host_ns += elapsed
        if error:
            self._event("step_error", frame_before=before, keys=mask, requested_frames=frames,
                        frame_after=self.frame, errno=error)
            raise OSError(error, os.strerror(error))
        rows = [(r.emulator_frame, r.keys, r.runframe_ns, r.audio_samples, r.watched_value) for r in records]
        self._frame_records.extend(rows)
        if self._timing_file:
            self._timing_writer.writerows(rows)
            self._timing_file.flush()
        self._event("input", frame_before=before, frame_after=self.frame, frames=frames, keys=mask,
                    key_names=[name for name, bit in KEYS.items() if mask & bit], host_step_ns=elapsed)
        return self.frame

    def tap(self, keys, *, hold=4, release=4):
        """Release first so the game sees a new press, then hold and release."""
        self.step((), release)
        self.step(keys, hold)
        self.step((), release)
        return self.frame

    def rgb(self):
        return C.string_at(self.lib.qa_rgb(self._open()), self.width * self.height * 3)

    def screenshot(self, path):
        path = Path(path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(_png_rgb(self.width, self.height, self.rgb()))
        self._event("screenshot", frame=self.frame, path=str(path), sha256=sha256(path))
        return path

    def read8(self, address):
        return self.lib.qa_read8(self._open(), address)

    def read16(self, address):
        return self.lib.qa_read16(self._open(), address)

    def read32(self, address):
        return self.lib.qa_read32(self._open(), address)

    # Explicit aliases match mGBA's public bus-read names.
    busRead8, busRead16, busRead32 = read8, read16, read32

    def read_range(self, address, size):
        if not 0 <= size <= 1_048_576:
            raise ValueError("Read range too large")
        return bytes(self.read8(address + i) for i in range(size))

    def read_symbol(self, name, *, width=None, offset=0, signed=False):
        symbol = self.symbols[name]
        width = width or symbol.size
        if width not in (1, 2, 4):
            raise ValueError(f"Symbol {name!r} has size {symbol.size}; specify width=1, 2, or 4")
        if offset < 0 or offset + width > symbol.size:
            raise ValueError("Read exceeds the ELF symbol size")
        value = {1: self.read8, 2: self.read16, 4: self.read32}[width](symbol.address + offset)
        if signed and value & (1 << (width * 8 - 1)):
            value -= 1 << (width * 8)
        return value

    def export_save(self, path):
        """Clone only actual battery SRAM, then write an atomic host file."""
        path = Path(path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
        os.close(descriptor)
        try:
            error = self.lib.qa_export_save(self._open(), os.fsencode(temporary))
            if error:
                raise OSError(error, os.strerror(error))
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        self._event("battery_save_export", frame=self.frame, path=str(path), size=path.stat().st_size, sha256=sha256(path))
        return path

    def start_recording(self, path):
        """Record all subsequent native frames and stereo samples to MKV/MP4."""
        self._open()
        if self._recording:
            raise RuntimeError("A capture is already running")
        if not shutil.which("ffmpeg"):
            raise RuntimeError("ffmpeg is required for video capture")
        path = Path(path).resolve()
        if path.suffix.lower() not in (".mkv", ".mp4"):
            raise ValueError("Capture path must end in .mkv or .mp4")
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix="mgba-capture-", dir=path.parent)
        folder = Path(temporary.name)
        video = folder / "native_video.mkv"
        pcm = folder / "native_audio.pcm"
        log = (folder / "ffmpeg.log").open("wb")
        command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
                   "-f", "rawvideo", "-pixel_format", "rgb24", "-video_size", f"{self.width}x{self.height}",
                   "-framerate", str(self.frame_rate), "-i", "pipe:0", "-an",
                   "-c:v", "ffv1", "-level", "3", str(video)]
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=log)
        error = self.lib.qa_start_capture(self._core, process.stdin.fileno(), os.fsencode(pcm))
        if error:
            process.stdin.close()
            process.wait()
            log.close()
            temporary.cleanup()
            raise OSError(error, os.strerror(error))
        self._recording = {"path": path, "temporary": temporary, "folder": folder, "video": video,
                           "pcm": pcm, "log": log, "process": process, "start_frame": self.frame}
        self._event("capture_start", frame=self.frame, path=str(path), native_frame_rate=str(self.frame_rate))
        return path

    def stop_recording(self):
        if not self._recording:
            return None
        capture = self._recording
        self._recording = None
        self.lib.qa_stop_capture(self._open())
        error = self.lib.qa_capture_error(self._core)
        capture["process"].stdin.close()
        code = capture["process"].wait(timeout=60)
        capture["log"].close()
        if error or code:
            detail = (capture["folder"] / "ffmpeg.log").read_text(errors="replace")
            raise RuntimeError(f"Native capture failed ({error=}, ffmpeg={code}): {detail}")
        frames = self.lib.qa_capture_frames(self._core)
        samples = self.lib.qa_capture_samples(self._core)
        if not frames:
            capture["temporary"].cleanup()
            raise RuntimeError("Capture contains no emulated frames")
        audio_path = capture["path"].with_suffix(".wav")
        with wave.open(str(audio_path), "wb") as out, capture["pcm"].open("rb") as source:
            out.setnchannels(2)
            out.setsampwidth(2)
            out.setframerate(self.sample_rate)
            for data in iter(lambda: source.read(1024 * 1024), b""):
                out.writeframesraw(data)
        command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
                   "-i", str(capture["video"]), "-i", str(audio_path),
                   "-map", "0:v:0", "-map", "1:a:0"]
        if capture["path"].suffix.lower() == ".mkv":
            command += ["-c:v", "copy", "-c:a", "pcm_s16le"]
        else:
            command += ["-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart"]
        command.append(str(capture["path"]))
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=60)
        video_seconds = float(Fraction(frames, 1) / self.frame_rate)
        audio_seconds = samples / self.sample_rate
        report = {
            **self.metadata, "path": str(capture["path"]), "sha256": sha256(capture["path"]),
            "start_frame": capture["start_frame"], "end_frame": self.frame, "captured_frames": frames,
            "video_seconds": video_seconds, "audio_samples_per_channel": samples,
            "audio_seconds": audio_seconds, "audio_minus_video_seconds": audio_seconds - video_seconds,
            "audio_path": str(audio_path), "audio_sha256": sha256(audio_path),
            "audio_peak_s16": self.lib.qa_capture_peak(self._core),
            "audio_nonzero_samples": self.lib.qa_capture_nonzero(self._core),
            "audio_rms_s16": math.sqrt(self.lib.qa_capture_sumsq(self._core) / (samples * 2)) if samples else 0,
            "video_source": "Native mGBA video buffer after each runFrame; no synthetic frames or overlays",
            "audio_source": "mGBA blip stereo output; no synthetic audio",
            "container": capture["path"].suffix.lower()[1:],
            "lossless_video": capture["path"].suffix.lower() == ".mkv",
        }
        capture["path"].with_suffix(".capture.json").write_text(json.dumps(report, indent=2) + "\n")
        self._event("capture_end", **report)
        capture["temporary"].cleanup()
        return report

    def timing_report(self):
        """Host core costs and native emulated duration; not a hardware FPS claim."""
        values = sorted(row[2] for row in self._frame_records)
        count = len(values)
        def percentile(fraction):
            return values[min(count - 1, math.ceil(count * fraction) - 1)] / 1e6 if count else None
        report = {
            "stepped_native_frames": count, "native_frame_rate": str(self.frame_rate),
            "emulated_seconds": float(Fraction(count, 1) / self.frame_rate),
            "runframe_total_seconds": sum(values) / 1e9,
            "runframe_ms_p50": percentile(.5), "runframe_ms_p95": percentile(.95),
            "runframe_ms_max": values[-1] / 1e6 if count else None,
            "step_host_seconds_including_capture": self._step_host_ns / 1e9,
            "runframe_cost_includes_os_preemption": True,
            "claim": "Emulator stepping costs on this host; does not measure GBA hardware display FPS",
        }
        if self._watch_symbol and count:
            observed = [row[4] for row in self._frame_records]
            report["watch_symbol"] = self._watch_symbol
            report["watch_distinct_values"] = len(set(observed))
            report["watch_repeated_native_frames"] = sum(a == b for a, b in zip(observed, observed[1:]))
            report["watch_first_value"] = observed[0]
            report["watch_last_value"] = observed[-1]
        return report

    def close(self):
        if not self._core:
            return
        try:
            if self._recording:
                self.stop_recording()
            if self.save_path:
                self.export_save(self.save_path)
            self._event("shutdown", frame=self.frame, timing=self.timing_report())
        finally:
            self.lib.qa_close(self._core)
            self._core = None
            if self._trace:
                self._trace.close()
                self._trace = None
            if self._timing_file:
                self._timing_file.close()
                self._timing_file = None

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", type=Path)
    parser.add_argument("--elf", type=Path)
    parser.add_argument("--save", type=Path)
    parser.add_argument("--script", type=Path, help="JSON list of {keys, frames, screenshot?, label?}; input only")
    parser.add_argument("--frames", type=int, default=180, help="Idle boot frames if no script")
    parser.add_argument("--screenshot", type=Path)
    parser.add_argument("--video", type=Path)
    parser.add_argument("--trace", type=Path)
    parser.add_argument("--watch-symbol")
    args = parser.parse_args()
    with Mgba(args.rom, elf=args.elf, save_path=args.save, trace_path=args.trace,
              watch_symbol=args.watch_symbol) as emu:
        if args.video:
            emu.start_recording(args.video)
        script = json.loads(args.script.read_text()) if args.script else [{"keys": [], "frames": args.frames}]
        for action in script:
            emu.step(action.get("keys", ()), action.get("frames", 1))
            if action.get("screenshot"):
                emu.screenshot(action["screenshot"])
            if action.get("label"):
                emu._event("label", frame=emu.frame, text=action["label"])
        if args.screenshot:
            emu.screenshot(args.screenshot)
        capture = emu.stop_recording() if args.video else None
        print(json.dumps({"boot": emu.metadata, "timing": emu.timing_report(), "capture": capture}, indent=2))


if __name__ == "__main__":
    main()
