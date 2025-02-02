#include "cpu.h"
#include <stdio.h>
#include <stddef.h>


void initCPU(CPUState *cpu) {
for (int i = 0; i < NUM_REGISTERS; i++)
cpu->regs[i] = 0;
cpu->eip = 0;
cpu->eflags = 0;
printf("CPU 초기화 완료\n");
}

void executeInstruction(CPUState *cpu, uint8_t *memory, size_t mem_size) {
if (cpu->eip >= mem_size) {
printf("EIP가 메모리 범위를 초과했습니다.\n");
return;
}
uint8_t opcode = memory[cpu->eip];
switch (opcode) {
case 0x90:
cpu->eip++;
break;
default:
printf("알 수 없는 opcode: 0x%02X at EIP=0x%08X\n", opcode, cpu->eip);
cpu->eip++;
break;
}
}

void handleInterrupt(CPUState *cpu, uint8_t intNumber) {
printf("인터럽트 발생: %d\n", intNumber);
cpu->eip = 0;
}
