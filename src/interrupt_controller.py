# interrupt_controller.py

class InterruptController:
    """
    간단한 PIC(PIT, 마스터/슬레이브)를 합쳐서 추상화한 클래스.
    IRQ0 ~ IRQ15 신호를 관리하고, CPU에 인터럽트가 필요함을 알려준다.
    """

    def __init__(self):
        # IRQ 라인별로 인터럽트 요청 상태
        self.irq_requests = [False]*16
        # 인터럽트 벡터 오프셋 (주로 마스터 PIC = 0x08, 슬레이브 PIC = 0x70 등)
        # DOS 시절에는 마스터 0x08, 슬레이브 0x70. 실제로는 OS별 재설정 가능.
        self.master_offset = 0x08
        self.slave_offset = 0x70

    def request_irq(self, irq_num: int):
        if 0 <= irq_num < 16:
            self.irq_requests[irq_num] = True

    def clear_irq(self, irq_num: int):
        if 0 <= irq_num < 16:
            self.irq_requests[irq_num] = False

    def get_pending_interrupt(self):
        """
        우선순위가 가장 높은(숫자가 낮은) IRQ를 찾아서
        해당 IRQ를 반환하고, 요청 상태를 클리어한다.
        없으면 None 반환.
        """
        for irq_num in range(16):
            if self.irq_requests[irq_num]:
                self.irq_requests[irq_num] = False
                # 0~7이면 마스터, 8~15이면 슬레이브
                if irq_num < 8:
                    return self.master_offset + irq_num
                else:
                    return self.slave_offset + (irq_num - 8)
        return None
