"""
Боунъярд — руины Лос-Анджелеса (Fallout 1, за сорок лет до Выходца из Убежища).
Второй акт. Сценарий — docs/story.md, раздел 14.

  boneyard           «Боунъярд» (84×60): развалины даунтауна, разбитое шоссе через весь город;
                     на северо-западе — Адитум за стеной из мешков и заборов, на северо-востоке —
                     логово банды «Лезвия», на юго-востоке — стройка «Детей Единства» (здесь вырастет
                     Собор), на юго-западе — руины регионального офиса Vault-Tec.
  boneyard_adytum    Адитум внутри: торговый центр, ставший поселением, — рынок, жильё, совет, цистерны.
  boneyard_cathedral фундамент Собора: молельный зал брата Морфея и склад — с куртками «Лезвий».
  boneyard_vt        офис Vault-Tec: холл, кабинеты, серверная, кабинет директора; дикие гули, робот-охранник —
                     и гуль в шляпе, Купер Говард.

Наборы: zombie-city (zcity), construction-site DLC (csite), abandoned-office (aoffice),
post-apocalyptic-shopping-mall (pmall), underground-survivor-camp (ucamp), cult-temple (cult),
nuclear-bunker (nbunk), wasteland-junkyard-town (jtown).
Запуск из папки game_project:  .venv/bin/python tools/build_boneyard.py
"""
import json

from citykit import City, CityMap

city = City("boneyard", "Боунъярд")


def P(name, img, **kw):
    city.prop(name, img, **kw)
    return name


def cells(page, pts):
    return [f"pk:{page}/{x},{y},1,1" for x, y in pts]


# ------------------------------------------------------------ улицы
TOWERS = [P(f"by_tower{i}", f"pk:zcity/zcity_5_{n:03d}", foot=[2, 2], sight=True) for i, n in enumerate((0, 1, 2, 3, 5))]
TOWER_BROKEN = P("by_tower_broken", "pk:zcity/zcity_5_004", foot=[2, 2], sight=True)
SHOP_ROW = P("by_shop_row", "pk:zcity/zcity_5_022", foot=[6, 1], sight=True)
SHOPS = [P(f"by_shop{i}", f"pk:zcity/zcity_5_{n:03d}", foot=[2, 1], sight=True) for i, n in enumerate((18, 21, 23))]
RUIN_WALL = P("by_ruin_wall", "pk:zcity/zcity_5_009", foot=[9, 1], sight=True)
RUIN_GRAFFITI = P("by_ruin_graffiti", "pk:zcity/zcity_5_016", foot=[4, 1], sight=True)
RUIN_WALL_S = P("by_ruin_wall_s", "pk:zcity/zcity_5_010", foot=[3, 1], sight=True)
RUBBLE = [P(f"by_rubble{i}", f"pk:zcity/zcity_4_{n:03d}", foot=[2, 1]) for i, n in enumerate((7, 8, 9, 21, 22, 23, 41))]
WRECKS = [P(f"by_wreck{i}", f"pk:zcity/zcity_2_{n:03d}", foot=[2, 1], sight=True)
          for i, n in enumerate((1, 5, 13, 21, 23, 34, 35, 36, 45, 46, 78, 97, 98))]
CAR_PILE = P("by_car_pile", "pk:zcity/zcity_5_026", foot=[2, 1], sight=True)
BUS = P("by_bus", "pk:zcity/zcity_5_019", foot=[2, 1], sight=True)
LAMPS = [P("by_lamp", "pk:zcity/zcity_3_011"), P("by_lamp_b", "pk:zcity/zcity_3_012")]
BILLBOARDS = [P(f"by_billboard{i}", f"pk:zcity/zcity_4_{n:03d}", foot=[2, 1], sight=True) for i, n in enumerate((142, 143, 145))]
SIGNS = [P("by_sign", "pk:zcity/zcity_3_036"), P("by_sign_b", "pk:zcity/zcity_3_039")]
TREES = [P("by_tree", "pk:zcity/zcity_4_126"), P("by_tree_b", "pk:zcity/zcity_4_127")]
VENDING = P("by_vending", "pk:zcity/zcity_1_135", sight=True, search="junk", title="автомат с газировкой")
FIRE_BARREL = "x_fire_barrel"
SANDBAGS = "x_sandbags"
# стройка
CABIN = [P("by_cabin", "pk:csite/csite_2_000", sight=True), P("by_cabin_b", "pk:csite/csite_2_005", sight=True),
         P("by_cabin_c", "pk:csite/csite_2_015", sight=True)]
