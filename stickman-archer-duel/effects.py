import random
import pygame

MAX_PARTICLES = 200


class Particle:
    __slots__ = ("pos", "vel", "life", "max_life", "color", "size")

    def __init__(self, pos, vel, life, color, size):
        self.pos = pygame.math.Vector2(pos)
        self.vel = pygame.math.Vector2(vel)
        self.life = life
        self.max_life = life
        self.color = color
        self.size = size

    def update(self, dt):
        self.pos += self.vel * dt
        self.vel.y += 300 * dt
        self.vel *= 0.96
        self.life -= dt

    @property
    def alive(self):
        return self.life > 0

    def draw(self, surface):
        ratio = max(0.0, self.life / self.max_life)
        size = max(1, int(self.size * ratio))
        color = tuple(int(c * (0.4 + 0.6 * ratio)) for c in self.color)
        pygame.draw.circle(surface, color, (int(self.pos.x), int(self.pos.y)), size)


class FloatingText:
    __slots__ = ("pos", "vel", "life", "max_life", "text", "color", "font_key")

    def __init__(self, pos, text, color, font_key="body", life=1.0):
        self.pos = pygame.math.Vector2(pos)
        self.vel = pygame.math.Vector2(0, -50)
        self.life = life
        self.max_life = life
        self.text = text
        self.color = color
        self.font_key = font_key

    def update(self, dt):
        self.pos += self.vel * dt
        self.vel.y += 20 * dt
        self.life -= dt

    @property
    def alive(self):
        return self.life > 0

    def draw(self, surface, fonts):
        font = fonts.get(self.font_key, fonts["body"])
        ratio = max(0.0, self.life / self.max_life)
        surf = font.render(self.text, True, self.color)
        surf.set_alpha(int(255 * ratio))
        rect = surf.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        surface.blit(surf, rect)


class ScreenShake:
    def __init__(self):
        self.duration = 0.0
        self.intensity = 0.0

    def trigger(self, intensity, duration):
        self.intensity = max(self.intensity, intensity)
        self.duration = max(self.duration, duration)

    def update(self, dt):
        if self.duration > 0:
            self.duration -= dt
            if self.duration <= 0:
                self.duration = 0
                self.intensity = 0

    @property
    def offset(self):
        if self.duration <= 0:
            return (0, 0)
        return (
            random.uniform(-self.intensity, self.intensity),
            random.uniform(-self.intensity, self.intensity),
        )


class EffectsManager:
    def __init__(self):
        self.particles = []
        self.floating_texts = []
        self.shake = ScreenShake()

    def reset(self):
        self.particles.clear()
        self.floating_texts.clear()
        self.shake = ScreenShake()

    def spawn_burst(self, pos, color, count=14, speed_range=(80, 240), size=4, life_range=(0.35, 0.7)):
        count = min(count, MAX_PARTICLES - len(self.particles))
        for _ in range(max(0, count)):
            angle = random.uniform(0, 6.28318)
            speed = random.uniform(*speed_range)
            vel = pygame.math.Vector2(1, 0).rotate_rad(angle) * speed
            life = random.uniform(*life_range)
            self.particles.append(Particle(pos, vel, life, color, size))

    def spawn_text(self, pos, text, color, font_key="body", life=1.0):
        self.floating_texts.append(FloatingText(pos, text, color, font_key, life))

    def update(self, dt):
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive]

        for t in self.floating_texts:
            t.update(dt)
        self.floating_texts = [t for t in self.floating_texts if t.alive]

        self.shake.update(dt)

    def draw(self, surface, fonts):
        for p in self.particles:
            p.draw(surface)
        for t in self.floating_texts:
            t.draw(surface, fonts)
