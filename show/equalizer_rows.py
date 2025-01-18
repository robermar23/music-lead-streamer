import pygame
import sounddevice as sd
import numpy as np
import math
import os
import sys
import random
import time

# Configuration
DEVICE_INDEX = 1
SAMPLE_RATE = 44100
CHANNELS = 2
BLOCKSIZE = 1024
LATENCY = "high"
NUM_BANDS = 30  # Number of frequency bands
BAR_WIDTH = 20  # Width of each bar
BAR_SPACING = 5  # Space between bars
BAR_COLOR_TOP = (0, 255, 0)  # Green color for bars
BAR_COLOR_BOTTOM = (0, 100, 0)
COLORS = {"bass": (0, 255, 0), "midrange": (0, 0, 255), "treble": (255, 0, 0)}  # Colors for rows
BLACK = (0, 0, 0)

volume = 0
bass, midrange, treble = 0, 0, 0
max_volume = 1

# Switch palette every 10 seconds
last_palette_switch = time.time()

# Define 5 custom color palettes
PALETTES = {
    "Neon Glow": [(255, 0, 255), (0, 255, 255), (255, 255, 0)],
    "Pastel Dream": [(255, 182, 193), (176, 224, 230), (221, 160, 221)],
    "Fire & Ice": [(255, 69, 0), (0, 191, 255), (255, 140, 0)],
    "Galaxy": [(72, 61, 139), (123, 104, 238), (25, 25, 112)],
    "Cyberpunk": [(255, 20, 147), (0, 255, 127), (75, 0, 130)],
    "Sunset Bliss": [(255, 94, 77), (255, 165, 0), (138, 43, 226)],
    "Arctic Chill": [(173, 216, 230), (0, 0, 139), (0, 128, 128)],
    "Retro Pop": [(255, 20, 147), (50, 205, 50), (255, 255, 0)],
    "Deep Space": [(0, 0, 0), (48, 25, 52), (255, 0, 255)],
    "Forest Mist": [(34, 139, 34), (144, 238, 144), (139, 69, 19)],
    "Tropical Sunset": [(255, 87, 51), (255, 195, 113), (255, 87, 159)],
    "Ocean Breeze": [(0, 128, 128), (0, 191, 255), (64, 224, 208)],
    "Autumn Forest": [(139, 69, 19), (205, 133, 63), (85, 107, 47)],
    "Electric Storm": [(25, 25, 112), (138, 43, 226), (255, 255, 0)],
    "Candy Pop": [(255, 105, 180), (135, 206, 250), (255, 182, 193)],
    "Volcano Blast": [(255, 69, 0), (255, 140, 0), (255, 215, 0)],
    "Cos    mic Dream": [(18, 10, 143), (75, 0, 130), (139, 0, 139)],
    "Monochrome Fade": [(0, 0, 0), (128, 128, 128), (255, 255, 255)],
    "Techno Pulse": [(0, 255, 0), (0, 255, 255), (255, 20, 147)],
    "Desert Glow": [(210, 180, 140), (244, 164, 96), (70, 130, 180)],
}

# Initialize display
def setup_display():
    os.putenv("DISPLAY", ":0")
    os.putenv("SDL_VIDEODRIVER", "x11")

    pygame.display.init()
    size = (800, 480)
    global screen
    screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
    screen.fill(BLACK)
    pygame.font.init()
    pygame.display.update()

# Audio Callback

bass_amplitudes = np.zeros(NUM_BANDS)
midrange_amplitudes = np.zeros(NUM_BANDS)
treble_amplitudes = np.zeros(NUM_BANDS)

