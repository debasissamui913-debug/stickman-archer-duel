import math
import pygame
import settings
def head_position(feet_pos):
    x, y = feet_pos
    return (x, y - settings.HEAD_OFFSET)

def body_center_position(feet_pos):
    x, y = feet_pos
    return (x, y - settings.BODY_CENTER_OFFSET)


def draw_stickman(surface, feet_pos, facing=1, color=settings.COLOR_BLACK,
                   pose="idle", aim_angle=0, bow_color=(60, 40, 20),
                   skin_id=settings.DEFAULT_SKIN_ID, animation_time=0.0):
    
    x, y = feet_pos

    if pose == "fallen":
        _draw_fallen(surface, feet_pos, facing, color)
        return

    head_r = settings.HEAD_RADIUS
    hip_y = y - 30
    shoulder_y = y - 62
    head_c = (x, shoulder_y - head_r - 2)

    
    pygame.draw.line(surface, color, (x, hip_y), (x - 14 * facing, y), 4)
    pygame.draw.line(surface, color, (x, hip_y), (x + 8 * facing, y), 4)

    
    pygame.draw.line(surface, color, (x, hip_y), (x, shoulder_y), 4)

    
    pygame.draw.circle(surface, color, (int(head_c[0]), int(head_c[1])), head_r)

    
    front_hand = (x + 22 * facing, shoulder_y - 5)
    if pose == "aim":
        rad = math.radians(aim_angle)
        dir_vec = pygame.math.Vector2(math.cos(rad) * facing, -math.sin(rad))
        front_hand = (x + dir_vec.x * 26, shoulder_y - 5 + dir_vec.y * 26)

    pygame.draw.line(surface, color, (x, shoulder_y), front_hand, 4)
    _draw_bow(
        surface, front_hand, facing, bow_color, aim_angle if pose == "aim" else 0,
        skin_id, animation_time,
    )

    
    back_hand = (x - 10 * facing, shoulder_y + 16)
    pygame.draw.line(surface, color, (x, shoulder_y), back_hand, 4)


def _draw_bow(surface, hand_pos, facing, bow_color, aim_angle, skin_id, animation_time):
    
    x, y = hand_pos
    rad = math.radians(aim_angle)
    perp = pygame.math.Vector2(-math.sin(rad), -math.cos(rad)) * facing
    top = (x + perp.x * 20, y + perp.y * 20)
    bottom = (x - perp.x * 20, y - perp.y * 20)
    mid = ((top[0] + bottom[0]) / 2 + 6 * facing, (top[1] + bottom[1]) / 2)
    if skin_id == "godly":
        glow = pygame.Surface((100, 100), pygame.SRCALPHA)
        pulse = int(35 + 25 * (0.5 + 0.5 * math.sin(animation_time * 4)))
        pygame.draw.circle(glow, (70, 210, 255, pulse), (50, 50), 43)
        surface.blit(glow, (int(x) - 50, int(y) - 50))

        pygame.draw.line(surface, (60, 170, 255), top, bottom, 8)
        pygame.draw.line(surface, (255, 240, 170), top, bottom, 3)
        pygame.draw.line(surface, (255, 220, 100), top, mid, 4)
        pygame.draw.line(surface, (255, 220, 100), mid, bottom, 4)
        pygame.draw.line(surface, (190, 250, 255), top, bottom, 1)

        orbit_radius = 30
        for i in range(4):
            angle = animation_time * (1.5 if i % 2 == 0 else -1.1) + i * math.tau / 4
            px = x + math.cos(angle) * orbit_radius
            py = y + math.sin(angle) * orbit_radius
            pygame.draw.circle(surface, (90, 225, 255), (int(px), int(py)), 2 + i % 2)
            if i == 0:
                pygame.draw.line(surface, (210, 250, 255), (px - 4, py), (px + 4, py), 1)
                pygame.draw.line(surface, (210, 250, 255), (px, py - 4), (px, py + 4), 1)

        arc_rect = pygame.Rect(int(x - 25), int(y - 25), 50, 50)
        start = animation_time * 1.8
        pygame.draw.arc(surface, (110, 230, 255), arc_rect, start, start + math.pi * 0.8, 2)
        pygame.draw.line(surface, (210, 245, 255), top, bottom, 1)
    else:
        pygame.draw.line(surface, bow_color, top, bottom, 3)
        pygame.draw.line(surface, bow_color, top, mid, 3)
        pygame.draw.line(surface, bow_color, mid, bottom, 3)


def _draw_fallen(surface, feet_pos, facing, color):
   
    x, y = feet_pos
    ground_y = y
    body_y = ground_y - 12
    head_r = settings.HEAD_RADIUS

    pygame.draw.line(surface, color, (x - 20 * facing, body_y), (x + 22 * facing, body_y), 4)
    pygame.draw.circle(surface, color, (int(x + 30 * facing), int(body_y - 2)), head_r)
    pygame.draw.line(surface, color, (x - 20 * facing, body_y), (x - 30 * facing, body_y + 10), 3)
    pygame.draw.line(surface, color, (x - 5 * facing, body_y), (x - 8 * facing, body_y + 10), 3)


def draw_shield(surface, feet_pos, facing, state, zone="body", color=(160, 120, 60)):
    
    if state == "down":
        return

    if zone == "head":
        cx, cy = head_position(feet_pos)
        cx += 20 * facing
        radius = 17
    else:
        cx, cy = body_center_position(feet_pos)
        cx += 24 * facing
        radius = 22

    if state == "warning":
        pygame.draw.circle(surface, color, (int(cx), int(cy)), radius, 3)
        return

    pygame.draw.circle(surface, color, (int(cx), int(cy)), radius)
    pygame.draw.circle(surface, (60, 45, 20), (int(cx), int(cy)), radius, 3)
    pygame.draw.circle(surface, (40, 60, 120), (int(cx), int(cy)), 6)
