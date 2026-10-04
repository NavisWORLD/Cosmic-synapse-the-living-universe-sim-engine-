ENTRY(_start)
SECTIONS
{
  .text 0x080000C0 : {
    KEEP(*(.text.startup))
    *(.text*)
    *(.rodata*)
    . = ALIGN(4);
    __rom_text_end__ = .;
  }

  /* Mutable non-zero globals execute from writable IWRAM.
     Their initial bytes are stored immediately after .text in ROM. */
  .data 0x03000000 : AT(__rom_text_end__) {
    __data_start__ = .;
    *(.data*)
    . = ALIGN(4);
    __data_end__ = .;
  }
  __data_load__ = LOADADDR(.data);

  .bss ALIGN(4) (NOLOAD) : {
    __bss_start__ = .;
    *(.bss*)
    *(COMMON)
    . = ALIGN(4);
    __bss_end__ = .;
  }
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) *(.note*) }
}
