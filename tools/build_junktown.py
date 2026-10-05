"""
Джанктаун — городок за стеной из хлама (Fallout 1, за сорок лет до Выходца из Убежища).
Второй акт. Сценарий — docs/story.md, раздел 11.

  junktown         «Джанктаун» (72×52): стена из машин, покрышек и куч хлама, ворота на западе
                   (из пустоши) и на востоке (на свалку); главная улица; ратуша мэра Дарквотера,
                   казино «Гизмо», лавка Дарквотеров, клиника Анны Шоу, бар «Скам-Питт», лачуги.
  junktown_dump    «Свалка Джанктауна» (60×44): горы хлама, ряды остовов машин, лагерь старьёвщиков
                   Спайка; на юго-востоке — стоянка наёмников охотника Рурка.
  junktown_hall    ратуша: кабинет мэра, архив, сейф.
  junktown_casino  казино «Гизмо»: автоматы, рулетка, блэкджек, касса, кабинет Гизмо.
  junktown_store   лавка Дарквотеров: довоенные припасы на стеллажах.
  junktown_clinic  клиника Анны Шоу: приёмная, палата, операционная; люк в подвал.
  junktown_cellar  подвал клиники: архив Анны, холодильник, сорок четыре года опытов с противоядием.
  junktown_skum    бар «Скам-Питт» и ночлежка при нём.

Наборы: wasteland-junkyard-town (jtown), modern-casino (casino), modern-convenience-store (store),
hospital (hosp), desert-town (destown), wild-west (west), bazaar (bazaar), nuclear-bunker (nbunk).
Запуск из папки game_project:  .venv/bin/python tools/build_junktown.py
"""
import json

from citykit import City, CityMap

city = City("junktown", "Джанктаун")


def P(name, img, **kw):
    city.prop(name, img, **kw)
    return name


def cells(page, pts):
    return [f"pk:{page}/{x},{y},1,1" for x, y in pts]


# ------------------------------------------------------------ объекты: город и свалка
SHACKS = [P(f"jt_shack{i}", f"pk:jtown/jtown_1_{n:03d}", foot=[2, 2], sight=True)
          for i, n in enumerate((0, 2, 7, 16, 18, 24, 27, 43, 44, 54))]
PILE_BIG = [P(f"jt_pile_big{i}", f"pk:jtown/jtown_2_{n:03d}", foot=[4, 2], sight=True) for i, n in enumerate((1, 2, 3))]
CARS = [P(f"jt_car{i}", f"pk:jtown/jtown_2_{n:03d}", foot=[4, 1], sight=True) for i, n in enumerate((8, 9, 14, 15))]
TRUCKS = [P(f"jt_truck{i}", f"pk:jtown/jtown_2_{n:03d}", foot=[4, 1], sight=True) for i, n in enumerate((16, 17, 18))]
TRAILER = P("jt_trailer", "pk:jtown/jtown_2_019", foot=[4, 1], sight=True)
VAN = P("jt_van", "pk:jtown/jtown_2_000", foot=[4, 1], sight=True)
CAB = P("jt_cab", "pk:jtown/jtown_2_005", foot=[2, 1], sight=True)
JEEP = P("jt_jeep", "pk:jtown/jtown_2_011", foot=[2, 1], sight=True)
BIKES = [P("jt_bike", "pk:jtown/jtown_2_010"), P("jt_bike_b", "pk:jtown/jtown_2_022"),
         P("jt_bike_c", "pk:jtown/jtown_2_028")]
JUNK = [P(f"jt_junk{i}", f"pk:jtown/jtown_2_{n:03d}") for i, n in
        enumerate((6, 7, 12, 13, 26, 27, 29, 47, 48, 49, 50, 54, 55))]
TIRES = P("jt_tires", "pk:jtown/jtown_2_024")
TIRE_STACK = P("jt_tire_stack", "pk:jtown/jtown_5_104")
TOXIC = P("jt_toxic", "pk:jtown/jtown_2_025", sight=True)
TOXIC_SPILL = P("jt_toxic_spill", "pk:jtown/jtown_2_004")
CORR_FENCE = [P("jt_fence_corr", "pk:jtown/jtown_1_020"), P("jt_fence_corr_b", "pk:jtown/jtown_1_021"),
              P("jt_fence_planks", "pk:jtown/jtown_1_056")]
