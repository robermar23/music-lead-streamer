import pygame
import sounddevice as sd
import numpy as np
import math
import os
import sys

# Configuration
DEVICE_INDEX = 1
SAMPLE_RATE = 44100
CHANNELS = 2
BLOCKSIZE = 1024
LATENCY = "high"
BLACK = (0, 0, 0)
volume = 0
bass, midrange, treble = 0, 0, 0

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

# Function to generate smooth gradient colors
def get_smooth_color(t):
    r = int((math.sin(t) * 127 + 128) % 255)
    g = int((math.sin(t + 2) * 127 + 128) % 255)
    b = int((math.sin(t + 4) * 127 + 128) % 255)
    return (r, g, b)

# Draw radial patterns based on frequency bands
def draw_radial_patterns():
    global screen, volume, bass, midrange, treble
    screen.fill(BLACK)

    # Get a smooth gradient color based on time
    t = pygame.time.get_ticks() / 1000
    color = get_smooth_color(t)

    # Center of the screen
    center_x, center_y = screen.get_width() // 2, screen.get_height() // 2

    # Adjust bass influence to control ring expansion
    max_radius = 50 + np.log1p(bass) * 200  # Logarithmic scaling to soften bass influence
    damping = 0.9  # Damping factor to smooth transitions

    # Draw expanding rings
    for i in range(10):
        radius = int(max_radius * (i / 10) * damping)
        pygame.draw.circle(screen, color, (center_x, center_y), radius, 2)

    # Draw rotating spiral
    num_points = int(midrange * 50)
    if num_points > 0:
        angle_step = 2 * math.pi / num_points
        for i in range(num_points):
            angle = i * angle_step + t
            x = center_x + int(max_radius * math.cos(angle) * (i / num_points))
            y = center_y + int(max_radius * math.sin(angle) * (i / num_points))
            pygame.draw.circle(screen, color, (x, y), 5)

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
            draw_radial_patterns()
            pygame.time.wait(50)

    except KeyboardInterrupt:
        pygame.quit()
        sys.exit()
