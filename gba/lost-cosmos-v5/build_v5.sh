#!/usr/bin/env bash
set -euo pipefail
QA=${QA:-0}
CFLAGS=(--target=arm-none-eabi -mcpu=arm7tdmi -marm -ffreestanding -fno-builtin -fno-stack-protector -fno-exceptions -fno-unwind-tables -fno-asynchronous-unwind-tables -Os -Wno-unused-function -Wno-misleading-indentation)
clang "${CFLAGS[@]}" -c start_v5.S -o start_v5.o
EXTRA=()
[[ "$QA" == 1 ]] && EXTRA=(-DQA_AUTORUN)
clang "${CFLAGS[@]}" "${EXTRA[@]}" -c lost_cosmos_v5.c -o game_v5.o
ld.lld -T linker_v5.ld start_v5.o game_v5.o -o lost_cosmos_v5.elf
llvm-objcopy -O binary lost_cosmos_v5.elf payload_v5.bin
python build_rom_v5.py --payload payload_v5.bin
python verify_v5.py
