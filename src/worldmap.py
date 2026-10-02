"""
Карта мира (как в Fallout 2): известные локации — точки на карте,
между ними идёшь пешком, и по дороге может случиться случайная встреча.

Клавиши: 1..9 — идти к локации, 0 — бродить по пустоши (гарантированная
встреча), E/Enter — войти в локацию, у которой стоишь.
"""
import math
import random

import pygame

from . import settings as S
from .ui.common import hotspot, digit_key

TRAVEL_SPEED = 140        # px/сек по карте
ENCOUNTER_CHANCE = 0.45   # шанс встречи за переход


def to_screen(p):
    """Координаты карты мира (заданы для 960×540) -> текущий экран."""
    rw, rh = S.WORLD_MAP_REF
    return pygame.Vector2(p[0] * S.SCREEN_W / rw, p[1] * S.SCREEN_H / rh)


class WorldMap:
    def __init__(self, location_defs, known):
        self.defs = location_defs
        self.known = known                  # множество id известных локаций
        self.pos = to_screen(location_defs["ruins"]["world_pos"])
        self.target = None                  # id локации, куда идём
        self.encounter_at = None            # доля пути, на которой случится встреча
        self.chance_mult = 1.0              # Выживание героя: реже нападают (ставит игра)
        self.progress = 0.0
        self.start = pygame.Vector2(self.pos)
        self.wander = False
        self._bg = None

    # ------------------------------------------------------------ логика
    def known_list(self):
        return [lid for lid in self.defs if lid in self.known]

    def location_here(self):
        for lid in self.known_list():
            if self.pos.distance_to(to_screen(self.defs[lid]["world_pos"])) < 6:
                return lid
        return None

    def travel_to(self, loc_id):
        if self.target:
            return
        self.target = loc_id
        self.start = pygame.Vector2(self.pos)
        self.progress = 0.0
        self.wander = False
        self.encounter_at = (random.uniform(0.25, 0.8) if random.random() < ENCOUNTER_CHANCE * self.chance_mult
                             else None)

    def wander_around(self):
        """Бродить по окрестностям: короткий путь в случайную сторону и гарантированная встреча."""
        if self.target:
            return
        ang = random.uniform(0, math.tau)
        dest = self.pos + pygame.Vector2(math.cos(ang), math.sin(ang)) * 90
        dest.x = max(40, min(S.SCREEN_W - 40, dest.x))
        dest.y = max(80, min(S.SCREEN_H - 90, dest.y))
        self.target = "__wander__"
        self.wander_dest = dest
        self.start = pygame.Vector2(self.pos)
        self.progress = 0.0
        self.encounter_at = random.uniform(0.4, 0.9)

    def _dest(self):
        if self.target == "__wander__":
            return self.wander_dest
        return to_screen(self.defs[self.target]["world_pos"])

    def update(self, dt_ms):
        """Возвращает событие: None, ("arrived", loc_id) или ("encounter", None)."""
        if not self.target:
            return None
        dest = self._dest()
        total = max(1.0, self.start.distance_to(dest))
        self.progress = min(1.0, self.progress + TRAVEL_SPEED * dt_ms / 1000 / total)
        self.pos = self.start.lerp(dest, self.progress)
        if self.encounter_at is not None and self.progress >= self.encounter_at:
            self.encounter_at = None
            self.target = None  # после встречи путь выбирают заново
            return ("encounter", None)
        if self.progress >= 1.0:
            arrived = self.target
            self.target = None
            return None if arrived == "__wander__" else ("arrived", arrived)
        return None

    # ------------------------------------------------------------ отрисовка
    def _background(self):
        if self._bg is None:
            self._bg = _paint_map()
        return self._bg

    def draw(self, surf, fonts, player_hint):
        font, font_small = fonts
        surf.blit(self._background(), (0, 0))
        here = self.location_here()
        for i, lid in enumerate(self.known_list()):
            d = self.defs[lid]
            p = tuple(int(v) for v in to_screen(d["world_pos"]))
            label = font_small.render(f"[{i + 1}] {d['name']}", True, (240, 230, 200))
            lrect = label.get_rect(midtop=(p[0], p[1] + 16))
            # клик: по локации, у которой стоишь, — войти; по другой — идти к ней
            key = pygame.K_e if lid == here and not self.target else digit_key(i)
            hover = hotspot(pygame.Rect(p[0] - 14, p[1] - 14, 28, 28).union(lrect), key)
            _town_icon(surf, p, lid == here or hover)
            if hover:
                pygame.draw.circle(surf, (255, 240, 170), p, 17, 2)
                label = font_small.render(f"[{i + 1}] {d['name']}", True, (255, 240, 170))
            shadow = font_small.render(f"[{i + 1}] {d['name']}", True, (30, 22, 14))
            surf.blit(shadow, lrect.move(1, 1))
            surf.blit(label, lrect)
        if self.target:
            pygame.draw.line(surf, (230, 90, 60), self.pos, self._dest(), 1)
        pygame.draw.circle(surf, (230, 60, 50), (int(self.pos.x), int(self.pos.y)), 6)
        pygame.draw.circle(surf, (20, 10, 10), (int(self.pos.x), int(self.pos.y)), 6, 2)

        panel = pygame.Surface((S.SCREEN_W, 70), pygame.SRCALPHA)
        panel.fill((*S.COLOR_PANEL, 230))
        surf.blit(panel, (0, S.SCREEN_H - 70))
        title = font.render("Карта пустоши", True, (230, 200, 110))
        surf.blit(title, (14, S.SCREEN_H - 64))
        if self.target:
            status = "В пути..." if self.target != "__wander__" else "Бродите по пустоши..."
        elif here:
            status = f"Вы у локации «{self.defs[here]['name']}». E — войти."
        else:
            status = "Вы посреди пустоши."
        surf.blit(font_small.render(status, True, (220, 210, 190)), (220, S.SCREEN_H - 60))
        surf.blit(font_small.render("Клик/1–9 — идти к локации · 0 — бродить · клик/E — войти · " + player_hint,
                                    True, (170, 160, 140)), (14, S.SCREEN_H - 30))


