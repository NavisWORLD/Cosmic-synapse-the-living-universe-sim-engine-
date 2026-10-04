# Native controller QA and capture

`tools/mgba.py` boots the unmodified GBA ROM in the actual libmGBA core.
`step(keys, frames)` applies controller bits through mGBA `addKeys` and
`clearKeys`, then calls `runFrame` once for every requested native frame.
No emulator memory write, cheat, savedata restore, or savestate loading API is
exported. ELF symbols and `busRead8/16/32` are used only to observe actual game
state, diagnose failures, or choose subsequent controller inputs.

## Dependencies and reproducible smoke check

Ubuntu 24.04 / mGBA 0.10.x:

```sh
sudo apt-get update
sudo apt-get install -y clang lld llvm libmgba-dev ffmpeg gcc python3
cd LOST_COSMOS_V10_SOURCE
bash build_v5.sh
cd ..
bash tools/mgba_build.sh
python3 tests/test_mgba_controller.py --out artifacts/mgba_controller
```

The smoke check uses a fresh battery save, starts New Game from the real title,
advances the real opening with A, walks through actual directional input,
saves through the real START menu, closes the core, and cold boots a second
core to select Continue. It checks the restored position and progression,
native 240×160 screenshots, every encoded video frame, and nonzero stereo audio.
It fails closed; it does not certify campaign completion or three endings.

For a GitHub Actions Ubuntu runner, the same commands run without Xvfb, SDL,
window automation, a BIOS file, or Python package installation. Upload the
whole `artifacts/mgba_controller` directory with `actions/upload-artifact@v4`,
including on failure, so native captures, input traces, and timing CSVs remain
reviewable. mGBA's built-in BIOS executes the normal ROM boot; a hardware BIOS
comparison is a separate acceptance step.

## Controller script API

```python
import sys
sys.path.insert(0, "tools")
from mgba import Mgba

with Mgba("LOST_COSMOS_V10_SOURCE/LOST_COSMOS_V10_OPENING_QA.gba",
          elf="LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.elf",
          save_path="artifacts/playthrough.sav",
          trace_path="artifacts/playthrough.inputs.jsonl",
          watch_symbol="frame") as emu:
    emu.start_recording("artifacts/playthrough.mkv")
    emu.step((), 180)
    emu.screenshot("artifacts/title.png")
    emu.tap("A", hold=12, release=12)
    emu.step(("RIGHT", "B"), 30)
    world = emu.read_symbol("current_world")
    # Clang -Os can split this Actor; resolve the names in the matching ELF.
    x = emu.read_symbol("player.0", signed=True)
    y = emu.read_symbol("player.1", signed=True)
    emu.screenshot("artifacts/current.png")
    capture = emu.stop_recording()
    timings = emu.timing_report()
```

The complete held-key set is supplied to each `step` call; an empty set
releases all keys. Supported names are A, B, SELECT, START, RIGHT, LEFT, UP,
DOWN, R, L. `tap` releases before a new press. Hold a key long enough for the
game's main loop to sample it; a one-native-frame press may be missed if the
game takes more than one VBlank to finish a loop. Holding directions remains
ordinary controller movement.

The supplied ELF must match the ROM build. Its bytes are never loaded into the
emulator; the parser reads the ELF32 ARM symbol table on the host. Structs and
arrays can be inspected with `read_range(symbol.address, symbol.size)` or
`read_symbol(..., width=..., offset=...)`. These APIs expose no write method.
LLVM may scalarize a static struct into symbols such as `player.0` (x) and
`player.1` (y); the smoke check supports both the original struct and these
actual scalar symbols. Resolve names and addresses from each matching ELF.

An existing `save_path` is loaded as battery SRAM **before** the cold boot. An
absent path starts with erased SRAM. Closing exports a clone of the actual
cartridge SRAM to that path; this is not a game save action. Only the native
game's own SAVE/controller actions establish gameplay progress. Keep an
original save backup before asking the emulator to play with it. A campaign
fork may cold boot from a byte-for-byte copy of an input-earned save, provided
the evidence identifies the common pre-choice input history and save hash.

The command line also accepts an input-only JSON script:

```sh
python3 tools/mgba.py path/to/game.gba --elf path/to/game.elf \
  --script path/to/inputs.json --save artifacts/session.sav \
  --trace artifacts/session.inputs.jsonl --watch-symbol frame \
  --video artifacts/session.mkv --screenshot artifacts/current.png
```

The JSON is a list of objects such as
`{"keys": ["RIGHT"], "frames": 30, "screenshot": "artifacts/walk.png"}`.
An optional `label` adds an annotation to the trace, not to captured frames.

## Evidence and timing limits

- PNGs are encoded directly from mGBA's current native video buffer. No game
  art renderer or synthetic preview contributes to captures.
- Lossless MKV stores every native RGB24 frame using FFV1 and genuine PCM
  stereo audio. MP4 exports the same frames with H.264/AAC compression. Neither
  adds overlays or rescales the 240×160 image. A separate WAV preserves the
  exact 32,768 Hz stereo signed 16-bit samples emitted by the core's blip
  output. Capture metadata records counts, duration, hashes, peak, and RMS.
- The native rate comes from `frequency / frameCycles`, usually
  `262144/4389` for GBA. Playback uses that native timeline, even if headless
  stepping is faster or slower than wall time. A 60 Hz encoder is not used.
- Timing CSVs record `runFrame` host cost per frame, native frame counter,
  held input, emitted audio sample count, and optional read-only game counter.
  They include host scheduling interruptions. They do not establish GBA
  hardware display FPS or prove the game completes its own loop every native
  frame. Repeated observed game-counter values are reported separately.
- Video encoding and disk backpressure are included in host `step` elapsed
  time but excluded from the isolated `runFrame` cost. Capture stops fail if
  encoding fails. Empty or silent files are not accepted by the smoke check.
- This frontend is synchronous and headless. It verifies native rendering,
  sound, SRAM, and controller behavior; it does not replace physical GBA,
  Delta on iPhone, touch usability, or human literary and visual acceptance.

The implementation follows mGBA's primary-source core interface and example:
[core.h](https://github.com/mgba-emu/mgba/blob/0.10.3/include/mgba/core/core.h),
[client/server example](https://github.com/mgba-emu/mgba/blob/0.10.3/src/platform/example/client-server/server.c),
[libretro audio frontend](https://github.com/mgba-emu/mgba/blob/0.10.3/src/platform/libretro/libretro.c),
and [official scripting API](https://mgba.io/docs/scripting.html).
