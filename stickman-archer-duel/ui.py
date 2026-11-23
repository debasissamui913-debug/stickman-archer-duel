import math
import pygame
import settings
from draw_utils import draw_rounded_panel, draw_text_with_shadow, draw_vertical_gradient


class TextInputBox:
    def __init__(self, rect, font, initial_text="", max_length=14, placeholder=""):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.text = initial_text
        self.max_length = max_length
        self.placeholder = placeholder
        self.active = False
        self._cursor_timer = 0.0
        self._cursor_visible = True

    def handle_click(self, mouse_pos):
        self.active = self.rect.collidepoint(mouse_pos)
        return self.active

    def handle_key(self, event):
        if not self.active:
            return
        if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
            self.active = False
        elif event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        else:
            char = event.unicode
            if char and char.isprintable() and len(self.text) < self.max_length:
                self.text += char

    def update(self, dt):
        self._cursor_timer += dt
        if self._cursor_timer >= 0.5:
            self._cursor_timer = 0.0
            self._cursor_visible = not self._cursor_visible

    def draw(self, surface):
        bg = (255, 255, 255, 235) if self.active else (255, 255, 255, 200)
        draw_rounded_panel(surface, self.rect, bg, radius=8, shadow=True, shadow_offset=(0, 2))
        border_color = settings.COLOR_ACCENT if self.active else (120, 120, 120)
        pygame.draw.rect(surface, border_color, self.rect, width=2, border_radius=8)

        display_text = self.text if (self.text or self.active) else self.placeholder
        text_color = (30, 30, 30) if (self.text or self.active) else (140, 140, 140)
        text_surf = self.font.render(display_text, True, text_color)
        text_rect = text_surf.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
        surface.blit(text_surf, text_rect)

        if self.active and self._cursor_visible:
            cursor_x = text_rect.right + 2
            pygame.draw.line(surface, (30, 30, 30), (cursor_x, self.rect.y + 8), (cursor_x, self.rect.bottom - 8), 2)


class Button:
    def __init__(self, rect, text, font, base_color=settings.COLOR_BUTTON,
                 hover_color=settings.COLOR_BUTTON_HOVER, text_color=settings.COLOR_WHITE,
                 enabled=True):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.hovered = False
        self.enabled = enabled
        self._hover_anim = 0.0

    def update(self, mouse_pos, dt=1 / 60):
        self.hovered = self.enabled and self.rect.collidepoint(mouse_pos)
        target = 1.0 if self.hovered else 0.0
        self._hover_anim += (target - self._hover_anim) * min(1.0, dt * 12)

    def is_clicked(self, mouse_pos):
        return self.enabled and self.rect.collidepoint(mouse_pos)

    def draw(self, surface):
        grow = int(4 * self._hover_anim)
        rect = self.rect.inflate(grow, grow)

        color = self.base_color
        if not self.enabled:
            color = tuple(int(c * 0.5) for c in self.base_color)
        elif self._hover_anim > 0:
            color = tuple(
                int(self.base_color[i] + (self.hover_color[i] - self.base_color[i]) * self._hover_anim)
                for i in range(3)
            )

        draw_rounded_panel(surface, rect, color, radius=12, shadow=True, shadow_offset=(0, 4))
        border_color = settings.COLOR_WHITE if self.hovered else (255, 255, 255, 90)
        pygame.draw.rect(surface, border_color, rect, width=2, border_radius=12)

        text_color = self.text_color if self.enabled else (150, 150, 150)
        draw_text_with_shadow(surface, self.font, self.text, text_color, rect.center, center=True)


