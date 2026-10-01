"""
Случайные встречи на карте мира (как в Fallout 2): сцена собирается на лету из объектов
наборов «wasteland town» и «War ruins» — пустыня, скалы, сухие деревья, остовы машин — и в
ней что-то происходит: засада, стая, караван, тайник, чья-то трагедия.

Что выпадет, зависит от уровня героя (у каждой сцены — окно уровней и вес), от того,
где он на карте (у реки на востоке — ящеры), и от сюжета (патрули культа — после Бейкера).
Есть встречи, которые не по зубам: голем, шагающая броня, звери. Они намного выше уровнем —
подсказка над врагом предупреждает, а уйти можно через край карты (выход на западе и востоке).
Опытный следопыт (навык «Выживание») опасную встречу замечает издалека и обходит.

make_encounter -> (Location, текст для лога) или (None, текст), если встречу обошли.
"""
import random
from collections import deque

from . import props as P
from .location import Location

W, H = 40, 24
MID = H // 2

# сухая трава и кусты (у травы из «War ruins» под картинкой квадрат песка — её не берём)
DRY = ["r_dry_bush", "bush_11", "bush_37", "bush_79", "grass_big"] + [f"grass_{i}" for i in (5, 6, 10, 13, 18, 26, 28, 35)]
TREES = [f"r_dtree_{c}" for c in "abcdefg"]
ROCKS = ["r_rocks", "stones_12", "stones_19", "stones_21", "stones_62", "rock_grass", "rock_grass_b"]
WRECKS = ["r_car_wreck", "r_car_a", "r_car_b", "r_car_c", "r_pickup", "r_taxi", "r_car_d"]
JUNK = ["r_trash", "r_bones", "r_planks", "r_barrels", "r_bin", "r_logs"]


class Scene:
    """Маленькая карта встречи в формате data/maps/*.json (её читает src/townmap.TownMap)."""

    def __init__(self, rnd, road=False):
        self.rnd = rnd
        self.ground = [["d"] * W for _ in range(H)]
        self.props, self.containers = [], []
        self.enemies, self.npcs, self.pickups = [], [], []
        self.blocked, self.taken = set(), set()
        self.start = (2, MID)
        self.exits = [(0, y) for y in range(MID - 2, MID + 2)] + [(W - 1, y) for y in range(MID - 2, MID + 2)]
        if road:   # старая трасса через всю сцену
            for y in range(MID - 2, MID + 2):
                for x in range(W):
                    self.ground[y][x] = "a"
            for x in range(0, W, 4):
                self.ground[MID - 1][x] = self.ground[MID - 1][x + 1] = "h"
        # вход и выходы — свободны
        for x in list(range(0, 5)) + list(range(W - 4, W)):
            for y in range(MID - 3, MID + 3):
                self.taken.add((x, y))

    def _reach(self, extra=()):
        bad = self.blocked | set(extra)
        seen, q = {self.start}, deque([self.start])
        while q:
            x, y = q.popleft()
            for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= n[0] < W and 0 <= n[1] < H and n not in seen and n not in bad:
                    seen.add(n)
                    q.append(n)
        return seen

    def put(self, name, x, y, check=True):
        inf = P.info(name)
        fw, fh = inf["foot"]
        foot = [(x + i, y + j) for i in range(fw) for j in range(fh)]
        if any(not (1 <= fx < W - 1 and 1 <= fy < H - 1) for fx, fy in foot):
            return False
        if any(t in self.taken or t in self.blocked for t in foot):
            return False
        if name in DRY and any(self.ground[fy][fx] != "d" for fx, fy in foot):
            return False
        if inf["block"] and check:
            before = len(self._reach())
            if len(self._reach(foot)) < before - len(foot):
                return False   # отрезал бы кусок карты
        if inf["block"]:
            self.blocked.update(foot)
        else:
            self.taken.update(foot)
        if name in DRY or name in ROCKS:
            self.props.append([name, x, y, self.rnd.randint(-12, 12), self.rnd.randint(-8, 6)])
        else:
            self.props.append([name, x, y])
        return True

    def scatter(self, names, n, x0=1, y0=1, x1=W - 2, y1=H - 2):
        for _ in range(n * 30):
            if n <= 0:
                break
            if self.put(self.rnd.choice(names), self.rnd.randint(x0, x1), self.rnd.randint(y0, y1)):
                n -= 1

    def box(self, name, x, y, title, loot):
        """Обыскиваемое: ставится ближайшее свободное место к (x, y)."""
        for r in range(0, 6):
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    if self.put(name, x + dx, y + dy):
                        self.containers.append({"prop": len(self.props) - 1, "name": title, "loot": loot,
                                                "owner": None})
                        return True
        return False

    def spot(self, x0, y0, x1, y1):
        """Свободная доступная клетка в прямоугольнике."""
        reach = self._reach()
        cells = [(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)
                 if (x, y) in reach and (x, y) not in self.taken and (x, y) not in self.blocked]
        c = self.rnd.choice(cells)
        self.taken.add(c)
        return c

    def enemy(self, kind, x0=20, y0=3, x1=W - 6, y1=H - 4):
        x, y = self.spot(x0, y0, x1, y1)
        self.enemies.append([kind, x, y])

    def npc(self, nid, x0=18, y0=MID - 4, x1=26, y1=MID + 4):
        x, y = self.spot(x0, y0, x1, y1)
        self.npcs.append([nid, x, y])

    def dress(self, trees=6, dry=20, rocks=10):
        """Пустыня вокруг: сухие деревья, кусты, камни."""
        self.scatter(TREES, trees)
        self.scatter(DRY, dry)
        self.scatter(ROCKS, rocks)

    def to_map(self):
        return {"w": W, "h": H, "player": list(self.start), "exits": [list(t) for t in self.exits],
                "ground": ["".join(r) for r in self.ground], "decals": [], "props": self.props,
                "containers": self.containers, "terminals": [], "portals": [], "roofs": [],
                "enemies": self.enemies, "npcs": self.npcs, "pickups": self.pickups, "tint": [255, 240, 212]}


