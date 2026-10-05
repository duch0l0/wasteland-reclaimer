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
BOAT = P("nd_boat", "pk:fishv/p3/0,10,2,1", foot=[2, 1], block=False, layer="floor")
BOAT_B = P("nd_boat_b", "pk:fishv/p3/0,11,2,1", foot=[2, 1], block=False, layer="floor")
SAILBOAT = P("nd_sailboat", "pk:fishv/p3/4,10,4,2", foot=[4, 2], block=False, layer="floor")
FISH_STALL = P("nd_fish_stall", "pk:fishv/p3/8,8,2,2", foot=[2, 1], sight=True)
FISH_STALL_B = P("nd_fish_stall_b", "pk:fishv/p3/10,8,2,2", foot=[2, 1], sight=True)
MEAT_STALL = P("nd_meat_stall", "pk:fishv/p3/10,10,2,2", foot=[2, 1], sight=True)
LIGHTHOUSE = P("nd_lighthouse", "pk:fishv/p3/8,10,1,2", foot=[1, 1], sight=True)
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
LANTERN_POST = P("nd_lantern_post", "pk:fishv/p4/14,8,1,2", foot=[1, 1],
                 light={"r": 160, "color": [255, 170, 90], "at": [0.6, 0.15], "flicker": 0.3})
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
BENCH = P("nd_bench", "pk:wrail/p1/9,2,2,1", foot=[2, 1])
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
RUG = P("nd_rug", "pk:west/west_2_060", block=False, layer="floor")
SAFE = P("nd_safe", "pk:west/west_2_105", search="military", title="сейф")
SUITCASES = P("nd_suitcases", "pk:wrail/wrail_1_014", search="bag", title="чемоданы")

SAND = cells("destown/p2", [(0, 0), (1, 0), (0, 1), (1, 1)])      # ровный песок (как в Зайзиксе)
DIRT = cells("destown/p2", [(4, 0), (5, 0), (4, 1), (5, 1)])      # укатанный гравий улиц
PLANK = ["pk:seaport/seaport_f1_21"]
STONE = ["pk:seaport/seaport_f1_26"]
WATER = cells("mport/p1", [(8, 4), (9, 4), (10, 4), (11, 4), (8, 5), (9, 5), (10, 5), (11, 5)])
DEEP = cells("mport/p1", [(8, 6), (9, 6), (10, 6), (11, 6)])
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
W, H = 72, 50
n = CityMap(city, "needles", "Нидлс: Пристань", W, H, start=(2, 24), seed=91, music="hub",
            world_pos=(2470, 1470))
n.floor_code("s", *SAND)
n.floor_code("t", *DIRT)
n.floor_code("w", *PLANK)
n.floor_code("~", *WATER)
n.floor_code("≈", *DEEP)
n.paint("s", 0, 0, W - 1, H - 1)
n.exits = [(0, y) for y in range(23, 27)]
n.paint("a", 0, 23, 12, 26)                             # I-40 с запада
for x in range(0, 12, 4):
    n.ground[24][x] = n.ground[24][x + 1] = "h"
n.paint("t", 13, 22, 52, 27)                            # Главная улица — укатанная земля
n.paint("t", 30, 8, 31, 21)                             # дорога к станции
n.paint("t", 44, 4, 46, 21)                             # дорога вдоль реки к мосту
river(n, 56, 0, W - 1, H - 1)                           # Колорадо
n.paint("w", 53, 22, 55, 27)                            # набережная
pier(n, 56, 23, 63, 25)                                 # главный причал
pier(n, 56, 33, 60, 34)                                 # рыбацкие мостки
pier(n, 56, 14, 58, 16)
n.reserve(0, 22, 55, 27)          # сама улица; дома стоят вдоль неё
n.reserve(29, 8, 32, 21)
n.reserve(43, 3, 47, 21)
n.portal([(x, 0) for x in (44, 45, 46)], "needles_bridge", (6, 15), "Мост через Колорадо")

n.npcs += [["kate", 62, 24], ["fisher_joe", 59, 33], ["morrow_scout", 45, 6], ["preacher_eli", 17, 32],
           ["needles_girl", 36, 28], ["fishmonger", 50, 30], ["drunk_vic", 15, 18]]
for _, x, y in n.npcs:
    n.reserve(x, y, x, y)

# станция Санта-Фе (север): кирпичный вокзал, вход посередине южной стены; пути и вагоны западнее
n.building(24, 1, 16, 7, "brick", south=(6,))
n.portal([(30, 7), (31, 7)], "needles_depot", (14, 17), "Вокзал Санта-Фе")
n.put(BENCH, 26, 9)
n.put(BENCH, 36, 9)
n.put(RAIL_WAGON, 14, 3)
n.put(RAIL_WAGON, 17, 3)
n.put(STAGECOACH, 18, 8)

