.syntax unified
.thumb
.cpu cortex-m33
.section .entry,"ax",%progbits
.global blob_start
.global native_entry
.type native_entry,%function
blob_start:
native_entry:
    b.w bootstrap_entry
.global blob_parameter
blob_parameter:
    .word 0
.thumb_func
bootstrap_entry:
    adr.w r0, blob_parameter
    ldr r0, [r0]
    b.w bootstrap
.global screen_hook_entry
.type screen_hook_entry,%function
.thumb_func
screen_hook_entry:
    adr.w r2, blob_parameter
    ldr r2, [r2]
    b.w screen_hook
