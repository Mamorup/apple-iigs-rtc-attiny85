#pragma once
#include <stdint.h>
#include <string.h>
#define EEMEM
static inline void eeprom_read_block(void *dst,const void *src,size_t n){memcpy(dst,src,n);}
static inline uint32_t eeprom_read_dword(const uint32_t *src){return *src;}
