    .syntax unified
    .cpu arm7tdmi
    .arm
    .section .text.startup,"ax",%progbits
    .global _start
    .type _start,%function
_start:
    ldr sp, =0x03007F00

    /* Copy initialized writable data from cartridge ROM to IWRAM. */
    ldr r0, =__data_load__
    ldr r1, =__data_start__
    ldr r2, =__data_end__
0:
    cmp r1, r2
    bhs 1f
    ldr r3, [r0], #4
    str r3, [r1], #4
    b 0b

    /* Clear BSS after .data. */
1:
    ldr r0, =__bss_start__
    ldr r1, =__bss_end__
    mov r2, #0
2:
    cmp r0, r1
    bhs 3f
    str r2, [r0], #4
    b 2b
3:
    bl gba_main
4:
    b 4b
    .size _start, .-_start
