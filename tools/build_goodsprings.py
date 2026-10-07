"""
Гудспрингс — тихий посёлок у источника. Третий акт.
Сценарий — docs/story.md, раздел «Гудспрингс — „Колокол и мальчик“».

  goodsprings         «Гудспрингс» (70×50): улица между холмами; салун «Старатель», лавка, дом старосты,
                      дом дока, ферма с загоном, колодец и колокол на площади, бензоколонка; на холме —
                      кладбище; на севере — пещера источника. Дорога на северо-восток — к Убежищу 22.
  goodsprings_saloon  салун «Старатель»: стойка, столы, задняя комната трактирщицы Труди — там прячут мальчика.
  goodsprings_doc     дом дока Митчелла: приёмная, койка, шкаф с лекарствами, записи наблюдений за мальчиком.
  goodsprings_cave    пещера источника: родник, гекконы — и старый тайник, куда можно спрятать мальчика.

Наборы: abandoned-rural-village (rvill), wild-west (west), desert-natural (desnat), desert-town (destown),
west, ucamp, grave, zombie-city (zcity), goblin-cave (gcave).
Запуск из папки game_project:  .venv/bin/python tools/build_goodsprings.py
"""
import json

from citykit import City, CityMap

city = City("goodsprings", "Гудспрингс")


def P(name, img, **kw):
    city.prop(name, img, **kw)
    return name


def cells(page, pts):
    return [f"pk:{page}/{x},{y},1,1" for x, y in pts]


S = 1.5   # дома и деревья деревни — крупнее, под рост героя
HOUSES = [P(f"gs_house{i}", f"pk:rvill/rvill_1_{n:03d}", scale=S, foot=[3, 2], sight=True)
          for i, n in enumerate((0, 24, 25, 26, 4, 41, 102))]
SHED = P("gs_shed", "pk:rvill/rvill_1_036", scale=S, foot=[3, 2], sight=True)
BARN = P("gs_barn", "pk:rvill/rvill_1_006", scale=S, foot=[3, 2], sight=True)
RUIN = P("gs_ruin", "pk:rvill/rvill_1_042", scale=S, foot=[3, 2], sight=True)
WELL = P("gs_well", "pk:rvill/rvill_1_060", foot=[2, 1])
STONE_WALL = [P("gs_stone_wall", "pk:rvill/rvill_1_047", foot=[2, 1]), P("gs_stone_wall_b", "pk:rvill/rvill_1_048", foot=[2, 1])]
DEAD_TREES = [P(f"gs_tree{i}", f"pk:rvill/rvill_2_{n:03d}", scale=S, foot=[2, 1]) for i, n in enumerate((10, 11, 12))]
BUSHES = [P("gs_bush_berry", "pk:rvill/rvill_2_033", foot=[2, 1]), P("gs_bush_blue", "pk:rvill/rvill_2_034", foot=[2, 1])]
GRASS = [P(f"gs_grass{i}", f"pk:rvill/rvill_2_{n:03d}", block=False) for i, n in enumerate((1, 2, 5, 6))]
CACTI = [P("gs_cactus", "pk:west/west_1_008"), P("gs_cactus_b", "pk:west/p1/12,0,1,2", foot=[1, 1])]
FENCE = [P("gs_fence", "pk:west/west_1_013", foot=[2, 1]), P("gs_fence_b", "pk:west/west_1_014"),
         P("gs_fence_c", "pk:west/west_1_015")]
TROUGH = P("gs_trough", "pk:west/west_1_016")
BARREL = P("gs_barrel", "pk:west/west_1_017", search="junk", title="бочка")
CRATE = P("gs_crate", "pk:west/west_1_018", search="crate", title="ящик")
STAGECOACH = P("gs_wagon", "pk:west/west_1_011", foot=[2, 1], sight=True)
SIGN = P("gs_sign", "pk:west/p1/12,4,2,2", foot=[2, 1])
BELL = P("gs_bell", "pk:cult/cult_2_131", sight=True)                       # колокол на столбе
GAS_PUMP = P("gs_gas_pump", "pk:zcity/zcity_1_134")
WRECK = P("gs_wreck", "pk:zcity/zcity_2_034", foot=[2, 1], sight=True)
CAMPFIRE = P("gs_campfire", "pk:ucamp/ucamp_2_040", foot=[2, 1],
             light={"r": 120, "color": [255, 150, 70], "at": [0.5, 0.5], "flicker": 0.35})
