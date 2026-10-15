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
BARBED_A = P("ar_barbed", "pk:mbase/p1/8,2,2,2", foot=[2, 1], keybg=True)
WATCH_A = P("ar_watch_torch", "pk:cult/cult_2_068", block=False, light={"r": 120, "color": [255, 170, 80], "at": [0.5, 0.3], "flicker": 0.5})
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
STALAGMITE = P("ar_stalagmite", "pk:dcave/p1/8,6,2,2", foot=[1, 1], keybg=True)
STALAG_B = P("ar_stalagmite_b", "pk:dcave/p1/12,2,2,2", foot=[1, 1], keybg=True)
CRYSTALS_A = [P("ar_crystal_a", "pk:dcave/p1/9,8,1,1", block=False, keybg=True, light={"r": 60, "color": [210, 130, 255], "at": [0.5, 0.5]}),
              P("ar_crystal_b", "pk:dcave/p1/10,8,1,1", block=False, keybg=True, light={"r": 60, "color": [120, 255, 160], "at": [0.5, 0.5]})]
NEST_A = P("ar_nest", "pk:dcave/p1/6,10,2,2", foot=[2, 1], keybg=True)               # гнездо скорпионов — из набора
NEST_B = P("ar_nest_b", "pk:dcave/p1/8,10,2,2", foot=[2, 1], keybg=True)
BONES_A = P("ar_drag_bones", "pk:dcave/p1/1,10,3,2", block=False, keybg=True)
COBBLE_A = cells("dcave/p2", [(4, 1), (5, 1), (4, 2), (5, 2)])
CLIFFS = [P(f"ar_cliff{i}", f"pk:desnat/p1/{x},14,2,2", foot=[2, 2], sight=True) for i, x in enumerate((8, 10, 12))]
OUTCROP = P("ar_outcrop", "pk:desnat/p1/12,4,3,2", foot=[3, 2], sight=True, keybg=True)
RUBBLE = [P("ar_burnt", "pk:zcity/zcity_1_122", foot=[2, 1]), P("ar_burnt_b", "pk:zcity/zcity_1_123", foot=[2, 1])]

PIT_A = [P("ar_pit_a", "pk:dcave/p1/2,8,2,2", block=False, layer="floor", keybg=True), P("ar_pit_b", "pk:dcave/p1/4,8,2,2", foot=[1, 1], layer="floor", keybg=True)]
MOSS_A = [P("ar_moss", "pk:dcave/p1/10,14,2,2", block=False, layer="floor", keybg=True)]
PEBBLE_A = [P(f"ar_pebbles{i}", f"pk:dcave/p1/{x},{y},1,1", block=False, keybg=True) for i, (x, y) in enumerate(((2, 4), (3, 4), (4, 4), (2, 5), (5, 5)))]
SAND = ["pk:desnat/p1/0,0,1,1", "pk:desnat/p1/1,0,1,1", "pk:desnat/p1/0,1,1,1"]   # тот же песок, что в каньоне: граница без скачка цвета
GRAVEL = ["noise:pk:mbase/p1/9,9,1,1"]                 # серый укатанный гравий колеи — читается на глине и песке
CRACK = ["noise:pk:rvill/p2/0,11,1,1"]                # тёплая приглушённая глина лагеря — не оранжевая заливка
PLAZA_A = cells("destown/p2", [(4, 0), (5, 0), (4, 1), (5, 1)])
PLANK = ["pk:bazaar/bazaar_f1_21"]
CAVE_DIRT = cells("dcave/p1", [(0, 2), (1, 2), (0, 3), (1, 3)])          # серо-бурая земля Dragon Cave
CAVE_DARK = cells("dcave/p1", [(0, 0), (1, 0), (0, 1), (1, 1), (2, 0), (3, 0)])   # земля с крупными трещинами
CAVE_GRAVEL = cells("dcave/p2", [(4, 7), (5, 7), (6, 7), (7, 7)])
CAVE_STONE = cells("gcave/p1", [(4, 6), (5, 6), (4, 7), (5, 7)])
SPRING = cells("sewer/p1", [(10, 1), (11, 1)])


