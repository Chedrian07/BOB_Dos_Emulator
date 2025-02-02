#ifndef TIMER_H
#define TIMER_H

#include <stdint.h>

typedef struct {
uint64_t tick_count;
} Timer;

void initTimer(Timer *timer);
void tickTimer(Timer *timer);
uint64_t getTickCount(const Timer *timer);

#endif  // TIMER_H
