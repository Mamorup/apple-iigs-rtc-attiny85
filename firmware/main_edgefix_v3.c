/*
 * Apple IIgs 343-0042-B RTC/PRAM emulator for ATtiny85.
 * ATmega1284P edgefix_v4 serial timing port: rising RX, falling TX.
 * Protocol logic derived from Phil Greenland's MIT-licensed ATTinyRTC.
 */
#include <stdint.h>
#include <stdbool.h>
#include <avr/io.h>
#include <avr/eeprom.h>
#include <avr/wdt.h>
#include <avr/fuse.h>

#define F_CPU 16000000UL
#define PRAM_SIZE 256
#define INITIAL_SECONDS UINT32_C(0xE6E1C7F5)

FUSES = {
    .low = 0xE1,
    .high = 0x5D,
    .extended = 0xFF
};

/* r25:r24: high byte 0 = command in low byte; high byte 1 = timer event. */
extern uint16_t fast_wait_first(void);
extern uint8_t fast_recv_next(void);
extern void fast_send_next(uint8_t value);
extern void fast_wait_en_high(void);

typedef union {
    uint32_t value;
    uint8_t byte[4];
} seconds_t;

static uint8_t EEMEM stored_pram[PRAM_SIZE] = {0};
static uint32_t EEMEM stored_seconds = INITIAL_SECONDS;

static uint8_t pram[PRAM_SIZE];
static seconds_t seconds;
static bool write_protected = false;
static uint8_t timer_fraction;

static inline bool is_extended(uint8_t command) {
    return (command & 0x78u) == 0x38u;
}

static inline bool is_write(uint8_t command) {
    return (command & 0x80u) == 0;
}

static inline uint8_t base_address(uint8_t command) {
    return (command & 0x7Cu) >> 2;
}

static inline uint8_t extended_address(uint8_t command, uint8_t extension) {
    return (uint8_t)(((command & 0x07u) << 5) | ((extension & 0x7Cu) >> 2));
}

static uint8_t regular_read(uint8_t command) {
    uint8_t address = base_address(command);
    if (address <= 0x07u) {
        return seconds.byte[address & 0x03u];
    }
    if ((address >= 0x08u && address <= 0x0Bu) ||
        (address >= 0x10u && address <= 0x1Fu)) {
        return pram[address];
    }
    return 0xFFu;
}

static void regular_write(uint8_t command, uint8_t data) {
    uint8_t address = base_address(command);
    if (write_protected && address != 0x0Du) {
        return;
    }
    if (address <= 0x07u) {
        seconds.byte[address & 0x03u] = data;
    } else if (address == 0x0Du) {
        write_protected = (data & 0x80u) != 0;
    } else if ((address >= 0x08u && address <= 0x0Bu) ||
               (address >= 0x10u && address <= 0x1Fu)) {
        pram[address] = data;
    }
}

static inline uint8_t extended_read(uint8_t command, uint8_t extension) {
    return pram[extended_address(command, extension)];
}

static inline void extended_write(uint8_t command, uint8_t extension, uint8_t data) {
    /* 343-0042-B extended PRAM writes are independent of regular WP. */
    pram[extended_address(command, extension)] = data;
}

static void timer_init(void) {
    /* 16 MHz / 1024 / 125 = 125 Hz; no interrupt, flag is polled. */
    TCCR0A = _BV(WGM01);
    TCCR0B = _BV(CS02) | _BV(CS00);
    OCR0A = 124;
    TIMSK = 0;
    TIFR = _BV(OCF0A);
}

static inline void timer_service(void) {
    TIFR = _BV(OCF0A);
    timer_fraction = (uint8_t)(timer_fraction + 2u);
    if (timer_fraction >= 125u) {
        timer_fraction = (uint8_t)(timer_fraction - 125u);
        DDRB ^= _BV(PB5);              /* open-drain 1SEC */
        if (DDRB & _BV(PB5)) {
            seconds.value++;
        }
    }
}

static void hardware_init(void) {
    MCUSR = 0;
    wdt_disable();
    ACSR |= _BV(ACD);
    PRR |= _BV(PRTIM1) | _BV(PRUSI) | _BV(PRADC);

    /* PB0=/EN, PB1=DATA, PB2=CLK inputs. PB1/PB5 open-drain outputs. */
    PORTB &= (uint8_t)~(_BV(PB1) | _BV(PB5));
    DDRB &= (uint8_t)~(_BV(PB0) | _BV(PB1) | _BV(PB2) | _BV(PB5));
    GIMSK = 0;
    PCMSK = 0;
    timer_init();
}

int main(void) {
#ifndef RTC_HOST_TEST
    __asm__ __volatile__("cli" ::: "memory");
#endif
    hardware_init();
    eeprom_read_block(pram, stored_pram, sizeof(pram));
    seconds.value = eeprom_read_dword(&stored_seconds);
    if (seconds.value == UINT32_MAX) {
        seconds.value = INITIAL_SECONDS;
    }

    for (;;) {
        uint16_t event = fast_wait_first();
        if ((uint8_t)(event >> 8) != 0) {
            timer_service();
            continue;
        }

        uint8_t command = (uint8_t)event;
        if (is_extended(command)) {
            uint8_t extension = fast_recv_next();
            if (is_write(command)) {
                uint8_t data = fast_recv_next();
                extended_write(command, extension, data);
            } else {
                fast_send_next(extended_read(command, extension));
            }
        } else if (is_write(command)) {
            regular_write(command, fast_recv_next());
        } else {
            fast_send_next(regular_read(command));
        }

        fast_wait_en_high();
    }
}
