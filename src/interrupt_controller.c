#include "interrupt_controller.h"
#include <string.h>

void initInterruptController(InterruptController *ic) {
    ic->head = 0;
    ic->tail = 0;
    memset(ic->queue, 0, sizeof(ic->queue));
}

int enqueueInterrupt(InterruptController *ic, Interrupt intr) {
    int next = (ic->tail + 1) % INTERRUPT_QUEUE_SIZE;
    if (next == ic->head) {
        return -1;
    }
    ic->queue[ic->tail] = intr;
    ic->tail = next;
    return 0;
}

int dequeueInterrupt(InterruptController *ic, Interrupt *intr) {
    if (ic->head == ic->tail) {
        return -1;
    }
    *intr = ic->queue[ic->head];
    ic->head = (ic->head + 1) % INTERRUPT_QUEUE_SIZE;
    return 0;
}
