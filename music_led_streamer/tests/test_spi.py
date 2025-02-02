import spidev
import time

NUM_PIXELS = 25
spi = spidev.SpiDev()
spi.open(0, 0)  # Open SPI bus 0, device 0
#spi.max_speed_hz = 1000000  # Set SPI speed to 1 MHz

# Function to send color data to the LED strip
def set_color(r, g, b):
    data = []
    for _ in range(NUM_PIXELS):
        data.extend([r, g, b])
    spi.xfer2(data)

# Set all LEDs to red
set_color(255, 0, 0)
time.sleep(1)

# Set all LEDs to green
set_color(0, 255, 0)
time.sleep(1)

# Set all LEDs to blue
set_color(0, 0, 255)
time.sleep(1)