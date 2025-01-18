import pygame
import random
import math

class Bubble:
    def __init__(self, x, y, size, speed, color):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.color = color

    def move(self, treble_intensity):
        """Move the bubble upward based on its speed and treble intensity."""
        self.y -= self.speed * (1 + treble_intensity * 10)

    def draw(self, screen):
        """Draw the bubble with a radial gradient, highlight, and glow."""
        bubble_surface = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        center = (int(self.size), int(self.size))

        # Radial gradient for the bubble
        for i in range(int(self.size), 0, -1):
            alpha = int(255 * (i / self.size))  # Fades out toward the edge
            color_with_alpha = (*self.color, alpha)
            pygame.draw.circle(bubble_surface, color_with_alpha, center, i)

        # Draw highlight (light reflection)
        highlight_x = int(self.size * 0.35)  # Top-left position
        highlight_y = int(self.size * 0.35)
        highlight_radius = max(1, int(self.size * 0.2))
        pygame.draw.circle(bubble_surface, (255, 255, 255, 150), (highlight_x, highlight_y), highlight_radius)

        # Draw bubble surface to the screen
        screen.blit(bubble_surface, (int(self.x - self.size), int(self.y - self.size)))

