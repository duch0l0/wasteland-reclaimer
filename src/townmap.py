"""
Карта из объектов (data/maps/*.json, собирается tools/build_town.py).

  ground   — строки кодов земли: d земля, a асфальт, h/v разметка, g гравий, c бетонный пол;
  decals   — плоские пятна на земле [имя, px, py] (центр в пикселях мира);
  props    — объекты [имя, x, y]: x, y — левая верхняя клетка пятна на земле;
  containers — какие объекты обыскиваются и что в них лежит;
  player, exits, enemies, npcs, pickups — точки появления и выходы.

Объекты рисуются вперемешку с персонажами по нижнему краю пятна (кто ниже —
тот ближе к камере), поэтому за высоким шкафом или палаткой можно спрятаться.
Пятна непроходимы, «высокие» объекты (sight) ещё и закрывают обзор в бою.
"""
import json
import os
import random

import pygame

from . import settings as S
from . import loader
from . import props as P
from .tilemap import MapBase

T = S.TILE
GROUND_DIR = os.path.join("assets", "town", "ground")


def _dirt_tiles(n=6):
    """Бесшовная земля: пиксельный шум в цветах пятен земли из набора (dirt_patch)."""
    src = pygame.image.load(os.path.join(P.PROPS_DIR, "p1_dirt_patch.png"))
    colors = []
    for y in range(0, src.get_height(), 3):
        for x in range(0, src.get_width(), 3):
            c = src.get_at((x, y))
            if c.a == 255 and 40 < sum(c[:3]) / 3 < 150:
                colors.append(tuple(c[:3]))
    colors.sort(key=sum)
    body = colors[len(colors) // 8: len(colors) * 7 // 8]  # без самых тёмных и светлых пятен
    tiles = []
    rnd = random.Random(11)
    for _ in range(n):
        t = pygame.Surface((T, T))
        for y in range(0, T, 2):  # пиксели 2×2 — в тон пиксель-арту
            for x in range(0, T, 2):
                t.fill(rnd.choice(body), (x, y, 2, 2))
        for _ in range(3):  # пара камешков
            x, y = rnd.randrange(2, T - 4, 2), rnd.randrange(2, T - 4, 2)
            t.fill(colors[-rnd.randrange(1, len(colors) // 10 + 2)], (x, y, 2, 2))
            t.fill(colors[rnd.randrange(0, len(colors) // 10 + 1)], (x, y + 2, 2, 2))
        tiles.append(t)
    return tiles


class TownMap(MapBase):
    parallax = False  # земля сплошная — фон под ней не нужен

    def __init__(self, path):
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        self.width, self.height = d["w"], d["h"]
        self.ground = d["ground"]
        self.blocked, self.sight = set(), set()
        self.exits = {tuple(t) for t in d.get("exits", [])}
        self.doors = []
        self.pickups = []
        self.player_spawn = (d["player"][0] * T, d["player"][1] * T)
        self.enemy_spawns = [((x * T, y * T), kind) for kind, x, y in d.get("enemies", [])]
        self.npc_spawns = [((x * T, y * T), nid) for nid, x, y in d.get("npcs", [])]
        for item, count, x, y in d.get("pickups", []):
            self.add_pickup((x * T, y * T), item, count)

        self.decals = []  # (картинка, rect в мире)
        for name, px, py in d.get("decals", []):
            img = P.image(name)
            self.decals.append((name, img.get_rect(center=(px, py))))

        self.objects = []  # dict(name, rect картинки в мире, sort_y, container)
        for name, x, y in d["props"]:
            inf = P.info(name)
            fw, fh = inf["foot"]
            foot = [(x + i, y + j) for i in range(fw) for j in range(fh)]
            if inf["block"]:
                self.blocked.update(foot)
            if inf["sight"]:
                self.sight.update(foot)
            bottom = (y + fh) * T
            rect = pygame.Rect(0, 0, *inf["size"])
            rect.midbottom = ((x + fw / 2) * T, bottom)
            self.objects.append({"name": name, "rect": rect, "sort_y": bottom, "foot": foot,
                                 "container": None, "floor": inf["layer"] == "floor"})

        self.containers = []
        for c in d.get("containers", []):
            obj = self.objects[c["prop"]]
            box = {"tile": obj["foot"][0], "tiles": obj["foot"], "name": c["name"], "loot": dict(c["loot"]),
                   "owner": c.get("owner"), "requires": c.get("requires"), "opened": False, "obj": obj}
            obj["container"] = box
            self.containers.append(box)

        self._dirt = _dirt_tiles()
        self._tiles = {"a": [], "g": []}
        for f in sorted(os.listdir(GROUND_DIR)):
            if f.startswith("asphalt_") and f[8:-4].isdigit():
                self._tiles["a"].append(pygame.image.load(os.path.join(GROUND_DIR, f)).convert())
            elif f.startswith("gravel_"):
                self._tiles["g"].append(pygame.image.load(os.path.join(GROUND_DIR, f)).convert())
        # бетонный пол в зданиях — асфальт, чуть светлее и теплее
        self._tiles["c"] = []
        for t in self._tiles["a"]:
            c = t.copy()
            c.fill((235, 222, 205), special_flags=pygame.BLEND_RGB_MULT)
            c.fill((18, 14, 8), special_flags=pygame.BLEND_RGB_ADD)
            self._tiles["c"].append(c)
        # земля пятнами: три оттенка, участки выбираются плавным шумом
        self._dirt_shades = []
        for mul in ((236, 232, 226), (245, 242, 237), (255, 255, 255), (255, 250, 243), (255, 245, 232)):
            shade = []
            for t in self._dirt:
                c = t.copy()
                c.fill(mul, special_flags=pygame.BLEND_RGB_MULT)
                shade.append(c)
            self._dirt_shades.append(shade)
        line = pygame.image.load(os.path.join(GROUND_DIR, "asphalt_line.png")).convert()
        self._tiles["v"] = [line]
        self._tiles["h"] = [pygame.transform.rotate(line, 90)]

        self.terminals = []
        for t in d.get("terminals", []):
            obj = self.objects[t["prop"]]
            term = {"id": t["id"], "tiles": obj["foot"], "obj": obj}
            obj["terminal"] = term
            self.terminals.append(term)

    # ------------------------------------------------------------ клетки
    def is_wall(self, x, y):
        if not (0 <= x < self.width and 0 <= y < self.height):
            return True
        return (x, y) in self.blocked

    def blocks_sight(self, x, y):
        return not (0 <= x < self.width and 0 <= y < self.height) or (x, y) in self.sight

    def is_exit(self, x, y):
        return (x, y) in self.exits

    def tile_at(self, x, y):
        return "#" if self.is_wall(x, y) else "."

    # ------------------------------------------------------------ контейнеры
    def terminal_sprite_at(self, world_pos):
        for o in sorted(self.objects, key=lambda o: -o["sort_y"]):
            if o.get("terminal") and o["rect"].collidepoint(world_pos):
                img = P.image(o["name"])
                if img.get_at((world_pos[0] - o["rect"].x, world_pos[1] - o["rect"].y)).a > 40:
                    return o["terminal"]
        return None

    def container_sprite_at(self, world_pos):
        """Закрытый контейнер, по картинке которого пришёлся клик (передний первым)."""
        hits = [o for o in self.objects if o["container"] and not o["container"]["opened"]
                and o["rect"].collidepoint(world_pos)]
        for o in sorted(hits, key=lambda o: -o["sort_y"]):
            img = P.image(o["name"])
            if img.get_at((world_pos[0] - o["rect"].x, world_pos[1] - o["rect"].y)).a > 40:
                return o["container"]
        return None

    # ------------------------------------------------------------ отрисовка
    def _ground_tile(self, x, y):
        code = self.ground[y][x]
        h = (x * 73856093) ^ (y * 19349663)  # один и тот же вариант клетки при каждом кадре
        if code in self._tiles and self._tiles[code]:
            variants = self._tiles[code]
        else:
            variants = self._dirt_shades[self._shade(x, y)]
        return variants[h % len(variants)]

    @staticmethod
    def _noise(x, y):
        h = (x * 374761393 + y * 668265263) & 0xFFFFFFFF
        h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
        return (h & 0xFFFF) / 0xFFFF

    def _shade(self, x, y):
        """Плавный шум по крупной сетке 6×6 клеток: участки земли чуть светлее/темнее (5 ступеней)."""
        gx, gy = x / 6, y / 6
        ix, iy = int(gx), int(gy)
        fx, fy = gx - ix, gy - iy
        n = (self._noise(ix, iy) * (1 - fx) * (1 - fy) + self._noise(ix + 1, iy) * fx * (1 - fy)
             + self._noise(ix, iy + 1) * (1 - fx) * fy + self._noise(ix + 1, iy + 1) * fx * fy)
        return min(4, int(n * 5))

    def draw(self, surf, cam):
        cam_x, cam_y = int(cam.x), int(cam.y)
        view = pygame.Rect(cam_x, cam_y, S.SCREEN_W, S.SCREEN_H)
        x0, y0 = max(0, cam_x // T), max(0, cam_y // T)
        x1 = min(self.width, (cam_x + S.SCREEN_W) // T + 1)
        y1 = min(self.height, (cam_y + S.SCREEN_H) // T + 1)
        for y in range(y0, y1):
            for x in range(x0, x1):
                surf.blit(self._ground_tile(x, y), (x * T - cam_x, y * T - cam_y))
        for name, rect in self.decals:
            if rect.colliderect(view):
                surf.blit(P.image(name), (rect.x - cam_x, rect.y - cam_y))
        for o in self.objects:
            if o["floor"] and o["rect"].colliderect(view):
                surf.blit(P.image(o["name"]), (o["rect"].x - cam_x, o["rect"].y - cam_y))
        for (x, y) in self.exits:
            if x0 <= x < x1 and y0 <= y < y1:
                surf.blit(self._exit_arrow(x, y), (x * T - cam_x, y * T - cam_y))
        self.draw_pickups(surf, cam)

    def _exit_arrow(self, x, y):
        """Стрелки выхода смотрят наружу, к краю карты."""
        arrow = loader.special_tile(">")
        if x == 0:
            return pygame.transform.flip(arrow, True, False)
        if y == self.height - 1:
            return pygame.transform.rotate(arrow, -90)
        if y == 0:
            return pygame.transform.rotate(arrow, 90)
        return arrow

    def drawables(self, cam):
        cam_x, cam_y = int(cam.x), int(cam.y)
        view = pygame.Rect(cam_x, cam_y, S.SCREEN_W, S.SCREEN_H)
        out = []
        for o in self.objects:
            if o["floor"] or not o["rect"].colliderect(view):
                continue
            opened = o["container"] is not None and o["container"]["opened"]
            out.append((o["sort_y"], P.image(o["name"], darken=opened), (o["rect"].x - cam_x, o["rect"].y - cam_y)))
        return out
