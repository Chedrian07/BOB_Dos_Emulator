#include "timer.h"

void initTimer(Timer *timer) {
timer->tick_count = 0;
}

void tickTimer(Timer *timer) {
timer->tick_count++;
}

uint64_t getTickCount(const Timer *timer) {
return timer->tick_count;
}
