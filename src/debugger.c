#include "debugger.h"
#include "cpu.h"
#include <stdio.h>
#include <string.h>

static void printCPUState(const CPUState *cpu) {
    printf("----- CPU 상태 -----\n");
    printf("EIP: 0x%08X, EFLAGS: 0x%08X\n", cpu->eip, cpu->eflags);
    for (int i = 0; i < NUM_REGISTERS; i++) {
        printf("R%d: 0x%08X ", i, cpu->regs[i]);
    }
    printf("\n---------------\n");
}

void debuggerLoop(CPUState *cpu, uint8_t *memory, size_t mem_size) {
    char input[64];
    DebugCommand cmd = DEBUG_STOP;
    while (1) {
        printf("디버거 명령 입력 (go, next, stop, state): ");
        if (fgets(input, sizeof(input), stdin) == NULL)
            break;
        if (strncmp(input, "go", 2) == 0) {
            cmd = DEBUG_GO;
        } else if (strncmp(input, "next", 4) == 0) {
            cmd = DEBUG_NEXT;
        } else if (strncmp(input, "stop", 4) == 0) {
            cmd = DEBUG_STOP;
        } else if (strncmp(input, "state", 5) == 0) {
            printCPUState(cpu);
            continue;
        } else {
            printf("알 수 없는 명령\n");
            continue;
        }

        if (cmd == DEBUG_NEXT) {
            executeInstruction(cpu, memory, mem_size);
            printCPUState(cpu);
        } else if (cmd == DEBUG_GO) {
            for (int i = 0; i < 1000; i++) {
                executeInstruction(cpu, memory, mem_size);
            }
            printCPUState(cpu);
        } else if (cmd == DEBUG_STOP) {
            printf("디버거 중단\n");
            break;
        }
    }
}
