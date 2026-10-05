"""
Локация: карта + враги + NPC + контейнеры. Описания — в data/locations.json,
типы врагов — в data/enemies.json. Состояние локации (кто убит, что
подобрано и открыто) живёт в объекте, пока игра открыта.
"""
import json

import pygame

from . import settings as S
from . import loader
from .tilemap import TileMap, load_map_file
from .townmap import TownMap
from .entities import Enemy, NPC

NPC_NAMES = {"gena": "Ржавый Гена", "robot": "Почтальон-3000", "blondie": "Блонди", "loner": "Панк-одиночка",
             "turtle": "Черепан", "dog": "Рыжий пёс", "silas": "Брат Сайлас", "mo": "Мо «Ведро»", "lenny": "Лен",
             "marta": "Марта", "sheriff": "Шериф Брэддок", "doc": "Док Мира", "ada": "Смотрительница Ада",
             "dale": "Дейл", "rose": "Караванщица Роза", "dex": "Наёмник Дэкс",
             # Бейкер
             "anselm": "Брат Ансельм", "amos": "Дед Эймос", "amos_b7": "Дед Эймос", "iskra": "Искра",
             "iskra_out": "Искра", "nick": "Ник Грек", "tobias": "Брат Тобиас", "hattie": "Хэтти Мур",
             "hollis": "Холлис", "lira_baker": "Лира", "loner_baker": "Панк", "silas_baker": "Брат Сайлас",
             "scar_baker": "Шрам", "baker_folk_a": "Житель", "baker_folk_b": "Жительница",
             "baker_kid": "Мальчишка", "baker_folk_c": "Девушка", "baker_folk_d": "Старик",
             "baker_folk_e": "Караванщица",
             # случайные встречи
             "caravan_trader": "Бродячий торговец", "caravan_guard": "Охранник каравана",
             "farmer_miller": "Фермер Миллер",
             "walt": "Старик Уолт", "miss_lane": "Мисс Лейн", "ghoul_kid_a": "Томми", "ghoul_kid_b": "Сью",
             "ghoul_kid_c": "Маленький Джо", "tess": "Тесс",
             "oskar": "Брат Оскар", "motel_mom": "Женщина в номере 201", "motel_kid": "Мальчик",
             "springer": "Отец Кёртис Спрингер", "nurse_ava": "Сестра Ава", "gus": "Смотритель Гас",
             "pilgrim_hank": "Паломник Хэнк", "pilgrim_maria": "Мария", "pilgrim_timmy": "Тимми",
             "healer_girl": "Целительница Лоис", "merchant_zz": "Торговец Абдул", "bath_pilgrim": "Паломница",
             "bath_pilgrim_b": "Паломник", "guest_widow": "Вдова Харпер",
             "kate": "Мамаша Кейт", "captain_morrow": "Капитан Морроу", "river_guard": "Страж Билли",
             "fisher_joe": "Рыбак Джо", "fishmonger": "Торговка Пег", "preacher_eli": "Проповедник Эли",
             "needles_girl": "Лиззи", "drunk_vic": "Пьяница Вик", "morrow_scout": "Дозорный стражи",
             "barkeep_ned": "Бармен Нед", "gambler_lou": "Картёжник Лу", "river_guard_off": "Стражник",
             "shopkeeper_rosa": "Лавочница Роуз",
             "dolores": "Долорес Вега", "water_clerk": "Конторщик Пабло", "hub_guard": "Хабская стража",
             "hub_guard_b": "Хабская стража", "crimson_boss": "Маргарет Крэйн", "spice_seller": "Торговец пряностями",
             "arms_seller": "Оружейник Кирк", "cult_preacher": "Сестра Мирра", "bos_scout": "Разведчица Братства",
             "hub_kid": "Мальчишка", "hub_beggar": "Нищий", "hub_beggar_b": "Нищенка", "old_woman": "Старуха Нэн",
             "junkie": "Торчок", "street_kid": "Беспризорник", "decker": "Декер", "falcon_barkeep": "Бармен Винни",
             "falcon_drunk": "Пьяница", "falcon_singer": "Певица Лулу", "falcon_gambler": "Шулер Ленни",
             "slum_mother": "Мать с ребёнком", "slum_old": "Старик у костра", "slum_boy": "Мальчишка с рогаткой",
             "roy": "Рой", "marla": "Марла", "marla_home": "Марла", "acolyte_a": "Послушница",
             "acolyte_b": "Послушник", "baker_kid_b": "Девочка",
             "gate_guard": "Привратник Кэл", "jt_guard": "Стражник", "cult_recruiter": "Брат Офир", "water_seller": "Водовоз Сэл", "jt_tinker": "Механик Лу", "jt_kid": "Пип", "jt_woman": "Прачка Дина", "jt_old_scav": "Старик Барни", "jt_drunk": "Пьяница Морт", "spike": "Старьёвщик Спайк", "scrapper": "Старьёвщик Хэл", "scrapper_girl": "Старьёвщица Джин", "mayor_darkwater": "Мэр Дарквотер", "hall_guard": "Стражник ратуши", "gizmo": "Гизмо", "gizmo_thug": "Громила Изо", "croupier": "Крупье Вера", "cashier_jt": "Кассир Билл", "gambler_jt": "Игрок", "gambler_jt_b": "Игрок", "marsha": "Марша Дарквотер", "anna_shaw": "Доктор Анна Шоу", "orderly_tom": "Санитар Томми", "patient_hank": "Больной Хэнк", "patient_girl": "Девочка Мэйси", "neal": "Бармен Нил", "hunter_rourke": "Рурк", "skum_drunk": "Пьянчуга", "skum_girl": "Танцовщица Сью",
             "nc_guard": "Страж Сета", "nc_guard_b": "Страж Сета", "cult_envoy": "Сестра Эсфирь", "gravedigger": "Могильщик Ирвинг", "harry_mech": "Механик Гарри", "water_queue": "Гуль в очереди", "water_queue_b": "Гулька в очереди", "maud": "Торговка Мод", "ghoul_vendor": "Старьёвщик Пит", "nc_ghoul_kid": "Гулёнок", "nc_old": "Старый гуль", "set": "Сет", "nc_hall_guard": "Страж Сета", "nc_hall_guard_b": "Страж Сета", "lorraine": "Писарь Лоррейн", "cobbs": "Капрал Коббс", "zeke": "Оружейник Зик", "ghoul_healer": "Целитель Дейв", "under_barkeep": "Хозяйка Бетти", "under_ghoul": "Гуль", "under_ghoul_b": "Гуль", "under_ghoul_c": "Гуль у костра"}