SCRAP_HEAP = [P(f"jt_scrap{i}", f"pk:jtown/jtown_1_{n:03d}", search="junk", title="куча хлама")
              for i, n in enumerate((22, 23, 31, 38, 39, 50))]
BARRELS = P("jt_barrels", "pk:jtown/jtown_1_046", sight=True)
CRATES = P("jt_crates", "pk:jtown/jtown_1_059", sight=True, search="crate", title="штабель ящиков")
CRATE = P("jt_crate", "pk:jtown/jtown_1_052", search="crate", title="ящик")
BARREL = P("jt_barrel", "pk:jtown/jtown_1_042", search="junk", title="бочка")
SOLAR = P("jt_solar", "pk:jtown/jtown_1_058", foot=[2, 1], sight=True)
SOLAR_LOW = P("jt_solar_low", "pk:jtown/jtown_1_015")
STALL = P("jt_stall", "pk:jtown/jtown_1_009", foot=[2, 1])
SIGN = P("jt_sign", "pk:jtown/jtown_2_038")
SIGN_B = P("jt_sign_b", "pk:jtown/jtown_2_039")
TENTS = [P("jt_tent_blue", "pk:jtown/jtown_5_105", foot=[2, 2], sight=True),
         P("jt_tent_brown", "pk:jtown/jtown_5_106", foot=[2, 2], sight=True),
         P("jt_tarp", "pk:jtown/jtown_5_109", foot=[2, 2], sight=True)]
FIREPIT = P("jt_firepit", "pk:jtown/jtown_4_043",
            light={"r": 110, "color": [255, 160, 70], "at": [0.5, 0.4], "flicker": 0.35})
STOVE = P("jt_stove", "pk:jtown/jtown_4_032", sight=True)
STOVE_SMALL = P("jt_stove_small", "pk:jtown/jtown_4_035")
SORT_BINS = P("jt_sort_bins", "pk:jtown/jtown_4_028", foot=[8, 1], sight=True)
BIN = [P(f"jt_bin{i}", f"pk:jtown/jtown_4_{n:03d}", search="junk", title="ящик с деталями")
       for i, n in enumerate((16, 17, 18, 19))]
SACKS = P("jt_sacks", "pk:jtown/jtown_4_020")
LOCKERS = P("jt_lockers", "pk:jtown/jtown_4_000", foot=[2, 1], sight=True, search="shelf", title="шкафчики")
WORKBENCH = P("jt_workbench", "pk:jtown/jtown_5_064", foot=[2, 1])
RACK = P("jt_rack", "pk:jtown/jtown_5_094", foot=[2, 1], sight=True, search="shelf", title="стеллаж")
TABLE_J = P("jt_table", "pk:jtown/jtown_5_053", foot=[2, 1])
CHAIR_J = P("jt_chair", "pk:jtown/jtown_5_013")
CABINET = P("jt_cabinet", "pk:jtown/jtown_5_057", sight=True, search="shelf", title="шкаф")
FRIDGE_OLD = P("jt_fridge", "pk:jtown/jtown_5_024", sight=True, search="shelf", title="старый холодильник")
STOVE_KITCHEN = P("jt_kitchen_stove", "pk:jtown/jtown_5_051")
TV = P("jt_tv", "pk:jtown/jtown_5_040")
RADIO = P("jt_radio", "pk:jtown/jtown_5_019")
WATER_TOWER = "r_water_tower_b"

# казино
SLOTS = [P(f"jt_slot{i}", f"pk:casino/casino_1_{n:03d}", foot=[1, 1], sight=True) for i, n in enumerate(range(8))]
SLOTS_OLD = [P("jt_slot_old", "pk:casino/casino_3_027", foot=[1, 1], sight=True),
             P("jt_slot_old_b", "pk:casino/casino_3_028", foot=[1, 1], sight=True)]
ROULETTE = P("jt_roulette", "pk:casino/casino_1_026", foot=[4, 2])
BLACKJACK = P("jt_blackjack", "pk:casino/casino_3_024", foot=[4, 2])
POKER = P("jt_poker_roul", "pk:casino/casino_3_032", foot=[4, 2])
CAGE = P("jt_cashier", "pk:casino/casino_2_017", foot=[4, 2], sight=True)
STOOL = P("jt_stool", "pk:casino/casino_1_044")
CHANGE = P("jt_change", "pk:casino/casino_1_066", sight=True)
JACKPOT = P("jt_neon_jackpot", "pk:casino/casino_1_051", block=False,
            light={"r": 90, "color": [255, 200, 90], "at": [0.5, 0.5], "flicker": 0.1})
