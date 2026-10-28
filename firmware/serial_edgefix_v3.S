#include <avr/io.h>

    .text

/* Wait for CLK low/high. These macros are intentionally tiny: at 16 MHz the
 * IIgs RTC clock provides only about eight CPU cycles per complete bit. */
.macro WAIT_LOW
.Lwait_low_\@:
    sbic _SFR_IO_ADDR(PINB), PB2
    rjmp .Lwait_low_\@
.endm

.macro WAIT_HIGH
.Lwait_high_\@:
    sbis _SFR_IO_ADDR(PINB), PB2
    rjmp .Lwait_high_\@
.endm

/* Save each DATA level in a separate call-clobbered register.  Only one IN is
 * executed between the detected low and high CLK levels; the byte is assembled
 * after the rising edge, during the inter-byte gap.  This remains edge-synchronous even
 * with the factory RC-oscillator tolerance. */
.macro RX_CAPTURE reg
    WAIT_LOW
    WAIT_HIGH
    in \reg, _SFR_IO_ADDR(PINB)
.endm

.macro RX_APPEND reg
    lsl r26
    bst \reg, PB1
    bld r26, 0
.endm
    .global fast_wait_first
    .type fast_wait_first, @function
fast_wait_first:
/* Poll /EN continuously. Timer0 is checked between /EN checks. */
.Lpoll_enable:
    sbic _SFR_IO_ADDR(PINB), PB0
    rjmp .Lread_timer_flag
    rjmp .Lfirst_start
.Lread_timer_flag:
    in r18, _SFR_IO_ADDR(TIFR)
    sbic _SFR_IO_ADDR(PINB), PB0
    rjmp .Ltest_timer_flag
    rjmp .Lfirst_start
.Ltest_timer_flag:
    sbrs r18, OCF0A
    rjmp .Lpoll_enable
    /* Give a newly asserted /EN priority over timer maintenance. */
    sbic _SFR_IO_ADDR(PINB), PB0
    rjmp .Ltimer_event
    rjmp .Lfirst_start
.Ltimer_event:
    clr r24
    ldi r25, 1
    ret

.Lfirst_start:
    /* Capture all command bits before doing any byte assembly. */
    RX_CAPTURE r18
    RX_CAPTURE r19
    RX_CAPTURE r20
    RX_CAPTURE r21
    RX_CAPTURE r22
    RX_CAPTURE r23
    RX_CAPTURE r24
    RX_CAPTURE r25
    clr r26
    RX_APPEND r18
    RX_APPEND r19
    RX_APPEND r20
    RX_APPEND r21
    RX_APPEND r22
    RX_APPEND r23
    RX_APPEND r24
    RX_APPEND r25
    mov r24, r26
    clr r25
    ret
    .size fast_wait_first, .-fast_wait_first

    .global fast_recv_next
    .type fast_recv_next, @function
fast_recv_next:
    RX_CAPTURE r18
    RX_CAPTURE r19
    RX_CAPTURE r20
    RX_CAPTURE r21
    RX_CAPTURE r22
    RX_CAPTURE r23
    RX_CAPTURE r24
    RX_CAPTURE r25
    clr r26
    RX_APPEND r18
    RX_APPEND r19
    RX_APPEND r20
    RX_APPEND r21
    RX_APPEND r22
    RX_APPEND r23
    RX_APPEND r24
    RX_APPEND r25
    mov r24, r26
    ret
    .size fast_recv_next, .-fast_recv_next

    .global fast_send_next
    .type fast_send_next, @function
fast_send_next:
    /* Precompute all eight DDRB states during the long inter-byte gap.
     * This leaves only one OUT after each sampled rising edge.  The IIgs
     * provides about eight 16 MHz CPU cycles between rising edges. */
    in r18, _SFR_IO_ADDR(DDRB)
    andi r18, 0xFD
    mov r27, r24
    com r27

    mov r19, r18
    bst r27, 7
    bld r19, PB1
    mov r20, r18
    bst r27, 6
    bld r20, PB1
    mov r21, r18
    bst r27, 5
    bld r21, PB1
    mov r22, r18
    bst r27, 4
    bld r22, PB1
    mov r23, r18
    bst r27, 3
    bld r23, PB1
    mov r24, r18
    bst r27, 2
    bld r24, PB1
    mov r25, r18
    bst r27, 1
    bld r25, PB1
    mov r26, r18
    bst r27, 0
    bld r26, PB1

    /* Port of ATmega1284P edgefix_v4: drive on FALL, host samples RISE.
     * Keep final bit driven until /EN is released by the caller. */
    WAIT_LOW
    out _SFR_IO_ADDR(DDRB), r19
    WAIT_HIGH
    WAIT_LOW
    out _SFR_IO_ADDR(DDRB), r20
    WAIT_HIGH
    WAIT_LOW
    out _SFR_IO_ADDR(DDRB), r21
    WAIT_HIGH
    WAIT_LOW
    out _SFR_IO_ADDR(DDRB), r22
    WAIT_HIGH
    WAIT_LOW
    out _SFR_IO_ADDR(DDRB), r23
    WAIT_HIGH
    WAIT_LOW
    out _SFR_IO_ADDR(DDRB), r24
    WAIT_HIGH
    WAIT_LOW
    out _SFR_IO_ADDR(DDRB), r25
    WAIT_HIGH
    WAIT_LOW
    out _SFR_IO_ADDR(DDRB), r26
    WAIT_HIGH
    ret
    .size fast_send_next, .-fast_send_next

    .global fast_wait_en_high
    .type fast_wait_en_high, @function
fast_wait_en_high:
.Lwait_en_high:
    sbis _SFR_IO_ADDR(PINB), PB0
    rjmp .Lwait_en_high
    cbi _SFR_IO_ADDR(DDRB), PB1
    ret
    .size fast_wait_en_high, .-fast_wait_en_high
