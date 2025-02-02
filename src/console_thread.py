# console_thread.py
import threading
import queue
import sys

class ConsoleThread:
    """
    별도 스레드로 돌며, 터미널에서 사용자 입력을 받는다.
    입력받은 명령을 commands 큐에 넣는다.
    """
    def __init__(self):
        self.commands = queue.Queue()
        self.running = False
        self.thread = None

    def _loop(self):
        while self.running:
            line = sys.stdin.readline()
            if not line:
                # EOF
                break
            cmd = line.strip().lower()
            self.commands.put(cmd)
            if cmd == "q":
                # 종료 의도
                self.running = False
                break

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def get_command_nowait(self):
        """
        큐에 쌓인 명령을 하나 꺼낸다.
        없으면 None 반환.
        """
        if not self.commands.empty():
            return self.commands.get_nowait()
        return None
