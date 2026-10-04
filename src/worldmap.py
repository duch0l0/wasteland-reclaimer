"""
Карта мира (как в Fallout 2): большая карта региона, по которой ходишь между локациями.

Мир — прямоугольник MAP_W×MAP_H «единиц карты» (координаты world_pos в data/locations.json);
экран показывает его кусок, камера следует за героем. Запад — Тихий океан и остров Санта-Каталина,
дальше Южная Калифорния, Мохаве, на востоке — река Колорадо и Невада; горы, солёные озёра,
трассы I-15, I-40, I-5, граница штатов.

  - клик по локации — идти к ней (у которой стоишь — войти), клик по пустому месту — идти туда;
    1..9 — к известной локации по списку, 0 — бродить рядом, E — войти;
  - туман войны: неизведанное затемнено и открывается вокруг пройденного пути;
  - локации с "discover": true открываются сами, если пройти рядом (придорожные места);
  - шанс случайной встречи растёт с длиной пути; что встретится — зависит от региона (region_at).
"""
import math
import random

import pygame

from . import settings as S
from .ui.common import hotspot, mouse_pos

MAP_W, MAP_H = 3200, 2000
TRAVEL_SPEED = 260          # единиц карты в секунду
ENCOUNTER_PER_UNIT = 1 / 900  # ожидаемых встреч на единицу пути (до множителя Выживания)
DISCOVER_R = 130             # с какого расстояния замечаешь придорожное место
FOG_STEP = 16                # туман — сетка такой крупности
REVEAL_R = 150               # радиус обзора на карте

# ------------------------------------------------------------ география (координаты карты)
COAST = [(330, 0), (360, 200), (300, 420), (380, 640), (330, 860), (420, 1080), (380, 1260), (470, 1440),
         (430, 1640), (520, 1820), (500, 2000)]
ISLAND = [(120, 1380), (230, 1350), (300, 1420), (250, 1500), (140, 1490)]
RIVER = [(2560 + 30 * math.sin(y / 140), y) for y in range(0, 2001, 40)]
STATE_LINE = [(1700, 0), (2080, 480), (2420, 900), (2560, 1080)]       # Калифорния / Невада
ROADS = {
    "I-15": [(560, 1330), (1000, 1250), (1450, 1150), (1600, 1100), (1900, 980), (2200, 840), (2550, 560),
             (2900, 200)],
    "I-40": [(1450, 1150), (1800, 1260), (2200, 1380), (2500, 1500), (3200, 1560)],
    "I-5": [(560, 1330), (650, 900), (720, 600), (760, 0)],
    "95": [(2500, 1500), (2650, 1150), (2560, 560)],
}
MOUNTAINS = [[(560, 980), (700, 900), (860, 820), (980, 760)], [(1150, 300), (1300, 420), (1380, 560)],
             [(1180, 1500), (1320, 1580), (1500, 1620)], [(2050, 1180), (2150, 1260), (2250, 1240)],
             [(2300, 300), (2380, 420), (2460, 380)], [(2700, 820), (2800, 920), (2900, 880)],
             [(1700, 620), (1820, 700), (1900, 660)], [(900, 1700), (1050, 1760), (1200, 1800)],
             [(2850, 1700), (2950, 1800), (3080, 1760)]]
SALT_LAKES = [(1960, 1060, 120, 50), (1880, 820, 80, 34), (1300, 1000, 90, 40), (2900, 1300, 110, 44)]
REGIONS = [("ТИХИЙ ОКЕАН", (150, 700)), ("ЮЖНАЯ КАЛИФОРНИЯ", (820, 1150)), ("МОХАВЕ", (1650, 1350)),
           ("НЕВАДА", (2750, 600)), ("Санта-Каталина", (210, 1550))]


def _river_x(y):
    return 2560 + 30 * math.sin(y / 140)


def _coast_x(y):
    for (x0, y0), (x1, y1) in zip(COAST, COAST[1:]):
        if y0 <= y <= y1:
            return x0 + (x1 - x0) * (y - y0) / max(1, y1 - y0)
    return COAST[-1][0]


def _state_side(x, y):
    """>0 — к востоку от границы штатов (Невада)."""
    for (x0, y0), (x1, y1) in zip(STATE_LINE, STATE_LINE[1:]):
        if y0 <= y <= y1:
            return x - (x0 + (x1 - x0) * (y - y0) / max(1, y1 - y0))
    return x - (STATE_LINE[-1][0] if y > STATE_LINE[-1][1] else STATE_LINE[0][0])