NEON_CASH = P("jt_neon_cash", "pk:casino/casino_1_052", block=False,
              light={"r": 80, "color": [120, 255, 140], "at": [0.5, 0.5], "flicker": 0.1})
NEON_ARROW = P("jt_neon_arrow", "pk:casino/casino_1_054", block=False)
CASINO_RUG = "pk:casino/p3/0,0,2,2"
CHIPS = P("jt_chips", "pk:casino/casino_2_009")
TRASH = P("jt_trashcan", "pk:casino/casino_1_065")

# лавка
SHELVES = [P(f"jt_shelf{i}", f"pk:store/store_2_{n:03d}", foot=[2, 1], sight=True, search="shelf", title="стеллаж")
           for i, n in enumerate((0, 1, 2, 3, 9, 10, 17))]
SHELF_TOOLS = P("jt_shelf_tools", "pk:store/store_2_020", foot=[2, 1], sight=True, search="shelf", title="полка с хозтоварами")
FRIDGE = P("jt_store_fridge", "pk:store/store_2_005", foot=[2, 1], sight=True, search="shelf", title="холодильник")
CHECKOUT = P("jt_checkout", "pk:store/store_2_025", foot=[4, 1])

# клиника
OP_TABLE = P("jt_op_table", "pk:hosp/hosp_1_001", foot=[4, 2])
HOSP_BED = P("jt_hosp_bed", "pk:hosp/hosp_1_007", foot=[3, 1])
DRIP = P("jt_drip", "pk:hosp/hosp_1_010")
MONITOR = P("jt_monitor", "pk:hosp/hosp_1_004", foot=[2, 1], sight=True)
MED_CART = P("jt_med_cart", "pk:hosp/hosp_1_008", search="drawer", title="медицинская тележка")
MED_SHELF = P("jt_med_shelf", "pk:hosp/hosp_1_009", foot=[1, 1], sight=True, search="drawer", title="шкаф с лекарствами")
SINK = P("jt_sink", "pk:hosp/hosp_1_013")
RECEPTION = P("jt_reception", "pk:hosp/hosp_1_024", foot=[4, 2], sight=True)
WAIT_CHAIR = P("jt_wait_chair", "pk:hosp/hosp_1_030")
OXYGEN = P("jt_oxygen", "pk:hosp/hosp_1_011")
BIOHAZ = P("jt_biohazard", "pk:hosp/hosp_1_012")
H_LOCKER = P("jt_hosp_locker", "pk:hosp/hosp_1_049", sight=True, search="drawer", title="шкафчик")

# общая мебель
BAR_COUNTER = P("jt_bar", "pk:west/west_2_108", foot=[4, 1])
SHELF_BOTTLES = P("jt_bottle_shelf", "pk:west/west_2_110", sight=True, search="shelf", title="полка с бутылками")
TABLE = P("jt_wtable", "pk:west/west_2_000", foot=[2, 1])
CHAIR = P("jt_wchair", "pk:west/west_2_001")
BED = P("jt_bed", "pk:west/west_2_005", foot=[2, 2])
DESK = P("jt_desk", "pk:west/west_2_000", foot=[2, 1])
SAFE = P("jt_safe", "pk:west/west_2_105", search="military", title="сейф")
BOOKS = P("jt_bookcase", "pk:west/west_2_116", sight=True, search="shelf", title="шкаф с бумагами")
CLOCK = P("jt_clock", "pk:west/west_2_019", sight=True)
TANKS = P("jt_tanks", "pk:nbunk/nbunk_2_021", sight=True)

SAND = cells("destown/p2", [(0, 0), (1, 0), (0, 1), (1, 1)])
GRAVEL = cells("destown/p2", [(4, 0), (5, 0), (4, 1), (5, 1)])
CRACK = cells("destown/p2", [(8, 0), (9, 0), (8, 1), (9, 1)])
PLANK = ["pk:bazaar/bazaar_f1_21"]
STONE_IN = ["pk:bazaar/bazaar_f1_19"]
COBBLE = ["pk:bazaar/bazaar_f1_26"]
METAL = cells("nbunk/p2", [(4, 8), (5, 9), (6, 10), (4, 10)])
TILE_W = ["pk:store/p1/12,0,1,1"]
CASINO_FL = ["pk:store/p1/2,8,1,1"]
SLAB = "pk:jtown/p3/4,6,4,4"

