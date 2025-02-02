#include "dma_controller.h"
#include <string.h>
#include <stdio.h>

void initDMAController(DMAController *dma) {
memset(dma->channels, 0, sizeof(dma->channels));
}

int startDMATransfer(DMAController *dma, uint8_t channel, const void *src, void *dst, size_t size) {
if (channel >= MAX_DMA_CHANNELS) {
return -1;
}
if (dma->channels[channel].busy) {
return -2;
}
dma->channels[channel].busy = 1;
memcpy(dst, src, size);
dma->channels[channel].busy = 0;
printf("DMA 채널 %d 전송 완료 (크기: %zu 바이트)\n", channel, size);
return 0;
}
