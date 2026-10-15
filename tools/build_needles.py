"""
Нидлс — переправа через Колорадо, конец первого акта (реальный город на I-40 у границы Аризоны).
Сценарий — docs/story.md, раздел 9.

  needles          «Нидлс: Пристань» (72×50): трасса I-40 с запада, станция Санта-Фе (старый вокзал,
                   ж/д пути), Главная улица с салуном «Последний паром», лавкой и церковью, на востоке —
                   река Колорадо: пристань с лодками, рыбный рынок, лодочные сараи, паром Мамаши Кейт.
                   К северу от пристани — блокпост на мосту (Речная стража).
  needles_bridge   «Мост через Колорадо» (64×30): обрушенный пролёт, блокпост Речной стражи (капитан
                   Морроу, пошлина), баррикады из контейнеров и грузовиков, на том берегу — Аризона.
  needles_saloon   салун «Последний паром» (интерьер): стойка, столы, сцена, комнаты наверху — проход.
  needles_depot    вокзал Санта-Фе (интерьер): зал ожидания, касса, багажное отделение — логово
                   речных ящеров, выбравшихся через сток.

Наборы: wasteland-port (wport), medieval-coastal-fishing-village (fishv), modern-port (mport),
wasteland-railway-station (wrail), wild-west (west), 1950s town (town50), small bar (sbar).
Запуск из папки game_project:  .venv/bin/python tools/build_needles.py
"""
import json

from citykit import City, CityMap

city = City("needles", "Нидлс")


def P(name, img, **kw):
    city.prop(name, img, **kw)
    return name


def cells(page, pts):
    return [f"pk:{page}/{x},{y},1,1" for x, y in pts]


# ------------------------------------------------------------ объекты
BOAT = P("nd_boat", "pk:fishv/p3/0,10,2,1", foot=[2, 1], block=False, layer="floor", keybg=True)
BOAT_B = P("nd_boat_b", "pk:fishv/p3/0,11,2,1", foot=[2, 1], block=False, layer="floor", keybg=True)
SAILBOAT = P("nd_sailboat", "pk:fishv/p3/4,10,4,2", foot=[4, 2], block=False, layer="floor", keybg=True)
FISH_STALL = P("nd_fish_stall", "pk:fishv/p3/8,8,2,2", foot=[2, 1], sight=True)
FISH_STALL_B = P("nd_fish_stall_b", "pk:fishv/p3/10,8,2,2", foot=[2, 1], sight=True)
MEAT_STALL = P("nd_meat_stall", "pk:fishv/p3/10,10,2,2", foot=[2, 1], sight=True)
LIGHTHOUSE = P("nd_lighthouse", "pk:fishv/p3/8,10,1,2", foot=[1, 1], sight=True, keybg=True)
SHED = P("nd_boatshed", "pk:fishv/p4/12,8,2,3", foot=[2, 2], sight=True)
SHED_B = P("nd_boatshed_b", "pk:fishv/p4/13,12,2,3", foot=[2, 2], sight=True)
HOUSE_W = P("nd_house_wood", "pk:fishv/p3/0,0,2,2", foot=[2, 2], sight=True)
HOUSE_W2 = P("nd_house_wood2", "pk:fishv/p3/2,0,2,2", foot=[2, 2], sight=True)
HOUSE_T = P("nd_house_thatch", "pk:fishv/p3/0,4,2,2", foot=[2, 2], sight=True)
HOUSE_T2 = P("nd_house_thatch2", "pk:fishv/p3/4,4,2,2", foot=[2, 2], sight=True)
NET = P("nd_net", "pk:fishv/fishv_1_012", block=False)
FISH_RACK = P("nd_fish_rack", "pk:fishv/fishv_1_078", foot=[2, 1])
FISH_RACK_B = P("nd_fish_rack_b", "pk:fishv/fishv_1_108", foot=[2, 1])
ANCHOR = P("nd_anchor", "pk:fishv/fishv_1_027")
BARREL = P("nd_barrel", "pk:fishv/fishv_1_057", search="junk", title="бочка")
CRATE = P("nd_crate", "pk:fishv/fishv_1_059", search="crate", title="ящик")
LANTERN_POST = "lamp_post"                                  # высокий уличный фонарь (свет описан в каталоге)
WRECK = P("nd_wreck", "pk:fishv/fishv_1_000", foot=[2, 1])
CONT_R = P("nd_container_r", "pk:wport/wport_2_007", foot=[3, 2], sight=True)
CONT_B = P("nd_container_b", "pk:wport/wport_2_010", foot=[3, 2], sight=True)
CONT_G = P("nd_container_g", "pk:wport/wport_2_045", foot=[3, 2], sight=True)
TRUCK = P("nd_truck", "pk:wport/wport_1_000", foot=[2, 2], sight=True)
TRUCK_B = P("nd_truck_b", "pk:wport/wport_4_004", foot=[4, 2], sight=True)
TIRES = P("nd_tires", "pk:wport/wport_1_013", foot=[2, 1])
BARRELS = P("nd_barrels", "pk:wport/wport_1_055", foot=[2, 1], search="junk", title="бочки")
CRANE = P("nd_crane", "pk:wport/wport_3_045", foot=[2, 2], sight=True)
JUNK = P("nd_junk", "pk:wport/wport_3_013", foot=[2, 1], search="junk", title="куча хлама")
STAGECOACH = P("nd_stagecoach", "pk:west/west_1_011", foot=[2, 1])
TROUGH = P("nd_trough", "pk:west/p1/12,3,2,1", foot=[2, 1])
WEST_SIGN = P("nd_signboard", "pk:west/p1/12,4,2,2", foot=[2, 1])
CACTUS = P("nd_cactus", "pk:west/p1/12,0,1,2", foot=[1, 1])
CACTUS_B = P("nd_cactus_b", "pk:west/p1/15,0,1,2", foot=[1, 1])
TUMBLE = P("nd_tumbleweed", "pk:west/west_1_004", block=False)
BENCH = "bench_7"
RAIL_WAGON = P("nd_wagon", "pk:wrail/p1/10,12,2,1", foot=[2, 1])
BAR_STOOLS = P("nd_bar_counter", "pk:west/west_2_108", foot=[4, 1])
PIANO = P("nd_piano", "pk:west/west_2_012", foot=[2, 1])
BOOKS = P("nd_bookcase", "pk:west/west_2_116", sight=True, search="shelf", title="книжный шкаф")
CABINET = P("nd_cabinet", "pk:west/west_2_110", sight=True, search="shelf", title="буфет")
TABLE = P("nd_table", "pk:west/west_2_000", foot=[2, 1])
POKER = P("nd_poker", "pk:west/west_2_020", foot=[2, 1])
CHAIR = P("nd_chair", "pk:west/west_2_001")
STOVE = P("nd_stove", "pk:west/west_2_018")
CLOCK = P("nd_clock", "pk:west/west_2_019", sight=True)
BED = P("nd_bed", "pk:west/west_2_005", foot=[2, 2])
RUG = P("nd_rug", "pk:west/west_2_060", block=False, layer="floor", keybg=True)
SAFE = P("nd_safe", "pk:west/west_2_105", search="military", title="сейф")
SUITCASES = P("nd_suitcases", "pk:wrail/wrail_1_014", search="bag", title="чемоданы")

