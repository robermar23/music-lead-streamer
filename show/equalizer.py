import pygame
import sounddevice as sd
import numpy as np
import math
import os
import sys
import random
import time

# Configuration
DEVICE_INDEX = 1
SAMPLE_RATE = 44100
CHANNELS = 2
BLOCKSIZE = 1024
LATENCY = "high"
NUM_BANDS = 25  # Number of frequency bands
BAR_WIDTH = 25  # Width of each bar
BAR_SPACING = 5  # Space between bars
BAR_COLOR_TOP = (0, 255, 0)  # Green color for bars
BAR_COLOR_BOTTOM = (0, 100, 0)
BAR_PEAK_COLOR = (0, 255, 0)
TEXT_COLOR = (255, 255, 255)  # White for text
BLACK = (0, 0, 0)
volume = 0
bass, midrange, treble = 0, 0, 0
max_volume = 1


# Switch palette every 10 seconds
last_palette_switch = time.time()

stars = []

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

# Audio Callback
frequency_amplitudes = np.zeros(NUM_BANDS)
peak_positions = np.zeros(NUM_BANDS)
#band_frequencies = np.logspace(np.log10(20), np.log10(SAMPLE_RATE / 2), NUM_BANDS + 1)
band_frequencies = np.geomspace(20, SAMPLE_RATE / 2, NUM_BANDS + 1)
def audio_callback(indata, frames, time, status):
    global frequency_amplitudes
    if status:
        print(f"Status: {status}")

    if status != "input overflow":
      
        # Perform FFT
        fft_data = np.abs(np.fft.rfft(indata[:, 0]))  # Use one channel
        freqs = np.fft.rfftfreq(len(indata[:, 0]), 1 / SAMPLE_RATE)

        # Calculate frequency band amplitudes
        band_amplitudes = np.zeros(NUM_BANDS)
        band_edges = np.logspace(np.log10(20), np.log10(SAMPLE_RATE / 2), NUM_BANDS + 1)

        for i in range(NUM_BANDS):
            #band_amplitudes[i] = np.mean(fft_data[(freqs >= band_edges[i]) & (freqs < band_edges[i + 1])])
            # Extract the frequencies for the current band
            band_data = fft_data[(freqs >= band_frequencies[i]) & (freqs < band_frequencies[i + 1])]
            #print(f"Band {i}: Size = {band_data.size}, Frequency Range = {band_frequencies[i]}-{band_frequencies[i + 1]}")
            
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
        frequency_amplitudes = 0.8 * frequency_amplitudes + 0.2 * band_amplitudes

        # for i, amplitude in enumerate(frequency_amplitudes):
        #     print(f"Band {i}: Amplitude = {amplitude}, Frequency = {band_frequencies[i]:.2f} Hz")


def switch_palette():
    global selected_palette, last_palette_switch, BAR_COLOR_TOP, BAR_COLOR_BOTTOM, BAR_PEAK_COLOR
    if time.time() - last_palette_switch > 30:
        selected_palette = random.choice(list(PALETTES.values()))
        last_palette_switch = time.time()
        BAR_COLOR_TOP = selected_palette[0]
        BAR_COLOR_BOTTOM = selected_palette[1]
        BAR_PEAK_COLOR = selected_palette[2]

def draw_palette_name():
    font = pygame.font.SysFont(None, 36)
    text = font.render(f"Palette: {list(PALETTES.keys())[list(PALETTES.values()).index(selected_palette)]}", True, (255, 255, 255))
    screen.blit(text, (10, 10))

def draw_gradient_bar(screen, x, y, width, height, color_top, color_bottom):
    """Draws a bar with a gradient effect."""
    for i in range(height):
        blend = i / height
        r = int(color_top[0] * (1 - blend) + color_bottom[0] * blend)
        g = int(color_top[1] * (1 - blend) + color_bottom[1] * blend)
        b = int(color_top[2] * (1 - blend) + color_bottom[2] * blend)
        pygame.draw.line(screen, (r, g, b), (x, y + i), (x + width, y + i))

# Function to draw frequency labels
def draw_frequency_labels():
    """Draws frequency labels below each bar."""
    font = pygame.font.SysFont(None, 10)
    for i in range(NUM_BANDS):
        center_frequency = int((band_frequencies[i] + band_frequencies[i + 1]) / 2)  # Calculate center frequency
        label = font.render(f"{center_frequency} Hz", True, (255, 255, 255))  # White text
        x = i * (BAR_WIDTH + BAR_SPACING)
        y = screen.get_height() - 20  # Position below the bars
        screen.blit(label, (x, y))

def draw_db_scale():
    """Draws a decibel (dB) scale on the left side of the screen."""
    max_height = screen.get_height() - 40  # Leave space for labels and bars
    font = pygame.font.SysFont(None, 20)
    interval = 50  # Distance between dB markers
    for i in range(0, max_height, interval):
        dB = -i // interval * 10  # Calculate dB value
        label = font.render(f"{dB} dB", True, (255, 255, 255))  # White text
        screen.blit(label, (10, max_height - i - 20))  # Position labels on the left

def draw_frequency_amplitudes():

    global BAR_COLOR_TOP, BAR_COLOR_BOTTOM, BAR_PEAK_COLOR

    # Draw frequency bars
    for i, amplitude in enumerate(frequency_amplitudes):
      # Ensure amplitude is a valid number
      if not np.isfinite(amplitude):
          amplitude = 0  # Replace invalid values with 0

      bar_height = int(amplitude * 5)  # Scale amplitude to screen height
      # Update peak position
      if bar_height > peak_positions[i]:
          peak_positions[i] = bar_height  # Move peak up
      else:
          peak_positions[i] -= 2  # Gradually fall down

      x = i * (BAR_WIDTH + BAR_SPACING)
      y = screen.get_height() - bar_height

      # Draw peak marker
      peak_y = screen.get_height() - 40 - peak_positions[i]
      pygame.draw.rect(screen, BAR_PEAK_COLOR, (x, peak_y, BAR_WIDTH, 5))  # White peak marker

      draw_gradient_bar(screen, x, y, BAR_WIDTH, bar_height, BAR_COLOR_TOP, BAR_COLOR_BOTTOM)

