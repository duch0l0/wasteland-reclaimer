"""
Лагерь Арадеша — переселенцы из Убежища 15 (будущий Шейди-Сэндс Fallout 1, за двадцать лет до основания).
Второй акт. Сценарий — docs/story.md, раздел 13.

  aradesh         «Лагерь Арадеша» (70×50): палатки переселенцев, дом собраний, теплица и грядки
                  из покрышек и бочек, поле, высохший колодец, мастерская; у въезда — шатёр «Детей
                  Единства» с бочками воды. Выход на восток — в каньон.
  aradesh_hall    дом собраний: стол совета, койки семьи Арадеша, терминал переселенцев.
  aradesh_canyon  каньон: сожжённый фургон культа (груз забрали — следы винтов на песке),
                  стоянка Ханов, вход в пещеру радскорпионов.
  aradesh_cave    пещера: радскорпионы, их матка — и подземный родник, из которого ушла вода колодца.

Наборы: post-apocalyptic-wasteland-survival-farm (wfarm), goblin-cave (gcave), underground-survivor-camp
(ucamp), desert-town (destown), desert-natural (desnat), wild-west (west), bazaar (bazaar), zombie-city (zcity).
Запуск из папки game_project:  .venv/bin/python tools/build_aradesh.py
"""
import json

from citykit import City, CityMap

city = City("aradesh", "Лагерь Арадеша")


def P(name, img, **kw):
    city.prop(name, img, **kw)
    return name


def cells(page, pts):
    return [f"pk:{page}/{x},{y},1,1" for x, y in pts]


# ------------------------------------------------------------ объекты
GREENHOUSE = P("ar_greenhouse", "pk:wfarm/wfarm_3_008", foot=[4, 2], sight=True)
WATER_TANK = P("ar_water_tank", "pk:wfarm/wfarm_3_009", foot=[2, 1], sight=True)
SHED = P("ar_shed", "pk:wfarm/wfarm_3_011", foot=[3, 2], sight=True)
WORKSHOP = P("ar_workshop", "pk:wfarm/wfarm_3_012", foot=[4, 2], sight=True)
SHACK_TIN = P("ar_shack_tin", "pk:wfarm/wfarm_3_004", foot=[4, 2], sight=True)
YARD = P("ar_yard", "pk:wfarm/wfarm_4_002", foot=[3, 2], sight=True)
BEDS = [P(f"ar_bed{i}", f"pk:wfarm/wfarm_{n}", foot=[2, 1]) for i, n in
        enumerate(("1_053", "1_054", "1_080", "1_081", "2_017", "2_018", "2_020", "2_021"))]
TUBS = [P("ar_tub", "pk:wfarm/wfarm_2_036", foot=[2, 1]), P("ar_tub_b", "pk:wfarm/wfarm_2_037", foot=[2, 1])]
BARREL_PLANTS = [P(f"ar_barrel_plant{i}", f"pk:wfarm/wfarm_5_{n:03d}", foot=[2, 1]) for i, n in enumerate((43, 44, 47))]
TIRE_PLANTS = [P(f"ar_tire_plant{i}", f"pk:wfarm/wfarm_5_{n:03d}", foot=[2, 1]) for i, n in enumerate((33, 34, 36, 37))]
TRELLIS = [P(f"ar_trellis{i}", f"pk:wfarm/wfarm_5_{n:03d}", foot=[2, 1]) for i, n in enumerate((25, 27, 29, 31))]
FRUIT = [P("ar_berries", "pk:wfarm/wfarm_5_023", foot=[2, 1]), P("ar_fruit", "pk:wfarm/wfarm_5_024", foot=[2, 1])]
SHELF_PLANTS = [P("ar_shelf_plants", "pk:wfarm/wfarm_1_085", foot=[2, 1], sight=True),
                P("ar_shelf_plants_b", "pk:wfarm/wfarm_1_086", foot=[2, 1], sight=True)]
RUST_BARRELS = [P(f"ar_rbarrel{i}", f"pk:wfarm/wfarm_1_{n:03d}", search="junk", title="бочка") for i, n in enumerate((7, 36))]
TIRES = [P("ar_tires", "pk:wfarm/wfarm_4_036", foot=[2, 1]), P("ar_tires_b", "pk:wfarm/wfarm_4_037", foot=[2, 1])]
TARP = [P("ar_tarp", "pk:wfarm/wfarm_4_015", foot=[2, 1], sight=True, search="crate", title="ящики под брезентом"),
        P("ar_tarp_b", "pk:wfarm/wfarm_4_027", foot=[2, 1], sight=True)]
