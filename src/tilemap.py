"""
Тайловая карта локации.

Карта — текстовый файл (data/maps/*.txt), символ = тип клетки:
  '.'  земля (проходимо)          '#'  стена/руины (непроходимо)
  'P'  точка появления игрока
  предметы на земле (подбираются при касании) — см. PICKUP_TILES
  враги — см. ENEMY_TILES (типы описаны в data/enemies.json)
  'N'  NPC (какой именно — задаётся в data/locations.json)
  'X'  контейнер (ящик/сейф/заначка; содержимое — в data/locations.json)
  'D'  запертая дверь (открывается отмычкой или выламывается ломом)
  '>'  выход на карту мира
  '%'  терминал RobCo (какой — список terminals в data/locations.json)
"""
import pygame

from . import settings as S
from . import loader

# символ -> (предмет, количество)
PICKUP_TILES = {
    "$": ("лом", 1),
    "C": ("химикаты", 1),
    "T": ("ткань", 1),
    "A": ("патроны", 3),
    "G": ("самопал", 1),
}
ENEMY_TILES = {"m": "mutant", "r": "rat", "R": "raider", "B": "beetle", "g": "gang", "S": "boss",
               "k": "ratman", "K": "ratman_boss", "z": "rad_mutant"}
SOLID_TILES = "#XD%"   # стена, контейнер и закрытая дверь непроходимы


def load_map_file(path):
    with open(path, "r", encoding="utf-8") as f:
        rows = [line.rstrip("\n") for line in f if line.strip()]
    width = max(len(r) for r in rows)
    return [r.ljust(width, "#") for r in rows]


