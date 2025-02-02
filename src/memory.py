# memory.py

class Memory:
    """
    간단한 물리 메모리(Physical Memory) 구현.
    i80386은 32비트 주소로 최대 4GB까지 접근할 수 있으므로
    여기서는 예시로 16MB(0x1000000) 정도만 할당해 둔다.
    필요에 따라 확장 가능.
    """

    def __init__(self, size_in_bytes=0x1000000):
        self.size = size_in_bytes
        self.mem = bytearray(self.size)

    def read8(self, addr: int) -> int:
        if addr < 0 or addr >= self.size:
            raise Exception(f"Memory read8 out of range: 0x{addr:08X}")
        return self.mem[addr]

    def read16(self, addr: int) -> int:
        # 리틀 엔디안
        low = self.read8(addr)
        high = self.read8(addr+1)
        return (high << 8) | low

    def read32(self, addr: int) -> int:
        # 리틀 엔디안
        b0 = self.read8(addr)
        b1 = self.read8(addr+1)
        b2 = self.read8(addr+2)
        b3 = self.read8(addr+3)
        return (b3 << 24) | (b2 << 16) | (b1 << 8) | b0

    def write8(self, addr: int, value: int):
        if addr < 0 or addr >= self.size:
            raise Exception(f"Memory write8 out of range: 0x{addr:08X}")
        self.mem[addr] = value & 0xFF

    def write16(self, addr: int, value: int):
        # 리틀 엔디안
        self.write8(addr, value & 0xFF)
        self.write8(addr+1, (value >> 8) & 0xFF)

    def write32(self, addr: int, value: int):
        self.write8(addr, value & 0xFF)
        self.write8(addr+1, (value >> 8) & 0xFF)
        self.write8(addr+2, (value >> 16) & 0xFF)
        self.write8(addr+3, (value >> 24) & 0xFF)
