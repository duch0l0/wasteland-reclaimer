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
SOLID_TILES = "#XD"   # стена, контейнер и закрытая дверь непроходимы


def load_map_file(path):
    with open(path, "r", encoding="utf-8") as f:
        rows = [line.rstrip("\n") for line in f if line.strip()]
    width = max(len(r) for r in rows)
    return [r.ljust(width, "#") for r in rows]


class TileMap:
    def __init__(self, rows, npc_ids=None, containers=None):
        self.rows = [list(r) for r in rows]
        self.height = len(rows)
        self.width = len(rows[0]) if rows else 0
        self.solid_rects = []
        self.pickups = []       # dict(rect, kind, count)
        self.player_spawn = (S.TILE, S.TILE)
        self.enemy_spawns = []  # (pos, enemy_type)
        self.npc_spawns = []    # (pos, npc_id)
        self.containers = []    # dict(tile, name, loot, owner, opened)
        self.doors = []         # (x, y) запертых дверей
        npc_ids = list(npc_ids or [])
        container_defs = list(containers or [])

        self.tile_ground = loader.load_tile(S.TILE_DIR, "ground", "ground", (S.TILE, S.TILE), (70, 60, 46))
        self.tile_wall = loader.load_tile(S.TILE_DIR, "wall", "wall", (S.TILE, S.TILE), (52, 46, 40))
        if S.GROUND_ALPHA < 255:
            self.tile_ground = self.tile_ground.copy()
            self.tile_ground.set_alpha(S.GROUND_ALPHA)

        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                px, py = x * S.TILE, y * S.TILE
                if ch in SOLID_TILES:
                    self.solid_rects.append(pygame.Rect(px, py, S.TILE, S.TILE))
                if ch == "X":
                    d = container_defs.pop(0) if container_defs else {}
                    self.containers.append({"tile": (x, y), "name": d.get("name", "ящик"),
                                            "loot": dict(d.get("loot", {})), "owner": d.get("owner"),
                                            "opened": False})
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

    def add_pickup(self, pos, kind, count):
        self.pickups.append({"rect": pygame.Rect(pos[0], pos[1], S.TILE, S.TILE),
                             "kind": kind, "count": count})

    @property
    def pixel_size(self):
        return self.width * S.TILE, self.height * S.TILE

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
        r = pygame.Rect(x * S.TILE, y * S.TILE, S.TILE, S.TILE)
        self.solid_rects = [w for w in self.solid_rects if w != r]

    def adjacent(self, tiles, player_rect, reach=1):
        """Первая из клеток tiles рядом с игроком (по соседству, включая диагональ)."""
        px, py = player_rect.centerx // S.TILE, player_rect.centery // S.TILE
        for t in tiles:
            if max(abs(t[0] - px), abs(t[1] - py)) <= reach:
                return t
        return None

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
                if ch in "XD>":
                    surf.blit(loader.special_tile(ch), (px, py))
        # предметы рисуем из списка, а не из карты — подобранные исчезают
        for p in self.pickups:
            icon = loader.item_icon(p["kind"])
            surf.blit(icon, icon.get_rect(center=(p["rect"].centerx - cam_x, p["rect"].centery - cam_y)))

    def collect_pickups(self, player_rect, inventory, log_fn=None):
        remaining = []
        for p in self.pickups:
            if p["rect"].colliderect(player_rect):
                inventory.add(p["kind"], p["count"])
                if log_fn:
                    log_fn(f"Подобрано: {p['kind']}" + (f" ×{p['count']}" if p["count"] > 1 else ""))
            else:
                remaining.append(p)
        self.pickups = remaining