GENERATOR = P("by_generator", "pk:csite/csite_2_016", sight=True)
GENERATOR_B = P("by_generator_b", "pk:csite/csite_2_017", sight=True)
SITE_GATE = P("by_site_gate", "pk:csite/csite_2_039")
SITE_FENCE = [P("by_site_fence", "pk:csite/csite_2_040"), P("by_site_fence_b", "pk:csite/csite_2_041")]
SCAFFOLD = [P("by_scaffold", "pk:csite/csite_2_076", sight=True), P("by_scaffold_b", "pk:csite/csite_2_075", sight=True)]
EXCAVATOR = P("by_excavator", "pk:csite/csite_2_087", sight=True)
DUMPER = P("by_dumper", "pk:csite/csite_2_089", sight=True)
FLOODLIGHT = P("by_floodlight", "pk:csite/csite_2_007",
               light={"r": 160, "color": [255, 240, 200], "at": [0.5, 0.1]})
WARN = [P("by_warn", "pk:csite/csite_2_018"), P("by_warn_b", "pk:csite/csite_2_019")]
BRICKS = P("by_bricks", "pk:csite/csite_2_066")
PLANKS = P("by_planks", "pk:csite/csite_1_062")
GRAVEL_PILE = P("by_gravel_pile", "pk:csite/csite_1_065")
PALLET = P("by_pallet", "pk:csite/csite_1_030", search="crate", title="поддон с мешками")
# лагерь «Лезвий»
TENTS = [P(f"by_tent{i}", f"pk:ucamp/ucamp_2_{n:03d}", foot=[2, 1], sight=True) for i, n in enumerate((0, 3, 19, 21))]
SHACKS = [P("by_shack", "pk:ucamp/ucamp_2_023", foot=[2, 1], sight=True),
          P("by_shack_b", "pk:ucamp/ucamp_2_025", foot=[2, 1], sight=True)]
CAMPFIRE = P("by_campfire", "pk:ucamp/ucamp_2_040", foot=[2, 1],
             light={"r": 120, "color": [255, 150, 70], "at": [0.5, 0.5], "flicker": 0.35})
GUN_TABLE = P("by_gun_table", "pk:ucamp/ucamp_2_004", foot=[2, 1], search="military", title="оружейный стол")
TIRES = P("by_tires", "pk:ucamp/ucamp_2_043", foot=[2, 1])
# Адитум
SHELVES = [P(f"by_mall_shelf{i}", f"pk:pmall/pmall_2_{n:03d}", sight=True, search="shelf", title="стеллаж")
           for i, n in enumerate((8, 9, 13, 66, 68))]