def audio_callback(indata, frames, time, status):
    global bass_amplitudes, midrange_amplitudes, treble_amplitudes
    if status:
        print(f"Status: {status}")

    if status != "input overflow":
        # Perform FFT
        fft_data = np.abs(np.fft.rfft(indata[:, 0]))  # Use one channel
        freqs = np.fft.rfftfreq(len(indata[:, 0]), 1 / SAMPLE_RATE)

        # Calculate frequency band amplitudes
        band_edges = np.logspace(np.log10(20), np.log10(SAMPLE_RATE / 2), NUM_BANDS * 3 + 1)

        # Divide bands into bass, midrange, and treble
        bass = fft_data[(freqs >= band_edges[0]) & (freqs < band_edges[NUM_BANDS])]
        midrange = fft_data[(freqs >= band_edges[NUM_BANDS]) & (freqs < band_edges[NUM_BANDS * 2])]
        treble = fft_data[(freqs >= band_edges[NUM_BANDS * 2]) & (freqs < band_edges[-1])]
        
        print(f"Bass length: {len(bass)}, Midrange length: {len(midrange)}, Treble length: {len(treble)}")


         # Ensure we have enough data points
        if len(bass) >= NUM_BANDS:
            bass_amplitudes = [np.mean(bass[i:i + max(1, len(bass) // NUM_BANDS)]) for i in range(0, len(bass), max(1, len(bass) // NUM_BANDS))]
        else:
            # Fallback: Zero amplitudes if there's insufficient data
            bass_amplitudes = np.zeros(NUM_BANDS)

        if  len(midrange) >= NUM_BANDS:
            midrange_amplitudes = [np.mean(midrange[i:i + max(1, len(midrange) // NUM_BANDS)]) for i in range(0, len(midrange), max(1, len(midrange) // NUM_BANDS))]
        else:
            midrange_amplitudes = np.zeros(NUM_BANDS)

        if len(treble) >= NUM_BANDS:
            treble_amplitudes = [np.mean(treble[i:i + max(1, len(treble) // NUM_BANDS)]) for i in range(0, len(treble), max(1, len(treble) // NUM_BANDS))]
        else:
            treble_amplitudes = np.zeros(NUM_BANDS)



def switch_palette():
    global selected_palette, last_palette_switch, BAR_COLOR_TOP, BAR_COLOR_BOTTOM
    if time.time() - last_palette_switch > 30:
        selected_palette = random.choice(list(PALETTES.values()))
        last_palette_switch = time.time()
        BAR_COLOR_TOP = selected_palette[0]
        BAR_COLOR_BOTTOM = selected_palette[2]

def draw_palette_name():
    font = pygame.font.SysFont(None, 36)
    text = font.render(f"Palette: {list(PALETTES.keys())[list(PALETTES.values()).index(selected_palette)]}", True, (255, 255, 255))
    screen.blit(text, (10, 10))

def draw_gradient_bar(screen, x, y, width, height, color_top, color_bottom):
    """Draws a bar with a gradient effect."""
    for i in range(height):
        blend = i / height
        r = int(color_top[0] * (1 - blend) + color_bottom[0] * blend)
        g = int(color_top[1] * (1 - blend) + color_bottom[1] * blend)
        b = int(color_top[2] * (1 - blend) + color_bottom[2] * blend)
        pygame.draw.line(screen, (r, g, b), (x, y + i), (x + width, y + i))

def draw_frequency_amplitudes():

    #global BAR_COLOR_TOP, BAR_COLOR_BOTTOM
  # Clear the screen
    screen.fill(BLACK)

    # Draw the bass row
    for i, amplitude in enumerate(bass_amplitudes):
        bar_height = int(amplitude * 300)  # Scale amplitude to screen height
        x = i * (BAR_WIDTH + BAR_SPACING)
        y = screen.get_height() - bar_height  # Bottom of the screen
        pygame.draw.rect(screen, COLORS["bass"], (x, y, BAR_WIDTH, bar_height))

    # Draw the midrange row
    for i, amplitude in enumerate(midrange_amplitudes):
        bar_height = int(amplitude * 300)  # Scale amplitude to screen height
        x = i * (BAR_WIDTH + BAR_SPACING)
        y = (screen.get_height() // 2) - (bar_height // 2)  # Middle of the screen
        pygame.draw.rect(screen, COLORS["midrange"], (x, y, BAR_WIDTH, bar_height))

    # Draw the treble row
    for i, amplitude in enumerate(treble_amplitudes):
        bar_height = int(amplitude * 300)  # Scale amplitude to screen height
        x = i * (BAR_WIDTH + BAR_SPACING)
        y = bar_height  # Top of the screen
        pygame.draw.rect(screen, COLORS["treble"], (x, y, BAR_WIDTH, bar_height))

    #draw_palette_name()

    # Update the display
    pygame.display.update()

# Main
setup_display()

# Randomly select a palette at the start
selected_palette = random.choice(list(PALETTES.values()))
print (f"Selected Color Palette: {selected_palette}")

with sd.InputStream(
    samplerate=SAMPLE_RATE,
    channels=CHANNELS,
    device=DEVICE_INDEX,
    callback=audio_callback,
    blocksize=BLOCKSIZE,
    latency=LATENCY
):
    try:
        while True:
          draw_frequency_amplitudes()  
          switch_palette()
          pygame.time.wait(10)

    except KeyboardInterrupt:
        pygame.quit()
        sys.exit()
