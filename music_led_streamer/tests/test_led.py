import board
import busio
import digitalio
import adafruit_ws2801

# Initialize SPI
#spi = busio.SPI(board.SCK, MOSI=board.MOSI)

# Check if SPI is locked
# if not spi.try_lock():
#     print("SPI is busy")
# else:
#     print("SPI is available")
#     spi.unlock()

NUM_PIXELS = 25  # Number of LEDs
odata = board.D5
oclock = board.D6
bright = 1.0
led_strip = adafruit_ws2801.WS2801(oclock, odata, NUM_PIXELS, brightness=bright, auto_write=False)

# Set all LEDs to red
for i in range(NUM_PIXELS):
    led_strip[i] = (255, 0, 0)

led_strip.show()

#leds.fill((0x80, 0, 0))