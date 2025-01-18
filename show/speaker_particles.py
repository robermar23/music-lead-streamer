import pygame
import sounddevice as sd
import numpy as np
import math
import os
import sys
import random
import time
from object.particle import Particle, RingParticle

# Configuration
DEVICE_INDEX = 1
SAMPLE_RATE = 44100
CHANNELS = 2
BLOCKSIZE = 1024
LATENCY = "high"
BLACK = (0, 0, 0)
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
        freqs = np.fft.rfftfreq(len(indata[:, 0]), 1 / SAMPLE_RATE)

        # Bass (20-250 Hz), Midrange (250-4000 Hz), Treble (4000-20000 Hz)
        bass = np.mean(fft_data[(freqs >= 20) & (freqs < 250)])
        midrange = np.mean(fft_data[(freqs >= 250) & (freqs < 4000)])
        treble = np.mean(fft_data[(freqs >= 4000)])

def switch_palette():
    global selected_palette, last_palette_switch
    if time.time() - last_palette_switch > 30:
        selected_palette = random.choice(list(PALETTES.values()))
        last_palette_switch = time.time()

def draw_palette_name():
    font = pygame.font.SysFont(None, 36)
    text = font.render(f"Palette: {list(PALETTES.keys())[list(PALETTES.values()).index(selected_palette)]}", True, (255, 255, 255))
    screen.blit(text, (10, 10))

def get_smooth_color(bass, midrange, treble, max_volume=1):
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
def draw_radial_patterns():

    global screen, volume, bass, midrange, treble, max_volume
    screen.fill(BLACK)

    # Get a balanced color based on the frequency bands
    color = get_smooth_color(bass, midrange, treble, max_volume)

    # Center of the screen
    center_x, center_y = screen.get_width() // 2, screen.get_height() // 2

    # PARTICLES #
     # Spawn new particles based on bass
    for _ in range(int(bass * 1)):
        size = random.randint(2, 5)
        #speed_x = random.uniform(-2, 2)
        #speed_y = random.uniform(-2, 2)
        #particles.append(Particle(center_x, center_y, color, size, speed_x, speed_y))
        particles.append(Particle(center_x, center_y, color, size, midrange, treble))

    # Update and draw particles
    for particle in particles[:]:
        particle.move()
        particle.draw(screen)
        if not particle.is_alive():
            particles.remove(particle)

    draw_palette_name()

    pygame.display.update()


def get_smooth_color(bass, midrange, treble, max_volume=1):
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
            draw_radial_patterns()
            switch_palette()
            pygame.time.wait(10)

    except KeyboardInterrupt:
        pygame.quit()
        sys.exit()
