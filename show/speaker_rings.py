import pygame
import sounddevice as sd
import numpy as np
import math
import os
import sys
import random
import time
from object.particle import RingParticle
from util import BLACK

# Configuration
sample_rate = 44100
volume = 0
bass, midrange, treble = 0, 0, 0
particles = []
ring_particles = []
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
    "Aurora Lights": [(0, 255, 127), (123, 104, 238), (0, 128, 255)],
    "Lava Flow": [(255, 69, 0), (255, 99, 71), (205, 92, 92)],
    "Rainbow Vibes": [(148, 0, 211), (75, 0, 130), (0, 0, 255)],
    "Crystal Cave": [(0, 206, 209), (72, 209, 204), (127, 255, 212)],
    "Electric Neon": [(0, 255, 255), (255, 0, 0), (255, 255, 0)],
    "Flaming Sun": [(255, 69, 0), (255, 215, 0), (255, 165, 0)],
    "Ethereal Mist": [(240, 248, 255), (224, 255, 255), (175, 238, 238)],
    "Night Drive": [(25, 25, 112), (0, 0, 0), (255, 0, 0)],
    "Mystic Woods": [(34, 139, 34), (46, 139, 87), (0, 100, 0)],
    "Polar Night": [(0, 51, 102), (0, 102, 204), (51, 153, 255)],
    "Frosted Glass": [(173, 216, 230), (224, 255, 255), (135, 206, 250)],
    "Vivid Spectrum": [(255, 0, 0), (0, 255, 0), (0, 0, 255)],
    "Starlit Sky": [(25, 25, 112), (72, 61, 139), (123, 104, 238)],
    "Jungle Fever": [(0, 128, 0), (85, 107, 47), (124, 252, 0)],
    "Golden Hour": [(255, 223, 0), (255, 140, 0), (255, 69, 0)],
    "Tech Glow": [(0, 255, 255), (255, 105, 180), (50, 205, 50)],
    "Solar Flare": [(255, 69, 0), (255, 165, 0), (255, 215, 0)],
    "Iceberg": [(176, 224, 230), (173, 216, 230), (70, 130, 180)],
    "Festival Lights": [(255, 0, 0), (0, 255, 0), (0, 0, 255)],
    "Dreamy Pastels": [(250, 218, 221), (230, 230, 250), (255, 228, 225)],
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
    return selected_palette

def draw_palette_name(screen, selected_palette):
    font = pygame.font.SysFont(None, 36)
    text = font.render(f"Palette: {list(PALETTES.keys())[list(PALETTES.values()).index(selected_palette)]}", True, (255, 255, 255))
    screen.blit(text, (10, 10))

def get_smooth_color(selected_palette, bass, midrange, treble, max_volume=1):
    """Generates a vibrant color based on frequency bands and the selected palette."""
    # Normalize each frequency band relative to max volume
    bass_norm = min(1, bass / max_volume)
    midrange_norm = min(1, midrange / max_volume)
    treble_norm = min(1, treble / max_volume)

    # Add weights to emphasize specific bands (adjust as needed)
    bass_weight = 1.0
    midrange_weight = 1.2
    treble_weight = 1.0

    # Get colors from the selected palette
    color_bass = selected_palette[0]
    color_mid = selected_palette[1]
    color_treble = selected_palette[2]

    # Adjust weights and interpolate between the colors
    red = int(
        bass_weight * bass_norm * color_bass[0] +
        midrange_weight * midrange_norm * color_mid[0] +
        treble_weight * treble_norm * color_treble[0]
    )
    green = int(
        bass_weight * bass_norm * color_bass[1] +
        midrange_weight * midrange_norm * color_mid[1] +
        treble_weight * treble_norm * color_treble[1]
    )
    blue = int(
        bass_weight * bass_norm * color_bass[2] +
        midrange_weight * midrange_norm * color_mid[2] +
        treble_weight * treble_norm * color_treble[2]
    )

    # Normalize to ensure RGB values are within 0-255
    max_value = max(red, green, blue, 255)  # Prevent division by zero
    red = int((red / max_value) * 255)
    green = int((green / max_value) * 255)
    blue = int((blue / max_value) * 255)

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

    # print (f"Treble: {treble}")
    # print (f"Bass: {bass}")
    # print (f"Midrange {midrange}")
    # Center of the screen
    center_x, center_y = screen.get_width() // 2, screen.get_height() // 2

    ring_particle_count = int(int(bass) / 3)
    if ring_particle_count < 1:
        ring_particle_count = 1
    # RINGS #
     # Spawn new ring particles based on bass
    for _ in range(ring_particle_count):
        #initial_radius = treble * midrange / 100
        initial_radius = bass * 0.25
        #print (f"Initial radius: {initial_radius}")
        ring_particles.append(RingParticle(center_x, center_y, color, initial_radius, bass))

    # Update and draw ring particles
    for ring in ring_particles[:]:
        ring.expand()
        ring.draw(screen)
        if not ring.is_alive():
            ring_particles.remove(ring)
    
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

    global selected_palette

    screen.fill(BLACK)

    draw_radial_patterns(screen, selected_palette)

    selected_palette = switch_palette(selected_palette)

    draw_palette_name(screen, selected_palette)

    pygame.display.update()

    pygame.time.wait(25)


def cleanup():
    """Clean up resources for the show."""
    global audio_stream
    if audio_stream:
        audio_stream.stop()
        audio_stream.close()