# ------------------------------------------------------------ сцены
def _rats(s, lvl):
    s.dress()
    s.scatter(JUNK, 4, 18, 4, W - 6, H - 5)
    for _ in range(s.rnd.randint(3, 5)):
        s.enemy("rat")


def _mutants(s, lvl):
    s.dress()
    s.put(s.rnd.choice(WRECKS), 22, MID + 2)
    s.box("r_bones", 24, MID - 3, "тело путника", {"крышки": s.rnd.randint(5, 20), "бинт": 1, "ткань": 1})
    for _ in range(2 + (lvl >= 3)):
        s.enemy("mutant")


def _raiders(s, lvl):
    s.dress(trees=3)
    for x, y in ((20, MID - 4), (21, MID + 2)):   # баррикада из машин поперёк дороги
        s.put(s.rnd.choice(WRECKS), x, y)
    s.put("r_sandbag_row", 25, MID - 1)
    s.box("r_barrels", 30, MID, "заначка рейдеров", {"патроны": s.rnd.randint(4, 10), "крышки": s.rnd.randint(10, 30)})
    for _ in range(2 + (lvl >= 3)):
        s.enemy("raider", 22, 3, W - 6, H - 4)
    if lvl >= 4:
        s.enemy("raider_elite", 28, 3, W - 6, H - 4)


def _beetles(s, lvl):
    s.dress(trees=4, rocks=16)
    s.enemy("beetle")
    for _ in range(s.rnd.randint(1, 2)):
        s.enemy("rat")


def _ferals(s, lvl):
    s.dress(trees=3)
    s.put(s.rnd.choice(["r_van", "r_tanker", "r_rv_b"]), 20, MID - 5)
    s.box("r_dumpster", 26, MID + 3, "мусорный бак", {"ткань": 1, "химикаты": 1, "крышки": 6})
    for _ in range(3 + (lvl >= 6)):
        s.enemy("feral")


