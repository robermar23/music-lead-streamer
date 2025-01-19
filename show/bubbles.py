import pygame
import sounddevice as sd
import numpy as np
import math
import os
import sys
import random
import time
from object.bubble import Bubble
from util import setup_display, BLACK

# Configuration
sample_rate = 44100
NUM_BANDS = 25  # Number of frequency bands
TEXT_COLOR = (255, 255, 255)  # White for text
MAX_BUBBLES = 100
volume = 0
bass, midrange, treble = 0, 0, 0
max_volume = 1

# Switch palette every 10 seconds
last_palette_switch = time.time()

stars = []

# Define 5 custom color palettes
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

# Audio Callback
frequency_amplitudes = np.zeros(NUM_BANDS)
peak_positions = np.zeros(NUM_BANDS)
#band_frequencies = np.logspace(np.log10(20), np.log10(sample_rate / 2), NUM_BANDS + 1)
band_frequencies = np.geomspace(20, sample_rate / 2, NUM_BANDS + 1)

def audio_callback(indata, frames, time, status):
    global frequency_amplitudes
    if status:
        print(f"Status: {status}")

    if status != "input overflow":
      
        # Perform FFT
        fft_data = np.abs(np.fft.rfft(indata[:, 0]))  # Use one channel
        freqs = np.fft.rfftfreq(len(indata[:, 0]), 1 / sample_rate)

        # Calculate frequency band amplitudes
        band_amplitudes = np.zeros(NUM_BANDS)
        band_edges = np.logspace(np.log10(20), np.log10(sample_rate / 2), NUM_BANDS + 1)
        
        for i in range(NUM_BANDS):
            #band_amplitudes[i] = np.mean(fft_data[(freqs >= band_edges[i]) & (freqs < band_edges[i + 1])])
            # Extract the frequencies for the current band
            band_data = fft_data[(freqs >= band_frequencies[i]) & (freqs < band_frequencies[i + 1])]
            #print(f"Band {i}: Size = {band_data.size}, Frequency Range = {band_frequencies[i]}-{band_frequencies[i + 1]}")
            
            # Check if the band_data is not empty
            if band_data.size > 0:
                band_amplitudes[i] = np.mean(band_data)
            else:
                band_amplitudes[i] = 0  # Default value for empty bands

        # Smooth neighboring bands for visualization
        for i in range(1, NUM_BANDS - 1):
            if band_amplitudes[i] == 0:
                band_amplitudes[i] = (band_amplitudes[i - 1] + band_amplitudes[i + 1]) / 2

        # Smooth out the amplitudes for a cleaner visualization
        frequency_amplitudes = 0.8 * frequency_amplitudes + 0.2 * band_amplitudes

        # for i, amplitude in enumerate(frequency_amplitudes):
        #     print(f"Band {i}: Amplitude = {amplitude}, Frequency = {band_frequencies[i]:.2f} Hz")


def switch_palette():
    global selected_palette, last_palette_switch, BAR_COLOR_TOP, BAR_COLOR_BOTTOM, BAR_PEAK_COLOR
    if time.time() - last_palette_switch > 30:
        selected_palette = random.choice(list(PALETTES.values()))
        last_palette_switch = time.time()
        BAR_COLOR_TOP = selected_palette[0]
        BAR_COLOR_BOTTOM = selected_palette[1]
        BAR_PEAK_COLOR = selected_palette[2]

def draw_palette_name(screen):
    font = pygame.font.SysFont(None, 36)
    text = font.render(f"Palette: {list(PALETTES.keys())[list(PALETTES.values()).index(selected_palette)]}", True, (255, 255, 255))
    screen.blit(text, (10, 10))

bubbles = []

def create_bubbles(screen, midrange_intensity, color_palette):
    """Create bubbles based on midrange intensity, capped at MAX_BUBBLES."""
    if len(bubbles) >= MAX_BUBBLES:
        return  # Do not create more bubbles if at max limit

    num_bubbles = int(midrange_intensity * 3)  # Scale number of new bubbles
    for _ in range(num_bubbles):
        if len(bubbles) >= MAX_BUBBLES:
            break  # Stop if reaching max limit

        x = random.randint(0, screen.get_width())
        y = screen.get_height()
        size = random.randint(5, 15)  # Smaller base size
        speed = random.uniform(0.5, 1.5)  # Adjust base speed
        color = random.choice(color_palette)
        bubbles.append(Bubble(x, y, size, speed, color))


def update_and_draw_bubbles(screen, bass_intensity, treble_intensity):
    """Update and draw bubbles, removing those that float off-screen."""
    for bubble in bubbles[:]:
        # Gradually increase size with bass intensity
        bubble.size += bass_intensity * 0.3  # Slow growth
        bubble.size = min(150, bubble.size)  # Max size limit

        # Optionally decay size if bass is low
        if bass_intensity < 0.1:  # Low bass
            bubble.size = max(5, bubble.size - 0.1)  # Gradual shrinkage

        # Move the bubble
        bubble.move(treble_intensity)

        # Remove bubble if it floats off-screen
        if bubble.y + bubble.size < 0:
            bubbles.remove(bubble)
        else:
            bubble.draw(screen)


def draw_gradient_background(screen, color_top, color_bottom):
    """Draw a vertical gradient background."""
    for y in range(screen.get_height()):
        blend = y / screen.get_height()
        r = int(color_top[0] * (1 - blend) + color_bottom[0] * blend)
        g = int(color_top[1] * (1 - blend) + color_bottom[1] * blend)
        b = int(color_top[2] * (1 - blend) + color_bottom[2] * blend)
        pygame.draw.line(screen, (r, g, b), (0, y), (screen.get_width(), y))


def main(display: str,
    video_driver: str,
    screen_width: int,
    screen_height: int,
    samplerate: int,
    channels: int,
    device_index: int,
    blocksize: int,
    latency: float,
):
    
    #setup the display
    screen = setup_display(display, video_driver, screen_width, screen_height)

    sample_rate = samplerate
    
    # Randomly select a palette at the start
    selected_palette = random.choice(list(PALETTES.values()))
    
    # start audio stream
    with sd.InputStream(
        samplerate=samplerate,
        channels=channels,
        device=device_index,
        callback=audio_callback,
        blocksize=blocksize,
        latency=latency,
    ):
        try:
            while True:
            
                screen.fill(BLACK)
            
                draw_gradient_background(screen, (0, 0, 64), (0, 0, 128))

                # Calculate music intensities
                if frequency_amplitudes.size > 0:
                    midrange_intensity = np.clip(np.mean(frequency_amplitudes[NUM_BANDS // 3:NUM_BANDS * 2 // 3]), 0, 1)
                    bass_intensity = np.clip(np.mean(frequency_amplitudes[:NUM_BANDS // 3]), 0, 1)
                    treble_intensity = np.clip(np.mean(frequency_amplitudes[NUM_BANDS * 2 // 3:]), 0, 1)
                else:
                    midrange_intensity = bass_intensity = treble_intensity = 0

                # Create, update, and draw bubbles
                create_bubbles(screen, midrange_intensity, selected_palette)
                update_and_draw_bubbles(screen, bass_intensity, treble_intensity)

                switch_palette()

                #draw_palette_name(screen)
                
                pygame.display.update()

                pygame.time.wait(10)

        except KeyboardInterrupt:
            pygame.quit()
            sys.exit()
