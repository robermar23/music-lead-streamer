import pygame
import sounddevice as sd
import numpy as np
import math
import os
import sys
import random
import time
from object.star import Star
from util import BLACK

# Configuration
sample_rate = 44100
volume = 0
bass, midrange, treble = 0, 0, 0
stars = []
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
    "Cosmic Dream": [(18, 10, 143), (75, 0, 130), (139, 0, 139)],
    "Monochrome Fade": [(0, 0, 0), (128, 128, 128), (255, 255, 255)],
    "Techno Pulse": [(0, 255, 0), (0, 255, 255), (255, 20, 147)],
    "Desert Glow": [(210, 180, 140), (244, 164, 96), (70, 130, 180)],
}

# Audio callback
def audio_callback(indata, frames, time, status):
    global volume, bass, midrange, treble, max_volume
    if status:
        print(f"Status: {status}")

    if status != "input overflow":
        # Calculate the volume
        volume = np.linalg.norm(indata) / np.sqrt(indata.size)

        # Update max volume
        max_volume = max(max_volume, volume)

        # Perform FFT on the audio data
        fft_data = np.abs(np.fft.rfft(indata[:, 0]))  # Use one channel
        freqs = np.fft.rfftfreq(len(indata[:, 0]), 1 / sample_rate)

        # Bass (20-250 Hz), Midrange (250-4000 Hz), Treble (4000-20000 Hz)
        bass = np.mean(fft_data[(freqs >= 20) & (freqs < 250)])
        midrange = np.mean(fft_data[(freqs >= 250) & (freqs < 4000)])
        treble = np.mean(fft_data[(freqs >= 4000)])

def switch_palette(selected_palette):
    global last_palette_switch
    if time.time() - last_palette_switch > 30:
        selected_palette = random.choice(list(PALETTES.values()))
        last_palette_switch = time.time()

def draw_palette_name(screen, selected_palette):
    font = pygame.font.SysFont(None, 36)
    text = font.render(f"Palette: {list(PALETTES.keys())[list(PALETTES.values()).index(selected_palette)]}", True, (255, 255, 255))
    screen.blit(text, (10, 10))

def get_smooth_color(selected_palette, bass, midrange, treble, max_volume=1):
    """Generates a color based on frequency bands and the selected palette."""
    # Normalize each frequency band relative to max volume
    bass_norm = min(1, bass / max_volume)
    midrange_norm = min(1, midrange / max_volume)
    treble_norm = min(1, treble / max_volume)

    # Get colors from the selected palette
    color_bass = selected_palette[0]
    color_mid = selected_palette[1]
    color_treble = selected_palette[2]

    # Interpolate between the colors based on frequency bands
    red = int(bass_norm * color_bass[0] + midrange_norm * color_mid[0] + treble_norm * color_treble[0])
    green = int(bass_norm * color_bass[1] + midrange_norm * color_mid[1] + treble_norm * color_treble[1])
    blue = int(bass_norm * color_bass[2] + midrange_norm * color_mid[2] + treble_norm * color_treble[2])

    # Clamp values to ensure valid RGB values
    return (
        max(0, min(255, red)),
        max(0, min(255, green)),
        max(0, min(255, blue)),
    )

# Draw radial patterns based on frequency bands
def draw_radial_patterns(screen, selected_palette):

    global volume, bass, midrange, treble, max_volume
    
    # Get a balanced color based on the frequency bands
    color = get_smooth_color(selected_palette, bass, midrange, treble, max_volume)

    # Center of the screen
    center_x, center_y = screen.get_width() // 2, screen.get_height() // 2

   # Spawn new stars based on bass, midrange, and treble
    if bass > 0:
        for _ in range(int(bass / 2)):
            size = random.randint(2, 10)
            stars.append(Star(center_x, center_y, color, size, midrange, treble))

    # Update and draw stars
    for star in stars[:]:
        star.move()
        star.draw(screen)
        if not star.is_alive():
            stars.remove(star)


def get_smooth_color(selected_palette, bass, midrange, treble, max_volume=1):
    """Generates a color based on frequency bands and the selected palette."""
    # Normalize each frequency band relative to max volume
    bass_norm = min(1, bass / max_volume)
    midrange_norm = min(1, midrange / max_volume)
    treble_norm = min(1, treble / max_volume)

    # Get colors from the selected palette
    color_bass = selected_palette[0]
    color_mid = selected_palette[1]
    color_treble = selected_palette[2]

    # Interpolate between the colors based on frequency bands
    red = int(bass_norm * color_bass[0] + midrange_norm * color_mid[0] + treble_norm * color_treble[0])
    green = int(bass_norm * color_bass[1] + midrange_norm * color_mid[1] + treble_norm * color_treble[1])
    blue = int(bass_norm * color_bass[2] + midrange_norm * color_mid[2] + treble_norm * color_treble[2])

    # Clamp values to ensure valid RGB values
    return (
        max(0, min(255, red)),
        max(0, min(255, green)),
        max(0, min(255, blue)),
    )

# Global state for the show
def initialize(audio_settings, screen):
    """Initialize the show."""
    global audio_stream, selected_palette
    
    # Extract audio settings
    samplerate, channels, device_index, blocksize, latency = audio_settings

    sample_rate = samplerate

    # Randomly select a palette at the start
    selected_palette = random.choice(list(PALETTES.values()))

    # Initialize audio stream
    audio_stream = sd.InputStream(
        samplerate=samplerate,
        channels=channels,
        device=device_index,
        callback=audio_callback,
        blocksize=blocksize,
        latency=latency,
    )
    audio_stream.start()

def render_step(screen):
    """Render a single frame of the visualization."""
    screen.fill(BLACK)

    draw_radial_patterns(screen, selected_palette)

    switch_palette(selected_palette)

    draw_palette_name(screen, selected_palette)

    pygame.display.update()
    #pygame.time.wait(10)

def cleanup():
    """Clean up resources for the show."""
    global audio_stream
    if audio_stream:
        audio_stream.stop()
        audio_stream.close()