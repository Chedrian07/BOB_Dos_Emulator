# eisa_bus.py

class EISABus:
    """
    EISA (Extended ISA) 버스 컨트롤러.
    I/O 포트 접근을 각 장치로 중계한다.
    """

    def __init__(self):
        self.io_port_devices = {}

    def register_io_device(self, port: int, device):
        self.io_port_devices[port] = device

    def io_in8(self, port: int) -> int:
        if port in self.io_port_devices:
            return self.io_port_devices[port].read_port(port)
        return 0xFF

    def io_out8(self, port: int, value: int):
        if port in self.io_port_devices:
            self.io_port_devices[port].write_port(port, value & 0xFF)