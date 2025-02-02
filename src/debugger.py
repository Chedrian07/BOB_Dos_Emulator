# debugger.py

import threading
import time

class Debugger:
    """
    간단한 명령어 단위 디버거.
    CPU를 별도 스레드로 돌리되, Next 요청 시 단일 스텝 실행,
    Go 요청 시 계속 실행, Stop 요청 시 중단.
    """

    def __init__(self, cpu):
        self.cpu = cpu
        self.running = False
        self.single_step_mode = False
        self.thread = None

    def debugger_loop(self):
        while self.running:
            if self.single_step_mode:
                # 단일 스텝
                try:
                    self.cpu.step()
                except Exception as e:
                    print(f"[Debugger] CPU Exception: {e}")
                    self.cpu.running = False
                    self.running = False
            else:
                # 계속 실행
                try:
                    self.cpu.step()
                except Exception as e:
                    print(f"[Debugger] CPU Exception: {e}")
                    self.cpu.running = False
                    self.running = False

            # 너무 빠른 루프를 약간 쉬어줌
            time.sleep(0.0001)

    def start(self):
        if not self.running:
            self.running = True
            self.cpu.running = True
            self.thread = threading.Thread(target=self.debugger_loop, daemon=True)
            self.thread.start()

    def stop(self):
        # CPU 정지
        self.running = False
        self.cpu.running = False
        if self.thread:
            self.thread.join()

    def go(self):
        self.single_step_mode = False

    def next(self):
        self.single_step_mode = True

    def print_cpu_state(self):
        print(f"EAX={self.cpu.EAX:08X} EBX={self.cpu.EBX:08X} "
              f"ECX={self.cpu.ECX:08X} EDX={self.cpu.EDX:08X}")
        print(f"CS={self.cpu.CS:04X} IP={self.cpu.EIP:04X} FLAGS={self.cpu.EFLAGS:08X}")