import os
import pygame

pygame.init()

# List available displays
num_displays = pygame.display.get_num_displays()
print(f"Available displays: {num_displays}")

# Choose a display to render on
display_index = int(input(f"Enter display index (0 to {num_displays - 1}): "))
os.environ["SDL_VIDEO_FULLSCREEN_HEAD"] = str(display_index)

# Set up the display
#screen = pygame.display.set_mode((800, 600), pygame.FULLSCREEN)
screen = pygame.display.set_mode((1080, 1920))

pygame.display.set_caption(f"Rendering on Display {display_index}")

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 0, 0))  # Red background
    pygame.display.flip()

pygame.quit()
