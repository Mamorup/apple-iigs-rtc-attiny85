#pragma once
#include <stdint.h>
struct test_fuses {uint8_t low,high,extended;};
#define FUSES const struct test_fuses test_fuse_bytes