class ToggleButton:
    def __init__(self, rect, label, font, initial_state=True,
                 on_color=settings.COLOR_ACCENT, off_color=(90, 95, 90),
                 text_color=settings.COLOR_WHITE):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.font = font
        self.state = bool(initial_state)
        self.on_color = on_color
        self.off_color = off_color
        self.text_color = text_color
        self.hovered = False
        self._hover_anim = 0.0

    def update(self, mouse_pos, dt=1 / 60):
        self.hovered = self.rect.collidepoint(mouse_pos)
        target = 1.0 if self.hovered else 0.0
        self._hover_anim += (target - self._hover_anim) * min(1.0, dt * 12)

    def handle_click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.state = not self.state
            return True
        return False

    def draw(self, surface):
        grow = int(3 * self._hover_anim)
        rect = self.rect.inflate(grow, grow)
        base = self.on_color if self.state else self.off_color

        draw_rounded_panel(surface, rect, (*base, 230), radius=10, shadow=True, shadow_offset=(0, 3))
        border_color = settings.COLOR_WHITE if self.hovered else (255, 255, 255, 90)
        pygame.draw.rect(surface, border_color, rect, width=2, border_radius=10)

        status = "ON" if self.state else "OFF"
        display = f"{self.label}: {status}"
        draw_text_with_shadow(surface, self.font, display, self.text_color, rect.center, center=True)


class SettingsMenu:
    def __init__(self, font_title, font_option, font_button, current_settings=None):
        self.font_title = font_title
        self.font_option = font_option
        self.font_button = font_button

        opts = current_settings or {}
        self.values = {
            "sound": opts.get("sound", True),
            "turn_timer": opts.get("turn_timer", True),
            "screen_shake": opts.get("screen_shake", True),
            "show_name_tags": opts.get("show_name_tags", True),
        }

        panel_w, panel_h = 460, 420
        px = (settings.SCREEN_WIDTH - panel_w) // 2
        py = (settings.SCREEN_HEIGHT - panel_h) // 2
        self.panel_rect = pygame.Rect(px, py, panel_w, panel_h)

        toggle_w, toggle_h = 360, 46
        tx = self.panel_rect.centerx - toggle_w // 2
        start_y = self.panel_rect.y + 85
        gap = 58

        self.toggles = {
            "sound": ToggleButton((tx, start_y + gap * 0, toggle_w, toggle_h), "Sound Effects", font_option, self.values["sound"]),
            "turn_timer": ToggleButton((tx, start_y + gap * 1, toggle_w, toggle_h), "Turn Timer", font_option, self.values["turn_timer"]),
            "screen_shake": ToggleButton((tx, start_y + gap * 2, toggle_w, toggle_h), "Screen Shake", font_option, self.values["screen_shake"]),
            "show_name_tags": ToggleButton((tx, start_y + gap * 3, toggle_w, toggle_h), "Name Tags", font_option, self.values["show_name_tags"]),
        }

        self.back_button = Button(
            (self.panel_rect.centerx - 90, self.panel_rect.bottom - 64, 180, 44),
            "DONE",
            font_button,
        )

    def update(self, mouse_pos, dt=1 / 60):
        for toggle in self.toggles.values():
            toggle.update(mouse_pos, dt)
        self.back_button.update(mouse_pos, dt)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._sync_values()
            return "close"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            for key, toggle in self.toggles.items():
                if toggle.handle_click(pos):
                    self.values[key] = toggle.state
            if self.back_button.is_clicked(pos):
                self._sync_values()
                return "close"

        return None

    def _sync_values(self):
        for key, toggle in self.toggles.items():
            self.values[key] = toggle.state

    def draw(self, surface):
        dim = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 140))
        surface.blit(dim, (0, 0))

        draw_rounded_panel(surface, self.panel_rect, (28, 32, 30, 240), radius=18, shadow=True, shadow_offset=(0, 6))
        pygame.draw.rect(surface, settings.COLOR_ACCENT, self.panel_rect, width=2, border_radius=18)

        draw_text_with_shadow(
            surface,
            self.font_title,
            "SETTINGS",
            settings.COLOR_WHITE,
            (self.panel_rect.centerx, self.panel_rect.y + 42),
            center=True,
        )

        for toggle in self.toggles.values():
            toggle.draw(surface)

        self.back_button.draw(surface)


