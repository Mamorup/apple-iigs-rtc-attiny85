# References and attribution

- [Phil Greenland / ATTinyRTC](https://github.com/pgreenland/attinyrtc): original
  MIT-licensed RTC/PRAM protocol logic and source inspiration; copyright 2022
  Phil Greenland is preserved in LICENSE. The upstream project targets Mac
  SE/30 at 250 kHz and itself credits earlier RTC work. This IIgs front end
  addresses a different, measured clock of approximately 2 MHz.
- [ATtiny25/45/85 official datasheet](https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ProductDocuments/DataSheets/Atmel-2586-AVR-8-bit-Microcontroller-ATtiny25-ATtiny45-ATtiny85_Datasheet.pdf): pinout,
  PLL clock selection, fuse bits, RSTDISBL/HV serial programming and electrical
  conditions. CKSEL 0001 selects nominal 16 MHz. Extended fuse bit 0 is SELFPRGEN.
- [Inside Macintosh Volume III](https://vintageapple.org/inside_o/pdf/Inside_Macintosh_Volume_III_1985.pdf): clock/parameter RAM background. Macintosh protocol/timing must not be
  assumed identical to the measured IIgs bus without checking.
- [Apple IIgs Hardware Reference](https://downloads.reactivemicro.com/Apple%20II%20Items/Documentation/Manuals/IIgs/IIgs%20Hardware%20Reference.pdf): machine-level clock/PRAM interface context.
- The IIgs serial implementation also used the working ATmega RTC development
  edgefix timing as a reference. Raw captures and third-party manuals are not
  distributed in this repository.

The AVR compiler/avr-libc/binutils are external build dependencies and retain
their own licenses. They are not vendored here.
