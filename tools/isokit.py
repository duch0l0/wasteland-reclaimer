"""
Помощники генератора изометрических карт (tools/build_iso_town.py).

Логика та же, что у прямых карт: сетка клеток, непроходимые клетки, контейнеры,
терминалы, NPC. Картинка — тайлы набора «Zombie City» (tools/slice_iso.py копирует нужные).

Стены стоят на рёбрах клеток — как в Fallout. Здание занимает прямоугольник клеток;
клетки по периметру непроходимы (у стен внутри — «мёртвая» полоса: туда ставим мебель),
стены рисуются по их внешним рёбрам: сзади (север, запад) — задние стены, спереди
(юг, восток) — передние, которые изнутри становятся полупрозрачными.

Имена рёбер -> вариант тайла набора (буква — куда смотрит плоскость): север — _W, запад — _S, юг — _E, восток — _N.
"""
import json
import os
import random
import sys
from collections import deque

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
os.chdir(ROOT)

import pygame  # noqa: E402

from slice_iso import need_tile  # noqa: E402

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
pygame.init()
pygame.display.set_mode((1, 1))   # перекраска тайлов (convert_alpha) требует окна

EDGE_VARIANT = {"n": "W", "w": "S", "s": "E", "e": "N"}   # буква набора — куда смотрит плоскость стены
# глубина: задние стены — раньше персонажей, передние — позже. Передняя стена стоит на дальнем
# крае клетки; персонаж снаружи, в соседнем ряду, имеет ту же сумму x+y и долю 0.4–1.4 — поэтому
# у передних стен доля 0.35: стена соседней клетки не налезает на того, кто стоит перед ней.
# (Кто внутри здания у самой стены, может оказаться поверх неё — но передние стены тогда и так
# полупрозрачны.)
EDGE_KEY = {"n": 0.0, "w": 0.0, "s": 0.35, "e": 0.35}
BREACHES = {5, 26}   # в руинах: обрушенная ступенькой стена и высокий пролом — через них можно пролезть


