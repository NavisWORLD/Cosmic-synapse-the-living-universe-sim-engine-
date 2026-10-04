#!/usr/bin/env bash
set -euo pipefail
QA=${QA:-0}
CFLAGS=(--target=arm-none-eabi -mcpu=arm7tdmi -marm -ffreestanding -fno-builtin -fno-stack-protector -fno-exceptions -fno-unwind-tables -fno-asynchronous-unwind-tables -Os -Wno-unused-function -Wno-misleading-indentation)
clang "${CFLAGS[@]}" -c start.S -o start.o
EXTRA=()
[[ "$QA" == 1 ]] && EXTRA=(-DQA_AUTORUN)
clang "${CFLAGS[@]}" "${EXTRA[@]}" -c lost_cosmos_v2.c -o game.o
ld.lld -T linker_v2.ld start.o game.o -o lost_cosmos_v2.elf
llvm-objcopy -O binary lost_cosmos_v2.elf payload.bin
python build_rom.py
python verify_v2.py
