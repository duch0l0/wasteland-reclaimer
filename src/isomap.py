"""
Изометрическая карта (data/maps/*.json с "iso": true, собирается tools/build_iso_town.py).

Для остальной игры это та же сетка клеток, что и у прямых карт: is_wall, контейнеры,
терминалы, выходы, порталы, трупы, предметы. Отличается только отрисовка:
  floor    — тайл пола в каждой клетке (id из assets/iso/tiles), рисуется ромбами сзади вперёд;
  objs     — всё, что стоит на клетках: стены на рёбрах клеток, машины, бочки, фонари…
             {t: тайл, x, y, k: сдвиг глубины, b: непроходимо, s: закрывает обзор,
              front: номер крыши, чья это передняя стена (изнутри она прозрачнеет),
              floor: плоское (рисуется с полом), dx/dy: сдвиг картинки};
  roofs    — крыши зданий: поднятые на высоту стен плиты, тают, когда герой внутри.

Порядок рисования — по «глубине» u + v (сумма координат клетки): что дальше от
зрителя, то раньше. Персонажи встают в тот же порядок по своей точке ног.
"""
import json

import pygame

from . import settings as S
from . import loader
from .iso import w2i, i2w, tile_center_iso, tile_image, TILE_ANCHOR, HW, HH
from .tilemap import MapBase

T = S.TILE
ROOF_LIFT = 132      # на сколько пикселей экрана крыша выше пола (высота стены набора)


# край крыши -> вариант плиты набора: A1 — парапет по стороне, A2 — угловой
ROOF_EDGE = {"n": "N", "e": "E", "w": "W", "s": "S"}
ROOF_CORNER = {("n", "w"): "W", ("n", "e"): "N", ("s", "e"): "E", ("s", "w"): "S"}


def _roof_tile(r, x, y):
    t = r["tiles"]
    side = {"n": y == r["y0"], "s": y == r["y1"], "w": x == r["x0"], "e": x == r["x1"]}
    for (a, b), v in ROOF_CORNER.items():
        if side[a] and side[b]:
            return t[f"corner_{v}"]
    for s_, v in ROOF_EDGE.items():
        if side[s_]:
            return t[f"edge_{v}"]
    return t["mid"]


