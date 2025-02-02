# dma_controller.py

class DMAController:
    """
    가상 DMA 컨트롤러.
    DMA 채널별로 메모리에 데이터를 블록 전송 후 IRQ 발생.
    """

    def __init__(self, memory, interrupt_controller):
        self.memory = memory
        self.ic = interrupt_controller
        self.channels = {
            0: {"address": 0, "count": 0, "mode": 0},
            1: {"address": 0, "count": 0, "mode": 0},
        }

    def start_dma(self, channel: int, source_data: bytes):
        if channel not in self.channels:
            return
        address = self.channels[channel]["address"]
        count = self.channels[channel]["count"]
        length = min(len(source_data), count)
        for i in range(length):
            self.memory.write8(address + i, source_data[i])
        # 끝나면 IRQ
        self.ic.request_irq(3)

    def set_channel_params(self, channel: int, address: int, count: int, mode: int):
        if channel in self.channels:
            self.channels[channel]["address"] = address
            self.channels[channel]["count"] = count
            self.channels[channel]["mode"] = mode