# ================================================================ лагерь
W, H = 70, 50
ar = CityMap(city, "aradesh", "Лагерь Арадеша", W, H, start=(1, 24), seed=131, music="desert", world_pos=(960, 930))
ar.floor_code("s", *SAND)
ar.floor_code("g", *GRAVEL)
ar.floor_code("k", *CRACK)
ar.floor_code("q", "noise:pk:desnat/p1/0,0,1,1")           # светлая утоптанная тропа
ar.floor_code("w", "pk:fishv/p4/6,10,1,1", "pk:fishv/p4/6,11,1,1", "pk:fishv/p4/5,10,1,1")
ar.piers = ("w",)
ar.paint("s", 0, 0, W - 1, H - 1)
ar.paint_ragged("k", 5, 3, 65, 47, depth=4)            # утоптанная земля лагеря — край рваный, в песок
ar.paint("g", 0, 23, W - 1, 26)                        # колея от въезда до каньона
ar.hwall([FENCE], 5, 30, 2, gaps=(17, 18))             # северная граница: забор, ворота, дальше — колючка за домом собраний
ar.hwall([BARBED_A], 31, 65, 2)
ar.hwall([FENCE], 5, 30, 47, gaps=(17, 18))
ar.hwall([BARBED_A], 31, 65, 47, gaps=(54, 55))
ar.side_fence("wire", 5, 3, 46, gaps=(23, 24, 25, 26))   # западная и восточная — колючка, въезд по колее свободен
ar.side_fence("wire", 65, 3, 46, gaps=(23, 24, 25, 26))
for x, y in ((6, 3), (64, 3), (6, 46), (64, 46), (17, 3), (54, 46)):
    ar.maybe(WATCH_A, x, y, allow_reserved=True)
# Дорожки: от колеи к дому собраний, к палаткам, к полям и к мастерской — лагерь ходит по тропам, а не по целине
ar.paint("q", 34, 14, 35, 22)                          # к дому собраний
ar.paint("q", 8, 20, 12, 22)                           # к шатру у въезда
ar.paint("q", 12, 12, 34, 13)                          # вдоль палаток
ar.paint("q", 12, 14, 13, 22)
ar.paint("q", 28, 27, 29, 36)                          # к колодцу и полям
ar.paint("q", 10, 36, 36, 37)
ar.paint("q", 44, 27, 45, 36)                          # к мастерской
ar.paint("q", 40, 36, 60, 37)
ar.paint("q", 44, 12, 62, 13)                          # к теплице и грядкам
ar.paint("q", 44, 14, 45, 22)
ar.paint("w", 30, 18, 39, 21)                          # дощатая площадка вокруг костра собраний
ar.exits = [(0, y) for y in range(23, 27)]
ar.reserve(0, 22, W - 1, 27)

# у въезда — шатёр «Детей Единства»: бочки с водой, очередь
ar.put(TENT_WHITE, 9, 18)
for x in (12, 13, 14):
    ar.put(WATER_BARREL, x, 20)
ar.npcs += [["unity_sister", 11, 21], ["settler_kai", 15, 21]]

# север: дом собраний Арадеша; перед ним — костёр и скамьи: здесь решают всё
ar.building(30, 6, 10, 8, "planks", south=(4,))        # дом собраний — компактнее: большая крыша давила на лагерь
ar.reserve(34, 14, 35, 16)
# пристройки дома собраний: навес-склад слева, сторожка справа, знамёна и лавки у крыльца — дом больше не одинокая плита
ar.maybe(SHED, 24, 7)
ar.maybe(SHACK_TIN, 41, 7)
for x in (31, 38):
    ar.maybe("bench_7", x, 14)
ar.maybe(WATER_BARREL, 29, 12)
ar.maybe(WATER_BARREL, 41, 12)
for x in (32, 37):
    ar.maybe("lantern_lit", x, 14, allow_reserved=True)
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
# общая кухня под открытым небом: плиты-костры, столы, лавки, бочки с водой, сушилки — здесь лагерь ест вместе
for x, y in ((48, 16), (52, 16), (56, 16)):
    ar.maybe("table_2", x, y)
for x, y in ((48, 18), (52, 18), (56, 18)):
    ar.maybe("bench_7", x, y)
ar.maybe(CAMPFIRE, 50, 14)
ar.maybe(CAMPFIRE, 56, 14)
for x, y in ((46, 20), (58, 20), (60, 17)):
    ar.maybe(WATER_BARREL, x, y)
