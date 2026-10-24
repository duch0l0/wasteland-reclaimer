"""
Конструктор больших городов из наборов Cute SCKR — поверх tools/mapkit.py.

Город = несколько локаций-карт: районы улицы (переходы — зелёные стрелки на краях дорог),
интерьеры домов (вход — дверь на улице), подвалы и этажи (лестницы). Каждая карта —
`CityMap`, все карты города — в `City`, который в конце пишет:
  data/maps/<id>.json          карты
  data/props/<город>.json      свои объекты (картинки «pk:…», см. src/props.py)
  data/locations.json          записи локаций (имя, музыка, ночь, «известна ли»)

Что умеет CityMap кроме MapKit:
  floors / walls      — свои коды земли: пол из набора и стены A4 (верх с окантовкой и фасад);
  room()              — комната: стены вокруг пола, у северной стены три ряда (верх + фасад 2 клетки);
  opening()           — проём в стене (дверь между комнатами);
  stamp()             — кусок страницы набора как плоская земля (озеро, дорожка, площадь);
                        клетки с водой сами становятся непроходимыми;
  thing()             — объект набора (дом, мебель, машина) с пятном на земле;
Связи между картами — City.door(), City.stairs(), City.road(): порталы в обе стороны.

Правила расстановки (чтобы всё стояло логично):
  - перед каждым проёмом (opening) и за ним — две клетки прохода, туда ничего не ставится;
  - явно расставленный объект (put, box, thing) обязан встать: если клетка занята, в проходе или
    объект перекрыл бы путь — сборка падает с ошибкой, а не тихо пропускает и не ставит в дверь;
    необязательные — maybe(), случайные — scatter()/grow();
  - мебель ставится по смыслу комнаты: шкафы и стеллажи вдоль стен, столы со стульями вместе,
    кровати — у стены, проход от двери к центру комнаты свободен.

Примеры — tools/build_fifteen.py, tools/build_baker_levels.py.
"""
import json
import os

from mapkit import MapKit, ROOT
from src import props as P  # noqa: E402

import pygame

T = 48