class IsoKit:
    def __init__(self, w, h, start, seed=15):
        self.W, self.H, self.START = w, h, start
        self.rnd = random.Random(seed)
        self.floor = [[None] * w for _ in range(h)]
        self.objs, self.containers, self.terminals, self.roofs = [], [], [], []
        self.blocked, self.sight, self.taken = set(), set(), set()
        self.enemies, self.npcs, self.pickups, self.exits, self.portals = [], [], [], [], []
        self.hordes = []   # толпы в домах (экшен-режим)

    # -------------------------------------------------------- пол
    def ground(self, name, x0, y0, x1, y1, rot=True):
        """Залить пол тайлом; name — «Ground A» (варианты A1..An выбираются случайно) или точное имя."""
        for y in range(max(0, y0), min(self.H, y1 + 1)):
            for x in range(max(0, x0), min(self.W, x1 + 1)):
                self.floor[y][x] = need_tile(self._pick(name, rot))

    def _pick(self, name, rot=True):
        if "_" in name:
            return name
        variants = {"Ground A": 7, "Ground B": 1, "Ground C": 1, "Ground D": 1, "Ground E": 1}
        n = variants.get(name)
        base = f"{name}{self.rnd.randint(1, n)}" if n else name
        side = self.rnd.choice("NESW") if rot else "N"
        return f"{base}_{side}"

    # -------------------------------------------------------- объекты
    def obj(self, name, x, y, block=True, sight=False, k=0.96, floor=False, front=None, dx=0, dy=0):
        o = {"t": name if name.startswith("x_") else need_tile(name), "x": x, "y": y, "k": k}   # x_ — свои тайлы
        if block:
            o["b"] = 1
            self.blocked.add((x, y))
        if sight:
            o["s"] = 1
            self.sight.add((x, y))
        if floor:
            o["floor"] = True
        if front is not None:
            o["front"] = front
        if dx or dy:
            o["dx"], o["dy"] = dx, dy
        self.objs.append(o)
        self.taken.add((x, y))
        return len(self.objs) - 1

    def free(self, x, y):
        return (0 < x < self.W - 1 and 0 < y < self.H - 1 and (x, y) not in self.taken
                and (x, y) not in self.blocked and self.floor[y][x] is not None)

    def box(self, name, x, y, title, loot, requires=None, owner=None):
        i = self.obj(name, x, y)
        self.containers.append({"obj": i, "name": title, "loot": loot, "requires": requires, "owner": owner})
        return i

    def terminal(self, name, x, y, tid):
        i = self.obj(name, x, y)
        self.terminals.append({"obj": i, "id": tid})

    # -------------------------------------------------------- здания
    def building(self, x0, y0, x1, y1, style, floor="Ground E1_N", doors=(), windows=(), roof="Roof A3",
                 roof_edge=None, sign=None, ruined=False, plain=None):
        """Здание в клетках x0..x1, y0..y1. style — буква стен набора (A камень, B бетон, D кирпич).
        doors / windows — [(край, смещение)] (край n/s/w/e, смещение вдоль края от угла); вариант
        двери/окна — (край, смещение, номер тайла). ruined — без крыши, стены с проломами."""
        rnd = self.rnd
        plain = plain or [1]
        self.ground(floor, x0, y0, x1, y1, rot=False)
        ri = None
        if not ruined:
            ri = len(self.roofs)
            # плиты крыши: середина — ровная, по краю — с парапетом (A1 — сторона, A2 — угол)
            tiles = {"mid": need_tile(f"{roof}_N")}
            for v in "NESW":
                tiles[f"edge_{v}"] = need_tile(f"Roof A1_{v}")
                tiles[f"corner_{v}"] = need_tile(f"Roof A2_{v}")
            self.roofs.append({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "tiles": tiles,
                               **({"sign": sign} if sign else {})})
        door_map = {(e, off): num for e, off, *num in [(d[0], d[1], *(d[2:] or [3])) for d in doors]}
        win_map = {(e, off): num for e, off, *num in [(d[0], d[1], *(d[2:] or [21])) for d in windows]}
        edges = {"n": [(x, y0) for x in range(x0, x1 + 1)], "s": [(x, y1) for x in range(x0, x1 + 1)],
                 "w": [(x0, y) for y in range(y0, y1 + 1)], "e": [(x1, y) for y in range(y0, y1 + 1)]}
        door_tiles = set()
        for e, cells in edges.items():
            for off, (x, y) in enumerate(cells):
                if (e, off) in door_map:
                    num = door_map[(e, off)][0]
                    door_tiles.add((x, y))
                elif (e, off) in win_map:
                    num = win_map[(e, off)][0]
                elif ruined and rnd.random() < 0.25:
                    num = rnd.choice([4, 5, 26]) if rnd.random() < 0.7 else None
                    if num is None or num in BREACHES:   # пролом выглядит как проход — и он проход
                        door_tiles.add((x, y))
                else:
                    num = rnd.choice(plain)
                if num is not None:
                    self.obj(f"Wall {style}{num}_{EDGE_VARIANT[e]}", x, y, block=False, sight=False,
                             k=EDGE_KEY[e], front=ri if e in ("s", "e") else None)
        # периметр непроходим, кроме дверей (стены — на рёбрах, клетка внутри — «мёртвая» полоса)
        for e, cells in edges.items():
            for c in cells:
                if c not in door_tiles:
                    self.blocked.add(c)
                    self.sight.add(c)
                    self.taken.add(c)
        # вход: у двери — ни мебели, ни обломков
        for (x, y) in door_tiles:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    self.taken.add((x + dx, y + dy))
        return ri

    # -------------------------------------------------------- проверка и запись
    def reachable(self):
        seen = {self.START}
        q = deque([self.START])
        while q:
            cx, cy = q.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (cx + dx, cy + dy)
                if (0 <= n[0] < self.W and 0 <= n[1] < self.H and n not in seen and n not in self.blocked
                        and self.floor[n[1]][n[0]] is not None):
                    seen.add(n)
                    q.append(n)
        return seen

    def check(self):
        reach = self.reachable()
        for kind, x, y in self.enemies + [[n, x, y] for n, x, y in self.npcs]:
            assert (x, y) in reach, f"{kind} в недоступной клетке {x, y}"
        for item, _, x, y in self.pickups:
            assert (x, y) in reach, f"{item} недоступен {x, y}"
        for c in self.containers + self.terminals:
            o = self.objs[c["obj"]]
            assert any((o["x"] + dx, o["y"] + dy) in reach for dx in (-1, 0, 1) for dy in (-1, 0, 1)), \
                f"к {c.get('name', c.get('id'))} не подойти"
        for t in self.exits:
            assert tuple(t) in reach, f"выход {t} недоступен"
        return reach

    def save(self, path, **extra):
        pal, idx = [], {}
        rows = []
        for row in self.floor:
            r = []
            for t in row:
                if t is None:
                    r.append(-1)
                    continue
                if t not in idx:
                    idx[t] = len(pal)
                    pal.append(t)
                r.append(idx[t])
            rows.append(r)
        out = {"iso": True, "w": self.W, "h": self.H, "player": list(self.START), "palette": pal, "floor": rows,
               "objs": self.objs, "blocked": sorted(self.blocked), "sight": sorted(self.sight),
               "containers": self.containers, "terminals": self.terminals, "roofs": self.roofs,
               "exits": [list(t) for t in self.exits], "portals": self.portals,
               "enemies": self.enemies, "npcs": self.npcs, "pickups": self.pickups, **extra}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, separators=(",", ":"))


