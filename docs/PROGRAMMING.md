# Programming with T48 / Xgpro

1. Remove the ATtiny85 from the IIgs and put it in the correct programmer
   socket/adapter. Select ATtiny85 and the actual DIP8/SOIC8 package.
2. Load `releases/edgefix_v3/t48_flash_8k.bin` into **FLASH** as **Binary**, address 0.
3. Load `t48_eeprom_512.bin` into **EEPROM** as **Binary**, address 0.
4. Erase/program and verify both memory regions using the programmer's
   ATtiny85 procedure. Do not overwrite the factory calibration byte.
5. Set/verify the final configuration bytes:

```text
LFUSE = E1
HFUSE = 5D
EFUSE = FF
LOCK  = FF
```

Set HFUSE 5D only after you have a suitable HVSP programming path. RSTDISBL is
programmed so pin 1 becomes PB5/1SEC. Ordinary ISP/USBasp reprogramming is then
unavailable; subsequent access needs high-voltage serial programming.
Never feed programming high voltage into the motherboard.

The MCU interprets programmed fuse bits as 0. Use the final byte readout rather
than guessing checkbox states. **5D and D5 are different settings.** Extended
fuse bit 0 is SELFPRGEN: FF leaves it disabled, FE enables it; that difference
is not caused by reserved bits. The source/build target is FF.

## File format mistakes to avoid

- `flash.hex` must be imported as **Intel HEX**, not Binary.
- `eeprom.eep` is also Intel HEX; load it into EEPROM, not FLASH.
- `fuses.bin` contains only 3 fuse bytes; it is not an application program.
- `eeprom_raw.bin` is 260 bytes; the T48 image pads it to 512 with FF.
- `flash.bin` is 996 bytes in the observed GCC 7.3.0 build; the T48 image pads
  it to 8192 with FF. All files start at memory address 0.
- If FLASH begins with ASCII `:100000...` / bytes `3A 31 30`, the HEX text was
  loaded as Binary. Reload using the correct format and program/verify again.
- Program the supplied EEPROM seed; an all-FF EEPROM is not that seed.

The actual EEPROM address layout is emitted by the linker. In the supplied
build, the first 4 bytes seed the seconds counter, followed by 256 PRAM bytes.
Use the EEPROM file from the same build as FLASH. Do not rearrange it by hand.

## After installation

Check supply, GND, /EN, CLK and DATA. With the chip powered and /EN idle HIGH,
pin 1 should produce approximately 1 Hz through the external pull-up.
Timekeeping accuracy depends on the RC oscillator. During IIgs accesses,
DATA must be released when /EN returns HIGH. A 1 Hz signal alone is not proof
that all RTC/PRAM commands are correct.

No flashing script is run automatically by building or running tests.
