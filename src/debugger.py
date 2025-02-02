class Debugger:
    """
    간단한 디버거:
    - single_step_mode = True면 한 번에 1명령어만 실행
    - False면 여러 번(연속) 실행
    - print_cpu_state() 등
    """

    def __init__(self, cpu):
        self.cpu = cpu
        self.single_step_mode = False

    def go(self):
        """계속 실행"""
        self.single_step_mode = False

    def next(self):
        """단일 스텝 모드"""
        self.single_step_mode = True

    def step_cpu_once(self):
        """
        single_step_mode=True => 한 번만 step
        single_step_mode=False => 여러 번 step
        """
        if self.single_step_mode:
            # 명령어 1번만 실행
            self.cpu.step()
        else:
            # 연속 실행 → 너무 빨라지지 않도록 1000 스텝 정도만
            for _ in range(1000):
                self.cpu.step()

    def print_cpu_state(self):
        print(f"EAX={self.cpu.EAX:08X}")
        print(f"CS={self.cpu.CS:04X} IP={self.cpu.EIP:04X} EFLAGS={self.cpu.EFLAGS:08X}")