import pygame
import sounddevice as sd
import numpy as np
import math
import os
import sys
import random
import time
from object.star import Star
from util import BLACK, PALETTES

# Configuration
sample_rate = 44100
volume = 0
bass, midrange, treble = 0, 0, 0
stars = []
max_volume = 1

# Switch palette every 10 seconds
last_palette_switch = time.time()

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
    return selected_palette

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
            #size = random.randint(2, 10)
            size = max(5, int((treble + midrange) * 2))
            stars.append(Star(center_x, center_y, color, size, midrange, treble))

    # Update and draw stars
    for star in stars[:]:
        star.move()
        star.draw(screen)
        if not star.is_alive():
            stars.remove(star)


def get_smooth_color(selected_palette, bass, midrange, treble, max_volume=1):
    """Generates a vibrant color based on frequency bands and the selected palette."""
    # Normalize each frequency band relative to max volume
    bass_norm = bass / max_volume
    midrange_norm = midrange / max_volume
    treble_norm = treble / max_volume

    # Apply a weighting factor to enhance vibrancy
    bass_weight = bass_norm**2
    midrange_weight = midrange_norm**2
    treble_weight = treble_norm**2

    # Normalize weights to sum up to 1
    total_weight = bass_weight + midrange_weight + treble_weight
    if total_weight > 0:
        bass_weight /= total_weight
        midrange_weight /= total_weight
        treble_weight /= total_weight

    # Get colors from the selected palette
    color_bass = selected_palette[0]
    color_mid = selected_palette[1]
    color_treble = selected_palette[2]

    # Interpolate between the colors based on adjusted weights
    red = int(bass_weight * color_bass[0] + midrange_weight * color_mid[0] + treble_weight * color_treble[0])
    green = int(bass_weight * color_bass[1] + midrange_weight * color_mid[1] + treble_weight * color_treble[1])
    blue = int(bass_weight * color_bass[2] + midrange_weight * color_mid[2] + treble_weight * color_treble[2])

    # Clamp values to ensure valid RGB values
    return (
        max(0, min(255, red)),
        max(0, min(255, green)),
        max(0, min(255, blue)),
    )

# Function to draw the gradient background
def draw_gradient_background(screen, width, height, colors):
    for y in range(height):
        t = y / height
        r = int(colors[0][0] * (1 - t) + colors[1][0] * t)
        g = int(colors[0][1] * (1 - t) + colors[1][1] * t)
        b = int(colors[0][2] * (1 - t) + colors[1][2] * t)
        pygame.draw.line(screen, (r, g, b), (0, y), (width, y))
        
# Global state for the show
def initialize(audio_settings, screen):
    """Initialize the show."""
    global audio_stream, selected_palette, sample_rate
    
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

    global selected_palette

    screen_width, screen_height = screen.get_width(), screen.get_height()
    draw_gradient_background(screen, screen_width, screen_height, selected_palette)

    draw_radial_patterns(screen, selected_palette)

    selected_palette = switch_palette(selected_palette)

    draw_palette_name(screen, selected_palette)

    pygame.display.update()
    #pygame.time.wait(10)

def cleanup():
    """Clean up resources for the show."""
    global audio_stream
    if audio_stream:
        audio_stream.stop()
        audio_stream.close()