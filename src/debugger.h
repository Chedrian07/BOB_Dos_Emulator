#ifndef DEBUGGER_H
#define DEBUGGER_H

#include "cpu.h"
#include <stddef.h>

typedef enum {
DEBUG_STOP,
DEBUG_NEXT,
DEBUG_GO
} DebugCommand;

void debuggerLoop(CPUState *cpu, uint8_t *memory, size_t mem_size);

#endif  // DEBUGGER_H
