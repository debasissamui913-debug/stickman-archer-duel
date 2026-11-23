import math
import pygame
import settings
class Arrow:
    def __init__(self, pos, velocity, color, wind_force=0.0, skin_id=settings.DEFAULT_SKIN_ID):
        self.pos = pygame.math.Vector2(pos)
        self.velocity = pygame.math.Vector2(velocity)
        self.color = color
        self.wind_force = wind_force
        self.skin_id = skin_id
        self.animation_time = 0.0
        self.trail = []
        self.active = True
        self.result = None  

    @property
    def angle(self):
        if self.velocity.length_squared() == 0:
            return 0
        return math.degrees(math.atan2(-self.velocity.y, self.velocity.x))

    def update(self, dt):
        self.animation_time += dt
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
        if self.skin_id == "godly":
            glow = pygame.Surface((36, 36), pygame.SRCALPHA)
            pygame.draw.circle(glow, (75, 220, 255, 75), (18, 18), 17)
            surface.blit(glow, (int(self.pos.x) - 18, int(self.pos.y) - 18))
        count = len(self.trail)
        for i, point in enumerate(self.trail):
            ratio = (i + 1) / max(count, 1)
            radius = max(1, int(settings.ARROW_RADIUS * ratio * 0.55))
            trail_color = (
                (int(70 + 70 * ratio), int(150 + 90 * ratio), 255)
                if self.skin_id == "godly"
                else tuple(int(c * ratio * 0.55) for c in self.color)
            )
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
        if self.skin_id == "godly":
            for i in range(3):
                angle = self.animation_time * 4 + i * math.tau / 3
                sparkle_x = self.pos.x + math.cos(angle) * 9
                sparkle_y = self.pos.y + math.sin(angle) * 9
                pygame.draw.circle(surface, (190, 250, 255), (int(sparkle_x), int(sparkle_y)), 2)
