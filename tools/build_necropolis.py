"""
Некрополь — город гулей в руинах Бейкерсфилда (Fallout 1, за сорок лет до Выходца из Убежища).
Второй акт. Сценарий — docs/story.md, раздел 12.

  necropolis        «Некрополь» (80×60): бульвар через руины, высотки без стёкол, остовы машин;
                    на севере — Зал Мёртвых (бывшая мэрия, дворец Сета), на северо-востоке — развалины
                    с дикими гулями и спуск в метро, на юго-западе — кладбище, на юге — Водораздел
                    (насос, на котором живёт город), на юго-востоке — рынок под эстакадой.
  necropolis_hall   Зал Мёртвых: тронный зал Сета, его покои с архивом, казарма стражи.
  necropolis_cobbs  квартира капрала Коббса: календари, на которых везде один и тот же год.
  necropolis_under  подземка: рынок гулей на платформе метро, канализация с дикими гулями,
                    в конце — полуоткрытая дверь Убежища 12.
  vault12           Убежище 12: дверь, которая нарочно не закрылась; атриум, жилой ярус,
                    кабинет смотрителя, водоочистка — откуда сорок лет назад вынесли водяной чип.

Наборы: zombie-city DLC (zcity), undead-graveyard (grave), medieval-sewer (sewer),
underground-survivor-camp (ucamp), cult-temple (cult), nuclear-bunker (nbunk).
Запуск из папки game_project:  .venv/bin/python tools/build_necropolis.py
"""
import json

from citykit import City, CityMap

city = City("necropolis", "Некрополь")


def P(name, img, **kw):
    city.prop(name, img, **kw)
    return name


# ------------------------------------------------------------ объекты: руины
TOWERS = [P(f"nc_tower{i}", f"pk:zcity/zcity_5_{n:03d}", foot=[2, 2], sight=True) for i, n in enumerate((0, 1, 2, 3, 5))]
TOWER_BROKEN = P("nc_tower_broken", "pk:zcity/zcity_5_004", foot=[2, 2], sight=True)
SHOP_ROW = P("nc_shop_row", "pk:zcity/zcity_5_022", foot=[6, 1], sight=True)
SHOP_WIDE = P("nc_shop_wide", "pk:zcity/zcity_5_017", foot=[4, 1], sight=True)
SHOPS = [P(f"nc_shop{i}", f"pk:zcity/zcity_5_{n:03d}", foot=[2, 1], sight=True) for i, n in enumerate((18, 21, 23))]
FACADE_LOW = P("nc_facade_low", "pk:zcity/zcity_5_006", foot=[4, 1], sight=True)
RUIN_WALL = P("nc_ruin_wall", "pk:zcity/zcity_5_009", foot=[9, 1], sight=True)
RUIN_WALL_S = P("nc_ruin_wall_s", "pk:zcity/zcity_5_010", foot=[3, 1], sight=True)
RUIN_GRAFFITI = P("nc_ruin_graffiti", "pk:zcity/zcity_5_016", foot=[4, 1], sight=True)
RUBBLE = [P(f"nc_rubble{i}", f"pk:zcity/zcity_4_{n:03d}", foot=[2, 1]) for i, n in enumerate((7, 8, 9, 21, 22, 23, 41))]
RUBBLE_S = [P("nc_rubble_s", "pk:zcity/zcity_5_024", foot=[2, 1]), P("nc_bricks", "pk:zcity/zcity_1_122", foot=[2, 1]),
            P("nc_bricks_b", "pk:zcity/zcity_1_123", foot=[2, 1])]
CARS = [P(f"nc_car{i}", f"pk:zcity/zcity_2_{n:03d}", foot=[2, 1], sight=True) for i, n in enumerate((1, 5, 13, 21, 22))]
WRECKS = [P(f"nc_wreck{i}", f"pk:zcity/zcity_2_{n:03d}", foot=[2, 1], sight=True)
          for i, n in enumerate((23, 34, 35, 36, 45, 46, 78, 97, 98))]
