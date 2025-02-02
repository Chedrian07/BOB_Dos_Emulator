#include "eisa_bus.h"
#include <string.h>
#include <stdio.h>

void initEISABus(EISABusController *bus) {
    bus->device_count = 0;
    memset(bus->devices, 0, sizeof(bus->devices));
}

int registerDevice(EISABusController *bus, Device device) {
    if (bus->device_count >= MAX_DEVICES)
        return -1;
    bus->devices[bus->device_count++] = device;
    printf("장치 등록: type=%d, port=0x%X\n", device.type, device.port_base);
    return 0;
}

int sendSignal(EISABusController *bus, DeviceType type, uint8_t signal) {
    for (int i = 0; i < bus->device_count; i++) {
        if (bus->devices[i].type == type) {
            printf("장치(type=%d)로 신호 전달: signal=0x%X\n", type, signal);
            return 0;
        }
    }
    return -1;
}
