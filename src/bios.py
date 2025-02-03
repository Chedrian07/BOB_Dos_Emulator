FLAG_CF = 0x00000001  # Carry flag bit for EFLAGS

class BIOS:
    """
    간단한 BIOS 에뮬레이션.
    실제 ROM 바이너리를 0xF0000 영역에 로드해두고,
    CPU가 리셋되면 0xFFFF0에서 실행을 시작하지만,
    여기서는 Python적으로 부트섹터 로딩 및 0xFFFF0에 JMP 명령 삽입만 시연.
    """

    def __init__(self, memory, disk, bios_start=0xF0000):
        self.memory = memory
        self.disk = disk
        self.bios_start = bios_start

    def load_bios(self):
        """
        1) IVT(0~0x3FF) 초기화
        2) 디스크 LBA=0 부트섹터 -> 0x7C00 로드
        3) 0xFFFF0 에 JMP 0x0000:0x7C00 심어주기
        """
        for i in range(0x400):
            self.memory.write8(i, 0)  # IVT 초기화

        boot_sector = self.disk.read_sector(0)
        for i, b in enumerate(boot_sector):
            self.memory.write8(0x7C00 + i, b)

        self.memory.write8(0xFFFF0, 0xEA)  # JMP ptr16:16
        self.memory.write8(0xFFFF1, 0x00)  # IP low
        self.memory.write8(0xFFFF2, 0x7C)  # IP high
        self.memory.write8(0xFFFF3, 0x00)  # CS low
        self.memory.write8(0xFFFF4, 0x00)  # CS high

        # BIOS 기반 인터럽트 벡터도 설정
        self.setup_interrupt_vectors()

    def setup_interrupt_vectors(self):
        """
        주요 BIOS 인터럽트 핸들러 주소 설정
        """
        # INT 10h (비디오)
        self.set_interrupt_vector(0x10, self.handle_int10)
        # INT 13h (디스크)
        self.set_interrupt_vector(0x13, self.handle_int13)
        # INT 15h (시스템)
        self.set_interrupt_vector(0x15, self.handle_int15)

    def set_interrupt_vector(self, int_num, handler):
        """
        IVT의 특정 인터럽트 번호에 대한 핸들러 주소 설정
        """
        vector_addr = int_num * 4
        # 포인터를 임시로 함수 id 해시 기반 주소로 매핑
        handler_addr = self.bios_start + (id(handler) & 0xFFFF)
        self.memory.write16(vector_addr, handler_addr & 0xFFFF)
        self.memory.write16(vector_addr + 2, (handler_addr >> 16) & 0xFFFF)

    def handle_int10(self, cpu):
        """
        INT 10h: 비디오 서비스 (기본 모드 설정 및 픽셀 출력)
        """
        ah = (cpu.EAX >> 8) & 0xFF
        if ah == 0x00:
            # 모드 설정
            mode = cpu.EAX & 0xFF
            if mode == 0x13:
                # 320x200 256색 모드
                pass
        elif ah == 0x0C:
            # 픽셀 그리기
            al = cpu.EAX & 0xFF
            cx = cpu.ECX & 0xFFFF
            dx = cpu.EDX & 0xFFFF
            addr = 0xA0000 + dx * 320 + cx
            if addr < 0x1000000:
                cpu.mem.write8(addr, al)

    def handle_int13(self, cpu):
        """
        INT 13h: 디스크 서비스
        """
        ah = (cpu.EAX >> 8) & 0xFF
        if ah == 0x02:
            # 섹터 읽기
            al = cpu.EAX & 0xFF
            ch = (cpu.ECX >> 8) & 0xFF
            cl = cpu.ECX & 0xFF
            dh = (cpu.EDX >> 8) & 0xFF
            dl = cpu.EDX & 0xFF
            es = cpu.ES
            bx = cpu.EBX & 0xFFFF

            lba = ch * 16 * 63 + dh * 63 + (cl - 1)
            data = self.disk.read_sector(lba)
            for i in range(len(data)):
                cpu.mem.write8(self.real_mode_address(es, bx + i), data[i])
            cpu.EAX = 0x0100  # AH=1, AL=0
        else:
            cpu.EFLAGS |= FLAG_CF  # 지원 안함

    def handle_int15(self, cpu):
        """
        INT 15h: 시스템 서비스
        """
        if cpu.EAX == 0xE820:
            # E820 메모리 맵
            self.setup_e820_map()
            cpu.EAX = 0x534D4150  # 'SMAP'
            cpu.ECX = 24
            cpu.EDX = 0x534D4150
            cpu.EFLAGS &= ~FLAG_CF
        else:
            cpu.EFLAGS |= FLAG_CF

    def setup_e820_map(self):
        """
        메모리 맵 (1MB~16MB 예시)
        """
        e820_map = [
            (0x00000000, 0x0009FC00, 1),
            (0x0009FC00, 0x000A0000, 2),
            (0x000F0000, 0x00100000, 2),
            (0x00100000, 0x1000000, 1)
        ]
        addr = 0x1000
        for base, length, mtype in e820_map:
            self.memory.write32(addr, base)
            self.memory.write32(addr + 4, 0)
            self.memory.write32(addr + 8, length)
            self.memory.write32(addr + 12, 0)
            self.memory.write32(addr + 16, mtype)
            addr += 20

    def real_mode_address(self, seg, off):
        """
        세그먼트:오프셋 -> 물리주소 변환
        """
        return ((seg & 0xFFFF) << 4) + (off & 0xFFFF)