CAR_PILE = P("nc_car_pile", "pk:zcity/zcity_5_026", foot=[2, 1], sight=True)
TAXI = P("nc_taxi", "pk:zcity/zcity_5_025", foot=[2, 1], sight=True)
LAMPS = [P("nc_lamp", "pk:zcity/zcity_3_011"), P("nc_lamp_b", "pk:zcity/zcity_3_012")]
SIGNS = [P("nc_sign", "pk:zcity/zcity_3_036"), P("nc_sign_b", "pk:zcity/zcity_3_039")]
BILLBOARDS = [P(f"nc_billboard{i}", f"pk:zcity/zcity_4_{n:03d}", foot=[2, 1], sight=True) for i, n in enumerate((142, 143, 145))]
TREES = [P("nc_tree", "pk:zcity/zcity_4_126"), P("nc_tree_b", "pk:zcity/zcity_4_127")]
PIPES = P("nc_pipes", "pk:zcity/zcity_4_050", foot=[2, 1])
TIRES = P("nc_tires", "pk:zcity/zcity_2_024")
VENDING = P("nc_vending", "pk:zcity/zcity_1_135", sight=True, search="junk", title="автомат с газировкой")
SUBWAY = P("nc_subway", "pk:zcity/p3/8,4,2,2", foot=[2, 1], sight=True)
WALK_TILES = [f"pk:zcity/p3/{x},{y},2,2" for x, y in ((8, 10), (10, 10), (12, 10), (14, 10), (0, 12), (2, 12),
                                                         (6, 12), (8, 12), (10, 12), (14, 12), (0, 14), (6, 14))]

# кладбище
FENCE = [P("nc_iron_fence", "pk:grave/grave_2_001", foot=[2, 1]), P("nc_iron_fence_b", "pk:grave/grave_2_003", foot=[2, 1])]
CRYPT = P("nc_crypt", "pk:grave/grave_2_013", foot=[2, 2], sight=True)
CRYPT_B = P("nc_crypt_b", "pk:grave/grave_2_015", foot=[2, 2], sight=True)
CHAPEL = P("nc_chapel", "pk:grave/grave_1_004", foot=[2, 2], sight=True)
DEAD_TREES = [P(f"nc_dead_tree{i}", f"pk:grave/grave_2_{n:03d}", foot=[2, 1]) for i, n in enumerate((19, 20, 21))]
STATUE = P("nc_grave_statue", "pk:grave/grave_2_034")
GRAVE_LAMP = P("nc_grave_lamp", "pk:grave/grave_2_036",
               light={"r": 90, "color": [180, 255, 160], "at": [0.5, 0.2], "flicker": 0.4})
BONES = [P("nc_bones", "pk:grave/grave_2_022", block=False), P("nc_bones_b", "pk:grave/grave_2_027", block=False)]
OPEN_GRAVE = P("nc_open_grave", "pk:grave/grave_2_026", search="grave", title="разрытая могила")
TOMBS = [P(f"nc_tomb{i}", f"pk:grave/p2/{x},1,1,1") for i, x in enumerate((12, 13, 14, 15))]

# водораздел и рынок
TANKS = P("nc_tanks", "pk:nbunk/nbunk_2_021", foot=[3, 1], sight=True)
PUMP_BIG = P("nc_pump", "pk:nbunk/nbunk_2_028", foot=[2, 2], sight=True)
GENERATOR = P("nc_generator", "pk:ucamp/ucamp_2_057", foot=[2, 1], sight=True)
STALLS = [P(f"nc_stall{i}", f"pk:ucamp/ucamp_1_{n:03d}", foot=[2, 1], sight=True)
          for i, n in enumerate((4, 5, 6, 7, 12, 36, 54))]