MALL_VENDING = [P("by_mall_vending", "pk:pmall/pmall_2_015", sight=True), P("by_mall_vending_b", "pk:pmall/pmall_2_016", sight=True)]
COUNTER = P("by_counter", "pk:pmall/pmall_2_017", foot=[4, 1])
COUNTER_B = P("by_counter_b", "pk:pmall/pmall_2_024", foot=[4, 1])
DISPLAY = P("by_display", "pk:pmall/pmall_2_028")
CART = P("by_cart", "pk:pmall/pmall_2_049")
RACKS = [P("by_rack", "pk:pmall/pmall_1_024"), P("by_rack_b", "pk:pmall/pmall_1_033")]
CLOTH_PILE = P("by_cloth_pile", "pk:pmall/pmall_1_006", block=False)
CANS = P("by_cans", "pk:pmall/pmall_2_057", block=False)
DEBRIS = P("by_debris", "pk:pmall/pmall_2_042")
BUNK = P("by_bunk", "pk:nbunk/nbunk_2_000", sight=True)
COT = P("by_cot", "pk:ucamp/ucamp_3_027", foot=[4, 1])
TANKS = P("by_tanks", "pk:nbunk/nbunk_2_021", foot=[3, 1], sight=True)
WORKBENCH = P("by_workbench", "pk:jtown/jtown_5_064", foot=[2, 1])
# офис Vault-Tec
DESKS = [P(f"by_desk{i}", f"pk:aoffice/aoffice_1_{n:03d}") for i, n in enumerate((0, 4, 9))]
DESK_ROW = P("by_desk_row", "pk:aoffice/aoffice_2_035", foot=[6, 1])
COOLER = P("by_cooler", "pk:aoffice/aoffice_1_006")
OFFICE_FRIDGE = P("by_office_fridge", "pk:aoffice/aoffice_1_017", search="shelf", title="холодильник")
MEETING = P("by_meeting", "pk:aoffice/aoffice_1_024", foot=[4, 2])
BOOKCASES = [P("by_bookcase", "pk:aoffice/aoffice_2_004", search="drawer", title="шкаф с папками"),
             P("by_bookcase_b", "pk:aoffice/aoffice_2_005", search="drawer", title="шкаф с папками")]
COPIER = P("by_copier", "pk:aoffice/aoffice_3_021")
WHITEBOARD = P("by_whiteboard", "pk:aoffice/aoffice_2_010")
CHART = P("by_chart", "pk:aoffice/aoffice_2_036")
PLANT = P("by_plant", "pk:aoffice/aoffice_3_025")
PLANT_B = P("by_plant_b", "pk:aoffice/aoffice_1_002")
CONF_TABLE = P("by_conf_table", "pk:aoffice/aoffice_4_020", foot=[3, 1])
CABINETS = P("by_cabinets", "pk:aoffice/aoffice_3_013", sight=True, search="drawer", title="картотека")
SERVER = P("by_server", "pk:nbunk/nbunk_2_028", foot=[2, 2], sight=True)
SAFE = P("by_safe", "pk:west/west_2_105", search="military", title="сейф")
# собор
ALTAR = P("by_altar", "pk:cult/cult_3_042", foot=[2, 1], sight=True)
BANNERS = [P("by_banner", "pk:cult/cult_2_141", block=False), P("by_banner_b", "pk:cult/cult_2_142", block=False)]
PILLAR = P("by_pillar", "pk:cult/cult_2_143", sight=True)
CANDELABRA = P("by_candelabra", "pk:cult/cult_2_068", block=False,
               light={"r": 90, "color": [255, 170, 80], "at": [0.5, 0.3], "flicker": 0.5})
PEWS = P("by_pew", "pk:cult/cult_3_044", foot=[2, 1])                 # каменные скамьи
CHEST = P("by_chest", "pk:cult/cult_2_134", search="military", title="сундук")
CRATE = P("by_crate", "pk:ucamp/ucamp_2_087", search="crate", title="ящик")

ROAD = ["pk:zcity/zcity_f3_09"]
WALK = ["pk:zcity/zcity_f1_22"]
RUBBLE_FL = ["pk:zcity/zcity_f2_26"]
DIRT = ["pk:zcity/zcity_f2_00"]
SAND = cells("destown/p2", [(0, 0), (1, 0), (0, 1), (1, 1)])
TILES = ["pk:zcity/zcity_f3_00"]
CARPET = ["pk:aoffice/p3/3,1,1,1"]
WOOD = ["pk:zcity/zcity_f1_00"]
STONE = ["pk:zcity/zcity_f1_23"]
CONCRETE = ["pk:zcity/zcity_f3_08"]
MALL_TILE = ["pk:store/p1/12,0,1,1"]


