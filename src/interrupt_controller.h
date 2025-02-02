#ifndef INTERRUPT_CONTROLLER_H
#define INTERRUPT_CONTROLLER_H

#include <stdint.h>

typedef enum {
INT_TYPE_HARDWARE,
INT_TYPE_SOFTWARE,
INT_TYPE_VIRTUAL
} InterruptType;

typedef struct {
InterruptType type;
uint8_t number;
uint8_t priority;
} Interrupt;

#define INTERRUPT_QUEUE_SIZE 256

typedef struct {
Interrupt queue[INTERRUPT_QUEUE_SIZE];
int head;
int tail;
} InterruptController;

void initInterruptController(InterruptController *ic);
int enqueueInterrupt(InterruptController *ic, Interrupt intr);
int dequeueInterrupt(InterruptController *ic, Interrupt *intr);

#endif  // INTERRUPT_CONTROLLER_H
