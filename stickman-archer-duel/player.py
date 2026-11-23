import math
import pygame
import settings
import stickman
class Player:
    def __init__(self, sound_manager):
        self.sounds = sound_manager
        self.feet_pos = pygame.math.Vector2(settings.PLAYER_X, settings.GROUND_Y)
        self.facing = 1

        self.dragging = False
        self.drag_current = pygame.math.Vector2(0, 0)
        self.bow_color = settings.SHOP_ITEMS[0]["bow_color"]
        self.arrow_color = settings.SHOP_ITEMS[0]["arrow_color"]
        self.skin_id = settings.DEFAULT_SKIN_ID
        self.animation_time = 0.0
        self.body_color = settings.PLAYER_COLOR_ITEMS[0]["color"]

        self.last_aim_angle = 35  
        self.alive = True
        self.hit_flash_timer = 0.0

    def set_skin(self, bow_color, arrow_color, skin_id=settings.DEFAULT_SKIN_ID):
        self.bow_color = bow_color
        self.arrow_color = arrow_color
        self.skin_id = skin_id

    def set_body_color(self, color):
        self.body_color = color

    def reset_combat_state(self):
        self.alive = True
        self.hit_flash_timer = 0.0
        self.cancel_drag()

    def register_hit_flash(self):
        self.hit_flash_timer = 0.12

    def register_defeat(self):
        self.alive = False

    @property
    def hand_pos(self):
       
        shoulder_y = self.feet_pos.y - 62 - 5
        return pygame.math.Vector2(self.feet_pos.x + 22 * self.facing, shoulder_y)

    @property
    def head_pos(self):
        return pygame.math.Vector2(stickman.head_position(self.feet_pos))

    @property
    def body_pos(self):
        return pygame.math.Vector2(stickman.body_center_position(self.feet_pos))

    def start_drag(self, mouse_pos):
        self.dragging = True
        self.drag_current = pygame.math.Vector2(mouse_pos)

    def update_drag(self, mouse_pos):
        if self.dragging:
            self.drag_current = pygame.math.Vector2(mouse_pos)

    def cancel_drag(self):
        self.dragging = False

    def _pull_vector(self):
        pull = self.hand_pos - self.drag_current
        if pull.length() > settings.DRAG_MAX_LENGTH:
            pull.scale_to_length(settings.DRAG_MAX_LENGTH)
        return pull

    def get_aim_preview(self):
        pull = self._pull_vector()
        if pull.length_squared() == 0:
            return self.last_aim_angle, 0.0
        angle = math.degrees(math.atan2(-pull.y, pull.x * self.facing))
        power_ratio = pull.length() / settings.DRAG_MAX_LENGTH
        return angle, power_ratio

    def release_shot(self):
        pull = self._pull_vector()
        self.dragging = False

        if pull.length() < 12:  
            return None

        power_ratio = pull.length() / settings.DRAG_MAX_LENGTH
        speed = settings.POWER_MIN_SPEED + power_ratio * (
            settings.POWER_MAX_SPEED - settings.POWER_MIN_SPEED
        )
        direction = pull.normalize()
        velocity = direction * speed

        angle = math.degrees(math.atan2(-direction.y, direction.x * self.facing))
        self.last_aim_angle = angle

        return self.hand_pos.copy(), velocity

    def update(self, dt):
        self.animation_time += dt
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt

    def draw(self, surface):
        if not self.alive:
            stickman.draw_stickman(surface, self.feet_pos, facing=self.facing, color=self.body_color, pose="fallen")
            return

        pose = "aim" if self.dragging else "idle"
        angle = self.last_aim_angle
        if self.dragging:
            angle, _ = self.get_aim_preview()

        color = (255, 255, 255) if self.hit_flash_timer > 0 else self.body_color
        stickman.draw_stickman(
            surface, self.feet_pos, facing=self.facing, pose=pose, color=color,
            aim_angle=angle, bow_color=self.bow_color, skin_id=self.skin_id,
            animation_time=self.animation_time,
        )

    def draw_trajectory_preview(self, surface):
        if not self.dragging:
            return
        pull = self._pull_vector()
        if pull.length() < 12:
            return

        power_ratio = pull.length() / settings.DRAG_MAX_LENGTH
        speed = settings.POWER_MIN_SPEED + power_ratio * (
            settings.POWER_MAX_SPEED - settings.POWER_MIN_SPEED
        )
        direction = pull.normalize()
        velocity = direction * speed

        pos = self.hand_pos.copy()
        vel = velocity.copy()
        dt = 0.03
        for i in range(40):
            vel.y += settings.GRAVITY * dt
            pos += vel * dt
            if i % 2 == 0:
                pygame.draw.circle(surface, (255, 255, 255), (int(pos.x), int(pos.y)), 2)
            if pos.y > settings.GROUND_Y or pos.x < 0 or pos.x > settings.SCREEN_WIDTH:
                break
        pygame.draw.line(surface, (255, 255, 255), self.hand_pos, self.drag_current, 2)
