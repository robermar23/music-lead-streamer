import pygame
import sounddevice as sd
import numpy as np
from collections import Counter
from music_led_streamer.object.image_fragment import ImageFragment

sample_Rate = 44100
bass, midrange, treble = 0, 0, 0
smoothed_bass, smoothed_midrange, smoothed_treble = 0, 0, 0  # Smoothed values
gradient_colors = [(0, 0, 0), (0, 0, 0), (0, 0, 0)]  # Default black

# Global state for the show
fragments = []

# Smoothing factor (closer to 1 = more smoothing)
SMOOTHING_FACTOR = 0.2
EXPANSION_FACTOR = 10  # Controls how much fragments separate

# Image settings
IMAGE_PATH = "images/image7.png"  # image to load (must be in the same directory)
NUM_ROWS = 50  # max Number of rows to split the image, if screen is too small, it will be less
NUM_COLS = 50 # max Number of columns to split the image, if screen is too small, it will be less
FRAGMENT_SPEED = 15  # Base movement speed
BUFFER_PERCENTAGE = 0.10  # buffer zone around image to prevent image disspearing from screen with large bass

# Audio callback
def audio_callback(indata, frames, time, status):
    """Calculates and updates the volume, bass, midrange, and treble levels from audio input.

    This callback function processes audio data, performs FFT to extract frequency components,
    and applies smoothing to the calculated values.
    """
    
    global bass, midrange, treble, smoothed_bass, smoothed_treble, smoothed_midrange
    if status:
        print(f"Status: {status}")

    if status != "input overflow":
      
      # Perform FFT on the audio data
      fft_data = np.abs(np.fft.rfft(indata[:, 0]))  # Use one channel
      freqs = np.fft.rfftfreq(len(indata[:, 0]), 1 / sample_Rate)

      # Bass (20-250 Hz), Midrange (250-4000 Hz), Treble (4000-20000 Hz)
      bass = np.mean(fft_data[(freqs >= 20) & (freqs < 250)])
      midrange = np.mean(fft_data[(freqs >= 250) & (freqs < 4000)])
      treble = np.mean(fft_data[(freqs >= 4000)])
      
      # Apply exponential moving average for smooth transitions to prevent "jitter" of fragements
      smoothed_bass = (SMOOTHING_FACTOR * bass) + ((1 - SMOOTHING_FACTOR) * smoothed_bass)
      smoothed_midrange = (SMOOTHING_FACTOR * midrange) + ((1 - SMOOTHING_FACTOR) * smoothed_midrange)
      smoothed_treble = (SMOOTHING_FACTOR * treble) + ((1 - SMOOTHING_FACTOR) * smoothed_treble)
      
      #print (f"bass: {bass}, midrange: {midrange}, treble: {treble}")

def extract_top_colors(image, num_colors=3):
    """Extracts the most common colors from an image."""
    image_data = pygame.surfarray.array3d(image)
    pixels = image_data.reshape(-1, 3)  # Flatten pixels into RGB values
    counter = Counter(map(tuple, pixels))  # Count occurrences of each color
    return [color for color, _ in counter.most_common(num_colors)]

def draw_gradient(screen, colors):
    """Draws a vertical gradient background using the top 3 colors."""
    width, height = screen.get_size()
    for y in range(height):
        ratio = y / height
        r = int((1 - ratio) * colors[0][0] + ratio * colors[1][0])
        g = int((1 - ratio) * colors[0][1] + ratio * colors[1][1])
        b = int((1 - ratio) * colors[0][2] + ratio * colors[1][2])
        pygame.draw.line(screen, (r, g, b), (0, y), (width, y))

def handle_image_paint(screen, bass, midrange, treble):
    """Manipulate and draw image fragments dynamically."""
    for fragment in fragments:
        fragment.update(smoothed_bass, smoothed_midrange, smoothed_treble, FRAGMENT_SPEED, EXPANSION_FACTOR)
        fragment.draw(screen)

# Global state for the show
def initialize(audio_settings, screen):
    """Initialize the show."""
    global audio_stream, selected_palette, sample_rate, fragments, gradient_colors
    
    # Extract audio settings
    samplerate, channels, device_index, blocksize, latency = audio_settings

    sample_Rate = samplerate

   # Load image and scale it to fit within the screen with a buffer
    screen_width, screen_height = screen.get_size()
    image = pygame.image.load(IMAGE_PATH)

    

    # Calculate buffer space
    buffer_x = int(screen_width * BUFFER_PERCENTAGE)
    buffer_y = int(screen_height * BUFFER_PERCENTAGE)

    max_width = screen_width - 2 * buffer_x
    max_height = screen_height - 2 * buffer_y

    # Maintain aspect ratio while scaling
    image_ratio = image.get_width() / image.get_height()
    screen_ratio = max_width / max_height

    if image_ratio > screen_ratio:
        # Image is wider, scale based on width
        new_width = max_width
        new_height = int(max_width / image_ratio)
    else:
        # Image is taller, scale based on height
        new_height = max_height
        new_width = int(max_height * image_ratio)

    image = pygame.transform.smoothscale(image, (new_width, new_height))

    # Calculate top-left position with buffer
    image_x = (screen_width - new_width) // 2
    image_y = (screen_height - new_height) // 2

    # Center of the image (for radial expansion effect)
    center_x = image_x + new_width // 2
    center_y = image_y + new_height // 2

    # **Fix subsurface issue**: Use `min()` to ensure fragments fit within image bounds
    fragment_width = max(1, new_width // NUM_COLS)  # Prevent zero division
    fragment_height = max(1, new_height // NUM_ROWS)

    # Split image and store each fragment
    fragments = []
    for y in range(NUM_ROWS):
        for x in range(NUM_COLS):
            frag_x = x * fragment_width
            frag_y = y * fragment_height

            # Ensure the fragment stays within the image bounds
            if frag_x + fragment_width > new_width or frag_y + fragment_height > new_height:
                continue

            start_x = image_x + frag_x
            start_y = image_y + frag_y

            fragment = ImageFragment(image, frag_x, frag_y, fragment_width, fragment_height, start_x, start_y, center_x, center_y)
            fragments.append(fragment)

    # Extract top colors for gradient background
    gradient_colors = extract_top_colors(image, num_colors=3)

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
    global selected_palette, bass, midrange, treble
    """Render a single frame of the visualization."""
    dt = pygame.time.Clock().tick(60) / 1000  # Delta time in seconds

    draw_gradient(screen, gradient_colors)  # Draw gradient instead of black background

    # Draw the image fragments with motion effect
    handle_image_paint(screen, bass, midrange, treble)
    pygame.display.update()

def cleanup():
    """Clean up resources for the show."""
    global audio_stream
    if audio_stream:
        audio_stream.stop()
        audio_stream.close()