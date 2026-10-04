#!/usr/bin/env bash
set -euo pipefail
QA=${QA:-0}
CFLAGS=(--target=arm-none-eabi -mcpu=arm7tdmi -marm -ffreestanding -fno-builtin -fno-stack-protector -fno-exceptions -fno-unwind-tables -fno-asynchronous-unwind-tables -Os -Wno-unused-function -Wno-misleading-indentation)
clang "${CFLAGS[@]}" -c start_v4.S -o start_v4.o
EXTRA=()
[[ "$QA" == 1 ]] && EXTRA=(-DQA_AUTORUN)
clang "${CFLAGS[@]}" "${EXTRA[@]}" -c lost_cosmos_v4.c -o game_v4.o
ld.lld -T linker_v4.ld start_v4.o game_v4.o -o lost_cosmos_v4.elf
llvm-objcopy -O binary lost_cosmos_v4.elf payload_v4.bin
python build_rom_v4.py --payload payload_v4.bin
python verify_v4.py
