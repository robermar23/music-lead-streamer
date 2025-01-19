import pygame
import sounddevice as sd
import numpy as np
import math
import os
import sys
from util import BLACK

# Configuration
sample_rate = 44100
volume = 0
bass, midrange, treble = 0, 0, 0

# Audio callback
def audio_callback(indata, frames, time, status):
    global volume, bass, midrange, treble
    if status:
        print(f"Status: {status}")

    # Calculate the volume
    volume = np.linalg.norm(indata) / np.sqrt(indata.size)

    # Perform FFT on the audio data
    fft_data = np.abs(np.fft.rfft(indata[:, 0]))  # Use one channel
    freqs = np.fft.rfftfreq(len(indata[:, 0]), 1 / sample_rate)

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
def draw_radial_patterns(screen):
    global  volume, bass, midrange, treble

    # Get a smooth gradient color based on time
    t = pygame.time.get_ticks() / 1000
    color = get_smooth_color(t)

    # Center of the screen
    center_x, center_y = screen.get_width() // 2, screen.get_height() // 2

    # Adjust bass influence to control ring expansion
    max_radius = 50 + np.log1p(bass) * 175  # Logarithmic scaling to soften bass influence
    damping = 0.9  # Damping factor to smooth transitions

    # Draw expanding rings
    for i in range(10):
        radius = int(max_radius * (i / 10) * damping)
        pygame.draw.circle(screen, color, (center_x, center_y), radius, 2)

    # Draw rotating spiral
    num_points = int(midrange * 150)
    if num_points > 0:
        angle_step = 2 * math.pi / num_points
        for i in range(num_points):
            angle = i * angle_step + t
            x = center_x + int(max_radius * math.cos(angle) * (i / num_points))
            y = center_y + int(max_radius * math.sin(angle) * (i / num_points))
            pygame.draw.circle(screen, color, (x, y), 2)


# Global state for the show
def initialize(audio_settings, screen):
    """Initialize the show."""
    global audio_stream
    
    # Extract audio settings
    samplerate, channels, device_index, blocksize, latency = audio_settings

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
    draw_radial_patterns(screen)
    pygame.display.update()

def cleanup():
    """Clean up resources for the show."""
    global audio_stream
    if audio_stream:
        audio_stream.stop()
        audio_stream.close()