class CityMap(MapKit):
    def __init__(self, city, mid, name, w, h, start, seed=1, fill="d", night=None, music="desert",
                 interior=False, known=False, world_pos=None, furnish=None):
        """furnish — своя обстановка для голого интерьера вместо стиля по id: {"scenes": [...],
        "along": ([у стены], [в углах])}; False — не обставлять вовсе."""
        super().__init__(w, h, start, seed, fill="_" if interior else fill)
        self.furnish = furnish
        self.music_zones = []      # [x0, y0, x1, y1, ключ]: в салуне — граммофон, в казино — джаз
        self.walk_zones = {}       # npc_id -> [x0, y0, x1, y1]: житель ходит у своего дела (src/wander.py)
        self.folk_spots = {}       # ключ анкеты жителя -> клетка, «critter:<вид>» -> [клетки] (src/ambient.py)
        self.city, self.id, self.name = city, mid, name
        self.floors, self.walls = {}, {}
        self.night, self.music, self.interior = night, music, interior
        self.known, self.world_pos = known, world_pos
        self.tint = None
        city.maps.append(self)

    def music_zone(self, x0, y0, x1, y1, key):
        """Своя музыка внутри здания на городской карте (src/game/world.py: update_music_zone)."""
        self.music_zones.append([x0, y0, x1, y1, key])

    # -------------------------------------------------------- коды земли из наборов
    def floor_code(self, code, *imgs):
        self.floors[code] = list(imgs)
        return code

    def wall_code(self, code, wall):
        self.walls[code] = wall
        return code

    def solid(self, x, y):
        return (x, y) in self.blocked or self.ground[y][x] in ("x", "_") or self.ground[y][x] in self.walls

    def reachable(self, extra=(), passable=()):
        from collections import deque
        seen = {self.START}
        q = deque([self.START])
        bad = (self.blocked | set(extra)) - set(passable)
        while q:
            cx, cy = q.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (cx + dx, cy + dy)
                if (0 <= n[0] < self.W and 0 <= n[1] < self.H and n not in seen and n not in bad
                        and self.ground[n[1]][n[0]] not in ("x", "_") and self.ground[n[1]][n[0]] not in self.walls):
                    seen.add(n)
                    q.append(n)
        return seen

    # -------------------------------------------------------- комнаты
    def room(self, x0, y0, x1, y1, wall, floor):
        """Комната в клетках x0..x1, y0..y1 (включая стены). Северная стена — 3 ряда (верх и фасад
        в 2 клетки, как в RPG Maker), остальные — 1. Возвращает внутренность (x0, y0, x1, y1) пола."""
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if self.ground[y][x] not in self.floors:   # соседние комнаты делят стену
                    self.ground[y][x] = wall
        for y in range(y0 + 3, y1):
            for x in range(x0 + 1, x1):
                self.ground[y][x] = floor
        self._reach = None
        return (x0 + 1, y0 + 3, x1 - 1, y1 - 1)

    def opening(self, x0, y0, x1, y1, floor):
        """Проём (дверь, арка) — клетки стены становятся полом. Перед проёмом и за ним — по две клетки
        зоны прохода: туда ничего не ставится (put откажет, а явная расстановка упадёт с ошибкой)."""
        self.paint(floor, x0, y0, x1, y1)
        self.__dict__.setdefault("openings", []).append((x0, y0, x1, y1))
        if (y1 - y0) >= (x1 - x0):      # проход с севера на юг
            self.reserve(x0, max(0, y0 - 2), x1, min(self.H - 1, y1 + 2))
        else:                            # с запада на восток
            self.reserve(max(0, x0 - 2), y0, min(self.W - 1, x1 + 2), y1)
        self._reach = None

    # -------------------------------------------------------- строгая расстановка
    # Явно расставленный объект обязан встать: если клетка занята, в зоне прохода или объект
    # перекрыл бы путь — сборка падает с понятной ошибкой (а не тихо пропускает или
    # ставит предмет в дверной проём). Случайная расстановка (scatter, grow, hwall) — как раньше.
    _loose = 0

    def put(self, name, x, y, check=True, allow_reserved=False, owner=None, force=False):
        ok = super().put(name, x, y, check=check, allow_reserved=allow_reserved, owner=owner, force=force)
        if not ok and not force and self._near_scaled(x, y):
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1), (-1, 1), (1, -1)):
                if super().put(name, x + dx, y + dy, check=check, allow_reserved=allow_reserved, owner=owner):
                    print(f"   {self.id}: «{name}» сдвинут на ({dx}, {dy}) — рядом выросла декорация")
                    return True
        if not ok and P.world_scale(name) != 1:
            # декорация выросла под рост героя (data/prop_scale.json) — сдвинуть рядом, где влезет
            fw, fh = P.info(name)["foot"]
            for dx, dy in [(-i, 0) for i in range(1, fw + 1)] + [(0, -j) for j in range(1, fh + 2)] + \
                    [(-i, -j) for i in range(1, fw + 1) for j in range(1, fh + 2)] + [(i, 0) for i in range(1, 4)] + \
                    [(0, j) for j in range(1, 3)]:
                if super().put(name, x + dx, y + dy, check=check, allow_reserved=allow_reserved, owner=owner, force=force):
                    return True
            for r in range(2, 6):                       # дальше по кольцу — ближайшее свободное место
                for dx in range(-r, r + 1):
                    for dy in range(-r, r + 1):
                        if max(abs(dx), abs(dy)) == r and super().put(name, x + dx, y + dy, check=check,
                                                                       allow_reserved=False, owner=owner):
                            return True
            print(f"   {self.id}: «{name}» после увеличения не влезает у ({x}, {y}) — пропущен")
            return True
        if not ok and not self._loose:
            h = self.hides(name, x, y) if P.info(name)["block"] else None
            if h:
                raise AssertionError(f"{self.id}: «{name}» в ({x}, {y}) и «{h[0]}» в ({h[1]}, {h[2]}) "
                                     f"заслоняют друг друга картинками — передвиньте один из них")
            raise AssertionError(f"{self.id}: «{name}» не встаёт в ({x}, {y}) — занято, проход или перекрыл бы путь")
        return ok

    def fix_ladders(self):
        """Лестница стоит только у стены (по ней лезут наверх/вниз вдоль стены). Посреди пола — это люк
        с лестницей вниз, а на улице — крышка колодца/шахты: x_ladder заменяется на x_manhole."""
        for e in self.props:
            if e[0] != "x_ladder":
                continue
            x, y = e[1], e[2]
            above = self.ground[y - 1][x] if y > 0 else "_"
            wall = above == "_" or above in self.walls or above == "x" or (x, y - 1) in self.blocked
            if not wall:
                e[0] = "x_manhole"

    def _near_scaled(self, x, y, r=6):
        """Рядом стоит декорация, увеличенная под рост героя (data/prop_scale.json)."""
        return any(P.world_scale(p[0]) != 1 and abs(p[1] - x) <= r and abs(p[2] - y) <= r for p in self.props)

    def _loosely(self, fn, *a, **kw):
        self._loose += 1
        try:
            return fn(*a, **kw)
        finally:
            self._loose -= 1

    def scatter(self, *a, **kw):
        return self._loosely(super().scatter, *a, **kw)

    def grow(self, *a, **kw):
        return self._loosely(super().grow, *a, **kw)

    def hwall(self, *a, **kw):
        return self._loosely(super().hwall, *a, **kw)

    def wall_row(self, *a, **kw):
        return self._loosely(super().wall_row, *a, **kw)

    def building(self, x0, y0, w, h, style, south=(), *a, **kw):
        out = self._loosely(super().building, x0, y0, w, h, style, south, *a, **kw)
        if south:                                   # в проёме — дверь (створка на каждую клетку), а не дыра в стене
            self.city.prop("x_door", "pk:west/p2/12,6,1,2", block=False, layer="floor")
            for off in south:
                for dx in (0, 1):
                    self.props.append(["x_door", x0 + off + dx, y0 + h - 1])
        return out

    def dress_empty(self, *a, **kw):
        return self._loosely(super().dress_empty, *a, **kw)

    def maybe(self, name, x, y, **kw):
        """Необязательный объект: встанет — хорошо, нет — пропускается."""
        return self._loosely(self.put, name, x, y, **kw)

    # -------------------------------------------------------- объекты наборов
    def thing(self, name, img, x, y, foot=None, block=True, sight=False, check=True, layer=None, **extra):
        """Объект набора: регистрирует картинку в каталоге города и ставит на карту."""
        self.city.prop(name, img, foot=foot, block=block, sight=sight, layer=layer, **extra)
        return self.put(name, x, y, check=check)

    def stamp(self, name, img, x, y, water=True, soft=None):
        """Кусок страницы набора как плоская земля (рисуется под всем). Клетки, где больше половины —
        вода (голубое), непроходимы и закрывают проход, но не обзор. soft — края тают в землю (по умолчанию —
        у воды на улице: оазис и озеро не обрываются прямоугольником)."""
        pond = soft is None and water and not self.interior
        extra = {"soft": "pond"} if pond else {"soft": True} if soft else {}
        self.city.prop(name, img, block=False, layer="floor", foot=_cells(img), **extra)
        if soft and not water:                       # воронка/пятно — не под домом, ракетой, ящиком
            fw, fh = P.info(name)["size"][0] // T, P.info(name)["size"][1] // T
            busy = set(self.blocked) | set(self.reserved)
            for e in self.props:
                if P.CATALOG.get(e[0], {}).get("layer") != "floor":
                    busy.update(self.footprint(e[0], e[1], e[2]))
            ok = None
            for r in range(0, 7):
                for dx in range(-r, r + 1):
                    for dy in range(-r, r + 1):
                        if max(abs(dx), abs(dy)) != r:
                            continue
                        area = {(x + dx + i, y + dy + j) for i in range(-1, fw + 1) for j in range(-1, fh + 1)}
                        if not area & busy and 0 <= x + dx and x + dx + fw < self.W and 0 <= y + dy and y + dy + fh < self.H:
                            ok = (x + dx, y + dy)
                            break
                    if ok:
                        break
                if ok:
                    break
            if not ok:
                return
            x, y = ok
            self.reserve(x, y, x + fw - 1, y + fh - 1)   # потом сюда не встанет ни дом, ни камень
        self.props.append([name, x, y])
        if water:
            if not hasattr(self, "_water"):
                self._water = set()
            cells = self.city.water_cells(img)
            if pond:                       # вода — только внутри пятна пруда (берег проходим)
                w, h = P.pack_image(img).get_size()
                dist = P.pond_mask(w, h, seed=w * 7 + h)
                cells = [(cx, cy) for cx, cy in cells if dist(cx * T + T / 2, cy * T + T / 2) > 9]
            for cx, cy in cells:
                self.blocked.add((x + cx, y + cy))
                self._water.add((x + cx, y + cy))
            self._reach = None

    # -------------------------------------------------------- запись
    def gate(self, name, x, y, flag, msg, key=None):
        """Гермодверь/бронедверь: объект-дверь, закрытый, пока не поставлен флаг (пульт, ключ, динамит)."""
        assert self.put(name, x, y, check=False, allow_reserved=True), f"дверь {name} не встала в {x, y}"
        if not hasattr(self, "gates"):
            self.gates = []
        self.gates.append({"prop": len(self.props) - 1, "flag": flag, "msg": msg, **({"key": key} if key else {})})

    def gate_tiles(self):
        return [t for g in getattr(self, "gates", []) for t in self.footprint(*self.props[g["prop"]])]

    def extra(self):
        out = {"floors": self.floors, "walls": self.walls}
        if getattr(self, "gates", None):
            out["gates"] = self.gates
        if self.night:
            out["night"] = self.night
        if self.walk_zones:
            out["walk_zones"] = {k: list(v) for k, v in self.walk_zones.items()}
        if self.folk_spots:
            out["folk_spots"] = {k: ([list(t) for t in v] if k.startswith("critter:") else list(v))
                                 for k, v in self.folk_spots.items()}
        if getattr(self, "lights", None):
            out["lights"] = self.lights               # потолочные светильники без картинки: [x, y, радиус, [r,g,b], мерцание] в пикселях
        if self.tint:
            out["tint"] = self.tint
        if getattr(self, "ring_spot", None):
            out["ring_spot"] = list(self.ring_spot)
        if getattr(self, "crisp", False):
            out["crisp"] = True
        if getattr(self, "piers", None):
            out["piers"] = list(self.piers)
        if getattr(self, "not_water", None):
            out["not_water"] = sorted(self.not_water)       # тёмный синеватый пол — не вода, берег ему не рисуется
        if getattr(self, "cave_style", False):
            out["style"] = "cave"                  # стены — скальные фасады из набора пещер
        elif getattr(self, "cliff_style", False):
            out["style"] = "cliff"                 # каньон: песчаное плато и обрыв из валунов общим контуром
        if self.blocked_extra():
            out["blocked"] = self.blocked_extra()
        return out

    def ceiling(self, x, y, r=170, color=(255, 190, 110), flick=0.04):
        """Потолочный светильник над клеткой (x, y): круг света без предмета."""
        if not hasattr(self, "lights"):
            self.lights = []
        self.lights.append([x * T + T // 2, y * T + T // 2, r, list(color), flick, "nh"])

    water_codes = ()   # коды земли, которые — вода (река, озеро): непроходимы в игре

    def blocked_extra(self):
        """Непроходимые клетки, которых не видно по объектам: вода в штампах и клетки с кодом воды."""
        cells = set(getattr(self, "_water", set())) | set(getattr(self, "solid_cells", set()))
        for y, row in enumerate(self.ground):
            for x, code in enumerate(row):
                if code in self.water_codes:
                    cells.add((x, y))
        return sorted([list(t) for t in cells])


def _cells(img):
    if img.startswith("pk:") and img.count("/") == 2:
        x, y, w, h = (int(v) for v in img.rsplit("/", 1)[1].split(","))
        return [w, h]
    return None


class City:
    def __init__(self, cid, title):
        self.id, self.title = cid, title
        self.maps, self.props = [], {}
        pygame.init()
        if pygame.display.get_surface() is None:
            pygame.display.set_mode((1, 1))

    def prop(self, name, img, foot=None, block=True, sight=False, layer=None, **extra):
        d = {"img": img, "block": block, "sight": sight}
        if foot:
            d["foot"] = list(foot)
        if layer:
            d["layer"] = layer
        d.update(extra)
        if name in self.props and self.props[name] != d:
            raise ValueError(f"объект {name} уже описан иначе")
        self.props[name] = d
        # сразу в каталог src/props — чтобы MapKit.put видел размеры и пятно
        from src import props as P
        P.CATALOG[name] = d

    def water_cells(self, img):
        from src import props as P
        surf = P.pack_image(img)
        out = []
        for cy in range(surf.get_height() // T):
            for cx in range(surf.get_width() // T):
                cell = surf.subsurface((cx * T, cy * T, T, T))
                blue = 0
                for py in range(2, T, 4):
                    for px in range(2, T, 4):
                        c = cell.get_at((px, py))
                        if c.a > 200 and c.b > c.r + 30 and c.b > 120:
                            blue += 1
                if blue > (T // 4) ** 2 * 0.5:
                    out.append((cx, cy))
        return out

    # -------------------------------------------------------- связи
    def door(self, outside, out_tile, inside, in_tile, label_in, label_out):
        """Дверь: на улице клетка out_tile ведёт внутрь (в in_tile), внутри — клетка ниже in_tile
        (порог у южной стены) ведёт обратно на улицу, на клетку под дверью."""
        ox, oy = out_tile
        ix, iy = in_tile
        outside.portal([out_tile], inside.id, (ix, iy - 1), label_in)
        inside.portal([(ix, iy)], outside.id, (ox, oy + 1), label_out)

    def stairs(self, a, a_tile, b, b_tile, label_ab, label_ba):
        """Лестница между уровнями: стоишь на клетке — переходишь на соседнюю с лестницей на другом уровне."""
        a.portal([a_tile], b.id, (b_tile[0], b_tile[1] + 1), label_ab)
        b.portal([b_tile], a.id, (a_tile[0], a_tile[1] + 1), label_ba)

    def road(self, a, a_tiles, b, b_tiles, label_ab, label_ba, step=(0, 0)):
        """Дорога между районами: край карты a (a_tiles) ведёт в b — на клетки b_tiles, сдвинутые на step."""
        a.portal(a_tiles, b.id, (b_tiles[0][0] + step[0], b_tiles[0][1] + step[1]), label_ab)
        b.portal(b_tiles, a.id, (a_tiles[0][0] - step[0], a_tiles[0][1] - step[1]), label_ba)

    # -------------------------------------------------------- запись
    def furnish_sparse(self):
        for m in self.maps:
            pass
        return self._furnish_sparse()

    def _furnish_sparse(self):
        """Голые интерьеры (меньше 4 объектов на 100 клеток пола) получают обстановку по стилю места:
        техзал (убежища, бункеры, лаборатории), жильё (салуны, ратуши, конторы), подземелье (стоки, туннели)."""
        TECH = ("vault", "fort_bunker", "ares", "nova_core", "poseidon7", "mariposa_lab", "vegas_tower", "vegas_vault",
                "vegas_zero", "vegas_bank", "boneyard_vt", "baker7")
        SEWER = ("hub_tunnels", "vegas_tunnels", "zzyzx_cistern", "drain")
        CAVE = ("aradesh_cave", "goodsprings_cave", "nipton_mine", "searchlight_mine")
        TECH = TECH + ("mariposa_vats",)
        home = [
            [("table_2", 0, 0), ("chair_0", 0, 1), ("chair_1", 1, 1)],
            [("shelf_wood", 0, 0), ("barrel_wood", 2, 0), ("sack", 0, 2)],
            [("sofa", 0, 0), ("round_table_42", 0, 2), ("armchair", 2, 2)],
            [("crate", 0, 0), ("crate_b", 1, 0), ("sack", 0, 1), ("barrel_wood", 2, 1)],
            [("table_3", 0, 0), ("stool_1", 2, 0), ("shelf_metal_tall", 3, 0)],
        ]
        sewer = [
            [("rubble_a", 0, 0), ("x_puddle", 2, 2), ("barrel_wood", 3, 0)],
            [("pile_scrap", 0, 0), ("x_puddle", 0, 2), ("sack", 3, 1)],
            [("rubble_heap", 0, 0), ("crate_b", 3, 1)],
            [("pile_bags", 0, 0), ("barrel_wood", 3, 0), ("x_puddle", 2, 2)],
        ]
        for m in self.maps:
            if not m.interior:
                continue
            walk = sum(1 for y in range(m.H) for x in range(m.W)
                       if m.ground[y][x] in m.floors and (x, y) not in m.blocked)
            if not walk:
                continue                                   # dress_empty занимает только пустые блоки 6×6 — большие голые залы
                                                           # получают обстановку и в густо заставленных картах
            if m.furnish is False:
                continue
            style = ("own" if m.furnish else "tech" if m.id.startswith(TECH) else "sewer" if m.id.startswith(SEWER)
                     else "cave" if m.id.startswith(CAVE) else "home")
            cave = [[("rock", 0, 0), ("stones_12", 2, 1)], [("bones_a" if "bones_a" in P.CATALOG else "r_bones", 0, 0), ("rock", 2, 0)],
                    [("stones_19", 0, 0), ("x_puddle", 1, 1)], [("crate_b", 0, 0), ("pickaxe", 1, 0), ("sack", 0, 1)]]
            scenes = {"own": lambda: m.furnish["scenes"],
                      "tech": lambda: tech_scenes(self, f"{self.id}_f"), "sewer": lambda: sewer, "cave": lambda: cave,
                      "home": lambda: home_scenes(self, f"{self.id}_f") + home}[style]()
            fl = "".join(m.floors) or m.ground[m.H // 2][m.W // 2]
            m.wall_strict = True            # автообстановка не встаёт перед доской, окном, плакатом
            n = m.dress_empty(scenes, ground=fl, block=6, margin=1, chance=0.75, max_uses=3)
            if style in ("home", "tech", "own") and 100 * len(m.props) / walk < 8:   # вдоль стен — как в настоящей комнате
                along = {"own": m.furnish and m.furnish.get("along"),
                         "home": (["shelf_wood", "wardrobe", "cabinet_small", "shelf_stuff_1", "glass_cabinet", "filecab_1"],
                                  ["barrel_wood", "crate", "sack", "crate_b"]),
                         "tech": (["locker_1", "locker_2", "locker_double", "metal_shelf", "filecab_2", "shelf_metal_tall"],
                                  ["crate", "barrel_wood", "toolbox_red", "canister"])}[style]
                if along:
                    n += m._loosely(m.furnish_walls, along[0], along[1], fl)
            small = [sc[:2] for sc in scenes]                 # участки поменьше — между жителями и у проходов
            n += m.dress_empty(small, ground=fl, block=4, margin=0, chance=0.6 if 100 * len(m.props) / walk < 4 else 0.35,
                               max_uses=4)
            m.wall_strict = False
            print(f"   {m.id}: обставлено ({style}) +{n}")

    def save(self, gap_exempt=()):
        from vaultkit import auto_ambient
        self.furnish_sparse()
        for _m in self.maps:
            auto_ambient(_m)                        # интерьеры без своего света получают фон и лампы (после обстановки)
        os.makedirs(os.path.join(ROOT, "data", "props"), exist_ok=True)
        with open(os.path.join(ROOT, "data", "props", f"{self.id}.json"), "w", encoding="utf-8") as f:
            json.dump({"props": self.props}, f, ensure_ascii=False, indent=0)
        loc_path = os.path.join(ROOT, "data", "locations.json")
        with open(loc_path, "r", encoding="utf-8") as f:
            locs = json.load(f)
        from vaultkit import tidy_lamps, exit_glow, clear_exits
        for m in self.maps:
            cx = clear_exits(m)
            if cx:
                print(f"   {m.id}: у выходов расчищено предметов — {cx}")
            tl = tidy_lamps(m)
            exit_glow(m)
            if tl[0] or tl[1]:
                print(f"   {m.id}: лампы — сдвинуто к стене {tl[0]}, заменено потолочным светом {tl[1]}")
            m.fix_ladders()
            reach = m.check(gap_exempt=gap_exempt, npc_enemy_gap=0 if m.interior else 6, passable=m.gate_tiles())
            m.save(os.path.join("data", "maps", f"{m.id}.json"), **m.extra())
            entry = {"name": m.name, "map": f"data/maps/{m.id}.json", "known": m.known, "music": m.music}
            if m.music_zones:
                entry["music_zones"] = m.music_zones
            if m.world_pos:
                entry["world_pos"] = list(m.world_pos)
            if m.interior:
                entry["underground"] = True
            old = locs.get(m.id, {})
            locs[m.id] = {**old, **entry}
            print(f"{m.id}: {m.W}×{m.H}, объектов {len(m.props)}, NPC {len(m.npcs)}, врагов {len(m.enemies)}, "
                  f"доступно клеток {len(reach)}")
        with open(loc_path, "w", encoding="utf-8") as f:
            json.dump(locs, f, ensure_ascii=False, indent=2)


def home_scenes(city, pre):
    """Жилая комната / салун / контора: стол со стульями на коврике, шкаф и часы у стены, растение в углу,
    бочки и ящики группой у входа в подсобку. Объекты — из набора wild-west (дерево) и базара (кадки)."""
    def P(n, img, **kw):
        name = f"{pre}_home_{n}"
        city.prop(name, img, **kw)
        return name
    rug = P("rug", "pk:west/west_2_060", block=False, layer="floor", keybg=True)
    table = P("table", "pk:west/west_2_000", foot=[2, 1])
    chair = P("chair", "pk:west/west_2_001")
    poker = P("poker", "pk:west/west_2_020", foot=[2, 1])
    shelf = P("shelf", "pk:west/west_2_110", sight=True)
    books = P("books", "pk:west/west_2_116", sight=True)
    clock = P("clock", "pk:west/west_2_019", sight=True)
    plant = P("plant", "pk:bazaar/bazaar_3_206")
    lamp = "lantern_lit"
    return [
        [(rug, 0, 1), (table, 0, 1), (chair, 2, 1), (chair, 0, 2)],
        [(rug, 1, 0), (poker, 1, 0), (chair, 0, 0), (chair, 3, 0)],
        [(shelf, 0, 0), (clock, 2, 0), (plant, 3, 0)],
        [(books, 0, 0), (lamp, 2, 0), (plant, 0, 2)],
        [("barrel_wood", 0, 0), ("crate", 1, 0), ("crate_b", 0, 1), ("sack", 2, 1)],
    ]


def tech_scenes(city, pre):
    """Сценки для пустых технических залов (хранилища, ядра, ангары, лаборатории): ряды серверных стоек,
    пульты, рабочие места с мониторами, огнетушитель. Объекты — из набора атомной станции (npower)."""
    def P(n, foot=(2, 1), **kw):
        name = f"{pre}_tech_{n}"
        city.prop(name, f"pk:npower/npower_{n}", foot=list(foot), sight=True, **kw)
        return name
    rack, rack2, rack3 = P("2_073"), P("2_079"), P("2_080")
    tall = P("2_042", foot=(1, 1))
    desk, desk2, desk3 = P("2_036"), P("2_047"), P("2_060")
    work, work2 = P("2_066"), P("2_074")
    fire = P("2_057", foot=(1, 1), scale=0.55)          # огнетушитель — по колено, не в рост
    glow = {"r": 70, "color": [120, 220, 160], "at": [0.5, 0.3], "flicker": 0.08}
    console = P("2_026", light=glow)
    return [
        [(rack, 0, 0), (rack2, 2, 0), (rack3, 4, 0), (tall, 0, 2)],
        [(desk, 0, 0), (desk2, 2, 0), (fire, 5, 0), (work, 0, 2)],
        [(console, 1, 1), (tall, 0, 0), (tall, 4, 0), (desk3, 3, 2)],
        [(work, 0, 0), (work2, 2, 0), (rack, 0, 2), (fire, 4, 2)],
        [(rack2, 0, 0), (rack3, 2, 0), (desk, 0, 2), (desk2, 2, 2)],
    ]
