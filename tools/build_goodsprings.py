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
HOUSES = [P(f"gs_house{i}", f"pk:rvill/rvill_1_{n:03d}", scale=2, foot=[2, 1], sight=True)
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
FRONT_SALOON = P("gs_front_saloon", "pk:west/p1/10,12,2,2", foot=[2, 1], sight=True)
FRONT_STORE = P("gs_front_store", "pk:west/p1/12,12,2,2", foot=[2, 1], sight=True)
FRONT_SHERIFF = P("gs_front_sheriff", "pk:west/p1/14,12,2,2", foot=[2, 1], sight=True)
WFENCE = P("gs_wfence", "pk:wfarm/p3/0,12,4,1", foot=[4, 1], keybg=True)
LAUNDRY = P("gs_laundry", "pk:wfarm/p3/0,0,4,3", foot=[4, 1], keybg=True)
STALL_G = P("gs_stall", "pk:destown/p3/4,8,2,2", foot=[2, 1], keybg=True)
STALL_G2 = P("gs_stall_b", "pk:destown/p3/0,8,2,2", foot=[2, 1], keybg=True)
HITCH = P("gs_hitch", "pk:west/p1/1,13,3,1", foot=[3, 1], keybg=True)
TANK_G = P("gs_tank", "pk:wfarm/p3/12,4,2,3", foot=[2, 1], sight=True, keybg=True)
BED_G = [P("gs_bed_a", "pk:wfarm/p1/0,8,2,2", foot=[2, 1], keybg=True), P("gs_bed_b", "pk:wfarm/p1/2,8,2,2", foot=[2, 1], keybg=True)]
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
STALAG_G = [P("gs_stalag_a", "pk:dcave/p1/8,6,2,2", foot=[1, 1], keybg=True), P("gs_stalag_b", "pk:dcave/p1/12,2,2,2", foot=[1, 1], keybg=True),
            P("gs_stalag_c", "pk:dcave/p1/0,12,2,2", foot=[1, 1], keybg=True)]
CRYSTALS_G = [P("gs_crystal_a", "pk:dcave/p1/9,8,1,1", block=False, keybg=True, light={"r": 60, "color": [210, 130, 255], "at": [0.5, 0.5]}),
              P("gs_crystal_b", "pk:dcave/p1/10,8,1,1", block=False, keybg=True, light={"r": 60, "color": [120, 255, 160], "at": [0.5, 0.5]}),
              P("gs_crystal_c", "pk:dcave/p1/8,8,1,1", block=False, keybg=True, light={"r": 60, "color": [120, 170, 255], "at": [0.5, 0.5]})]
BONES_G = P("gs_dragon_bones", "pk:dcave/p1/1,10,3,2", block=False, keybg=True)
COBBLE_G = cells("dcave/p2", [(4, 1), (5, 1), (4, 2), (5, 2)])
LANTERN_G = P("gs_cave_lantern", "pk:cmine/cmine_1_032", light={"r": 100, "color": [255, 190, 110], "at": [0.5, 0.5], "flicker": 0.3})
BOULDERS = [P("gs_boulder", "pk:gcave/p1/4,4,1,1"), P("gs_boulder_b", "pk:gcave/p1/5,4,1,1")]

PIT_G = [P("gs_pit_a", "pk:dcave/p1/2,8,2,2", block=False, layer="floor", keybg=True), P("gs_pit_b", "pk:dcave/p1/4,8,2,2", foot=[1, 1], layer="floor", keybg=True)]
MOSS_G = [P("gs_moss", "pk:dcave/p1/10,14,2,2", block=False, layer="floor", keybg=True)]
PEBBLE_G = [P(f"gs_pebbles{i}", f"pk:dcave/p1/{x},{y},1,1", block=False, keybg=True) for i, (x, y) in enumerate(((2, 4), (3, 4), (4, 4), (2, 5), (5, 5)))]
SAND = ["pk:desnat/p1/0,0,1,1", "pk:desnat/p1/1,0,1,1", "pk:desnat/p1/0,1,1,1"]   # песок под цвет окружающей пустыни, без скачка
DIRT = ["noise:pk:rvill/p2/0,11,1,1"]
ROAD = ["noise:pk:destown/p2/4,0,1,1"]          # утоптанный гравий улицы — как в Зайзиксе
STONE = cells("west/p1", [(4, 0), (5, 0), (4, 1), (5, 1)])         # булыжник площади
PLANK = ["pk:bazaar/bazaar_f1_21"]
BOARDS = ["pk:fishv/p4/6,10,1,1", "pk:fishv/p4/6,11,1,1", "pk:fishv/p4/5,10,1,1"]      # светлые доски тротуаров
CAVE_DIRT = cells("dcave/p1", [(0, 2), (1, 2), (0, 3), (1, 3)])          # серо-бурая земля Dragon Cave
CAVE_DARK = cells("dcave/p1", [(0, 0), (1, 0), (0, 1), (1, 1), (2, 0), (3, 0)])   # земля с крупными трещинами
CAVE_GRAVEL = cells("dcave/p2", [(4, 7), (5, 7), (6, 7), (7, 7)])
SPRING = cells("sewer/p1", [(10, 1), (11, 1)])


# ================================================================ посёлок
W, H = 70, 50
gs = CityMap(city, "goodsprings", "Гудспрингс", W, H, start=(1, 30), seed=181, music="desert", world_pos=(2330, 560))
gs.floor_code("s", *SAND)
gs.floor_code("d", *DIRT)
gs.floor_code("r", *ROAD)
gs.floor_code("t", *STONE)
gs.floor_code("w", *BOARDS)
gs.piers = ("w",)                                       # тротуар — доски с чёткой кромкой, без размытия в землю
gs.paint("s", 0, 0, W - 1, H - 1)
gs.paint_ragged("d", 4, 12, 64, 44, depth=4)                          # утоптанная земля посёлка
gs.paint("r", 0, 29, W - 1, 32)                         # улица
gs.paint("r", 33, 10, 36, 29)                           # проезд к пещере
gs.paint_ragged("t", 26, 20, 43, 28, depth=3)             # площадь у колодца — неровный булыжник, как стёртая мостовая
gs.exits = [(0, y) for y in range(29, 33)] + [(W - 1, y) for y in range(29, 33)]
gs.reserve(0, 29, W - 1, 32)
gs.reserve(33, 10, 36, 28)
gs.paint("w", 6, 27, 27, 28)                            # дощатые тротуары вдоль фасадов
gs.paint("w", 42, 27, 64, 28)
gs.paint("w", 6, 33, 24, 34)
gs.paint("w", 38, 33, 58, 34)
for _x0, _y0, _x1, _y1 in ((6, 27, 27, 28), (42, 27, 64, 28), (6, 33, 24, 34), (38, 33, 58, 34)):
    gs.reserve(_x0, _y0, _x1, _y1)

# площадь: колодец и колокол — бить тревогу, если придёт культ
gs.put(WELL, 30, 24)
gs.put(BELL, 39, 24)
gs.put(LAMP, 28, 22)
gs.put(LAMP, 41, 22)
gs.put(TROUGH, 31, 27)
# площадь живёт: скамьи вокруг колодца, прилавок с овощами, ящики, привязь, бельё у колодца
for x, y in ((29, 26), (38, 26), (29, 23), (40, 27)):
    gs.maybe("bench_7", x, y)
gs.maybe(STALL_G, 33, 26)
gs.maybe(STALL_G2, 36, 24)
for x, y in ((27, 21), (42, 21), (27, 27), (42, 24)):
    gs.maybe(CRATE if (x + y) % 2 else BARREL, x, y)

# север улицы: салун «Старатель» (большой, с крышей), лавка, дом старосты
gs.building(10, 16, 14, 11, "planks", south=(6,))       # салун
gs.reserve(16, 27, 17, 28)
gs.put(SIGN, 12, 27, allow_reserved=True)
gs.put(BARREL, 22, 27, allow_reserved=True)
gs.put(FRONT_STORE, 44, 20)                             # лавка Чета
gs.put(CRATE, 49, 22)
gs.put(FRONT_SHERIFF, 52, 20)                           # дом старосты Петтита — он же шериф, пока шерифа нет
gs.put(HITCH, 44, 25, check=False)
gs.put(HITCH, 52, 25, check=False)
gs.put(TROUGH, 49, 26)
# юг улицы: дом дока Митчелла (с крышей — заходят внутрь), жилые дома, ферма с загоном
gs.building(26, 34, 10, 8, "planks", north=(4,))       # дом дока
gs.reserve(30, 32, 31, 34)
gs.put(HOUSES[2], 8, 38)
gs.put(HOUSES[3], 15, 38)
gs.put(HOUSES[4], 42, 38)
gs.put(HITCH, 8, 34, check=False, allow_reserved=True)        # коновязь перед домом, а не за его картинкой
gs.put(HITCH, 15, 34, check=False, allow_reserved=True)
gs.put(HITCH, 42, 34, check=False, allow_reserved=True)
gs.put(BARN, 50, 35)
gs.hwall(FENCE, 49, 61, 40, gaps=(55, 56))
gs.side_fence("wood", 61, 34, 39)
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
gs.npcs += [["joe_cobb", 64, 33]]                          # охотник за головами — появляется, когда Ринго сознался
gs.npcs += [["sunny", 26, 30], ["chet", 46, 22], ["mayor_pettit", 54, 22], ["gs_farmer", 55, 38], ["gs_kid", 38, 27],
            ["gs_old", 32, 22]]
gs.box("r_trash_can", 20, 25, "мусорный бак за салуном", {"фартук в крови": 1, "ткань": 1})
for _, x, y in gs.npcs:
    gs.reserve(x, y, x, y)
# север посёлка вдоль дороги к пещере: кузница-навес, загон с повозкой, дровяник — жизнь у самого центра
gs.maybe(SHED, 42, 13)
gs.maybe(HITCH, 46, 16, check=False)
gs.maybe(STAGECOACH, 46, 14)
gs.hwall([WFENCE], 52, 62, 13)
gs.side_fence("wood", 62, 14, 17)
gs.maybe(TROUGH, 56, 15)
gs.maybe(HOUSES[5], 54, 5)
for x, y in ((40, 16), (50, 17), (60, 17), (38, 12)):
    gs.maybe(BARREL if (x + y) % 2 else CRATE, x, y)
gs.maybe(LAUNDRY, 26, 14)
gs.maybe(CAMPFIRE, 40, 31) if False else None
# окраины: поля за посёлком, брошенные фермы, стоянка караванщиков — земля вокруг не пустует
for i, (x, y) in enumerate(((3, 14), (6, 14), (3, 17), (6, 17), (3, 20), (6, 20), (65, 14), (68, 14), (65, 17), (68, 17), (65, 20), (68, 20))):
    gs.maybe(BED_G[i % 2], x, y)
gs.hwall([WFENCE], 2, 9, 13)
gs.hwall([WFENCE], 2, 9, 23)
gs.hwall([WFENCE], 64, 69, 13)
gs.hwall([WFENCE], 64, 69, 23)
gs.side_fence("wood", 9, 14, 22)
gs.maybe(RUIN, 66, 8)
gs.maybe(HOUSES[5], 58, 5)
gs.maybe(HOUSES[6], 64, 4)
gs.maybe(LAUNDRY, 60, 9)
gs.maybe(STAGECOACH, 4, 44)
gs.maybe(STAGECOACH, 62, 44)
gs.maybe(CAMPFIRE, 56, 47)                               # стоянка караванщиков у повозки
for x, y in ((53, 47), (59, 47)):
    gs.maybe("bench_7", x, y)
gs.maybe(CAMPFIRE, 8, 47)
for x, y in ((5, 47), (11, 47)):
    gs.maybe("bench_7", x, y)
gs.grow(1, 1, W - 2, 9, 4, names=CACTI + BUSHES + DEAD_TREES)
gs.grow(1, 46, W - 2, H - 2, 3, names=CACTI + BUSHES)
gs.scatter(DEAD_TREES, 28, 46, W - 2, H - 2, 3)
gs.grow(1, 10, 3, 43, 2, names=CACTI + BUSHES)
gs.grow(66, 10, W - 2, 43, 2, names=CACTI + BUSHES)
# дворы жилых домов: штакетник, бельё на верёвке, повозка у порога
for x in (6, 14, 40):
    gs.hwall([WFENCE], x, x + 7, 42, gaps=(x + 3, x + 4))
gs.maybe(LAUNDRY, 18, 37)
gs.maybe(LAUNDRY, 46, 38)
gs.maybe(STAGECOACH, 36, 38)
for x, y in ((22, 38), (4, 38), (47, 36), (39, 37)):
    gs.maybe(BARREL, x, y)
# огороды и водокачка за домами: грядки, бак на ножках, бочки с дождевой водой
gs.put(TANK_G, 20, 43)
for i, (x, y) in enumerate(((10, 44), (13, 44), (24, 44), (46, 44), (49, 44))):
    gs.maybe(BED_G[i % 2], x, y)
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
cv.floor_code("o", *COBBLE_G)
cv.floor_code("k", *CAVE_DARK)
cv.floor_code("q", *CAVE_GRAVEL)
cv.water_codes = ("~",)
cv.paint("x", 0, 0, 39, 33)
# Планировка: низкий вход -> извилистый ход на север -> большой грот с родником (светящиеся грибы по берегу) ->
# перешеек на восток -> тайник старателей в боковой нише. Каждый участок — отдельное «место», а не коробка.
cv.blob("d", 8, 29, 6, 4)                              # вход
cv.tunnel("d", [(9, 27), (10, 22), (9, 17), (11, 13)], width=3, wobble=1)
cv.blob("d", 15, 9, 11, 6)                             # грот с родником
cv.tunnel("d", [(24, 11), (28, 13), (31, 16)], width=3, wobble=1)
cv.blob("d", 31, 17, 6, 5)                             # ниша старателей
cv.blob("d", 3, 8, 3, 3)                               # тупиковый карман с костями
cv.tunnel("d", [(5, 8), (8, 9)], width=2, wobble=0)
cv.blob("o", 15, 8, 7, 4, wobble=0.25)                 # мшистый булыжник вокруг родника — как в превью набора
cv.blob("~", 15, 8, 4, 2, wobble=0.25)                 # родник
cv.portal([(8, 31), (9, 31)], "goodsprings", (34, 5), "Наружу")
cv.reserve(6, 28, 11, 31)
for x, y in ((11, 6), (19, 6), (11, 10), (20, 10), (14, 11), (17, 11)):
    cv.maybe(MUSH[(x + y) % 2], x, y)                  # грибы — у воды, их свет отражается
for x, y in ((6, 11), (23, 4), (26, 8), (29, 14), (33, 19)):
    cv.maybe(STALAG_G[(x + y) % 3], x, y)
for x, y in ((7, 24), (12, 18), (21, 7), (31, 14)):
    cv.maybe(BOULDERS[(x + y) % 2], x, y)                  # одиночные валуны, не груды
cv.maybe(BONES_G, 2, 7)
for x, y in ((12, 5), (18, 5), (20, 11), (13, 11)):
    cv.maybe(CRYSTALS_G[(x + y) % 3], x, y)
cv.maybe("pickaxe", 4, 7)
cv.maybe(LANTERN_G, 9, 25)
for x, y in ((11, 21), (8, 16), (12, 12), (26, 12)):
    cv.maybe(LANTERN_G, x, y)                          # старатели развесили фонари вдоль всего хода
for x, y in ((7, 19), (13, 15), (12, 22), (28, 14)):
    cv.maybe(MUSH[(x + y) % 2], x, y)                  # редкие грибы в проходе — слабый зелёный свет
cv.maybe(LANTERN_G, 29, 16)
cv.maybe(LANTERN_G, 34, 18)
cv.box(CRATE, 33, 16, "тайник старателей", {"крышки": 40, "динамит": 1})
cv.maybe(COT, 29, 19)
cv.maybe("barrel_wood", 35, 15)
cv.maybe("crate_b", 34, 20)
cv.maybe("table_chair", 30, 15)
cv.enemies += [["river_lizard", 20, 12], ["river_lizard", 30, 14], ["river_lizard", 6, 9]]


# пустыри обживаются сценками (экскурсия по городам показала голый песок)
print("обжито:", gs.dress_empty([
    [("r_shack", 0, 0), ("pile_junk", 5, 1), ("barrel_wood", 0, 3), ("x_fire_barrel", 3, 3)],
    [("r_tent_beige", 0, 0), ("r_tent_low", 3, 0), ("campfire", 2, 2), ("r_logs", 4, 2), ("barrel_wood", 0, 2)],
    [("r_car_wreck", 0, 0), ("pile_tires", 0, 2), ("r_trash", 3, 2)],
    [("r_camper", 0, 0), ("r_awning", 0, 2), ("crate", 3, 2), ("sack", 4, 2)],
    [("r_water_tower_b", 3, 0), ("barrel_wood", 4, 1), ("bucket", 2, 1), ("r_barrels", 5, 1)],
    [("x_cross", 0, 0), ("x_grave", 0, 1), ("x_cross", 2, 0), ("x_grave", 2, 1), ("x_cross", 4, 0), ("x_grave", 4, 1), ("r_dtree_a", 5, 2)],
    [("r_dumpster", 0, 0), ("pile_cans", 2, 0), ("r_trash", 0, 2), ("crate_broken", 3, 2)],
    [("r_pickup", 0, 0), ("r_barrels", 3, 0), ("r_barrels", 3, 1), ("pile_scrap", 0, 2)],
    [("r_billboard", 0, 0), ("r_dtree_a", 2, 1), ("r_bones", 3, 2)],
], block=7, margin=1, chance=1.0))

for x, y in ((8, 21), (12, 15), (28, 17)):
    cv.maybe(PIT_G[(x + y) % 2], x, y)                 # провалы и трещины в полу
for x, y in ((8, 5), (21, 8), (11, 12), (31, 20)):
    cv.maybe(MOSS_G[0], x, y)                # мшистые поляны у воды и в нише
cv.scatter(PEBBLE_G, 1, 1, 38, 32, 18)
cv.patchwork("d", ["k", "k", "k"], 14, 2, 4, seed=1)
cv.cave_style = True
cv.erode_cave(keep=[(3, 25, 14, 32)], chance=0.25, passes=1)
cv.scatter(["stones_12", "stones_19"], 1, 1, 38, 32, 12)
city.save(gap_exempt=("ezekiel",))
L = json.load(open("data/locations.json", encoding="utf-8"))
L["goodsprings"].update({"world_name": "Гудспрингс", "discover": True})
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
