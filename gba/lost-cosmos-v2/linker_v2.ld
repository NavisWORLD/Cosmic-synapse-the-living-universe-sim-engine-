ENTRY(_start)
SECTIONS
{
  .text 0x080000C0 : {
    KEEP(*(.text.startup))
    *(.text*)
    *(.rodata*)
  }
  . = ALIGN(4);
  .data : { *(.data*) }
  .bss 0x03000000 (NOLOAD) : {
    __bss_start__ = .;
    *(.bss*)
    *(COMMON)
    . = ALIGN(4);
    __bss_end__ = .;
  }
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) *(.note*) }
}
