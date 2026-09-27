"""
Локация: карта + враги + NPC + контейнеры. Описания — в data/locations.json,
типы врагов — в data/enemies.json. Состояние локации (кто убит, что
подобрано и открыто) живёт в объекте, пока игра открыта.
"""
import json

from . import settings as S
from . import loader
from .tilemap import TileMap, load_map_file
from .entities import Enemy, NPC

NPC_NAMES = {"gena": "Ржавый Гена", "robot": "Почтальон-3000"}

with open("data/enemies.json", "r", encoding="utf-8") as f:
    ENEMY_DEFS = json.load(f)
with open("data/locations.json", "r", encoding="utf-8") as f:
    LOCATION_DEFS = json.load(f)

_ANIM_CACHE = {}


def enemy_animations(type_id):
    if type_id not in _ANIM_CACHE:
        d = ENEMY_DEFS[type_id]
        art = d["art"]
        # мутант исторически лежит в assets/sprites/enemy, остальные — в папке своего типа
        folder = f"{S.ASSET_ROOT}/sprites/{d.get('sprite_dir', type_id)}"
        _ANIM_CACHE[type_id] = loader.load_creature_animations(
            folder, tuple(art["size"]), tuple(art["base"]), tuple(art["accent"]), kind=art["kind"])
    return _ANIM_CACHE[type_id]


def make_enemy(pos, type_id):
    return Enemy(pos, enemy_animations(type_id), type_id, ENEMY_DEFS[type_id])


def npc_animations(npc_id):
    key = f"npc:{npc_id}"
    if key not in _ANIM_CACHE:
        if npc_id == "robot":
            _ANIM_CACHE[key] = loader.load_creature_animations(
                f"{S.ASSET_ROOT}/sprites/robot", (44, 56), (120, 125, 135), (230, 190, 60), kind="humanoid")
        else:
            _ANIM_CACHE[key] = loader.load_humanoid_animations(
                S.NPC_DIR, loader.FRAME_SIZE, base_color=(70, 90, 110), accent_color=(190, 180, 150))
    return _ANIM_CACHE[key]


class Location:
    def __init__(self, loc_id, d=None, rows=None):
        d = d if d is not None else LOCATION_DEFS.get(loc_id, {})
        self.id = loc_id
        self.name = d.get("name", loc_id)
        self.world_pos = d.get("world_pos")
        self.is_encounter = d.get("encounter", False)
        self.level = TileMap(rows or load_map_file(d["map"]), npc_ids=d.get("npcs"),
                             containers=d.get("containers"))
        entry = d.get("entry")
        self.entry = (entry[0] * S.TILE, entry[1] * S.TILE) if entry else self.level.player_spawn
        self.enemies = [make_enemy(pos, t) for pos, t in self.level.enemy_spawns]
        self.npcs = [NPC(pos, npc_animations(nid), npc_id=nid, name=NPC_NAMES.get(nid, nid))
                     for pos, nid in self.level.npc_spawns]

    def faction_members(self, faction):
        return [e for e in self.enemies if e.alive and e.faction == faction]
