#include "bios.h"
#include <string.h>
#include <stdio.h>

void initBIOS(BIOS *bios) {
    bios->entry_count = 0;
    memset(bios->entries, 0, sizeof(bios->entries));
    printf("BIOS 초기화 완료\n");
}

void addE820Entry(BIOS *bios, uint64_t base, uint64_t length, uint32_t type) {
    if (bios->entry_count < MAX_E820_ENTRIES) {
        bios->entries[bios->entry_count].base = base;
        bios->entries[bios->entry_count].length = length;
        bios->entries[bios->entry_count].type = type;
        bios->entry_count++;
        printf("E820 Entry 추가: base=0x%llX, length=0x%llX, type=%u\n",
               (unsigned long long)base, (unsigned long long)length, type);
    } else {
        printf("E820 Entry 테이블이 가득 찼습니다.\n");
    }
}