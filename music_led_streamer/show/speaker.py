import pygame
import sounddevice as sd
import numpy as np
import time
import random
from music_led_streamer.util import BLACK, PALETTES

# Configuration
sample_rate = 44100
volume = 0
bass, midrange, treble = 0, 0, 0

# Number of equalizer bands
NUM_BANDS = 20
TOWER_BORDER_COLOR =  (70, 70, 70)
TOWER_BACKGROUND_COLOR = (50, 50, 50)

# Switch palette every 10 seconds
last_palette_switch = time.time()

frequency_bands = np.zeros(NUM_BANDS)
band_frequencies = np.geomspace(20, sample_rate / 2, NUM_BANDS + 1)

# Palette Configuration
current_palette = [(0, 0, 0), (0, 0, 0), (0, 0, 0)]
next_palette = [(0, 0, 0), (0, 0, 0), (0, 0, 0)]
fade_start_time = time.time()
fade_duration = 3  # 3 seconds for fade effect

# Audio callback
def audio_callback(indata, frames, time, status):
    global volume, frequency_bands, bass, midrange, treble
    if status:
        print(f"Status: {status}")

    
    if status != "Input Overflow":
        # Calculate the volume
        volume = np.linalg.norm(indata) / np.sqrt(indata.size)
        
        # Perform FFT
        fft_data = np.abs(np.fft.rfft(indata[:, 0]))  # Use one channel
        freqs = np.fft.rfftfreq(len(indata[:, 0]), 1 / sample_rate)

         # Bass (20-250 Hz), Midrange (250-4000 Hz), Treble (4000-20000 Hz)
        bass = np.mean(fft_data[(freqs >= 20) & (freqs < 250)])
        midrange = np.mean(fft_data[(freqs >= 250) & (freqs < 4000)])
        treble = np.mean(fft_data[(freqs >= 4000)])
        
        # Calculate frequency band amplitudes
        band_amplitudes = np.zeros(NUM_BANDS)
        
        for i in range(NUM_BANDS):
            # Extract the frequencies for the current band
            band_data = fft_data[(freqs >= band_frequencies[i]) & (freqs < band_frequencies[i + 1])]
            
            # Check if the band_data is not empty
            if band_data.size > 0:
                band_amplitudes[i] = np.mean(band_data)
            else:
                band_amplitudes[i] = 0  # Default value for empty bands

        # Smooth neighboring bands for visualization
        for i in range(1, NUM_BANDS - 1):
            if band_amplitudes[i] == 0:
                band_amplitudes[i] = (band_amplitudes[i - 1] + band_amplitudes[i + 1]) / 2

        # Smooth out the amplitudes for a cleaner visualization
        frequency_bands = 0.8 * frequency_bands + 0.2 * band_amplitudes