LAMP = P("gs_lamp", "pk:apark/apark_3_070", light={"r": 140, "color": [255, 200, 130], "at": [0.5, 0.1]})
GRAVE_STATUE = P("gs_angel", "pk:grave/grave_2_034")
DEAD_TREE_G = P("gs_grave_tree", "pk:grave/grave_2_019", foot=[2, 1])
# интерьеры
BAR = P("gs_bar", "pk:west/west_2_108", foot=[4, 1])
BOTTLES = P("gs_bottle_shelf", "pk:west/west_2_110", sight=True, search="shelf", title="полка с бутылками")
TABLE = P("gs_table", "pk:west/west_2_000", foot=[2, 1])
CHAIR = P("gs_chair", "pk:west/west_2_001")
PIANO = P("gs_piano", "pk:west/west_2_012", foot=[2, 1])
BED = P("gs_bed", "pk:west/west_2_005", foot=[2, 2])
BOOKS = P("gs_bookcase", "pk:west/west_2_116", sight=True, search="shelf", title="книжный шкаф")
CLOCK = P("gs_clock", "pk:west/west_2_019", sight=True)
SAFE = P("gs_safe", "pk:west/west_2_105", search="military", title="сейф")
MED_SHELF = P("gs_med_shelf", "pk:hosp/hosp_1_009", sight=True, search="drawer", title="шкаф с лекарствами")
HOSP_BED = P("gs_hosp_bed", "pk:hosp/hosp_1_007", foot=[3, 1])
COT = P("gs_cot", "pk:ucamp/ucamp_3_027", foot=[4, 1])
# пещера
MUSH = [P("gs_mush", "pk:gcave/p1/2,4,1,1", light={"r": 60, "color": [140, 255, 170], "at": [0.5, 0.5]}),
        P("gs_mush_b", "pk:gcave/p1/2,5,1,1", light={"r": 60, "color": [120, 200, 255], "at": [0.5, 0.5]})]
BOULDERS = [P("gs_boulder", "pk:gcave/p1/4,4,1,1"), P("gs_boulder_b", "pk:gcave/p1/5,4,1,1")]

SAND = cells("destown/p2", [(0, 0), (1, 0), (0, 1), (1, 1)])
DIRT = cells("rvill/p2", [(0, 11), (1, 11), (0, 12), (1, 12)])
ROAD = cells("west/p1", [(0, 1), (1, 1), (0, 2), (1, 2)])          # красная укатанная колея
STONE = cells("west/p1", [(4, 0), (5, 0), (4, 1), (5, 1)])         # булыжник площади
PLANK = ["pk:bazaar/bazaar_f1_21"]
CAVE_DIRT = cells("gcave/p1", [(1, 4), (1, 5), (2, 6), (3, 6)])
SPRING = cells("sewer/p1", [(10, 1), (11, 1)])


# ================================================================ посёлок
W, H = 70, 50
gs = CityMap(city, "goodsprings", "Гудспрингс", W, H, start=(1, 30), seed=181, music="desert", world_pos=(2330, 560))
gs.floor_code("s", *SAND)
gs.floor_code("d", *DIRT)
gs.floor_code("r", *ROAD)
gs.floor_code("t", *STONE)
gs.paint("s", 0, 0, W - 1, H - 1)
gs.paint("d", 6, 14, 62, 42)                            # утоптанная земля посёлка
gs.paint("r", 0, 29, W - 1, 32)                         # улица
gs.paint("r", 33, 10, 36, 29)                           # проезд к пещере
gs.paint("t", 28, 22, 41, 28)                           # площадь у колодца
gs.exits = [(0, y) for y in range(29, 33)] + [(W - 1, y) for y in range(29, 33)]
gs.reserve(0, 29, W - 1, 32)
gs.reserve(33, 10, 36, 28)

