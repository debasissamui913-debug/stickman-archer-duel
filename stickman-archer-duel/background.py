import math
import pygame

import settings
from draw_utils import draw_vertical_gradient, draw_glow_circle


SUN_COLOR = (255, 244, 200)


def get_theme(theme_id):
    for theme in settings.BACKGROUND_THEMES:
        if theme["id"] == theme_id:
            return theme
    return settings.BACKGROUND_THEMES[0]


class Background:
    def __init__(self, theme_id=None):
        self.time = 0.0
        self._cloud_seeds = [
            (150, 90, 1.0, 40),
            (520, 130, 0.6, 55),
            (900, 70, 0.8, 35),
            (1150, 150, 0.5, 45),
        ]
        self._hill_far_points = self._make_hill_points(seed_offset=0, amplitude=26, base_y=settings.GROUND_Y - 70)
        self._hill_near_points = self._make_hill_points(seed_offset=3.1, amplitude=34, base_y=settings.GROUND_Y - 35)
        self.set_theme(theme_id or settings.DEFAULT_BACKGROUND_ID)

    def set_theme(self, theme_id):
        theme = get_theme(theme_id)
        self.theme_id = theme["id"]
        self.sky_top = theme["sky_top"]
        self.sky_bottom = theme["sky_bottom"]
        self.hill_far = theme["hill_far"]
        self.hill_near = theme["hill_near"]
        self.ground_top = theme["ground_top"]
        self.ground_bottom = theme["ground_bottom"]

    def _make_hill_points(self, seed_offset, amplitude, base_y):
        points = []
        for i in range(0, settings.SCREEN_WIDTH + 40, 40):
            y = base_y + math.sin(i * 0.01 + seed_offset) * amplitude
            points.append((i, y))
        return points

    def update(self, dt):
        self.time += dt

    def draw(self, surface):
        draw_vertical_gradient(
            surface, (0, 0, settings.SCREEN_WIDTH, settings.GROUND_Y), self.sky_top, self.sky_bottom
        )

        draw_glow_circle(surface, (settings.SCREEN_WIDTH - 150, 110), 55, SUN_COLOR, layers=5)
        pygame.draw.circle(surface, SUN_COLOR, (settings.SCREEN_WIDTH - 150, 110), 42)

        for base_x, base_y, speed, size in self._cloud_seeds:
            drift = (self.time * speed * 6) % (settings.SCREEN_WIDTH + 200)
            x = (base_x + drift) % (settings.SCREEN_WIDTH + 200) - 100
            self._draw_cloud(surface, (x, base_y), size)

        self._draw_hill_layer(surface, self._hill_far_points, self.hill_far)
        self._draw_hill_layer(surface, self._hill_near_points, self.hill_near)

        draw_vertical_gradient(
            surface,
            (0, settings.GROUND_Y, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT - settings.GROUND_Y),
            self.ground_top, self.ground_bottom,
        )
        pygame.draw.line(
            surface, (60, 120, 80), (0, settings.GROUND_Y), (settings.SCREEN_WIDTH, settings.GROUND_Y), 3
        )

    def _draw_cloud(self, surface, pos, size):
        x, y = pos
        cloud_surf = pygame.Surface((size * 3, size * 2), pygame.SRCALPHA)
        c = (255, 255, 255, 210)
        pygame.draw.circle(cloud_surf, c, (int(size), int(size)), int(size * 0.6))
        pygame.draw.circle(cloud_surf, c, (int(size * 1.6), int(size * 0.8)), int(size * 0.5))
        pygame.draw.circle(cloud_surf, c, (int(size * 0.5), int(size * 0.9)), int(size * 0.45))
        surface.blit(cloud_surf, (x, y))

    def _draw_hill_layer(self, surface, points, color):
        polygon = list(points) + [(settings.SCREEN_WIDTH + 40, settings.GROUND_Y + 5), (-40, settings.GROUND_Y + 5)]
        pygame.draw.polygon(surface, color, polygon)