# у кого кадры лежат в чужой папке (жители из tools/make_variants.py)
NPC_SPRITES = {"marta": "folk_a", "dale": "folk_b", "rose": "folk_a", "dex": "merc",
               # Бейкер (листы из tools/import_sheets.py)
               "amos_b7": "amos", "iskra": "girl_hood", "iskra_out": "girl_hood", "nick": "barkeep",
               "tobias": "cultist", "hattie": "seer", "hollis": "detective", "lira_baker": "blondie",
               "loner_baker": "loner", "silas_baker": "silas", "scar_baker": "boss",
               "baker_folk_a": "folk_c", "baker_folk_b": "folk_d", "baker_kid": "kid", "baker_folk_c": "girl_pink",
               "baker_folk_d": "folk_g", "baker_folk_e": "folk_e",
               "caravan_trader": "healer", "caravan_guard": "desert_guard", "farmer_miller": "folk_i",
               "walt": "folk_g", "miss_lane": "ghoul_lady", "ghoul_kid_a": "ghoul_kid", "ghoul_kid_b": "ghoul_kid",
               "ghoul_kid_c": "ghoul_kid", "tess": "acolyte",
               "oskar": "folk_c", "motel_mom": "folk_f", "motel_kid": "kid",
               "springer": "detective", "nurse_ava": "seer", "gus": "folk_g", "pilgrim_hank": "feral",
               "pilgrim_maria": "folk_d", "pilgrim_timmy": "kid", "healer_girl": "acolyte", "merchant_zz": "healer",
               "bath_pilgrim": "folk_h", "bath_pilgrim_b": "folk_c", "guest_widow": "folk_f",
               "kate": "folk_d", "captain_morrow": "desert_guard", "river_guard": "soldier", "fisher_joe": "folk_e",
               "fishmonger": "folk_h", "preacher_eli": "monk", "needles_girl": "girl_pink", "drunk_vic": "folk_c",
               "morrow_scout": "scout", "barkeep_ned": "barkeep", "gambler_lou": "detective",
               "river_guard_off": "redarmor", "shopkeeper_rosa": "seer",
               "dolores": "folk_f", "water_clerk": "detective", "hub_guard": "soldier", "hub_guard_b": "soldier",
               "crimson_boss": "redarmor", "spice_seller": "healer", "arms_seller": "desert_guard",
               "cult_preacher": "cultist", "bos_scout": "blondie", "hub_kid": "kid", "hub_beggar": "folk_c",
               "hub_beggar_b": "folk_h", "old_woman": "folk_d", "junkie": "folk_e", "street_kid": "kid",
               "decker": "visor_punk", "falcon_barkeep": "barkeep", "falcon_drunk": "folk_g",
               "falcon_singer": "girl_pink", "falcon_gambler": "scout",
               "slum_mother": "folk_d", "slum_old": "folk_g", "slum_boy": "kid",
               "roy": "folk_f", "marla": "folk_h", "marla_home": "folk_h", "acolyte_a": "acolyte",
               "acolyte_b": "monk", "baker_kid_b": "folk_j",
               "gate_guard": "soldier", "jt_guard": "desert_guard", "cult_recruiter": "cultist", "water_seller": "healer", "jt_tinker": "folk_i", "jt_kid": "kid", "jt_woman": "folk_h", "jt_old_scav": "folk_g", "jt_drunk": "folk_c", "spike": "merc", "scrapper": "folk_e", "scrapper_girl": "girl_hood", "mayor_darkwater": "sheriff", "hall_guard": "soldier", "gizmo": "boss", "gizmo_thug": "gang", "croupier": "blondie", "cashier_jt": "detective", "gambler_jt": "folk_b", "gambler_jt_b": "folk_e", "marsha": "folk_d", "anna_shaw": "doc", "orderly_tom": "folk_j", "patient_hank": "folk_c", "patient_girl": "girl_pink", "neal": "barkeep", "hunter_rourke": "loner", "skum_drunk": "folk_g", "skum_girl": "girl_pink",
               "nc_guard": "ghoul_b", "nc_guard_b": "ghoul_e", "cult_envoy": "cultist", "gravedigger": "ghoul_c", "harry_mech": "ghoul_e", "water_queue": "ghoul_a", "water_queue_b": "ghoul_d", "maud": "ghoul_d", "ghoul_vendor": "ghoul_a", "nc_ghoul_kid": "ghoul_child", "nc_old": "ghoul_c", "set": "ghoul_set", "nc_hall_guard": "ghoul_b", "nc_hall_guard_b": "ghoul_e", "lorraine": "ghoul_lady", "cobbs": "ghoul_cobbs", "zeke": "ghoul_b", "ghoul_healer": "ghoul_c", "under_barkeep": "ghoul_d", "under_ghoul": "ghoul_a", "under_ghoul_b": "ghoul_e", "under_ghoul_c": "ghoul_c"}

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


