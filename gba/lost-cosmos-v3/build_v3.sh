#!/usr/bin/env bash
set -euo pipefail
QA=${QA:-0}
CFLAGS=(--target=arm-none-eabi -mcpu=arm7tdmi -marm -ffreestanding -fno-builtin -fno-stack-protector -fno-exceptions -fno-unwind-tables -fno-asynchronous-unwind-tables -Os -Wno-unused-function -Wno-misleading-indentation)
clang "${CFLAGS[@]}" -c start_v3.S -o start_v3.o
EXTRA=()
[[ "$QA" == 1 ]] && EXTRA=(-DQA_AUTORUN)
clang "${CFLAGS[@]}" "${EXTRA[@]}" -c lost_cosmos_v3.c -o game_v3.o
ld.lld -T linker_v3.ld start_v3.o game_v3.o -o lost_cosmos_v3.elf
llvm-objcopy -O binary lost_cosmos_v3.elf payload_v3.bin
python build_rom_v3.py --payload payload_v3.bin
python verify_v3.py