# ------------------------------------------------------------ картинка карты (рисуется один раз)
def _W(x, y):
    """Точка в координатах карты 960×540 -> экран."""
    return tuple(int(v) for v in to_screen((x, y)))


def _paint_map():
    """Карта пустоши в духе Fallout 2: пергамент песочного цвета, пятна рельефа, хребты из
    штрихованных пиков, высохшие солёные озёра, река Колорадо на востоке, трасса I-15,
    сетка квадратов, роза ветров и затемнение по краям."""
    W, H = S.SCREEN_W, S.SCREEN_H
    rnd = random.Random(7)
    bg = pygame.Surface((W, H))
    bg.fill((156, 128, 86))
    # пятна рельефа: мелкий случайный шум, растянутый с размытием
    for cells, alpha, spread in ((24, 110, 26), (60, 70, 16)):
        n = pygame.Surface((cells, cells * H // W + 1))
        for y in range(n.get_height()):
            for x in range(cells):
                c = rnd.randint(-spread, spread)
                n.set_at((x, y), (156 + c, 128 + c, 86 + c // 2))
        n = pygame.transform.smoothscale(n, (W, H))
        n.set_alpha(alpha)
        bg.blit(n, (0, 0))
    # высохшие солёные озёра (Сода-Лейк у Бейкера, Силвер-Лейк к северу)
    for (x, y, w, h) in ((800, 170, 90, 40), (770, 95, 60, 26), (520, 420, 70, 30)):
        r = pygame.Rect(0, 0, *[int(v) for v in to_screen((w, h))])
        r.center = _W(x, y)
        pygame.draw.ellipse(bg, (196, 182, 150), r)
        pygame.draw.ellipse(bg, (170, 150, 112), r, 2)
        for _ in range(10):   # трещины на соли
            sx, sy = rnd.randint(r.left + 8, r.right - 8), rnd.randint(r.top + 4, r.bottom - 4)
            pygame.draw.line(bg, (176, 160, 126), (sx, sy), (sx + rnd.randint(-10, 10), sy + rnd.randint(-5, 5)))
    # горные хребты: цепочки пиков со светлым и тёмным склоном
    ranges = [[(270, 70), (360, 95), (460, 80), (540, 120)], [(60, 470), (160, 500), (280, 490)],
              [(600, 400), (690, 430), (780, 470), (860, 450)], [(470, 230), (520, 260), (560, 250)],
              [(40, 130), (90, 200), (120, 260)], [(640, 60), (700, 40), (760, 55)]]
    for chain in ranges:
        for (x0, y0), (x1, y1) in zip(chain, chain[1:]):
            steps = max(2, int(math.hypot(x1 - x0, y1 - y0) / 9))
            for i in range(steps):
                t = i / steps
                cx = x0 + (x1 - x0) * t + rnd.uniform(-6, 6)
                cy = y0 + (y1 - y0) * t + rnd.uniform(-8, 8)
                hgt = rnd.uniform(9, 18)
                base = rnd.uniform(7, 12)
                top, left, right = _W(cx, cy - hgt), _W(cx - base, cy), _W(cx + base, cy)
                mid = _W(cx + rnd.uniform(-2, 2), cy)
                pygame.draw.polygon(bg, (188, 160, 112), [top, left, mid])     # освещённый склон
                pygame.draw.polygon(bg, (112, 86, 56), [top, mid, right])      # теневой
                pygame.draw.lines(bg, (84, 62, 40), False, [left, top, right], 1)
    # река Колорадо на востоке
    pts = [_W(948 + 8 * math.sin(y / 37), y) for y in range(0, 541, 12)]
    pygame.draw.lines(bg, (150, 140, 110), False, pts, 9)      # берега
    pygame.draw.lines(bg, (70, 104, 128), False, pts, 5)
    pygame.draw.lines(bg, (120, 158, 176), False, pts, 1)
    # трасса I-15 и старая дорога
    road = [_W(*p) for p in [(0, 420), (200, 350), (420, 300), (620, 190), (960, 120)]]
    pygame.draw.lines(bg, (70, 62, 54), False, road, 6)
    pygame.draw.lines(bg, (196, 180, 120), False, road, 1)
    side = [_W(*p) for p in [(230, 330), (300, 420), (420, 470), (560, 520)]]
    for (ax, ay), (bx, by) in zip(side, side[1:]):     # грунтовка — пунктиром
        n = int(math.hypot(bx - ax, by - ay) / 10)
        for i in range(0, n, 2):
            pygame.draw.line(bg, (110, 90, 62), (ax + (bx - ax) * i / n, ay + (by - ay) * i / n),
                             (ax + (bx - ax) * (i + 1) / n, ay + (by - ay) * (i + 1) / n), 2)
    # зернистость пергамента
    for _ in range(2400):
        x, y = rnd.randrange(W), rnd.randrange(H)
        c = bg.get_at((x, y))
        k = rnd.randint(-20, 14)
        bg.set_at((x, y), (max(0, min(255, c.r + k)), max(0, min(255, c.g + k)), max(0, min(255, c.b + k))))
    # сетка квадратов, как на карте Fallout
    grid = pygame.Surface((W, H), pygame.SRCALPHA)
    step = W // 16
    for x in range(0, W, step):
        pygame.draw.line(grid, (60, 44, 28, 40), (x, 0), (x, H))
    for y in range(0, H, step):
        pygame.draw.line(grid, (60, 44, 28, 40), (0, y), (W, y))
    bg.blit(grid, (0, 0))
    _compass(bg, (W - 70, 70))
    # затемнение к краям
    v = pygame.Surface((32, 18), pygame.SRCALPHA)
    for y in range(18):
        for x in range(32):
            d = max(abs(x - 15.5) / 16, abs(y - 8.5) / 9)
            v.set_at((x, y), (20, 12, 6, int(max(0, d - 0.55) / 0.45 * 170)))
    bg.blit(pygame.transform.smoothscale(v, (W, H)), (0, 0))
    return bg


def _compass(surf, c):
    """Роза ветров: четыре луча, север — тёмный, подпись «С»."""
    x, y = c
    for dx, dy, col in ((0, -1, (70, 46, 30)), (1, 0, (170, 140, 96)), (0, 1, (170, 140, 96)), (-1, 0, (170, 140, 96))):
        tip = (x + dx * 34, y + dy * 34)
        a = (x + dy * 8, y - dx * 8)
        b = (x - dy * 8, y + dx * 8)
        pygame.draw.polygon(surf, col, [tip, a, b])
        pygame.draw.polygon(surf, (60, 40, 26), [tip, a, b], 1)
    pygame.draw.circle(surf, (60, 40, 26), c, 20, 1)
    f = pygame.font.Font(None, 22)
    surf.blit(f.render("С", True, (60, 40, 26)), (x - 5, y - 58))


def _town_icon(surf, p, lit):
    """Значок поселения: тёмный круг-подложка, домик с крышей."""
    pygame.draw.circle(surf, (40, 28, 18), p, 13)
    pygame.draw.circle(surf, (230, 190, 90) if lit else (196, 164, 104), p, 11)
    x, y = p
    pygame.draw.rect(surf, (70, 46, 28), (x - 5, y - 1, 10, 7))
    pygame.draw.polygon(surf, (70, 46, 28), [(x - 7, y - 1), (x, y - 7), (x + 7, y - 1)])