# стена из хлама: длинные куски по северу и югу, плотная полоса покрышек и мусора по бокам
WALL_H = PILE_BIG + CARS + TRUCKS + [VAN] + CORR_FENCE
WALL_V = [TIRES, TIRE_STACK] + JUNK


def junk_wall(m, x0, y0, x1, y1, gate_w=(), gate_e=()):
    """Стена из хлама по прямоугольнику: север/юг — машины и кучи, запад/восток — полоса в 2 клетки."""
    for y in (y0, y1):
        m.hwall(WALL_H, x0, x1, y)
        m.hwall(WALL_V, x0, x1, y)          # дыры между большими кусками — мелким хламом
    for x, gates in ((x0, gate_w), (x1 - 1, gate_e)):
        for y in range(y0 + 1, y1):
            if y not in gates:
                m.maybe(m.rnd.choice(WALL_V), x, y, check=False, allow_reserved=False)


# ================================================================ город
W, H = 72, 52
jt = CityMap(city, "junktown", "Джанктаун", W, H, start=(1, 26), seed=111, music="junktown", world_pos=(880, 1080))
jt.floor_code("s", *SAND)
jt.floor_code("g", *GRAVEL)
jt.floor_code("k", *CRACK)
jt.paint("s", 0, 0, W - 1, H - 1)
jt.paint("k", 5, 5, 66, 46)                             # утоптанная земля внутри стены
jt.paint("g", 0, 24, W - 1, 28)                         # главная улица от ворот до ворот
jt.exits = [(0, y) for y in range(24, 29)]
jt.reserve(0, 23, W - 1, 29)
GATES = range(23, 30)
junk_wall(jt, 3, 4, 68, 47, gate_w=GATES, gate_e=GATES)

# ворота: столбы-вывески, бочки с огнём, привратник
jt.put(SIGN, 6, 21)
jt.put(SIGN_B, 6, 31)
jt.put("x_fire_barrel", 8, 22)
jt.put("x_fire_barrel", 8, 30)
jt.put("x_fire_barrel", 64, 22)
jt.put("x_fire_barrel", 64, 30)

# север улицы: ратуша, казино «Гизмо», лавка Дарквотеров — двери на улицу, перед ними дощатый настил
jt.building(8, 9, 14, 11, "planks", south=(6,))          # ратуша
jt.building(26, 7, 20, 13, "metal", south=(8,))          # казино «Гизмо»
jt.building(50, 9, 14, 11, "brick", south=(6,))          # лавка
for x0, door in ((8, 14), (26, 34), (50, 56)):
    jt.reserve(door, 20, door + 1, 23)
jt.stamp("jt_casino_slab", SLAB, 33, 20, water=False)
jt.put(JACKPOT, 30, 21)                                   # неоновые вывески у входа в казино
jt.put(NEON_CASH, 38, 21)
jt.put(NEON_ARROW, 41, 21)
jt.put(SOLAR, 22, 12)                                     # солнечные панели ратуши
jt.put(SOLAR_LOW, 22, 15)
jt.put(BARRELS, 46, 12)                                   # задний двор казино: бочки, ящики
jt.box(CRATES, 46, 16, "ящики казино", {"самогон": 2, "крышки": 25}, owner="gizmo")
jt.put(BARREL, 59, 21)                                    # у лавки: бочка и тачка с товаром
jt.put(CRATE, 61, 21)
jt.put(BIKES[0], 24, 21)

# юг улицы: клиника, бар «Скам-Питт», лачуги
jt.building(8, 31, 14, 11, "metal", north=(6,))          # клиника Анны Шоу
jt.building(28, 31, 16, 12, "planks", north=(6,))        # «Скам-Питт»
for door in (14, 34):
    jt.reserve(door, 29, door + 1, 33)
jt.put(OXYGEN, 10, 30)                                     # у клиники — баллоны и урна для отходов
jt.put(BIOHAZ, 19, 30)
jt.put(WATER_TOWER, 24, 36)                                # общая цистерна между клиникой и баром
jt.put(BARREL, 23, 42)
jt.put(STALL, 45, 31)                                      # прилавок водовоза у перекрёстка
jt.put(TABLE_J, 30, 44)                                    # задний двор бара — стол под открытым небом
jt.put(BARRELS, 40, 44)

