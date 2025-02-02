# cpu.py

from interrupt_controller import InterruptController
from memory import Memory

FLAG_CF = 1 << 0
FLAG_ZF = 1 << 6
FLAG_IF = 1 << 9
FLAG_SF = 1 << 7
FLAG_OF = 1 << 11

class CPU:
    """
    i80386 리얼모드 기반 간단 CPU.
    일부 명령어만 구현 (JMP, INT, MOV AX, ADD AX, CALL/RET, etc.)
    """

    def __init__(self, memory: Memory, ic: InterruptController):
        self.mem = memory
        self.ic = ic

        self.EAX = 0
        self.EBX = 0
        self.ECX = 0
        self.EDX = 0
        self.ESI = 0
        self.EDI = 0
        self.EBP = 0
        self.ESP = 0

        self.CS = 0xF000
        self.DS = 0
        self.ES = 0
        self.FS = 0
        self.GS = 0
        self.SS = 0

        self.EIP = 0xFFF0
        self.EFLAGS = 0x00000002  # IF=0, Reserved=1

        self.running = True

    def get_flags(self):
        return self.EFLAGS

    def set_flag_if(self, val: bool):
        if val:
            self.EFLAGS |= FLAG_IF
        else:
            self.EFLAGS &= ~FLAG_IF

    def real_mode_address(self, seg, off):
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

    def push16(self, value):
        self.ESP = (self.ESP - 2) & 0xFFFF
        addr = self.real_mode_address(self.SS, self.ESP)
        self.mem.write16(addr, value)

    def pop16(self):
        addr = self.real_mode_address(self.SS, self.ESP)
        val = self.mem.read16(addr)
        self.ESP = (self.ESP + 2) & 0xFFFF
        return val

    def step(self):
        # IF=1이면 IRQ 체크
        if (self.get_flags() & FLAG_IF) != 0 and self.ic:
            pend = self.ic.get_pending_interrupt()
            if pend is not None:
                self.handle_interrupt(pend)
                return

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
            # ZF, SF, CF, OF 설정 예시
            if result == 0:
                self.EFLAGS |= FLAG_ZF
            else:
                self.EFLAGS &= ~FLAG_ZF
            if (result & 0x8000) != 0:
                self.EFLAGS |= FLAG_SF
            else:
                self.EFLAGS &= ~FLAG_SF
            if (ax + imm16) > 0xFFFF:
                self.EFLAGS |= FLAG_CF
            else:
                self.EFLAGS &= ~FLAG_CF
            signed_ax = (ax if ax < 0x8000 else ax - 0x10000)
            signed_imm = (imm16 if imm16 < 0x8000 else imm16 - 0x10000)
            signed_res = signed_ax + signed_imm
            # 16비트 범위 확인
            if -(1 << 15) <= signed_res < (1 << 15):
                self.EFLAGS &= ~FLAG_OF
            else:
                self.EFLAGS |= FLAG_OF

        elif op == 0xE8:
            # CALL rel16
            disp16 = self.fetch16()
            next_ip = self.EIP
            self.push16(next_ip)
            signed_disp = (disp16 if disp16 < 0x8000 else disp16 - 0x10000)
            self.EIP = (self.EIP + signed_disp) & 0xFFFF

        elif op == 0xC3:
            # RET
            ret_ip = self.pop16()
            self.EIP = ret_ip

        else:
            # 미구현
            raise Exception(f"Unimplemented opcode 0x{op:02X} at CS:IP={self.CS:04X}:{(self.EIP-1)&0xFFFF:04X}")

    def handle_interrupt(self, int_num):
        # push FLAGS, CS, IP
        self.push16(self.EFLAGS & 0xFFFF)
        self.set_flag_if(False)
        self.push16(self.CS)
        self.push16(self.EIP)

        # IVT lookup (4바이트)
        vector_addr = int_num * 4
        ip = self.mem.read16(vector_addr)
        cs = self.mem.read16(vector_addr+2)

        self.CS = cs
        self.EIP = ip