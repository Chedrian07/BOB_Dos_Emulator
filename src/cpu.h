#ifndef CPU_H
#define CPU_H

#include <stdint.h>
#include <stddef.h>

#define NUM_REGISTERS 8

typedef struct {
uint32_t regs[NUM_REGISTERS];
uint32_t eip;
uint32_t eflags;
} CPUState;

void initCPU(CPUState *cpu);
void executeInstruction(CPUState *cpu, uint8_t *memory, size_t mem_size);
void handleInterrupt(CPUState *cpu, uint8_t intNumber);

#endif  // CPU_H