SAND = ["pk:desnat/p1/0,0,1,1", "pk:desnat/p1/1,0,1,1", "pk:desnat/p1/0,1,1,1"]   # песок под цвет окружающей пустыни, без узора-повтора
DIRT = ["noise:pk:destown/p2/4,0,1,1"]      # укатанный гравий улиц — бесшовный
PLANK = ["pk:seaport/seaport_f1_21"]
STONE = ["pk:seaport/seaport_f1_26"]
WATER = cells("mport/p1", [(8, 4), (9, 4), (10, 4), (11, 4), (8, 5), (9, 5), (10, 5), (11, 5)])
DEEP = WATER
SALOON_FLOOR = ["pk:seaport/seaport_f1_21"]
TILE = ["pk:hotel/hotel_f1_11", "pk:hotel/hotel_f1_12"]


# лодки — плоский рисунок на воде (force: клетки воды заняты, это и есть их место)


def river(m, x0, y0, x1, y1):
    """Река: клетки воды (код «~», непроходимы), у середины — глубже."""
    m.water_codes = ("~", "≈")
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            m.ground[y][x] = "≈" if x0 + 2 < x < x1 - 1 else "~"
            m.blocked.add((x, y))
    m._reach = None


def pier(m, x0, y0, x1, y1):
    """Причал из досок поверх воды: снова проходим."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            m.ground[y][x] = "w"
            m.blocked.discard((x, y))
    m._reach = None


# ================================================================ Пристань
# Собрано по превью набора «рыбацкая деревня»: изогнутый берег, дощатая набережная у воды, причалы с лодками,
# рыбный рынок у причала, лодочный сарай и хижины на берегу (не в воде!), рельсы у вокзала.
import math as _m

W, H = 72, 50
n = CityMap(city, "needles", "Нидлс: Пристань", W, H, start=(2, 24), seed=91, music="hub",
            world_pos=(2470, 1470))
n.floor_code("s", *SAND)
n.floor_code("t", *DIRT)
n.floor_code("w", "pk:fishv/p4/6,10,1,1", "pk:fishv/p4/6,11,1,1", "pk:fishv/p4/5,10,1,1")   # доски набережной
n.piers = ("w",)
n.floor_code("~", *WATER)
n.floor_code("≈", *DEEP)
n.water_codes = ("~", "≈")
n.paint("s", 0, 0, W - 1, H - 1)


def bank(y):
    """Первая клетка воды в строке y: берег Колорадо гуляет плавно."""
    return int(round(56 + 1.8 * _m.sin(y / 5.0) + 1.0 * _m.sin(y / 2.3 + 2)))


for y in range(H):
    for x in range(bank(y), W):
        n.ground[y][x] = "≈" if x >= bank(y) + 4 else "~"
        n.blocked.add((x, y))
# мыс с маяком на севере — суша выдаётся в реку
for y in range(7, 14):
    for x in range(bank(y), bank(y) + 5 - abs(y - 10)):
        n.ground[y][x] = "s"
        n.blocked.discard((x, y))
# набережная: дощатый настил вдоль воды напротив города
for y in range(18, 38):
    for x in range(bank(y) - 3, bank(y)):
        n.ground[y][x] = "w"


def pier(y0, y1, x1):
    for y in range(y0, y1 + 1):
        for x in range(bank(y) - 1, x1 + 1):
            n.ground[y][x] = "w"
            n.blocked.discard((x, y))
    for y in (y0 - 1, y1 + 1):                    # сваи вдоль причала
        for x in range(bank(y) + 1, x1 + 1, 3):
            n.props.append(["nd_pile", x, y])


P("nd_pile", "pk:fishv/p1/9,15,1,1", block=False)
pier(23, 25, 63)                                   # главный причал — паром Кейт
pier(33, 34, 60)                                   # рыбацкие мостки
n._reach = None

n.exits = [(0, y) for y in range(23, 27)]
n.paint("a", 0, 23, 12, 26)                        # I-40 с запада
for x in range(0, 12, 4):
    n.ground[24][x] = n.ground[24][x + 1] = "h"
n.paint("t", 13, 22, bank(24) - 4, 27)             # Главная улица — до набережной
n.paint("t", 30, 8, 31, 21)                        # к вокзалу
n.paint("t", 44, 0, 46, 21)                        # вдоль реки к мосту
n.reserve(0, 22, 55, 27)
n.reserve(29, 8, 32, 21)
n.reserve(43, 0, 47, 21)
n.portal([(x, 0) for x in (44, 45, 46)], "needles_bridge", (6, 15), "Мост через Колорадо")

n.npcs += [["kate", 62, 24], ["fisher_joe", 59, 33], ["morrow_scout", 45, 6], ["preacher_eli", 17, 32],
           ["needles_girl", 36, 28], ["fishmonger", 50, 30], ["drunk_vic", 15, 18]]
for _, x, y in n.npcs:
    n.reserve(x, y, x, y)

# ---- вокзал Санта-Фе и пути: рельсы упираются в перрон у западной стены вокзала
n.building(24, 1, 16, 7, "brick", south=(6,))
n.portal([(30, 7), (31, 7)], "needles_depot", (14, 17), "Вокзал Санта-Фе")
TRACK = P("nd_track", "pk:wrail/p1/4,4,4,2", block=False, layer="floor")
for x in range(0, 24, 4):
    n.props.append([TRACK, x, 3])
WAGON = P("nd_freight", "pk:wrail/p1/10,12,2,1", foot=[2, 1], sight=True, scale=1.5)
n.put(WAGON, 4, 3, check=False)
n.put(WAGON, 8, 3, check=False)
n.put(BENCH, 26, 9)
n.put(BENCH, 36, 9)
n.put(STAGECOACH, 18, 8)
n.put(TROUGH, 15, 9)
# склад речников у дороги к мосту
n.put(CONT_R, 35, 11)
n.put(CONT_B, 38, 11)
n.put(BARRELS, 35, 14, allow_reserved=False) if False else None
n.box(JUNK, 41, 13, "куча хлама у склада", {"гаечный ключ": 1, "изолента": 1, "моторное масло": 1})
n.put(TRUCK, 48, 7)
n.put(CRANE, 49, 13)
n.put(TIRES, 48, 18)

# ---- Главная улица: северная сторона — салун, лавка, контора стражи
n.building(13, 13, 10, 9, "planks", south=(4,))
n.portal([(17, 21), (18, 21)], "needles_saloon", (13, 21), "Салун «Последний паром»")
n.building(25, 14, 8, 8, "planks", south=(2,))
n.portal([(27, 21), (28, 21)], "needles_shop", (7, 13), "Лавка «Всё для реки»")
n.building(35, 15, 8, 7, "brick", south=(2,))
n.put(TROUGH, 11, 20)
n.put(WEST_SIGN, 23, 20)
n.box(CRATE, 33, 20, "ящик у лавки", {"консервы": 2, "верёвка": 1, "крышки": 10})
for x in (12, 24, 33, 43):                         # фонари по обеим сторонам улицы
    n.maybe(LANTERN_POST, x, 22, allow_reserved=True)
for x in (12, 23, 33, 46):
    n.maybe(LANTERN_POST, x, 27, allow_reserved=True)
# уличная жизнь: у каждой двери — ящики, бочки, скамья; в колеях лужи; повозка у обочины
for x, y, name in ((14, 22, CRATE), (20, 22, "barrel_wood"), (22, 22, "crate_b"), (30, 22, BENCH), (34, 22, "crate_b"),
                   (40, 22, "barrel_wood"), (42, 22, CRATE), (15, 27, "barrel_wood"), (21, 27, "crate_b"),
                   (26, 27, "barrel_wood"), (31, 27, BENCH), (38, 27, CRATE), (41, 27, "barrel_wood"), (13, 27, "crate")):
    n.maybe(name, x, y, allow_reserved=True)
n.maybe(STAGECOACH, 46, 28, allow_reserved=True)
# ---- южная сторона: церковь, дома; за ними — дворы с заборами и кладбище
n.building(14, 29, 8, 8, "planks", north=(2,))
n.portal([(16, 29), (17, 29)], "needles_church", (8, 13), "Церковь")
n.building(24, 29, 8, 7, "planks", north=(2,))
n.building(34, 30, 8, 7, "brick", north=(2,))
n.box("wardrobe", 26, 33, "шкаф в доме рыбака", {"ткань": 2, "крышки": 8})
FENCE_W = P("nd_fence", "pk:fishv/p4/12,0,4,1", foot=[4, 1], keybg=True)
n.hwall([FENCE_W], 12, 42, 39, gaps=(23, 33))      # дворы за домами
for i, (x, y) in enumerate(((14, 41), (16, 41), (18, 41), (14, 43), (16, 43), (18, 43))):
    n.put("x_cross" if i % 2 else "x_grave", x, y)   # кладбище за церковью
n.put("x_cross", 15, 38)
for x, y in ((26, 41), (36, 41)):                  # огороды и бочки во дворах
    n.put(BARREL, x, y) if False else n.maybe("barrel_wood", x, y)
n.maybe(FISH_RACK, 28, 41)
n.maybe(FISH_RACK_B, 38, 41)

# ---- набережная и рыбный рынок: прилавки рядами вдоль прохода к причалу
for name, x, y in ((FISH_STALL, 44, 29), (FISH_STALL_B, 47, 29), (MEAT_STALL, 44, 32), (FISH_STALL, 47, 32)):
    n.put(name, x, y)
RACKS = [P("nd_rack_fish", "pk:fishv/p1/6,10,2,2", foot=[2, 1]), P("nd_rack_fish_b", "pk:fishv/p1/8,10,2,2", foot=[2, 1])]
for i, x in enumerate((44, 47)):
    n.put(RACKS[i], x, 35)
n.box(BARREL, 53, 29, "бочка с рыбой", {"вяленое мясо": 2})
for x, y in ((52, 31), (53, 36), (52, 19)):
    n.maybe("nd_barrel_plain", x, y) if False else n.maybe(CRATE, x, y)
NETS = P("nd_net_rack", "pk:fishv/p2/12,4,2,2", foot=[2, 1])
n.maybe(NETS, 50, 35)
n.put(ANCHOR, 50, 20)
for y in (21, 28):
    n.maybe(LANTERN_POST, bank(y) - 3, y, allow_reserved=True)
GULL = P("nd_gull", "pk:fishv/p4/14,1,1,1", block=False)
GULL_B = P("nd_gull_b", "pk:fishv/p4/12,2,1,1", block=False)
for x, y in ((55, 26), (52, 33), (58, 12)):
    n.maybe(GULL if x % 2 else GULL_B, x, y)

# ---- лодки: у причалов на воде; паром Кейт — у главного причала
ROWBOAT = P("nd_rowboat", "pk:fishv/p2/6,12,2,4", foot=[2, 3], block=False, layer="floor")
FERRY = P("nd_ferry", "pk:fishv/p4/12,4,4,2", foot=[4, 2], block=False, layer="floor", keybg=True)
SKIFF = P("nd_skiff", "pk:fishv/p4/12,6,4,2", foot=[4, 2], block=False, layer="floor", keybg=True)
n.put(FERRY, 59, 20, force=True)
n.put(ROWBOAT, 60, 26, force=True)
n.put(SKIFF, 56, 35, force=True)
n.put(ROWBOAT, 62, 30, force=True)

# ---- маяк на мысу, камни у воды
n.put(LIGHTHOUSE, bank(10) + 1, 9, force=True)
ROCKS_W = [P("nd_rock", "pk:fishv/p3/9,6,1,1", keybg=True), P("nd_rock_b", "pk:fishv/p3/13,3,1,1", keybg=True), P("nd_rock_c", "pk:fishv/p3/11,13,1,2", keybg=True)]
for i, (x, y) in enumerate(((bank(8), 8), (bank(12) + 1, 12), (bank(11) + 2, 11))):
    n.maybe(ROCKS_W[i], x, y)

# ---- южный берег: лодочный сарай и хижины на песке, лодки вытащены на берег
BOATHOUSE = P("nd_boathouse_big", "pk:fishv/p4/12,12,4,4", foot=[6, 3], sight=True, scale=1.6, keybg=True)
HUT = P("nd_fisher_hut", "pk:fishv/p4/12,8,2,3", foot=[3, 2], sight=True, scale=1.6, keybg=True)
n.put(BOATHOUSE, bank(42) - 8, 40)
n.put(HUT, 44, 41)
n.put(HUT, 41, 44)
n.put(ROWBOAT, bank(45) - 3, 44)                     # вытащена на песок
n.put(WRECK, 47, 46)
n.maybe(NETS, 46, 44)
n.maybe(BARREL, 43, 46) if False else n.maybe("barrel_wood", 43, 46)

# ---- пустыня на западе: кустами и камнями группами, у трассы — щит и брошенная машина
n.put("r_billboard", 6, 20)
n.put("r_car_wreck", 3, 28)
for cx, cy in ((4, 10), (8, 36), (3, 44), (20, 46), (32, 45)):
    for dx, dy, nm in ((0, 0, CACTUS), (2, 1, "r_rocks"), (1, 2, CACTUS_B), (3, -1, TUMBLE)):
        n.maybe(nm, cx + dx, cy + dy)
n.enemies += [["river_lizard", 52, 47], ["rat", 8, 44], ["rat", 11, 46]]

# ничего, кроме лодок, свай и чаек, не стоит в воде
from src import props as _P  # noqa: E402
for e in n.props:
    if e[0] in (ROWBOAT, FERRY, SKIFF, "nd_pile", GULL, GULL_B, LIGHTHOUSE):
        continue
    if _P.CATALOG.get(e[0], {}).get("layer") == "floor":
        continue
    for t in n.footprint(e[0], e[1], e[2]):
        assert n.ground[t[1]][t[0]] not in "~≈", f"needles: «{e[0]}» стоит в воде у {t}"


# ================================================================ мост
W, H = 64, 30
b = CityMap(city, "needles_bridge", "Мост через Колорадо", W, H, start=(6, 15), seed=92, music="raiders", night=[170, 152, 160])
b.floor_code("s", *SAND)
b.floor_code("~", *WATER)
b.floor_code("≈", *DEEP)
b.floor_code("k", "pk:fishv/p4/6,10,1,1", "pk:fishv/p4/6,11,1,1")   # дощатые мостки через пролом
b.piers = ("a", "h", "k")                                  # полотно моста и мостки — над водой, без берега
b.paint("s", 0, 0, W - 1, H - 1)
river(b, 14, 0, 51, H - 1)
b.paint("a", 0, 13, W - 1, 17)                           # полотно моста
for x in range(14, 52):
    for y in range(13, 18):
        b.blocked.discard((x, y))
for x in (32, 33, 34, 35):                               # обрушенный пролёт: дыра в полотне
    for y in range(13, 18):
        b.ground[y][x] = "≈"
        b.blocked.add((x, y))
for x in (32, 33, 34, 35):                               # мостки Речной стражи через пролом
    b.ground[15][x] = "k"
    b.blocked.discard((x, 15))
for x in range(0, W, 4):
    b.ground[15][x] = b.ground[15][x + 1] = "h" if b.ground[15][x] == "a" else b.ground[15][x]
RAIL = [P("nd_rail", "pk:wrail/p2/12,6,2,1", foot=[2, 1], keybg=True), P("nd_rail_b", "pk:wrail/p2/14,6,2,1", foot=[2, 1], keybg=True),
        P("nd_rail_broken", "pk:wrail/p2/10,7,2,1", foot=[2, 1], keybg=True)]
for x in range(14, 52):                                    # обочины моста — бетонный бортик под ограждением
    for y in (12, 18):
        if not 32 <= x <= 35:
            b.ground[y][x] = "a"
for x in range(14, 51, 2):                                 # ограждение моста: целое, местами сорвано; у пролома — нет
    if 32 <= x <= 35:
        continue
    for y in (12, 18):
        k = 2 if (x * 7 + y) % 9 == 0 else (x // 2) % 2
        b.put(RAIL[k], x, y, force=True)
for x in (31, 36):                                         # торчащая арматура у краёв пролома
    b.maybe("rebar_bits", x, 14, allow_reserved=True)
b.portal([(0, y) for y in range(13, 18)], "needles", (45, 2), "Нидлс")
b.exits = [(W - 1, y) for y in range(13, 18)]
b.reserve(0, 12, W - 1, 18)
# блокпост на западном въезде: контейнеры по обе стороны полотна, грузовик-ворота у южного края
b.put(CONT_R, 8, 10)
b.put(CONT_B, 8, 19)
b.put(TRUCK_B, 2, 21)
b.put(BARRELS, 5, 11)
b.put("x_fire_barrel", 9, 12, allow_reserved=True)
b.put("x_fire_barrel", 9, 18, allow_reserved=True)
b.terminal(4, 10, "needles_toll")
b.npcs += [["captain_morrow", 11, 14], ["river_guard", 12, 16], ["billy", 14, 17]]
b.enemies += [["raider_elite", 54, 14], ["raider", 57, 16], ["raider", 59, 13], ["sniper", 60, 15]]
b.box(CRATE, 5, 20, "ящик Речной стражи", {"патроны": 15, "дробь": 6, "бинт": 2}, owner="captain_morrow")
b.put("r_car_wreck", 22, 14, allow_reserved=True)
b.put("r_car_b", 44, 16, allow_reserved=True)
b.put(TIRES, 27, 16, allow_reserved=True)
# река живёт: камни и коряги в воде, плоты и брошенные лодки у быков моста, коряги и костры на берегах, лампы на мосту, граффити Стражи
for x, y in ((18, 6), (24, 4), (40, 5), (46, 8), (20, 24), (28, 26), (42, 22), (47, 25), (38, 27), (16, 9)):
    b.maybe(["r_rocks", "rock_grass", "rock_grass_b"][(x + y) % 3], x, y)
for x, y in ((21, 8), (44, 10), (26, 22), (36, 25)):
    b.maybe("r_logs" if (x + y) % 2 else "r_planks", x, y)
for x in range(16, 50, 6):
    if not 31 <= x <= 36:
        b.maybe("r_streetlamp" if x % 4 else "r_streetlamp_b", x, 12, allow_reserved=True)
for x, y in ((6, 5), (6, 24), (58, 6), (60, 24)):
    b.maybe("x_fire_barrel", x, y, check=False)
for x, y in ((3, 4), (4, 26), (56, 26), (61, 4), (2, 12), (62, 20)):
    b.maybe("r_dry_bush", x, y)
b.scatter(["r_rocks", "pile_tires", "crate_broken", "pile_rags", "r_trash", "r_bones"], 1, 1, 12, H - 2, 8)
b.scatter(["r_rocks", "r_bones", "r_trash", "pile_scrap", "pile_tires"], 52, 1, W - 2, H - 2, 8)
for x, y in ((16, 14), (20, 16), (26, 13), (40, 14), (47, 16)):
    b.maybe("x_vd_blood0", x, y, check=False)
for x, y in ((18, 13), (28, 16), (42, 15)):
    b.maybe("x_vd_oil0", x, y, check=False)


# ================================================================ салун
sl = CityMap(city, "needles_saloon", "Салун «Последний паром»", 28, 24, start=(13, 21), seed=93, interior=True,
             music="junktown")
sl.floor_code("F", *SALOON_FLOOR)
sl.wall_code("W", "pk:west/west_w1_04")
sl.room(1, 1, 26, 23, "W", "F")
sl.opening(13, 23, 14, 23, "F")
sl.portal([(13, 23), (14, 23)], "needles", (17, 22), "На улицу")
# стойка вдоль северной стены, буфет за ней, бармен — между
sl.put(BAR_STOOLS, 4, 6)
sl.put(CABINET, 3, 4)
sl.put(CABINET, 8, 4)
sl.put(CLOCK, 12, 4)
sl.npcs += [["barkeep_ned", 6, 5]]
# пианино в углу, столы для покера и обычные — рядами, стулья у столов
# зал салуна (набор wild-west): круглые игорные столы, стулья по обе стороны, ковры, картины и окна на стенах
CARD = [P("nd_card_table", "pk:west/west_2_020", foot=[2, 1]), P("nd_card_table_b", "pk:west/west_2_021", foot=[2, 1])]
CH_L, CH_R = P("nd_chair_l", "pk:west/west_2_001"), P("nd_chair_r", "pk:west/west_2_002")
RUGS = [P("nd_rug_red", "pk:west/west_2_060", block=False, layer="floor", foot=[2, 2], scale=1.5),
        P("nd_rug_quilt", "pk:west/west_2_062", block=False, layer="floor", foot=[2, 2], scale=1.5)]
WALL_ART = [P("nd_painting", "pk:west/west_2_030", block=False), P("nd_mona", "pk:west/west_2_029", block=False),
            P("nd_window", "pk:west/west_2_027", block=False), P("nd_wall_clock", "pk:west/west_2_011", block=False)]
PLANTS = [P("nd_plant", "pk:west/west_2_031"), P("nd_plant_b", "pk:west/west_2_042"), P("nd_plant_c", "pk:west/west_2_033")]
STOVE_W = P("nd_fireplace", "pk:west/west_2_010", foot=[2, 1], light={"r": 130, "color": [255, 150, 70], "at": [0.5, 0.7], "flicker": 0.4})
for i, x in enumerate((15, 18, 21, 24)):                     # на северной стене — картины, окно, часы
    sl.props.append([WALL_ART[i % 4], x, 3, 0, -14])
sl.put(PIANO, 20, 4)
sl.maybe(STOVE_W, 15, 4)
for i, (x, y) in enumerate(((3, 10), (9, 10), (16, 10), (21, 10), (3, 15), (9, 16), (16, 15), (21, 16))):
    sl.props.append([RUGS[0], x, y, 0, -12])               # ковёр — под столом, по центру группы
    sl.maybe(CARD[i % 2], x, y)
    sl.maybe(CH_L, x - 1, y)
    sl.maybe(CH_R, x + 2, y)
for i, (x, y) in enumerate(((2, 6), (25, 6), (2, 19), (25, 19))):      # кадки в углах
    sl.maybe(PLANTS[i % 3], x, y)
for x, y in ((2, 21), (3, 21)):
    sl.maybe("barrel_wood", x, y)
for x, y in ((24, 21), (25, 21)):
    sl.maybe("crate", x, y)
sl.npcs += [["gambler_lou", 6, 12], ["river_guard_off", 18, 17]]
sl.box(SAFE, 24, 4, "сейф салуна", {"крышки": 140, "сигареты": 3},
       requires={"items_any": ["отмычка", "ключ от сейфа салуна"], "msg": "Старый банковский сейф. Без отмычки — никак."})


# ================================================================ вокзал
dp = CityMap(city, "needles_depot", "Вокзал Санта-Фе", 30, 20, start=(14, 17), seed=94, interior=True, music="caves")
dp.floor_code("T", *TILE)
dp.floor_code("P", *PLANK)
dp.wall_code("K", "pk:hotel/hotel_w1_14")
WAIT = dp.room(1, 1, 20, 19, "K", "T")
BAG = dp.room(20, 1, 29, 19, "K", "P")
dp.opening(13, 19, 14, 19, "T")
dp.portal([(13, 19), (14, 19)], "needles", (30, 8), "На привокзальную площадь")
dp.opening(20, 9, 20, 10, "T")
# зал ожидания: скамьи рядами, касса у северной стены, часы
for y in (8, 12):
    for x in (3, 9, 15):
        dp.put(BENCH, x, y)
dp.put("counter", 6, 4)
dp.put("counter", 8, 4)
dp.put(CLOCK, 12, 4)
dp.box("cabinet_small", 4, 4, "касса", {"крышки": 30, "билет до Барстоу": 1})
# багажное отделение: чемоданы и ящики вдоль стен — логово ящеров
for x, y in ((22, 4), (25, 4), (27, 4)):
    dp.put(SUITCASES, x, y)
dp.box(CRATE, 22, 16, "почтовый мешок 2077 года", {"письмо": 1, "плюшевый мишка": 1, "консервы": 1,
                                                    "кинолента «Пески Мохаве»": 1})
dp.put(BARRELS, 26, 16)
dp.enemies += [["river_lizard", 24, 10], ["river_lizard", 27, 12], ["radroach", 23, 14]]
# вокзал (набор railway-station): табло и окна на стене, мусор, перевёрнутые стулья, чемоданы
STATION_SIGN = P("nd_station_sign", "pk:wrail/p2/0,8,4,2", block=False)
DELAYED = P("nd_delayed", "pk:wrail/p2/10,0,2,1", block=False)
WIN_BROKEN = [P("nd_win_broken", "pk:wrail/p2/6,0,2,2", block=False), P("nd_win_broken_b", "pk:wrail/p2/8,2,2,2", block=False)]
SEATS = [P("nd_seats", "pk:wrail/p2/4,0,2,1", foot=[2, 1]), P("nd_seat_fallen", "pk:wrail/p2/2,4,2,1", foot=[2, 1])]
LUGGAGE = [P("nd_luggage", "pk:wrail/p2/0,12,1,1"), P("nd_luggage_b", "pk:wrail/p2/2,12,2,1", foot=[2, 1]),
           P("nd_luggage_c", "pk:wrail/p2/2,13,1,1")]
dp.props.append([STATION_SIGN, 8, 3, 0, -6])
dp.props.append([DELAYED, 15, 3, 0, -20])
for i, x in enumerate((3, 17, 23, 26)):
    dp.props.append([WIN_BROKEN[i % 2], x, 3, 0, -6])
for x, y in ((4, 15), (16, 15), (10, 16)):
    dp.maybe(SEATS[(x + y) % 2], x, y)
for i, (x, y) in enumerate(((21, 7), (28, 8), (23, 18), (28, 15), (6, 17))):
    dp.maybe(LUGGAGE[i % 3], x, y)
for x, y in ((12, 14), (18, 6), (2, 10)):
    dp.maybe("pile_bottles" if x % 2 else "r_trash", x, y)

# ================================================================ лавка
sh = CityMap(city, "needles_shop", "Лавка «Всё для реки»", 16, 16, start=(7, 13), seed=95, interior=True, music="hub")
sh.floor_code("F", *SALOON_FLOOR)
sh.wall_code("W", "pk:west/west_w1_04")
sh.room(1, 1, 14, 15, "W", "F")
sh.opening(7, 15, 8, 15, "F")
sh.portal([(7, 15), (8, 15)], "needles", (27, 22), "На улицу")
# прилавок поперёк лавки, за ним — полки с товаром вдоль стены; торговка за прилавком
sh.put("counter", 4, 8)
sh.put("counter", 9, 8)
sh.put(CABINET, 3, 4)
sh.put(BOOKS, 6, 4)
sh.put(CABINET, 10, 4)
sh.put(NET, 12, 6)
sh.put(BARREL, 2, 12)
sh.put(CRATE, 13, 12)
sh.npcs += [["shopkeeper_rosa", 7, 6]]
# лавка речника: вёсла и сети на стене, бочки и корзины у прилавка, кадка у двери
OARS = P("nd_oars", "pk:fishv/p1/2,6,2,2", block=False)
BASKET = P("nd_basket", "pk:fishv/p1/12,2,2,2", foot=[2, 1])
CRATE_FISH = P("nd_crate_fish", "pk:fishv/p2/4,0,2,1", foot=[2, 1])
sh.props.append([OARS, 12, 3, 0, -10])
sh.props.append(["nd_window", 8, 3, 0, -14])
sh.maybe(BASKET, 2, 9)
sh.maybe(CRATE_FISH, 11, 10)
sh.maybe("nd_plant", 13, 14)
sh.maybe("nd_plant_b", 2, 14)
sh.props.append(["nd_rug_red", 7, 11, 0, 0])

# ================================================================ церковь
ch = CityMap(city, "needles_church", "Церковь проповедника Эли", 16, 16, start=(8, 13), seed=96, interior=True,
             music="vats")
ch.floor_code("F", *SALOON_FLOOR)
ch.wall_code("W", "pk:west/west_w1_04")
ch.room(1, 1, 14, 15, "W", "F")
ch.opening(7, 15, 8, 15, "F")
ch.portal([(7, 15), (8, 15)], "needles", (16, 28), "На улицу")
# кафедра у северной стены, скамьи рядами с проходом посередине
ch.put("display_case_b", 7, 4)
ch.put("candles", 5, 4)
ch.put("candles", 10, 4)
for y in (7, 9, 11):
    ch.put("bench_7", 3, y)
    ch.put("bench_7", 10, y)
ch.box("cabinet_small", 13, 4, "ящик для пожертвований", {"крышки": 35, "бинт": 1})
ch.npcs += [["noa_runaway", 2, 5]]
# церковь: дорожка-ковёр от двери к кафедре, окна с занавесями, распятие и свечи, кадки
RUNNER = P("nd_runner", "pk:west/west_2_061", block=False, layer="floor", foot=[2, 2], scale=1.15)
for y in (6, 8, 10, 12):
    ch.props.append([RUNNER, 7, y])
for x in (3, 12):
    ch.props.append(["nd_window", x, 3, 0, -14])
ch.props.append(["x_cross", 7, 3, 24, -20])
for x, y in ((2, 13), (13, 13)):
    ch.maybe("nd_plant_c", x, y)
for x, y in ((4, 4), (11, 4)):
    ch.maybe("lantern_lit", x, y)         # беглянка из конвоя культа прячется за кафедрой

city.save(gap_exempt=("captain_morrow", "river_guard", "barkeep_ned", "gambler_lou", "river_guard_off",
                      "kate", "fisher_joe", "fishmonger", "shopkeeper_rosa"))
L = json.load(open("data/locations.json", encoding="utf-8"))
L["needles"].update({"world_name": "Нидлс", "discover": True})
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
