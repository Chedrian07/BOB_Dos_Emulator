# video_device.py

import sdl2
import sdl2.ext
import threading
import time

class VideoDevice:
    """
    매우 간단한 VGA 호환 디바이스.
    320x200x8bpp (256 color) 가정.
    메모리 0xA0000 ~ 0xAFA00 (예시) 범위를 화면으로 매핑한다고 가정.
    """

    def __init__(self, memory, vga_base_addr=0xA0000, width=320, height=200):
        self.memory = memory
        self.vga_base_addr = vga_base_addr
        self.width = width
        self.height = height
        self.running = False
        self._thread = None

        # SDL2 초기화
        sdl2.ext.init()
        self.window = sdl2.ext.Window("VGA Emulator", size=(self.width, self.height))
        self.window.show()

        # 8비트 팔레트 -> 32비트 RGBA 변환용 간단 테이블
        # 실제 VGA 팔레트는 256개 색상 레지스터를 이용하지만,
        # 여기서는 임의로 256개 컬러를 정의한다(그라데이션, 무지개 등).
        self.palette = [(i, i, i, 255) for i in range(256)]

    def _update_loop(self):
        # 초당 30프레임 정도로 디스플레이 갱신
        fps = 30
        interval = 1.0 / fps

        # 렌더 서페이스
        renderer = sdl2.ext.Renderer(self.window)
        texture = renderer.create_texture(sdl2.SDL_PIXELFORMAT_RGBA8888,
                                          sdl2.SDL_TEXTUREACCESS_STREAMING,
                                          (self.width, self.height))

        while self.running:
            start_time = time.time()

            # 이벤트 처리(창 닫힘 이벤트 등)
            events = sdl2.ext.get_events()
            for event in events:
                if event.type == sdl2.SDL_QUIT:
                    self.running = False

            # 메모리에서 VGA 데이터를 읽어서 texture에 복사
            pitch = self.width * 4  # RGBA8888
            pixels_ptr, _ = sdl2.SDL_LockTexture(texture, None)
            # Python에서 직접 pointer 다루기는 복잡하므로,
            # ctypes 배열처럼 취급해 색 변환
            import ctypes
            pix_array = (ctypes.c_uint8 * (pitch * self.height)).from_address(pixels_ptr)

            for y in range(self.height):
                for x in range(self.width):
                    # VGA 1바이트
                    color_index = self.memory.read8(self.vga_base_addr + y*self.width + x)
                    # 팔레트에서 RGBA
                    r, g, b, a = self.palette[color_index & 0xFF]
                    offset = (y*self.width + x)*4
                    pix_array[offset+0] = r
                    pix_array[offset+1] = g
                    pix_array[offset+2] = b
                    pix_array[offset+3] = a

            sdl2.SDL_UnlockTexture(texture)

            # 렌더링
            renderer.copy(texture, None, None)
            renderer.present()

            # 프레임 제한
            elapsed = time.time() - start_time
            sleep_time = interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

        sdl2.ext.quit()

    def start(self):
        if not self.running:
            self.running = True
            self._thread = threading.Thread(target=self._update_loop, daemon=True)
            self._thread.start()

    def stop(self):
        self.running = False
        if self._thread:
            self._thread.join()
