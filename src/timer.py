# timer.py
import time
import threading

class TimerDevice:
    """
    간단한 타이머 구현.
    실제 하드웨어 8253 PIT처럼 일정 주기로 IRQ0을 발생시킨다.
    """

    def __init__(self, interrupt_controller, frequency_hz=1000):
        """
        :param interrupt_controller: InterruptController 객체
        :param frequency_hz: 1초에 몇 번 인터럽트를 발생시킬지 (기본 1000Hz = 1ms)
        """
        self.ic = interrupt_controller
        self.frequency = frequency_hz
        self.running = False
        self._thread = None

    def _run(self):
        interval = 1.0 / self.frequency
        while self.running:
            time.sleep(interval)
            # IRQ0 발생 요청
            self.ic.request_irq(0)  # IRQ0 = 타이머 인터럽트

    def start(self):
        if not self.running:
            self.running = True
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def stop(self):
        self.running = False
        if self._thread:
            self._thread.join()