# ================================================================ Боунъярд
W, H = 84, 60
by = CityMap(city, "boneyard", "Боунъярд", W, H, start=(1, 29), seed=141, music="reno", world_pos=(760, 1290))
by.floor_code("r", *RUBBLE_FL)
by.floor_code("a", *ROAD)
by.floor_code("p", *WALK)
by.floor_code("d", *DIRT)
by.floor_code("c", *CONCRETE)
by.paint("r", 0, 0, W - 1, H - 1)
by.paint("p", 0, 26, W - 1, 33)                        # шоссе через весь город
by.paint("a", 0, 27, W - 1, 32)
by.paint("p", 40, 0, 45, H - 1)                        # улица с севера на юг
by.paint("a", 41, 0, 44, H - 1)
by.paint("d", 4, 3, 34, 23)                            # двор Адитума
by.paint("c", 50, 37, 80, 57)                          # площадка стройки
by.exits = [(0, y) for y in range(27, 33)]
by.reserve(0, 27, W - 1, 32)
by.reserve(41, 0, 44, H - 1)

# северо-запад: Адитум — торговый центр за стеной из мешков и сетки; ворота на шоссе
by.hwall([SANDBAGS], 4, 34, 3)
by.hwall([SANDBAGS, "chain_a", "chain_b"], 4, 34, 23, gaps=(18, 19, 20))
for x in (4, 34):
    for y in range(4, 23):
        by.maybe(SANDBAGS if y % 3 else "chain_c", x, y, check=False)
by.reserve(17, 20, 21, 25)
by.building(8, 5, 22, 12, "concrete", south=(10,))
by.reserve(18, 17, 19, 20)
by.put(TANKS, 6, 19)                                    # цистерны и огородик во дворе
by.put(FIRE_BARREL, 16, 22)
by.put(FIRE_BARREL, 22, 22)
by.put(GENERATOR, 30, 8)
by.box(CRATE, 31, 18, "ящик Адитума", {"консервы": 2, "чистая вода": 1}, owner="adytum_guard")
by.npcs += [["adytum_guard", 17, 21], ["adytum_guard_b", 21, 21], ["adytum_farmer", 27, 19]]

# северо-восток: «Лезвия» — палатки в руинах, костёр, граффити
by.put(RUIN_GRAFFITI, 50, 3)
by.put(RUIN_WALL_S, 56, 3)
by.put(TOWER_BROKEN, 62, 2)
by.put(TOWERS[2], 72, 2)
by.put(TENTS[0], 50, 9)
by.put(TENTS[1], 55, 9)
by.put(SHACKS[0], 62, 12)
by.put(CAMPFIRE, 56, 15)
by.put(TIRES, 49, 17)
by.box(GUN_TABLE, 67, 9, "оружейный стол «Лезвий»", {"патроны": 20, "охотничий нож": 1}, owner="blade_nika")
by.put(FIRE_BARREL, 48, 20)
by.put(FIRE_BARREL, 66, 20)
by.npcs += [["blade_nika", 58, 13], ["blade_a", 52, 18], ["blade_b", 63, 18]]

# руины вдоль шоссе: высотки, лавки, рекламные щиты, остовы машин
for i, x in enumerate((47, 51, 70, 76)):
    by.put(TOWERS[i % len(TOWERS)], x, 23)
by.put(SHOP_ROW, 58, 24)
by.put(BILLBOARDS[0], 37, 20)
by.put(BILLBOARDS[1], 36, 36)
for i, (x, y) in enumerate(((6, 33), (14, 26), (24, 33), (31, 26), (52, 33), (63, 26), (70, 33), (78, 26))):
    by.put(WRECKS[i % len(WRECKS)], x, y)
by.put(BUS, 34, 26)
for x in (10, 30, 56, 66):
    by.maybe(LAMPS[x % 2], x, 26)
    by.maybe(LAMPS[(x + 1) % 2], x + 3, 33)