GUN_STALL = P("nc_gun_stall", "pk:ucamp/ucamp_4_012", foot=[2, 1], sight=True)
TENTS = [P(f"nc_tent{i}", f"pk:ucamp/ucamp_2_{n:03d}", foot=[2, 1], sight=True) for i, n in enumerate((0, 2, 11, 21))]
SHACK = [P("nc_shack", "pk:ucamp/ucamp_2_023", foot=[2, 1], sight=True),
         P("nc_shack_b", "pk:ucamp/ucamp_2_024", foot=[2, 1], sight=True),
         P("nc_shack_c", "pk:ucamp/ucamp_2_025", foot=[2, 1], sight=True)]
CAMPFIRE = P("nc_campfire", "pk:ucamp/ucamp_2_040", foot=[2, 1],
             light={"r": 120, "color": [255, 150, 70], "at": [0.5, 0.5], "flicker": 0.35})
GOODS = [P("nc_cans", "pk:ucamp/ucamp_2_031", foot=[2, 1], search="shelf", title="стол с консервами"),
         P("nc_water_tbl", "pk:ucamp/ucamp_2_032", foot=[2, 1]),
         P("nc_bags", "pk:ucamp/ucamp_2_034", foot=[2, 1], search="bag", title="рюкзаки")]
BARREL = P("nc_barrel", "pk:ucamp/ucamp_2_042", search="junk", title="бочка")
TIRE_PILE = P("nc_tire_pile", "pk:ucamp/ucamp_2_043", foot=[2, 1])
COT = P("nc_cot", "pk:ucamp/ucamp_3_027", foot=[4, 1])
MED_CAB = P("nc_med_cab", "pk:ucamp/ucamp_3_031", foot=[1, 1], sight=True, search="drawer", title="аптечный шкаф")
BASIN = P("nc_basin", "pk:sewer/sewer_1_073", foot=[2, 1], sight=True)
PIPES_B = P("nc_pipes_b", "pk:zcity/zcity_4_120", foot=[2, 1])
CRATES = P("nc_crates", "pk:ucamp/ucamp_2_087", search="crate", title="ящик")
WORKTABLE = P("nc_worktable", "pk:ucamp/ucamp_2_016", foot=[2, 1])

# зал Сета
ALTAR = P("nc_set_dais", "pk:cult/cult_2_045", foot=[2, 1], sight=True)
ALTAR_B = P("nc_set_table", "pk:cult/cult_2_046", foot=[2, 1])
STATUES = [P("nc_statue", "pk:cult/cult_2_094"), P("nc_statue_b", "pk:cult/cult_2_121")]
BANNERS = [P("nc_banner", "pk:cult/cult_2_141", block=False), P("nc_banner_b", "pk:cult/cult_2_142", block=False)]
PILLAR = P("nc_pillar", "pk:cult/cult_2_143", sight=True)
SHELVES = [P("nc_bookcase", "pk:cult/cult_2_006", foot=[2, 1], sight=True, search="shelf", title="шкаф с бумагами"),
           P("nc_bookcase_b", "pk:cult/cult_2_007", foot=[2, 1], sight=True, search="shelf", title="шкаф с бумагами")]
CANDELABRA = P("nc_candelabra", "pk:cult/cult_2_068", block=False,
               light={"r": 90, "color": [255, 170, 80], "at": [0.5, 0.3], "flicker": 0.5})
CHEST = P("nc_chest", "pk:cult/cult_2_134", search="military", title="сундук")

# канализация и убежище
SEWER_GATE = P("nc_sewer_gate", "pk:sewer/sewer_1_001", foot=[2, 1], sight=True)
SEWER_OUTLET = P("nc_sewer_outlet", "pk:sewer/sewer_1_008", foot=[3, 1], sight=True)
SEWER_RUBBLE = [P("nc_sewer_rubble", "pk:sewer/sewer_1_042", foot=[2, 1]),
                P("nc_sewer_moss", "pk:sewer/sewer_1_041", foot=[2, 1])]
BUNKS = [P("nc_bunk", "pk:nbunk/nbunk_2_000", foot=[2, 1], sight=True),
         P("nc_bunk_b", "pk:nbunk/nbunk_2_004", foot=[2, 1], sight=True, search="locker", title="стеллаж")]
