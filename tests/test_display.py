import pygame
import sys
import os

#print(pygame.display.get_driver())

os.putenv('SDL_FBDEV', '/dev/fb0')
os.putenv('SDL_VIDEODRIVER', 'x11')
os.putenv('SDL_AUDIODRIVER', 'dsp')


# Initialize Pygame
pygame.init()

# Set up the display (adjust resolution to your screen)
screen = pygame.display.set_mode((800, 480))

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Fill the screen with a color
    screen.fill((0, 0, 255))  # Blue background

    # Draw a circle
    pygame.draw.circle(screen, (255, 0, 0), (400, 240), 100)  # Red circle

    # Update the display
    pygame.display.flip()

