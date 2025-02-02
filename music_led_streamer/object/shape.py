import pygame
import random
import math
from music_led_streamer.util import hsv_to_rgb

# Shape Class
class Shape:
    def __init__(self, x, y, size, color, lifetime, treble, midrange, bass):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.alpha = 0  # Start fully transparent
        self.lifetime = lifetime
        self.age = 0

        # Determine movement direction based on frequencies
        self.dx = 0
        self.dy = 0

        # Unique properties for behaviors
        self.angle = random.uniform(0, 360)  # Rotation angle
        self.rotation_speed = random.uniform(30, 100)  # Degrees per second
        self.pulse = random.uniform(0.5, 1.5)  # Pulsating scale factor
        self.twinkle_rate = random.uniform(5, 15)  # Twinkle speed

        # Randomly choose a shape type (circle, star, snowflake, polygon)
        self.shape_type = random.choice([
            'circle', 'star', 'snowflake', 'polygon', 
            'diamond', 'spiral', 'heart', 'burst', 'wave',
            'pentagon', 'hexagon', 'cross', 'flower', 'arrow', 'gear', 'cloud'
        ])
        #self.shape_type = "circle"

        # Vertical movement based on treble (higher treble moves upward)
        if treble > bass + midrange:
            self.dy = -1 * (treble / 10)  # Upward motion

        # Vertical movement based on bass (higher bass moves downward)
        if bass > midrange + treble:
            self.dy = bass / 10  # Downward motion

        # Horizontal movement based on midrange
        if midrange > bass + treble:
            mid_normalized = midrange / (bass + midrange + treble)
            if mid_normalized < 0.5:  # Closer to lower frequencies
                self.dx = -1 * (midrange / 10)  # Leftward motion
            else:  # Closer to higher frequencies
                self.dx = midrange / 10  # Rightward motion

    
    def update(self, dt):
        self.age += dt
        # Update position based on direction
        self.x += self.dx
        self.y += self.dy

        # Keep shapes on screen by wrapping around
        screen_width, screen_height = pygame.display.get_surface().get_size()
        self.x %= screen_width
        self.y %= screen_height

        # Ensure positions are integers
        self.x = int(self.x)
        self.y = int(self.y)

        # Fade in
        if self.age < self.lifetime / 3:
            self.alpha = min(255, int(255 * (self.age / (self.lifetime / 3))))
        # Fade out
        elif self.age > 2 * self.lifetime / 3:
            self.alpha = max(0, int(255 * ((self.lifetime - self.age) / (self.lifetime / 3))))
        else:
            self.alpha = 255

         # Adjust unique behavior per shape type
        if self.shape_type == 'circle':
            self.angle = (self.angle + self.rotation_speed * dt) % 360  # Spin
        elif self.shape_type == 'arrow':
            if random.random() < 0.05:  # Occasionally change direction
                self.dx = random.uniform(-2, 2)
                self.dy = random.uniform(-2, 2)
        elif self.shape_type == 'star':
            self.pulse = 0.9 + 0.1 * math.sin(self.age * self.twinkle_rate)  # Twinkle effect
        elif self.shape_type == 'snowflake':
            self.dx += random.uniform(-0.1, 0.1) * dt  # Slight horizontal drift
        elif self.shape_type == 'diamond':
            self.pulse = 0.8 + 0.2 * math.sin(self.age * 5)  # Pulsating size
        elif self.shape_type == 'wave':
            self.angle = (self.angle + 10 * math.sin(self.age * 3)) % 360  # Sway effect
        elif self.shape_type == 'polygon':
            self.angle = (self.angle + self.rotation_speed * dt) % 360  # Rotate steadily
        elif self.shape_type == 'spiral':
            self.angle = (self.angle + self.rotation_speed * dt) % 360  # Continuous rotation
        elif self.shape_type == 'heart':
            self.size = self.size * (0.9 + 0.1 * math.sin(self.age * 2))  # Heartbeat effect
        elif self.shape_type == 'burst':
            self.pulse = 0.8 + 0.2 * math.cos(self.age * 5)  # Expand and contract


        return self.age < self.lifetime  # Return False if the shape is expired

    def draw(self, screen):
        
         # Convert HSB to RGB for color
        # rgb = hsv_to_rgb(self.hue, self.saturation, self.brightness)
        # self.color = tuple(int(c * 255) for c in rgb)

        surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)

        draw_method = getattr(self, f"draw_{self.shape_type}", None)
        if draw_method:
            draw_method(surf)
        
         # Rotate surface for spinning shapes
        if self.shape_type in ['circle', 'spiral', 'wave', 'polygon']:
            surf = pygame.transform.rotate(surf, self.angle)

        screen.blit(surf, (self.x - self.size, self.y - self.size))

    def draw_circle(self, surf):
        """Draws a circle shape."""
        pygame.draw.circle(surf, (*self.color, self.alpha), (self.size, self.size), self.size)

    def draw_star(self, surf):
        """Draws a star shape."""
        points = []
        num_points = 5
        for i in range(num_points * 2):
            angle = i * math.pi / num_points
            radius = self.size if i % 2 == 0 else self.size / 2
            x = int(self.size + radius * math.cos(angle))
            y = int(self.size + radius * math.sin(angle))
            points.append((x, y))
        pygame.draw.polygon(surf, (*self.color, self.alpha), points)

    def draw_snowflake(self, surf):
        """Draws a snowflake-like pattern."""
        for i in range(6):  # 6 arms for a snowflake
            angle = i * math.pi / 3
            end_x = int(self.size + self.size * math.cos(angle))
            end_y = int(self.size + self.size * math.sin(angle))
            pygame.draw.line(surf, (*self.color, self.alpha), (self.size, self.size), (end_x, end_y), 2)

    def draw_polygon(self, surf):
        """Draws a random polygon with 6-10 sides."""
        num_sides = random.randint(6, 10)
        points = []
        for i in range(num_sides):
            angle = i * 2 * math.pi / num_sides
            x = int(self.size + self.size * math.cos(angle))
            y = int(self.size + self.size * math.sin(angle))
            points.append((x, y))
        pygame.draw.polygon(surf, (*self.color, self.alpha), points)

    def draw_diamond(self, surf):
        """Draws a diamond shape."""
        points = [
            (self.size, 0),  # Top
            (2 * self.size, self.size),  # Right
            (self.size, 2 * self.size),  # Bottom
            (0, self.size)  # Left
        ]
        pygame.draw.polygon(surf, (*self.color, self.alpha), points)

    def draw_spiral(self, surf):
        """Draws a spiral pattern."""
        center = (self.size, self.size)
        for i in range(20):
            angle = i * 0.3
            radius = i * 2
            x = int(center[0] + radius * math.cos(angle))
            y = int(center[1] + radius * math.sin(angle))
            pygame.draw.circle(surf, (*self.color, self.alpha), (x, y), 2)

    def draw_heart(self, surf):
        """Draws a heart shape."""
        for angle in range(0, 360, 5):
            theta = math.radians(angle)
            x = int(self.size + self.size * 0.5 * (16 * math.sin(theta) ** 3))
            y = int(self.size - self.size * 0.5 * (13 * math.cos(theta) - 5 * math.cos(2 * theta) - 2 * math.cos(3 * theta) - math.cos(4 * theta)))
            pygame.draw.circle(surf, (*self.color, self.alpha), (x, y), 2)

    def draw_burst(self, surf):
        """Draws a burst shape with radial lines."""
        center = (self.size, self.size)
        for i in range(12):
            angle = i * math.pi / 6
            end_x = int(center[0] + self.size * math.cos(angle))
            end_y = int(center[1] + self.size * math.sin(angle))
            pygame.draw.line(surf, (*self.color, self.alpha), center, (end_x, end_y), 2)

    def draw_wave(self, surf):
        """Draws a wavy line."""
        points = []
        for x in range(0, 2 * self.size, 4):
            y = int(self.size + 10 * math.sin(2 * math.pi * x / self.size))
            points.append((x, y))
        if len(points) >= 2:
            pygame.draw.lines(surf, (*self.color, self.alpha), False, points, 2)
    
    def draw_pentagon(self, surf):
        """Draws a pentagon shape."""
        self.draw_regular_polygon(surf, 5)

    def draw_hexagon(self, surf):
        """Draws a hexagon shape."""
        self.draw_regular_polygon(surf, 6)

    def draw_cross(self, surf):
        """Draws a cross shape."""
        points = [
            (self.size - self.size // 3, self.size - self.size // 2),
            (self.size + self.size // 3, self.size - self.size // 2),
            (self.size + self.size // 3, self.size - self.size // 3),
            (self.size + self.size // 2, self.size - self.size // 3),
            (self.size + self.size // 2, self.size + self.size // 3),
            (self.size + self.size // 3, self.size + self.size // 3),
            (self.size + self.size // 3, self.size + self.size // 2),
            (self.size - self.size // 3, self.size + self.size // 2),
            (self.size - self.size // 3, self.size + self.size // 3),
            (self.size - self.size // 2, self.size + self.size // 3),
            (self.size - self.size // 2, self.size - self.size // 3),
            (self.size - self.size // 3, self.size - self.size // 3),
        ]
        pygame.draw.polygon(surf, (*self.color, self.alpha), points)

    def draw_flower(self, surf):
        """Draws a flower pattern."""
        center = (self.size, self.size)
        for i in range(6):
            angle = i * math.pi / 3
            petal_x = int(center[0] + self.size * math.cos(angle))
            petal_y = int(center[1] + self.size * math.sin(angle))
            pygame.draw.circle(surf, (*self.color, self.alpha), (petal_x, petal_y), self.size // 3)

    def draw_arrow(self, surf):
        """Draws an arrow pointing in a random direction."""
        points = [
            (self.size, 0),  # Tip
            (2 * self.size, self.size),  # Right wing
            (self.size + self.size // 4, self.size),
            (self.size + self.size // 4, 2 * self.size),  # Shaft bottom
            (self.size - self.size // 4, 2 * self.size),
            (self.size - self.size // 4, self.size),
            (0, self.size)  # Left wing
        ]
        pygame.draw.polygon(surf, (*self.color, self.alpha), points)

    def draw_gear(self, surf):
        """Draws a gear-like pattern."""
        center = (self.size, self.size)
        for i in range(12):
            angle = i * math.pi / 6
            tooth_x = int(center[0] + self.size * math.cos(angle))
            tooth_y = int(center[1] + self.size * math.sin(angle))
            pygame.draw.line(surf, (*self.color, self.alpha), center, (tooth_x, tooth_y), 2)

    def draw_cloud(self, surf):
        """Draws a cloud shape."""
        base = (self.size, self.size)
        for i in range(-2, 3):
            pygame.draw.circle(surf, (*self.color, self.alpha), (base[0] + i * self.size // 3, base[1]), self.size // 3)
        pygame.draw.circle(surf, (*self.color, self.alpha), base, self.size // 2)

    def draw_regular_polygon(self, surf, num_sides):
        """Draws a regular polygon with `num_sides` sides."""
        points = []
        for i in range(num_sides):
            angle = i * 2 * math.pi / num_sides
            x = int(self.size + self.size * math.cos(angle))
            y = int(self.size + self.size * math.sin(angle))
            points.append((x, y))
        pygame.draw.polygon(surf, (*self.color, self.alpha), points)