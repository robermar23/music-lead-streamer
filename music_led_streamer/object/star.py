import pygame
import random
import math

# Function to draw a star shape
def draw_star(screen, color, x, y, points, outer_radius, inner_radius):
    angle_step = math.pi / points
    vertices = []
    for i in range(points * 2):
        angle = i * angle_step
        radius = outer_radius if i % 2 == 0 else inner_radius
        vx = x + int(math.cos(angle) * radius)
        vy = y + int(math.sin(angle) * radius)
        vertices.append((vx, vy))
    pygame.draw.polygon(screen, color, vertices)

# Updated Star class
class Star:
    def __init__(self, x, y, color, size, midrange, treble):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.speed_x = random.uniform(-1, 1) * (1 + midrange * 2 + treble * 0.5)
        self.speed_y = random.uniform(-1, 1) * (1 + midrange * 2 + treble * 0.5)
        self.life = 75
        self.points = random.randint(5, 10)

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1

    def is_alive(self):
        return self.life > 0

    def draw(self, screen):
        alpha = max(0, self.life / 100)
        faded_color = (
            int(self.color[0] * alpha),
            int(self.color[1] * alpha),
            int(self.color[2] * alpha),
        )
        draw_star(screen, faded_color, int(self.x), int(self.y), self.points, self.size, self.size // 2)
