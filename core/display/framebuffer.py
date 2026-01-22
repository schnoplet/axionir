import numpy as np


class Framebuffer:
    def __init__(self, width=1280, height=720):
        self.width = width
        self.height = height

        # RGBA8888
        self.buffer = np.zeros((height, width, 4), dtype=np.uint8)

    def clear(self, r, g, b):
        self.buffer[:, :, 0] = r
        self.buffer[:, :, 1] = g
        self.buffer[:, :, 2] = b
        self.buffer[:, :, 3] = 255

    def get_pixels(self):
        return self.buffer