# Главная улица, северная сторона: салун, лавка, контора Речной стражи — двери на улицу
n.building(13, 13, 10, 9, "planks", south=(4,))           # салун «Последний паром»
n.portal([(17, 21), (18, 21)], "needles_saloon", (13, 21), "Салун «Последний паром»")
n.building(25, 14, 8, 8, "planks", south=(2,))            # лавка
n.portal([(27, 21), (28, 21)], "needles_shop", (7, 13), "Лавка «Всё для реки»")
n.building(35, 15, 8, 7, "brick", south=(2,))             # контора Речной стражи (заперта)
n.put(TROUGH, 11, 20)                                     # поилка у салуна
n.put(WEST_SIGN, 23, 20)
n.box(CRATE, 33, 20, "ящик у лавки", {"консервы": 2, "верёвка": 1, "крышки": 10})
# южная сторона: церковь Эли и дома, двери на улицу (в северной стене)
n.building(14, 29, 8, 8, "planks", north=(2,))            # церковь
n.put("x_cross", 15, 38)
n.portal([(16, 29), (17, 29)], "needles_church", (8, 13), "Церковь")
n.building(24, 29, 8, 7, "planks", north=(2,))
n.building(34, 30, 8, 7, "brick", north=(2,))
n.box("wardrobe", 26, 33, "шкаф в доме рыбака", {"ткань": 2, "крышки": 8})
# набережная и рынок: прилавки рядом, бочки и сети у воды
n.put(FISH_STALL, 47, 28)
n.put(FISH_STALL_B, 50, 28)
n.put(MEAT_STALL, 47, 32)
n.put(FISH_RACK, 51, 34)
n.put(FISH_RACK_B, 48, 35)
n.box(BARREL, 53, 29, "бочка с рыбой", {"вяленое мясо": 2})
n.put(NET, 54, 31)
n.put(ANCHOR, 54, 21)
n.put(LANTERN_POST, 53, 21)
n.put(LANTERN_POST, 53, 28)
# лодочные сараи и рыбацкие мостки — южнее
n.put(HOUSE_W, 44, 37)                                     # рыбацкие хижины у воды
n.put(HOUSE_T2, 44, 41)
n.put(SHED, 50, 38)
n.put(SHED_B, 53, 41)
n.put(WRECK, 47, 44)
n.put(BOAT, 61, 33, force=True)
n.put(BOAT_B, 57, 36, force=True)
# паром Мамаши Кейт у главного причала, лодки у мостков
n.put(SAILBOAT, 64, 22, force=True)
n.put(BOAT, 58, 27, force=True)
n.put(LIGHTHOUSE, 57, 15)            # маяк на мостках к северу от причала
# склад речников между вокзалом и дорогой к мосту: два контейнера в ряд, бочки и хлам перед ними
n.put(CONT_R, 34, 10)
n.put(CONT_B, 38, 10)
n.put(BARRELS, 35, 13)
n.box(JUNK, 39, 13, "куча хлама у склада", {"гаечный ключ": 1, "изолента": 1, "моторное масло": 1})
# у реки, за дорогой к мосту: грузовик и портовый кран
n.put(TRUCK, 48, 8)
n.put(CRANE, 50, 12)
n.put(TIRES, 49, 17)
# пустыня на западе
n.scatter([CACTUS, CACTUS_B, TUMBLE], 1, 1, 22, 20, 10)
n.scatter([CACTUS, CACTUS_B, TUMBLE, "r_rocks"], 1, 30, 45, H - 2, 12)
n.enemies += [["river_lizard", 52, 47], ["rat", 8, 44], ["rat", 11, 46]]


# ================================================================ мост
W, H = 64, 30
b = CityMap(city, "needles_bridge", "Мост через Колорадо", W, H, start=(6, 15), seed=92, music="raiders")
b.floor_code("s", *SAND)
b.floor_code("~", *WATER)
b.floor_code("≈", *DEEP)
b.floor_code("k", *STONE)
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
b.npcs += [["captain_morrow", 11, 14], ["river_guard", 12, 16]]
b.enemies += [["raider_elite", 54, 14], ["raider", 57, 16], ["raider", 59, 13], ["sniper", 60, 15]]
b.box(CRATE, 5, 20, "ящик Речной стражи", {"патроны": 15, "дробь": 6, "бинт": 2}, owner="captain_morrow")
b.put("r_car_wreck", 22, 14, allow_reserved=True)
b.put("r_car_b", 44, 16, allow_reserved=True)
b.put(TIRES, 27, 16, allow_reserved=True)


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
sl.put(PIANO, 22, 4)
for x, y in ((4, 11), (10, 11), (17, 11), (4, 16), (17, 16)):
    sl.put(POKER if (x + y) % 3 == 0 else TABLE, x, y)
    sl.put(CHAIR, x + 2, y)
sl.put(RUG, 11, 16)
sl.npcs += [["gambler_lou", 6, 12], ["river_guard_off", 18, 17]]
sl.box(SAFE, 24, 4, "сейф салуна", {"крышки": 140, "сигареты": 3},
       requires={"item": "отмычка", "msg": "Старый банковский сейф. Без отмычки — никак."})


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
dp.box(CRATE, 22, 16, "почтовый мешок 2077 года", {"письмо": 1, "плюшевый мишка": 1, "консервы": 1})
dp.put(BARRELS, 26, 16)
dp.enemies += [["river_lizard", 24, 10], ["river_lizard", 27, 12], ["radroach", 23, 14]]

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

city.save(gap_exempt=("captain_morrow", "river_guard", "barkeep_ned", "gambler_lou", "river_guard_off",
                      "kate", "fisher_joe", "fishmonger", "shopkeeper_rosa"))
L = json.load(open("data/locations.json", encoding="utf-8"))
L["needles"].update({"world_name": "Нидлс", "discover": True})
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
