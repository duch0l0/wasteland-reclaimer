"""
Общие помощники генераторов карт из объектов (tools/build_town.py, tools/build_underground.py).

Карта собирается из клеток земли (ground) и объектов набора «wasteland town»
плюс своих (tools/make_props.py). Каждый загораживающий объект ставится,
только если после него все места, куда можно было дойти, остаются
достижимыми — карта не запирает проходы. Случайность фиксирована (seed).
"""
import json
import os
import random
import sys
from collections import deque

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from src import props as P  # noqa: E402

T = 48

# ------------------------------------------------------------ наборы объектов
BARRELS = [f"barrel_{i}" for i in (0, 1, 2, 3, 4, 5, 9, 10, 11, 12, 13, 18)]
CRATES = ["crate", "crate_b", "crate_small", "cardboard", "crate_empty", "crate_open", "crate_broken"]
GRASS = [f"grass_{i}" for i in (5, 6, 10, 13, 18, 26, 28, 29, 35, 36, 53, 54, 65, 66, 68, 78, 80)]
BUSHES = ["bush_11", "bush_37", "bush_79", "grass_big"]
STONES = ["stones_12", "stones_19", "stones_21", "stones_62", "stones_63", "clods_67", "clods_81"]
FLOOR_BITS = ["bricks_a", "brick_b", "bricks_c", "brick_d", "bricks_e", "concrete_bit", "concrete_bit_b",
              "concrete_bits", "plank_floor", "log", "rebar_bits", "cloth_bit", "cloth_bit_b", "sock", "rag", "bits"]
# только пятна с рваными краями: квадратные куски выглядят вырезанными и вставленными
DIRT_DECALS = ["dirt_patch"]
JUNK_PILES = ["pile_cans", "pile_tires", "pile_scrap", "pile_electronics", "pile_bottles", "pile_tech_tire",
              "pile_barrel_junk", "pile_tires_pc", "pile_junk", "pile_bottles_b", "pile_tires_cans",
              "pile_appliances", "pile_computers", "pile_electronics_b", "pile_sink_junk"]
CLOTH_PILES = ["pile_rags", "pile_cloth", "pile_cloth_bottle", "pile_cloth_b", "pile_clothes", "pile_bags",
               "pile_cloth_scrap"] + [f"clothes_{i}" for i in (55, 56, 72, 73, 74, 75, 76, 77, 78)]
RUBBLE = ["rubble_a", "rubble_b", "brick_pile_a", "brick_pile_b", "concrete_block", "cinder_a", "cinder_b",
          "cinder_c", "rubble_heap", "rubble_rebar", "rebar_fence", "plank_block", "planks", "metal_sheets_b"]
FURNITURE = ["table_1", "table_2", "table_3", "table_4", "table_5", "chair_wood", "chair_b", "chair_c", "chair_1",
             "chair_2", "chair_3", "sofa", "sofa_corner", "bed", "bed_frame", "table_upside", "stool_1", "stool_2",
             "armchair", "nightstand", "cabinet_small", "wardrobe", "wardrobe_junk", "shelf_goods", "table_chair"]
LOCKERS = ["locker_1", "locker_2", "locker_3", "locker_4", "filecab_1", "filecab_2", "filecab_3", "locker_double"]
POLES = [f"pole_{i}" for i in (8, 9, 17, 25, 38, 49, 51, 52, 76, 77)]
SIGNS = ["sign_stop"] + [f"sign_{i}" for i in (43, 44, 50, 70, 71, 72, 73, 74)]
PLANTS = set(GRASS + BUSHES)
OUTDOOR = set(GRASS + BUSHES + POLES + SIGNS + STONES + ["rock_grass", "rock_grass_b", "dead_tree", "lamp_post",
                                                         "x_cross", "x_tombstone", "x_grave"])
SEATS = [f"seat_{i}" for i in (14, 15, 22, 23, 32, 33, 39, 40, 46, 47)]
BENCHES = [f"bench_{i}" for i in (7, 16, 24, 34, 48)]

