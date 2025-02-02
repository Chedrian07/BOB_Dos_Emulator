# debugger.py

class Debugger:
    """
    간단한 디버거:
    - single_step_mode = True면 한 번에 1명령어만 실행
    - False면 여러 번(연속) 실행
    - print_cpu_state() 등
    - 'd' 명령으로 현재 EIP부터 10줄 정도 디스어셈블 출력
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

    def disassemble_next_10(self):
        """
        현재 CPU의 CS:IP부터 최대 10개의 명령어를
        '간단히' 디스어셈블하여 출력한다.
        실제 x86 모든 opcode를 처리하진 않고,
        우리가 구현한 opcode만 간단히 문자열로 매핑한다.
        """
        old_cs = self.cpu.CS
        old_ip = self.cpu.EIP

        # 복사본을 써서 fetch8/16을 시뮬레이션
        temp_ip = old_ip

        print(f"Disassembly from {old_cs:04X}:{temp_ip:04X} ...")
        for _ in range(10):
            # 주소
            addr_str = f"{old_cs:04X}:{temp_ip:04X}"

            # opcode 한 바이트 읽기
            op_addr = self.cpu.real_mode_address(old_cs, temp_ip)
            if op_addr >= self.cpu.mem.size:
                print(f"{addr_str}  ??    ; out of mem range")
                break

            op = self.cpu.mem.read8(op_addr)
            disasm_line, instr_size = self.decode_instruction(op_addr, op, old_cs, temp_ip)

            # 출력
            print(f"{addr_str}  {disasm_line}")

            # 다음 명령어 위치로 이동
            temp_ip = (temp_ip + instr_size) & 0xFFFF

        print("----- end of 10 lines disasm -----")

    def decode_instruction(self, phys_addr, op, cs, ip):
        """
        우리가 구현한 opcode(0xEA, 0xCD, 0x90, 0xB8, 0x05, 0xE8, 0xC3)만
        대충 해석. 그 외는 db.
        리턴 (디스어셈블 문자열, instr_size)
        """
        mem = self.cpu.mem

        if op == 0xEA:
            # JMP ptr16:16
            # 다음 4바이트 = IP(2), CS(2)
            # 주의: fetch16()과 동일하게 little endian
            ip_low = mem.read8(phys_addr+1)
            ip_high = mem.read8(phys_addr+2)
            cs_low = mem.read8(phys_addr+3)
            cs_high = mem.read8(phys_addr+4)

            new_ip = (ip_high << 8) | ip_low
            new_cs = (cs_high << 8) | cs_low

            instr_str = f"JMP  {new_cs:04X}:{new_ip:04X}"
            return (instr_str, 5)  # opcode+4바이트=5

        elif op == 0xCD:
            # INT imm8
            imm = mem.read8(phys_addr+1)
            instr_str = f"INT  {imm:02X}h"
            return (instr_str, 2)

        elif op == 0x90:
            # NOP
            return ("NOP", 1)

        elif op == 0xB8:
            # MOV AX, imm16
            imm_low = mem.read8(phys_addr+1)
            imm_high = mem.read8(phys_addr+2)
            imm16 = (imm_high << 8) | imm_low
            instr_str = f"MOV AX, {imm16:04X}h"
            return (instr_str, 3)

        elif op == 0x05:
            # ADD AX, imm16
            imm_low = mem.read8(phys_addr+1)
            imm_high = mem.read8(phys_addr+2)
            imm16 = (imm_high << 8) | imm_low
            instr_str = f"ADD AX, {imm16:04X}h"
            return (instr_str, 3)

        elif op == 0xE8:
            # CALL rel16
            disp_low = mem.read8(phys_addr+1)
            disp_high = mem.read8(phys_addr+2)
            disp16 = (disp_high << 8) | disp_low
            instr_str = f"CALL +{disp16:04X}h"
            return (instr_str, 3)

        elif op == 0xC3:
            # RET
            return ("RET", 1)

        else:
            # unknown / unimplemented
            instr_str = f"db {op:02X}h"
            return (instr_str, 1)