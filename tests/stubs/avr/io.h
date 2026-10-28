#pragma once
#include <stdint.h>
#define _BV(x) (1u << (x))
enum { PB0=0, PB1=1, PB2=2, PB5=5, WGM01=1, CS02=2, CS00=0,
       OCF0A=4, ACD=7, PRTIM1=3, PRUSI=1, PRADC=0 };
extern volatile uint8_t TCCR0A,TCCR0B,OCR0A,TIMSK,TIFR,DDRB,PORTB;
extern volatile uint8_t MCUSR,ACSR,PRR,GIMSK,PCMSK;
