# dma_controller.py

class DMAController:
    """
    가상 DMA 컨트롤러.
    가상 장치(예: 디스크 -> 메모리, 메모리 -> 사운드 버퍼 등)에서
    블록 데이터를 주 메모리로 이동할 때 사용.
    """

    def __init__(self, memory, interrupt_controller):
        self.memory = memory
        self.ic = interrupt_controller
        # 채널별 주소, 크기
        self.channels = {
            0: {"address": 0, "count": 0, "mode": 0},  # 예시
            1: {"address": 0, "count": 0, "mode": 0},
        }

    def start_dma(self, channel: int, source_data: bytes):
        """
        DMA 전송 시뮬레이션: source_data를 해당 channel 정보에 따라
        memory에 써넣는다. 끝나면 IRQ 발생.
        """
        if channel not in self.channels:
            return

        address = self.channels[channel]["address"]
        count = self.channels[channel]["count"]
        # 실제로는 count+1 바이트가 이동되지만 단순화
        length = min(len(source_data), count)

        for i in range(length):
            self.memory.write8(address + i, source_data[i])

        # 전송 완료 후 DMA 인터럽트(예: 채널별 IRQ가 다를 수 있음, 여기서는 IRQ 3 가정)
        # 실제로는 채널마다 IRQ가 다르고, 마스터/슬레이브 PIC 어디에 연결되는지도 다름
        self.ic.request_irq(3)

    def set_channel_params(self, channel: int, address: int, count: int, mode: int):
        if channel in self.channels:
            self.channels[channel]["address"] = address
            self.channels[channel]["count"] = count
            self.channels[channel]["mode"] = mode
