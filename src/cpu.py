# cpu.py

from interrupt_controller import InterruptController
from memory import Memory

FLAG_CF = 1 << 0  # Carry
FLAG_ZF = 1 << 6  # Zero
FLAG_IF = 1 << 9  # Interrupt Enable
FLAG_SF = 1 << 7  # Sign
FLAG_OF = 1 << 11 # Overflow

class CPU:
    """
    i80386 리얼모드 기반의 간단한 CPU 에뮬레이터 예시.
    """

    def __init__(self, memory: Memory, ic: InterruptController):
        self.mem = memory
        self.ic = ic

        # 32비트 레지스터 (리얼모드라도 내부적으로 32비트를 사용)
        self.EAX = 0
        self.EBX = 0
        self.ECX = 0
        self.EDX = 0
        self.ESI = 0
        self.EDI = 0
        self.EBP = 0
        self.ESP = 0

        # 세그먼트 레지스터 (16비트)
        self.CS = 0xF000  # BIOS 리셋 벡터를 흉내내기 위해
        self.DS = 0
        self.ES = 0
        self.FS = 0
        self.GS = 0
        self.SS = 0

        # IP (Instruction Pointer) 16비트
        self.EIP = 0xFFF0

        # EFLAGS (리얼모드 초기값, IF=0이라 인터럽트 꺼져 있음이 일반적이지만 필요에 따라 조정)
        self.EFLAGS = 0x00000002  # x86에서 리셋 후 Reserved bit=1, IF=0

        # 내부 실행 상태
        self.running = True

    def get_flags(self):
        return self.EFLAGS

    def set_flags(self, newflags):
        self.EFLAGS = newflags & 0xFFFFFFFF

    def real_mode_address(self, seg, off):
        """
        리얼모드에서 물리주소 = seg*16 + off
        """
        return ((seg & 0xFFFF) << 4) + (off & 0xFFFF)

    def fetch8(self):
        addr = self.real_mode_address(self.CS, self.EIP)
        val = self.mem.read8(addr)
        self.EIP = (self.EIP + 1) & 0xFFFF
        return val

    def fetch16(self):
        low = self.fetch8()
        high = self.fetch8()
        return (high << 8) | low

    def fetch32(self):
        v0 = self.fetch8()
        v1 = self.fetch8()
        v2 = self.fetch8()
        v3 = self.fetch8()
        return (v3 << 24) | (v2 << 16) | (v1 << 8) | v0

    def push16(self, value):
        self.ESP = (self.ESP - 2) & 0xFFFF
        addr = self.real_mode_address(self.SS, self.ESP)
        self.mem.write16(addr, value)

    def pop16(self):
        addr = self.real_mode_address(self.SS, self.ESP)
        val = self.mem.read16(addr)
        self.ESP = (self.ESP + 2) & 0xFFFF
        return val

    def set_flag_zf(self, val: bool):
        if val:
            self.EFLAGS |= FLAG_ZF
        else:
            self.EFLAGS &= ~FLAG_ZF

    def set_flag_sf(self, val: bool):
        if val:
            self.EFLAGS |= FLAG_SF
        else:
            self.EFLAGS &= ~FLAG_SF

    def set_flag_cf(self, val: bool):
        if val:
            self.EFLAGS |= FLAG_CF
        else:
            self.EFLAGS &= ~FLAG_CF

    def set_flag_of(self, val: bool):
        if val:
            self.EFLAGS |= FLAG_OF
        else:
            self.EFLAGS &= ~FLAG_OF

    def step(self):
        """
        한 명령어를 디코딩하여 실행한다.
        여기서는 극히 일부 오퍼코드만 예시로 구현.
        """
        # 인터럽트 체크 (IF=1 일 때만)
        if (self.get_flags() & FLAG_IF) != 0:
            pending_int = self.ic.get_pending_interrupt()
            if pending_int is not None:
                self.handle_interrupt(pending_int)
                return  # 인터럽트 벡터로 점프 후 끝

        op = self.fetch8()

        if op == 0xEA:
            # JMP ptr16:16
            new_ip = self.fetch16()
            new_cs = self.fetch16()
            self.CS = new_cs
            self.EIP = new_ip

        elif op == 0xCD:
            # INT imm8
            int_num = self.fetch8()
            self.handle_interrupt(int_num)

        elif op == 0x90:
            # NOP
            pass

        elif op == 0xB8:
            # MOV AX, imm16
            imm16 = self.fetch16()
            self.EAX = (self.EAX & 0xFFFF0000) | imm16

        elif op == 0x05:
            # ADD AX, imm16
            imm16 = self.fetch16()
            ax = self.EAX & 0xFFFF
            result = (ax + imm16) & 0xFFFF
            self.EAX = (self.EAX & 0xFFFF0000) | result
            # 플래그 설정 예시 (ZF, SF, CF, OF)
            self.set_flag_zf(result == 0)
            self.set_flag_sf((result & 0x8000) != 0)
            # 단순 carry
            self.set_flag_cf((ax + imm16) > 0xFFFF)
            # overflow 체크(16비트 부호 연산)
            signed_ax = (ax if ax < 0x8000 else ax - 0x10000)
            signed_imm = (imm16 if imm16 < 0x8000 else imm16 - 0x10000)
            signed_res = (signed_ax + signed_imm)
            self.set_flag_of(not (-(1 << 15) <= signed_res < (1 << 15)))

        elif op == 0xE8:
            # CALL rel16
            disp16 = self.fetch16()
            next_ip = self.EIP
            self.push16(next_ip)
            # ip += disp16 (부호 확장)
            signed_disp = (disp16 if disp16 < 0x8000 else disp16 - 0x10000)
            self.EIP = (self.EIP + signed_disp) & 0xFFFF

        elif op == 0xC3:
            # RET
            ret_ip = self.pop16()
            self.EIP = ret_ip

        else:
            # 아직 구현 안 된 명령어
            # 실제로는 예외(interrupt 6 #UD) 발생
            raise Exception(f"Unimplemented opcode 0x{op:02X} at CS:IP={self.CS:04X}:{self.EIP-1:04X}")

    def handle_interrupt(self, int_num):
        """
        리얼모드 IVT(0:0 ~ 0:400)를 참조하여 세그먼트:오프셋을 가져온 뒤,
        현재 CS:IP, FLAGS를 스택에 저장 후 점프.
        """
        # push flags, CS, IP
        self.push16(self.get_flags() & 0xFFFF)  # 16비트만 push
        self.set_flag_if(False)  # 리얼모드에서는 HW interrupt 시 IF=0 클리어(마스크)
        self.push16(self.CS)
        self.push16(self.EIP)

        # IVT에서 int_num의 벡터를 읽는다
        vector_addr = int_num * 4
        ip = self.mem.read16(vector_addr)
        cs = self.mem.read16(vector_addr+2)

        self.CS = cs
        self.EIP = ip

    def run(self, max_steps=1000000):
        step_count = 0
        while self.running and step_count < max_steps:
            self.step()
            step_count += 1