BENCH = P("ar_stool", "pk:ucamp/ucamp_2_084")
LAUNDRY = P("ar_laundry", "pk:wfarm/wfarm_3_000", foot=[4, 1], sight=True)
CABBAGES = "pk:wfarm/p5/0,2,8,2"
GREENS = "pk:wfarm/p5/4,0,4,2"
TOOL_RACK = P("ar_tool_rack", "pk:wfarm/p3/8,10,2,2", foot=[2, 1], search="tools", title="стойка с инструментами")
FERT = P("ar_fertilizer", "pk:wfarm/p3/2,10,2,2", foot=[2, 1])
FENCE = P("ar_fence", "pk:wfarm/p3/3,12,2,1", foot=[2, 1])
TENTS = [P(f"ar_tent{i}", f"pk:ucamp/ucamp_2_{n:03d}", foot=[2, 1], sight=True) for i, n in enumerate((0, 2, 8, 11, 19, 21))]
CAMPFIRE = P("ar_campfire", "pk:ucamp/ucamp_2_040", foot=[2, 1],
             light={"r": 120, "color": [255, 150, 70], "at": [0.5, 0.5], "flicker": 0.35})
GOODS = [P("ar_cans", "pk:ucamp/ucamp_2_031", foot=[2, 1], search="shelf", title="стол с консервами"),
         P("ar_water_tbl", "pk:ucamp/ucamp_2_032", foot=[2, 1])]
WELL = P("ar_well", "pk:desnat/desnat_3_026", foot=[2, 1])
TENT_WHITE = P("ar_tent_white", "pk:bazaar/bazaar_1_004", foot=[2, 2], sight=True)
WATER_BARREL = P("ar_water_barrel", "pk:desnat/desnat_3_037")
CACTI = ["r_dry_bush", "r_rocks"]
BED = P("ar_bed", "pk:west/west_2_005", foot=[2, 2])
COT = P("ar_cot", "pk:ucamp/ucamp_3_027", foot=[4, 1])
TABLE = P("ar_table", "pk:west/west_2_000", foot=[2, 1])
CHAIR = P("ar_chair", "pk:west/west_2_001")
CHEST = P("ar_chest", "pk:west/west_2_105", search="drawer", title="сундук")
SHELF = P("ar_shelf", "pk:west/west_2_116", sight=True, search="shelf", title="полка")
# каньон и пещера
WRECKS = [P("ar_wreck", "pk:zcity/zcity_2_034", foot=[2, 1], sight=True),
          P("ar_wreck_b", "pk:zcity/zcity_2_036", foot=[2, 1], sight=True)]
VAN_BURNT = P("ar_van_burnt", "pk:zcity/zcity_2_097", foot=[2, 1], sight=True)
BONE_TOTEM = P("ar_bone_totem", "pk:gcave/p1/3,2,1,2")
SKULL_POLE = P("ar_skull_pole", "pk:gcave/p1/2,8,1,2")
TEEPEE = P("ar_khan_hut", "pk:gcave/p1/0,10,2,4", foot=[2, 1], sight=True)
SPIKES = P("ar_spikes", "pk:gcave/p1/12,8,2,2", foot=[2, 1])
WEAPON_RACK = P("ar_weapon_rack", "pk:gcave/p1/14,8,2,2", foot=[2, 1], search="military", title="стойка с оружием")
HIDE = P("ar_hide", "pk:gcave/p1/10,8,2,2", block=False, layer="floor")
LOOT_PILE = P("ar_loot_pile", "pk:gcave/p1/10,10,2,2", search="military", title="добыча Ханов")
CAMP_FIRE_C = P("ar_cave_fire", "pk:gcave/p1/14,5,1,1",
                light={"r": 110, "color": [255, 150, 70], "at": [0.5, 0.5], "flicker": 0.4})
MUSHROOMS = [P("ar_mush", "pk:gcave/p1/2,4,1,1", light={"r": 60, "color": [140, 255, 170], "at": [0.5, 0.5]}),
             P("ar_mush_b", "pk:gcave/p1/2,5,1,1", light={"r": 60, "color": [120, 200, 255], "at": [0.5, 0.5]}),
             P("ar_mush_c", "pk:gcave/p1/7,4,1,1")]
BOULDERS = [P("ar_boulder", "pk:gcave/p1/4,4,1,1"), P("ar_boulder_b", "pk:gcave/p1/5,4,1,1"),
            P("ar_boulder_c", "pk:gcave/p1/4,5,1,1")]
