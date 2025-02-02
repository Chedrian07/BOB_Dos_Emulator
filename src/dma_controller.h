#ifndef DMA_CONTROLLER_H
#define DMA_CONTROLLER_H

#include <stddef.h>
#include <stdint.h>

typedef struct {
uint8_t channel;
uint8_t busy;
} DMAChannel;

#define MAX_DMA_CHANNELS 4

typedef struct {
DMAChannel channels[MAX_DMA_CHANNELS];
} DMAController;

void initDMAController(DMAController *dma);
int startDMATransfer(DMAController *dma, uint8_t channel, const void *src, void *dst, size_t size);

#endif  // DMA_CONTROLLER_H