# Function to draw the speaker tower
def draw_speaker_tower(screen, center_x, center_y, tower_width, tower_height):
    border_width = tower_width * 0.05  # 5% of the tower width
    pygame.draw.rect(screen, TOWER_BORDER_COLOR, (center_x - tower_width // 2, center_y - tower_height // 2, tower_width, tower_height), 0)
    pygame.draw.rect(screen, TOWER_BACKGROUND_COLOR, (center_x - tower_width // 2 + border_width, center_y - tower_height // 2 + border_width, tower_width - 2 * border_width, tower_height - 2 * border_width), 0)


# Function to draw enhanced speaker cones with dynamic ring colors
def draw_speaker_cone(screen, center_x, center_y, frequency_response, base_radius, max_displacement, base_color, num_rings=10):
    cone_displacement = min(int(np.log1p(frequency_response) * 15), max_displacement)

    for i in range(num_rings):
        ring_radius = base_radius - i * 8 + cone_displacement
        if ring_radius > 0:
            alpha = max(50, 255 - i * 25)
            color = calculate_ring_color(base_color, frequency_response)
            pygame.draw.circle(screen, color, (center_x, center_y), ring_radius, 2)

    pygame.draw.circle(screen, TOWER_BACKGROUND_COLOR, (center_x, center_y), base_radius - 40 + cone_displacement)

# Function to draw the speakers in a tower
def draw_speakers(screen, center_x, center_y, tower_height, bass, midrange, treble, palette):
    speaker_spacing = tower_height // 3
    half_spacing = speaker_spacing // 2
    base_radii = [tower_height * 0.05, tower_height * 0.08, tower_height * 0.1]  # Scale based on tower height
    max_displacements = [half_spacing - base_radii[i] for i in range(3)]

    speaker_positions = [
        center_y - tower_height // 2 + half_spacing,  # Treble
        center_y,                                     # Midrange
        center_y + tower_height // 2 - half_spacing,  # Bass
    ]

    for i, y in enumerate(speaker_positions):
        if i == 0:
            draw_speaker_cone(screen, center_x, y, treble, int(base_radii[i]), int(max_displacements[i]), palette[2], num_rings=8)
        elif i == 1:
            draw_speaker_cone(screen, center_x, y, midrange, int(base_radii[i]), int(max_displacements[i]), palette[1], num_rings=10)
        elif i == 2:
            draw_speaker_cone(screen, center_x, y, bass, int(base_radii[i]), int(max_displacements[i]), palette[0], num_rings=12)

# Function to draw the equalizer with scaling
def draw_equalizer(screen, center_x, center_y, frequency_bands, left_tower_x, right_tower_x, screen_height, gap=40):
    equalizer_height = screen_height * 0.3  # 30% of screen height

    # Housing dimensions
    housing_x = left_tower_x + gap  # Start to the right of the left tower
    housing_width = right_tower_x - housing_x - gap
    housing_height = equalizer_height + screen_height * 0.1  # Add padding
    housing_y = center_y - housing_height // 2

    # Draw the housing (outer frame)
    pygame.draw.rect(screen, TOWER_BORDER_COLOR, (housing_x, housing_y, housing_width, housing_height), 0)
    pygame.draw.rect(screen, TOWER_BACKGROUND_COLOR, (housing_x + 10, housing_y + 10, housing_width - 20, housing_height - 20), 0)

    if frequency_bands is None or len(frequency_bands) == 0:
        return

    # Draw the bars inside the housing
    bar_width = (housing_width - 75) // len(frequency_bands)  # Account for spacing
    bar_spacing = 2

    for i, energy in enumerate(frequency_bands):
        # Normalize energy to determine bar height
        bar_height = min(equalizer_height, int(np.log1p(energy) * equalizer_height * 0.1))
        bar_x = housing_x + 10 + i * (bar_width + bar_spacing)
        bar_y = center_y

        # Gradient colors for the bars
        red = 100 + i * 5
        green = 200 - i * 8
        blue = 100 + i * 10
        color = (red % 255, green % 255, blue % 255)

        pygame.draw.rect(screen, color, (bar_x, bar_y - bar_height // 2, bar_width, bar_height))


# Function to calculate the gradient color intensity
def calculate_gradient_color(colors, bass, midrange, treble):
    return [
        (
            min(255, int(colors[0][0] * (bass / 10))),
            min(255, int(colors[0][1] * (midrange / 10))),
            min(255, int(colors[0][2] * (treble / 10))),
        ),
        (
            min(255, int(colors[1][0] * (bass / 10))),
            min(255, int(colors[1][1] * (midrange / 10))),
            min(255, int(colors[1][2] * (treble / 10))),
        ),
    ]


# Function to interpolate between palettes for a fade effect
def interpolate_palettes(start_palette, end_palette, progress):
    return [
        (
            int(start_palette[i][0] * (1 - progress) + end_palette[i][0] * progress),
            int(start_palette[i][1] * (1 - progress) + end_palette[i][1] * progress),
            int(start_palette[i][2] * (1 - progress) + end_palette[i][2] * progress),
        )
        for i in range(len(start_palette))
    ]

# Function to calculate the ring color based on frequency and palette
def calculate_ring_color(base_color, frequency_level):
    return (
        min(255, int(base_color[0] * (frequency_level / 10))),
        min(255, int(base_color[1] * (frequency_level / 10))),
        min(255, int(base_color[2] * (frequency_level / 10))),
    )

# Function to draw the gradient background
def draw_gradient_background(screen, width, height, colors):
    for y in range(height):
        t = y / height
        r = int(colors[0][0] * (1 - t) + colors[1][0] * t)
        g = int(colors[0][1] * (1 - t) + colors[1][1] * t)
        b = int(colors[0][2] * (1 - t) + colors[1][2] * t)
        pygame.draw.line(screen, (r, g, b), (0, y), (width, y))

# Function to switch palettes and handle fade effect
def switch_palette():
    global current_palette, next_palette, fade_start_time

    if time.time() - fade_start_time >= 30:  # Switch palette every 30 seconds
        fade_start_time = time.time()
        current_palette = next_palette
        next_palette = random.choice(list(PALETTES.values()))

# Global state for the show
def initialize(audio_settings, screen):
    """Initialize the show."""
    global audio_stream, selected_palette, sample_rate, current_palette, next_palette
    
    # Extract audio settings
    samplerate, channels, device_index, blocksize, latency = audio_settings

    sample_rate = samplerate

    # Randomly select a palette at the start
    current_palette = random.choice(list(PALETTES.values()))
    next_palette = random.choice(list(PALETTES.values()))

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

    global frequency_bands, selected_palette, current_palette, next_palette, fade_start_time

    screen.fill(BLACK)

    screen_width, screen_height = screen.get_width(), screen.get_height()
    tower_height = int(screen_height * 0.8)  # Towers occupy 80% of the screen height
    tower_width = int(screen_width * 0.2)   # Towers occupy 10% of the screen width

    # Handle palette switching and fading
    switch_palette()
    #fade_progress = min(1, (time.time() - fade_start_time) / fade_duration)
    #interpolated_palette = interpolate_palettes(current_palette, next_palette, fade_progress)

    # Draw gradient background     
    draw_gradient_background(screen, screen_width, screen_height, current_palette)

     # Left tower
    left_tower_x = screen_width // 4
    draw_speaker_tower(screen, left_tower_x, screen_height // 2, tower_width, tower_height)
    draw_speakers(screen, left_tower_x, screen_height // 2, tower_height, bass, midrange, treble, current_palette)

    # Right tower
    right_tower_x = 3 * screen_width // 4
    draw_speaker_tower(screen, right_tower_x, screen_height // 2, tower_width, tower_height)
    draw_speakers(screen, right_tower_x, screen_height // 2, tower_height, bass, midrange, treble, current_palette)

    # Equalizer
    draw_equalizer(screen, screen_width // 2, screen_height // 2, frequency_bands, left_tower_x, right_tower_x, screen_height, gap=50)

    pygame.display.update()


def cleanup():
    global audio_stream
    if audio_stream:
        audio_stream.stop()
        audio_stream.close()
