// dos_sandbox/src/main.c

#include <stdio.h>
#include <stdlib.h>
#include <SDL2/SDL.h>

#include "bios.h"
#include "cpu.h"
#include "debugger.h"
#include "dma_controller.h"
#include "eisa_bus.h"
#include "interrupt_controller.h"
#include "timer.h"
#include "vga_graphics.h"
#include "virtual_storage.h"

#define MEMORY_SIZE 1024

int main(void) {
    printf("DOS Sandbox 프로젝트 시작\n");

    /* 1. 타이머 초기화 */
    Timer timer;
    initTimer(&timer);

    /* 2. 인터럽트 컨트롤러 초기화 */
    InterruptController ic;
    initInterruptController(&ic);

    /* 3. 가상 EISA 버스 컨트롤러 초기화 */
    EISABusController bus;
    initEISABus(&bus);

    /* 4. DMA 컨트롤러 초기화 */
    DMAController dma;
    initDMAController(&dma);

    /* 5. VGA 그래픽 초기화 */
    VGADisplay display;
    if (initVGADisplay(&display) != 0) {
        fprintf(stderr, "VGA 그래픽 초기화 실패\n");
        return EXIT_FAILURE;
    }

    /* 6. 가상 저장장치 초기화 (disk.img 파일) */
    VirtualStorage storage;
    if (initVirtualStorage(&storage, "disk.img") != 0) {
        fprintf(stderr, "가상 저장장치 초기화 실패\n");
        return EXIT_FAILURE;
    }

    /* 7. BIOS 초기화 */
    BIOS bios;
    initBIOS(&bios);
    // 예시: 메모리 맵 정보 추가 (사용 가능 메모리와 예약 영역)
    addE820Entry(&bios, 0x00000000, 0x0009FC00, 1);  // 사용 가능 메모리
    addE820Entry(&bios, 0x0009FC00, 0x00000400, 2);  // 예약 영역

    /* 8. CPU(i80386) 초기화 */
    CPUState cpu;
    initCPU(&cpu);

    /* 9. 테스트용 메모리 초기화 (프로그램 코드 영역) */
    uint8_t memory[MEMORY_SIZE] = {0};
    // 간단 테스트: 3회의 NOP 명령 (opcode 0x90)
    memory[0] = 0x90;  // NOP
    memory[1] = 0x90;  // NOP
    memory[2] = 0x90;  // NOP

    /* 10. 디버거 루프를 통해 CPU 명령어 실행 (Go/Next/Stop 기능) */
    debuggerLoop(&cpu, memory, MEMORY_SIZE);

    /* 11. 종료 처리 */
    SDL_Quit();
    printf("DOS Sandbox 종료\n");
    return EXIT_SUCCESS;
}