STALAGMITE = P("ar_stalagmite", "pk:gcave/p1/8,3,1,1")
CLIFFS = [P(f"ar_cliff{i}", f"pk:desnat/p1/{x},14,2,2", foot=[2, 2], sight=True) for i, x in enumerate((8, 10, 12))]
OUTCROP = P("ar_outcrop", "pk:desnat/p1/12,4,3,2", foot=[3, 2], sight=True)
RUBBLE = [P("ar_burnt", "pk:zcity/zcity_1_122", foot=[2, 1]), P("ar_burnt_b", "pk:zcity/zcity_1_123", foot=[2, 1])]

SAND = cells("destown/p2", [(0, 0), (1, 0), (0, 1), (1, 1)])
GRAVEL = cells("destown/p2", [(4, 0), (5, 0), (4, 1), (5, 1)])
CRACK = cells("destown/p2", [(8, 0), (9, 0), (8, 1), (9, 1)])
PLANK = ["pk:bazaar/bazaar_f1_21"]
CAVE_DIRT = cells("gcave/p1", [(1, 4), (1, 5), (2, 6), (3, 6)])
CAVE_STONE = cells("gcave/p1", [(4, 6), (5, 6), (4, 7), (5, 7)])
SPRING = cells("sewer/p1", [(10, 1), (11, 1)])


# ================================================================ лагерь
W, H = 70, 50
ar = CityMap(city, "aradesh", "Лагерь Арадеша", W, H, start=(1, 24), seed=131, music="desert", world_pos=(960, 930))
ar.floor_code("s", *SAND)
ar.floor_code("g", *GRAVEL)
ar.floor_code("k", *CRACK)
ar.paint("s", 0, 0, W - 1, H - 1)
ar.paint("k", 8, 6, 62, 44)                            # утоптанная земля лагеря
ar.paint("g", 0, 23, W - 1, 26)                        # колея от въезда до каньона
ar.exits = [(0, y) for y in range(23, 27)]
ar.reserve(0, 22, W - 1, 27)

# у въезда — шатёр «Детей Единства»: бочки с водой, очередь
ar.put(TENT_WHITE, 9, 18)
for x in (12, 13, 14):
    ar.put(WATER_BARREL, x, 20)
ar.npcs += [["unity_sister", 11, 21], ["settler_kai", 15, 21]]

# север: дом собраний Арадеша; перед ним — костёр и скамьи: здесь решают всё
ar.building(28, 4, 14, 10, "planks", south=(6,))
ar.reserve(34, 14, 35, 16)
ar.put(CAMPFIRE, 34, 18)
for x, y in ((32, 18), (37, 18), (33, 20), (36, 20)):      # табуреты вокруг костра
    ar.put(BENCH, x, y)

# северо-запад: палатки переселенцев рядами, верёвка с бельём
for i, (x, y) in enumerate(((10, 7), (14, 7), (18, 7), (22, 7), (10, 12), (14, 12), (18, 12), (22, 12))):
    ar.put(TENTS[i % len(TENTS)], x, y)
ar.put(LAUNDRY, 12, 15)
ar.box(TARP[0], 24, 15, "ящики под брезентом", {"консервы": 1, "бинт": 1})

# северо-восток: теплица, бак с дождевой водой (почти пустой), грядки в бочках и покрышках
ar.put(GREENHOUSE, 46, 5)
ar.put(WATER_TANK, 51, 6)
for i, x in enumerate((54, 57, 60)):
    ar.put(BARREL_PLANTS[i], x, 7)
for i, x in enumerate((46, 49, 52, 55, 58)):
    ar.put(TIRE_PLANTS[i % 4], x, 11)
ar.put(SHELF_PLANTS[0], 46, 15)
ar.put(SHELF_PLANTS[1], 49, 15)
ar.put(FRUIT[0], 53, 15)
ar.put(FRUIT[1], 56, 15)
ar.box(TOOL_RACK, 60, 15, "стойка с инструментами", {"лопата": 1, "гаечный ключ": 1})

# юго-запад: поле — капуста и зелень на вскопанной земле, за изгородью; шпалеры с бобами
ar.stamp("ar_field", CABBAGES, 10, 32, water=False)
ar.stamp("ar_field_b", CABBAGES, 10, 34, water=False)
ar.stamp("ar_greens", GREENS, 19, 32, water=False)
ar.stamp("ar_greens_b", GREENS, 19, 34, water=False)
ar.hwall([FENCE], 9, 25, 30, gaps=(16, 17))
ar.hwall([FENCE], 9, 25, 38)
for i, x in enumerate((10, 13, 16, 19, 22)):
    ar.put(TRELLIS[i % 4], x, 40)