# стили зданий: целые фасады для северной стены (по ширине в клетках),
# для южной — вперемешку целые и обветшалые; боковые стены — vwall_<стиль>_w/e
WALLS_INTACT = {
    "brick": {4: ["wall_brick_long"], 2: ["wall_concrete_brick"]},
    "concrete": {2: ["wall_concrete", "wall_concrete_brick"]},
    "metal": {2: ["wall_metal", "wall_metal2", "wall_corrugated"]},
    "planks": {2: ["wall_planks", "wall_planks_blue", "wall_planks_dark"]},
}
WALLS_WORN = {
    "brick": {4: ["wall_brick_long", "wall_brick_crumble"], 2: ["wall_concrete_brick"]},
    "concrete": {4: ["wall_grey_broken"], 2: ["wall_concrete", "wall_concrete_broken", "wall_concrete_broken2"]},
    "metal": {2: ["wall_metal", "wall_metal2", "wall_corrugated", "wall_corrugated2", "wall_corrugated_rust"]},
    "planks": {2: ["wall_planks", "wall_planks_blue", "wall_planks_dark", "wall_corrugated_small"]},
}


class MapKit:
    def __init__(self, w, h, start, seed, fill="d"):
        self.W, self.H, self.START = w, h, start
        self.rnd = random.Random(seed)
        self.ground = [[fill] * w for _ in range(h)]
        self.props, self.decals, self.containers, self.terminals = [], [], [], []
        self.blocked, self.soft, self.reserved = set(), set(), set()
        self.enemies, self.npcs, self.pickups = [], [], []
        self.exits, self.portals = [], []
        self.roofs = []     # крыши зданий: убираются, когда герой внутри
        self._reach = None

    # -------------------------------------------------------- земля и резерв
    def paint(self, code, x0, y0, x1, y1):
        for y in range(max(0, y0), min(self.H, y1 + 1)):
            for x in range(max(0, x0), min(self.W, x1 + 1)):
                self.ground[y][x] = code

    def reserve(self, x0, y0, x1, y1):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.reserved.add((x, y))

    def solid(self, x, y):
        return (x, y) in self.blocked or self.ground[y][x] == "x"

    def footprint(self, name, x, y):
        fw, fh = P.info(name)["foot"]
        return [(x + i, y + j) for i in range(fw) for j in range(fh)]

    def reachable(self, extra=(), passable=()):
        seen = {self.START}
        q = deque([self.START])
        bad = (self.blocked | set(extra)) - set(passable)
        while q:
            cx, cy = q.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (cx + dx, cy + dy)
                if (0 <= n[0] < self.W and 0 <= n[1] < self.H and n not in seen and n not in bad
                        and self.ground[n[1]][n[0]] != "x"):
                    seen.add(n)
                    q.append(n)
        return seen

    # -------------------------------------------------------- объекты
    def put(self, name, x, y, check=True, allow_reserved=False, owner=None, force=False):
        """Поставить объект; False — не влез или перекрыл бы проход.
        force — без проверок (угловой кусок боковой стены поверх фасада)."""
        inf = P.info(name)
        foot = self.footprint(name, x, y)
        if force:
            self.props.append([name, x, y])
            if inf["block"]:
                self.blocked.update(foot)
                self._reach = None
            return True
        if any(not (1 <= fx < self.W - 1 and 1 <= fy < self.H - 1) for fx, fy in foot):
            return False
        if any(self.ground[fy][fx] == "x" for fx, fy in foot):
            return False
        if name in OUTDOOR and any(self.ground[fy][fx] in "cmw" for fx, fy in foot):
            return False  # трава, кусты, знаки и камни — только снаружи зданий
        if name in PLANTS and any(self.ground[fy][fx] != "d" for fx, fy in foot):
            return False  # трава и кусты не растут на асфальте и гравии
        if inf["block"]:
            if any(t in self.blocked for t in foot):
                return False
            if not allow_reserved and any(t in self.reserved for t in foot):
                return False
            if check:
                if self._reach is None:
                    self._reach = len(self.reachable())
                n = len(self.reachable(foot))
                if n < self._reach - len([t for t in foot if t not in self.blocked]):
                    return False  # отрезал бы кусок карты
            self.blocked.update(foot)
            self._reach = None
        else:
            if any(t in self.soft or t in self.blocked for t in foot):
                return False
            self.soft.update(foot)
        if name in PLANTS or name in STONES:   # живое и мелкое — не по сетке
            self.props.append([name, x, y, self.rnd.randint(-14, 14), self.rnd.randint(-10, 8)])
        else:
            self.props.append([name, x, y])
        if inf.get("search"):
            self.containers.append({"prop": len(self.props) - 1, "name": inf.get("title", "ящик"),
                                    "loot": self.roll_loot(inf["search"]), "owner": owner})
        return True

    def terminal(self, x, y, tid):
        """Терминал RobCo (стол с монитором) — содержимое в data/terminals.json."""
        assert self.put("terminal", x, y, check=False), f"терминал {tid} не встал в {x, y}"
        self.terminals.append({"prop": len(self.props) - 1, "id": tid})

    def box(self, name, x, y, title, loot, requires=None, owner=None):
        """Контейнер с заданным содержимым (сюжетный, не случайный)."""
        assert self.put(name, x, y, check=False, owner=owner), f"{title} не встал в {x, y}"
        if not P.info(name).get("search"):  # обычный объект (бочка, витрина) — тоже можно обыскать
            self.containers.append({"prop": len(self.props) - 1, "owner": owner})
        self.containers[-1].update({"name": title, "loot": loot, "requires": requires})

    def roll_loot(self, table):
        loot = {}
        for item, (lo, hi, chance) in P.LOOT_TABLES[table].items():
            if self.rnd.randint(1, 100) <= chance:
                loot[item] = self.rnd.randint(lo, hi)
        return loot

    def scatter(self, names, x0, y0, x1, y1, n, tries=40):
        placed = 0
        for _ in range(n * tries):
            if placed >= n:
                break
            if self.put(self.rnd.choice(names), self.rnd.randint(x0, x1), self.rnd.randint(y0, y1)):
                placed += 1
        return placed

    def grow(self, x0, y0, x1, y1, clumps, names=None):
        """Растительность куртинами, как растёт на самом деле: у стен, заборов, обочин
        (где есть тень и сток воды) гуще, на открытом месте — редкие кустики.
        В куртине 3–8 растений, к краю реже; соседние — разные."""
        names = names or GRASS + BUSHES
        rnd = self.rnd
        cand = [(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)
                if 0 < x < self.W - 1 and 0 < y < self.H - 1 and self.ground[y][x] == "d"
                and (x, y) not in self.blocked]
        if not cand:
            return
        def shelter(t):  # рядом стена, забор, дорога или объект — тут растёт гуще
            return sum(1 for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                       if (t[0] + dx, t[1] + dy) in self.blocked
                       or self.ground[min(self.H - 1, t[1] + dy)][min(self.W - 1, t[0] + dx)] in "ag")
        weighted = [t for t in cand if shelter(t)] * 3 + cand
        placed = 0
        for _ in range(clumps):
            cx, cy = rnd.choice(weighted)
            size = rnd.randint(3, 8)
            last = None
            for _ in range(size * 4):
                if size <= 0:
                    break
                r = rnd.choice((0, 0, 1, 1, 1, 2))   # плотная куртина, редкие побеги по краю
                t = (cx + rnd.randint(-r, r), cy + rnd.randint(-r, r))
                name = rnd.choice([n for n in names if n != last] or names)
                if self.put(name, *t):
                    last, size, placed = name, size - 1, placed + 1
        return placed

    def decal(self, names, x0, y0, x1, y1, n, floor_ok=False):
        for _ in range(n):
            x, y = self.rnd.randint(x0, x1), self.rnd.randint(y0, y1)
            if self.ground[y][x] in ("x",) or (not floor_ok and self.ground[y][x] == "c"):
                continue  # пятна земли — не на полу зданий
            self.decals.append([self.rnd.choice(names), x * T + self.rnd.randint(8, 40),
                                y * T + self.rnd.randint(8, 40)])

    def hwall(self, names, x0, x1, y, gaps=()):
        """Ряд стен/заборов по строке y от x0 до x1, с проходами в клетках gaps."""
        x = x0
        while x <= x1:
            if x in gaps:
                x += 1
                continue
            name = self.rnd.choice(names)
            fw = P.info(name)["foot"][0]
            if x + fw - 1 > x1 or any(g in range(x, x + fw) for g in gaps) or not self.put(name, x, y, check=False):
                x += 1
                continue
            x += fw

    def vline(self, names, x, y0, y1, gaps=()):
        for y in range(y0, y1 + 1):
            if y not in gaps:
                self.put(self.rnd.choice(names), x, y, check=False)

    def wall_row(self, pieces, x0, x1, y, gaps=()):
        """Сплошной ряд фасадов от x0 до x1 по строке y, кроме клеток-проёмов gaps."""
        x = x0
        while x <= x1:
            if x in gaps:
                x += 1
                continue
            end = x
            while end + 1 <= x1 and end + 1 not in gaps:
                end += 1
            left = end - x + 1
            while left > 0:
                w = 4 if left >= 4 and 4 in pieces and self.rnd.random() < 0.6 else 2
                if w not in pieces or left < w:
                    w = 2
                if left < w:  # нечётный хвост — боковой кусок стены
                    break
                self.put(self.rnd.choice(pieces[w]), x, y, check=False, allow_reserved=True)
                x += w
                left -= w
            x = end + 1

    def side_wall(self, style, side, x, y0, y1, gaps=()):
        for y in range(y0, y1 + 1):
            if y not in gaps:
                self.put(f"vwall_{style}_{side}", x, y, check=False, allow_reserved=True)

    def building(self, x0, y0, w, h, style, south=(), west=(), east=(), north=(), roof=True, sign=None):
        """Здание со всеми стенами: северная — целая (north — проёмы), южная — с проёмами
        дверей (смещения от x0, чётные, проём 2 клетки), боковые — с проёмами в строках
        west/east (смещения от y0). Пол бетонный. w — чётное. Возвращает внутренность."""
        assert w % 2 == 0, "ширина здания — чётная (фасады по 2 клетки)"
        x1, y1 = x0 + w - 1, y0 + h - 1
        self.paint("c", x0, y0 + 1, x1, y1)
        if roof:
            self.roofs.append({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "style": style,
                               "seed": len(self.roofs) * 7 + x0 * 3 + y0, "sign": sign})
        ngaps = set()
        for off in north:
            ngaps.update((x0 + off, x0 + off + 1))
        self.wall_row(WALLS_INTACT[style], x0, x1, y0, gaps=ngaps)
        doors = set()
        for off in south:
            assert off % 2 == 0, "дверь на южной стене — с чётного смещения"
            doors.update((x0 + off, x0 + off + 1))
        self.wall_row(WALLS_WORN[style], x0, x1, y1, gaps=doors)
        for side, x, gaps in (("w", x0, west), ("e", x1, east)):
            self.put(f"vwall_{style}_{side}", x, y0, force=True, allow_reserved=True)
            for y in range(y0 + 1, y1):
                if y - y0 not in gaps:
                    self.put(f"vwall_{style}_{side}", x, y, check=False, allow_reserved=True)
        for off in south:  # у двери ничего не ставим
            self.reserve(x0 + off, y1 - 1, x0 + off + 1, y1 + 1)
        return (x0 + 1, y0 + 1, x1 - 1, y1 - 1)

    def portal(self, tiles, to, at, label):
        self.portals.append({"tiles": [list(t) for t in tiles], "to": to, "at": list(at), "label": label})
        for t in tiles:
            self.reserve(*t, *t)

    # -------------------------------------------------------- проверка и запись
    def check(self, npc_enemy_gap=6, gap_exempt=(), passable=()):
        """passable — клетки, которые откроются по ходу игры (гермодвери)."""
        reach = self.reachable(passable=passable)
        for kind, x, y in self.enemies + [[n, x, y] for n, x, y in self.npcs]:
            assert (x, y) in reach and (x, y) not in self.blocked, f"{kind} в недоступной клетке {x, y}"
        for item, _, x, y in self.pickups:
            assert (x, y) in reach, f"{item} недоступен {x, y}"
        for c in self.containers:
            foot = self.footprint(*self.props[c["prop"]])
            assert any((fx + dx, fy + dy) in reach for fx, fy in foot for dx in (-1, 0, 1) for dy in (-1, 0, 1)), \
                f"к {c['name']} не подойти"
        for t in self.terminals:
            foot = self.footprint(*self.props[t["prop"]])
            assert any((fx + dx, fy + dy) in reach for fx, fy in foot for dx in (-1, 0, 1) for dy in (-1, 0, 1)), \
                f"к терминалу {t['id']} не подойти"
        for t in self.exits:
            assert tuple(t) in reach, f"выход {t} недоступен"
        for p in self.portals:
            assert any(tuple(t) in reach for t in p["tiles"]), f"портал {p['to']} недоступен"
        for kind, ex, ey in self.enemies:
            for nid, nx, ny in self.npcs:
                if nid in gap_exempt:
                    continue
                assert max(abs(ex - nx), abs(ey - ny)) >= npc_enemy_gap, f"{kind} слишком близко к {nid}"
        return reach

    def save(self, path, **extra):
        out = {"w": self.W, "h": self.H, "player": list(self.START), "exits": [list(t) for t in self.exits],
               "ground": ["".join(r) for r in self.ground], "decals": self.decals, "props": self.props,
               "containers": self.containers, "terminals": self.terminals, "portals": self.portals,
               "roofs": self.roofs,
               "enemies": self.enemies, "npcs": self.npcs, "pickups": self.pickups, **extra}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
