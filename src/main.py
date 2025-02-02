# main.py

import sys
import time

from memory import Memory
from interrupt_controller import InterruptController
from timer import TimerDevice
from eisa_bus import EISABus
from dma_controller import DMAController
from video_device import VideoDevice
from storage_device import IDEHardDisk
from bios import BIOS
from cpu import CPU
from debugger import Debugger

def main():
    # 1) 메모리 생성 (16MB)
    mem = Memory(0x1000000)

    # 2) 인터럽트 컨트롤러
    ic = InterruptController()

    # 3) EISA 버스
    eisa = EISABus()

    # 4) DMA 컨트롤러
    dma = DMAController(mem, ic)

    # 5) 가상 저장장치 (IDE 하드)
    disk = IDEHardDisk(disk_image_path="disk.img", cylinders=16, heads=16, sectors=63)
    # EISA 버스에 포트 매핑
    for p in range(0x1F0, 0x1F8):
        eisa.register_io_device(p, disk)

    # 6) BIOS
    bios = BIOS(mem, disk)
    bios.load_bios()
    # e820 등 추가 세팅 필요 시 bios.setup_e820_map()

    # 7) CPU
    cpu = CPU(mem, ic)

    # 8) Timer (IRQ0 발생)
    timer = TimerDevice(ic, frequency_hz=1000)
    timer.start()

    # 9) Video Device (VGA)
    video = VideoDevice(mem)
    video.start()

    # 10) Debugger
    dbg = Debugger(cpu)
    dbg.start()

    print("===== My DOS x86 Emulator Started =====")
    print("Commands: g=go, n=next, s=stop, r=regs, q=quit")

    # 간단한 명령어 루프
    while True:
        cmd = input("> ").strip()
        if cmd == "g":
            dbg.go()
        elif cmd == "n":
            dbg.next()
        elif cmd == "s":
            dbg.stop()
        elif cmd == "r":
            dbg.print_cpu_state()
        elif cmd == "q":
            dbg.stop()
            video.stop()
            timer.stop()
            break
        else:
            print("Unknown command")

    print("Emulator terminated.")

if __name__ == "__main__":
    main()