# лачуги: два ряда, между ними — двор с костром и верёвками
for i, (x, y) in enumerate(((50, 32), (54, 32), (58, 32), (62, 32), (50, 40), (55, 40), (61, 40))):
    jt.put(SHACKS[i % len(SHACKS)], x, y)
jt.put(FIREPIT, 56, 37)
jt.put(TENTS[0], 49, 44)
jt.put(TENTS[1], 64, 44)
jt.maybe(SACKS, 53, 37)
jt.maybe(TIRE_STACK, 60, 37)
jt.box(FRIDGE_OLD, 47, 36, "холодильник без двери", {"консервы": 1, "чистая вода": 1})

# северо-запад и северо-восток за домами — огороды из хлама и хлам
jt.scatter(JUNK + ["r_trash", "pile_scrap"], 5, 5, 66, 7, 8)
jt.scatter(["r_trash", "pile_cans", "pile_bottles", "r_planks"], 5, 30, 66, 46, 14)
jt.scatter(["r_dry_bush", "r_rocks"], 0, 0, 2, H - 1, 6)
jt.scatter(["r_dry_bush", "r_rocks", "r_bones"], 69, 0, W - 1, H - 1, 6)

jt.npcs += [["gate_guard", 7, 23], ["jt_guard", 37, 22], ["cult_recruiter", 25, 30], ["water_seller", 45, 30],
            ["jt_tinker", 63, 22], ["jt_kid", 56, 35], ["jt_woman", 52, 38], ["jt_old_scav", 60, 35],
            ["jt_drunk", 41, 30]]
for _, x, y in jt.npcs:
    jt.reserve(x, y, x, y)


# ================================================================ свалка
W, H = 60, 44
dm = CityMap(city, "junktown_dump", "Свалка Джанктауна", W, H, start=(1, 22), seed=112, music="raiders")
dm.floor_code("s", *SAND)
dm.floor_code("k", *CRACK)
dm.floor_code("g", *GRAVEL)
dm.paint("k", 0, 0, W - 1, H - 1)
dm.paint("g", 0, 20, W - 1, 24)                         # колея через свалку
dm.paint("g", 26, 4, 30, 40)                            # поперечный проезд
dm.exits = [(W - 1, y) for y in range(20, 25)]
dm.reserve(0, 19, W - 1, 25)
dm.reserve(25, 3, 31, 41)
city.road(jt, [(71, y) for y in range(24, 29)], dm, [(0, y) for y in range(20, 25)],
          "Свалка", "Джанктаун", step=(1, 0))

# лагерь старьёвщиков Спайка (северо-запад): палатки, печь, сортировка, верстак
dm.put(TENTS[2], 4, 5)
dm.put(TENTS[1], 8, 5)
dm.put(STOVE, 13, 6)
dm.put(SORT_BINS, 4, 13)
dm.put(WORKBENCH, 16, 10)
dm.put(FIREPIT, 10, 9)
dm.box(LOCKERS, 19, 6, "шкафчики старьёвщиков", {"пружина": 2, "изолента": 1, "гаечный ключ": 1}, owner="spike")
dm.box(BIN[0], 13, 15, "ящик с деталями", {"батарейки": 1, "пружина": 1})
dm.put(BIN[1], 16, 15)
dm.npcs += [["spike", 11, 11], ["scrapper", 7, 15], ["scrapper_girl", 18, 12]]

# горы хлама и ряды машин — лабиринт свалки
for x, y in ((35, 5), (42, 7), (50, 5), (36, 13), (48, 13), (6, 30), (14, 33), (20, 28)):
    dm.put(PILE_BIG[(x + y) % 3], x, y)
for i, (x, y) in enumerate(((33, 17), (38, 17), (44, 17), (50, 17), (33, 28), (38, 28), (6, 38), (12, 38),
                            (18, 38))):
    dm.put((CARS + TRUCKS)[i % 7], x, y)
dm.put(TRAILER, 54, 10)
dm.put(JEEP, 3, 27)
dm.put(CAB, 22, 34)
dm.put(TOXIC, 40, 9)
dm.put(TOXIC_SPILL, 46, 10)
for x, y in ((3, 18), (20, 17), (34, 32), (45, 26), (52, 27)):
    dm.box(SCRAP_HEAP[(x + y) % len(SCRAP_HEAP)], x, y, "куча хлама",
           {"пружина": 1, "изолента": 1} if x % 2 else {"батарейки": 1, "крышки": 6})
