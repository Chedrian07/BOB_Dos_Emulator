# eisa_bus.py

class EISABus:
    """
    EISA (Extended ISA) 버스 컨트롤러.
    I/O 포트 접근을 각 장치(키보드, 마우스, IDE, VGA 등)로 중계한다.
    """

    def __init__(self):
        # 연결된 장치들(I/O 포트 기반 접근)을 저장
        # 예: { 0x60: keyboard_device, 0x64: keyboard_ctrl_reg, ... }
        self.io_port_devices = {}

    def register_io_device(self, port: int, device):
        """
        특정 포트 번호에 대해 read/write를 담당할 객체(device)를 등록.
        device는 read_port(port), write_port(port, value) 메서드를 구현한다고 가정.
        """
        self.io_port_devices[port] = device

    def io_in8(self, port: int) -> int:
        """
        8비트 read (inb)
        """
        if port in self.io_port_devices:
            return self.io_port_devices[port].read_port(port)
        # 없는 포트일 경우 0xFF를 반환하거나 예외를 던질 수 있음
        return 0xFF

    def io_out8(self, port: int, value: int):
        """
        8비트 write (outb)
        """
        if port in self.io_port_devices:
            self.io_port_devices[port].write_port(port, value)
        else:
            # 연결되지 않은 포트라면 무시
            pass
