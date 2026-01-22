import pygame
import sys


class HostWindow:
    def __init__(self, framebuffer):
        pygame.init()
        self.fb = framebuffer
        self.screen = pygame.display.set_mode(
            (framebuffer.width, framebuffer.height)
        )
        pygame.display.set_caption("AxionIR - NS2 Display")

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

        surf = pygame.surfarray.make_surface(
            self.fb.get_pixels()[:, :, :3].swapaxes(0, 1)
        )
        self.screen.blit(surf, (0, 0))
        pygame.display.flip()
