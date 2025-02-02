# bios.py

class BIOS:
    """
    간단한 BIOS 에뮬레이션. 
    실제로는 ROM 바이너리를 0xF0000 등지에 로드해두고,
    CPU가 리셋되면 0xFFFF0 주소에서 실행을 시작하게 되지만,
    여기서는 Python적으로 간단히 '부팅 루틴'을 메모리에 써두고 
    CPU 초기 레지스터를 설정해주는 정도의 기능만 시연.
    """

    def __init__(self, memory, disk, bios_start=0xF0000):
        self.memory = memory
        self.disk = disk
        self.bios_start = bios_start

    def load_bios(self):
        """
        간단히, 0x7C00에 디스크의 0번 LBA(부트섹터)를 읽어다 복사해두고,
        실제 실행이 가능하도록 BIOS 흉내를 낸다.
        또한, IVT(Interrupt Vector Table) 등도 초기화한다.
        """
        # 1) IVT(Interrupt Vector Table) 0:0 ~ 0:400 초기화
        for i in range(0x400):
            self.memory.write8(i, 0)

        # 2) LBA=0 섹터를 읽어서 0x7C00에 로드
        boot_sector = self.disk.read_sector(0)
        for i, b in enumerate(boot_sector):
            self.memory.write8(0x7C00 + i, b)

        # 3) 임의의 간단한 BIOS 루틴(0xF000:FFF0)에 JMP 0x7C00 같은 코드를 써둘 수도 있음
        # 여기서는 생략. CPU 리셋시 EIP=0xFFF0로 가정하고, 그곳에서 JMP 0x7C00 하는 식.

    def setup_e820_map(self):
        """
        e820 호출을 대비해, 어떤 메모리 맵 정보를 특정 위치에 저장한다고 가정.
        DOS의 IO.SYS 등이 INT 15h, EAX=0xE820 호출할 때 참조.
        실제로는 훨씬 복잡하지만, 여기서는 간단히 '전체가 RAM'이라는 식의 한 엔트리만 넣는다.
        """
        # 필요시 구현
        pass
