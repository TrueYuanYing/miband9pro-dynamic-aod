ENTRY(native_entry)
SECTIONS {
 . = 0;
 .text : { KEEP(*(.entry)) *(.text .text.*) *(.rodata .rodata.*) }
 blob_end = .;
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) *(.eh_frame*) }
}