def draw_coin_badge(surface, font, coins, pos=(20, 20)):
    x, y = pos
    w, h = 150, 44
    draw_rounded_panel(surface, (x, y, w, h), (30, 34, 30, 210), radius=20)
    pygame.draw.rect(surface, settings.COLOR_COIN, (x, y, w, h), width=2, border_radius=20)

    coin_center = (x + 26, y + h // 2)
    pygame.draw.circle(surface, settings.COLOR_COIN, coin_center, 13)
    pygame.draw.circle(surface, (180, 130, 30), coin_center, 13, 2)

    text_surf = font.render(str(coins), True, settings.COLOR_WHITE)
    text_rect = text_surf.get_rect(midleft=(x + 46, y + h // 2))
    surface.blit(text_surf, text_rect)


def draw_level_badge(surface, font, level_number, pos_center_x):
    text = f"LEVEL {level_number}"
    w, h = 160, 40
    x = pos_center_x - w // 2
    y = 18
    draw_rounded_panel(surface, (x, y, w, h), (30, 34, 30, 210), radius=20)
    pygame.draw.rect(surface, settings.COLOR_ACCENT, (x, y, w, h), width=2, border_radius=20)
    draw_text_with_shadow(surface, font, text, settings.COLOR_WHITE, (pos_center_x, y + h // 2), center=True)


def draw_arrow_icons(surface, count_remaining, total, pos=(20, 74)):
    x, y = pos
    spacing = 26
    for i in range(total):
        cx = x + i * spacing + 10
        cy = y + 10
        if i < count_remaining:
            pygame.draw.line(surface, settings.COLOR_WHITE, (cx - 8, cy), (cx + 8, cy), 3)
            pygame.draw.polygon(
                surface, settings.COLOR_WHITE,
                [(cx + 8, cy), (cx + 2, cy - 4), (cx + 2, cy + 4)]
            )
        else:
            pygame.draw.line(surface, (90, 90, 90), (cx - 8, cy), (cx + 8, cy), 3)


def draw_pause_button(surface, rect, hovered):
    color = settings.COLOR_BUTTON_HOVER if hovered else (30, 34, 30)
    draw_rounded_panel(surface, rect, (*color, 220), radius=12)
    pygame.draw.rect(surface, settings.COLOR_WHITE, rect, width=2, border_radius=12)
    cx, cy = rect.center
    pygame.draw.rect(surface, settings.COLOR_WHITE, (cx - 8, cy - 9, 5, 18))
    pygame.draw.rect(surface, settings.COLOR_WHITE, (cx + 3, cy - 9, 5, 18))


def draw_wind_indicator(surface, font, wind_force, pos=(20, 110)):
    if abs(wind_force) < 5:
        return
    x, y = pos
    direction = "→" if wind_force > 0 else "←"
    text = f"WIND {direction}"
    color = (255, 220, 150)
    draw_text_with_shadow(surface, font, text, color, (x, y), center=False)


def draw_hp_bar(surface, font, name, hp, max_hp, rect, align_right=False):
    x, y, w, h = rect
    ratio = max(0.0, hp / max_hp)

    name_surf = font.render(name, True, settings.COLOR_WHITE)
    shadow_surf = font.render(name, True, (0, 0, 0))
    if align_right:
        name_rect = name_surf.get_rect(topright=(x + w, y - 20))
    else:
        name_rect = name_surf.get_rect(topleft=(x, y - 20))
    surface.blit(shadow_surf, (name_rect.x + 1, name_rect.y + 1))
    surface.blit(name_surf, name_rect)

    draw_rounded_panel(surface, (x, y, w, h), (30, 32, 34, 220), radius=8)
    fill_color = settings.COLOR_HEALTH_GOOD if ratio > 0.3 else settings.COLOR_HEALTH_LOW
    if ratio > 0:
        fill_rect = (x, y, w * ratio, h) if not align_right else (x + w * (1 - ratio), y, w * ratio, h)
        pygame.draw.rect(surface, fill_color, fill_rect, border_radius=8)
    pygame.draw.rect(surface, settings.COLOR_WHITE, (x, y, w, h), width=2, border_radius=8)

    hp_text = f"{int(hp)}/{int(max_hp)}"
    hp_surf = font.render(hp_text, True, settings.COLOR_WHITE)
    hp_rect = hp_surf.get_rect(center=(x + w // 2, y + h // 2))
    surface.blit(hp_surf, hp_rect)


def draw_name_tag(surface, font, name, above_pos):
    x, y = above_pos
    surf = font.render(name, True, settings.COLOR_WHITE)
    rect = surf.get_rect(center=(int(x), int(y)))
    bg_rect = rect.inflate(16, 8)
    draw_rounded_panel(surface, bg_rect, (20, 24, 20, 170), radius=8, shadow=False)
    surface.blit(surf, rect)


def draw_turn_indicator(surface, font, turn, player_name, opponent_name):
    text = f"{player_name}'s Turn" if turn == "player" else f"{opponent_name} is Aiming..."
    color = settings.COLOR_ACCENT if turn == "player" else (220, 120, 100)
    draw_text_with_shadow(
        surface, font, text, color, (settings.SCREEN_WIDTH // 2, settings.GROUND_Y + 30), center=True
    )


def draw_turn_timer(surface, time_remaining, time_limit, warning):
    w, h = 240, 10
    x = settings.SCREEN_WIDTH // 2 - w // 2
    y = settings.GROUND_Y + 55
    ratio = max(0.0, time_remaining / time_limit)
    draw_rounded_panel(surface, (x, y, w, h), (30, 32, 34, 200), radius=5)
    color = (220, 90, 80) if warning else settings.COLOR_ACCENT
    if ratio > 0:
        pygame.draw.rect(surface, color, (x, y, w * ratio, h), border_radius=5)
    pygame.draw.rect(surface, settings.COLOR_WHITE, (x, y, w, h), width=1, border_radius=5)


def draw_boss_banner(surface, font, opponent_name):
    text = f"⚔ BOSS: {opponent_name} ⚔"
    w = font.size(text)[0] + 50
    h = 44
    rect = (settings.SCREEN_WIDTH // 2 - w // 2, 130, w, h)
    draw_rounded_panel(surface, rect, (90, 20, 25, 230), radius=20)
    pygame.draw.rect(surface, settings.COLOR_COIN, rect, width=2, border_radius=20)
    draw_text_with_shadow(surface, font, text, settings.COLOR_COIN, (settings.SCREEN_WIDTH // 2, 130 + h // 2), center=True)


def draw_streak_badge(surface, font, streak, pos):
    if streak < 2:
        return
    x, y = pos
    text = f"🔥 {streak} Win Streak"
    surf = font.render(text, True, (255, 170, 60))
    rect = surf.get_rect(topleft=(x, y))
    bg_rect = rect.inflate(16, 8)
    draw_rounded_panel(surface, bg_rect, (30, 30, 30, 200), radius=10)
    surface.blit(surf, rect)


def _draw_card_frame(surface, rect, owned, equipped):
    x, y, w, h = rect
    bg_color = (60, 80, 50, 240) if equipped else (40, 46, 40, 230)
    draw_rounded_panel(surface, rect, bg_color, radius=14, shadow=True)
    border_color = settings.COLOR_ACCENT if equipped else (255, 255, 255, 60)
    pygame.draw.rect(surface, border_color, rect, width=2, border_radius=14)


def _draw_card_status(surface, rect, font_small, item, owned, equipped, affordable):
    x, y, w, h = rect
    if equipped:
        status_text, status_color = "EQUIPPED", settings.COLOR_ACCENT
    elif owned:
        status_text, status_color = "OWNED - TAP TO EQUIP", (180, 220, 180)
    elif item.get("code_required"):
        status_text, status_color = "CODE REQUIRED", (130, 225, 255)
    elif affordable:
        status_text, status_color = f"{item['cost']} coins - TAP TO BUY", settings.COLOR_COIN
    else:
        status_text, status_color = f"{item['cost']} coins", (150, 150, 150)
    status_surf = font_small.render(status_text, True, status_color)
    status_rect = status_surf.get_rect(center=(x + w // 2, y + h - 20))
    surface.blit(status_surf, status_rect)


def draw_skin_card(surface, rect, font_name, font_small, item, owned, equipped, affordable, animation_time=0.0):
    x, y, w, h = rect
    _draw_card_frame(surface, rect, owned, equipped)

    preview_cx, preview_cy = x + w // 2, y + 46
    if item["id"] == "godly":
        glow = pygame.Surface((80, 80), pygame.SRCALPHA)
        pulse = int(25 + 18 * (0.5 + 0.5 * math.sin(animation_time * 3)))
        pygame.draw.circle(glow, (100, 220, 255, pulse), (40, 40), 38)
        surface.blit(glow, (preview_cx - 40, preview_cy - 40))
        for i in range(3):
            angle = animation_time * (1.2 + i * 0.25) + i * math.tau / 3
            px = preview_cx + math.cos(angle) * 31
            py = preview_cy + math.sin(angle) * 22
            pygame.draw.circle(surface, (180, 250, 255), (int(px), int(py)), 2 + i % 2)
    pygame.draw.line(surface, item["bow_color"], (preview_cx - 18, preview_cy - 20), (preview_cx - 18, preview_cy + 20), 4)
    pygame.draw.line(surface, item["arrow_color"], (preview_cx - 25, preview_cy), (preview_cx + 20, preview_cy), 4)
    pygame.draw.polygon(
        surface, item["arrow_color"],
        [(preview_cx + 20, preview_cy), (preview_cx + 12, preview_cy - 5), (preview_cx + 12, preview_cy + 5)]
    )

    name_surf = font_name.render(item["name"], True, settings.COLOR_WHITE)
    name_rect = name_surf.get_rect(center=(x + w // 2, y + 90))
    surface.blit(name_surf, name_rect)

    _draw_card_status(surface, rect, font_small, item, owned, equipped, affordable)

def draw_shield_card(surface, rect, font_name, font_small, item, shield_count, affordable):
    x, y, w, h = rect
    _draw_card_frame(surface, rect, shield_count > 0, False)

    cx, cy = x + w // 2, y + 52
    color = item["color"]
    points = [
        (cx, cy - 29), (cx + 24, cy - 20), (cx + 20, cy + 6),
        (cx, cy + 28), (cx - 20, cy + 6), (cx - 24, cy - 20),
    ]
    pygame.draw.polygon(surface, color, points, width=3)
    pygame.draw.line(surface, (205, 250, 255), (cx, cy - 19), (cx, cy + 17), 2)
    pygame.draw.line(surface, (205, 250, 255), (cx - 14, cy - 7), (cx + 14, cy - 7), 2)

    name_surf = font_name.render(item["name"], True, settings.COLOR_WHITE)
    surface.blit(name_surf, name_surf.get_rect(center=(cx, y + 99)))
    status = f"{shield_count} IN INVENTORY - TAP TO BUY" if shield_count else (
        f"{item['cost']} coins - TAP TO BUY" if affordable else f"{item['cost']} coins"
    )
    status_color = (180, 220, 180) if shield_count else (
        settings.COLOR_COIN if affordable else (150, 150, 150)
    )
    status_surf = font_small.render(status, True, status_color)
    surface.blit(status_surf, status_surf.get_rect(center=(cx, y + h - 17)))


def draw_color_card(surface, rect, font_name, font_small, item, owned, equipped, affordable):
    x, y, w, h = rect
    _draw_card_frame(surface, rect, owned, equipped)

    preview_cx, preview_cy = x + w // 2, y + 46
    pygame.draw.circle(surface, item["color"], (preview_cx, preview_cy), 24)
    pygame.draw.circle(surface, settings.COLOR_WHITE, (preview_cx, preview_cy), 24, 2)

    name_surf = font_name.render(item["name"], True, settings.COLOR_WHITE)
    name_rect = name_surf.get_rect(center=(x + w // 2, y + 90))
    surface.blit(name_surf, name_rect)

    _draw_card_status(surface, rect, font_small, item, owned, equipped, affordable)


def draw_background_card(surface, rect, font_name, font_small, item, owned, equipped, affordable):
    x, y, w, h = rect
    _draw_card_frame(surface, rect, owned, equipped)

    preview_rect = (x + w // 2 - 45, y + 24, 90, 44)
    draw_vertical_gradient(surface, preview_rect, item["sky_top"], item["ground_bottom"])
    pygame.draw.rect(surface, settings.COLOR_WHITE, preview_rect, width=2, border_radius=4)

    name_surf = font_name.render(item["name"], True, settings.COLOR_WHITE)
    name_rect = name_surf.get_rect(center=(x + w // 2, y + 90))
    surface.blit(name_surf, name_rect)

    _draw_card_status(surface, rect, font_small, item, owned, equipped, affordable)
