import pygame
import sounddevice as sd
import numpy as np
import random
import time
from music_led_streamer.util import BLACK, PALETTES

# Constants
sample_rate = 44100
volume = 0
max_volume = 0
bass, midrange, treble = 0, 0, 0

# Switch palette every 10 seconds
last_palette_switch = time.time()

# Global rotation factor to keep rotation smooth over time
global_rotation = 0
max_radius = 0
previous_sub_segments = 5  # Keep track of previous segments to smooth changes
previous_scale = 1

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

def lerp_color(color1, color2, t):
    """Linear interpolate between two colors."""
    return (
        int(color1[0] + (color2[0] - color1[0]) * t),
        int(color1[1] + (color2[1] - color1[1]) * t),
        int(color1[2] + (color2[2] - color1[2]) * t),
    )

def draw_gradient_triangle(surface, points, color1, color2):
    temp_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    points = sorted(points, key=lambda p: p[1])
    top, mid, bot = points

    for y in range(top[1], bot[1] + 1):
        if y < mid[1]:
            t = (y - top[1]) / max(1, mid[1] - top[1])
            x1 = int(top[0] + (mid[0] - top[0]) * t)
            x2 = int(top[0] + (bot[0] - top[0]) * ((y - top[1]) / max(1, bot[1] - top[1])))
        else:
            t = (y - mid[1]) / max(1, bot[1] - mid[1])
            x1 = int(mid[0] + (bot[0] - mid[0]) * t)
            x2 = int(top[0] + (bot[0] - top[0]) * ((y - top[1]) / max(1, bot[1] - top[1])))

        if x1 > x2:
            x1, x2 = x2, x1

        blended_color = lerp_color(color1, color2, (y - top[1]) / max(1, bot[1] - top[1])) + (200,)
        pygame.draw.line(temp_surface, blended_color, (x1, y), (x2, y))

    pygame.draw.polygon(temp_surface, color2, points, 1)
    surface.blit(temp_surface, (0, 0))

def draw_kaleidoscope(screen, bass, midrange, treble, selected_palette):
    global global_rotation, max_radius, previous_sub_segments, previous_scale

    width, height = screen.get_size()
    center = (width // 2, height // 2)
    max_radius = min(width, height) // 2

    # Rotation reacts to treble
    treble_effect = max(0.1, treble)  # Prevents excessive speed
    global_rotation += (np.pi / 240) + (treble_effect * np.pi / 120)

    # Number of segments depends on midrange
    num_segments = max(1, int(midrange))  # Ensures at least 5
    if num_segments <= 0:
        num_segments = 2

    # *Bass controls pulsing scale
    new_scale_factor = bass * 0.015
    scale_factor = 0.8 * previous_scale + 0.2 * new_scale_factor
    if scale_factor <= 0:
        scale_factor = 1
    previous_scale = scale_factor

    #print (f"num_segments: {num_segments}")
    print (f"global_rotation: {global_rotation}, scale_factor: {scale_factor}")
    #print (f"bass: {bass}, midrange: {midrange}, treble: {treble}")

    base_points = [
        (0, -max_radius),
        (max_radius * np.sin(np.pi / num_segments), max_radius * np.cos(np.pi / num_segments)),
        (-max_radius * np.sin(np.pi / num_segments), max_radius * np.cos(np.pi / num_segments)),
    ]
    
    for i in range(num_segments):
        angle = i * (2 * np.pi / num_segments) + global_rotation

        rotated_points = [
            (
                int(center[0] + (x * np.cos(angle) - y * np.sin(angle)) * scale_factor),
                int(center[1] + (x * np.sin(angle) + y * np.cos(angle)) * scale_factor),
            )
            for x, y in base_points
        ]

        color_index = i % len(selected_palette)
        base_color = selected_palette[color_index]
        highlight_color = lerp_color(base_color, (255, 255, 255), 0.5)

        draw_gradient_triangle(screen, rotated_points, base_color, highlight_color)

    flipped_surface = pygame.transform.flip(screen, True, False)
    screen.blit(flipped_surface, (0, 0))

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
    draw_kaleidoscope(screen, bass, midrange, treble, selected_palette)

    selected_palette = switch_palette(selected_palette)

    draw_palette_name(screen, selected_palette)

    # Update the display
    pygame.display.update()

def cleanup():
    """Clean up resources for the show."""
    global audio_stream
    if audio_stream:
        audio_stream.stop()
        audio_stream.close()