class MapBase:
    """Общее для карт любого вида (текстовая сетка — TileMap, город из объектов — TownMap).
    Остальной код игры общается с картой только через эти методы."""
    width = height = 0
    parallax = True  # под полупрозрачной землёй виден параллакс-фон

    @property
    def pixel_size(self):
        return self.width * S.TILE, self.height * S.TILE

    def is_wall(self, x, y):
        raise NotImplementedError

    def blocks_sight(self, x, y):
        """Закрывает ли клетка обзор (для линии огня)."""
        return self.is_wall(x, y)

    def is_exit(self, x, y):
        return False

    def solids_near(self, rect, margin=S.TILE):
        """Прямоугольники непроходимых клеток рядом с rect — для столкновений при ходьбе."""
        r = rect.inflate(margin * 2, margin * 2)
        out = []
        for ty in range(r.top // S.TILE, r.bottom // S.TILE + 1):
            for tx in range(r.left // S.TILE, r.right // S.TILE + 1):
                if self.is_wall(tx, ty):
                    out.append(pygame.Rect(tx * S.TILE, ty * S.TILE, S.TILE, S.TILE))
        return out

    def drawables(self, cam):
        """Объекты, которые рисуются вперемешку с персонажами: [(y для сортировки, картинка, позиция)]."""
        return []

    def add_pickup(self, pos, kind, count):
        self.pickups.append({"rect": pygame.Rect(pos[0], pos[1], S.TILE, S.TILE),
                             "kind": kind, "count": count})

    def adjacent(self, tiles, player_rect, reach=1):
        """Первая из клеток tiles рядом с игроком (по соседству, включая диагональ)."""
        px, py = player_rect.centerx // S.TILE, player_rect.centery // S.TILE
        for t in tiles:
            if max(abs(t[0] - px), abs(t[1] - py)) <= reach:
                return t
        return None

    terminals = ()  # [{"id": терминал, "tiles": клетки}]

    def terminal_near(self, player_rect):
        for t in self.terminals:
            if self.adjacent(t["tiles"], player_rect):
                return t
        return None

    def terminal_at(self, tile):
        return next((t for t in self.terminals if tuple(tile) in t["tiles"]), None)

    corpses = ()  # трупы — тоже контейнеры (с картинкой лежащего тела)

    def add_corpse(self, enemy, loot):
        """Тело врага остаётся на земле, добыча — на нём (обыскать)."""
        from .corpse import corpse_image
        if not isinstance(self.corpses, list):
            self.corpses = []
        img = corpse_image(enemy)
        rect = img.get_rect(center=(enemy.rect.centerx, enemy.rect.bottom - 6))
        tile = (enemy.rect.centerx // S.TILE, enemy.rect.centery // S.TILE)
        box = {"tile": tile, "tiles": [tile], "name": f"тело: {enemy.name}", "who": enemy.name, "loot": dict(loot),
               "owner": None, "requires": None, "opened": False, "corpse": {"img": img, "rect": rect}}
        self.corpses.append(box)
        self.containers.append(box)
        return box

    def corpse_at(self, world_pos):
        for c in reversed(self.corpses):
            r = c["corpse"]["rect"]
            if r.collidepoint(world_pos) and c["corpse"]["img"].get_at(
                    (world_pos[0] - r.x, world_pos[1] - r.y)).a > 40:
                return c
        return None

    def draw_corpses(self, surf, cam):
        for c in self.corpses:
            r = c["corpse"]["rect"]
            surf.blit(c["corpse"]["img"], (r.x - int(cam.x), r.y - int(cam.y)))

    def container_at(self, tile):
        """Контейнер, занимающий клетку (открыть можно и повторно — положить или добрать)."""
        return next((c for c in self.containers if tuple(tile) in c["tiles"]), None)

    def container_near(self, player_rect):
        """Контейнер вплотную к игроку (любой его клеткой); сначала — ещё не осмотренные."""
        for c in sorted(self.containers, key=lambda c: c["opened"]):
            if self.adjacent(c["tiles"], player_rect):
                return c
        return None

    def draw_pickups(self, surf, cam):
        cam_x, cam_y = int(cam.x), int(cam.y)
        for p in self.pickups:
            icon = loader.item_icon(p["kind"])
            surf.blit(icon, icon.get_rect(center=(p["rect"].centerx - cam_x, p["rect"].centery - cam_y)))

    def pickup_icon_rect(self, p):
        """Где на земле нарисована иконка предмета (в координатах мира)."""
        icon = loader.item_icon(p["kind"])
        return icon.get_rect(center=p["rect"].center)

    def pickup_at(self, world_pos):
        return next((p for p in self.pickups if self.pickup_icon_rect(p).inflate(8, 8).collidepoint(world_pos)), None)

    def pickup_near(self, player_rect):
        """Предмет под ногами или на соседней клетке."""
        for p in self.pickups:
            if self.adjacent([(p["rect"].x // S.TILE, p["rect"].y // S.TILE)], player_rect):
                return p
        return None

    def take_pickup(self, p, inventory, log_fn=None):
        """Подобрать предмет — только вручную (E или клик), автоподбора нет."""
        if p not in self.pickups:
            return
        self.pickups.remove(p)
        inventory.add(p["kind"], p["count"])
        if log_fn:
            log_fn(f"Подобрано: {p['kind']}" + (f" ×{p['count']}" if p["count"] > 1 else ""))


class TileMap(MapBase):
    def __init__(self, rows, npc_ids=None, containers=None, terminals=None):
        self.rows = [list(r) for r in rows]
        self.height = len(rows)
        self.width = len(rows[0]) if rows else 0
        self.pickups = []       # dict(rect, kind, count)
        self.player_spawn = (S.TILE, S.TILE)
        self.enemy_spawns = []  # (pos, enemy_type)
        self.npc_spawns = []    # (pos, npc_id)
        self.containers = []    # dict(tile, tiles, name, loot, owner, opened)
        self.doors = []         # (x, y) запертых дверей
        npc_ids = list(npc_ids or [])
        container_defs = list(containers or [])
        terminal_ids = list(terminals or [])
        self.terminals = []

        self.tile_ground = loader.load_tile(S.TILE_DIR, "ground", "ground", (S.TILE, S.TILE), (70, 60, 46))
        self.tile_wall = loader.load_tile(S.TILE_DIR, "wall", "wall", (S.TILE, S.TILE), (52, 46, 40))
        if S.GROUND_ALPHA < 255:
            self.tile_ground = self.tile_ground.copy()
            self.tile_ground.set_alpha(S.GROUND_ALPHA)

        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                px, py = x * S.TILE, y * S.TILE
                if ch == "X":
                    d = container_defs.pop(0) if container_defs else {}
                    self.containers.append({"tile": (x, y), "tiles": [(x, y)], "name": d.get("name", "ящик"),
                                            "loot": dict(d.get("loot", {})), "owner": d.get("owner"),
                                            "requires": d.get("requires"), "opened": False})
                elif ch == "%":
                    self.terminals.append({"id": terminal_ids.pop(0) if terminal_ids else None, "tiles": [(x, y)]})
                elif ch == "D":
                    self.doors.append((x, y))
                elif ch == "P":
                    self.player_spawn = (px, py)
                elif ch in ENEMY_TILES:
                    self.enemy_spawns.append(((px, py), ENEMY_TILES[ch]))
                elif ch == "N" and npc_ids:
                    self.npc_spawns.append(((px, py), npc_ids.pop(0)))
                elif ch in PICKUP_TILES:
                    kind, count = PICKUP_TILES[ch]
                    self.add_pickup((px, py), kind, count)

    def tile_at(self, x, y):
        if 0 <= y < self.height and 0 <= x < self.width:
            return self.rows[y][x]
        return "#"

    def is_wall(self, x, y):
        return self.tile_at(x, y) in SOLID_TILES

    def is_exit(self, x, y):
        return self.tile_at(x, y) == ">"

    def open_door(self, tile):
        x, y = tile
        self.rows[y][x] = "."
        self.doors.remove(tile)

    def draw(self, surf, cam):
        cam_x, cam_y = int(cam.x), int(cam.y)
        start_col = max(0, cam_x // S.TILE)
        start_row = max(0, cam_y // S.TILE)
        end_col = min(self.width, (cam_x + S.SCREEN_W) // S.TILE + 2)
        end_row = min(self.height, (cam_y + S.SCREEN_H) // S.TILE + 2)
        for y in range(start_row, end_row):
            for x in range(start_col, end_col):
                px, py = x * S.TILE - cam_x, y * S.TILE - cam_y
                ch = self.rows[y][x]
                surf.blit(self.tile_wall if ch == "#" else self.tile_ground, (px, py))
                if ch in "XD>%":
                    surf.blit(loader.special_tile(ch), (px, py))
        # предметы рисуем из списка, а не из карты — подобранные исчезают
        self.draw_pickups(surf, cam)
