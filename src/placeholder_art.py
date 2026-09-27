"""
Процедурная заглушка-графика.

Пока реальные спрайты не подложены в assets/, все существа и тайлы
рисуются простыми геометрическими фигурами в духе "грубого пиксель-арта".
Это ОРИГИНАЛЬНАЯ генерация примитивами, не имитация чьих-либо персонажей —
просто чтобы игра запускалась и была играбельна с первого дня.

Как только в assets/ появятся настоящие файлы (см. README), loader.py
подхватит их автоматически и эти функции больше не понадобятся.
"""
import math
import pygame


def _base_surface(size):
    surf = pygame.Surface(size, pygame.SRCALPHA)
    return surf


def make_humanoid_frame(size, base_color, accent_color, phase, action="idle"):
    """Рисует силуэт гуманоида с простой анимацией по фазе 0..1."""
    w, h = size
    surf = _base_surface(size)
    cx = w // 2

    # лёгкое приседание/раскачивание в идле
    bob = int(math.sin(phase * math.tau) * 2)
    leg_swing = math.sin(phase * math.tau) * (6 if action == "walk" else 0)
    arm_swing = math.sin(phase * math.tau) * (8 if action == "walk" else 0)

    head_r = w // 6
    torso_top = h // 4 + bob
    torso_bot = h * 3 // 4 + bob

    # ноги
    pygame.draw.line(surf, accent_color, (cx - 5, torso_bot), (cx - 5 - leg_swing, h - 4), 6)
    pygame.draw.line(surf, accent_color, (cx + 5, torso_bot), (cx + 5 + leg_swing, h - 4), 6)
    # торс
    pygame.draw.rect(surf, base_color, (cx - w // 6, torso_top, w // 3, torso_bot - torso_top), border_radius=4)
    # руки
    arm_y = torso_top + 6
    if action == "attack":
        pygame.draw.line(surf, accent_color, (cx + 6, arm_y), (cx + 22, arm_y - 10), 6)
        pygame.draw.line(surf, accent_color, (cx - 6, arm_y), (cx - 16, arm_y + 4), 5)
    else:
        pygame.draw.line(surf, accent_color, (cx - 6, arm_y), (cx - 10 - arm_swing, arm_y + 14), 5)
        pygame.draw.line(surf, accent_color, (cx + 6, arm_y), (cx + 10 + arm_swing, arm_y + 14), 5)
    # голова
    pygame.draw.circle(surf, accent_color, (cx, torso_top - head_r + 2), head_r)
    # глаза (пара пикселей, чтобы читалось направление)
    pygame.draw.circle(surf, (10, 10, 10), (cx - 3, torso_top - head_r), 2)
    pygame.draw.circle(surf, (10, 10, 10), (cx + 3, torso_top - head_r), 2)
    return surf


def make_mutant_frame(size, base_color, accent_color, phase):
    """Кривая клешнявая тварь — плейсхолдер под врага-мутанта."""
    w, h = size
    surf = _base_surface(size)
    cx, cy = w // 2, h // 2
    bob = int(math.sin(phase * math.tau) * 3)
    r = w // 3
    pygame.draw.ellipse(surf, base_color, (cx - r, cy - r + bob, r * 2, int(r * 1.6)))
    pygame.draw.circle(surf, accent_color, (cx - r // 2, cy - r // 2 + bob), 4)
    pygame.draw.circle(surf, accent_color, (cx + r // 2, cy - r // 2 + bob), 4)
    leg_off = int(math.sin(phase * math.tau * 2) * 4)
    pygame.draw.line(surf, accent_color, (cx - r // 2, cy + r // 2), (cx - r - leg_off, h - 2), 4)
    pygame.draw.line(surf, accent_color, (cx + r // 2, cy + r // 2), (cx + r + leg_off, h - 2), 4)
    return surf


def make_beetle_frame(size, base_color, accent_color, phase):
    """Приземистый жук в сегментированном панцире."""
    w, h = size
    surf = _base_surface(size)
    cx = w // 2
    bob = int(math.sin(phase * math.tau) * 2)
    leg = int(math.sin(phase * math.tau * 2) * 3)
    for i, lx in enumerate((cx - w // 3, cx, cx + w // 3)):
        off = leg if i % 2 else -leg
        pygame.draw.line(surf, accent_color, (lx, h // 2 + bob), (lx - 8 + off, h - 2), 3)
        pygame.draw.line(surf, accent_color, (lx, h // 2 + bob), (lx + 8 - off, h - 2), 3)
    shell = pygame.Rect(4, h // 4 + bob, w - 8, h // 2)
    pygame.draw.ellipse(surf, base_color, shell)
    dark = tuple(max(0, c - 25) for c in base_color)
    for i in range(1, 4):
        x = shell.x + shell.w * i // 4
        pygame.draw.line(surf, dark, (x, shell.y + 3), (x, shell.bottom - 3), 2)
    pygame.draw.ellipse(surf, dark, shell, 2)
    pygame.draw.circle(surf, accent_color, (shell.right - 6, shell.y + 8), 3)
    return surf


def make_item_icon(item_id, size):
    """Иконка предмета, лежащего на земле."""
    w, h = size
    s = _base_surface(size)
    if item_id == "scrap":
        pygame.draw.line(s, (150, 140, 130), (6, h - 8), (w - 6, 8), 6)
        pygame.draw.line(s, (90, 80, 70), (w - 12, 6), (w - 4, 12), 4)
    elif item_id == "chems":
        pygame.draw.rect(s, (80, 170, 90), (w // 2 - 7, 10, 14, h - 14), border_radius=4)
        pygame.draw.rect(s, (200, 200, 190), (w // 2 - 4, 4, 8, 7))
    elif item_id == "cloth":
        pygame.draw.polygon(s, (200, 185, 150), [(5, 10), (w - 6, 6), (w - 4, h - 8), (7, h - 5)])
        pygame.draw.line(s, (150, 135, 105), (8, h // 2), (w - 6, h // 2 - 2), 2)
    elif item_id == "ammo":
        for i in range(3):
            x = 7 + i * 8
            pygame.draw.rect(s, (200, 160, 70), (x, 12, 6, h - 18), border_radius=2)
            pygame.draw.rect(s, (160, 90, 60), (x, 8, 6, 6), border_radius=3)
    elif item_id == "pistol":
        pygame.draw.rect(s, (70, 70, 75), (5, 10, w - 10, 8))
        pygame.draw.rect(s, (90, 70, 50), (8, 16, 8, 12))
        pygame.draw.rect(s, (40, 40, 45), (w - 9, 9, 5, 4))
    else:
        pygame.draw.circle(s, (180, 170, 150), (w // 2, h // 2), w // 3)
    # тёмный ореол — чтобы предмет читался на любом фоне
    halo = _base_surface(size)
    pygame.draw.circle(halo, (0, 0, 0, 70), (w // 2, h // 2 + 3), w // 2 - 1)
    halo.blit(s, (0, 0))
    return halo


def make_special_tile(name, size):
    w, h = size
    s = _base_surface(size)
    if name == "container":
        pygame.draw.rect(s, (110, 80, 50), (6, 12, w - 12, h - 18), border_radius=3)
        pygame.draw.rect(s, (70, 50, 30), (6, 12, w - 12, h - 18), 2, border_radius=3)
        pygame.draw.line(s, (70, 50, 30), (6, 22), (w - 7, 22), 2)
        pygame.draw.rect(s, (200, 180, 90), (w // 2 - 3, 18, 6, 7))
    elif name == "door":
        pygame.draw.rect(s, (90, 90, 100), (4, 2, w - 8, h - 4))
        for yy in range(8, h - 4, 10):
            pygame.draw.line(s, (60, 60, 70), (6, yy), (w - 7, yy), 2)
        pygame.draw.circle(s, (200, 170, 60), (w - 14, h // 2), 4)
    elif name == "exit":
        for i in range(3):
            x = 8 + i * 12
            pygame.draw.polygon(s, (230, 200, 90, 160), [(x, 14), (x + 10, h // 2), (x, h - 14)])
    return s


def make_tile_surface(size, base_color, kind="ground"):
    surf = pygame.Surface(size)
    surf.fill(base_color)
    # немного "шума"/трещин для текстуры без реальных текстур
    dark = tuple(max(0, c - 22) for c in base_color)
    light = tuple(min(255, c + 18) for c in base_color)
    w, h = size
    pygame.draw.line(surf, dark, (0, h - 1), (w, h - 1), 1)
    if kind == "wall":
        pygame.draw.rect(surf, dark, (0, 0, w, h), 3)
        for i in range(0, w, 12):
            pygame.draw.line(surf, dark, (i, 0), (i, h), 1)
    elif kind == "scrap":
        pygame.draw.circle(surf, light, (w // 3, h // 2), 6)
        pygame.draw.circle(surf, dark, (w * 2 // 3, h * 2 // 3), 5)
    return surf


def make_parallax_layer(size, top_color, bottom_color, seed, fill_sky=True, baseline_ratio=0.72):
    """Слой параллакса: у дальнего слоя — градиентное небо, у остальных
    только силуэты (дюны/руины) на прозрачном фоне, чтобы сквозь них
    были видны более дальние слои."""
    import random
    w, h = size
    surf = pygame.Surface(size, pygame.SRCALPHA)
    if fill_sky:
        for y in range(h):
            t = y / max(1, h - 1)
            color = tuple(int(top_color[i] + (bottom_color[i] - top_color[i]) * t) for i in range(3))
            pygame.draw.line(surf, color, (0, y), (w, y))
    rnd = random.Random(seed)
    silhouette = tuple(max(0, c - 14) for c in bottom_color)
    x = 0
    baseline = int(h * baseline_ratio)
    while x < w:
        bump_w = rnd.randint(60, 160)
        bump_h = rnd.randint(20, 90)
        pygame.draw.ellipse(surf, silhouette, (x, baseline - bump_h // 2, bump_w, bump_h))
        x += bump_w - rnd.randint(10, 30)
    # под линией силуэтов слой залит сплошным цветом, чтобы не было «дыр» снизу
    pygame.draw.rect(surf, silhouette, (0, baseline, w, h - baseline))
    return surf
