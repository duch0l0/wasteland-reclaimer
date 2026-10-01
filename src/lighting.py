"""
Ночное освещение карт: синеватая темнота, тёплые круги света от фонарей и огня,
мерцание пламени и живой огонь в бочках и кострах.

Как это устроено. Карта с полем "night" (цвет темноты, например [70, 76, 120]) рисуется
как обычно, а потом умножается на карту света: она залита цветом темноты, и в неё
добавляются (ADD) радиальные круги от каждого источника. Где света нет — мир тёмный и
синий, под фонарём — тёплый и почти дневной. Сверху у самих источников — неяркий ореол,
а у огня — пламя и искры.

Источники:
  - объекты карты с полем "light" в data/props.json:
      {"r": радиус круга px, "color": [r,g,b], "at": [доля ширины, доля высоты] — где источник
       на картинке, "flicker": 0..1 — дрожание огня, "flame": true — нарисовать пламя};
    круг света ложится на землю под источником (у фонаря — под плафоном);
  - "lights" в самой карте: [x, y, радиус, [r,g,b], мерцание] в пикселях мира;
  - герой: слабый свет вокруг, чтобы он не терялся в темноте.

Свет внутри здания под крышей снаружи не виден: пока крыша на месте, его источники пропускаются.
"""
import math
import random

import pygame

from . import props as P
from . import settings as S

_GRAD = {}
HERO_LIGHT = (150, (70, 68, 78))


def gradient(radius, color):
    """Круг света: в центре — color, к краю — плавно в чёрное (для смешивания ADD)."""
    key = (radius, tuple(color))
    if key not in _GRAD:
        s = pygame.Surface((radius * 2, radius * 2))
        s.fill((0, 0, 0))
        steps = max(8, radius // 3)
        for i in range(steps, 0, -1):
            k = 1 - i / steps
            k = k ** 1.25
            r = int(radius * i / steps)
            pygame.draw.circle(s, tuple(int(c * k) for c in color), (radius, radius), r)
        _GRAD[key] = s
    return _GRAD[key]


def light_sources(level):
    """Источники света карты в пикселях мира: (x, y земли, радиус, цвет, мерцание, (x, y) огня или None, ореол)."""
    out = []
    for o in getattr(level, "objects", []):
        if o.get("hidden"):
            continue
        spec = P.CATALOG.get(o["name"], {}).get("light")
        if not spec:
            continue
        r = o["rect"]
        ax, ay = spec.get("at", (0.5, 0.1))
        sx, sy = r.x + r.w * ax, r.y + r.h * ay
        ground = (sx, r.bottom - 4)
        out.append((ground[0], ground[1], spec["r"], spec["color"], spec.get("flicker", 0),
                    (sx, sy) if spec.get("flame") else None, (sx, sy)))
    for x, y, rad, color, flick in getattr(level, "lights", []):
        out.append((x, y, rad, color, flick, None, (x, y)))
    return out


class Lighting:
    def __init__(self):
        self._lm = None
        self._sources = None
        self._level = None

    def _lightmap(self, size):
        if self._lm is None or self._lm.get_size() != size:
            self._lm = pygame.Surface(size)
        return self._lm

    def apply(self, surf, level, cam, hero_screen, t_ms):
        night = getattr(level, "night", None)
        if not night:
            return
        if self._level is not level:   # источники считаются один раз на карту (объекты не двигаются)
            self._level, self._sources = level, light_sources(level)
        w, h = surf.get_size()
        view = pygame.Rect(int(cam.x), int(cam.y), w, h)
        lm = self._lightmap((w, h))
        lm.fill(tuple(night))
        visible = []
        for i, (x, y, rad, color, flick, flame, src) in enumerate(self._sources):
            if not view.inflate(rad * 2, rad * 2).collidepoint(x, y):
                continue
            roof = level.roof_over((int(x) // S.TILE, int(y) // S.TILE)) if hasattr(level, "roof_over") else None
            if roof is not None and roof["alpha"] > 128:
                continue   # лампа в доме под крышей: снаружи её свет не виден
            k = 1.0
            if flick:   # огонь дышит: радиус и яркость гуляют
                k = 1 + flick * (0.07 * math.sin(t_ms / 90 + i * 1.7) + 0.05 * math.sin(t_ms / 37 + i))
            r = max(10, int(rad * k) // 6 * 6)
            g = gradient(r, color)
            lm.blit(g, (x - view.x - r, y - view.y - r), special_flags=pygame.BLEND_RGB_ADD)
            visible.append((x, y, rad, color, flick, flame, src, k))
        hr, hc = HERO_LIGHT
        lm.blit(gradient(hr, hc), (hero_screen[0] - hr, hero_screen[1] - hr), special_flags=pygame.BLEND_RGB_ADD)
        surf.blit(lm, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        # тёплый отсвет поверх: без него круг света выходит бело-серым, а нужен оранжевый, как у огня
        for x, y, rad, color, flick, flame, src, k in visible:
            r = max(10, int(rad * 0.8 * k) // 6 * 6)
            warm = tuple(int(c * 0.32) for c in color)
            surf.blit(gradient(r, warm), (x - view.x - r, y - view.y - r), special_flags=pygame.BLEND_RGB_ADD)
        # ореолы у самих источников и пламя — поверх, светятся в темноте
        for x, y, rad, color, flick, flame, (sx, sy), k in visible:
            halo = max(12, int(rad * 0.22 * k) // 4 * 4)
            dim = tuple(int(c * 0.55) for c in color)
            surf.blit(gradient(halo, dim), (sx - view.x - halo, sy - view.y - halo),
                      special_flags=pygame.BLEND_RGB_ADD)
            if flame:
                draw_flame(surf, (sx - view.x, sy - view.y), t_ms, seed=int(sx * 7 + sy))


def draw_flame(surf, pos, t_ms, seed=0, size=1.0):
    """Живой огонь: несколько языков пламени и искры, каждые ~70 мс по-новому."""
    rnd = random.Random(seed * 1000 + t_ms // 70)
    x, y = pos
    for color, h, w in (((200, 60, 20), 22, 14), ((250, 140, 40), 16, 10), ((255, 230, 140), 9, 6)):
        for _ in range(3):
            fh = int(h * size * rnd.uniform(0.7, 1.15))
            fw = int(w * size * rnd.uniform(0.6, 1.0))
            dx = rnd.randint(-4, 4)
            pygame.draw.ellipse(surf, color, (x + dx - fw // 2, y - fh, fw, fh))
    for _ in range(3):   # искры улетают вверх
        sx = x + rnd.randint(-8, 8)
        sy = y - rnd.randint(18, 40)
        surf.fill((255, 200, 120), (sx, sy, 2, 2))
