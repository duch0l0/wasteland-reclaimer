"""
Кровь и ошмётки при попаданиях.

Частица летит в мировых координатах: позиция на земле (x, y) и высота z над
ней; гравитация тянет z вниз. Упав, капля становится пятном на полу
локации (level.stains) и остаётся там — как в Fallout, где после боя
видно, где он был.

  удар в ближнем бою — несколько брызг;
  выстрел — больше крови и кусочки плоти;
  крит или смертельный выстрел — ошмётки с уровня головы, осколки кости.
"""
import math
import random

import pygame

GRAVITY = 900          # px/с² — падение по высоте
MAX_STAINS = 400       # пятен на локацию; старые исчезают

BLOOD = [(150, 14, 12), (178, 22, 18), (120, 8, 8), (200, 30, 24)]
FLESH = [(170, 60, 60), (140, 40, 45), (196, 96, 90)]
BONE = [(230, 220, 200), (210, 200, 180)]


class Gore:
    def __init__(self):
        self.parts = []

    def hit(self, level, target_rect, from_pos, kind="melee", crit=False, kill=False, delay_ms=140):
        """Брызги от попадания: летят от нападавшего (from_pos) через цель."""
        cx, ground = target_rect.centerx, target_rect.bottom - 4
        away = pygame.Vector2(cx - from_pos[0], ground - from_pos[1])
        away = away.normalize() if away.length() else pygame.Vector2(1, 0)
        chest_h, head_h = 38, 60   # высоты груди и головы над землёй, px (спрайт 2× масштаба)

        def spray(n, h, speed, colors, size, spread=0.9, up=(40, 160)):
            for _ in range(n):
                ang = math.atan2(away.y, away.x) + random.uniform(-spread, spread)
                v = random.uniform(*speed)
                self.parts.append({
                    "x": cx + random.uniform(-6, 6), "y": ground + random.uniform(-3, 3), "z": h + random.uniform(-6, 6),
                    "vx": math.cos(ang) * v, "vy": math.sin(ang) * v * 0.6, "vz": random.uniform(*up),
                    "color": random.choice(colors), "size": random.choice(size), "delay": delay_ms,
                    "level": level})

        if kind == "melee":
            spray(7 if not crit else 14, chest_h, (40, 120), BLOOD, (2, 2, 3))
        else:
            spray(14, chest_h, (80, 220), BLOOD, (2, 3, 3), spread=0.6)
            spray(4, chest_h, (60, 170), FLESH, (3, 4))
            if crit or kill:  # ошмётки с головы
                spray(12, head_h, (90, 240), BLOOD, (2, 3, 4), spread=1.1, up=(80, 240))
                spray(6, head_h, (70, 200), FLESH, (3, 4, 5), spread=1.2, up=(100, 260))
                spray(3, head_h, (60, 180), BONE, (2, 3), spread=1.3, up=(120, 260))

    def update(self, dt_ms):
        dt = dt_ms / 1000
        alive = []
        for p in self.parts:
            if p["delay"] > 0:
                p["delay"] -= dt_ms
                alive.append(p)
                continue
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["vz"] -= GRAVITY * dt
            p["z"] += p["vz"] * dt
            if p["z"] <= 0:  # упала — пятно на полу
                self._stain(p)
            else:
                alive.append(p)
        self.parts = alive

    def _stain(self, p):
        level = p["level"]
        if not isinstance(getattr(level, "stains", None), list):
            level.stains = []
        grow = 2 if p["color"] in BLOOD else 1
        level.stains.append((int(p["x"]), int(p["y"]), p["size"] + grow, p["color"]))
        if len(level.stains) > MAX_STAINS:
            del level.stains[: len(level.stains) - MAX_STAINS]

    # ------------------------------------------------------------ отрисовка
    @staticmethod
    def draw_ground(surf, level, cam):
        """Пятна на полу — под персонажами."""
        cx, cy = int(cam.x), int(cam.y)
        w, h = surf.get_size()
        for x, y, size, color in getattr(level, "stains", ()):
            sx, sy = x - cx, y - cy
            if -8 < sx < w + 8 and -8 < sy < h + 8:
                c = (color[0] * 3 // 4, color[1] * 3 // 4, color[2] * 3 // 4)  # засохшее — темнее
                pygame.draw.ellipse(surf, c, (sx - size, sy - size // 2, size * 2, size))

    def draw_air(self, surf, level, cam):
        """Летящие капли и ошмётки — поверх персонажей, с тенью на земле."""
        cx, cy = int(cam.x), int(cam.y)
        for p in self.parts:
            if p["delay"] > 0 or p["level"] is not level:
                continue
            sx, sy = p["x"] - cx, p["y"] - cy
            s = p["size"]
            if s >= 4:  # тень на земле — только у крупных ошмётков
                pygame.draw.ellipse(surf, (40, 30, 26), (sx - s // 2, sy - 1, s, 3))
            pygame.draw.rect(surf, p["color"], (sx - s // 2, sy - p["z"] - s // 2, s, s))