dm.enemies += [["rat", 40, 4], ["rat", 52, 14], ["rat", 9, 35]]

# стоянка наёмников Рурка (юго-восток): обгоревший автобус как стена, палатка, костёр
dm.put(TRUCKS[1], 43, 33)
dm.put(TENTS[0], 50, 36)
dm.put(FIREPIT, 47, 37)
dm.box(CRATE, 54, 38, "ящик наёмников", {"расписка Анны Шоу": 1, "крышки": 80, "патроны": 15},
       owner="hunter_rourke")
dm.enemies += [["raider", 46, 39], ["raider", 52, 33], ["raider_elite", 55, 40]]
# плотность свалки: ещё кучи и остовы в середине и на юго-западе, мелочь — повсюду
dm.scatter(PILE_BIG + CARS + [CAB, JEEP, TIRE_STACK], 32, 1, 58, 15, 12)
dm.scatter(PILE_BIG + CARS + [CAB, TIRE_STACK], 2, 27, 24, 42, 9)
dm.scatter(PILE_BIG + CARS + [TIRES], 32, 26, 40, 42, 5)
dm.scatter(JUNK + [TIRES, TOXIC, "r_trash", "pile_scrap", "r_bones"], 1, 1, W - 2, H - 2, 60)


# ================================================================ ратуша
hl = CityMap(city, "junktown_hall", "Ратуша Джанктауна", 24, 18, start=(11, 16), seed=113, interior=True,
             music="junktown")
hl.floor_code("F", *PLANK)
hl.wall_code("W", "pk:jtown/jtown_w2_14")
hl.room(1, 1, 23, 17, "W", "F")
hl.opening(11, 17, 12, 17, "F")
jt.portal([(14, 19), (15, 19)], "junktown_hall", (11, 15), "Ратуша")
hl.portal([(11, 17), (12, 17)], "junktown", (14, 21), "На улицу")
# кабинет мэра: стол лицом к двери, шкафы с бумагами вдоль северной стены, сейф в углу
hl.put(BOOKS, 3, 4)
hl.put(BOOKS, 5, 4)
hl.put(CLOCK, 11, 4)
hl.put(DESK, 11, 8)
hl.put(CHAIR, 13, 8)
hl.box(SAFE, 21, 4, "сейф мэра", {"крышки": 150, "лицензия казино": 1},
       requires={"item": "отмычка", "msg": "Сейф мэра. Без отмычки — никак."}, owner="mayor_darkwater")
hl.terminal(17, 5, "junktown_hall")
hl.put(TABLE, 3, 12)                                     # стол для совета
hl.put(CHAIR, 5, 12)
hl.put(TANKS, 20, 12)                                    # запас воды ратуши
hl.npcs += [["mayor_darkwater", 12, 7], ["hall_guard", 16, 13]]


# ================================================================ казино «Гизмо»
cs = CityMap(city, "junktown_casino", "Казино «Гизмо»", 34, 24, start=(12, 22), seed=114, interior=True,
             music="reno")
cs.floor_code("F", *CASINO_FL)
cs.floor_code("O", *PLANK)
cs.wall_code("W", "pk:jtown/jtown_w2_04")
cs.room(1, 6, 24, 23, "W", "F")                     # игровой зал
cs.room(24, 6, 33, 16, "W", "O")                    # кабинет Гизмо
cs.opening(12, 23, 13, 23, "F")
jt.portal([(34, 19), (35, 19)], "junktown_casino", (12, 21), "Казино «Гизмо»")
cs.portal([(12, 23), (13, 23)], "junktown", (34, 21), "На улицу")
cs.opening(24, 11, 24, 12, "O")
# неон над северной стеной, автоматы рядом вдоль неё
cs.put(JACKPOT, 4, 8)
cs.put(NEON_CASH, 14, 8)
for i, x in enumerate(range(2, 12)):
    cs.put((SLOTS + SLOTS_OLD)[i], x, 9)
