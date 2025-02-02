# cpu.py

from interrupt_controller import InterruptController
from memory import Memory

FLAG_CF = 1 << 0
FLAG_PF = 1 << 2
FLAG_AF = 1 << 4
FLAG_ZF = 1 << 6
FLAG_SF = 1 << 7
FLAG_TF = 1 << 8
FLAG_IF = 1 << 9
FLAG_DF = 1 << 10
FLAG_OF = 1 << 11

def sign_extend16_to32(x):
    return x if x < 0x8000 else x - 0x10000

class CPU:
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
        self.EFLAGS = 0x00000002
        self.running = True

    def get_flags(self):
        return self.EFLAGS

    def set_flag_if(self, val: bool):
        if val: self.EFLAGS |= FLAG_IF
        else:   self.EFLAGS &= ~FLAG_IF

    def real_mode_address(self, seg, off):
        return ((seg & 0xFFFF) << 4) + (off & 0xFFFF)

    def seg_override(self, default_seg):
        return default_seg

    def read_rm16(self, seg, offset):
        addr = self.real_mode_address(seg, offset)
        return self.mem.read16(addr)

    def write_rm16(self, seg, offset, val):
        addr = self.real_mode_address(seg, offset)
        self.mem.write16(addr, val & 0xFFFF)

    def step(self):
        if (self.EFLAGS & FLAG_IF) != 0:
            pending_int = self.ic.get_pending_interrupt()
            if pending_int is not None:
                self.handle_interrupt(pending_int)
                return

        op = self.fetch8()

        if op == 0xEA:
            new_ip = self.fetch16()
            new_cs = self.fetch16()
            self.CS = new_cs
            self.EIP = new_ip

        elif op == 0xCD:
            int_num = self.fetch8()
            self.handle_interrupt(int_num)

        elif op == 0x90:
            pass

        elif op == 0xB8:
            imm16 = self.fetch16()
            self.EAX = (self.EAX & 0xFFFF0000) | imm16

        elif op == 0x05:  # ADD AX, imm16
            imm16 = self.fetch16()
            ax = self.EAX & 0xFFFF
            full = ax + imm16
            result = full & 0xFFFF
            self.EAX = (self.EAX & 0xFFFF0000) | result
            # Update flags
            if full > 0xFFFF:
                self.EFLAGS |= FLAG_CF
            else:
                self.EFLAGS &= ~FLAG_CF
            if result == 0:
                self.EFLAGS |= FLAG_ZF
            else:
                self.EFLAGS &= ~FLAG_ZF
            if (result & 0x8000) != 0:
                self.EFLAGS |= FLAG_SF
            else:
                self.EFLAGS &= ~FLAG_SF
            sign_ax = (ax & 0x8000) != 0
            sign_imm = (imm16 & 0x8000) != 0
            sign_res = (result & 0x8000) != 0
            if (sign_ax == sign_imm) and (sign_ax != sign_res):
                self.EFLAGS |= FLAG_OF
            else:
                self.EFLAGS &= ~FLAG_OF

        elif op == 0xE8:
            disp16 = self.fetch16()
            next_ip = self.EIP
            self.push16(next_ip)
            signed_disp = sign_extend16_to32(disp16)
            self.EIP = (self.EIP + signed_disp) & 0xFFFF

        elif op == 0xC3:
            ret_ip = self.pop16()
            self.EIP = ret_ip

        elif op == 0x8B:
            self.mov_r16_rm16()

        elif op == 0x89:
            self.mov_rm16_r16()

        elif op >= 0x50 and op <= 0x57:  # PUSH r16
            reg_id = op & 0x07
            val16 = self.get_reg16(reg_id)
            self.push16(val16)

        elif op >= 0x58 and op <= 0x5F:  # POP r16
            reg_id = op & 0x07
            val16 = self.pop16()
            self.set_reg16(reg_id, val16)

        elif op == 0x3D:  # CMP AX, imm16
            imm16 = self.fetch16()
            ax = self.EAX & 0xFFFF
            full = ax - imm16
            result = full & 0xFFFF
            # Update flags
            if ax < imm16:
                self.EFLAGS |= FLAG_CF
            else:
                self.EFLAGS &= ~FLAG_CF
            if result == 0:
                self.EFLAGS |= FLAG_ZF
            else:
                self.EFLAGS &= ~FLAG_ZF
            if (result & 0x8000) != 0:
                self.EFLAGS |= FLAG_SF
            else:
                self.EFLAGS &= ~FLAG_SF
            sign_ax = (ax & 0x8000) != 0
            sign_imm = (imm16 & 0x8000) != 0
            sign_res = (result & 0x8000) != 0
            if (sign_ax != sign_imm) and (sign_ax != sign_res):
                self.EFLAGS |= FLAG_OF
            else:
                self.EFLAGS &= ~FLAG_OF

        elif (op >= 0x70 and op <= 0x7F):
            self.jcc_short(op)

        elif op == 0xE2:
            disp8 = self.fetch8()
            cx = self.ECX & 0xFFFF
            cx = (cx - 1) & 0xFFFF
            self.ECX = (self.ECX & 0xFFFF0000) | cx
            if cx != 0:
                signed_disp = disp8 if disp8 < 0x80 else disp8 - 0x100
                self.EIP = (self.EIP + signed_disp) & 0xFFFF

        elif op == 0xAA:  # STOSB
            es_val = self.ES
            di = self.EDI & 0xFFFF
            al = self.EAX & 0xFF
            addr = self.real_mode_address(es_val, di)
            self.mem.write8(addr, al)
            if (self.EFLAGS & FLAG_DF) != 0:
                di = (di - 1) & 0xFFFF
            else:
                di = (di + 1) & 0xFFFF
            self.EDI = (self.EDI & 0xFFFF0000) | di

        elif op == 0xAC:  # LODSB
            ds_val = self.DS
            si = self.ESI & 0xFFFF
            addr = self.real_mode_address(ds_val, si)
            data = self.mem.read8(addr)
            self.EAX = (self.EAX & 0xFFFFFF00) | data
            if (self.EFLAGS & FLAG_DF) != 0:
                si = (si - 1) & 0xFFFF
            else:
                si = (si + 1) & 0xFFFF
            self.ESI = (self.ESI & 0xFFFF0000) | si

        elif op == 0xF3:  # REP prefix
            next_op = self.fetch8()
            if next_op == 0xA4:  # REP MOVSB
                self.rep_movsb()
            elif next_op == 0xA5:  # REP MOVSW
                self.rep_movsw()
            elif next_op == 0xAA:  # REP STOSB
                self.rep_stosb()
            else:
                raise Exception("REP prefix used with unimplemented instruction 0x%02X" % next_op)
        else:
            raise Exception(f"Unimplemented opcode 0x{op:02X} at CS:IP={self.CS:04X}:{(self.EIP-1) & 0xFFFF:04X}")

    def mov_r16_rm16(self):
        modrm = self.fetch8()
        reg_id = (modrm >> 3) & 7
        rm_id  = modrm & 7
        mod    = (modrm >> 6) & 3
        if mod == 3:
            rm_val = self.get_reg16(rm_id)
            self.set_reg16(reg_id, rm_val)
        else:
            offset = self.calc_modrm16_address(mod, rm_id)
            seg = self.seg_override(self.DS)
            val16 = self.read_rm16(seg, offset)
            self.set_reg16(reg_id, val16)

    def mov_rm16_r16(self):
        modrm = self.fetch8()
        reg_id = (modrm >> 3) & 7
        rm_id  = modrm & 7
        mod    = (modrm >> 6) & 3
        reg_val = self.get_reg16(reg_id)
        if mod == 3:
            self.set_reg16(rm_id, reg_val)
        else:
            offset = self.calc_modrm16_address(mod, rm_id)
            seg = self.seg_override(self.DS)
            self.write_rm16(seg, offset, reg_val)

    def get_reg16(self, reg_id):
        if reg_id == 0: return self.EAX & 0xFFFF
        elif reg_id == 1: return self.ECX & 0xFFFF
        elif reg_id == 2: return self.EDX & 0xFFFF
        elif reg_id == 3: return self.EBX & 0xFFFF
        elif reg_id == 4: return self.ESP & 0xFFFF
        elif reg_id == 5: return self.EBP & 0xFFFF
        elif reg_id == 6: return self.ESI & 0xFFFF
        elif reg_id == 7: return self.EDI & 0xFFFF

    def set_reg16(self, reg_id, val):
        if reg_id == 0: self.EAX = (self.EAX & 0xFFFF0000) | (val & 0xFFFF)
        elif reg_id == 1: self.ECX = (self.ECX & 0xFFFF0000) | (val & 0xFFFF)
        elif reg_id == 2: self.EDX = (self.EDX & 0xFFFF0000) | (val & 0xFFFF)
        elif reg_id == 3: self.EBX = (self.EBX & 0xFFFF0000) | (val & 0xFFFF)
        elif reg_id == 4: self.ESP = (self.ESP & 0xFFFF0000) | (val & 0xFFFF)
        elif reg_id == 5: self.EBP = (self.EBP & 0xFFFF0000) | (val & 0xFFFF)
        elif reg_id == 6: self.ESI = (self.ESI & 0xFFFF0000) | (val & 0xFFFF)
        elif reg_id == 7: self.EDI = (self.EDI & 0xFFFF0000) | (val & 0xFFFF)

    def calc_modrm16_address(self, mod, rm):
        disp = 0
        if mod == 0:
            if rm == 6:
                disp = self.fetch16()
                return disp
        elif mod == 1:
            disp = self.fetch8()
            if disp >= 0x80:
                disp -= 0x100
        elif mod == 2:
            disp = self.fetch16()
        base = 0
        bx = self.EBX & 0xFFFF
        si = self.ESI & 0xFFFF
        di = self.EDI & 0xFFFF
        bp = self.EBP & 0xFFFF
        if rm == 0: base = (bx + si + disp) & 0xFFFF
        elif rm == 1: base = (bx + di + disp) & 0xFFFF
        elif rm == 2: base = (bp + si + disp) & 0xFFFF
        elif rm == 3: base = (bp + di + disp) & 0xFFFF
        elif rm == 4: base = (si + disp) & 0xFFFF
        elif rm == 5: base = (di + disp) & 0xFFFF
        elif rm == 6: base = (bp + disp) & 0xFFFF
        elif rm == 7: base = (bx + disp) & 0xFFFF
        return base & 0xFFFF

    def push16(self, val):
        sp = self.ESP & 0xFFFF
        sp = (sp - 2) & 0xFFFF
        self.ESP = (self.ESP & 0xFFFF0000) | sp
        addr = self.real_mode_address(self.SS, sp)
        self.mem.write16(addr, val & 0xFFFF)

    def pop16(self):
        sp = self.ESP & 0xFFFF
        addr = self.real_mode_address(self.SS, sp)
        val = self.mem.read16(addr)
        sp = (sp + 2) & 0xFFFF
        self.ESP = (self.ESP & 0xFFFF0000) | sp
        return val

    def jcc_short(self, op):
        disp8 = self.fetch8()
        signed_disp = disp8 if disp8 < 0x80 else disp8 - 0x100
        cond = False
        if op == 0x70:  # JO
            cond = (self.EFLAGS & FLAG_OF) != 0
        elif op == 0x71:  # JNO
            cond = (self.EFLAGS & FLAG_OF) == 0
        elif op == 0x72:  # JB/JC
            cond = (self.EFLAGS & FLAG_CF) != 0
        elif op == 0x73:  # JNB/JNC
            cond = (self.EFLAGS & FLAG_CF) == 0
        elif op == 0x74:  # JZ/JE
            cond = (self.EFLAGS & FLAG_ZF) != 0
        elif op == 0x75:  # JNZ/JNE
            cond = (self.EFLAGS & FLAG_ZF) == 0
        # You can add more here if needed
        if cond:
            self.EIP = (self.EIP + signed_disp) & 0xFFFF

    def rep_movsb(self):
        cx = self.ECX & 0xFFFF
        ds = self.DS
        es = self.ES
        si = self.ESI & 0xFFFF
        di = self.EDI & 0xFFFF
        inc = -1 if ((self.EFLAGS & FLAG_DF) != 0) else 1
        while cx > 0:
            src = self.real_mode_address(ds, si)
            dst = self.real_mode_address(es, di)
            val = self.mem.read8(src)
            self.mem.write8(dst, val)
            si = (si + inc) & 0xFFFF
            di = (di + inc) & 0xFFFF
            cx -= 1
        self.ECX = (self.ECX & 0xFFFF0000) | (cx & 0xFFFF)
        self.ESI = (self.ESI & 0xFFFF0000) | (si & 0xFFFF)
        self.EDI = (self.EDI & 0xFFFF0000) | (di & 0xFFFF)

    def rep_movsw(self):
        cx = self.ECX & 0xFFFF
        ds = self.DS
        es = self.ES
        si = self.ESI & 0xFFFF
        di = self.EDI & 0xFFFF
        inc = -2 if ((self.EFLAGS & FLAG_DF) != 0) else 2
        while cx > 0:
            src = self.real_mode_address(ds, si)
            dst = self.real_mode_address(es, di)
            val = self.mem.read16(src)
            self.mem.write16(dst, val)
            si = (si + inc) & 0xFFFF
            di = (di + inc) & 0xFFFF
            cx -= 1
        self.ECX = (self.ECX & 0xFFFF0000) | (cx & 0xFFFF)
        self.ESI = (self.ESI & 0xFFFF0000) | (si & 0xFFFF)
        self.EDI = (self.EDI & 0xFFFF0000) | (di & 0xFFFF)

    def rep_stosb(self):
        cx = self.ECX & 0xFFFF
        es = self.ES
        di = self.EDI & 0xFFFF
        inc = -1 if ((self.EFLAGS & FLAG_DF) != 0) else 1
        al = self.EAX & 0xFF
        while cx > 0:
            dst = self.real_mode_address(es, di)
            self.mem.write8(dst, al)
            di = (di + inc) & 0xFFFF
            cx -= 1
        self.ECX = (self.ECX & 0xFFFF0000) | (cx & 0xFFFF)
        self.EDI = (self.EDI & 0xFFFF0000) | di

    def fetch8(self):
        addr = self.real_mode_address(self.CS, self.EIP)
        val = self.mem.read8(addr)
        self.EIP = (self.EIP + 1) & 0xFFFF
        return val

    def fetch16(self):
        low = self.fetch8()
        high = self.fetch8()
        return (high << 8) | low

    def handle_interrupt(self, int_num):
        self.push16(self.EFLAGS & 0xFFFF)
        self.set_flag_if(False)
        self.push16(self.CS)
        self.push16(self.EIP)
        vector_addr = int_num * 4
        new_ip = self.mem.read16(vector_addr)
        new_cs = self.mem.read16(vector_addr + 2)
        self.CS = new_cs
        self.EIP = new_ip