by.put(SIGNS[0], 39, 25)
by.put(SIGNS[1], 46, 34)

# юго-запад: руины офиса Vault-Tec — фасад, щит с рекламой убежищ, дикие гули у входа
by.building(8, 38, 18, 12, "concrete", north=(8,))
by.reserve(16, 35, 17, 38)
by.put(BILLBOARDS[2], 28, 37)
by.put(RUIN_WALL, 5, 54)
by.put(CAR_PILE, 28, 46)
by.enemies += [["feral", 24, 41], ["feral", 30, 52], ["feral", 6, 36]]

# юго-восток: стройка «Детей Единства» — забор, бытовки, леса, экскаватор, прожекторы; вход в фундамент
by.hwall(SITE_FENCE, 50, 80, 36, gaps=(56, 57, 58))
by.reserve(55, 34, 59, 39)
by.building(62, 42, 16, 11, "concrete", north=(6,), roof=False)   # фундамент — без крыши, только стены
by.reserve(68, 39, 69, 42)
by.put(SCAFFOLD[0], 62, 40)
by.put(SCAFFOLD[1], 74, 40)
by.put(CABIN[0], 51, 38)
by.put(CABIN[1], 51, 42)
by.put(CABIN[2], 51, 48)
by.put(EXCAVATOR, 56, 52)
by.put(DUMPER, 70, 55)
by.put(GENERATOR_B, 79, 38)
by.put(FLOODLIGHT, 60, 38)
by.put(FLOODLIGHT, 78, 54)
by.put(WARN[0], 54, 37)
by.put(WARN[1], 61, 37)
for x, y in ((57, 45), (59, 47)):
    by.put(BRICKS, x, y)
by.put(PLANKS, 55, 49)
by.put(GRAVEL_PILE, 60, 55)
by.box(PALLET, 65, 56, "поддон с мешками", {"мешок цемента": 1})
by.npcs += [["cult_foreman", 58, 41], ["cult_worker", 64, 54], ["cult_worker_b", 75, 50], ["adytum_worker", 54, 46]]

for _, x, y in by.npcs:
    by.reserve(x, y, x, y)
by.scatter(RUBBLE + [VENDING, "r_trash"], 36, 1, 39, 24, 4)
by.scatter(RUBBLE + WRECKS[5:] + ["r_trash", "r_bones"], 46, 1, W - 2, 22, 10)
by.scatter(RUBBLE + ["r_trash", "r_bones"], 1, 35, 38, H - 2, 12)
by.scatter(RUBBLE + WRECKS, 46, 34, 49, H - 2, 4)
by.scatter(TREES, 1, 1, 3, 24, 4)


# ================================================================ Адитум (внутри)
ad = CityMap(city, "boneyard_adytum", "Адитум", 40, 28, start=(19, 26), seed=142, interior=True, music="hub")
ad.floor_code("F", *MALL_TILE)
ad.floor_code("C", *CONCRETE)
ad.wall_code("W", "pk:pmall/pmall_w3_17")
ad.room(1, 1, 14, 14, "W", "C")                       # склад и цистерны
ad.room(14, 1, 26, 14, "W", "F")                      # лавка
ad.room(26, 1, 39, 14, "W", "F")                      # зал совета
ad.room(1, 14, 39, 27, "W", "F")                      # галерея — здесь живут
ad.opening(19, 27, 20, 27, "F")
by.portal([(18, 16), (19, 16)], "boneyard_adytum", (19, 25), "Адитум")
ad.portal([(19, 27), (20, 27)], "boneyard", (18, 18), "Во двор")
ad.opening(7, 14, 8, 16, "C")
ad.opening(19, 14, 20, 16, "F")
ad.opening(32, 14, 33, 16, "F")
# склад: цистерны с водой из Хаба, верстак, ящик
ad.put(TANKS, 3, 4)
ad.put(TANKS, 8, 4)
ad.put(WORKBENCH, 11, 9)
ad.box(CRATE, 3, 11, "ящик со склада", {"консервы": 2, "бинт": 1}, owner="adytum_mayor")
# лавка: прилавок лицом к двери, стеллажи вдоль стен, автоматы
ad.put(COUNTER, 17, 7)
ad.put(SHELVES[0], 15, 4)
ad.put(SHELVES[1], 17, 4)
ad.put(SHELVES[2], 21, 4)
ad.put(MALL_VENDING[0], 24, 4)
ad.put(MALL_VENDING[1], 24, 9)
ad.npcs += [["adytum_trader", 18, 5]]
# совет: стол, шкафы, сейф мэра
ad.put(CONF_TABLE, 31, 7)
ad.put(BOOKCASES[0], 28, 4)
ad.put(BOOKCASES[1], 30, 4)
ad.box(SAFE, 37, 4, "сейф совета", {"крышки": 120},
       requires={"item": "отмычка", "msg": "Сейф совета Адитума. Без отмычки не открыть."}, owner="adytum_mayor")
