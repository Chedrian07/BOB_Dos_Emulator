# main.py

import time
import sdl2.ext

from memory import Memory
from interrupt_controller import InterruptController
from timer import TimerDevice
from eisa_bus import EISABus
from dma_controller import DMAController
from storage_device import IDEHardDisk
from bios import BIOS
from cpu import CPU
from debugger import Debugger
from video_device import VideoDevice

from console_thread import ConsoleThread

def main():
    # 1) 메모리
    mem = Memory(0x1000000)

    # 2) 인터럽트 컨트롤러
    ic = InterruptController()

    # 3) EISA 버스
    eisa = EISABus()

    # 4) DMA
    dma = DMAController(mem, ic)

    # 5) IDE 디스크
    disk = IDEHardDisk("disk.img", cylinders=16, heads=16, sectors=63)
    for p in range(0x1F0, 0x1F8):
        eisa.register_io_device(p, disk)

    # 6) BIOS
    bios = BIOS(mem, disk)
    bios.load_bios()

    # 7) CPU
    cpu = CPU(mem, ic)

    # 8) 타이머 (IRQ0)
    timer = TimerDevice(ic, frequency_hz=1000)
    timer.start()

    # 9) 비디오 (메인 스레드에서만 update_frame())
    video = VideoDevice(mem)

    # 10) 디버거
    dbg = Debugger(cpu)

    # 11) 콘솔 입력 스레드
    cthread = ConsoleThread()
    cthread.start()

    print("===== My DOS x86 Emulator (macOS-safe) Started =====")
    print("Commands (in console): g=go, n=next, s=stop, r=regs, q=quit")

    running = True
    stopped = False  # s=stop -> CPU 실행 중단

    while running:
        # 1) 콘솔에서 명령 큐 확인
        cmd = cthread.get_command_nowait()
        while cmd is not None:
            if cmd == "g":
                stopped = False
                dbg.go()
            elif cmd == "n":
                stopped = False
                dbg.next()
            elif cmd == "s":
                stopped = True
            elif cmd == "r":
                dbg.print_cpu_state()
            elif cmd == "q":
                running = False
            else:
                print(f"Unknown command: {cmd}")
            cmd = cthread.get_command_nowait()

        # 2) CPU 실행
        if not stopped:
            try:
                dbg.step_cpu_once()  # single_step_mode? => 단일 or 연속 스텝
            except Exception as e:
                print(f"[CPU Exception] {e}")
                stopped = True

        # 3) 비디오 갱신 (메인 스레드에서 SDL 사용)
        video.update_frame()

        # 4) 루프 간 약간 쉼
        time.sleep(0.01)

    print("Stopping...")

    # 종료 처리
    cthread.stop()
    timer.stop()
    sdl2.ext.quit()
    print("Emulator terminated.")

if __name__ == "__main__":
    main()