def _roaches(s, lvl):
    s.dress(trees=2, rocks=6)
    s.put("r_junk_mound", 22, MID - 2)
    s.box("r_dumpster_b", 28, MID + 3, "ржавый бак", {"химикаты": 2, "лом": 2})
    for _ in range(s.rnd.randint(4, 6)):
        s.enemy("radroach")


def _cult(s, lvl, hostile):
    s.dress(trees=4)
    s.put("r_tent_beige", 24, MID - 4)
    s.put("firewood", 27, MID)
    for kind in ("cult_guard", "cult_guard", "cultist"):
        s.enemy(kind, 20, MID - 5, 32, MID + 5)


def _robots(s, lvl):
    s.dress(trees=2, rocks=8)
    s.put("r_bunker_small", 24, MID - 6)
    s.box("ammo_box", 22, MID + 3, "армейский ящик", {"патроны": 12, "дробь": 6, "граната": 1})
    for _ in range(2):
        s.enemy("robot_skel")


def _snipers(s, lvl):
    s.dress(trees=3)
    s.put("r_derrick", 30, MID - 6)
    s.put("r_sandbag_row", 27, MID + 1)
    s.enemy("sniper", 30, 3, W - 4, MID - 3)
    s.enemy("sniper", 30, MID + 3, W - 4, H - 3)
    s.enemy("raider_elite", 26, MID - 2, 32, MID + 2)


def _golem(s, lvl):
    s.dress(trees=1, dry=12, rocks=24)
    s.enemy("sand_golem", 22, MID - 4, 30, MID + 4)
    s.box("r_bones", 30, MID - 6, "кости и рюкзак", {"крышки": s.rnd.randint(20, 60), "стимулятор": 1,
                                                    "химикаты": 2})


def _beasts(s, lvl):
    s.dress(trees=5)
    for _ in range(1 + (lvl >= 7)):
        s.enemy("beast")


def _lizards(s, lvl):
    s.dress(trees=2, dry=30)
    s.scatter(["x_puddle"], 5)
    for _ in range(2):
        s.enemy("river_lizard")


def _mech(s, lvl):
    s.dress(trees=2)
    s.put("r_army_truck", 22, MID - 6)
    s.enemy("mech_green", 24, MID - 2, 32, MID + 3)
    s.enemy("robot_skel")


def _caravan(s, lvl):
    s.dress(trees=3)
    s.put("r_camper", 20, MID - 5)
    s.put("r_awning", 24, MID + 2)
    s.npc("caravan_trader", 22, MID - 2, 26, MID + 1)
    s.npc("caravan_guard", 27, MID - 3, 30, MID + 3)


def _robot_post(s, lvl):
    s.dress()
    s.npc("robot")


def _cache(s, lvl):
    s.dress()
    s.box("r_dumpster", 22, MID, "тележка каравана", {"крышки": s.rnd.randint(15, 35),
                                                     "патроны": s.rnd.randint(3, 8), "химикаты": 2, "бинт": 1})


def _dead_trailer(s, lvl):
    """Уникальная: трейлер Мэйбл — дневник и дробовик (один раз за игру)."""
    s.dress(trees=4)
    s.put("r_rv", 20, MID - 5)
    s.box("metal_chest", 24, MID - 1, "сундук Мэйбл", {"дневник Мэйбл": 1, "дробовик": 1, "дробь": 10})
    s.box("r_bones", 27, MID + 2, "останки у трейлера", {"ткань": 1})


