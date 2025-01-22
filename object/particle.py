import random
import pygame

class Particle:
    def __init__(self, x, y, color, size,  midrange, treble):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        # self.speed_x = speed_x
        self.speed_x = random.uniform(-1, 1) * (1 + midrange * 2 + treble * 0.5)  # Speed influenced by midrange and treble
        self.speed_y = random.uniform(-1, 1) * (1 + midrange * 2 + treble * 0.5)
        # self.speed_y = speed_y
        self.life = 75  # Particle lifespan (affects fading)

    def move(self):
        """Move the particle based on its speed."""
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1  # Decrease life to simulate fading

    def is_alive(self):
        """Check if the particle is still alive."""
        return self.life > 0

    def draw(self, screen):
        """Draw the particle on the screen with fading."""
        alpha = max(0, self.life / 100)  # Calculate alpha for fading
        faded_color = (
            int(self.color[0] * alpha),
            int(self.color[1] * alpha),
            int(self.color[2] * alpha),
        )
        pygame.draw.circle(screen, faded_color, (int(self.x), int(self.y)), self.size)

class RingExpandingParticle:
    def __init__(self, x, y, color, initial_radius, bass):
        self.x = x
        self.y = y
        self.color = color
        self.radius = initial_radius
        #self.expansion_rate = expansion_rate
        self.expansion_rate = 1 + bass * 0.25  # Expansion rate based on bass frequency
        self.life = 50  # Lifespan of the ring

    def expand(self):
        """Expand the ring and reduce its life."""
        self.radius += self.expansion_rate
        self.life -= 1

    def is_alive(self):
        """Check if the ring is still visible."""
        return self.life > 0

    def draw(self, screen):
        """Draw the ring with fading effect."""
        alpha = max(0, self.life / 100)  # Calculate fading alpha
        faded_color = (
            int(self.color[0] * alpha),
            int(self.color[1] * alpha),
            int(self.color[2] * alpha),
        )
        pygame.draw.circle(screen, faded_color, (int(self.x), int(self.y)), int(self.radius), int(self.life / 4))

class RingCollapsingParticle:
    def __init__(self, x, y, color, initial_radius, bass):
        self.x = x
        self.y = y
        self.color = color
        self.initial_radius = initial_radius
        self.radius = initial_radius
        self.shrink_rate = 1 + bass * 0.25  # Shrink rate based on bass frequency
        self.life = 50  # Lifespan of the ring

    def expand(self):
        """Shrink the ring and reduce its life."""
        self.radius -= self.shrink_rate
        self.life -= 1

    def is_alive(self):
        """Check if the ring is still visible."""
        return self.radius > 0 and self.life > 0

    def draw(self, screen):
        """Draw the ring with fading effect."""
        alpha = max(0, self.life / 100)  # Calculate fading alpha
        faded_color = (
            int(self.color[0] * alpha),
            int(self.color[1] * alpha),
            int(self.color[2] * alpha),
        )
        if self.radius > 0:  # Only draw if the radius is positive
            pygame.draw.circle(screen, faded_color, (int(self.x), int(self.y)), int(self.radius), int(self.life / 4))
