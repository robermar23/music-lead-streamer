import pygame
import sounddevice as sd
import numpy as np
import random
import os
import sys
import math


# Configuration
DEVICE_INDEX = 1
SAMPLE_RATE = 44100
CHANNELS = 2
BLOCKSIZE = 1024
LATENCY = "high"
BLACK = (0, 0, 0)

# Colors to cycle through
COLORS = [
    (255, 0, 0),   # Red
    (0, 255, 0),   # Green
    (0, 0, 255),   # Blue
    (255, 255, 0), # Yellow
    (0, 255, 255), # Cyan
    (255, 0, 255)  # Magenta
]

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

# Audio callback
volume = 0
bass, midrange, treble = 0, 0, 0

def audio_callback(indata, frames, time, status):
    global volume, bass, midrange, treble
    if status:
        print(f"Status: {status}")

    # Calculate the volume
    volume = np.linalg.norm(indata) / np.sqrt(indata.size)

    # Perform FFT on the audio data
    fft_data = np.abs(np.fft.rfft(indata[:, 0]))  # Use one channel
    freqs = np.fft.rfftfreq(len(indata[:, 0]), 1 / SAMPLE_RATE)

    # Bass (20-250 Hz), Midrange (250-4000 Hz), Treble (4000-20000 Hz)
    bass = np.mean(fft_data[(freqs >= 20) & (freqs < 250)])
    midrange = np.mean(fft_data[(freqs >= 250) & (freqs < 4000)])
    treble = np.mean(fft_data[(freqs >= 4000)])

def get_smooth_color(t):
    """Generates a smooth gradient color based on time (t)."""
    r = int((math.sin(t) * 127 + 128) % 255)
    g = int((math.sin(t + 2) * 127 + 128) % 255)
    b = int((math.sin(t + 4) * 127 + 128) % 255)
    return (r, g, b)

# Draw shapes based on frequency bands
def draw_shapes1():
    global screen, volume, bass, midrange, treble
    screen.fill(BLACK)

    # Determine the size of shapes based on volume
    shape_size = int(volume * 100)

    # Randomly select a color based on treble
    color_index = int(treble) % len(COLORS)
    #color = COLORS[color_index]
    color = tuple(
        max(0, min(255, int((1 - treble) * start + treble * end)))
        for start, end in zip(COLORS[color_index], COLORS[(color_index + 1) % len(COLORS)])
    )

    # Draw shapes based on bass and midrange
    num_shapes = int(bass * 2)
    for _ in range(num_shapes):
        shape_type = random.choice(['circle', 'rect', 'line', 'triangle'])
        x, y = random.randint(0, 800), random.randint(0, 480)
        if shape_size > 10:
            size = random.randint(10, shape_size)
        else:
            size = 1

        if shape_type == 'circle':
            pygame.draw.circle(screen, color, (x, y), size)
        elif shape_type == 'rect':
            pygame.draw.rect(screen, color, (x, y, size, size))
        elif shape_type == 'line':
            end_x, end_y = x + random.randint(-100, 100), y + random.randint(-100, 100)
            pygame.draw.line(screen, color, (x, y), (end_x, end_y), 2)
        elif shape_type == 'triangle':
            points = [(x, y), (x + size, y), (x + size // 2, y - size)]
            pygame.draw.polygon(screen, color, points)

    pygame.display.update()

def draw_shapes2():
    global screen, volume, bass, midrange, treble
    screen.fill(BLACK)

    # Determine the size of shapes based on volume
    shape_size = int(volume * 100)

    # Get a smooth gradient color based on time
    t = pygame.time.get_ticks() / 1000  # Time in seconds
    color = get_smooth_color(t)

    # Draw shapes based on bass and midrange
    num_shapes = int(bass * 2)
    for _ in range(num_shapes):
        shape_type = random.choice(['circle', 'rect', 'line', 'triangle'])
        x, y = random.randint(0, 800), random.randint(0, 480)
        if shape_size > 10:
            size = random.randint(10, shape_size)
        else:
            size = 1

        if shape_type == 'circle':
            pygame.draw.circle(screen, color, (x, y), size)
        elif shape_type == 'rect':
            pygame.draw.rect(screen, color, (x, y, size, size))
        elif shape_type == 'line':
            end_x, end_y = x + random.randint(-100, 100), y + random.randint(-100, 100)
            pygame.draw.line(screen, color, (x, y), (end_x, end_y), 2)
        elif shape_type == 'triangle':
            points = [(x, y), (x + size, y), (x + size // 2, y - size)]
            pygame.draw.polygon(screen, color, points)

    pygame.display.update()


# Main
setup_display()
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
            draw_shapes2()
            pygame.time.wait(100)  # Introduces a delay to slow down the drawing

    except KeyboardInterrupt:
        pygame.quit()
        sys.exit()
