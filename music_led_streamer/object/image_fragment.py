import random
import pygame
import numpy as np

class ImageFragment:
    """Represents a fragment of the image that moves dynamically based on audio."""
    
    def __init__(self, image, x, y, width, height, start_x, start_y, center_x, center_y):
        """Initialize the fragment with its position and size."""
        width = min(width, image.get_width() - x)
        height = min(height, image.get_height() - y)

        self.image = image.subsurface(pygame.Rect(x, y, width, height))  
        self.original_image = self.image.copy()  # Keep original for rotation
        self.start_x = start_x  
        self.start_y = start_y
        self.x = start_x
        self.y = start_y
        self.width = width
        self.height = height
        self.center_x = center_x  
        self.center_y = center_y
        self.speed = random.uniform(1, 5)  

        self.target_x = start_x
        self.target_y = start_y
        self.angle = 0  # Initial rotation angle

    def update(self, bass, midrange, treble, base_fragment_speed, space_expansion_factor, rotate_expansion_factor = 25):
        """Smoothly update position and rotation based on bass, midrange, and treble."""
        spacing = int(bass * space_expansion_factor)  
        speed_boost = int(treble * base_fragment_speed)  

        # Ensure uniform outward movement from the center
        dir_x = self.start_x - self.center_x
        dir_y = self.start_y - self.center_y
        magnitude = max(np.sqrt(dir_x**2 + dir_y**2), 1)  # Normalize direction

        # Move outward in both X and Y proportionally
        self.target_x = self.start_x + (spacing * dir_x / magnitude)
        self.target_y = self.start_y + (spacing * dir_y / magnitude) + speed_boost

        # Apply easing effect (gradual movement)
        self.x += (self.target_x - self.x) * 0.2  
        self.y += (self.target_y - self.y) * 0.2  

        # Rotate fragment based on midrange levels
        self.angle = midrange * rotate_expansion_factor

    def draw(self, screen):
        """Draw the fragment on the screen."""
        rotated_image = pygame.transform.rotate(self.original_image, self.angle)
        rect = rotated_image.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(rotated_image, rect.topleft)