# ================================================================ общие приёмы генератора
DUST = "Ground D1_{r}@dust"


class Town(IsoKit):
    """IsoKit + улицы, тротуары, машины, заборы, вывески, рельсы."""

    def dust(self, x0, y0, x1, y1):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.ground(DUST.format(r=self.rnd.choice("NESW")), x, y, x, y)

    def pavers(self, x0, y0, x1, y1, broken=0.12):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                n = self.rnd.choice((1, 2, 3, 4, 5)) if self.rnd.random() > broken else self.rnd.choice((6, 7))
                self.ground(f"Ground A{n}_{self.rnd.choice('NESW')}", x, y, x, y)

    def road_x(self, y0, y1, x0=0, x1=None, center="Ground B2_E"):
        """Дорога вдоль x (на экране — вниз-вправо), по середине — разметка."""
        x1 = self.W - 1 if x1 is None else x1
        self.ground("Ground B1_N", x0, y0, x1, y1, rot=False)
        if center and y1 - y0 >= 2:
            self.ground(center, x0, (y0 + y1) // 2, x1, (y0 + y1) // 2, rot=False)

    def road_y(self, x0, x1, y0=0, y1=None, dashes=True):
        """Дорога вдоль y (на экране — вниз-влево), прерывистая по оси."""
        y1 = self.H - 1 if y1 is None else y1
        self.ground("Ground B1_N", x0, y0, x1, y1, rot=False)
        if dashes and x1 - x0 >= 2:
            for y in range(y0, y1 + 1, 2):
                self.ground("Ground B7_N", (x0 + x1) // 2, y, (x0 + x1) // 2, y, rot=False)

    def edge_line(self, tile_base, cells, edge, block=True):
        """Забор/ограда по ребру клеток (как стены)."""
        for x, y in cells:
            self.obj(f"{tile_base}_{EDGE_VARIANT[edge]}", x, y, block=block, k=EDGE_KEY[edge])

    def lamp(self, x, y):
        if self.free(x, y):
            self.obj("StreetLamp 1_N", x, y)

    def car(self, n, x, y, side="N"):
        """Машина 2×2 клетки (картинка 256×512): ставится по левой-верхней клетке."""
        cells = [(x + dx, y + dy) for dx in (0, 1) for dy in (0, 1)]
        if not all(self.free(*c) for c in cells):
            return False
        self.obj(f"Car{n}_{side}", x, y, dx=-64, dy=-175, k=1.9)
        for c in cells:
            self.blocked.add(c)
            self.taken.add(c)
        return True

    def sign(self, name, x, y, edge):
        """Вывеска/деталь стены набора (HOTEL, MART, MOTEL, пожарная лестница) на ребре клетки.
        Вывеска выше края стены — рисуется после крыши своего здания, иначе крыша её срежет."""
        k = EDGE_KEY[edge] + 0.02
        for r in self.roofs:
            if r["x0"] <= x <= r["x1"] and r["y0"] <= y <= r["y1"]:
                k = r["x1"] + r["y1"] + 2.3 - (x + y)
        self.obj(f"{name}_{EDGE_VARIANT[edge]}", x, y, block=False, k=k)

    def scatter(self, names, x0, y0, x1, y1, n, block=True, only_dust=False, k=0.96):
        placed = 0
        for _ in range(n * 30):
            if placed >= n:
                break
            x, y = self.rnd.randint(x0, x1), self.rnd.randint(y0, y1)
            if not self.free(x, y):
                continue
            if only_dust and not (self.floor[y][x] or "").startswith("ground_d1"):
                continue
            self.obj(self.rnd.choice(names), x, y, block=block, k=k)
            placed += 1
        return placed

    def grass(self, x0, y0, x1, y1, clumps):
        for _ in range(clumps):
            cx, cy = self.rnd.randint(x0, x1), self.rnd.randint(y0, y1)
            for _ in range(self.rnd.randint(2, 5)):
                x, y = cx + self.rnd.randint(-1, 1), cy + self.rnd.randint(-1, 1)
                if self.free(x, y) and (self.floor[y][x] or "").startswith("ground_d1"):
                    self.obj(f"Flora A{self.rnd.randint(1, 7)}_{self.rnd.choice('NESW')}", x, y, block=False, k=0.9)

    def splats(self, x0, y0, x1, y1, n):
        for _ in range(n):
            x, y = self.rnd.randint(x0, x1), self.rnd.randint(y0, y1)
            if self.free(x, y):
                self.obj(f"Splat {self.rnd.randint(1, 5)}_{self.rnd.choice('NESW')}", x, y, block=False, floor=True)

    def rails_x(self, y, x0=0, x1=None):
        """Железнодорожный путь вдоль x: щебень, шпалы, два рельса."""
        x1 = self.W - 1 if x1 is None else x1
        tid = make_rails_tile()
        for x in range(x0, x1 + 1):
            self.floor[y][x] = tid

    def portal(self, tiles, to, at, label, requires=None):
        p = {"tiles": [list(t) for t in tiles], "to": to, "at": list(at), "label": label}
        if requires:
            p["requires"] = requires
        self.portals.append(p)
        for t in tiles:
            self.taken.add(tuple(t))


def make_rails_tile():
    """Тайл пути: песок, щебёночная насыпь, деревянные шпалы поперёк, стальные рельсы вдоль x."""
    tid = "x_rails_x"
    dst = os.path.join(ROOT, "assets", "iso", "tiles", tid + ".png")
    if os.path.isfile(dst):
        return tid
    base = pygame.image.load(os.path.join(ROOT, "assets", "iso", "tiles", need_tile("Ground D1_N@dust") + ".png"))
    img = base.convert_alpha()
    cx, cy = 64, 207

    def p(u, v):   # точка в долях клетки (u вдоль x, v вдоль y, от центра) -> пиксель тайла
        return (cx + (u - v) * 64, cy + (u + v) * 32)
    pygame.draw.polygon(img, (118, 108, 96), [p(-0.5, -0.32), p(0.5, -0.32), p(0.5, 0.32), p(-0.5, 0.32)])
    rnd = random.Random(7)
    for _ in range(140):
        u, v = rnd.uniform(-0.5, 0.5), rnd.uniform(-0.3, 0.3)
        x, y = p(u, v)
        img.fill(rnd.choice(((92, 86, 78), (140, 130, 116), (104, 96, 88))), (int(x), int(y), 2, 2))
    for u in (-0.375, -0.125, 0.125, 0.375):
        pygame.draw.polygon(img, (86, 62, 42), [p(u - 0.06, -0.28), p(u + 0.06, -0.28), p(u + 0.06, 0.28),
                                               p(u - 0.06, 0.28)])
        pygame.draw.line(img, (110, 82, 56), p(u - 0.06, -0.28), p(u - 0.06, 0.28), 1)
    for v in (-0.16, 0.16):
        pygame.draw.line(img, (60, 58, 56), p(-0.5, v + 0.02), p(0.5, v + 0.02), 3)
        pygame.draw.line(img, (170, 168, 160), p(-0.5, v), p(0.5, v), 2)
    pygame.image.save(img, dst)
    return tid


def make_neon_tile(text, tid, color=(255, 70, 190)):
    """Неоновая вывеска на южную (передне-левую) стену: текст, наклонённый по плоскости стены,
    со свечением. Картинка шире тайла — ставится по левой клетке стены."""
    dst = os.path.join(ROOT, "assets", "iso", "tiles", tid + ".png")
    if os.path.isfile(dst):
        return tid
    font = pygame.font.Font(None, 52)
    t = font.render(text, True, color)
    w, h = t.get_width() + 16, t.get_height() + 16
    flat = pygame.Surface((w, h), pygame.SRCALPHA)
    glow = font.render(text, True, (color[0] // 2, color[1] // 3, color[2] // 2))
    for dx in range(-4, 5, 2):
        for dy in range(-4, 5, 2):
            g = glow.copy()
            g.set_alpha(40)
            flat.blit(g, (8 + dx, 8 + dy))
    flat.blit(t, (8, 8))
    pygame.draw.rect(flat, (40, 30, 40), flat.get_rect(), 3, border_radius=6)
    sheared = pygame.Surface((w, h + w // 2 + 2), pygame.SRCALPHA)   # по стене: вдоль x вниз вдвое медленнее
    for x in range(w):
        sheared.blit(flat, (x, x // 2), area=pygame.Rect(x, 0, 1, h))
    out = pygame.Surface((max(128, w), 256), pygame.SRCALPHA)
    out.blit(sheared, (0, 256 - 150 - sheared.get_height() // 2))
    pygame.image.save(out, dst)
    return tid
