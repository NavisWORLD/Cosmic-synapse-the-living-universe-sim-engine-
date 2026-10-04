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

    /* Freestanding ARM EABI unsigned quotient/remainder. ARM7TDMI has no
       divide instruction; avoid an external runtime dependency in the ROM. */
    .global __aeabi_uidiv
    .global __aeabi_uidivmod
    .type __aeabi_uidiv,%function
    .type __aeabi_uidivmod,%function
__aeabi_uidiv:
__aeabi_uidivmod:
    cmp r1, #0
    moveq r1, r0
    moveq r0, #0
    bxeq lr
    mov r2, #0
    mov r3, #1
5:
    cmp r1, r0
    bhs 6f
    tst r1, #0x80000000
    bne 6f
    mov r1, r1, lsl #1
    mov r3, r3, lsl #1
    b 5b
6:
    cmp r0, r1
    subcs r0, r0, r1
    orrcs r2, r2, r3
    mov r1, r1, lsr #1
    movs r3, r3, lsr #1
    bne 6b
    mov r1, r0
    mov r0, r2
    bx lr