cs.put(CHANGE, 13, 9)
# касса-клетка в северо-восточном углу зала, кассир за ней
cs.put(CAGE, 18, 10)
# столы: блэкджек и покер на западе, рулетка в центре на ковре
cs.stamp("jt_casino_rug", CASINO_RUG, 12, 14, water=False)
cs.put(ROULETTE, 11, 14)
cs.put(BLACKJACK, 3, 14)
cs.put(POKER, 3, 19)
cs.put(STOOL, 8, 19)
cs.put(STOOL, 17, 15)
cs.put(TRASH, 22, 21)
cs.put(TRASH, 2, 21)
# кабинет Гизмо: стол, сейф с долговой книгой, шкаф
cs.put(DESK, 28, 10)
cs.put(CHAIR, 30, 10)
cs.put(BOOKS, 26, 9)
cs.box(SAFE, 31, 9, "сейф Гизмо", {"долговая книга Гизмо": 1, "крышки": 220},
       requires={"item": "отмычка", "msg": "Сейф Гизмо. Нужна отмычка — и чтобы громила отвернулся."}, owner="gizmo")
cs.put(CHIPS, 27, 14)
cs.npcs += [["gizmo", 29, 12], ["gizmo_thug", 21, 14], ["croupier", 13, 13], ["cashier_jt", 19, 9],
            ["gambler_jt", 7, 16], ["gambler_jt_b", 10, 20]]


# ================================================================ лавка Дарквотеров
st = CityMap(city, "junktown_store", "Лавка Дарквотеров", 26, 18, start=(12, 16), seed=115, interior=True,
             music="junktown")
st.floor_code("F", *STONE_IN)
st.wall_code("W", "pk:jtown/jtown_w1_14")
st.room(1, 1, 25, 17, "W", "F")
st.opening(12, 17, 13, 17, "F")
jt.portal([(56, 19), (57, 19)], "junktown_store", (12, 15), "Лавка Дарквотеров")
st.portal([(12, 17), (13, 17)], "junktown", (56, 21), "На улицу")
# стеллажи вдоль северной стены, холодильники на востоке, касса у входа, ряд стеллажей посреди
for i, x in enumerate((2, 4, 6, 8, 14, 16)):
    st.put(SHELVES[i], x, 4)
st.put(SHELF_TOOLS, 18, 4)
st.put(FRIDGE, 22, 4)
st.put(FRIDGE, 22, 8)
for i, x in enumerate((3, 5, 7, 9)):                     # два ряда стеллажей — проходы между ними
    st.put(SHELVES[(i + 3) % 7], x, 8)
    st.put(SHELVES[(i + 5) % 7], x, 12)
st.put(SACKS, 22, 15)
st.put(CHECKOUT, 15, 12)
st.npcs += [["marsha", 17, 11]]
st.box(CRATE, 3, 15, "ящик с товаром", {"консервы": 2, "энергетический батончик": 2})


# ================================================================ клиника Анны Шоу
cl = CityMap(city, "junktown_clinic", "Клиника Анны Шоу", 30, 22, start=(14, 20), seed=116, interior=True,
             music="junktown")
cl.floor_code("F", *TILE_W)
cl.wall_code("W", "pk:jtown/jtown_w2_02")
cl.room(1, 10, 29, 21, "W", "F")                     # приёмная
cl.room(1, 1, 16, 10, "W", "F")                      # палата
cl.room(16, 1, 29, 10, "W", "F")                     # операционная и кабинет
cl.opening(14, 21, 15, 21, "F")
jt.portal([(14, 31), (15, 31)], "junktown_clinic", (14, 19), "Клиника Анны Шоу")
cl.portal([(14, 21), (15, 21)], "junktown", (14, 29), "На улицу")
cl.opening(7, 10, 8, 12, "F")
cl.opening(22, 10, 23, 12, "F")
cl.opening(16, 6, 16, 7, "F")
# приёмная: стойка лицом ко входу, стулья ожидания вдоль западной стены, шкаф с лекарствами
cl.put(RECEPTION, 18, 15)
for y in (14, 16, 18):
    cl.put(WAIT_CHAIR, 2, y)
cl.box(MED_SHELF, 27, 13, "шкаф с лекарствами", {"бинт": 2, "стимулятор": 1},
       requires={"flag": "anna_trust", "msg": "Шкаф с лекарствами заперт. Ключ — у доктора Шоу."}, owner="anna_shaw")
cl.put(SINK, 25, 13)
cl.put(H_LOCKER, 10, 13)
# палата: три койки у северной стены, капельницы рядом
for x in (2, 7, 12):
    cl.put(HOSP_BED, x, 5)
