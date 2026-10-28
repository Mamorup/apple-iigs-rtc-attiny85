# Apple IIgs RTC replacement on ATtiny85

[Русское описание](README.ru.md) · [Programming](docs/PROGRAMMING.md) · [Wiring](hardware/WIRING.md)

An experimental replacement for the Apple IIgs **343-0042-B RTC/PRAM** using
an ATtiny85. This repository publishes the **edgefix_v3** adaptation developed
during a ROM01 IIgs repair, with a cycle-sensitive AVR assembler serial front
end for the measured IIgs RTC clock of approximately 2 MHz.

Maintainer / hardware bring-up: [Mamorup](https://github.com/Mamorup).
Protocol logic is derived from **Phil Greenland's
[ATTinyRTC](https://github.com/pgreenland/attinyrtc)** under its MIT license;
the original copyright/license is preserved in [LICENSE](LICENSE).
The Mac SE/30 project is credited upstream; its firmware should not be assumed
interchangeable with this IIgs adaptation.

## Status

The RTC replacement was used during the IIgs bring-up where the 1 Hz output
was observed and full-machine **System Good** was obtained. The published
FLASH, EEPROM and fuse bytes reproduce the saved edgefix_v3 artifacts exactly
with AVR GCC 7.3.0. This is a development prototype, not a qualification claim
for all motherboards, clock tolerances or battery configurations.

**Runtime PRAM/time writes are held in SRAM only. They are NOT committed back
to EEPROM. A complete loss of power reloads the supplied EEPROM seed.**
The clock uses the internal RC oscillator/PLL, not a 32.768 kHz crystal; it is
not a precision RTC. See [validation and limits](docs/VALIDATION.md).

## Direct pin mapping

Numbers are ATtiny85 physical package pins, not Digispark header numbers.

| IIgs RTC/UG3 pad | Signal | ATtiny85 pin / port |
|---|---|---|
|1|1SEC, open drain|1 / PB5|
|2|Original crystal|2 / PB3, not used|
|3|Original crystal|3 / PB4, not used|
|4|GND|4|
|5|/EN|5 / PB0|
|6|DATA, bidirectional open drain|6 / PB1|
|7|CLK|7 / PB2|
|8|RTC supply|8 / VCC|

DATA and 1SEC require the motherboard pull-ups. No external crystal is used.
Check package orientation/pin 1 and supply voltage; nominal 5 V operation is the
development target. A battery/low-voltage implementation is not qualified.
See [hardware/WIRING.md](hardware/WIRING.md).

## Programming files

Use the [edgefix_v3 release folder](releases/edgefix_v3/).

| File | Memory / format |
|---|---|
| `t48_flash_8k.bin` | FLASH, Binary, address 0; 8 KiB with unused space FF |
| `t48_eeprom_512.bin` | EEPROM, Binary, address 0; 512 B with unused space FF |
| `flash.hex` | FLASH, Intel HEX; contains only code/data, no fuse records |
| `eeprom.eep` | EEPROM, Intel HEX |
| `flash.bin` / `eeprom_raw.bin` | Unpadded raw sections, 996 B / 260 B |
| `fuses.bin` | Fuse bytes only; do not load into FLASH |

Fuse settings:

| Setting | Value | Purpose |
|---|---|---|
| LFUSE | `0xE1` | Internal PLL divided to nominal 16 MHz; no CKDIV8 |
| HFUSE | `0x5D` | Disable external RESET so PB5/pin 1 can output1SEC |
| EFUSE | `0xFF` | SELFPRGEN disabled |
| LOCK | `0xFF` | Unlocked |

**HFUSE 5D disables ordinary ISP/USBasp access. Use an appropriate socket
HVSP programmer, such as the T48, for subsequent reprogramming. Never apply
high-voltage programming to a chip connected to the IIgs motherboard.**

Program and verify FLASH and EEPROM, then set/verify fuses. See the detailed
[T48 instructions](docs/PROGRAMMING.md). EFUSE FE is not the same as FF:
bit 0 is SELFPRGEN, not a reserved bit.

## Build

Requires Python 3 and AVR GCC/binutils/avr-libc. Linux example:

```sh
sudo apt-get install gcc-avr avr-libc binutils-avr
python3 tools/build.py
python3 tools/verify_images.py build
```

Windows: put AVR tools on PATH or pass `--toolchain` with the folder containing
avr-gcc.exe, avr-objcopy.exe and avr-size.exe. The script has no machine-specific
compiler paths and never connects to a programmer or writes fuse bits.

Observed GCC 7.3.0 build: FLASH 996 B, BSS 262 B, EEPROM 260 B, fuses E1/5D/FF.
Other compiler versions may generate different machine code/timing. Recheck
timing before treating a different build as hardware-qualified.

## Validation

```sh
python3 tests/run_tests.py
python3 tools/verify_images.py releases/edgefix_v3
```

Native tests execute the actual C protocol/timer logic with AVR HAL stubs:
time aliases, regular write protect, all 256 extended PRAM addresses, timer
rollover, open-drain register state and fuse values. They do not execute the
serial assembler or prove physical edge timing.

An optional waveform model accepts a private LA capture:

```sh
python3 -m pip install numpy
python3 tools/validate_timing.py capture.bin --sample-rate 100000000
```

The file must contain little-endian uint16 samples: bit 0=/EN, bit1=CLK,
bit2=DATA. Supply the **actual analyzer sampling rate**, not the RTC clock.
The historical model replayed 1746 two-byte transactions at an assumed 100 MHz
capture rate, 89046 phase/frequency cases, with no modeled failures. Its
dispatch-time assumptions and scope are documented in [docs/VALIDATION.md](docs/VALIDATION.md).
Large analyzer files and proprietary manuals are not bundled.

## Related project

[Apple IIgs combined UI12/UI14 replacement on RP2350](https://github.com/Mamorup/apple-iigs-ui12-ui14-rp2350).
The RTC is a separate device/project; RP2350 watchdog features do not apply
to this ATtiny85 firmware. This firmware disables the ATtiny watchdog.

[References and attribution](docs/REFERENCES.md).