ar.put(FERT, 26, 41)
ar.npcs += [["farmer_ruth", 17, 36]]

# юг: высохший колодец — рядом бадья, копаные ямы, лопаты; отсюда видно, что воды нет
ar.put(WELL, 34, 36)
ar.put(TUBS[0], 31, 38)
ar.put(TUBS[1], 37, 38)
ar.put(RUST_BARRELS[0], 33, 40)
ar.npcs += [["well_digger", 36, 34]]

# юго-восток: мастерская и сарай, ящики под брезентом, покрышки
ar.put(WORKSHOP, 46, 33)
ar.put(SHED, 54, 33)
ar.put(SHACK_TIN, 59, 39)
ar.put(TIRES[0], 46, 39)
ar.put(TIRES[1], 50, 41)
ar.put(TARP[1], 53, 41)
ar.box(RUST_BARRELS[1], 44, 36, "бочка мастерской", {"пружина": 1, "изолента": 1})
ar.npcs += [["mechanic_vic", 51, 36]]

ar.npcs += [["aradesh", 34, 17], ["settler_kid", 20, 17], ["settler_old", 39, 21], ["settler_woman", 16, 10]]
for _, x, y in ar.npcs:
    ar.reserve(x, y, x, y)
ar.scatter(CACTI + ["r_bones"], 1, 1, W - 2, 5, 8)
ar.scatter(CACTI, 1, 45, W - 2, H - 2, 8)
ar.scatter(CACTI, 63, 1, W - 2, H - 2, 6)


# ================================================================ дом собраний
hl = CityMap(city, "aradesh_hall", "Дом собраний", 24, 18, start=(11, 16), seed=132, interior=True, music="desert")
hl.floor_code("F", *PLANK)
hl.wall_code("W", "pk:bazaar/bazaar_w2_12")
hl.room(1, 1, 23, 17, "W", "F")
hl.opening(11, 17, 12, 17, "F")
ar.portal([(34, 13), (35, 13)], "aradesh_hall", (11, 15), "Дом собраний")
hl.portal([(11, 17), (12, 17)], "aradesh", (34, 15), "Наружу")
# стол совета посередине, стулья по сторонам; полка и терминал переселенцев у северной стены
hl.put(TABLE, 9, 9)
hl.put(TABLE, 11, 9)
hl.put(CHAIR, 8, 9)
hl.put(CHAIR, 13, 9)
hl.put(SHELF, 3, 4)
hl.terminal(14, 4, "aradesh_log")
# угол семьи Арадеша: кровать, сундук
hl.put(BED, 19, 4)
hl.box(CHEST, 21, 8, "сундук Арадеша", {"флаг Убежища 15": 1, "крышки": 40}, owner="aradesh")
hl.put(GOODS[1], 3, 13)
hl.put(GOODS[0], 6, 13)                                  # припасы общины — на виду, делят поровну
hl.put(COT, 15, 13)                                      # койка для гостей и больных
for x in (20, 21):
    hl.put(WATER_BARREL, x, 15)                          # бочки для воды — пустые
hl.put(SHELF, 6, 4)
hl.stamp("ar_hall_rug", "pk:casino/p3/0,0,2,2", 9, 10, water=False)
hl.npcs += [["aradesh_wife", 18, 11]]


# ================================================================ каньон
W, H = 60, 44
cn = CityMap(city, "aradesh_canyon", "Каньон у лагеря", W, H, start=(1, 21), seed=133, music="raiders")
cn.floor_code("s", *SAND)
cn.floor_code("g", *GRAVEL)
cn.paint("s", 0, 0, W - 1, H - 1)
FLOOR = set()
for x0, y0, x1, y1 in ((0, 18, 30, 25),                # горло каньона с запада
                       (22, 6, 44, 30),                # широкая чаша посередине
                       (40, 26, 58, 40),               # юго-восточный отрог — стоянка Ханов
                       (44, 3, 56, 12)):               # северный отрог — к пещере
    FLOOR |= {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}
cn.paint("g", 0, 20, 28, 23)
city.road(ar, [(69, y) for y in range(23, 27)], cn, [(0, y) for y in range(20, 24)], "Каньон", "Лагерь", step=(1, 0))
cn.reserve(0, 19, 6, 24)

# сожжённый фургон культа: остов, пятна гари, рассыпанные ящики — груза нет, только следы винтов
cn.put(VAN_BURNT, 30, 14)
cn.put(WRECKS[0], 25, 10)
for x, y in ((28, 16), (33, 12), (35, 15)):                   # обломки и сгоревшие ящики вокруг
    cn.put(RUBBLE[(x + y) % 2], x, y)
