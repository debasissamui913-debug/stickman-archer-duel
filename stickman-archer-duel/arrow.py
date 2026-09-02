import math
import pygame
import settings
class Arrow:
    def __init__(self, pos, velocity, color, wind_force=0.0):
        self.pos = pygame.math.Vector2(pos)
        self.velocity = pygame.math.Vector2(velocity)
        self.color = color
        self.wind_force = wind_force
        self.trail = []
        self.active = True
        self.result = None  

    @property
    def angle(self):
        if self.velocity.length_squared() == 0:
            return 0
        return math.degrees(math.atan2(-self.velocity.y, self.velocity.x))

    def update(self, dt):
        self.trail.append((self.pos.x, self.pos.y))
        if len(self.trail) > settings.ARROW_TRAIL_LENGTH:
            self.trail.pop(0)

        self.velocity.y += settings.GRAVITY * dt
        self.velocity.x += self.wind_force * dt
        self.pos += self.velocity * dt

        if self.pos.x < -60 or self.pos.x > settings.SCREEN_WIDTH + 60:
            self.active = False
        if self.pos.y > settings.SCREEN_HEIGHT + 60:
            self.active = False

    def draw(self, surface):
        count = len(self.trail)
        for i, point in enumerate(self.trail):
            ratio = (i + 1) / max(count, 1)
            radius = max(1, int(settings.ARROW_RADIUS * ratio * 0.55))
            trail_color = tuple(int(c * ratio * 0.55) for c in self.color)
            pygame.draw.circle(surface, trail_color, (int(point[0]), int(point[1])), radius)

        rad = math.radians(self.angle)
        direction = pygame.math.Vector2(math.cos(rad), -math.sin(rad))
        tail = self.pos - direction * 18
        pygame.draw.line(surface, self.color, tail, self.pos, 3)

        tip = self.pos + direction * 7
        perp = pygame.math.Vector2(-direction.y, direction.x)
        left = self.pos - perp * 4
        right = self.pos + perp * 4
        pygame.draw.polygon(surface, self.color, [tip, left, right])
