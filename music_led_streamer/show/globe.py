import pygame
import pygame.gfxdraw
import sounddevice as sd
import numpy as np
import math
import os
import sys
import random
import time
from music_led_streamer.util import BLACK

# Constants
sample_rate = 44100
bass, midrange, treble = 0, 0, 0

FLARE_COLOR = (255, 69, 0)  # Orange-red flares
BACKGROUND_COLOR = (10, 10, 30)  # Dark blue for a space-like feel
FLARE_LIFE_MAX = 20  # Maximum lifecycle of a flare (in frames)
ROTATION_SPEED_BASE = 0.02  # Base rotation speed
BASE_RADIUS = 15
RADIUS_SCALING = 1.05  # Maximum increase in radius

# Switch palette every 10 seconds
last_palette_switch = time.time()

# State variables
flares = []
rotation_angle = 0
rotation_speed = ROTATION_SPEED_BASE
volume = 0
smoothed_bass = 0  # Add this as a global variable

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

def audio_callback(indata, frames, time, status):
    global volume, bass, midrange, treble
    if status:
        print(f"Status: {status}")

    if status != "input overflow":
      # Calculate the volume
      volume = np.linalg.norm(indata) / np.sqrt(indata.size)

      # Perform FFT on the audio data
      fft_data = np.abs(np.fft.rfft(indata[:, 0]))  # Use one channel
      freqs = np.fft.rfftfreq(len(indata[:, 0]), 1 / sample_rate)

      # Bass (20-250 Hz), Midrange (250-4000 Hz), Treble (4000-20000 Hz)
      bass = np.mean(fft_data[(freqs >= 20) & (freqs < 250)])
      midrange = np.mean(fft_data[(freqs >= 250) & (freqs < 4000)])
      treble = np.mean(fft_data[(freqs >= 4000)])

# Draw a gradient background
def draw_background(screen, screen_height, screen_width):
    """Draw a gradient background."""
    for y in range(screen_height):
        color = tuple(
            int(BACKGROUND_COLOR[i] + (20 * y / screen_height)) for i in range(3)
        )
        pygame.draw.line(screen, color, (0, y), (screen_width, y))

def calculate_dynamic_radius(bass):
    """Calculate the globe radius based on bass levels."""
    global smoothed_bass

    # Smooth the bass value
    smoothing_factor = 0.2
    smoothed_bass = (smoothing_factor * bass) + ((1 - smoothing_factor) * smoothed_bass)

    # Calculate dynamic radius
    return BASE_RADIUS + int(smoothed_bass * RADIUS_SCALING)

# Draw the Globe
def draw_globe(screen, center, radius, angle, base_color):
    """Draw a rotating globe with simple shading."""
    light_direction = (
        math.cos(angle),  # Rotating light x-component
        math.sin(angle),  # Rotating light y-component
    )
    for y in range(-radius, radius):
        for x in range(-radius, radius):
            distance = math.sqrt(x**2 + y**2)
            if distance <= radius:  # Only draw within the circle
                normal_x = x / radius
                normal_y = y / radius
                dot = normal_x * light_direction[0] + normal_y * light_direction[1]
                shade = max(0, min(255, int(255 * dot)))

                # Apply the shade to the base color
                color = (
                    max(0, min(255, base_color[0] + shade)),
                    max(0, min(255, base_color[1] + shade)),
                    max(0, min(255, base_color[2] + shade)),
                )
                screen.set_at((center[0] + x, center[1] + y), color)

# Generate flares based on audio input
# Generate flares based on audio input
def generate_flares(bass, midrange, treble, color):
    """Create new solar flares dynamically."""
    global flares

    # Determine flare count based on bass intensity
    num_new_flares = int(bass / 3)

    for _ in range(num_new_flares):
        flares.append({
            "angle": random.uniform(0, 2 * math.pi),
            "life": 0,  # Start of lifecycle
            "max_length": int(50 + 100 * (midrange + treble) / 2),  # Length grows with mid/treble
            "color": color,
        })

# Render flares
def render_flares(screen, globe_center, dynamic_radius):
    """Render flares and update their lifecycle."""
    global flares
    updated_flares = []

    for flare in flares:
        # Progress lifecycle
        flare["life"] += 2
        if flare["life"] > FLARE_LIFE_MAX:
            continue  # Skip expired flares

        # Calculate flare properties
        progress = flare["life"] / FLARE_LIFE_MAX  # 0 to 1
        length = flare["max_length"] * progress  # Flare grows over time
        fade = 1 - progress  # Flare fades out over time
        angle = flare["angle"]

        # Calculate line thickness (start thick, get thinner)
        thickness = max(1, int(10 * (1 - progress)))  # Start at 10px, taper to 1px

        # Calculate start and end points
        start_x = globe_center[0] + dynamic_radius * math.cos(angle)
        start_y = globe_center[1] + dynamic_radius * math.sin(angle)
        end_x = globe_center[0] + (dynamic_radius + length) * math.cos(angle)
        end_y = globe_center[1] + (dynamic_radius + length) * math.sin(angle)

        # Calculate faded color
        color = (
            int(flare["color"][0] * fade),
            int(flare["color"][1] * fade),
            int(flare["color"][2] * fade),
        )

        # Draw the flare
        pygame.draw.line(screen, color, (start_x, start_y), (end_x, end_y), thickness)

        # Keep the flare for the next frame
        updated_flares.append(flare)

    flares = updated_flares  # Replace with updated flares

def switch_palette(selected_palette):
    global last_palette_switch
    if time.time() - last_palette_switch > 30:
        selected_palette = random.choice(list(PALETTES.values()))
        last_palette_switch = time.time()
    return selected_palette
        
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

# Render a single frame
def render_step(screen):
    """Render a single frame of the visualization."""
    global flares, bass, midrange, treble, rotation_angle, rotation_speed, volume, selected_palette

    # Clear the screen
    screen.fill(BLACK)

    screen_width = screen.get_width()
    screen_height = screen.get_height()
    globe_center = (screen_width // 2, screen_height // 2)
    
    # Draw background
    draw_background(screen, screen_height, screen_width)

    # Adjust rotation speed based on volume
    rotation_speed = ROTATION_SPEED_BASE + volume * 0.1
    rotation_angle += rotation_speed

    # Calculate dynamic globe radius
    dynamic_radius = calculate_dynamic_radius(bass)

    # Draw the rotating globe
    draw_globe(screen, globe_center, dynamic_radius, rotation_angle, selected_palette[0])

    # Generate and render flares
    generate_flares(bass, midrange, treble, selected_palette[2])
    render_flares(screen, globe_center, dynamic_radius)

    selected_palette = switch_palette(selected_palette)

    # Update the display
    pygame.display.flip()

# Cleanup resources
def cleanup():
    """Clean up resources for the show."""
    global audio_stream
    if audio_stream:
        audio_stream.stop()
        audio_stream.close()
