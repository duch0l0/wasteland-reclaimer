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

import pygame

T = 48


class CityMap(MapKit):
    def __init__(self, city, mid, name, w, h, start, seed=1, fill="d", night=None, music="desert",
                 interior=False, known=False, world_pos=None):
        super().__init__(w, h, start, seed, fill="_" if interior else fill)
        self.city, self.id, self.name = city, mid, name
        self.floors, self.walls = {}, {}
        self.night, self.music, self.interior = night, music, interior
        self.known, self.world_pos = known, world_pos
        self.tint = None
        city.maps.append(self)

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
        if not ok and not self._loose:
            raise AssertionError(f"{self.id}: «{name}» не встаёт в ({x}, {y}) — занято, проход или перекрыл бы путь")
        return ok

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

    def building(self, *a, **kw):
        return self._loosely(super().building, *a, **kw)

    def maybe(self, name, x, y, **kw):
        """Необязательный объект: встанет — хорошо, нет — пропускается."""
        return self._loosely(self.put, name, x, y, **kw)

    # -------------------------------------------------------- объекты наборов
    def thing(self, name, img, x, y, foot=None, block=True, sight=False, check=True, layer=None, **extra):
        """Объект набора: регистрирует картинку в каталоге города и ставит на карту."""
        self.city.prop(name, img, foot=foot, block=block, sight=sight, layer=layer, **extra)
        return self.put(name, x, y, check=check)

    def stamp(self, name, img, x, y, water=True):
        """Кусок страницы набора как плоская земля (рисуется под всем). Клетки, где больше половины —
        вода (голубое), непроходимы и закрывают проход, но не обзор."""
        self.city.prop(name, img, block=False, layer="floor", foot=_cells(img))
        self.props.append([name, x, y])
        if water:
            if not hasattr(self, "_water"):
                self._water = set()
            for cx, cy in self.city.water_cells(img):
                self.blocked.add((x + cx, y + cy))
                self._water.add((x + cx, y + cy))
            self._reach = None

    # -------------------------------------------------------- запись
    def extra(self):
        out = {"floors": self.floors, "walls": self.walls}
        if self.night:
            out["night"] = self.night
        if self.tint:
            out["tint"] = self.tint
        if self.blocked_extra():
            out["blocked"] = self.blocked_extra()
        return out

    def blocked_extra(self):
        """Непроходимые клетки, которых не видно по объектам (вода в штампах)."""
        return sorted([list(t) for t in getattr(self, "_water", set())])


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
    def save(self, gap_exempt=()):
        os.makedirs(os.path.join(ROOT, "data", "props"), exist_ok=True)
        with open(os.path.join(ROOT, "data", "props", f"{self.id}.json"), "w", encoding="utf-8") as f:
            json.dump({"props": self.props}, f, ensure_ascii=False, indent=0)
        loc_path = os.path.join(ROOT, "data", "locations.json")
        with open(loc_path, "r", encoding="utf-8") as f:
            locs = json.load(f)
        for m in self.maps:
            reach = m.check(gap_exempt=gap_exempt, npc_enemy_gap=0 if m.interior else 6)
            m.save(os.path.join("data", "maps", f"{m.id}.json"), **m.extra())
            entry = {"name": m.name, "map": f"data/maps/{m.id}.json", "known": m.known, "music": m.music}
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