ad.npcs += [["adytum_mayor", 33, 10]]
# галерея: бывшие магазины одежды — теперь углы семей: стойки с тряпьём, двухъярусные койки, раскладушки
ad.put(RACKS[0], 3, 19)
ad.put(RACKS[1], 11, 19)
ad.put(DISPLAY, 14, 19)
ad.put(CART, 24, 19)
for x in (27, 35):
    ad.put(BUNK, x, 19)
ad.put(COT, 3, 24)
ad.put(COT, 33, 24)
ad.put(CLOTH_PILE, 9, 24)
ad.put(CANS, 26, 24)
ad.npcs += [["adytum_mom", 29, 22], ["adytum_kid", 14, 23], ["adytum_doc", 6, 22]]


# ================================================================ фундамент Собора
ct = CityMap(city, "boneyard_cathedral", "Фундамент Собора", 36, 26, start=(17, 5), seed=143, interior=True, music="vats")
ct.floor_code("F", *STONE)
ct.floor_code("C", *CONCRETE)
ct.wall_code("W", "pk:cult/cult_w1_22")
ct.room(1, 1, 26, 25, "W", "F")                       # молельный зал
ct.room(26, 1, 35, 25, "W", "C")                      # склад
ct.opening(26, 18, 26, 19, "C")
ct.props.append(["x_ladder", 17, 4])
by.props.append(["x_ladder", 69, 47])                    # внутри фундамента — лестница вниз, в будущий собор
by.portal([(69, 47)], "boneyard_cathedral", (17, 5), "Вниз, в Собор")
by.reserve(67, 45, 71, 49)
for x, y in ((64, 45), (64, 50), (74, 45)):                # внутри — то, из чего строят: поддоны, доски, кирпич
    by.put(BRICKS if x == 64 else PLANKS, x, y)
by.put(GRAVEL_PILE, 74, 50)
by.put(FLOODLIGHT, 76, 47)
ct.portal([(17, 4)], "boneyard", (69, 48), "Наверх, на стройку")
ct.reserve(15, 4, 20, 7)
# зал: алтарь у южной стены (кафедра лицом к входу), скамьи рядами, колонны со свечами
ct.put(ALTAR, 13, 22)
ct.put(BANNERS[0], 10, 21)
ct.put(BANNERS[1], 17, 21)
for y in (10, 13, 16):
    ct.put(PEWS, 6, y)
    ct.put(PEWS, 9, y)
    ct.put(PEWS, 17, y)
    ct.put(PEWS, 20, y)
for y in (9, 15, 21):
    ct.put(PILLAR, 3, y)
    ct.put(PILLAR, 24, y)
    ct.put(CANDELABRA, 4, y)
    ct.put(CANDELABRA, 23, y)
