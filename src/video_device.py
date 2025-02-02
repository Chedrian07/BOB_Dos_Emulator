# video_device.py

import sdl2
import sdl2.ext
import ctypes

class VideoDevice:
    """
    VGA 호환 디바이스.
    320x200x8bpp.
    스레드 없이 메인 스레드에서 update_frame()을 호출해 렌더링/이벤트 처리.
    """

    def __init__(self, memory, vga_base_addr=0xA0000, width=320, height=200):
        self.memory = memory
        self.vga_base_addr = vga_base_addr
        self.width = width
        self.height = height

        sdl2.ext.init()
        self.window = sdl2.ext.Window("VGA Emulator", size=(self.width, self.height))
        self.window.show()

        self.renderer = sdl2.ext.Renderer(self.window)
        self.sdl_renderer = self.renderer.sdlrenderer

        # 8비트 -> RGBA8888 텍스처
        self.texture = sdl2.SDL_CreateTexture(
            self.sdl_renderer,
            sdl2.SDL_PIXELFORMAT_RGBA8888,
            sdl2.SDL_TEXTUREACCESS_STREAMING,
            self.width,
            self.height
        )

        self.palette = [(i, i, i, 255) for i in range(256)]

    def update_frame(self):
        """
        1) SDL 이벤트 폴링
        2) VGA 메모리 -> texture 복사
        3) 화면 렌더링
        메인 스레드에서 주기적으로 호출하면 macOS에서도 문제 없음.
        """
        # 이벤트 처리
        events = sdl2.ext.get_events()
        for e in events:
            if e.type == sdl2.SDL_QUIT:
                # 창 닫힐 때 동작을 원한다면 처리
                pass

        # Lock texture
        pixels_ptr = ctypes.c_void_p()
        pitch = ctypes.c_int()
        ret = sdl2.SDL_LockTexture(self.texture, None, ctypes.byref(pixels_ptr), ctypes.byref(pitch))
        if ret != 0:
            return

        pitch_val = pitch.value
        buf_ptr = pixels_ptr.value
        pix_array = (ctypes.c_uint8 * (pitch_val * self.height)).from_address(buf_ptr)

        # 8bpp VGA -> RGBA
        for y in range(self.height):
            for x in range(self.width):
                color_index = self.memory.read8(self.vga_base_addr + y*self.width + x)
                r, g, b, a = self.palette[color_index & 0xFF]
                offset = y*pitch_val + x*4
                pix_array[offset+0] = r
                pix_array[offset+1] = g
                pix_array[offset+2] = b
                pix_array[offset+3] = a

        sdl2.SDL_UnlockTexture(self.texture)
        sdl2.SDL_RenderCopy(self.sdl_renderer, self.texture, None, None)
        sdl2.SDL_RenderPresent(self.sdl_renderer)