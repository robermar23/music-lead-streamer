import os
import pygame

# Constants
BLACK = (0, 0, 0)
screen = None  # This will hold the global screen object

def setup_display(display: str, video_driver: str, screen_width: int, screen_height: int):
    """
    Set up the display environment and initialize pygame.
    """
    os.putenv("DISPLAY", display)
    os.putenv("SDL_VIDEODRIVER", video_driver)

    pygame.display.init()
    size = (screen_width, screen_height)
    screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
    screen.fill(BLACK)
    pygame.font.init()
    pygame.display.update()

    #this screen object is what is used to create everything else
    return screen 