LOCKER = P("nc_locker", "pk:nbunk/nbunk_2_005", search="locker", title="шкафчик")
V_DESK = P("nc_v_desk", "pk:nbunk/nbunk_2_016", foot=[2, 1])
V_GEN = P("nc_v_gen", "pk:nbunk/nbunk_2_028", foot=[2, 2], sight=True)

CARPET = "pk:casino/p3/0,0,2,2"
ROAD = ["pk:zcity/zcity_f3_09"]
WALK = ["pk:zcity/zcity_f1_22"]
RUBBLE_FL = ["pk:zcity/zcity_f2_26"]
DIRT = ["pk:zcity/zcity_f2_00"]
STONE = ["pk:zcity/zcity_f1_23"]
WOOD = ["pk:zcity/zcity_f1_00"]
METAL = ["pk:ucamp/ucamp_f2_00"]
VAULT_FL = ["pk:nbunk/p2/4,8,1,1"]
WATER = ["pk:sewer/p1/10,1,1,1"]


# ================================================================ Некрополь
W, H = 80, 60
nc = CityMap(city, "necropolis", "Некрополь", W, H, start=(1, 29), seed=121, music="vats", world_pos=(1200, 1090))
nc.floor_code("r", *RUBBLE_FL)
nc.floor_code("a", *ROAD)
nc.floor_code("p", *WALK)
nc.floor_code("d", *DIRT)
nc.floor_code("s", *STONE)
nc.paint("r", 0, 0, W - 1, H - 1)
nc.paint("p", 0, 26, W - 1, 33)                       # тротуары бульвара
nc.paint("a", 0, 28, W - 1, 31)                       # бульвар через весь город
nc.paint("p", 36, 19, 43, 57)                         # тротуары проспекта
nc.paint("a", 38, 19, 41, 57)                         # проспект: от Зала Мёртвых к Водоразделу
nc.paint("d", 3, 37, 32, 56)                          # кладбище
nc.paint("s", 46, 40, 64, 56)                         # площадь Водораздела
nc.exits = [(0, y) for y in range(28, 32)]
nc.reserve(0, 27, W - 1, 32)
nc.reserve(37, 19, 42, 57)

# север: Зал Мёртвых — бывшая мэрия; по бокам статуи, у дверей — стража Сета
nc.building(28, 3, 24, 16, "concrete", south=(10,))
nc.reserve(38, 19, 39, 21)
nc.put(STATUES[0], 33, 20)
nc.put(STATUES[1], 45, 20)
nc.put(BANNERS[0], 35, 19)
nc.put(BANNERS[1], 43, 19)

# северо-запад: высотки вдоль бульвара, за ними — дом Коббса
for i, x in enumerate((2, 5, 8, 22, 25)):
    nc.put(TOWERS[i % len(TOWERS)], x, 24)
nc.put(SHOP_ROW, 12, 25)
nc.put(TOWER_BROKEN, 19, 24)
nc.building(6, 9, 12, 10, "brick", south=(4,))        # дом капрала Коббса
nc.reserve(10, 19, 11, 22)
nc.put(CAR_PILE, 20, 12)
nc.put(BILLBOARDS[0], 21, 17)
nc.put(TREES[0], 3, 6)
nc.put(VENDING, 24, 20)

# северо-восток: развалины, где бродят дикие гули; спуск в метро
nc.put(RUIN_WALL, 56, 24)
nc.put(RUIN_GRAFFITI, 66, 24)
nc.put(RUIN_WALL_S, 71, 24)
nc.put(FACADE_LOW, 56, 8)
nc.put(TOWER_BROKEN, 64, 6)
nc.put(TOWERS[3], 74, 6)
nc.put(SUBWAY, 70, 15)
nc.reserve(70, 16, 71, 18)
nc.put(BILLBOARDS[2], 58, 15)
nc.put(TAXI, 62, 19)
nc.enemies += [["feral", 59, 11], ["feral", 66, 13], ["feral", 74, 18], ["ghoul_runner", 61, 20]]