def region_at(p):
    """ocean / island / socal / mojave / river / nevada — для случайных встреч."""
    x, y = p
    if pygame.Rect(100, 1330, 220, 190).collidepoint(x, y):
        return "island"
    if x < _coast_x(y):
        return "ocean"
    if abs(x - _river_x(y)) < 70:
        return "river"
    if _state_side(x, y) > 0 or x > _river_x(y):
        return "nevada"
    if x < 1300:
        return "socal"
    return "mojave"


def to_screen(p):
    """Старое имя: координаты карты мира — как есть (камера переводит в экран)."""
    return pygame.Vector2(p)


class WorldMap:
    def __init__(self, location_defs, known):
        self.defs = location_defs
        self.known = known                  # множество id известных локаций
        self.pos = pygame.Vector2(location_defs["ruins"]["world_pos"])
        self.target = None                  # id локации, куда идём ("__point__" — в точку)
        self.dest = None                    # куда идём (точка карты)
        self.encounter_at = None            # доля пути, на которой случится встреча
        self.chance_mult = 1.0              # Выживание героя: реже нападают (ставит игра)
        self.progress = 0.0
        self.start = pygame.Vector2(self.pos)
        self._bg = None
        self.fog = None                     # туман войны: маска по сетке FOG_STEP (1 — разведано)
        self.discovered = []                # что открылось само (игра пишет в лог)
        self.cam = pygame.Vector2()

    # ------------------------------------------------------------ туман
    def _fog_grid(self):
        if self.fog is None:
            self.fog = bytearray((MAP_W // FOG_STEP) * (MAP_H // FOG_STEP))
            self.reveal(self.pos)
            for lid in self.known:
                if self.defs.get(lid, {}).get("world_pos"):
                    self.reveal(self.defs[lid]["world_pos"], 90)
        return self.fog

    def reveal(self, p, r=REVEAL_R):
        fog = self.fog if self.fog is not None else self._fog_grid()
        gw, gh = MAP_W // FOG_STEP, MAP_H // FOG_STEP
        cx, cy, rr = int(p[0]) // FOG_STEP, int(p[1]) // FOG_STEP, r // FOG_STEP
        for gy in range(max(0, cy - rr), min(gh, cy + rr + 1)):
            for gx in range(max(0, cx - rr), min(gw, cx + rr + 1)):
                if (gx - cx) ** 2 + (gy - cy) ** 2 <= rr * rr:
                    fog[gy * gw + gx] = 1
        self._fog_surf = None

    def fog_bytes(self):
        return bytes(self._fog_grid())

    def set_fog(self, data):
        self.fog = bytearray(data) if data else None
        self._fog_surf = None

    # ------------------------------------------------------------ логика
    def known_list(self):
        return [lid for lid in self.defs if lid in self.known and self.defs[lid].get("world_pos")]

    def location_here(self):
        for lid in self.known_list():
            if self.pos.distance_to(self.defs[lid]["world_pos"]) < 14:
                return lid
        return None

    def _go(self, dest, target):
        if self.target:
            return
        self.target, self.dest = target, pygame.Vector2(dest)
        self.start = pygame.Vector2(self.pos)
        self.progress = 0.0
        dist = self.start.distance_to(self.dest)
        p = min(0.85, dist * ENCOUNTER_PER_UNIT * self.chance_mult)
        self.encounter_at = random.uniform(0.2, 0.85) if random.random() < p else None

    def travel_to(self, loc_id):
        self._go(self.defs[loc_id]["world_pos"], loc_id)

    def travel_to_point(self, p):
        x = max(20, min(MAP_W - 20, p[0]))
        y = max(20, min(MAP_H - 20, p[1]))
        if region_at((x, y)) == "ocean":   # в океан пешком не уйти: до берега
            x = _coast_x(y) + 20
        self._go((x, y), "__point__")

    def wander_around(self):
        """Бродить по окрестностям: короткий путь в случайную сторону и гарантированная встреча."""
        if self.target:
            return
        ang = random.uniform(0, math.tau)
        self.travel_to_point(self.pos + pygame.Vector2(math.cos(ang), math.sin(ang)) * 160)
        self.encounter_at = random.uniform(0.4, 0.9)

    def update(self, dt_ms):
        """Возвращает событие: None, ("arrived", loc_id), ("encounter", None)."""
        if not self.target:
            return None
        total = max(1.0, self.start.distance_to(self.dest))
        self.progress = min(1.0, self.progress + TRAVEL_SPEED * dt_ms / 1000 / total)
        self.pos = self.start.lerp(self.dest, self.progress)
        self.reveal(self.pos)
        for lid, d in self.defs.items():   # придорожные места открываются сами
            if d.get("discover") and lid not in self.known and d.get("world_pos") \
                    and self.pos.distance_to(d["world_pos"]) < DISCOVER_R:
                self.known.add(lid)
                self.discovered.append(lid)
        if self.encounter_at is not None and self.progress >= self.encounter_at:
            self.encounter_at = None
            self.target = None  # после встречи путь выбирают заново
            return ("encounter", None)
        if self.progress >= 1.0:
            arrived = self.target
            self.target = None
            return None if arrived == "__point__" else ("arrived", arrived)
        return None

    # ------------------------------------------------------------ отрисовка
    def _background(self):
        if self._bg is None:
            self._bg = _paint_map()
        return self._bg

    def _fog_surface(self):
        if getattr(self, "_fog_surf", None) is None:
            gw, gh = MAP_W // FOG_STEP, MAP_H // FOG_STEP
            s = pygame.Surface((gw, gh), pygame.SRCALPHA)
            s.fill((24, 16, 8, 205))
            fog = self._fog_grid()
            for i, v in enumerate(fog):
                if v:
                    s.set_at((i % gw, i // gw), (0, 0, 0, 0))
            self._fog_surf = pygame.transform.smoothscale(s, (MAP_W, MAP_H))
        return self._fog_surf

    def screen_to_map(self, pos):
        return (pos[0] + self.cam.x, pos[1] + self.cam.y)

    def click(self, pos):
        """Клик по пустому месту карты — идти туда."""
        if pos[1] < S.SCREEN_H - 70:
            self.travel_to_point(self.screen_to_map(pos))

    def draw(self, surf, fonts, player_hint):
        font, font_small = fonts
        view_h = S.SCREEN_H - 70
        self.cam.x = max(0, min(MAP_W - S.SCREEN_W, self.pos.x - S.SCREEN_W / 2))
        self.cam.y = max(0, min(MAP_H - view_h, self.pos.y - view_h / 2))
        cx, cy = int(self.cam.x), int(self.cam.y)
        area = pygame.Rect(cx, cy, S.SCREEN_W, view_h)
        surf.blit(self._background(), (0, 0), area)
        surf.blit(self._fog_surface(), (0, 0), area)
        hotspot(pygame.Rect(0, 0, S.SCREEN_W, view_h), lambda: self.click(mouse_pos()))
        here = self.location_here()
        for i, lid in enumerate(self.known_list()):
            d = self.defs[lid]
            p = (int(d["world_pos"][0] - cx), int(d["world_pos"][1] - cy))
            if not area.move(-cx, -cy).inflate(60, 60).collidepoint(p):
                continue
            num = f"[{i + 1}] " if i < 9 else ""
            title = d.get("world_name", d["name"])   # на карте — имя города, а не района
            label = font_small.render(f"{num}{title}", True, (240, 230, 200))
            lrect = label.get_rect(midtop=(p[0], p[1] + 16))
            if lid == here and not self.target:
                key = pygame.K_e
            else:
                key = (lambda lid=lid: self.travel_to(lid))
            hover = hotspot(pygame.Rect(p[0] - 16, p[1] - 16, 32, 32).union(lrect), key)
            _town_icon(surf, p, lid == here or hover, small=d.get("discover", False))
            if hover:
                pygame.draw.circle(surf, (255, 240, 170), p, 17, 2)
                label = font_small.render(f"{num}{title}", True, (255, 240, 170))
            shadow = font_small.render(f"{num}{title}", True, (30, 22, 14))
            surf.blit(shadow, lrect.move(1, 1))
            surf.blit(label, lrect)
        me = (int(self.pos.x - cx), int(self.pos.y - cy))
        if self.target:
            pygame.draw.line(surf, (230, 90, 60), me, (int(self.dest.x - cx), int(self.dest.y - cy)), 1)
        pygame.draw.circle(surf, (230, 60, 50), me, 6)
        pygame.draw.circle(surf, (20, 10, 10), me, 6, 2)

        panel = pygame.Surface((S.SCREEN_W, 70), pygame.SRCALPHA)
        panel.fill((*S.COLOR_PANEL, 230))
        surf.blit(panel, (0, S.SCREEN_H - 70))
        title = font.render("Карта пустоши", True, (230, 200, 110))
        surf.blit(title, (14, S.SCREEN_H - 64))
        names = {"ocean": "побережье", "island": "остров", "socal": "Южная Калифорния", "mojave": "Мохаве",
                 "river": "река Колорадо", "nevada": "Невада"}
        if self.target:
            status = "В пути..."
        elif here:
            status = f"Вы у локации «{self.defs[here].get('world_name', self.defs[here]['name'])}». E — войти."
        else:
            status = f"Вы посреди пустоши: {names[region_at(self.pos)]}."
        surf.blit(font_small.render(status, True, (220, 210, 190)), (220, S.SCREEN_H - 60))
        surf.blit(font_small.render("Клик — идти (по локации — к ней) · 1–9 — к локации · 0 — бродить · E — войти · "
                                    + player_hint, True, (170, 160, 140)), (14, S.SCREEN_H - 30))


# ------------------------------------------------------------ картинка карты (рисуется один раз)
def _paint_map():
    """Пергамент песочного цвета, рельеф, океан с береговой линией, остров, река Колорадо, горы,
    солёные озёра, трассы, граница штатов, сетка квадратов, подписи регионов, роза ветров."""
    W, H = MAP_W, MAP_H
    rnd = random.Random(7)
    bg = pygame.Surface((W, H))
    bg.fill((156, 128, 86))
    for cells, alpha, spread in ((40, 110, 26), (110, 70, 16)):   # пятна рельефа
        n = pygame.Surface((cells, cells * H // W + 1))
        for y in range(n.get_height()):
            for x in range(cells):
                c = rnd.randint(-spread, spread)
                n.set_at((x, y), (156 + c, 128 + c, 86 + c // 2))
        n = pygame.transform.smoothscale(n, (W, H))
        n.set_alpha(alpha)
        bg.blit(n, (0, 0))
    # Невада — чуть краснее, Южная Калифорния у побережья — чуть зеленее
    tint = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(tint, (150, 60, 30, 26), STATE_LINE + [(W, 1080), (W, 0)])
    pygame.draw.polygon(tint, (60, 90, 40, 26), [(0, 0), (1000, 0), (1100, 2000), (0, 2000)])
    bg.blit(tint, (0, 0))
    # океан
    sea = [(0, 0)] + COAST + [(0, H)]
    pygame.draw.polygon(bg, (58, 92, 120), sea)
    for k in range(1, 6):   # прибой — светлые полосы вдоль берега
        pts = [(x - k * 14, y) for x, y in COAST]
        pygame.draw.lines(bg, (74 + k * 4, 110 + k * 4, 140 + k * 3), False, pts, 2)
    pygame.draw.lines(bg, (200, 186, 140), False, COAST, 5)
    pygame.draw.polygon(bg, (176, 156, 108), ISLAND)
    pygame.draw.polygon(bg, (110, 140, 80), [(160, 1400), (230, 1385), (270, 1430), (230, 1480), (160, 1470)])
    pygame.draw.polygon(bg, (200, 186, 140), ISLAND, 3)
    # горы
    for chain in MOUNTAINS:
        for (x0, y0), (x1, y1) in zip(chain, chain[1:]):
            steps = max(2, int(math.hypot(x1 - x0, y1 - y0) / 14))
            for i in range(steps):
                t = i / steps
                cx = x0 + (x1 - x0) * t + rnd.uniform(-10, 10)
                cy = y0 + (y1 - y0) * t + rnd.uniform(-12, 12)
                hgt, base = rnd.uniform(16, 30), rnd.uniform(12, 20)
                top, left, right, mid = (cx, cy - hgt), (cx - base, cy), (cx + base, cy), (cx + rnd.uniform(-3, 3), cy)
                pygame.draw.polygon(bg, (188, 160, 112), [top, left, mid])
                pygame.draw.polygon(bg, (112, 86, 56), [top, mid, right])
                pygame.draw.lines(bg, (84, 62, 40), False, [left, top, right], 1)
    # солёные озёра
    for x, y, w, h in SALT_LAKES:
        r = pygame.Rect(0, 0, w, h)
        r.center = (x, y)
        pygame.draw.ellipse(bg, (204, 192, 160), r)
        pygame.draw.ellipse(bg, (170, 150, 112), r, 2)
    # река Колорадо
    pygame.draw.lines(bg, (150, 140, 110), False, RIVER, 16)
    pygame.draw.lines(bg, (64, 104, 132), False, RIVER, 9)
    pygame.draw.lines(bg, (120, 160, 180), False, RIVER, 2)
    # граница штатов — пунктир
    for (ax, ay), (bx, by) in zip(STATE_LINE, STATE_LINE[1:]):
        n = int(math.hypot(bx - ax, by - ay) / 14)
        for i in range(0, n, 2):
            pygame.draw.line(bg, (110, 60, 50), (ax + (bx - ax) * i / n, ay + (by - ay) * i / n),
                             (ax + (bx - ax) * (i + 1) / n, ay + (by - ay) * (i + 1) / n), 2)
    # трассы
    f = pygame.font.Font(None, 26)
    for name, pts in ROADS.items():
        pygame.draw.lines(bg, (70, 62, 54), False, pts, 7)
        pygame.draw.lines(bg, (196, 180, 120), False, pts, 1)
        mx, my = pts[len(pts) // 2]
        shield = f.render(name, True, (240, 236, 220))
        r = shield.get_rect(center=(mx, my - 18)).inflate(10, 6)
        pygame.draw.rect(bg, (40, 70, 140), r, border_radius=5)
        pygame.draw.rect(bg, (220, 220, 220), r, 1, border_radius=5)
        bg.blit(shield, shield.get_rect(center=r.center))
    # зерно
    for _ in range(12000):
        x, y = rnd.randrange(W), rnd.randrange(H)
        c = bg.get_at((x, y))
        k = rnd.randint(-18, 12)
        bg.set_at((x, y), (max(0, min(255, c.r + k)), max(0, min(255, c.g + k)), max(0, min(255, c.b + k))))
    # сетка квадратов
    grid = pygame.Surface((W, H), pygame.SRCALPHA)
    for x in range(0, W, 100):
        pygame.draw.line(grid, (60, 44, 28, 36), (x, 0), (x, H))
    for y in range(0, H, 100):
        pygame.draw.line(grid, (60, 44, 28, 36), (0, y), (W, y))
    bg.blit(grid, (0, 0))
    big = pygame.font.Font(None, 64)
    for text, (x, y) in REGIONS:
        t = big.render(text, True, (90, 66, 42))
        t.set_alpha(110)
        bg.blit(t, t.get_rect(center=(x, y)))
    _compass(bg, (W - 90, 90))
    return bg


def _compass(surf, c):
    x, y = c
    for dx, dy, col in ((0, -1, (70, 46, 30)), (1, 0, (170, 140, 96)), (0, 1, (170, 140, 96)), (-1, 0, (170, 140, 96))):
        tip = (x + dx * 44, y + dy * 44)
        a = (x + dy * 10, y - dx * 10)
        b = (x - dy * 10, y + dx * 10)
        pygame.draw.polygon(surf, col, [tip, a, b])
        pygame.draw.polygon(surf, (60, 40, 26), [tip, a, b], 1)
    pygame.draw.circle(surf, (60, 40, 26), c, 26, 1)
    f = pygame.font.Font(None, 28)
    surf.blit(f.render("С", True, (60, 40, 26)), (x - 6, y - 72))


def _town_icon(surf, p, lit, small=False):
    """Значок: поселение — домик в круге; придорожное место — маленький ромб."""
    x, y = p
    if small:
        pts = [(x, y - 9), (x + 9, y), (x, y + 9), (x - 9, y)]
        pygame.draw.polygon(surf, (40, 28, 18), [(px * 1, py) for px, py in pts])
        pygame.draw.polygon(surf, (230, 190, 90) if lit else (176, 146, 96),
                            [(x, y - 6), (x + 6, y), (x, y + 6), (x - 6, y)])
        return
    pygame.draw.circle(surf, (40, 28, 18), p, 13)
    pygame.draw.circle(surf, (230, 190, 90) if lit else (196, 164, 104), p, 11)
    pygame.draw.rect(surf, (70, 46, 28), (x - 5, y - 1, 10, 7))
    pygame.draw.polygon(surf, (70, 46, 28), [(x - 7, y - 1), (x, y - 7), (x + 7, y - 1)])