def _paint_sign(img, r, origin):
    """Надпись белой краской по крыше, как на крышах в Fallout 2 («САЛУН», «КЛИНИКА»…),
    сжатая по вертикали вдвое и повёрнутая вдоль оси x — лежит на плоскости крыши."""
    text = r["sign"]
    mark = text[0] if text[0] in "+★" else None
    text = text[1:] if mark else text
    font = pygame.font.Font(None, 64)
    t = font.render(("✚ " if mark == "+" else "") + text, True, (225, 218, 196))
    # на плоскость: вдоль оси x клетки — это направление (64, 32) на экране (≈ 26.6°), высота букв сжата
    flat = pygame.transform.smoothscale(t, (t.get_width(), max(1, t.get_height() // 2)))
    flat = pygame.transform.rotate(flat, -26.57)
    flat.set_alpha(150)
    cx = (r["x0"] + r["x1"] + 1) / 2
    cy = (r["y0"] + r["y1"] + 1) / 2
    px, py = w2i(cx * T, cy * T)
    img.blit(flat, flat.get_rect(center=(px - origin[0], py - ROOF_LIFT - origin[1])))


class IsoMap(MapBase):
    parallax = False
    iso = True

    def __init__(self, path):
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        self.width, self.height = d["w"], d["h"]
        self.dark = d.get("dark", False)
        pal = d["palette"]
        self.floor = [[pal[i] if i >= 0 else None for i in row] for row in d["floor"]]
        self.ground = ["".join("." for _ in row) for row in d["floor"]]  # для миникарты и проверок
        self.blocked = {tuple(t) for t in d.get("blocked", [])}
        self.sight = {tuple(t) for t in d.get("sight", [])}
        self.exits = {tuple(t) for t in d.get("exits", [])}
        self.portals = [{"tiles": {tuple(t) for t in p["tiles"]}, "to": p["to"], "at": tuple(p["at"]),
                         "label": p.get("label", ""), "requires": p.get("requires")} for p in d.get("portals", [])]
        self.doors, self.gates = [], []
        self.pickups = []
        self.player_spawn = (d["player"][0] * T, d["player"][1] * T)
        self.enemy_spawns = [((x * T, y * T), kind) for kind, x, y in d.get("enemies", [])]
        self.npc_spawns = [((x * T, y * T), nid) for nid, x, y in d.get("npcs", [])]
        for item, count, x, y in d.get("pickups", []):
            self.add_pickup((x * T, y * T), item, count)

        self.objects = []
        for o in d["objs"]:
            img = tile_image(o["t"])
            cx, cy = tile_center_iso(o["x"], o["y"])
            rect = img.get_rect(topleft=(cx - TILE_ANCHOR[0] + o.get("dx", 0), cy - TILE_ANCHOR[1] + o.get("dy", 0)))
            obj = {"name": o["t"], "img": img, "rect": rect, "tile": (o["x"], o["y"]), "foot": [(o["x"], o["y"])],
                   "key": o["x"] + o["y"] + o.get("k", 1.0), "floor": o.get("floor", False),
                   "front": o.get("front"), "container": None}
            if o.get("b"):
                self.blocked.add((o["x"], o["y"]))
            if o.get("s"):
                self.sight.add((o["x"], o["y"]))
            self.objects.append(obj)

        self.containers = []
        for c in d.get("containers", []):
            obj = self.objects[c["obj"]]
            box = {"tile": obj["tile"], "tiles": [obj["tile"]], "name": c["name"], "loot": dict(c["loot"]),
                   "owner": c.get("owner"), "requires": c.get("requires"), "opened": False, "obj": obj,
                   "on_put": c.get("on_put")}
            obj["container"] = box
            self.containers.append(box)
        self.terminals = []
        for t in d.get("terminals", []):
            obj = self.objects[t["obj"]]
            term = {"id": t["id"], "tiles": [obj["tile"]], "obj": obj}
            obj["terminal"] = term
            self.terminals.append(term)

        # толпы гулей в домах (экшен): подошёл к зоне — из двери вываливаются
        self.hordes = [{**h, "done": False} for h in d.get("hordes", [])]

        self.roofs = []
        for i, r in enumerate(d.get("roofs", [])):
            self.roofs.append({**r, "alpha": 255.0, "img": None, "pos": None,
                               "key": r["x1"] + r["y1"] + 2.2})

    # ------------------------------------------------------------ клетки
    def is_wall(self, x, y):
        if not (0 <= x < self.width and 0 <= y < self.height):
            return True
        return (x, y) in self.blocked or self.floor[y][x] is None

    def blocks_sight(self, x, y):
        return not (0 <= x < self.width and 0 <= y < self.height) or (x, y) in self.sight

    def is_exit(self, x, y):
        return (x, y) in self.exits

    def portal_at(self, x, y):
        return next((p for p in self.portals if (x, y) in p["tiles"]), None)

    def tile_at(self, x, y):
        return "#" if self.is_wall(x, y) else "."

    def gate_at(self, tile):
        return None

    def remove_object(self, obj):
        obj["hidden"] = True
        self.blocked.discard(obj["tile"])
        self.sight.discard(obj["tile"])

    # ------------------------------------------------------------ крыши
    def roof_over(self, tile):
        x, y = tile
        return next((r for r in self.roofs if r["x0"] <= x <= r["x1"] and r["y0"] <= y <= r["y1"]), None)

    def update_roofs(self, player_tile, dt_ms):
        inside = self.roof_over(player_tile)
        for r in self.roofs:
            target = 0.0 if r is inside else 255.0
            step = dt_ms * 1.4
            r["alpha"] = min(target, r["alpha"] + step) if r["alpha"] < target else max(target, r["alpha"] - step)

    def _roof_image(self, r):
        """Крыша целиком: плиты по всем клеткам здания, на высоте стен; парапет по краю."""
        cells = [(x, y) for y in range(r["y0"], r["y1"] + 1) for x in range(r["x0"], r["x1"] + 1)]
        pts = [tile_center_iso(x, y) for x, y in cells]
        x0 = min(p[0] for p in pts) - TILE_ANCHOR[0]
        y0 = min(p[1] for p in pts) - TILE_ANCHOR[1] - ROOF_LIFT
        x1 = max(p[0] for p in pts) + TILE_ANCHOR[0]
        y1 = max(p[1] for p in pts) + (256 - TILE_ANCHOR[1]) - ROOF_LIFT
        img = pygame.Surface((int(x1 - x0) + 2, int(y1 - y0) + 2), pygame.SRCALPHA)
        for (x, y), (cx, cy) in sorted(zip(cells, pts), key=lambda c: c[0][0] + c[0][1]):
            tile = tile_image(_roof_tile(r, x, y))
            img.blit(tile, (cx - TILE_ANCHOR[0] - x0, cy - TILE_ANCHOR[1] - ROOF_LIFT - y0))
        if r.get("sign"):   # надпись краской по крыше, вдоль длинной стороны
            _paint_sign(img, r, (x0, y0))
        r["pos"] = (x0, y0)
        return img

    # ------------------------------------------------------------ отрисовка
    def _visible(self, rect, cam, size):
        return rect.colliderect(pygame.Rect(cam.x - 20, cam.y - 20, size[0] + 40, size[1] + 40))

    def draw(self, surf, cam):
        """Пол сзади вперёд, плоские объекты (решётки, лужи крови), предметы на земле."""
        sw, sh = surf.get_size()
        view = pygame.Rect(cam.x - 130, cam.y - 260, sw + 260, sh + 520)
        # клетки, попадающие в экран: по диагоналям u+v, внутри — по u
        (tlx, tly), (brx, bry) = (cam.x, cam.y), (cam.x + sw, cam.y + sh)
        smin = int((tly - 64) / HH) - 1
        smax = int((bry + 300) / HH) + 1
        for s in range(max(0, smin), min(self.width + self.height - 1, smax) + 1):
            for x in range(max(0, s - self.height + 1), min(self.width - 1, s) + 1):
                y = s - x
                tid = self.floor[y][x]
                if tid is None:
                    continue
                cx, cy = tile_center_iso(x, y)
                if not view.collidepoint(cx, cy):
                    continue
                surf.blit(tile_image(tid), (cx - TILE_ANCHOR[0] - cam.x, cy - TILE_ANCHOR[1] - cam.y))
        for o in self.objects:
            if o["floor"] and not o.get("hidden") and o["rect"].colliderect(view):
                surf.blit(o["img"], (o["rect"].x - cam.x, o["rect"].y - cam.y))
        self._draw_ways(surf, cam)
        self.draw_pickups(surf, cam)

    def _draw_ways(self, surf, cam):
        """Выходы на карту мира и переходы в другие районы — жёлтые ромбы на земле со стрелкой."""
        cells = [(t, True) for t in self.exits] + [(t, not p.get("requires")) for p in self.portals for t in p["tiles"]]
        for (x, y), open_ in cells:
            pts = [cam.p(x * T + a, y * T + b) for a, b in ((6, 6), (T - 6, 6), (T - 6, T - 6), (6, T - 6))]
            color = (240, 200, 90) if open_ else (150, 120, 170)
            pygame.draw.polygon(surf, color, pts, 2)
            cx, cy = cam.p(x * T + T / 2, y * T + T / 2)
            pygame.draw.circle(surf, color, (int(cx), int(cy)), 4)

    def drawables(self, cam, size=None):
        size = size or (S.SCREEN_W, S.SCREEN_H)
        out = []
        for o in self.objects:
            if o["floor"] or o.get("hidden") or not self._visible(o["rect"], cam, size):
                continue
            img = o["img"]
            c = o["container"]
            if c is not None and c["opened"] and not c["loot"]:
                img = img.copy()
                img.fill((150, 140, 130, 255), special_flags=pygame.BLEND_RGBA_MULT)
            if o["front"] is not None:   # передняя стена здания, где стоит герой, — полупрозрачная
                a = self.roofs[o["front"]]["alpha"]
                if a < 255:
                    img = img.copy()
                    img.set_alpha(int(70 + 185 * a / 255))
            out.append((o["key"], img, (o["rect"].x - cam.x, o["rect"].y - cam.y)))
        for r in self.roofs:
            if r["alpha"] <= 1:
                continue
            if r["img"] is None:
                r["img"] = self._roof_image(r)
            img = r["img"]
            if r["alpha"] < 255:
                img = img.copy()
                img.set_alpha(int(r["alpha"]))
            out.append((r["key"], img, (r["pos"][0] - cam.x, r["pos"][1] - cam.y)))
        return out

    @staticmethod
    def entity_key(ent):
        """Глубина персонажа — как у клетки, где его ноги (u + v)."""
        return (ent.rect.centerx + ent.rect.bottom - T // 2) / T

    def iso_bounds(self):
        """Прямоугольник всей карты в изометрическом пространстве."""
        xs = [w2i(0, self.height * T)[0], w2i(self.width * T, 0)[0]]
        return pygame.Rect(xs[0] - HW, -300, xs[1] - xs[0] + 2 * HW, w2i(self.width * T, self.height * T)[1] + 400)

    # ------------------------------------------------------------ предметы, тела, клики
    def draw_pickups(self, surf, cam):
        for p in self.pickups:
            icon = loader.item_icon(p["kind"])
            surf.blit(icon, icon.get_rect(center=cam.p(*p["rect"].center)))

    def pickup_screen_rect(self, p, cam):
        return loader.item_icon(p["kind"]).get_rect(center=cam.p(*p["rect"].center))

    def draw_corpses(self, surf, cam):
        for c in self.corpses:
            cc = c["corpse"]
            fx, fy = cam.p(*cc["foot"])
            surf.blit(cc["img"], (fx - cc["anchor"][0], fy - cc["anchor"][1]))

    def add_corpse(self, enemy, loot):
        box = super().add_corpse(enemy, loot)
        anim = enemy.anim
        foot = getattr(anim, "foot", None)
        cc = box["corpse"]
        cc["foot"] = (enemy.rect.centerx, enemy.rect.bottom - T // 2 + 2)
        if foot:   # изометрический персонаж: последний кадр смерти, стоит там же, где стоял
            frames = anim.frames_by_action.get(f"die_{anim.direction}")
            if frames:
                cc["img"] = frames[-1]
            cc["anchor"] = foot
        else:
            cc["anchor"] = (cc["img"].get_width() // 2, cc["img"].get_height() // 2 + 6)
        return box

    def corpse_at(self, world_pos):
        tile = (int(world_pos[0]) // T, int(world_pos[1]) // T)
        return next((c for c in reversed(self.corpses) if c["tile"] == tile), None)

    def corpse_screen_rect(self, c, cam):
        cc = c["corpse"]
        fx, fy = cam.p(*cc["foot"])
        return cc["img"].get_rect(topleft=(fx - cc["anchor"][0], fy - cc["anchor"][1]))

    def _sprite_hit(self, world_pos, key):
        ix, iy = w2i(*world_pos)
        hits = [o for o in self.objects if o.get(key) and not o.get("hidden") and o["rect"].collidepoint(ix, iy)]
        for o in sorted(hits, key=lambda o: -o["key"]):
            if o["img"].get_at((int(ix - o["rect"].x), int(iy - o["rect"].y))).a > 40:
                return o[key]
        return None

    def container_sprite_at(self, world_pos):
        return self._sprite_hit(world_pos, "container")

    def terminal_sprite_at(self, world_pos):
        return self._sprite_hit(world_pos, "terminal")
