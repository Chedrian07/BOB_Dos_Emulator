#ifndef VIRTUAL_STORAGE_H
#define VIRTUAL_STORAGE_H

#include <stdint.h>
#include <stddef.h>
#include <stdio.h>

typedef struct {
uint16_t cylinders;
uint8_t heads;
uint8_t sectors;
FILE *image;
} VirtualStorage;

int initVirtualStorage(VirtualStorage *storage, const char *imagePath);
int readSector(VirtualStorage *storage, uint32_t cylinder, uint32_t head, uint32_t sector, void *buffer, size_t size);
int writeSector(VirtualStorage *storage, uint32_t cylinder, uint32_t head, uint32_t sector, const void *buffer, size_t size);

#endif  // VIRTUAL_STORAGE_H
