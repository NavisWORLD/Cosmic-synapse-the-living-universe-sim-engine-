#!/usr/bin/env bash
# Build the current Lost Cosmos cartridge (Act I on the V11.2 Spark ROM) into the handheld.
# The ROM is original homebrew and is not committed.
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
src="$root/gba/lost-cosmos-living-multiverse/LOST_COSMOS_V10_SOURCE"
out="$root/arcade/lost-cosmos/rom"
mkdir -p "$out"
node "$root/scripts/bake-spark-gba.mjs"
(
  cd "$src"
  QA=0 IMPORTED_BEAST=0 bash build_v5.sh
)
cp -f "$src/LOST_COSMOS_V10_OPENING_QA.gba" "$out/lost-cosmos.gba"
python3 - "$out" <<'PY'
import hashlib, json, pathlib, subprocess, sys
out = pathlib.Path(sys.argv[1])
rom = (out / 'lost-cosmos.gba').read_bytes()
manifest = {'version': '11.3', 'sha256': hashlib.sha256(rom).hexdigest(),
            'bytes': len(rom), 'source_commit': subprocess.check_output(
                ['git', 'rev-parse', 'HEAD'], cwd=out, text=True).strip()}
(out / 'release.json').write_text(json.dumps(manifest, indent=2) + '\n')
PY
echo "Built $out/lost-cosmos.gba"
