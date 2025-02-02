#ifndef EISA_BUS_H
#define EISA_BUS_H

#include <stdint.h>

typedef enum {
DEVICE_KEYBOARD,
DEVICE_MOUSE,
DEVICE_HARDDISK
} DeviceType;

typedef struct {
DeviceType type;
uint16_t port_base;
} Device;

#define MAX_DEVICES 16

typedef struct {
Device devices[MAX_DEVICES];
int device_count;
} EISABusController;

void initEISABus(EISABusController *bus);
int registerDevice(EISABusController *bus, Device device);
int sendSignal(EISABusController *bus, DeviceType type, uint8_t signal);

#endif  // EISA_BUS_H
