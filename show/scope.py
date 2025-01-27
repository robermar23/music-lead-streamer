import pygame
import sounddevice as sd
import numpy as np
import random
import time
import colorsys
import math
from util import BLACK, PALETTES

# Constants
sample_rate = 44100
volume = 0
max_volume = 0
bass, midrange, treble = 0, 0, 0

NUM_SLICES = 8  # Number of slices in the kaleidoscope
TRIANGLE_SIZE = 50  # Size of the equilateral triangles

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

# Draw a Single Triangle
def draw_triangle(surface, x, y, size, orientation, color, glow_color=None):
    """Draw a single triangle with optional glow effect."""
    if glow_color:
        for i in range(4, 0, -1):  # Draw larger, semi-transparent triangles for glow
            alpha = int(255 * (i / 4))  # Fade glow layers
            glow_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.polygon(
                glow_surface, (*glow_color, alpha),
                [(x - size / 2 * i, y + size * math.sqrt(3) / 2 * i),
                 (x, y - size * math.sqrt(3) / 2 * i),
                 (x + size / 2 * i, y + size * math.sqrt(3) / 2 * i)]
            )
            surface.blit(glow_surface, (x - size, y - size))

    # Draw the triangle itself
    points = [
        (x, y),
        (x + size / 2, y + size * math.sqrt(3) / 2) if orientation == 'up' else (x + size / 2, y - size * math.sqrt(3) / 2),
        (x - size / 2, y + size * math.sqrt(3) / 2) if orientation == 'up' else (x - size / 2, y - size * math.sqrt(3) / 2)
    ]
    pygame.draw.polygon(surface, color, points)


# Draw Kaleidoscope
def draw_kaleidoscope(screen, bass, midrange, treble):
    """Draw the kaleidoscope with a tessellated triangle grid."""
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    base_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    height = TRIANGLE_SIZE * math.sqrt(3) / 2
    num_rows = int(screen_height / height) + 1
    num_cols = int(screen_width / TRIANGLE_SIZE) + 1

    for row in range(num_rows):
        for col in range(num_cols):
            # Position of the triangle
            x = col * TRIANGLE_SIZE
            y = row * height
            if row % 2 == 1:
                x += TRIANGLE_SIZE / 2  # Offset every other row

            # Triangle orientation
            orientation = 'up' if (row + col) % 2 == 0 else 'down'

            # Smooth fading effect for brightness
            #brightness = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 500 + row + col)
            brightness = bass * math.sin(pygame.time.get_ticks() / 500 + row + col)

            # Color based on audio
            hue = treble 
            saturation = 1  # Full saturation
            # Convert HSV to RGB
            rgb = colorsys.hsv_to_rgb(hue, saturation, brightness)
            color = tuple(int(c * 255) for c in rgb)  # Scale to [0, 255]

            # Generate glow color with reduced brightness
            glow_brightness = brightness * 0.5
            glow_rgb = colorsys.hsv_to_rgb(hue, saturation, glow_brightness)
            glow_color = tuple(int(c * 255) for c in glow_rgb)

            # Draw triangle with glow
            draw_triangle(base_surface, x, y, TRIANGLE_SIZE, orientation, color, glow_color)

    # Symmetry: Create kaleidoscope slices
    for i in range(NUM_SLICES):
        angle = i * (360 / NUM_SLICES)
        rotated_surface = pygame.transform.rotate(base_surface, angle)
        screen.blit(rotated_surface, (0, 0))


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

    global selected_palette, bass, midrange, treble

    screen.fill(BLACK)

    # Draw the kaleidoscope
    draw_kaleidoscope(screen, bass, midrange, treble)

    # Update the display
    pygame.display.update()

    pygame.time.wait(100)

def cleanup():
    """Clean up resources for the show."""
    global audio_stream
    if audio_stream:
        audio_stream.stop()
        audio_stream.close()