# бульвар: остовы машин у тротуаров, фонари через равные промежутки
for i, (x, y) in enumerate(((4, 33), (14, 26), (27, 33), (48, 26), (53, 33), (64, 33), (72, 26))):
    nc.put((CARS + WRECKS)[i % 14], x, y)
for x in (10, 30, 50, 70):
    nc.put(LAMPS[(x // 10) % 2], x, 26)
    nc.put(LAMPS[(x // 10 + 1) % 2], x + 2, 33)
nc.put(SIGNS[0], 35, 26)
nc.put(SIGNS[1], 44, 33)

# юго-запад: кладбище за чугунной оградой, ворота с бульвара
nc.hwall(FENCE, 3, 32, 36, gaps=(16, 17))
nc.reserve(16, 34, 17, 39)
nc.put(CHAPEL, 4, 39)
nc.put(CRYPT, 26, 39)
nc.put(CRYPT_B, 29, 39)
for row, y in enumerate((42, 45, 48, 51, 54)):
    for x in range(5, 31, 3):
        if x in (14, 17):
            continue                                   # центральная аллея
        nc.maybe(TOMBS[(x + row) % 4] if (x + y) % 5 else "x_cross", x, y)
nc.put(STATUE, 15, 44)
nc.put(GRAVE_LAMP, 19, 40)
nc.put(GRAVE_LAMP, 13, 50)
nc.put(DEAD_TREES[0], 8, 38)
nc.put(DEAD_TREES[1], 22, 38)
nc.box(OPEN_GRAVE, 23, 55, "разрытая могила", {"жетон Vault-Tec": 1})

# юг: Водораздел — насос на водяном чипе Убежища 12, баки, очередь гулей; люк в подземку
nc.hwall(["chain_a", "chain_b", "chain_c"], 46, 64, 39, gaps=(46, 47))
nc.put(PUMP_BIG, 53, 42)
nc.put(TANKS, 57, 43)
nc.put(TANKS, 61, 43)
nc.put(GENERATOR, 50, 43)
nc.put(PIPES, 55, 46)
nc.put(BASIN, 50, 49)                                    # чаша, куда насос качает воду; к ней — очередь
nc.put(PIPES_B, 58, 48)
nc.put(BARREL, 54, 53)
nc.put(BARREL, 55, 53)
nc.box(CRATES, 63, 47, "ящик с запчастями", {"гаечный ключ": 1, "изолента": 1})
nc.props.append(["x_manhole", 59, 52])
nc.reserve(58, 51, 60, 53)

# юго-восток: рынок под эстакадой — прилавки, палатки, костёр
for i, x in enumerate((66, 69, 72, 75)):
    nc.put(STALLS[i], x, 37)
for i, x in enumerate((66, 69, 72, 75)):              # второй ряд прилавков — спиной к первому через проход
    nc.put(STALLS[(i + 4) % len(STALLS)], x, 41 if x != 69 else 41)
nc.put(TENTS[0], 66, 47)
nc.put(TENTS[2], 75, 47)
nc.put(SHACK[0], 66, 52)
nc.put(SHACK[1], 71, 52)
nc.put(SHACK[2], 75, 52)
nc.put(CAMPFIRE, 70, 47)
nc.put(BARREL, 77, 45)
nc.put(TIRE_PILE, 63, 54)

nc.npcs += [["nc_guard", 37, 22], ["nc_guard_b", 42, 22], ["cult_envoy", 46, 23], ["gravedigger", 18, 47],
            ["harry_mech", 52, 46], ["water_queue", 48, 50], ["water_queue_b", 48, 52], ["maud", 70, 39],
            ["ghoul_vendor", 74, 39], ["nc_ghoul_kid", 73, 49], ["nc_old", 33, 34]]
for _, x, y in nc.npcs:
    nc.reserve(x, y, x, y)
nc.scatter(RUBBLE + RUBBLE_S + [TIRES, "r_trash"], 1, 1, 34, 22, 14)
nc.scatter(RUBBLE + RUBBLE_S + WRECKS, 54, 1, W - 2, 22, 12)
nc.scatter(RUBBLE_S + ["r_trash", "r_bones"], 44, 34, 64, 38, 4)
nc.scatter(BONES, 4, 40, 31, 55, 6)


# ================================================================ Зал Мёртвых
hl = CityMap(city, "necropolis_hall", "Зал Мёртвых", 36, 26, start=(17, 24), seed=122, interior=True, music="vats")
hl.floor_code("F", *STONE)
hl.floor_code("C", *WOOD)
hl.wall_code("W", "pk:zcity/zcity_w1_15")
hl.room(1, 1, 26, 25, "W", "F")                      # тронный зал
hl.room(26, 1, 35, 13, "W", "C")                     # покои Сета
hl.room(26, 13, 35, 25, "W", "F")                    # казарма стражи
hl.opening(17, 25, 18, 25, "F")
nc.portal([(38, 18), (39, 18)], "necropolis_hall", (17, 23), "Зал Мёртвых")
hl.portal([(17, 25), (18, 25)], "necropolis", (38, 20), "На проспект")
hl.opening(26, 7, 26, 8, "C")
hl.opening(26, 19, 26, 20, "F")
# помост Сета у северной стены, по бокам знамёна и свечи; колонны вдоль зала
hl.put(ALTAR, 12, 5)
hl.put(BANNERS[0], 9, 3)
hl.put(BANNERS[1], 16, 3)
hl.put(CANDELABRA, 10, 6)
hl.put(CANDELABRA, 15, 6)
for y in (9, 13, 17, 21):
    hl.put(PILLAR, 4, y)
    hl.put(PILLAR, 23, y)
    hl.put(CANDELABRA, 5, y)                             # у каждой колонны — свечи: Сет не любит темноты
    hl.put(CANDELABRA, 22, y)
hl.put(BANNERS[0], 3, 3)
hl.put(BANNERS[1], 24, 3)
hl.put(STATUES[0], 7, 4)
hl.put(STATUES[1], 19, 4)
for i, y in enumerate((10, 14, 18)):                    # ковры дорожкой от дверей к помосту
    hl.stamp(f"nc_hall_carpet{i}", CARPET, 12, y, water=False)
hl.npcs += [["set", 13, 7], ["nc_hall_guard", 9, 9], ["nc_hall_guard_b", 17, 9], ["lorraine", 6, 14]]
# покои: шкафы с бумагами, стол-архив с терминалом, сундук
hl.put(SHELVES[0], 28, 4)
hl.put(SHELVES[1], 30, 4)
hl.terminal(33, 6, "set_ledger")
hl.put(ALTAR_B, 29, 9)
hl.box(CHEST, 33, 10, "сундук Сета", {"крышки": 180, "стимулятор": 2},
       requires={"item": "отмычка", "msg": "Сундук Сета. Замок довоенный, крепкий."}, owner="set")
# казарма: койки вдоль стен, оружейный стол
hl.put(COT, 28, 16)
hl.put(COT, 28, 23)
hl.put(WORKTABLE, 32, 19)
hl.box(CRATES, 34, 16, "ящик стражи", {"патроны": 20, "граната": 1}, owner="nc_hall_guard")


# ================================================================ квартира Коббса
cb = CityMap(city, "necropolis_cobbs", "Квартира Коббса", 22, 16, start=(10, 14), seed=123, interior=True, music="vats")
cb.floor_code("F", *WOOD)
cb.wall_code("W", "pk:zcity/zcity_w2_13")
cb.room(1, 1, 21, 15, "W", "F")
cb.opening(10, 15, 11, 15, "F")
nc.portal([(10, 18), (11, 18)], "necropolis_cobbs", (10, 13), "Дом Коббса")
cb.portal([(10, 15), (11, 15)], "necropolis", (10, 20), "На улицу")
# армейский порядок: койка заправлена, сундук под ней, радио на столе; по стенам — календари
cb.put(COT, 2, 5)
cb.box(CHEST, 7, 4, "армейский сундук", {"патроны": 10, "консервы": 1})
cb.put(WORKTABLE, 14, 5)
cb.terminal(18, 4, "cobbs_diary")
cb.put(SHELVES[0], 2, 10)
cb.put(BARREL, 19, 12)
cb.put("jt_radio", 16, 5)                                # радио на столе ловит одни помехи — Коббс слушает их часами
cb.put("jt_lockers", 18, 9)
cb.put(TIRE_PILE, 3, 13)
cb.npcs += [["cobbs", 15, 8]]


# ================================================================ подземка
W, H = 64, 40
un = CityMap(city, "necropolis_under", "Подземка Некрополя", W, H, start=(4, 5), seed=124, interior=True, music="caves")
un.floor_code("F", *WALK)
un.floor_code("M", *METAL)
un.floor_code("S", *STONE)
un.floor_code("~", *WATER)
un.wall_code("W", "pk:zcity/zcity_w1_15")
un.wall_code("K", "pk:zcity/zcity_w2_03")
un.water_codes = ("~",)
un.room(1, 1, 42, 24, "W", "F")                      # платформа метро — рынок гулей
un.room(42, 1, 63, 39, "K", "S")                     # канализация к Убежищу 12
un.room(1, 24, 42, 39, "K", "S")                     # старый тоннель — ночлежка
un.opening(42, 18, 42, 20, "S")
un.opening(20, 24, 21, 26, "S")
un.paint("~", 50, 4, 52, 32)                          # сточный канал
for y in (10, 22):
    un.paint("S", 50, y, 52, y + 1)                   # мостки
un.props.append(["x_ladder", 4, 4])
nc.portal([(59, 52)], "necropolis_under", (4, 5), "Люк в подземку")
un.portal([(4, 4)], "necropolis", (59, 53), "Наверх, к Водоразделу")
un.reserve(2, 4, 7, 7)
un.put(SUBWAY, 36, 4)
nc.portal([(70, 16), (71, 16)], "necropolis_under", (36, 6), "Метро")
un.portal([(36, 5), (37, 5)], "necropolis", (70, 17), "Наверх, в развалины")
un.reserve(35, 5, 38, 8)
# рынок: прилавки рядами, палатки торговцев, генератор с лампами
for i, x in enumerate((8, 12, 16, 24, 28)):
    un.put(STALLS[(i + 2) % len(STALLS)], x, 9)
un.put(GUN_STALL, 20, 9)
for i, x in enumerate((8, 14, 26)):
    un.put(GOODS[i], x, 15)
un.put(GENERATOR, 33, 12)
for x in (10, 22, 31):                                   # колонны платформы метро
    un.put(PILLAR, x, 6)
    un.put(PILLAR, x, 21)
un.put(CAMPFIRE, 18, 18)
un.put(TENTS[1], 4, 18)
un.put(TENTS[3], 34, 19)
un.box(MED_CAB, 39, 9, "аптечный шкаф", {"бинт": 2, "антирадин": 1}, owner="ghoul_healer")
un.npcs += [["zeke", 21, 11], ["ghoul_healer", 38, 11], ["under_barkeep", 13, 17], ["under_ghoul", 25, 13],
            ["under_ghoul_b", 30, 17]]
# старый тоннель: койки, бочки, костёр — здесь живут те, кому не хватило места наверху
for x in (4, 12, 28):
    un.put(COT, x, 30)
un.put(CAMPFIRE, 20, 33)
un.put(BARREL, 36, 28)
un.put(TIRE_PILE, 38, 35)
un.npcs += [["under_ghoul_c", 16, 35]]
# канализация: трубы, решётки, дикие гули у шлюза; в конце — дверь Убежища 12
un.put(SEWER_OUTLET, 44, 4)
un.put(SEWER_GATE, 58, 4)
un.put(SEWER_RUBBLE[0], 45, 28)
un.put(SEWER_RUBBLE[1], 56, 14)
un.enemies += [["feral", 47, 26], ["feral", 56, 18], ["feral", 59, 27], ["radroach", 46, 12], ["radroach", 55, 6]]
un.put("x_vault_gear12", 56, 36)
un.reserve(55, 34, 60, 38)
un.portal([(58, 36)], "vault12", (20, 5), "Убежище 12",
          requires={"flag": "v12_way", "msg": "Дверь-шестерня Убежища 12 приоткрыта на ладонь. Протиснуться можно — если знать, что внутри и зачем."})
un.scatter(["r_trash", "r_bones"] + SEWER_RUBBLE, 43, 4, 62, 38, 10)


# ================================================================ Убежище 12
W, H = 44, 34
v = CityMap(city, "vault12", "Убежище 12", W, H, start=(20, 5), seed=125, interior=True, music="lab")
v.floor_code("F", *VAULT_FL)
v.floor_code("M", *METAL)
v.wall_code("W", "pk:nbunk/nbunk_w3_17")
v.wall_code("V", "pk:nbunk/nbunk_w3_01")
v.room(1, 1, 43, 12, "V", "F")                       # входной зал: дверь-шестерня, которая не закрылась
v.room(1, 12, 16, 33, "W", "F")                      # жилой ярус
v.room(16, 12, 30, 33, "W", "F")                     # атриум
v.room(30, 12, 43, 22, "W", "M")                     # кабинет смотрителя
v.room(30, 22, 43, 33, "W", "M")                     # водоочистка
v.put("x_vault_gear12", 18, 3, force=True)                 # дверь-шестерня в стене, откачена на ладонь
v.portal([(18, 4), (19, 4)], "necropolis_under", (58, 37), "Назад, в канализацию")
v.reserve(17, 3, 23, 7)
v.opening(22, 12, 23, 14, "F")
v.opening(16, 20, 16, 21, "F")
v.opening(30, 17, 30, 18, "M")
v.opening(30, 27, 30, 28, "M")
v.terminal(6, 5, "v12_door")
for x, y in ((14, 6), (24, 5), (27, 9), (9, 9)):          # кости у двери: здесь ждали, что она закроется
    v.put(BONES[(x + y) % 2], x, y)
v.put(CRATES, 34, 9)
v.put(CRATES, 36, 9)
v.put(BUNKS[1], 40, 7)
v.put(LOCKER, 36, 4)
v.put(LOCKER, 37, 4)
# жилой ярус: двухъярусные койки рядами, шкафчики
for y in (16, 21, 26):
    v.put(BUNKS[0], 3, y)
    v.put(BUNKS[0], 9, y)
v.box(LOCKER, 14, 15, "шкафчик жильца", {"консервы": 1, "антирадин": 1})
# атриум: кости у стены — здесь собрались, когда поняли, что дверь не закроется
v.put(V_DESK, 18, 17)
for x, y in ((18, 26), (24, 29), (27, 24)):
    v.put(BONES[(x + y) % 2], x, y)
# кабинет смотрителя: стол, терминал, сейф
v.put(V_DESK, 34, 16)
v.terminal(39, 16, "v12_overseer")
v.box(CHEST, 41, 19, "сейф смотрителя", {"голодиск смотрителя": 1, "крышки": 60},
      requires={"item": "отмычка", "msg": "Сейф смотрителя Убежища 12. Замок Vault-Tec."})
# водоочистка: генератор, баки — гнездо водяного чипа пустое
v.put(V_GEN, 33, 25)
v.put(TANKS, 37, 25)
v.box(CRATES, 41, 30, "ящик запчастей водоочистки", {"плата водоочистки": 1, "гаечный ключ": 1})
v.enemies += [["feral", 8, 23], ["feral", 22, 27], ["feral", 37, 30], ["rad_mutant", 34, 29]]

city.save(gap_exempt=("nc_guard", "nc_guard_b", "cult_envoy", "harry_mech", "water_queue", "water_queue_b"))
L = json.load(open("data/locations.json", encoding="utf-8"))
L["necropolis"].update({"world_name": "Некрополь", "discover": True})
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
