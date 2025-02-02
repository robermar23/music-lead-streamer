import os
import pygame

pygame.init()

# Get display information
num_displays = pygame.display.get_num_displays()
print(f"Number of displays: {num_displays}")

# Choose display index
display_index = int(input(f"Select display index (0 to {num_displays - 1}): "))

# Get screen resolution of the selected display
display_info = pygame.display.Info()
width, height = display_info.current_w, display_info.current_h

# Position the window manually
if display_index == 1:  # Second monitor
    os.environ['SDL_VIDEO_WINDOW_POS'] = f"{width},0"  # Place at the start of the second screen
else:  # Primary monitor
    os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"

# Create a borderless window
screen = pygame.display.set_mode((1080, 1920), pygame.NOFRAME)
pygame.display.set_caption(f"Rendering on Display {display_index}")

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 255, 0))  # Green background
    pygame.display.flip()

pygame.quit()
