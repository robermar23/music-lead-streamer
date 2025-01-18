import pygame
import sounddevice as sd
import numpy as np
import wave
import os
import random
import sys


NUM_BANDS=5
SAMPLE_RATE = 44100
CHANNELS = 2
DEVICE = "Loopback"
DEVICE_INDEX = 1
BLOCKSIZE=16184
LATENCY="high"
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
# Colors to cycle through
COLORS = [
    (255, 0, 0),   # Red
    (0, 255, 0),   # Green
    (0, 0, 255),   # Blue
    (255, 255, 0), # Yellow
    (0, 255, 255), # Cyan
    (255, 0, 255)  # Magenta
]

def setup_display():
    # Allow running from ssh
    os.putenv("DISPLAY", ":0")
    os.putenv('SDL_VIDEODRIVER', "x11")
    
    disp_no = os.getenv("DISPLAY")
    
    if disp_no:
        print("I'm running under X display = {0}".format(disp_no))

    pygame.display.init()

    global screen
    size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
    print("Framebuffer size: %d x %d" % (size[0], size[1]))
    screen = pygame.display.set_mode(size, pygame.FULLSCREEN)

    # Clear the screen to start
    screen.fill((0, 0, 0))
    # Initialise font support
    pygame.font.init()
    # Render the screen
    pygame.display.update()
    

def audio_callback(indata, frames, time, status):

    global volume

    #if status:
        #print(f"Status: {status}")

    # Process audio and update LEDs
    if status != "input overflow":
        #volume = np.linalg.norm(indata)  # Calculate volume
        volume = np.linalg.norm(indata) / np.sqrt(indata.size)
        print (f"Volume: {volume}")
 
# Draw random shapes based on volume
def draw_shapes():
    global screen, volume
    screen.fill(BLACK)

    # Determine number of shapes to draw based on volume
    num_shapes = int(volume * 50)
    color = random.choice(COLORS)

    for _ in range(num_shapes):
        shape_type = random.choice(['circle', 'rect', 'line', 'triangle'])
        x, y = random.randint(0, 800), random.randint(0, 480)
        size = random.randint(10, 100)

        if shape_type == 'circle':
            pygame.draw.circle(screen, color, (x, y), size)
        elif shape_type == 'rect':
            pygame.draw.rect(screen, color, (x, y, size, size))
        elif shape_type == 'line':
            end_x, end_y = x + random.randint(-100, 100), y + random.randint(-100, 100)
            pygame.draw.line(screen, color, (x, y), (end_x, end_y), 2)
        elif shape_type == 'triangle':
            points = [(x, y), (x + size, y), (x + size // 2, y - size)]
            pygame.draw.polygon(screen, color, points)

    pygame.display.update()


setup_display()

device_info = sd.query_devices(DEVICE_INDEX, 'input')
SAMPLE_RATE = int(device_info['default_samplerate'])

print (device_info)
print (f"Default Sample Rate: {SAMPLE_RATE}")

# Start the audio stream
volume = 0
# Open the input stream
with sd.InputStream(
    samplerate=SAMPLE_RATE,
    channels=CHANNELS,
    device=DEVICE_INDEX,  # Replace with your loopback device index or name
    callback=audio_callback,
    blocksize=BLOCKSIZE,
    latency=LATENCY
):
    # Main loop
    try:
        while True:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    stream.stop()
                    pygame.quit()
                    sys.exit()

            # # Clear the screen
            # screen.fill(BLACK)

            # # Draw a volume bar
            # bar_height = int(volume * 500)  # Scale the volume
            # #print(bar_height)
            # pygame.draw.rect(screen, GREEN, (350, 480 - bar_height, 100, bar_height))

            # # Update the display
            # #pygame.display.flip()
            # pygame.display.update()

            # print (bar_height)
            draw_shapes()
            pygame.time.wait(int(200 - volume * 100))

    except KeyboardInterrupt:
        if stream:
            stream.stop()
        if pygame:
            pygame.quit()
