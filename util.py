import os
import sys
import pygame
from pathlib import Path

# Constants
BLACK = (0, 0, 0)

PALETTES = {
    "Ocean Glow": [(0, 191, 255), (64, 224, 208), (135, 206, 250)],
    "Aurora Borealis": [(0, 255, 127), (123, 104, 238), (0, 128, 255)],
    "Pastel Bliss": [(255, 182, 193), (176, 224, 230), (221, 160, 221)],
    "Neon Bubblegum": [(255, 20, 147), (0, 255, 127), (0, 191, 255)],
    "Mystic Moon": [(72, 61, 139), (123, 104, 238), (240, 248, 255)],
    "Golden Hour": [(255, 223, 0), (255, 165, 0), (255, 69, 0)],
    "Ethereal Frost": [(224, 255, 255), (175, 238, 238), (173, 216, 230)],
    "Tropical Breeze": [(255, 87, 51), (255, 195, 113), (64, 224, 208)],
    "Candy Glow": [(255, 105, 180), (255, 182, 193), (135, 206, 250)],
    "Electric Pulse": [(255, 0, 255), (0, 255, 255), (255, 255, 0)],
    "Firefly Night": [(25, 25, 112), (72, 61, 139), (144, 238, 144)],
    "Sunset Skies": [(255, 94, 77), (255, 165, 0), (138, 43, 226)],
    "Crystal Lagoon": [(0, 206, 209), (72, 209, 204), (127, 255, 212)],
    "Molten Glow": [(255, 69, 0), (255, 140, 0), (255, 215, 0)],
    "Frosted Mint": [(173, 216, 230), (144, 238, 144), (224, 255, 255)],
    "Deep Sea": [(0, 51, 102), (0, 102, 204), (51, 153, 255)],
    "Galaxy Swirl": [(75, 0, 130), (123, 104, 238), (255, 0, 255)],
    "Tropical Sunset": [(255, 87, 51), (255, 159, 63), (255, 223, 127)],
    "Cosmic Dream": [(18, 10, 143), (75, 0, 130), (139, 0, 139)],
    "Dream Pastels": [(250, 218, 221), (230, 230, 250), (255, 228, 225)],
    "Ice Glow": [(176, 224, 230), (173, 216, 230), (70, 130, 180)],
    "Festival Neon": [(255, 0, 0), (0, 255, 0), (0, 0, 255)],
    "Lava Lamp": [(255, 69, 0), (255, 140, 0), (205, 92, 92)],
    "Ethereal Mist": [(240, 248, 255), (224, 255, 255), (175, 238, 238)],
    "Polar Glow": [(0, 128, 255), (123, 104, 238), (0, 255, 127)],
    "Aurora Glow": [(0, 255, 127), (64, 224, 208), (0, 191, 255)],
    "Starry Night": [(25, 25, 112), (72, 61, 139), (123, 104, 238)],
    "Tropical Waters": [(0, 128, 128), (0, 191, 255), (64, 224, 208)],
    "Sunrise Bliss": [(255, 87, 51), (255, 195, 113), (255, 159, 127)],
}

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

    pygame.init()
    
    # Detect platform
    platform = sys.platform
    print(f"Running on platform: {platform}")
    if platform.startswith("linux"):
        print("Running on Linux, using framebuffer")
        pygame.display.init()
        size = (screen_width, screen_height)
        screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        screen.fill(BLACK)
        pygame.font.init()
        pygame.display.update()
    elif platform.startswith("win"):
        print("Running on Windows")
        os.putenv("SDL_VIDEODRIVER", "")
        pygame.display.init()
        # Get screen resolution of the selected display
        display_info = pygame.display.Info()
        #print(f"Display info: {display_info}")
        width = display_info.current_w
        display_index = int(display)
        # Position the window manually to support 2 displays atm
        if display_index == 1:  # Second monitor
            os.environ['SDL_VIDEO_WINDOW_POS'] = f"{width},0"  # Place at the start of the second screen
        else:  # Primary monitor
            os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"

        screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
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

def hsv_to_rgb(h, s, v):
    """Convert HSV to RGB color space."""
    i = int(h * 6)  # Hue segment
    f = h * 6 - i  # Fractional part of hue
    p = int(255 * v * (1 - s))
    q = int(255 * v * (1 - f * s))
    t = int(255 * v * (1 - (1 - f) * s))
    v = int(255 * v)
    i %= 6
    if i == 0:
        return v, t, p
    if i == 1:
        return q, v, p
    
def frequency_to_rgb(frequency):
    """Convert a sound frequency to an RGB color."""
    # Speed of light in m/s
    speed_of_light = 299_792_458  

    # Prevent issues with zero or extremely low frequencies
    if frequency <= 0:
        frequency = 20  # Set a minimum frequency (e.g., 20 Hz)

    # Double the frequency until it is in the range of 400–800 THz
    while frequency < 400e12:
        frequency *= 2
    while frequency > 800e12:
        frequency /= 2

    # Convert frequency to wavelength in meters
    wavelength = speed_of_light / frequency

    # Convert wavelength to nanometers
    wavelength_nm = wavelength * 1e9

    # Map wavelength (380–750 nm) to RGB
    if 380 <= wavelength_nm <= 440:
        r = -(wavelength_nm - 440) / (440 - 380)
        g = 0
        b = 1
    elif 440 < wavelength_nm <= 490:
        r = 0
        g = (wavelength_nm - 440) / (490 - 440)
        b = 1
    elif 490 < wavelength_nm <= 510:
        r = 0
        g = 1
        b = -(wavelength_nm - 510) / (510 - 490)
    elif 510 < wavelength_nm <= 580:
        r = (wavelength_nm - 510) / (580 - 510)
        g = 1
        b = 0
    elif 580 < wavelength_nm <= 645:
        r = 1
        g = -(wavelength_nm - 645) / (645 - 580)
        b = 0
    elif 645 < wavelength_nm <= 750:
        r = 1
        g = 0
        b = 0
    else:
        r = g = b = 0  # Wavelength outside visible range

    # Adjust intensity for wavelengths outside the central range
    if 380 <= wavelength_nm < 420:
        factor = 0.3 + 0.7 * (wavelength_nm - 380) / (420 - 380)
    elif 645 < wavelength_nm <= 750:
        factor = 0.3 + 0.7 * (750 - wavelength_nm) / (750 - 645)
    else:
        factor = 1

    # Apply factor and convert to 8-bit RGB
    r = int((r * factor) * 255)
    g = int((g * factor) * 255)
    b = int((b * factor) * 255)

    return r, g, b
