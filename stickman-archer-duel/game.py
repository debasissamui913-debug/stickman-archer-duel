import math
import random
import sys
import pygame
import settings
from settings import GameState
from assets import AssetManager
from sounds import SoundManager
from background import Background
from player import Player
from opponent import Opponent
from arrow import Arrow
from effects import EffectsManager
import ui
from ui import Button, TextInputBox
from draw_utils import draw_text_with_shadow, draw_outlined_text, draw_rounded_panel
import progress
from shop import ShopManager

class Game:
    def __init__(self):
        pygame.init()

        self.audio_available = True
        try:
            pygame.mixer.init()
        except pygame.error as e:
            print(f"[Game] Audio device unavailable, sound disabled: {e}")
            self.audio_available = False

        self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        pygame.display.set_caption(settings.GAME_TITLE)

        self.clock = pygame.time.Clock()
        self.running = True

        self.assets = AssetManager()
        self.sounds = SoundManager(self.assets)
        if not self.audio_available:
            self.sounds.set_enabled(False)

        self._font_title = pygame.font.SysFont("arial", 50, bold=True)
        self._font_button = pygame.font.SysFont("consolas", 22, bold=True)
        self._font_body = pygame.font.SysFont("consolas", 20)
        self._font_small = pygame.font.SysFont("consolas", 15)
        self._font_hud = pygame.font.SysFont("consolas", 18, bold=True)
        self._font_headshot = pygame.font.SysFont("consolas", 22, bold=True)
        self._font_name = pygame.font.SysFont("consolas", 15, bold=True)
        self.fonts = {"body": self._font_body, "headshot": self._font_headshot, "small": self._font_small}

        # Progress / Shop
        self.progress_data = progress.load()
        self.shop = ShopManager(self.progress_data)
        self.highest_level = self.progress_data["highest_level"]

        self.background = Background(self.shop.get_equipped_background_id())

        # Core gameplay objects
        self.player = Player(self.sounds)
        self.player.set_skin(*self.shop.get_equipped_bow_colors())
        self.player.set_body_color(self.shop.get_equipped_player_color())
        self.opponent = Opponent()
        self.effects = EffectsManager()

        self.player_arrow = None
        self.enemy_arrows = []

        self.level_number = 1
        self.player_hp = settings.PLAYER_MAX_HP
        self.opponent_hp = settings.OPPONENT_MAX_HP
        self.opponent_max_hp = settings.OPPONENT_MAX_HP
        self.turn = "player"
        self.enemy_turn_timer = 0.0
        self.player_turn_timer = settings.PLAYER_TURN_TIME_LIMIT
        self.win_streak = 0
        self.current_wind_force = 0.0
        self.level_coin_breakdown = None
        self._complete_particles_spawned = False

        self.pause_button_rect = pygame.Rect(settings.SCREEN_WIDTH - 64, 16, 44, 44)
        self.world_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))

        self.state = GameState.MENU
        self._previous_state = GameState.MENU
        self._state_before_pause = GameState.PLAYING
        self._settings_return_state = GameState.MENU
        self.shop_tab = "bow"

        self.menu_buttons = self._build_menu_buttons()
        self.pause_buttons = self._build_pause_buttons()
        self.level_complete_buttons = self._build_level_complete_buttons()
        self.level_failed_buttons = self._build_level_failed_buttons()
        self.settings_widgets = self._build_settings_widgets()
        self.shop_back_button = Button(
            (settings.SCREEN_WIDTH // 2 - 130, settings.SCREEN_HEIGHT - 70, 260, 50),
            "BACK", self._font_button
        )
        self.shop_tab_buttons = self._build_shop_tab_buttons()
        self._shop_card_layout = self._build_shop_layout("bow")

        self.player_name_input = TextInputBox(
            (settings.SCREEN_WIDTH // 2 - 260, 246, 240, 40), self._font_body,
            initial_text=self.shop.player_name, placeholder="Your name",
        )
        self.opponent_name_input = TextInputBox(
            (settings.SCREEN_WIDTH // 2 + 20, 246, 240, 40), self._font_body,
            initial_text=self.shop.opponent_name, placeholder="Opponent name",
        )

    
    def run(self):
        while self.running:
            dt = self.clock.tick(settings.FPS) / 1000.0
            self._handle_events(dt)
            self._update(dt)
            self._draw()
        pygame.quit()
        sys.exit()

    def _handle_events(self, dt):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if self.state == GameState.MENU:
                self._events_menu(event)
            elif self.state == GameState.PLAYING:
                self._events_playing(event)
            elif self.state == GameState.PAUSED:
                self._events_paused(event)
            elif self.state == GameState.LEVEL_COMPLETE:
                self._events_level_complete(event)
            elif self.state == GameState.LEVEL_FAILED:
                self._events_level_failed(event)
            elif self.state == GameState.SHOP:
                self._events_shop(event)
            elif self.state == GameState.SETTINGS:
                self._events_settings(event)
            elif self.state == GameState.HOW_TO_PLAY:
                self._events_info_screen(event)

    def _update(self, dt):
        self.background.update(dt)
        self.player.update(dt)

        if self.state == GameState.PLAYING:
            self._update_playing(dt)
        elif self.state == GameState.MENU:
            self._update_buttons(self.menu_buttons.values(), dt)
            self.player_name_input.update(dt)
            self.opponent_name_input.update(dt)
        elif self.state == GameState.PAUSED:
            self._update_buttons(self.pause_buttons.values(), dt)
        elif self.state == GameState.LEVEL_COMPLETE:
            self._update_buttons(self.level_complete_buttons.values(), dt)
            if not self._complete_particles_spawned:
                self._complete_particles_spawned = True
                center = (settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2)
                self.effects.spawn_burst(center, settings.COLOR_COIN, count=40, speed_range=(120, 320), size=5)
        elif self.state == GameState.LEVEL_FAILED:
            self._update_buttons(self.level_failed_buttons.values(), dt)
        elif self.state == GameState.SHOP:
            self._update_buttons([self.shop_back_button, *self.shop_tab_buttons.values()], dt)
        elif self.state == GameState.SETTINGS:
            self._update_settings_buttons(dt)

        self.effects.update(dt)

    def _update_buttons(self, buttons, dt):
        mouse_pos = pygame.mouse.get_pos()
        for button in buttons:
            button.update(mouse_pos, dt)

    def _draw(self):
        if self.state == GameState.MENU:
            self._draw_menu()
        elif self.state == GameState.PLAYING:
            self._draw_playing()
        elif self.state == GameState.PAUSED:
            self._draw_playing()
            self._draw_pause_overlay()
        elif self.state == GameState.LEVEL_COMPLETE:
            self._draw_playing(show_hud=False)
            self._draw_level_complete_overlay()
        elif self.state == GameState.LEVEL_FAILED:
            self._draw_playing(show_hud=False)
            self._draw_level_failed_overlay()
        elif self.state == GameState.SHOP:
            self._draw_shop()
        elif self.state == GameState.SETTINGS:
            self._draw_settings()
        elif self.state == GameState.HOW_TO_PLAY:
            self._draw_info_screen()
        else:
            self.screen.fill((20, 20, 20))
        pygame.display.flip()

    # MENU
    
    def _build_menu_buttons(self):
        w, h, gap = 280, 56, 14
        cx = settings.SCREEN_WIDTH // 2
        start_y = 330
        labels = ["PLAY", "SHOP", "HOW TO PLAY", "SETTINGS", "EXIT"]
        buttons = {}
        for i, label in enumerate(labels):
            rect = (cx - w // 2, start_y + i * (h + gap), w, h)
            buttons[label] = Button(rect, label, self._font_button)
        return buttons

    def _events_menu(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            was_player_active = self.player_name_input.active
            was_opponent_active = self.opponent_name_input.active

            self.player_name_input.handle_click(event.pos)
            self.opponent_name_input.handle_click(event.pos)

            if was_player_active and not self.player_name_input.active:
                self._commit_player_name()
            if was_opponent_active and not self.opponent_name_input.active:
                self._commit_opponent_name()

            if self.player_name_input.active or self.opponent_name_input.active:
                return  

            for label, button in self.menu_buttons.items():
                if button.is_clicked(event.pos):
                    self.sounds.play("button_click")
                    self._handle_menu_selection(label)
                    break

        elif event.type == pygame.KEYDOWN:
            if self.player_name_input.active:
                self.player_name_input.handle_key(event)
                if not self.player_name_input.active:
                    self._commit_player_name()
            elif self.opponent_name_input.active:
                self.opponent_name_input.handle_key(event)
                if not self.opponent_name_input.active:
                    self._commit_opponent_name()

    def _commit_player_name(self):
        name = self.player_name_input.text.strip() or settings.DEFAULT_PLAYER_NAME
        self.player_name_input.text = name
        self.shop.player_name = name
        self._save_progress()

    def _commit_opponent_name(self):
        name = self.opponent_name_input.text.strip() or settings.DEFAULT_OPPONENT_NAME
        self.opponent_name_input.text = name
        self.shop.opponent_name = name
        self._save_progress()

    def _handle_menu_selection(self, label):
        if label == "PLAY":
            self._start_level(self.highest_level)
            self.state = GameState.PLAYING
        elif label == "SHOP":
            self.shop_tab = "bow"
            self._shop_card_layout = self._build_shop_layout("bow")
            self.state = GameState.SHOP
        elif label == "HOW TO PLAY":
            self._previous_state = GameState.MENU
            self.state = GameState.HOW_TO_PLAY
        elif label == "SETTINGS":
            self._settings_return_state = GameState.MENU
            self.state = GameState.SETTINGS
        elif label == "EXIT":
            self.running = False

    def _draw_menu(self):
        self.background.draw(self.screen)

        draw_outlined_text(
            self.screen, self._font_title, settings.GAME_TITLE, settings.COLOR_WHITE,
            (settings.SCREEN_WIDTH // 2, 60), outline_color=(30, 40, 30),
        )
        text = self._font_small.render(
        "Drag to pull back the bow, release to fire!",
        True,
        (55, 65, 50)
        )
        text_rect = text.get_rect(center=(settings.SCREEN_WIDTH // 2, 110))
        self.screen.blit(text, text_rect)


        ui.draw_coin_badge(self.screen, self._font_hud, self.shop.coins, pos=(20, 20))

        best_text = f"Best Level: {max(1, self.highest_level - 1)}"
        

        name_label1 = self._font_small.render("Your Name", True, (45, 60, 45))
        self.screen.blit(name_label1, (self.player_name_input.rect.x, self.player_name_input.rect.y - 20))
        name_label2 = self._font_small.render("Opponent Name", True, (45, 60, 45))
        self.screen.blit(name_label2, (self.opponent_name_input.rect.x, self.opponent_name_input.rect.y - 20))

        self.player_name_input.draw(self.screen)
        self.opponent_name_input.draw(self.screen)

        for button in self.menu_buttons.values():
            button.draw(self.screen)

    # Level lifecycle
    
    def _start_level(self, level_number):
        self.level_number = max(1, level_number)
        is_boss = False  

        self.opponent.reset_for_level(self.level_number, is_boss=is_boss)
        self.current_wind_force = self.opponent.get_wind_force(self.level_number)

        self.player_hp = settings.PLAYER_MAX_HP
        self.opponent_max_hp = settings.OPPONENT_MAX_HP * (settings.BOSS_HP_MULTIPLIER if is_boss else 1.0)
        self.opponent_hp = self.opponent_max_hp
        self.turn = "player"
        self.enemy_turn_timer = 0.0
        self.player_turn_timer = settings.PLAYER_TURN_TIME_LIMIT

        self.player_arrow = None
        self.enemy_arrows = []
        self.player.reset_combat_state()
        self.player.facing = 1
        self.opponent.aiming = False

        self.effects.reset()
        self.level_coin_breakdown = None
        self._complete_particles_spawned = False

    def _enemy_damage_multiplier(self):
        return min(
            settings.ENEMY_DAMAGE_RAMP_CAP,
            1.0 + (self.level_number - 1) * settings.ENEMY_DAMAGE_RAMP_PER_LEVEL,
        )

    def _save_progress(self):
        progress.save(self.shop.to_dict(self.highest_level))

    def _enemy_accuracy_error(self):
        error = settings.ENEMY_ACCURACY_ERROR_START - (self.level_number - 1) * settings.ENEMY_ACCURACY_LEVEL_STEP
        return max(settings.ENEMY_ACCURACY_ERROR_MIN, error)
    
    def _events_playing(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._state_before_pause = GameState.PLAYING
            self.state = GameState.PAUSED
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.pause_button_rect.collidepoint(event.pos):
                self.sounds.play("button_click")
                self._state_before_pause = GameState.PLAYING
                self.state = GameState.PAUSED
                return
            if self.turn == "player" and self.player_arrow is None:
                self.player.start_drag(event.pos)

        elif event.type == pygame.MOUSEMOTION:
            if self.player.dragging:
                self.player.update_drag(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.player.dragging:
                result = self.player.release_shot()
                if result:
                    pos, velocity = result
                    _, arrow_color = self.shop.get_equipped_bow_colors()
                    self.player_arrow = Arrow(pos, velocity, arrow_color, wind_force=self.current_wind_force)
                    self.sounds.play("bow_shoot")

    def _update_playing(self, dt):
        self.opponent.update(dt)

        if self.player_arrow:
            self.player_arrow.update(dt)
            self._check_player_arrow_collision()

        if self.turn == "player" and self.player_arrow is None:
            self.player_turn_timer -= dt
            if self.player_turn_timer <= 0:
                self.player.cancel_drag()
                self.effects.spawn_text(
                    (self.player.feet_pos.x, self.player.feet_pos.y - 160), "TIME'S UP!",
                    (220, 90, 80), life=0.9,
                )
                self._start_enemy_turn()

        if self.turn == "opponent" and self.player_arrow is None:
            if not self.enemy_arrows and self.enemy_turn_timer > 0:
                self.enemy_turn_timer -= dt
                self.opponent.aiming = True
                if self.enemy_turn_timer <= 0:
                    self._fire_enemy_arrows()

        if self.enemy_arrows:
            self._update_enemy_arrows(dt)
    
    def _check_player_arrow_collision(self):
        arrow = self.player_arrow
        if arrow is None:
            return
        opp = self.opponent

        if opp.alive:
            head_dist = (arrow.pos - opp.head_pos).length()
            if head_dist <= settings.HEAD_RADIUS + settings.ARROW_RADIUS:
                blocked = opp.shield_up and opp.guard_zone == "head"
                self._resolve_player_shot("blocked" if blocked else "headshot")
                return

            body_dist = (arrow.pos - opp.body_pos).length()
            if body_dist <= settings.BODY_HIT_RADIUS + settings.ARROW_RADIUS:
                blocked = opp.shield_up and opp.guard_zone == "body"
                self._resolve_player_shot("blocked" if blocked else "hit")
                return

        if arrow.pos.y >= settings.GROUND_Y or not arrow.active:
            self._resolve_player_shot("miss")

    def _resolve_player_shot(self, result):
        arrow = self.player_arrow
        impact_pos = pygame.math.Vector2(arrow.pos)
        self.player_arrow = None

        if result == "headshot":
            damage = settings.DAMAGE_HEAD
            self.opponent_hp = max(0, self.opponent_hp - damage)
            self.opponent.register_flash()
            self.shop.add_coins(settings.COIN_PER_HIT)
            self.sounds.play("headshot")
            self.effects.spawn_burst(self.opponent.head_pos, settings.COLOR_HEADSHOT, count=24, speed_range=(110, 270))
            self.effects.spawn_text(self.opponent.head_pos, "HEADSHOT!", settings.COLOR_HEADSHOT, font_key="headshot", life=1.2)
            self.effects.spawn_text((self.opponent.head_pos.x, self.opponent.head_pos.y - 30), f"+{settings.COIN_PER_HIT}", settings.COLOR_COIN, life=0.9)
            self.effects.shake.trigger(8, 0.25)
            if self.opponent_hp <= 0:
                self.opponent.register_hit()
                self._win_level(is_headshot=True)
                return

        elif result == "hit":
            damage = settings.DAMAGE_BODY
            self.opponent_hp = max(0, self.opponent_hp - damage)
            self.opponent.register_flash()
            self.shop.add_coins(settings.COIN_PER_HIT)
            self.sounds.play("arrow_hit")
            self.effects.spawn_burst(self.opponent.body_pos, (200, 70, 70), count=16)
            self.effects.spawn_text(self.opponent.body_pos, "HIT!", settings.COLOR_WHITE, life=0.9)
            self.effects.spawn_text((self.opponent.body_pos.x, self.opponent.body_pos.y - 30), f"+{settings.COIN_PER_HIT}", settings.COLOR_COIN, life=0.9)
            self.effects.shake.trigger(5, 0.18)
            if self.opponent_hp <= 0:
                self.opponent.register_hit()
                self._win_level(is_headshot=False)
                return

        elif result == "blocked":
            block_pos = self.opponent.head_pos if self.opponent.guard_zone == "head" else self.opponent.body_pos
            self.sounds.play("blocked")
            self.effects.spawn_burst(block_pos, settings.COLOR_BLOCKED, count=10, speed_range=(60, 160))
            self.effects.spawn_text(block_pos, "BLOCKED!", settings.COLOR_BLOCKED, life=0.8)

        else:  # miss
            self.sounds.play("miss")
            self.effects.spawn_text((impact_pos.x, settings.GROUND_Y - 10), "MISS", settings.COLOR_MISS, life=0.7)

        self._start_enemy_turn()

    def _start_enemy_turn(self):
        self.turn = "opponent"
        self.enemy_turn_timer = settings.ENEMY_TURN_DELAY
        angle_to_player = self._angle_from_to(self.opponent.hand_pos, self.player.body_pos, facing=self.opponent.facing)
        self.opponent.aim_angle = angle_to_player
        self.opponent.aiming = True

    def _angle_from_to(self, origin, target, facing):
        direction = pygame.math.Vector2(target) - pygame.math.Vector2(origin)
        if direction.length_squared() == 0:
            return 0
        return math.degrees(math.atan2(-direction.y, direction.x * facing))

    def _win_level(self, is_headshot):
        total = settings.COIN_LEVEL_WIN

        self.level_coin_breakdown = {"total": total, "is_headshot": is_headshot}
        self.shop.add_coins(total)

        if self.level_number >= self.highest_level:
            self.highest_level = self.level_number + 1

        self._save_progress()
        self.sounds.play("level_complete")
        self.state = GameState.LEVEL_COMPLETE

    def _lose_level(self):
        self.win_streak = 0
        self._save_progress()
        self.sounds.play("level_failed")
        self.state = GameState.LEVEL_FAILED

    
    def _fire_enemy_arrows(self):
        self.opponent.aiming = False
        shot_count = 2 if (self.opponent.is_boss and settings.BOSS_DOUBLE_SHOT) else 1
        for _ in range(shot_count):
            self.enemy_arrows.append(self._build_enemy_arrow())
        self.sounds.play("bow_shoot")

    def _build_enemy_arrow(self):
        origin = self.opponent.hand_pos
        target = pygame.math.Vector2(self.player.body_pos)
        distance = abs(target.x - origin.x)

        angle_deg = settings.ENEMY_SHOT_BASE_ANGLE + random.uniform(-6, 6)
        error = self._enemy_accuracy_error()
        angle_deg += random.uniform(-error, error)
        angle_rad = math.radians(angle_deg)

        g = settings.GRAVITY
        sin_2theta = math.sin(2 * angle_rad)
        if abs(sin_2theta) < 0.05:
            sin_2theta = 0.5
        speed = math.sqrt(max(1.0, distance * g / abs(sin_2theta)))
        speed = max(settings.POWER_MIN_SPEED, min(settings.POWER_MAX_SPEED * 1.15, speed))

        direction_x = -1 if self.opponent.facing < 0 else 1
        velocity = pygame.math.Vector2(
            math.cos(angle_rad) * speed * direction_x,
            -math.sin(angle_rad) * speed,
        )

        color = (190, 60, 60)
        return Arrow(origin, velocity, color, wind_force=self.current_wind_force)

    def _update_enemy_arrows(self, dt):
        still_flying = []
        for arrow in self.enemy_arrows:
            arrow.update(dt)
            result = self._evaluate_enemy_arrow(arrow)
            if result is None:
                still_flying.append(arrow)
                continue

            self._apply_enemy_shot_result(result, arrow.pos)
            if self.state != GameState.PLAYING:
                self.enemy_arrows = []
                return

        self.enemy_arrows = still_flying

        if not self.enemy_arrows and self.turn == "opponent" and self.enemy_turn_timer <= 0 and not self.opponent.aiming:
            self.turn = "player"
            self.player_turn_timer = settings.PLAYER_TURN_TIME_LIMIT

    def _evaluate_enemy_arrow(self, arrow):
        if self.player.alive:
            head_dist = (arrow.pos - self.player.head_pos).length()
            if head_dist <= settings.HEAD_RADIUS + settings.ARROW_RADIUS:
                return "headshot"
            body_dist = (arrow.pos - self.player.body_pos).length()
            if body_dist <= settings.BODY_HIT_RADIUS + settings.ARROW_RADIUS:
                return "hit"

        if arrow.pos.y >= settings.GROUND_Y or not arrow.active:
            return "miss"
        return None

    def _apply_enemy_shot_result(self, result, impact_pos):
        impact_pos = pygame.math.Vector2(impact_pos)
        multiplier = self._enemy_damage_multiplier()

        if result == "headshot":
            damage = int(settings.DAMAGE_HEAD * multiplier)
            self.player_hp = max(0, self.player_hp - damage)
            self.player.register_hit_flash()
            self.sounds.play("headshot")
            self.effects.spawn_burst(self.player.head_pos, settings.COLOR_HEADSHOT, count=22, speed_range=(100, 250))
            self.effects.spawn_text(self.player.head_pos, "HEADSHOT!", settings.COLOR_HEADSHOT, font_key="headshot", life=1.2)
            self.effects.shake.trigger(8, 0.25)
            if self.player_hp <= 0:
                self.player.register_defeat()
                self._lose_level()

        elif result == "hit":
            damage = int(settings.DAMAGE_BODY * multiplier)
            self.player_hp = max(0, self.player_hp - damage)
            self.player.register_hit_flash()
            self.sounds.play("arrow_hit")
            self.effects.spawn_burst(self.player.body_pos, (200, 70, 70), count=16)
            self.effects.spawn_text(self.player.body_pos, "HIT!", settings.COLOR_WHITE, life=0.9)
            self.effects.shake.trigger(5, 0.18)
            if self.player_hp <= 0:
                self.player.register_defeat()
                self._lose_level()

        else:  
            self.sounds.play("miss")
            self.effects.spawn_text((impact_pos.x, settings.GROUND_Y - 10), "MISS", settings.COLOR_MISS, life=0.7)

   
    def _draw_playing(self, show_hud=True):
        world = self.world_surface
        self.background.draw(world)
        self.opponent.draw(world)
        if self.player_arrow:
            self.player_arrow.draw(world)
        for arrow in self.enemy_arrows:
            arrow.draw(world)
        self.player.draw_trajectory_preview(world)
        self.player.draw(world)

        ui.draw_name_tag(world, self._font_name, self.shop.player_name, (self.player.feet_pos.x, self.player.feet_pos.y - 145))
        ui.draw_name_tag(world, self._font_name, self.shop.opponent_name, (self.opponent.feet_pos.x, self.opponent.feet_pos.y - 145))

        self.effects.draw(world, self.fonts)

        offset = self.effects.shake.offset
        self.screen.fill((20, 20, 20))
        self.screen.blit(world, offset)

        if show_hud:
            ui.draw_coin_badge(self.screen, self._font_hud, self.shop.coins)
            ui.draw_level_badge(self.screen, self._font_hud, self.level_number, settings.SCREEN_WIDTH // 2)
            ui.draw_wind_indicator(self.screen, self._font_small, self.current_wind_force, pos=(20, 74))

            ui.draw_hp_bar(self.screen, self._font_small, self.shop.player_name, self.player_hp, settings.PLAYER_MAX_HP,
                            (20, 98, 260, 26), align_right=False)
            ui.draw_hp_bar(self.screen, self._font_small, self.shop.opponent_name, self.opponent_hp, self.opponent_max_hp,
                            (settings.SCREEN_WIDTH - 280, 98, 260, 26), align_right=True)

            if self.opponent.is_boss:
                ui.draw_boss_banner(self.screen, self._font_button, self.shop.opponent_name)

            ui.draw_turn_indicator(self.screen, self._font_body, self.turn, self.shop.player_name, self.shop.opponent_name)

            if self.turn == "player" and self.player_arrow is None:
                warning = self.player_turn_timer <= settings.PLAYER_TURN_WARNING_TIME
                ui.draw_turn_timer(self.screen, self.player_turn_timer, settings.PLAYER_TURN_TIME_LIMIT, warning)

            mouse_pos = pygame.mouse.get_pos()
            ui.draw_pause_button(self.screen, self.pause_button_rect, self.pause_button_rect.collidepoint(mouse_pos))

    
    def _build_pause_buttons(self):
        w, h, gap = 260, 54, 14
        cx = settings.SCREEN_WIDTH // 2
        start_y = 280
        labels = ["RESUME", "RESTART LEVEL", "SETTINGS", "MAIN MENU"]
        buttons = {}
        for i, label in enumerate(labels):
            rect = (cx - w // 2, start_y + i * (h + gap), w, h)
            buttons[label] = Button(rect, label, self._font_button)
        return buttons

    def _events_paused(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = self._state_before_pause
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for label, button in self.pause_buttons.items():
                if button.is_clicked(event.pos):
                    self.sounds.play("button_click")
                    self._handle_pause_selection(label)
                    break

    def _handle_pause_selection(self, label):
        if label == "RESUME":
            self.state = self._state_before_pause
        elif label == "RESTART LEVEL":
            self._start_level(self.level_number)
            self.state = GameState.PLAYING
        elif label == "SETTINGS":
            self._settings_return_state = GameState.PAUSED
            self.state = GameState.SETTINGS
        elif label == "MAIN MENU":
            self.state = GameState.MENU

    def _draw_pause_overlay(self):
        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(settings.COLOR_OVERLAY)
        self.screen.blit(overlay, (0, 0))
        draw_outlined_text(self.screen, self._font_title, "PAUSED", settings.COLOR_WHITE, (settings.SCREEN_WIDTH // 2, 190))
        for button in self.pause_buttons.values():
            button.draw(self.screen)

    
    def _build_level_complete_buttons(self):
        w, h = 260, 56
        cx = settings.SCREEN_WIDTH // 2
        return {"CONTINUE": Button((cx - w // 2, 470, w, h), "CONTINUE", self._font_button)}

    def _events_level_complete(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.level_complete_buttons["CONTINUE"].is_clicked(event.pos):
                self.sounds.play("button_click")
                self._start_level(self.level_number + 1)
                self.state = GameState.PLAYING

    def _draw_level_complete_overlay(self):
        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(settings.COLOR_OVERLAY)
        self.screen.blit(overlay, (0, 0))

        panel_rect = (settings.SCREEN_WIDTH // 2 - 220, 160, 440, 240)
        draw_rounded_panel(self.screen, panel_rect, (35, 50, 38, 235), radius=18, shadow=True)
        pygame.draw.rect(self.screen, settings.COLOR_ACCENT, panel_rect, width=2, border_radius=18)

        b = self.level_coin_breakdown or {}
        title = "HEADSHOT VICTORY!" if b.get("is_headshot") else "VICTORY!"
        draw_outlined_text(self.screen, self._font_title, title, settings.COLOR_ACCENT, (settings.SCREEN_WIDTH // 2, 215))

        if self.level_coin_breakdown:
            reward_text = f"Victory Reward:  +{b['total']} coins"
            surf = self._font_body.render(reward_text, True, settings.COLOR_COIN)
            rect = surf.get_rect(center=(settings.SCREEN_WIDTH // 2, 280))
            self.screen.blit(surf, rect)

        self.level_complete_buttons["CONTINUE"].draw(self.screen)

    
    def _build_level_failed_buttons(self):
        w, h, gap = 260, 54, 16
        cx = settings.SCREEN_WIDTH // 2
        return {
            "RETRY": Button((cx - w // 2, 400, w, h), "RETRY", self._font_button),
            "MAIN MENU": Button((cx - w // 2, 400 + h + gap, w, h), "MAIN MENU", self._font_button),
        }

    def _events_level_failed(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for label, button in self.level_failed_buttons.items():
                if button.is_clicked(event.pos):
                    self.sounds.play("button_click")
                    if label == "RETRY":
                        self._start_level(self.level_number)
                        self.state = GameState.PLAYING
                    elif label == "MAIN MENU":
                        self.state = GameState.MENU
                    break

    def _draw_level_failed_overlay(self):
        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(settings.COLOR_OVERLAY)
        self.screen.blit(overlay, (0, 0))
        draw_outlined_text(self.screen, self._font_title, "DEFEATED", (214, 100, 90), (settings.SCREEN_WIDTH // 2, 260))
        draw_text_with_shadow(
            self.screen, self._font_body, f"{self.shop.opponent_name} bested you on Level {self.level_number}",
            settings.COLOR_WHITE, (settings.SCREEN_WIDTH // 2, 320), center=True,
        )
        for button in self.level_failed_buttons.values():
            button.draw(self.screen)

    
    def _build_shop_tab_buttons(self):
        w, h, gap = 180, 44, 12
        total = w * 3 + gap * 2
        start_x = (settings.SCREEN_WIDTH - total) // 2
        y = 110
        labels = [("bow", "BOW"), ("color", "COLOR"), ("background", "BACKGROUND")]
        buttons = {}
        for i, (key, label) in enumerate(labels):
            rect = (start_x + i * (w + gap), y, w, h)
            buttons[key] = Button(rect, label, self._font_button)
        return buttons

    def _build_shop_layout(self, category):
        catalog = {
            "bow": settings.SHOP_ITEMS,
            "color": settings.PLAYER_COLOR_ITEMS,
            "background": settings.BACKGROUND_THEMES,
        }[category]

        cols = 3
        card_w, card_h = 220, 150
        gap_x, gap_y = 30, 26
        total_w = cols * card_w + (cols - 1) * gap_x
        start_x = (settings.SCREEN_WIDTH - total_w) // 2
        start_y = 180

        layout = []
        for i, item in enumerate(catalog):
            row, col = divmod(i, cols)
            x = start_x + col * (card_w + gap_x)
            y = start_y + row * (card_h + gap_y)
            layout.append((item, pygame.Rect(x, y, card_w, card_h)))
        return layout

    def _events_shop(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.shop_back_button.is_clicked(event.pos):
                self.sounds.play("button_click")
                self.state = GameState.MENU
                return

            for key, button in self.shop_tab_buttons.items():
                if button.is_clicked(event.pos):
                    self.sounds.play("button_click")
                    self.shop_tab = key
                    self._shop_card_layout = self._build_shop_layout(key)
                    return

            for item, rect in self._shop_card_layout:
                if rect.collidepoint(event.pos):
                    self._handle_shop_card_click(item["id"])
                    break

    def _handle_shop_card_click(self, item_id):
        category = self.shop_tab
        if self.shop.is_owned(category, item_id):
            if self.shop.equip(category, item_id):
                self.sounds.play("button_click")
                self._apply_equipped_cosmetics()
                self._save_progress()
        else:
            if self.shop.purchase(category, item_id):
                self.sounds.play("purchase")
                self._save_progress()
            else:
                self.sounds.play("button_click")  # can't afford - soft click, no crash

    def _apply_equipped_cosmetics(self):
        self.player.set_skin(*self.shop.get_equipped_bow_colors())
        self.player.set_body_color(self.shop.get_equipped_player_color())
        self.background.set_theme(self.shop.get_equipped_background_id())

    def _draw_shop(self):
        self.background.draw(self.screen)
        draw_outlined_text(self.screen, self._font_title, "SHOP", settings.COLOR_WHITE, (settings.SCREEN_WIDTH // 2, 55))
        ui.draw_coin_badge(self.screen, self._font_hud, self.shop.coins, pos=(20, 20))

        for key, button in self.shop_tab_buttons.items():
            button.base_color = settings.COLOR_ACCENT if self.shop_tab == key else settings.COLOR_BUTTON
            button.draw(self.screen)

        draw_fn = {
            "bow": ui.draw_skin_card,
            "color": ui.draw_color_card,
            "background": ui.draw_background_card,
        }[self.shop_tab]

        for item, rect in self._shop_card_layout:
            owned = self.shop.is_owned(self.shop_tab, item["id"])
            equipped = self.shop.equipped_id(self.shop_tab) == item["id"]
            affordable = self.shop.can_afford(self.shop_tab, item["id"])
            draw_fn(self.screen, rect, self._font_body, self._font_small, item, owned, equipped, affordable)

        self.shop_back_button.draw(self.screen)

    
    def _build_settings_widgets(self):
        cx = settings.SCREEN_WIDTH // 2
        widgets = {
            "sound_toggle": Button((cx - 130, 220, 260, 50), "SOUND: ON", self._font_button),
            "volume_down": Button((cx - 130, 290, 60, 50), "-", self._font_button),
            "volume_up": Button((cx + 70, 290, 60, 50), "+", self._font_button),
            "back": Button((cx - 130, 400, 260, 50), "BACK", self._font_button),
        }
        return widgets

    def _events_settings(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = self._settings_return_state
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for key, widget in self.settings_widgets.items():
                if widget.is_clicked(event.pos):
                    self.sounds.play("button_click")
                    self._handle_settings_click(key)
                    break

    def _handle_settings_click(self, key):
        if key == "sound_toggle":
            self.sounds.toggle_enabled()
        elif key == "volume_down":
            self.sounds.adjust_volume(-0.1)
        elif key == "volume_up":
            self.sounds.adjust_volume(0.1)
        elif key == "back":
            self.state = self._settings_return_state

    def _update_settings_buttons(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        for widget in self.settings_widgets.values():
            widget.update(mouse_pos, dt)
        self.settings_widgets["sound_toggle"].text = f"SOUND: {'ON' if self.sounds.enabled else 'OFF'}"

    def _draw_settings(self):
        self.background.draw(self.screen)
        draw_outlined_text(self.screen, self._font_title, "SETTINGS", settings.COLOR_WHITE, (settings.SCREEN_WIDTH // 2, 110))
        for key in ("sound_toggle", "volume_down", "volume_up", "back"):
            self.settings_widgets[key].draw(self.screen)

        volume_label = self._font_body.render(f"Volume: {int(self.sounds.volume * 100)}%", True, settings.COLOR_WHITE)
        rect = volume_label.get_rect(center=(settings.SCREEN_WIDTH // 2, 315))
        self.screen.blit(volume_label, rect)

    
    def _events_info_screen(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = self._previous_state
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.state = self._previous_state

    def _draw_info_screen(self):
        self.background.draw(self.screen)
        draw_outlined_text(self.screen, self._font_title, "HOW TO PLAY", settings.COLOR_WHITE, (settings.SCREEN_WIDTH // 2, 90))
        lines = [
            "Click and drag away from your archer to pull back the bow.",
            "The farther you drag, the more power your shot has.",
            "Release the mouse to fire the arrow.",
            "Hit the head for a HEADSHOT bonus - and extra damage!",
            "The enemy shoots back after your turn - watch out!",
            "The enemy raises a shield sometimes to block body shots.",
            "You have a few seconds to shoot each turn - don't wait too long!",
            "Whoever's HP reaches zero first loses the duel.",
            "Distance increases each level, and the enemy gets more accurate.",
            "Earn coins per hit and per victory - spend them in the Shop!",
            "",
            "Click anywhere to go back.",
        ]
        for i, line in enumerate(lines):
            surf = self._font_body.render(line, True, settings.COLOR_WHITE)
            rect = surf.get_rect(center=(settings.SCREEN_WIDTH // 2, 175 + i * 34))
            self.screen.blit(surf, rect)
