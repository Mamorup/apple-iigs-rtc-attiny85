/* Test the actual C protocol/timer logic with AVR register/EEPROM stubs.
 * This does not execute serial_edgefix_v3.S or model real GPIO edge timing. */
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#define RTC_HOST_TEST 1
#define main rtc_firmware_main
#include "../firmware/main_edgefix_v3.c"
#undef main
volatile uint8_t TCCR0A,TCCR0B,OCR0A,TIMSK,TIFR,DDRB,PORTB;
volatile uint8_t MCUSR,ACSR,PRR,GIMSK,PCMSK;
uint16_t fast_wait_first(void){abort();}
uint8_t fast_recv_next(void){abort();}
void fast_send_next(uint8_t value){(void)value;abort();}
void fast_wait_en_high(void){abort();}
int main(void){
    assert(test_fuse_bytes.low==0xe1 && test_fuse_bytes.high==0x5d && test_fuse_bytes.extended==0xff);
    hardware_init();
    assert((PORTB & (_BV(PB1)|_BV(PB5)))==0); /* open-drain latches stay LOW */
    assert((DDRB & (_BV(PB0)|_BV(PB1)|_BV(PB2)|_BV(PB5)))==0);
    regular_write(0x01,0x12);regular_write(0x05,0x34);
    assert(regular_read(0x81)==0x12 && regular_read(0x85)==0x34);
    assert(regular_read(0x91)==0x12); /* time register aliases */
    regular_write(0x35,0x80); /* regular write protect */
    regular_write(0x01,0x99);assert(regular_read(0x81)==0x12);
    for(unsigned i=0;i<256;i++){
        uint8_t command=0x38|(i>>5), extension=(i&31)<<2;
        assert(is_extended(command) && is_write(command));
        extended_write(command,extension,(uint8_t)(i^0xa5));
        assert(extended_read(command|0x80,extension)==(uint8_t)(i^0xa5));
    } /* extended PRAM writes are independent of regular WP */
    regular_write(0x35,0);assert(!write_protected);
    regular_write(0x41,0x5a);assert(regular_read(0xc1)==0x5a);
    assert(regular_read(0xb1)==0xff); /* reserved regular register */
    seconds.value=UINT32_MAX;timer_fraction=0;DDRB=0;
    for(unsigned i=0;i<125;i++)timer_service();
    assert(seconds.value==0 && timer_fraction==0 && !(DDRB&_BV(PB5)));
    assert(!(PORTB&(_BV(PB1)|_BV(PB5))));
    puts("PASS: raw protocol, time aliases,256-byte PRAM, write protect, open-drain state, timer/rollover and fuses");
    return 0;
}
