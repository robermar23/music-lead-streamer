import os
import pygame
from pathlib import Path

# Constants
BLACK = (0, 0, 0)

 # This will hold the global screen object
screen = None 

# Path to the "shows" directory, which we load dynamically
SHOWS_PATH = Path(__file__).parent / "show"

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

def get_shows():
    """
    Iterate ofver shows folder to find all python files
    """
    return [
        f.stem for f in SHOWS_PATH.glob("*.py")
        # make sure to skip module file
        if f.is_file() and f.stem != "__init__"
    ]
