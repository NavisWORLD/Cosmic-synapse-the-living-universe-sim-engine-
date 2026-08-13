# Native Living Universe Engine

The native rebuild separates external data ingestion from an authoritative C++ simulation runtime.

## Headless deterministic test

```bash
cmake -S . -B build -DCOSMOS_BUILD_GAME=OFF -DCOSMOS_BUILD_TESTS=ON
cmake --build build --config Release
./build/cosmos_headless
```

## Live NASA/USGS bridge

```bash
export NASA_API_KEY="YOUR_KEY"
python3 python/run_bridge.py
```

PowerShell:

```powershell
$env:NASA_API_KEY="YOUR_KEY"
python python/run_bridge.py
```

The Python process writes an atomic TSV snapshot under `runtime/`; the C++ game polls that snapshot without allowing network latency to block the fixed-step simulation.

## Native game

```bash
cmake -S . -B build -DCOSMOS_BUILD_GAME=ON
cmake --build build --config Release
```

Controls in the vertical slice:

- `TAB`: orbit/surface/APOD
- `WASD`: surface movement
- arrows: turn
- `SPACE`: jump
- `Shift`: sprint
- `F`: fold through sample worlds
- `L`: seed simulated life
- `O`: place outpost
- `K`: inject simulated storm
- `X`: manifest anomaly
- `T`: time warp

The native port is a vertical slice. The single-file HTML remains the richest all-in-one implementation in this release.
