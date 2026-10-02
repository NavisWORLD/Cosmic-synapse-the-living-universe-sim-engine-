#!/usr/bin/env python3
"""Bundle the compiled bridge and its actual non-glibc ELF dependencies.

Run on the Ubuntu 24.04 CI runner after mgba_build.sh. Returned artifacts can
run with Python on a matching Ubuntu 24.04 x86_64 container without apt access.
No ROM or emulator state is modified by this packaging tool.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge", type=Path, default=root / "tools/mgba_bridge.so")
    parser.add_argument("--out", type=Path, default=root / "artifacts/runner-runtime")
    args = parser.parse_args()
    bridge = args.bridge.resolve()
    output = args.out.resolve()
    libraries = output / "lib"
    libraries.mkdir(parents=True, exist_ok=True)
    if not bridge.is_file():
        raise FileNotFoundError(f"Build the genuine libmGBA bridge first: {bridge}")
    listing = subprocess.check_output(["ldd", str(bridge)], text=True, stderr=subprocess.STDOUT)
    if "not found" in listing:
        raise RuntimeError(f"The built bridge has missing dependencies:\n{listing}")
    # glibc must come from the matching host rather than mixing dynamic loaders.
    system = re.compile(r"^(?:ld-linux.*|lib(?:c|m|pthread|dl|rt|resolv|util|nsl)\.so(?:\..*)?)$")
    copied, excluded = [], []
    for line in listing.splitlines():
        match = re.match(r"\s*(\S+)\s+=>\s+(/\S+)\s+\(", line)
        if not match:
            continue
        soname, original = match.groups()
        original = Path(original)
        actual = original.resolve()
        if system.match(soname):
            excluded.append({"soname": soname, "host_path": str(original)})
            continue
        destination = libraries / actual.name
        shutil.copy2(actual, destination)
        if soname != actual.name:
            alias = libraries / soname
            if alias.is_symlink() or alias.exists():
                alias.unlink()
            alias.symlink_to(actual.name)
        copied.append({"soname": soname, "source": str(actual), "file": str(destination.relative_to(output)),
                       "bytes": actual.stat().st_size, "sha256": digest(actual)})
    bundled_bridge = output / "mgba_bridge.so"
    shutil.copy2(bridge, bundled_bridge)
    wrapper = output / "run.sh"
    wrapper.write_text('''#!/usr/bin/env bash
set -euo pipefail
MGBA_RUNTIME_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
export MGBA_BRIDGE_PATH="$MGBA_RUNTIME_DIR/mgba_bridge.so"
export LD_LIBRARY_PATH="$MGBA_RUNTIME_DIR/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
exec "${PYTHON:-python3}" "$@"
''')
    wrapper.chmod(0o755)
    manifest = {"purpose": "Genuine headless libmGBA controller capture runtime", "machine": platform.machine(),
                "runner_os": Path("/etc/os-release").read_text() if Path("/etc/os-release").exists() else platform.platform(),
                "bridge_sha256": digest(bridge), "copied_libraries": copied,
                "required_host_libraries": excluded, "ldd_output": listing}
    (output / "runtime.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (output / "README.txt").write_text(
        "Use on a matching Ubuntu 24.04 runner/container architecture.\n"
        "Run from the repository: bash artifacts/runner-runtime/run.sh tests/test_mgba_controller.py --out artifacts/local_mgba\n"
        "Or: bash artifacts/runner-runtime/run.sh tools/mgba.py path/to/actual.gba --elf path/to/matching.elf --frames 180 --screenshot artifacts/boot.png\n"
        "The wrapper sets MGBA_BRIDGE_PATH and LD_LIBRARY_PATH; it never installs libraries system-wide.\n"
        "Python3 and ffmpeg/ffprobe are supplied by the host. A matching native ROM and ELF must be provided.\n")
    print(json.dumps({"runtime_directory": str(output), "dependency_count": len(copied),
                      "total_bytes": bridge.stat().st_size + sum(lib["bytes"] for lib in copied)}, indent=2))


if __name__ == "__main__":
    main()
