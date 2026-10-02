#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
cc="${CC:-cc}"
bin="$(mktemp "${TMPDIR:-/tmp}/lost-cosmos-c99.XXXXXXXX")"
trap 'rm -f "$bin"' EXIT INT HUP TERM
"$cc" -std=c99 -O2 -Wall -Wextra -Werror -pedantic native/lc_creature.c tests/test_creature.c -o "$bin"
"$bin"
python3 -B -m unittest discover -s tests -p 'test_bridge.py' -v
printf '%s\n' 'PASS: all standalone host creature and build-time import tests completed'