cn.box("hb_crate", 34, 17, "разбитый ящик с печатью круга", {"накладная культа": 1})
cn.terminal(27, 18, "convoy_wreck")

# стоянка Ханов: хижины из шкур, тотемы с черепами, стойка с оружием, костёр
cn.put(TEEPEE, 46, 29)
cn.put(TEEPEE, 52, 29)
cn.put(BONE_TOTEM, 43, 28)
cn.put(SKULL_POLE, 56, 34)
cn.put(SPIKES, 41, 33)
cn.put(CAMP_FIRE_C, 49, 35)
cn.put(HIDE, 47, 37)
cn.box(WEAPON_RACK, 54, 37, "стойка с оружием Ханов", {"патроны": 15, "охотничий нож": 1}, owner="khan_chief")
cn.box(LOOT_PILE, 44, 38, "добыча Ханов", {"крышки": 70, "консервы": 2}, owner="khan_chief")
cn.npcs += [["khan_chief", 50, 33], ["khan_a", 45, 34], ["khan_b", 55, 31]]

# вход в пещеру — в северном отроге
cn.props.append(["x_puddle", 50, 4])
cn.portal([(49, 3), (50, 3), (51, 3)], "aradesh_cave", (6, 36), "Пещера")
cn.reserve(48, 3, 52, 6)
cn.enemies += [["radscorpion", 48, 9], ["radscorpion", 38, 7]]
# стены каньона — скалы сплошь вокруг дна (клетки 2×2, ни одна не заходит на дно)
for y in range(0, H, 2):
    for x in range(0, W, 2):
        if not {(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)} & FLOOR:
            cn.props.append([CLIFFS[(x * 7 + y * 3) % 3], x, y])
            cn.blocked.update({(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)})
for x, y in ((24, 7), (40, 20), (57, 39), (23, 28)):
    cn.maybe(OUTCROP, x, y)
cn.scatter(BOULDERS + ["r_bones", "r_dry_bush"], 1, 1, W - 2, H - 2, 26)


# ================================================================ пещера
W, H = 48, 40
cv = CityMap(city, "aradesh_cave", "Пещера радскорпионов", W, H, start=(6, 36), seed=134, interior=True, music="caves")
cv.floor_code("d", *CAVE_DIRT)
cv.floor_code("t", *CAVE_STONE)
cv.floor_code("~", *SPRING)
cv.water_codes = ("~",)
cv.paint("x", 0, 0, W - 1, H - 1)
cv.paint("d", 3, 30, 12, 37)                           # вход
cv.paint("d", 7, 20, 11, 30)                           # ход на север
cv.paint("d", 4, 10, 22, 21)                           # первый грот — гнёзда
cv.paint("d", 20, 14, 30, 17)                          # перешеек
cv.paint("t", 28, 6, 44, 24)                           # большой грот — родник
cv.paint("d", 26, 24, 34, 34)                          # тупик с костями переселенца
cv.paint("~", 33, 10, 39, 15)                          # подземный родник
cv.portal([(6, 37), (7, 37)], "aradesh_canyon", (50, 5), "Наружу, в каньон")
cv.reserve(4, 33, 10, 37)
for x, y in ((6, 13), (16, 12), (12, 18), (30, 21), (42, 9), (11, 31)):
    cv.put(MUSHROOMS[(x + y) % 3], x, y)
for x, y in ((5, 17), (19, 19), (29, 8), (43, 20), (27, 30)):
    cv.put(BOULDERS[(x + y) % 3], x, y)
cv.put(STALAGMITE, 21, 11)
cv.put(STALAGMITE, 41, 22)
# тупик: кости переселенца, который первым нашёл родник; его записка — у тела
cv.put("r_bones", 30, 31)
cv.box("ar_tarp", 32, 31, "рюкзак переселенца", {"записка Тома": 1, "лопата": 1})
cv.enemies += [["radscorpion", 10, 14], ["radscorpion", 17, 18], ["radscorpion", 9, 24], ["radscorpion", 31, 18],
               ["radscorpion", 42, 16], ["radscorpion_queen", 36, 8]]
cv.scatter(["r_bones"], 4, 10, 30, 21, 6)

city.save(gap_exempt=("unity_sister", "settler_kai"))
L = json.load(open("data/locations.json", encoding="utf-8"))
L["aradesh"].update({"world_name": "Лагерь Арадеша", "discover": True})
L["aradesh_cave"]["clear_flag"] = "aradesh_spring_cleared"     # пещера чиста — вода возвращается в колодец
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