def make_enemy(pos, type_id, iso=False):
    """iso — на изометрической карте: кадры из iso_sprite (data/enemies.json), если есть."""
    sprite = ENEMY_DEFS[type_id].get("iso_sprite") if iso else None
    if sprite:
        from .iso import char_animator
        e = Enemy(pos, {"idle": [pygame.Surface((1, 1))]}, type_id, ENEMY_DEFS[type_id])
        e.anim = char_animator(sprite)
        return e
    return Enemy(pos, enemy_animations(type_id), type_id, ENEMY_DEFS[type_id])


def npc_animations(npc_id):
    """Кадры NPC — assets/sprites/<npc_id>/ (см. tools/slice_sprites.py), иначе плейсхолдер."""
    key = f"npc:{npc_id}"
    if key not in _ANIM_CACHE:
        folder = f"{S.ASSET_ROOT}/sprites/{NPC_SPRITES.get(npc_id, npc_id)}"
        if npc_id == "robot":
            _ANIM_CACHE[key] = loader.load_creature_animations(
                folder, (44, 56), (120, 125, 135), (230, 190, 60), kind="humanoid")
        else:
            _ANIM_CACHE[key] = loader.load_humanoid_animations(
                folder, loader.FRAME_SIZE, base_color=(70, 90, 110), accent_color=(190, 180, 150))
    return _ANIM_CACHE[key]


class Location:
    def __init__(self, loc_id, d=None, rows=None):
        d = d if d is not None else LOCATION_DEFS.get(loc_id, {})
        self.id = loc_id
        self.name = d.get("name", loc_id)
        self.world_pos = d.get("world_pos")
        self.is_encounter = d.get("encounter", False)
        if rows is None and d.get("scene"):   # придорожное место: сцена из src/encounters.py, всегда одна и та же
            from .encounters import spot_map
            self.level = TownMap(spot_map(loc_id, d["scene"]))
        elif rows is None and isinstance(d.get("map"), dict):   # сцена случайной встречи, собранная на лету
            self.level = TownMap(d["map"])
        elif rows is None and d["map"].endswith(".json"):
            with open(d["map"], "r", encoding="utf-8") as f:
                is_iso = '"iso":true' in f.read(200).replace(" ", "")
            if is_iso:
                from .isomap import IsoMap
                self.level = IsoMap(d["map"])   # изометрия (tools/build_iso_town.py)
            else:
                self.level = TownMap(d["map"])  # карта из объектов (tools/build_town.py)
        else:
            self.level = TileMap(rows or load_map_file(d["map"]), npc_ids=d.get("npcs"),
                                 containers=d.get("containers"), terminals=d.get("terminals"))
        entry = d.get("entry")
        self.entry = (entry[0] * S.TILE, entry[1] * S.TILE) if entry else self.level.player_spawn
        iso = getattr(self.level, "iso", False)
        self.enemies = [make_enemy(pos, t, iso) for pos, t in self.level.enemy_spawns]
        if d.get("action"):   # экшен (Барстоу): здоровье гулей — ровно в пулях
            from .action import set_action_hp
            for e in self.enemies:
                set_action_hp(e)
        self.enemies_all = list(self.enemies)  # исходный порядок — для сохранений (ушедшие исчезают из enemies)
        self.npcs = [NPC(pos, npc_animations(nid), npc_id=nid, name=NPC_NAMES.get(nid, nid))
                     for pos, nid in self.level.npc_spawns]

    def faction_members(self, faction):
        return [e for e in self.enemies if e.alive and e.faction == faction]
