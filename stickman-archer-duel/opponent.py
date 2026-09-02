import random
import pygame
import settings
import stickman
class Opponent:
    def __init__(self):
        self.feet_pos = pygame.math.Vector2(0, settings.GROUND_Y)
        self.facing = -1  # faces left, toward the player
        self.alive = True
        self.shield_up = False
        self.shield_timer = settings.SHIELD_DOWN_DURATION
        self.shield_warning = False
        self.hit_flash_timer = 0.0
        self.aiming = False
        self.aim_angle = 180
        self.is_boss = False
        self.guard_zone = "body"
        self._shield_up_duration = settings.SHIELD_UP_DURATION
        self._shield_down_duration = settings.SHIELD_DOWN_DURATION

    @property
    def head_pos(self):
        return pygame.math.Vector2(stickman.head_position(self.feet_pos))

    @property
    def body_pos(self):
        return pygame.math.Vector2(stickman.body_center_position(self.feet_pos))

    @property
    def hand_pos(self):
        shoulder_y = self.feet_pos.y - 62 - 5
        return pygame.math.Vector2(self.feet_pos.x + 22 * self.facing, shoulder_y)

    def position_for_level(self, level_number):
        distance = settings.BASE_OPPONENT_DISTANCE + (level_number - 1) * settings.DISTANCE_INCREMENT
        target_x = settings.PLAYER_X + distance
        target_x = min(target_x, settings.MAX_OPPONENT_X)
        self.feet_pos = pygame.math.Vector2(target_x, settings.GROUND_Y)

    def get_wind_force(self, level_number):
        distance = settings.BASE_OPPONENT_DISTANCE + (level_number - 1) * settings.DISTANCE_INCREMENT
        overflow_levels = max(0, (distance - (settings.MAX_OPPONENT_X - settings.PLAYER_X)) / settings.DISTANCE_INCREMENT)
        ramp = min(1.0, overflow_levels / settings.WIND_LEVEL_RAMP)
        if ramp <= 0:
            return 0.0
        rng = random.Random(int(level_number))
        direction = 1 if rng.random() > 0.5 else -1
        return direction * ramp * settings.WIND_MAX_FORCE

    def _shield_ramp_ratio(self, level_number):
        return min(1.0, max(0.0, (level_number - 1) / settings.SHIELD_LEVEL_RAMP))

    def reset_for_level(self, level_number, is_boss=False):
        self.alive = True
        self.is_boss = is_boss
        self.hit_flash_timer = 0.0
        self.shield_up = False
        self.shield_warning = False
        self.guard_zone = "body"

        ratio = self._shield_ramp_ratio(level_number)
        self._shield_up_duration = settings.SHIELD_UP_DURATION + ratio * (
            settings.SHIELD_UP_DURATION_MAX - settings.SHIELD_UP_DURATION
        )
        self._shield_down_duration = settings.SHIELD_DOWN_DURATION - ratio * (
            settings.SHIELD_DOWN_DURATION - settings.SHIELD_DOWN_DURATION_MIN
        )
        self.shield_timer = self._shield_down_duration
        self.position_for_level(level_number)

    def update(self, dt):
        if not self.alive:
            return

        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt

        self.shield_timer -= dt
        if self.shield_up:
            if self.shield_timer <= 0:
                self.shield_up = False
                self.shield_timer = self._shield_down_duration
        else:
            if self.shield_timer <= settings.SHIELD_WARNING_TIME and not self.shield_warning:
                self.shield_warning = True
                self.guard_zone = "head" if random.random() < settings.SHIELD_HEAD_GUARD_CHANCE else "body"
            if self.shield_timer <= 0:
                self.shield_up = True
                self.shield_warning = False
                self.shield_timer = self._shield_up_duration

    def register_hit(self):
        self.alive = False

    def register_flash(self):
        self.hit_flash_timer = 0.12

    def draw(self, surface):
        color = (255, 255, 255) if self.hit_flash_timer > 0 else (
            (90, 20, 25) if self.is_boss else settings.COLOR_BLACK
        )
        pose = "fallen" if not self.alive else ("aim" if self.aiming else "idle")
        stickman.draw_stickman(
            surface, self.feet_pos, facing=self.facing, color=color, pose=pose, aim_angle=self.aim_angle
        )

        if self.alive and self.is_boss:
            crown_x, crown_y = self.feet_pos.x, self.feet_pos.y - settings.HEAD_OFFSET - settings.HEAD_RADIUS - 10
            pygame.draw.polygon(surface, settings.COLOR_COIN, [
                (crown_x - 10, crown_y + 6), (crown_x - 6, crown_y - 4), (crown_x, crown_y + 2),
                (crown_x + 6, crown_y - 4), (crown_x + 10, crown_y + 6),
            ])

        if self.alive:
            shield_color = (200, 90, 90) if self.shield_warning else (160, 120, 60)
            shield_state = "up" if self.shield_up else ("warning" if self.shield_warning else "down")
            stickman.draw_shield(surface, self.feet_pos, self.facing, shield_state, zone=self.guard_zone, color=shield_color)
