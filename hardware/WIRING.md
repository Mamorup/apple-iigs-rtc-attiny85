# RTC / UG3 wiring

ATtiny85 physical package pin numbers, top view. Check the notch/dot marking.
Do not confuse these with Digispark P0..P5 header labels.

```text
          notch
 1SEC PB5  1 | 8  VCC
 unused    2 | 7  PB2 CLK
 unused    3 | 6  PB1 DATA
 GND       4 | 5  PB0 /EN
```

| Original RTC UG3 pad | ATtiny85 physical pin | Function |
|---|---|---|
|1|1/PB5|1SEC, open drain; needs RESET-disable fuse|
|2|2/PB3|Not used; original crystal not needed|
|3|3/PB4|Not used; original crystal not needed|
|4|4|GND|
|5|5/PB0|Active-low /EN input|
|6|6/PB1|Bidirectional DATA, open drain|
|7|7/PB2|CLK input|
|8|8|RTC supply|

Use the motherboard pull-ups for DATA and 1SEC, common ground and a local 100 nF
VCC/GND bypass if the adapter does not already provide one. Check supply
against the actual ATtiny85's 16 MHz operating limits; nominal 5 V is the target.
Battery-voltage operation and long-term timekeeping are not qualified.

No new PCB/Gerber files are supplied. This is firmware and a direct pin map.
Remove the original RTC before connecting an active replacement.

For an isolated bench 1 Hz check, /EN must be HIGH and 1SEC needs a pull-up.
Floating /EN or a stalled transaction can leave the assembler waiting for CLK.
Do not infer that no 1 Hz waveform always means a dead chip.

Program in an external socket/adapter. Do not apply HV programming while the
chip is attached to the motherboard. An intact Digispark board has extra USB,
LED and power circuitry; that complete board is not a pin-compatible RTC.
