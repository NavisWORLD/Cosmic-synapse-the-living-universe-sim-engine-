#!/usr/bin/env bash
# Build the committed Lost Cosmos V11.1.1 source into the handheld ROM.
# The ROM is original homebrew and is not committed.
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
src="$root/gba/lost-cosmos-living-multiverse/LOST_COSMOS_V10_SOURCE"
out="$root/arcade/lost-cosmos/rom"
mkdir -p "$out"
(
  cd "$src"
  QA=0 IMPORTED_BEAST=0 bash build_v5.sh
)
cp -f "$src/LOST_COSMOS_V10_OPENING_QA.gba" "$out/lost-cosmos.gba"
echo "Built $out/lost-cosmos.gba"
