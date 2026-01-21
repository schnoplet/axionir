class Framebuffer:
    WIDTH = 1280
    HEIGHT = 720
    BPP = 4  # RGBX8888

    @staticmethod
    def size_bytes() -> int:
        return Framebuffer.WIDTH * Framebuffer.HEIGHT * Framebuffer.BPP