# площадь: колодец и колокол — бить тревогу, если придёт культ
gs.put(WELL, 30, 24)
gs.put(BELL, 39, 24)
gs.put(LAMP, 28, 22)
gs.put(LAMP, 41, 22)
gs.put(TROUGH, 31, 27)

# север улицы: салун «Старатель» (большой, с крышей), лавка, дом старосты
gs.building(10, 16, 14, 11, "planks", south=(6,))       # салун
gs.reserve(16, 27, 17, 28)
gs.put(SIGN, 12, 27)
gs.put(BARREL, 22, 27)
gs.put(HOUSES[0], 44, 18)                               # лавка Чета
gs.put(CRATE, 48, 20)
gs.put(HOUSES[1], 52, 18)                               # дом старосты Петтита
# юг улицы: дом дока Митчелла (с крышей — заходят внутрь), жилые дома, ферма с загоном
gs.building(26, 34, 10, 8, "planks", north=(4,))       # дом дока
gs.reserve(30, 32, 31, 34)
gs.put(HOUSES[2], 8, 35)
gs.put(HOUSES[3], 14, 35)
gs.put(HOUSES[4], 42, 35)
gs.put(BARN, 50, 35)
gs.hwall(FENCE, 49, 61, 40, gaps=(55, 56))
gs.vline([FENCE[1]], 61, 34, 39)
gs.put(TROUGH, 57, 37)
gs.put(STAGECOACH, 20, 37)
# запад: бензоколонка у въезда
gs.put(GAS_PUMP, 4, 26)
gs.put(GAS_PUMP, 6, 26)
gs.put(WRECK, 3, 35)
# восток: дорога на Убежище 22 — указатель, развалины
gs.put(RUIN, 63, 22)
gs.put(SIGN, 64, 34)

# холм на северо-западе: кладбище за каменной оградой
gs.hwall(STONE_WALL, 4, 22, 3)
gs.hwall(STONE_WALL, 4, 22, 12, gaps=(13, 14))
for row, y in enumerate((5, 8)):
    for x in range(6, 22, 3):
        gs.maybe("x_grave" if (x + row) % 2 else "x_cross", x, y)
gs.put(GRAVE_STATUE, 13, 6)
gs.put(DEAD_TREE_G, 19, 10)
gs.npcs += [["gravedigger_gs", 10, 10]]

# пещера источника на севере — тропа, камни, вход
gs.props.append(["x_puddle", 34, 4])
gs.portal([(33, 3), (34, 3), (35, 3)], "goodsprings_cave", (8, 30), "Пещера источника")
gs.reserve(32, 3, 37, 9)
for x, y in ((28, 3), (40, 4), (30, 8), (39, 8)):
    gs.put(CACTI[0], x, y)

gs.npcs += [["cult_hunter", 66, 27]]                       # брат-ловчий ждёт у восточного въезда
gs.npcs += [["sunny", 26, 30], ["chet", 46, 22], ["mayor_pettit", 54, 22], ["gs_farmer", 55, 38], ["gs_kid", 38, 27],
            ["gs_old", 32, 22]]
gs.box("r_trash_can", 20, 25, "мусорный бак за салуном", {"фартук в крови": 1, "ткань": 1})
for _, x, y in gs.npcs:
    gs.reserve(x, y, x, y)
gs.grow(1, 1, W - 2, H - 2, 9, names=CACTI + BUSHES + DEAD_TREES)
gs.scatter(GRASS + ["r_rocks"], 1, 1, W - 2, H - 2, 30)


# ================================================================ салун «Старатель»
sl = CityMap(city, "goodsprings_saloon", "Салун «Старатель»", 30, 22, start=(13, 20), seed=182, interior=True,
             music="desert")
sl.floor_code("F", *PLANK)
sl.wall_code("W", "pk:bazaar/bazaar_w2_12")
sl.room(1, 1, 20, 21, "W", "F")                       # зал
sl.room(20, 1, 29, 21, "W", "F")                      # задняя комната Труди — тайник
sl.opening(13, 21, 14, 21, "F")
gs.portal([(16, 26), (17, 26)], "goodsprings_saloon", (13, 19), "Салун «Старатель»")
sl.portal([(13, 21), (14, 21)], "goodsprings", (16, 28), "На улицу")
sl.opening(20, 14, 20, 15, "F")
sl.put(BOTTLES, 3, 4)
sl.put(BOTTLES, 8, 4)
sl.put(BAR, 3, 7)
sl.put(BAR, 7, 7)
sl.put(CLOCK, 13, 4)
sl.put(PIANO, 16, 4)
for x, y in ((3, 11), (9, 11), (3, 16), (14, 12)):
    sl.put(TABLE, x, y)
    sl.put(CHAIR, x + 2, y)