# торговый ряд у колеи: столы, палатка скупщика, фонари — первое, что видит входящий
for x, y in ((14, 28), (18, 28), (22, 28)):
    ar.maybe(GOODS[(x // 4) % len(GOODS)], x, y)
ar.maybe(TENT_WHITE, 26, 29)
# тропы освещены: факелы-фонари через каждые шесть клеток
for x, y in ((34, 14), (35, 21), (13, 14), (13, 21), (28, 28), (29, 35), (44, 28), (45, 35), (45, 15), (60, 14)):
    ar.maybe("lantern_lit", x, y, allow_reserved=True)
# знамёна «Детей Единства» у входа в дом собраний, лавки вокруг костра
for x in (32, 38):
    ar.maybe("bench_7", x, 22)
ar.maybe(TARP[0], 40, 30)
ar.maybe(TARP[1], 34, 30)
for x, y in ((36, 28), (38, 31), (32, 32)):
    ar.maybe(RUST_BARRELS[0], x, y)

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
cn.floor_code("Q", *["pk:desnat/p1/0,0,1,1", "pk:desnat/p1/1,0,1,1", "pk:desnat/p1/0,1,1,1"])   # верх плато — песок, как верх скал
cn.cliff_walls(CLIFFS, FLOOR, decor=["r_rocks", "r_dry_bush", "r_bones"], plateau="Q")
for x, y in ((24, 7), (40, 20), (57, 39), (23, 28)):
    cn.maybe(OUTCROP, x, y)
cn.scatter(BOULDERS + ["r_bones", "r_dry_bush"], 1, 1, W - 2, H - 2, 26)


# ================================================================ пещера
W, H = 48, 40
cv = CityMap(city, "aradesh_cave", "Пещера радскорпионов", W, H, start=(6, 36), seed=134, interior=True, music="caves")
cv.floor_code("d", *CAVE_DIRT)
cv.floor_code("t", *CAVE_STONE)
cv.floor_code("~", *SPRING)
cv.floor_code("o", *COBBLE_A)
cv.floor_code("k", *CAVE_DARK)
cv.floor_code("q", *CAVE_GRAVEL)
cv.water_codes = ("~",)
cv.paint("x", 0, 0, W - 1, H - 1)
# Планировка: вход -> ход на север -> первый грот (гнёзда скорпионов, кости) -> узкий перешеек -> большой каменный грот
# с родником и королевой -> тупик с телом переселенца Тома. Формы — гроты и извилистые ходы, а не прямоугольники.
cv.blob("d", 7, 34, 6, 4)                              # вход
cv.tunnel("d", [(8, 31), (9, 26), (9, 21)], width=3, wobble=1)
cv.blob("d", 13, 15, 10, 6)                            # первый грот — гнёзда
cv.tunnel("d", [(21, 15), (25, 16), (29, 14)], width=3, wobble=1)
cv.blob("t", 36, 15, 9, 9)                             # большой грот — родник
cv.tunnel("d", [(33, 23), (31, 27), (30, 31)], width=3, wobble=1)
cv.blob("d", 30, 31, 5, 4)                             # тупик с костями переселенца
cv.blob("o", 36, 12, 7, 5, wobble=0.22)                # каменная площадка вокруг родника
cv.blob("~", 36, 12, 3, 2, wobble=0.25)                # подземный родник
cv.portal([(6, 37), (7, 37)], "aradesh_canyon", (50, 5), "Наружу, в каньон")
cv.reserve(4, 33, 10, 37)
for x, y in ((9, 12), (17, 12), (12, 19), (34, 20), (40, 9), (7, 33)):
    cv.maybe(MUSHROOMS[(x + y) % 3], x, y)
for x, y in ((7, 17), (18, 18), (31, 10), (41, 19), (28, 33)):
    cv.maybe(BOULDERS[(x + y) % 3], x, y)
for i, (x, y) in enumerate(((21, 12), (41, 21), (6, 30), (28, 14))):
    cv.maybe((STALAGMITE, STALAG_B)[i % 2], x, y)
# гнёзда первого грота: кучки костей и яйца вперемешку, чтобы место читалось как логово
for i, (x, y) in enumerate(((8, 12), (13, 10), (17, 16), (11, 18))):
    cv.maybe((NEST_A, NEST_B)[i % 2], x, y)               # гнёзда радскорпионов
for x, y in ((10, 14), (15, 12)):
    cv.maybe(BONES_A, x, y)
for x, y in ((33, 9), (40, 11), (34, 18), (38, 20)):
    cv.maybe(CRYSTALS_A[(x + y) % 2], x, y)
# тупик: кости переселенца, который первым нашёл родник; его записка — у тела
cv.put("r_bones", 29, 31)
cv.box("ar_tarp", 32, 31, "рюкзак переселенца", {"записка Тома": 1, "лопата": 1})
cv.maybe("pickaxe", 28, 30)
cv.maybe("lantern_lit", 31, 29)
cv.enemies += [["radscorpion", 10, 14], ["radscorpion", 9, 24], ["radscorpion", 31, 25],
               ["radscorpion", 38, 18], ["radscorpion_queen", 37, 9]]


# пустыри обживаются сценками (экскурсия по городам показала голый песок)
# юго-восток: двор мастерской — хлам под брезентом, покрышки, стойка с инструментом, бочки
for name, x, y in ((YARD, 40, 38), (TOOL_RACK, 45, 37), (TIRES[1], 44, 41), (RUST_BARRELS[0], 47, 41),
                   (TARP[0], 49, 38), (FERT, 52, 41), (SHED, 54, 34), (WATER_TANK, 50, 33), (LAUNDRY, 40, 33)):
    ar.maybe(name, x, y)
print("обжито в лагере:", ar.dress_empty([
    [(TENTS[0], 0, 0), (TENTS[2], 3, 0), (CAMPFIRE, 1, 2), (BENCH, 0, 3), (BENCH, 3, 3)],
    [(TIRE_PLANTS[0], 0, 0), (TIRE_PLANTS[1], 2, 0), (BARREL_PLANTS[0], 0, 2), (TRELLIS[0], 2, 2), (WATER_BARREL, 4, 1)],
    [(LAUNDRY, 0, 0), (TUBS[0], 0, 2), (BENCH, 3, 2)],
    [(TENTS[4], 0, 0), (BEDS[0], 3, 0), (TARP[1], 0, 2), (TIRES[0], 3, 2)],
    [(TRELLIS[1], 0, 0), (TRELLIS[2], 2, 0), (FRUIT[0], 0, 2), (FRUIT[1], 2, 2), (FENCE, 4, 0)],
    [(WATER_TANK, 0, 0), (TUBS[1], 3, 0), (BARREL_PLANTS[1], 0, 2), (FERT, 3, 2)],
    [(TENTS[5], 0, 0), (GOODS[1], 3, 0), (CHAIR, 3, 1), (TIRE_PLANTS[2], 0, 2)],
], ground="k", block=6, margin=1, chance=1.0))
print("обжито по краям:", ar.dress_empty([
    [("r_shack", 0, 0), ("pile_junk", 5, 1), ("barrel_wood", 0, 3), ("x_fire_barrel", 3, 3)],
    [("r_tent_beige", 0, 0), ("r_tent_low", 3, 0), ("campfire", 2, 2), ("r_logs", 4, 2), ("barrel_wood", 0, 2)],
    [("r_car_wreck", 0, 0), ("pile_tires", 0, 2), ("r_trash", 3, 2)],
    [("r_camper", 0, 0), ("r_awning", 0, 2), ("crate", 3, 2), ("sack", 4, 2)],
    [("r_water_tower_b", 3, 0), ("barrel_wood", 4, 1), ("bucket", 2, 1), ("r_barrels", 5, 1)],
    [("x_cross", 0, 0), ("x_grave", 0, 1), ("x_cross", 2, 0), ("x_grave", 2, 1), ("x_cross", 4, 0), ("x_grave", 4, 1), ("r_dtree_a", 5, 2)],
    [("r_dumpster", 0, 0), ("pile_cans", 2, 0), ("r_trash", 0, 2), ("crate_broken", 3, 2)],
    [("r_pickup", 0, 0), ("r_barrels", 3, 0), ("r_barrels", 3, 1), ("pile_scrap", 0, 2)],
    [("r_billboard", 0, 0), ("r_dtree_a", 2, 1), ("r_bones", 3, 2)],
], ground="s", block=6, margin=1, chance=1.0))

for x, y in ((9, 22), (16, 14), (33, 20), (30, 30)):
    cv.maybe(PIT_A[(x + y) % 2], x, y)
for x, y in ((7, 14), (20, 13), (40, 14), (30, 31)):
    cv.maybe(MOSS_A[0], x, y)
cv.scatter(PEBBLE_A, 1, 1, 46, 38, 20)
cv.patchwork("d", ["k", "k", "k"], 16, 2, 4, seed=2)
cv.cave_style = True
cv.erode_cave(keep=[(3, 33, 12, 38)])
cv.scatter(["stones_12", "stones_19"], 1, 1, 46, 38, 12)
city.save(gap_exempt=("unity_sister", "settler_kai"))
L = json.load(open("data/locations.json", encoding="utf-8"))
L["aradesh"].update({"world_name": "Лагерь Арадеша", "discover": True})
L["aradesh_cave"]["clear_flag"] = "aradesh_spring_cleared"     # пещера чиста — вода возвращается в колодец
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
