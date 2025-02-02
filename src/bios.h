#ifndef BIOS_H
#define BIOS_H

#include <stdint.h>

typedef struct {
uint64_t base;
uint64_t length;
uint32_t type;  // 1: 사용 가능, 2: 예약 등
} E820Entry;

#define MAX_E820_ENTRIES 16

typedef struct {
E820Entry entries[MAX_E820_ENTRIES];
int entry_count;
} BIOS;

void initBIOS(BIOS *bios);
void addE820Entry(BIOS *bios, uint64_t base, uint64_t length, uint32_t type);

#endif  // BIOS_H