sl.npcs += [["trudy", 6, 5], ["gs_drunk", 10, 13], ["gs_prospector", 15, 17]]
# «Кто убил Гаррисона?»: тело у стойки, помощница шерифа и трое из того вечера
sl.box("bag", 10, 8, "тело Гаррисона", {"часы Гаррисона": 1, "записка из кармана Гаррисона": 1, "крышки": 12})
sl.npcs += [["deputy_abby", 12, 18], ["luis_cards", 8, 14], ["beth_waitress", 5, 9], ["hank_miner", 17, 10]]
# задняя комната: койка, сундук, бочки — за ними мальчик
sl.put(COT, 22, 4)
sl.put(BARREL, 27, 9)
sl.put(BARREL, 27, 11)
sl.box(CRATE, 22, 18, "ящик Труди", {"консервы": 2, "самогон": 1}, owner="trudy")
sl.npcs += [["ezekiel", 25, 13]]


# ================================================================ дом дока
dc = CityMap(city, "goodsprings_doc", "Дом дока Митчелла", 22, 16, start=(10, 14), seed=183, interior=True, music="desert")
dc.floor_code("F", *PLANK)
dc.wall_code("W", "pk:bazaar/bazaar_w2_12")
dc.room(1, 1, 21, 15, "W", "F")
dc.opening(10, 15, 11, 15, "F")
gs.portal([(30, 33), (31, 33)], "goodsprings_doc", (10, 13), "Дом дока Митчелла")
dc.portal([(10, 15), (11, 15)], "goodsprings", (30, 32), "На улицу")
dc.put(HOSP_BED, 3, 4)
dc.box(MED_SHELF, 8, 4, "шкаф с лекарствами", {"бинт": 2, "стимулятор": 1, "антирадин": 1}, owner="doc_mitchell")
dc.put(BOOKS, 11, 4)
dc.put(TABLE, 15, 8)
dc.put(CHAIR, 17, 8)
dc.terminal(19, 4, "mitchell_notes")
dc.put(BED, 3, 11)
dc.npcs += [["doc_mitchell", 14, 10]]


# ================================================================ пещера источника
cv = CityMap(city, "goodsprings_cave", "Пещера источника", 40, 34, start=(8, 30), seed=184, interior=True, music="caves")
cv.floor_code("d", *CAVE_DIRT)
cv.floor_code("~", *SPRING)
cv.water_codes = ("~",)
cv.paint("x", 0, 0, 39, 33)
cv.paint("d", 4, 26, 14, 31)
cv.paint("d", 8, 14, 12, 26)
cv.paint("d", 4, 4, 26, 15)
cv.paint("d", 24, 8, 36, 20)                           # дальний грот — тайник старателей
cv.paint("~", 10, 6, 18, 10)                           # родник
cv.portal([(8, 31), (9, 31)], "goodsprings", (34, 5), "Наружу")
cv.reserve(6, 28, 11, 31)
for x, y in ((5, 12), (20, 5), (30, 18), (12, 24)):
    cv.put(MUSH[(x + y) % 2], x, y)
for x, y in ((6, 6), (22, 13), (34, 10)):
    cv.put(BOULDERS[(x + y) % 2], x, y)
cv.box(CRATE, 33, 16, "тайник старателей", {"крышки": 40, "динамит": 1})
cv.put(COT, 26, 10)
cv.enemies += [["river_lizard", 20, 12], ["river_lizard", 30, 14], ["river_lizard", 6, 9]]

city.save(gap_exempt=("ezekiel",))
L = json.load(open("data/locations.json", encoding="utf-8"))
L["goodsprings"].update({"world_name": "Гудспрингс", "discover": True})
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