cl.put(DRIP, 5, 5)
cl.put(DRIP, 10, 5)
cl.npcs += [["patient_hank", 4, 7], ["patient_girl", 13, 7]]
# операционная: стол, монитор, тележка; кабинет Анны: стол с терминалом, люк в подвал
cl.put(OP_TABLE, 18, 4)
cl.put(MONITOR, 23, 4)
cl.box(MED_CART, 25, 4, "медицинская тележка", {"стимулятор": 1, "бинт": 2})
cl.terminal(27, 7, "anna_notes")
cl.props.append(["x_manhole", 20, 8])
cl.portal([(20, 8)], "junktown_cellar", (4, 5), "Подвал",
          requires={"flag": "anna_trust", "msg": "Люк в полу на замке. Анна носит ключ на шее, рядом с жетоном."})
cl.npcs += [["anna_shaw", 24, 8], ["orderly_tom", 6, 15]]


# ================================================================ подвал клиники
cr = CityMap(city, "junktown_cellar", "Подвал клиники", 26, 18, start=(4, 5), seed=117, interior=True,
             music="lab")
cr.floor_code("M", *METAL)
cr.wall_code("K", "pk:jtown/jtown_w1_19")
cr.room(1, 1, 25, 17, "K", "M")
cr.props.append(["x_ladder", 4, 4])
cr.portal([(4, 4)], "junktown_clinic", (20, 9), "Наверх, в клинику")
cr.reserve(2, 4, 7, 7)
# архив: шкафы вдоль стен, стол с терминалом, раскладушка — Анна ночует здесь, когда работает
cr.put(BOOKS, 10, 4)
cr.put(BOOKS, 12, 4)
cr.put(BOOKS, 14, 4)
cr.terminal(19, 5, "anna_archive")
cr.put(TABLE, 18, 10)
cr.put(CHAIR, 20, 10)
cr.put(BED, 3, 13)
cr.box(FRIDGE, 22, 4, "холодильный шкаф", {"образец ВРЭ": 1, "сыворотка Шоу-44": 1, "стимулятор": 2})
cr.put(MED_SHELF, 9, 14)
cr.put(BIOHAZ, 23, 14)
cr.put(OXYGEN, 16, 15)


# ================================================================ бар «Скам-Питт» и ночлежка
sk = CityMap(city, "junktown_skum", "Бар «Скам-Питт»", 30, 20, start=(10, 18), seed=118, interior=True,
             music="junktown")
sk.floor_code("F", *PLANK)
sk.wall_code("W", "pk:jtown/jtown_w1_20")
sk.room(1, 1, 20, 19, "W", "F")                     # зал
sk.room(20, 1, 29, 19, "W", "F")                    # ночлежка
sk.opening(10, 19, 11, 19, "F")
jt.portal([(34, 31), (35, 31)], "junktown_skum", (10, 17), "Бар «Скам-Питт»")
sk.portal([(10, 19), (11, 19)], "junktown", (34, 29), "На улицу")
sk.opening(20, 12, 20, 13, "F")
# стойка вдоль северной стены, полки с бутылками за ней, бармен между
sk.put(SHELF_BOTTLES, 3, 4)
sk.put(SHELF_BOTTLES, 9, 4)
sk.put(BAR_COUNTER, 3, 7)
sk.put(BAR_COUNTER, 7, 7)
sk.npcs += [["neal", 6, 5]]
# зал: столы со стульями, дальний стол у восточной стены — там сидит Рурк
for x, y in ((3, 11), (9, 11), (3, 15), (14, 15)):
    sk.put(TABLE, x, y)
    sk.put(CHAIR, x + 2, y)
sk.put(TABLE, 16, 9)
sk.put(CHAIR, 18, 9)
sk.put(RADIO, 15, 4)
sk.npcs += [["hunter_rourke", 17, 10], ["skum_drunk", 7, 12], ["skum_girl", 13, 13]]
# ночлежка: койки вдоль стен, сундук постояльца
for x, y in ((22, 4), (26, 4), (22, 16), (26, 16)):
    sk.put(BED, x, y)
sk.box("wardrobe", 27, 9, "сундук постояльца", {"самогон": 1, "крышки": 12})


city.save(gap_exempt=("spike", "scrapper", "scrapper_girl"))
L = json.load(open("data/locations.json", encoding="utf-8"))
L["junktown"].update({"world_name": "Джанктаун", "discover": True})
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