ct.npcs += [["morpheus", 14, 20], ["cult_listener", 7, 11], ["cult_listener_b", 18, 14]]
# склад: ящики с цементом и водой, сундук — в нём куртки «Лезвий» и ножи с их меткой
for x, y in ((28, 4), (31, 4), (34, 4), (28, 9), (31, 9)):
    ct.put(CRATE, x, y)
ct.box(CHEST, 33, 14, "сундук на складе", {"куртка «Лезвий»": 1, "приказ брата Т.": 1},
       requires={"item": "отмычка", "msg": "Сундук на замке. Брат-кладовщик носит ключ на поясе."}, owner="morpheus")
ct.put(TANKS, 29, 22)


# ================================================================ офис Vault-Tec
vt = CityMap(city, "boneyard_vt", "Офис Vault-Tec", 44, 32, start=(16, 30), seed=144, interior=True, music="lab")
vt.floor_code("F", *CARPET)
vt.floor_code("T", *TILES)
vt.floor_code("M", *CONCRETE)
vt.wall_code("W", "pk:pmall/pmall_w3_10")
vt.room(1, 18, 43, 31, "W", "T")                      # холл
vt.room(1, 1, 22, 18, "W", "F")                       # кабинеты отдела продаж
vt.room(22, 1, 33, 18, "W", "M")                      # серверная
vt.room(33, 1, 43, 18, "W", "F")                      # кабинет директора
vt.opening(16, 31, 17, 31, "T")
by.portal([(16, 38), (17, 38)], "boneyard_vt", (16, 29), "Офис Vault-Tec")
vt.portal([(16, 31), (17, 31)], "boneyard", (16, 36), "На улицу")
vt.opening(10, 18, 11, 20, "F")
vt.opening(27, 18, 28, 20, "M")
vt.opening(38, 18, 39, 20, "F")
# холл: стойка ресепшена лицом ко входу, кулер, растения, стенд «Будущее — под землёй»
vt.put(COUNTER_B, 14, 23)
vt.put(COOLER, 3, 21)
vt.put(PLANT, 6, 21)
vt.put(PLANT_B, 30, 21)
vt.put(CHART, 34, 21)
vt.put(MEETING, 34, 25)
vt.put(DEBRIS, 24, 27)
vt.terminal(20, 22, "vt_lobby")
# кабинеты: ряды столов, шкафы с папками вдоль стены, копир
vt.put(BOOKCASES[0], 3, 4)
vt.put(BOOKCASES[1], 5, 4)
vt.put(CABINETS, 8, 4)
vt.put(COPIER, 19, 4)
vt.put(DESK_ROW, 3, 9)
vt.put(DESK_ROW, 3, 14)
vt.put(DESKS[0], 15, 9)
vt.put(DESKS[1], 15, 14)
vt.put(OFFICE_FRIDGE, 19, 12)
# серверная: стойки вдоль стен, генератор
for x in (24, 27, 30):
    vt.put(SERVER, x, 4)
vt.put(SERVER, 24, 10)
vt.terminal(30, 12, "vt_server")
# кабинет директора: стол, сейф, доска с планом убежищ — здесь сидит Купер
vt.put(DESKS[2], 37, 7)
vt.put(WHITEBOARD, 35, 4)
vt.box(SAFE, 41, 4, "сейф директора", {"ключ-карта Vault-Tec": 1, "крышки": 90},
       requires={"flag": "cooper_card", "msg": "Сейф директора. Купер сидит на нём верхом и не собирается слезать."})
vt.put(PLANT, 34, 15)
vt.npcs += [["cooper", 39, 11]]
vt.enemies += [["feral", 6, 12], ["feral", 18, 7], ["robot_guard", 28, 14], ["feral", 30, 26], ["feral", 8, 26]]

city.save(gap_exempt=("cooper", "adytum_guard", "adytum_guard_b", "adytum_farmer"))
L = json.load(open("data/locations.json", encoding="utf-8"))
L["boneyard"].update({"world_name": "Боунъярд", "discover": True})
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
