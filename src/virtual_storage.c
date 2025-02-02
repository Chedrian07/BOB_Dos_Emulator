#include "virtual_storage.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#define SECTOR_SIZE 512

int initVirtualStorage(VirtualStorage *storage, const char *imagePath) {
    storage->cylinders = 1024;
    storage->heads = 16;
    storage->sectors = 63;

    storage->image = fopen(imagePath, "r+b");
    if (!storage->image) {
        storage->image = fopen(imagePath, "w+b");
        if (!storage->image) {
            perror("가상 저장장치 파일 열기 실패");
            return -1;
        }
        size_t disk_size = (size_t)storage->cylinders * storage->heads * storage->sectors * SECTOR_SIZE;
        void *zero = calloc(1, disk_size);
        fwrite(zero, 1, disk_size, storage->image);
        free(zero);
        fflush(storage->image);
    }
    printf("가상 저장장치 초기화 완료 (파일: %s)\n", imagePath);
    return 0;
}

int readSector(VirtualStorage *storage, uint32_t cylinder, uint32_t head, uint32_t sector, void *buffer, size_t size) {
    if (size < SECTOR_SIZE) return -1;
    uint32_t lba = (cylinder * storage->heads + head) * storage->sectors + (sector - 1);
    fseek(storage->image, lba * SECTOR_SIZE, SEEK_SET);
    size_t read = fread(buffer, 1, SECTOR_SIZE, storage->image);
    return (read == SECTOR_SIZE) ? 0 : -1;
}

int writeSector(VirtualStorage *storage, uint32_t cylinder, uint32_t head, uint32_t sector, const void *buffer, size_t size) {
    if (size < SECTOR_SIZE) return -1;
    uint32_t lba = (cylinder * storage->heads + head) * storage->sectors + (sector - 1);
    fseek(storage->image, lba * SECTOR_SIZE, SEEK_SET);
    size_t written = fwrite(buffer, 1, SECTOR_SIZE, storage->image);
    fflush(storage->image);
    return (written == SECTOR_SIZE) ? 0 : -1;
}