def determine_background_color():
    # Determine dominant frequency range
    dominant_frequency = np.argmax(frequency_amplitudes)
    color_factor = dominant_frequency / NUM_BANDS

    # Map the dominant frequency to a gradient color
    background_color = (
        int(255 * color_factor),  # Red
        int(255 * (1 - color_factor)),  # Green
        int(255 * (1 - color_factor)),  # Blue
    )

    # Clear the screen
    #screen.fill(BLACK)
    screen.fill(background_color)

# def draw_wave_background():
#     for x in range(0, screen.get_width(), 10):
#         y = int((math.sin(x / 50 + pygame.time.get_ticks() / 500) + 1) * screen.get_height() / 4)
#         pygame.draw.line(screen, (50, 50, 50), (x, y), (x, y + 5))
def draw_wave_background():
    """Draws a sine wave background that reacts smoothly to the music."""
    # Calculate music-based properties
    bass_intensity = np.clip(np.mean(frequency_amplitudes[:NUM_BANDS // 3]), 0, 1)  # Bass range
    midrange_intensity = np.clip(np.mean(frequency_amplitudes[NUM_BANDS // 3:NUM_BANDS * 2 // 3]), 0, 1)  # Midrange
    treble_intensity = np.clip(np.mean(frequency_amplitudes[NUM_BANDS * 2 // 3:]), 0, 1)  # Treble range

    # Adjust wave properties
    wave_amplitude = int(bass_intensity * 100)  # Height of the wave
    wave_frequency = 50 + int(midrange_intensity * 100)  # Wavelength
    wave_speed = max(0.1, treble_intensity * 0.3)

    # Draw the sine wave
    for x in range(0, screen.get_width(), 10):  # Step size of 10 for better performance
        y = int(
            screen.get_height() / 2
            + wave_amplitude * math.sin((x / wave_frequency) + pygame.time.get_ticks() / 1000 * wave_speed)
        )
        pygame.draw.line(screen, (50, 50, 255), (x, y), (x, y + 5))  # Draw a segment of the wave

def create_starfield(num_stars=100):
    """Initialize the starfield with random positions, base sizes, and brightness."""
    for _ in range(num_stars):
        x = random.randint(0, screen.get_width())
        y = random.randint(0, screen.get_height())
        base_size = random.uniform(1, 7)  # Base size of the star
        base_brightness = random.randint(50, 150)  # Base brightness
        stars.append({
            "x": x,
            "y": y,
            "base_size": base_size,
            "current_size": base_size,
            "base_brightness": base_brightness,
            "current_brightness": base_brightness,
            "speed": random.uniform(0.5, 2),  # Base horizontal speed
        })

def draw_starfield():
    """Draw the starfield, reacting to bass for brightness/size and treble for speed."""
    if frequency_amplitudes.size == 0:
        bass_intensity = 0
        treble_intensity = 0
    else:
        # Calculate bass intensity
        max_bass_intensity = max(np.max(frequency_amplitudes[:NUM_BANDS // 3]), 0.01)
        bass_intensity = np.clip(np.mean(frequency_amplitudes[:NUM_BANDS // 3]) / max_bass_intensity, 0, 1)

        # Calculate treble intensity
        max_treble_intensity = max(np.max(frequency_amplitudes[NUM_BANDS * 2 // 3:]), 0.01)
        treble_intensity = np.clip(np.mean(frequency_amplitudes[NUM_BANDS * 2 // 3:]) / max_treble_intensity, 0, 1)

    for star in stars:
        # Scale brightness and size with bass intensity
        brightness_boost = int(bass_intensity * 155)
        star["current_brightness"] = min(255, star["base_brightness"] + brightness_boost)

        size_boost = bass_intensity * 8
        star["current_size"] = star["base_size"] + size_boost

        # Scale horizontal movement with treble intensity
        star["x"] += star["speed"] * (1 + treble_intensity * 5)

        # Wrap stars that move off-screen
        if star["x"] > screen.get_width():
            star["x"] = 0
            star["y"] = random.randint(0, screen.get_height())

        # Draw the star
        star_color = (star["current_brightness"], star["current_brightness"], star["current_brightness"])
        pygame.draw.circle(screen, star_color, (int(star["x"]), int(star["y"])), int(star["current_size"]))

        # Gradual decay for brightness and size
        star["current_brightness"] = max(star["base_brightness"], star["current_brightness"] - 5)
        star["current_size"] = max(star["base_size"], star["current_size"] - 0.2)



# Main
setup_display()

create_starfield()

# Randomly select a palette at the start
selected_palette = random.choice(list(PALETTES.values()))
#print (f"Selected Color Palette: {selected_palette}")

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
          
          screen.fill(BLACK)
          #determine_background_color()

          #draw_wave_background()

          # Draw starfield
          draw_starfield()

          draw_db_scale()
          
          draw_frequency_amplitudes()  

          #draw_frequency_labels()

          switch_palette()

          #draw_palette_name()
          
          pygame.display.update()

          pygame.time.wait(10)

    except KeyboardInterrupt:
        pygame.quit()
        sys.exit()
