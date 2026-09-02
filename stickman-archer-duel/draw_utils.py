import pygame
def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def draw_vertical_gradient(surface, rect, top_color, bottom_color):
    x, y, w, h = rect
    if h <= 0:
        return
    gradient = pygame.Surface((1, h))
    for row in range(h):
        t = row / max(1, h - 1)
        gradient.set_at((0, row), lerp_color(top_color, bottom_color, t))
    scaled = pygame.transform.scale(gradient, (w, h))
    surface.blit(scaled, (x, y))


def draw_rounded_panel(surface, rect, color, radius=14, border_color=None,
                        border_width=0, shadow=True, shadow_offset=(0, 5), alpha=255):
    x, y, w, h = rect
    if shadow:
        shadow_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 90), (0, 0, w, h), border_radius=radius)
        surface.blit(shadow_surf, (x + shadow_offset[0], y + shadow_offset[1]))

    panel_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    fill_color = (*color[:3], alpha) if len(color) == 3 else color
    pygame.draw.rect(panel_surf, fill_color, (0, 0, w, h), border_radius=radius)
    if border_color and border_width > 0:
        pygame.draw.rect(panel_surf, border_color, (0, 0, w, h), width=border_width, border_radius=radius)
    surface.blit(panel_surf, (x, y))


def draw_glow_circle(surface, center, radius, color, layers=4):
    glow_surf = pygame.Surface((radius * 2 * layers, radius * 2 * layers), pygame.SRCALPHA)
    gc = glow_surf.get_width() // 2
    for i in range(layers, 0, -1):
        alpha = int(60 / i)
        r = radius + (layers - i) * radius // 2
        pygame.draw.circle(glow_surf, (*color, alpha), (gc, gc), r)
    surface.blit(glow_surf, (center[0] - gc, center[1] - gc))


def draw_text_with_shadow(surface, font, text, color, pos, center=False, shadow_color=(0, 0, 0), offset=(2, 2)):
    shadow_surf = font.render(text, True, shadow_color)
    main_surf = font.render(text, True, color)
    if center:
        shadow_rect = shadow_surf.get_rect(center=(pos[0] + offset[0], pos[1] + offset[1]))
        main_rect = main_surf.get_rect(center=pos)
    else:
        shadow_rect = shadow_surf.get_rect(topleft=(pos[0] + offset[0], pos[1] + offset[1]))
        main_rect = main_surf.get_rect(topleft=pos)
    surface.blit(shadow_surf, shadow_rect)
    surface.blit(main_surf, main_rect)
    return main_rect


def draw_outlined_text(surface, font, text, color, pos, outline_color=(25, 30, 25), outline_width=2, center=True):
    scale = 2
    main_surf = font.render(text, True, color)
    outline_mask = font.render(text, True, outline_color)

    pad = outline_width * scale + 4
    w, h = main_surf.get_width(), main_surf.get_height()
    big_w, big_h = (w + pad * 2) * scale, (h + pad * 2) * scale

    canvas = pygame.Surface((big_w, big_h), pygame.SRCALPHA)

    big_outline = pygame.transform.scale(outline_mask, (outline_mask.get_width() * scale, outline_mask.get_height() * scale))
    ow = outline_width * scale
    for dx in (-ow, 0, ow):
        for dy in (-ow, 0, ow):
            if dx == 0 and dy == 0:
                continue
            canvas.blit(big_outline, (pad * scale + dx, pad * scale + dy))

    big_main = pygame.transform.scale(main_surf, (w * scale, h * scale))
    canvas.blit(big_main, (pad * scale, pad * scale))

    final = pygame.transform.smoothscale(canvas, (big_w // scale, big_h // scale))

    if center:
        rect = final.get_rect(center=pos)
    else:
        rect = final.get_rect(topleft=pos)
    surface.blit(final, rect)
    return rect
