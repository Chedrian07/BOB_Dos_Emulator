# bios.py

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
        # 1) IVT 초기화
        for i in range(0x400):
            self.memory.write8(i, 0)

        # 2) 부트섹터 로드
        boot_sector = self.disk.read_sector(0)
        for i, b in enumerate(boot_sector):
            self.memory.write8(0x7C00 + i, b)

        # 3) 0xFFFF0에 JMP 0x0000:0x7C00 (오퍼코드 = 0xEA, 0x00,0x7C, 0x00,0x00)
        # 물리주소 F000:FFF0 = 0xFFFF0
        self.memory.write8(0xFFFF0, 0xEA)  # JMP ptr16:16
        self.memory.write8(0xFFFF1, 0x00)  # IP low
        self.memory.write8(0xFFFF2, 0x7C)  # IP high = 0x7C00
        self.memory.write8(0xFFFF3, 0x00)  # CS low
        self.memory.write8(0xFFFF4, 0x00)  # CS high

    def setup_e820_map(self):
        # 필요하다면 INT 15h/E820 호출 시 참조할 메모리 맵 구조를
        # 특정 위치에 생성 가능
        pass