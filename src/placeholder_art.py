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


def make_item_icon(item_id, size=(32, 32), halo=True):
    """Иконка предмета на холсте 32×32 (масштабируется под нужный размер).
    halo — тёмное пятно под предметом, чтобы он читался на земле."""
    s = _base_surface((32, 32))
    d = pygame.draw
    if item_id == "scrap":            # ржавая труба
        d.line(s, (95, 70, 55), (6, 26), (26, 6), 7)
        d.line(s, (160, 120, 90), (6, 26), (26, 6), 3)
        d.circle(s, (70, 50, 40), (26, 6), 4)
    elif item_id == "sharp_scrap":    # заточенный лом с блестящим концом
        d.line(s, (95, 70, 55), (5, 27), (22, 10), 7)
        d.polygon(s, (215, 220, 225), [(20, 8), (29, 2), (25, 13)])
        d.line(s, (240, 240, 245), (22, 9), (28, 3), 1)
    elif item_id == "chems":          # склянка с зелёной жижей
        d.rect(s, (200, 200, 190), (13, 3, 6, 5))
        d.rect(s, (150, 190, 170), (9, 8, 14, 21), border_radius=4)
        d.rect(s, (80, 200, 90), (10, 15, 12, 13), border_radius=3)
        d.circle(s, (170, 250, 170), (14, 19), 2)
    elif item_id == "cloth":          # сложенная тряпка
        d.polygon(s, (190, 175, 140), [(4, 10), (27, 6), (28, 24), (6, 27)])
        d.line(s, (140, 125, 95), (6, 16), (27, 13), 2)
        d.line(s, (140, 125, 95), (7, 22), (27, 19), 1)
    elif item_id == "ammo":           # три патрона
        for i in range(3):
            x = 7 + i * 7
            d.rect(s, (205, 165, 70), (x, 12, 5, 16), border_radius=1)
            d.rect(s, (170, 100, 60), (x, 7, 5, 6), border_radius=2)
    elif item_id == "pistol":         # самопал
        d.rect(s, (75, 75, 80), (4, 10, 24, 7))
        d.rect(s, (45, 45, 50), (24, 9, 5, 4))
        d.rect(s, (110, 80, 50), (7, 16, 7, 12), border_radius=2)
        d.line(s, (60, 60, 60), (14, 18), (17, 21), 2)
    elif item_id == "caps":           # крышки
        for cx, cy in ((12, 20), (20, 17), (15, 11)):
            d.circle(s, (180, 160, 60), (cx, cy), 7)
            d.circle(s, (230, 210, 110), (cx, cy), 5)
            d.circle(s, (180, 160, 60), (cx, cy), 2)
    elif item_id == "lockpick":       # отмычки
        d.line(s, (190, 190, 200), (6, 26), (24, 8), 2)
        d.line(s, (190, 190, 200), (24, 8), (28, 12), 2)
        d.line(s, (150, 150, 165), (9, 27), (27, 16), 2)
        d.rect(s, (120, 70, 50), (4, 23, 7, 6), border_radius=2)
    elif item_id == "bandage":        # бинт
        d.rect(s, (225, 220, 205), (6, 10, 20, 13), border_radius=5)
        d.rect(s, (200, 60, 55), (13, 13, 6, 7))
        d.line(s, (190, 185, 170), (8, 23), (26, 27), 3)
    elif item_id == "kit":            # набор выжившего
        d.rect(s, (120, 90, 55), (4, 9, 24, 18), border_radius=3)
        d.rect(s, (80, 60, 35), (12, 5, 8, 5), 2)
        d.rect(s, (225, 220, 205), (13, 13, 6, 10))
        d.rect(s, (225, 220, 205), (11, 15, 10, 6))
    elif item_id == "tonic":          # тоник
        d.rect(s, (120, 80, 50), (13, 2, 6, 5))
        d.rect(s, (110, 60, 130), (9, 7, 14, 22), border_radius=5)
        d.rect(s, (200, 120, 230), (11, 13, 10, 13), border_radius=4)
        d.rect(s, (240, 230, 200), (11, 16, 10, 5))
    elif item_id == "jacket":         # куртка из покрышек
        d.polygon(s, (50, 50, 55), [(8, 5), (24, 5), (29, 12), (26, 14), (25, 28), (7, 28), (6, 14), (3, 12)])
        for y in (10, 16, 22):
            d.line(s, (85, 85, 90), (8, y), (24, y), 2)
        d.line(s, (150, 130, 80), (16, 6), (16, 27), 1)
    elif item_id == "sign_vest":      # бронежилет из дорожных знаков
        d.polygon(s, (60, 60, 65), [(8, 4), (24, 4), (29, 11), (26, 13), (25, 29), (7, 29), (6, 13), (3, 11)])
        d.polygon(s, (200, 40, 40), [(11, 8), (16, 5), (21, 8), (21, 14), (16, 17), (11, 14)])  # «Стоп»
        d.line(s, (240, 240, 240), (13, 11), (19, 11), 1)
        d.polygon(s, (230, 200, 40), [(16, 18), (22, 27), (10, 27)])                        # «Осторожно»
        d.line(s, (40, 40, 40), (16, 21), (16, 24), 1)
        d.line(s, (150, 150, 160), (5, 17), (27, 17), 1)                                    # изолента
    elif item_id == "hardhat":        # каска строителя
        d.ellipse(s, (225, 190, 40), (6, 9, 20, 17))
        d.rect(s, (225, 190, 40), (3, 20, 26, 5), border_radius=2)
        d.line(s, (170, 140, 20), (16, 10), (16, 20), 2)
        d.line(s, (120, 100, 20), (10, 12), (13, 17), 1)  # трещина
    elif item_id == "moto_helmet":    # мотошлем
        d.circle(s, (60, 70, 110), (16, 16), 12)
        d.rect(s, (40, 45, 60), (7, 13, 18, 7), border_radius=3)   # визор
        d.line(s, (150, 170, 200), (10, 15), (18, 15), 1)
        d.line(s, (90, 100, 130), (8, 24), (24, 24), 2)
    elif item_id == "eye":            # чей-то глаз
        d.circle(s, (120, 30, 30), (17, 18), 11)
        d.circle(s, (235, 225, 215), (16, 16), 10)
        d.circle(s, (70, 130, 200), (18, 15), 5)
        d.circle(s, (15, 15, 20), (18, 15), 2)
        d.circle(s, (255, 255, 255), (16, 13), 1)
        d.line(s, (170, 40, 40), (7, 20), (11, 18), 1)
        d.line(s, (170, 40, 40), (22, 24), (25, 21), 1)
    elif item_id == "holotape":       # голозапись
        d.rect(s, (60, 70, 60), (5, 8, 22, 17), border_radius=2)
        d.rect(s, (110, 200, 120), (8, 11, 16, 6))
        d.circle(s, (30, 35, 30), (11, 21), 2)
        d.circle(s, (30, 35, 30), (21, 21), 2)
        d.rect(s, (220, 200, 120), (8, 11, 6, 3))
    elif item_id == "medal":          # медаль
        d.polygon(s, (170, 30, 40), [(11, 3), (21, 3), (19, 13), (13, 13)])
        d.line(s, (240, 240, 240), (16, 3), (16, 13), 2)
        d.circle(s, (200, 160, 60), (16, 21), 8)
        d.circle(s, (240, 210, 110), (16, 21), 6)
        d.polygon(s, (200, 160, 60), [(16, 16), (18, 20), (22, 20), (19, 23), (20, 27), (16, 24), (12, 27), (13, 23), (10, 20), (14, 20)])
    elif item_id == "pistol10":       # 10-мм пистолет
        d.rect(s, (40, 42, 48), (4, 9, 24, 7), border_radius=1)
        d.rect(s, (70, 72, 80), (4, 9, 24, 2))
        d.rect(s, (35, 30, 28), (8, 15, 7, 13), border_radius=2)
        d.line(s, (25, 25, 25), (15, 17), (18, 21), 2)
    elif item_id == "note":           # записка
        d.polygon(s, (225, 215, 180), [(7, 4), (25, 6), (24, 28), (6, 27)])
        for y in (10, 14, 18, 22):
            d.line(s, (130, 120, 100), (10, y), (21, y + 1), 1)
    elif item_id == "stash":          # мешочек
        d.ellipse(s, (120, 90, 55), (5, 11, 22, 18))
        d.polygon(s, (120, 90, 55), [(11, 12), (21, 12), (19, 6), (13, 6)])
        d.line(s, (70, 50, 30), (11, 9), (21, 9), 2)
        d.circle(s, (230, 210, 110), (13, 20), 2)
    elif item_id == "terminal":       # терминал RobCo (для карты)
        d.rect(s, (70, 72, 70), (3, 22, 26, 8))
        d.rect(s, (200, 190, 160), (5, 3, 22, 20), border_radius=3)
        d.rect(s, (25, 45, 30), (8, 6, 16, 12))
        d.line(s, (100, 230, 120), (10, 9), (19, 9), 1)
        d.line(s, (100, 230, 120), (10, 12), (16, 12), 1)
        d.rect(s, (150, 140, 120), (7, 24, 18, 4))
    elif item_id == "letter":         # письмо
        d.rect(s, (225, 215, 180), (4, 8, 24, 17))
        d.lines(s, (160, 145, 110), False, [(4, 8), (16, 18), (28, 8)], 2)
        d.circle(s, (170, 40, 40), (16, 18), 3)
    elif item_id == "shovel":         # сапёрная лопатка
        d.line(s, (110, 80, 50), (6, 26), (20, 12), 3)
        d.polygon(s, (150, 155, 160), [(18, 8), (27, 4), (28, 13), (22, 16)])
        d.line(s, (200, 205, 210), (20, 9), (26, 6), 1)
    elif item_id == "bottle":         # бутылка
        d.rect(s, (150, 110, 60), (14, 3, 4, 8))
        d.rect(s, (110, 140, 90), (10, 10, 12, 19), border_radius=4)
        d.rect(s, (230, 220, 190), (11, 16, 10, 6))
        d.line(s, (170, 200, 150), (12, 12), (12, 27), 1)
    elif item_id == "keycard":        # ключ-карта Vault-Tec
        d.rect(s, (44, 80, 150), (5, 8, 22, 15), border_radius=2)
        d.rect(s, (230, 190, 60), (5, 12, 22, 3))
        d.rect(s, (220, 220, 220), (8, 17, 6, 3))
    elif item_id == "grenade":        # граната из банки
        d.rect(s, (90, 110, 70), (9, 10, 14, 18), border_radius=4)
        d.rect(s, (60, 70, 50), (9, 15, 14, 2))
        d.rect(s, (160, 160, 160), (13, 5, 6, 6))
        d.circle(s, (200, 200, 200), (22, 7), 3, 1)
    else:
        d.circle(s, (180, 170, 150), (16, 16), 10)
    if size != (32, 32):
        s = pygame.transform.smoothscale(s, size) if size[0] % 32 else pygame.transform.scale(s, size)
    if not halo:
        return s
    w, h = size
    out = _base_surface(size)
    pygame.draw.circle(out, (0, 0, 0, 70), (w // 2, h // 2 + 3), w // 2 - 1)
    out.blit(s, (0, 0))
    return out


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
