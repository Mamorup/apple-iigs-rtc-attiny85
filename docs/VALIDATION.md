# Validation and known limits

## Source and binary reproducibility

The published source is the development `main_edgefix_v3.c` plus
`serial_edgefix_v3.S`. A host-test-only guard suppresses the AVR CLI instruction
when compiling the C protocol tests for a desktop CPU. That guard does not
change the AVR build. With AVR GCC 7.3.0, the resulting FLASH, EEPROM and fuse
bytes match the saved development artifacts byte for byte:

| Artifact | Size | SHA256 |
|---|---|---|
|FLASH|996B|`fe3652553e711209d85684448ca82dc29c4391c01bf87ffb99377922468cdce4`|
|EEPROM section|260B|`cfe2cab5b94806e34f0bd0e4994f6ff70518997cb7b2eaacbef6ab6f616fced7`|
|Fuses|3B|`5e1781c80d3b878076e1c078990c984f825d5f6133e4b9ce7fdcd40b67a1a9cd`|

BSS is 262 B. FLASH HEX exports only .text/.data; EEPROM and fuses are separate.
`tools/verify_images.py` checks Intel HEX record checksums/addressing, exact
HEX/BIN equality, T48 padding, fuse values and SHA256 manifests.

## Protocol tests

`tests/protocol_test.c` includes the actual firmware C with desktop AVR
register/EEPROM stubs. It tests clock register aliases, regular write protect,
all 256 extended PRAM addresses, independent extended writes, open-drain output
latches, timer fraction/32-bit rollover and fuse constants. It does NOT
execute the serial assembler or prove electrical timing.

## Serial timing model

The serial front end is a port of the development ATmega edgefix timing:
receive after detecting CLK LOW then HIGH; install output DATA after FALL;
hold the last bit until /EN HIGH, then release DATA. At 16 MHz there are only
about 8 CPU cycles per 2 MHz RTC clock period.

A historical replay of 1746 complete two-byte transactions from a private
capture used an **assumed 100 MHz** analyzer rate. It evaluated 89046 phase/
frequency combinations at 14/16/18 MHz core clocks and reported no failures,
with minimum modeled TX setup 351.57 ns. This is a simplified instruction-
timing model, not complete AVR execution or measured open-drain rise time.
Its 100-cycle C dispatch allowance is an assumption, not a bound for all
extended transactions. Do not apply that result to a differently sampled
file without specifying its actual sample rate.

## Hardware context

During the IIgs repair, the ATtiny85 replacement produced the1SEC signal and
the complete machine eventually displayed System Good with the separate RTC
installed. This does not establish exhaustive qualification of every RTC
command, silicon sample, supply voltage, oscillator phase, or compiler build.
The installed chip was not freshly read back as part of preparing this
repository. No claim of a new hardware programming/test session is made here.

## Important limitations

- Runtime time/PRAM changes stay in SRAM. No runtime EEPROM writer exists.
  Complete power loss reloads the initial EEPROM seed and fixed time value.
- Internal RC/PLL accuracy is not a precision crystal reference. Battery
  operation, retention and long-term clock drift are not qualified.
- Timer flags are polled while idle. Missed ticks under prolonged bus activity
  are not reconstructed as a precision elapsed-time counter.
- Malformed/aborted transactions can leave tight edge-wait loops waiting.
  General bus timeouts/recovery are not implemented; the ATtiny watchdog is disabled.
- Earlier slow/fast/debug/A5-test firmware and the old Digispark dump are not
  published as recommended images. Use this edgefix_v3 image set consistently.