# вес, id, уровни [от, до], текст, сцена, условие (флаги, уровень, восток ли)
ENCOUNTERS = [
    (24, "rats", (1, 4), "Стая крысюков. Похоже, они тоже рады встрече.", _rats, None),
    (18, "mutants", (1, 5), "Мутанты-падальщики что-то доедают. Возможно, предыдущего путника.", _mutants, None),
    (16, "raiders", (2, 9), "Машины поперёк дороги, мешки с песком. Засада — и вас уже заметили.", _raiders, None),
    (12, "beetles", (2, 6), "Панцирный жук и его свита из крысюков греются на камнях.", _beetles, None),
    (14, "ferals", (3, 10), "У разбитого фургона бродят дикие гули. Один уже поднял голову.", _ferals, None),
    (10, "roaches", (1, 5), "Гора хлама шевелится. Это радтараканы. Много радтараканов.", _roaches, None),
    (12, "cult", (3, 12), "Патруль в белых балахонах. «Свет с тобой, путник», — говорит старший.", _cult,
     lambda f, lv, east: f.get("seen_baker")),
    (10, "robots", (4, 12), "Довоенный пост: два робота-скелета всё ещё несут караул.", _robots, None),
    (8, "snipers", (4, 12), "Блик оптики на вышке. Снайперы. Голову ниже.", _snipers, None),
    (5, "golem", (1, 20), "Дюна впереди шевелится и встаёт. Это не дюна.", _golem, None),
    (6, "beasts", (3, 20), "Рогатая тварь роет землю и смотрит на вас. Очень внимательно.", _beasts, None),
    (10, "lizards", (4, 20), "У пересохшего русла греются речные ящеры. Пара голов поворачивается к вам.", _lizards,
     lambda f, lv, east: east),
    (3, "mech", (6, 20), "Лязг металла. Шагающая броня без опознавательных знаков идёт патрулём.", _mech, None),
    (9, "caravan", (1, 20), "Караван бродячего торговца сделал привал. Охранник машет рукой.", _caravan, None),
    (4, "robot", (1, 20), "Посреди пустоши стоит почтовый робот и терпеливо ждёт. Уже лет сто.", _robot_post,
     lambda f, lv, east: not f.get("robot_done")),
    (7, "cache", (1, 20), "Брошенная тележка каравана. Караванщиков не видно. Может, оно и к лучшему.", _cache, None),
    (4, "trailer", (2, 20), "Ржавый трейлер у дороги. Дверь распахнута, внутри тихо.", _dead_trailer,
     lambda f, lv, east: not f.get("mabel_found")),
]
ROADS = {"raiders", "caravan", "cache", "trailer", "mech"}


def roll(flags, level, east=False, rnd=random):
    table = [e for e in ENCOUNTERS if e[2][0] <= level <= e[2][1] and (e[5] is None or e[5](flags, level, east))]
    return rnd.choices(table, weights=[e[0] for e in table])[0]


def danger(enc_id):
    """Самый высокий уровень врага в сцене (для «обойти издалека»)."""
    from .location import ENEMY_DEFS
    kinds = {"golem": "sand_golem", "beasts": "beast", "lizards": "river_lizard", "mech": "mech_green",
             "snipers": "sniper", "robots": "robot_skel"}
    k = kinds.get(enc_id)
    return ENEMY_DEFS[k].get("level", 1) if k else 0


def make_encounter(flags, level=1, survival=20, east=False, rnd=random):
    _, enc_id, _lv, text, build, _cond = roll(flags, level, east, rnd)
    # следопыт замечает опасное заранее и обходит: шанс — Выживание/2 %
    if danger(enc_id) >= level + 3 and rnd.randint(1, 100) <= survival // 2:
        return None, f"Вы замечаете издалека: {text[0].lower() + text[1:]} Связываться не стоит — вы обходите стороной."
    s = Scene(rnd, road=enc_id in ROADS)
    if enc_id == "cult":
        build(s, level, flags.get("cult_hostile"))
    else:
        build(s, level)
    loc = Location(f"encounter:{enc_id}", d={"name": "Пустошь", "map": s.to_map(), "encounter": True})
    if enc_id == "cult" and flags.get("cult_hostile"):
        for e in loc.enemies:
            e.hostile = True
            e.talk = None
        text = "Патруль в белых балахонах. Старший узнаёт вас: «Это он! Огонь соединяет!»"
    if enc_id == "trailer":
        flags["mabel_found"] = True
    return loc, text
