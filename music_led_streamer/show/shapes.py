import pygame
import sounddevice as sd
import numpy as np
import random
import os
import sys
import math
from music_led_streamer.util import BLACK, frequency_to_rgb
from music_led_streamer.object.shape import Shape
from music_led_streamer.color_music_mapper import ColorSoundMapper


sample_Rate = 44100

# Audio callback
volume = 0
bass, midrange, treble = 0, 0, 0
dominant_frequency = 0
shapes = []  # List to store active shapes
mapped_colors = ColorSoundMapper.create_instances()

def audio_callback(indata, frames, time, status):
    global volume, bass, midrange, treble, dominant_frequency
    if status:
        print(f"Status: {status}")

    # Calculate the volume
    volume = np.linalg.norm(indata) / np.sqrt(indata.size)

    # Perform FFT on the audio data
    fft_data = np.abs(np.fft.rfft(indata[:, 0]))  # Use one channel
    freqs = np.fft.rfftfreq(len(indata[:, 0]), 1 / sample_Rate)

    # Bass (20-250 Hz), Midrange (250-4000 Hz), Treble (4000-20000 Hz)
    bass = np.mean(fft_data[(freqs >= 20) & (freqs < 250)])
    midrange = np.mean(fft_data[(freqs >= 250) & (freqs < 4000)])
    treble = np.mean(fft_data[(freqs >= 4000)])
    # Find the dominant frequency
    dominant_idx = np.argmax(fft_data)
    dominant_frequency = freqs[dominant_idx]# * 2  # Adjust for doubling frequency
     # Ensure the dominant frequency is above a safe threshold
    if dominant_frequency < 20:
        dominant_frequency = 20  # Set a minimum frequency

# Draw shapes
def draw_shapes(screen, dt):
    global shapes, bass, midrange, treble, volume, dominant_frequency, mapped_colors
    #total_shapes = int((bass + midrange + treble)/2)  # Total number of shapes to create

    # Screen dimensions
    #screen_width, screen_height = screen.get_width(), screen.get_height()

    # Create new shapes
    #total_shapes = int((bass * 0.1))  # Total number of new shapes to create
    #print (f"bass: {bass}, midrange: {midrange}, treble: {treble}")
    total_shapes = int(((bass + midrange + treble) * 0.1))  # Total number of new shapes to create
    if int(total_shapes) == 0:
        total_shapes = int((bass * 100) + (midrange * 100) + (treble * 100)  * 0.1)
    if len(shapes) + total_shapes <= 900:
        print (f"New shapes: {total_shapes}")
        for _ in range(total_shapes):
            x = random.randint(0, screen.get_width())
            y = random.randint(0, screen.get_height())
            size = int(volume * 100)  # Scale size with volume
            # Use dominant frequency to determine the color
            #color = frequency_to_rgb(dominant_frequency)
            #print(f"dominant_frequency: {dominant_frequency}")
            mapped_color = ColorSoundMapper.find_by_frequency(mapped_colors, dominant_frequency)
            if mapped_color != None:
                color = mapped_color.get_rgb()
            else:
                color = (255, 255, 255)
            lifetime = random.uniform(1, 3)  # Randomize lifetime
            shapes.append(Shape(x, y, size, color, lifetime, treble, midrange, bass))

    # Update and draw existing shapes.  update returns False if the shape is expired
    shapes = [shape for shape in shapes if shape.update(dt)]
    for shape in shapes:
        shape.draw(screen)

    #print (f"Alive Shapes: {len(shapes)}")

# def add_shape(x, y, size, frequency):
#     """Add a new shape to the shapes list."""
#     # Size based on volume
#     #size = int(volume * 100)

#     # Expanded color logic
#     # color = (
#     #     min(255, int(255 * abs(math.sin(treble * 0.1 + 4)))),
#     #     min(255, int(255 * abs(math.sin(midrange * 0.1 + 2)))),
#     #     min(255, int(255 * abs(math.sin(bass * 0.1 + 1)))),
#     # )
#     color = frequency_to_rgb(frequency)

#     # Lifetime influenced by treble
#     lifetime = max(1, int(treble * 2))

#     # Add the new shape
#     shapes.append(Shape(x, y, size, color, lifetime, treble, midrange, bass))

    #print (f"Added volume {volume} with size {size} and lifetime {lifetime}")

# Global state for the show
def initialize(audio_settings, screen):
    """Initialize the show."""
    global audio_stream
    
    # Extract audio settings
    samplerate, channels, device_index, blocksize, latency = audio_settings

    sample_Rate = samplerate

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
    dt = pygame.time.Clock().tick(60) / 1000  # Delta time in seconds
    screen.fill(BLACK)
    draw_shapes(screen, dt)
    pygame.display.update()

def cleanup():
    """Clean up resources for the show."""
    global audio_stream
    if audio_stream:
        audio_stream.stop()
        audio_stream.close()