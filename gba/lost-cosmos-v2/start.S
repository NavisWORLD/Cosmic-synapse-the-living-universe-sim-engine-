    .syntax unified
    .cpu arm7tdmi
    .arm
    .section .text.startup,"ax",%progbits
    .global _start
    .type _start,%function
_start:
    ldr sp, =0x03007F00
    ldr r0, =__bss_start__
    ldr r1, =__bss_end__
    mov r2, #0
0:
    cmp r0, r1
    bhs 1f
    str r2, [r0], #4
    b 0b
1:
    bl gba_main
2:
    b 2b
    .size _start, .-_start
