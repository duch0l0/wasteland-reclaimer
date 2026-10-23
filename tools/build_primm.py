"""
Примм — казино-отели на границе штатов, ставшие городом. Третий акт.
Сценарий — docs/story.md, раздел «Примм — „Шериф умер дважды“».

  primm         «Примм» (80×54): трасса I-15 через город; на севере — отель «Бизон Стив», на юге —
                казино «Викки и Вэнс» с офисом шерифа; на западе — парковка караванов и заправка;
                на востоке — ворота к лагерю культа.
  primm_bison   отель «Бизон Стив»: холл с ресепшеном, коридор, номера жителей, номер вдовы Ривз.
  primm_vikki   казино «Викки и Вэнс»: игровой зал, бар, офис шерифа (место убийства), чёрный ход.
  primm_cellar  подвал казино: камеры (там сидит «подозреваемый» послушник), архив шерифа.
  primm_camp    лагерь «Детей Единства» под старыми американскими горками: шатры, фургон с детьми.

Наборы: amusement-park (apark), wasteland-abandoned-parking-lot (wpark), luxury-hotel (lhotel),
modern-casino (casino), wild-west (west), desert-town (destown), zombie-city (zcity), cult-temple (cult),
bazaar, underground-survivor-camp (ucamp).
Запуск из папки game_project:  .venv/bin/python tools/build_primm.py
"""
import json

from citykit import City, CityMap
from vaultkit import Lamps, entry_door

city = City("primm", "Примм")


def P(name, img, **kw):
    city.prop(name, img, **kw)
    return name


def cells(page, pts):
    return [f"pk:{page}/{x},{y},1,1" for x, y in pts]


# ------------------------------------------------------------ улица
T50CARS = [P(f"pr_t50car{i}", f"pk:town50/town50_1_{n:03d}", foot=[2, 1], sight=True) for i, n in enumerate((29, 37, 45, 53, 41, 40))]
T50_PUMPS = [P("pr_t50pump_red", "pk:town50/town50_1_102", foot=[1, 1]), P("pr_t50pump_yellow", "pk:town50/town50_1_103", foot=[1, 1])]
SIGN_DINER = P("pr_sign_diner", "pk:town50/town50_1_116", foot=[1, 1], sight=True, light={"r": 120, "color": [255, 90, 90], "at": [0.5, 0.4], "flicker": 0.1})
SIGN_MOTEL = P("pr_sign_motel", "pk:town50/town50_1_117", foot=[1, 1], sight=True, light={"r": 120, "color": [90, 200, 255], "at": [0.5, 0.4], "flicker": 0.1})
PHONE = P("pr_phone", "pk:town50/town50_1_100", foot=[1, 1])
HYDRANT = P("pr_hydrant", "pk:town50/town50_1_109", block=False)
T50LAMP = P("pr_t50lamp", "pk:town50/town50_1_120", light={"r": 150, "color": [255, 210, 140], "at": [0.5, 0.1]})
PICKET = P("pr_picket", "pk:town50/town50_1_135", foot=[2, 1], keybg=True)
DPALMS = [P(f"pr_dpalm{i}", f"pk:desnat/desnat_4_{n:03d}", foot=[1, 1]) for i, n in enumerate((49, 50, 51, 52))]
BUMPERS = [P(f"pr_bumper{i}", f"pk:apark/apark_2_{n:03d}", foot=[1, 1]) for i, n in enumerate((127, 128, 130, 137, 139, 141))]
PARK_FENCE = [P("pr_pfence_a", "pk:apark/apark_2_150", foot=[1, 1], keybg=True), P("pr_pfence_b", "pk:apark/apark_2_152", foot=[1, 1], keybg=True)]
HEDGE = P("pr_hedge", "pk:apark/apark_2_160", foot=[5, 1], keybg=True)
TRASH_A = P("pr_trash_a", "pk:apark/apark_2_044", foot=[1, 1], keybg=True)
TRASH_B = P("pr_trash_b", "pk:apark/apark_2_046", foot=[1, 1], keybg=True)
PARK_BENCH = [P("pr_pbench_a", "pk:apark/apark_2_075", foot=[1, 1], keybg=True), P("pr_pbench_b", "pk:apark/apark_2_076", foot=[1, 1], keybg=True)]
PRETZEL = P("pr_stall_pretzel", "pk:apark/apark_2_144", foot=[2, 1], sight=True, keybg=True)
GIFTS = P("pr_stall_gifts", "pk:apark/apark_2_146", foot=[2, 1], sight=True, keybg=True)
DRINKS = P("pr_stall_drinks", "pk:apark/apark_2_145", foot=[2, 1], sight=True, keybg=True)
COASTER = [P("pr_coaster", "pk:apark/apark_2_121", foot=[4, 1], sight=True),
           P("pr_coaster_long", "pk:apark/apark_2_133", foot=[6, 1], sight=True)]
COASTER_LOOP = [P("pr_coaster_loop", "pk:apark/apark_2_120", foot=[2, 1], sight=True),
                P("pr_coaster_ring", "pk:apark/apark_2_131", foot=[2, 1], sight=True)]
BOOTHS = [P(f"pr_booth{i}", f"pk:apark/apark_2_{n:03d}", foot=[1, 1], keybg=True) for i, n in enumerate((100, 101, 102))]
STALLS = [P("pr_stall_hotdog", "pk:apark/apark_1_022", foot=[2, 1], sight=True),
          P("pr_stall", "pk:apark/apark_1_030", foot=[2, 1], sight=True)]
SIGNPOST = P("pr_signpost", "pk:apark/apark_1_037")
UMBRELLA = P("pr_umbrella", "pk:apark/apark_3_028", foot=[2, 1])
LAMPS = [P("pr_lamp", "pk:apark/apark_3_064", light={"r": 140, "color": [255, 210, 140], "at": [0.5, 0.1]}),
         P("pr_lamp_b", "pk:apark/apark_3_070", light={"r": 140, "color": [255, 210, 140], "at": [0.5, 0.1]})]
TICKET = P("pr_ticket", "pk:apark/apark_1_078", foot=[2, 1], sight=True)
BENCH = P("pr_bench", "pk:apark/apark_1_066", foot=[2, 1])
WRECKS = [P(f"pr_wreck{i}", f"pk:zcity/zcity_2_{n:03d}", foot=[2, 1], sight=True) for i, n in enumerate((1, 5, 13, 21, 34, 45))]
TRUCK = P("pr_truck", "pk:jtown/jtown_2_016", foot=[4, 1], sight=True)
BRAHMIN_CART = P("pr_cart", "pk:bazaar/bazaar_1_023", foot=[2, 1], sight=True)
WATER_BARREL = P("pr_water_barrel", "pk:desnat/desnat_3_037")
CRATE = P("pr_crate", "pk:bazaar/bazaar_3_000", search="crate", title="ящик")
TIRES = P("pr_tires", "pk:ucamp/ucamp_2_043", foot=[2, 1])
GAS_PUMP = P("pr_gas_pump", "pk:zcity/zcity_1_134")
SANDBAGS = "x_sandbags"
# отель
RECEPTION = P("pr_reception", "pk:lhotel/lhotel_1_012", foot=[4, 1])
SOFA = [P("pr_sofa", "pk:lhotel/lhotel_1_022", foot=[2, 1]), P("pr_sofa_red", "pk:lhotel/lhotel_1_024", foot=[2, 1])]
HOTEL_PLANT = P("pr_hotel_plant", "pk:lhotel/lhotel_1_016", foot=[1, 1])
PALMS = [P("pr_palm", "pk:lhotel/lhotel_1_016"), P("pr_palm_b", "pk:lhotel/lhotel_1_020")]
LUGGAGE = P("pr_luggage", "pk:lhotel/lhotel_1_008")
FLOOR_LAMP = P("pr_floor_lamp", "pk:lhotel/lhotel_1_043",
               light={"r": 100, "color": [255, 220, 160], "at": [0.5, 0.1]})
DESK = P("pr_desk", "pk:lhotel/lhotel_1_029", foot=[2, 1])
BEDS = [P(f"pr_bed{i}", f"pk:lhotel/lhotel_2_{n:03d}", foot=[2, 2]) for i, n in enumerate((9, 20, 29, 52))]
ARMCHAIR = [P("pr_armchair", "pk:lhotel/lhotel_2_016"), P("pr_armchair_b", "pk:lhotel/lhotel_2_017")]
WARDROBE = P("pr_wardrobe", "pk:lhotel/lhotel_2_054", foot=[2, 1], sight=True, search="cloth", title="шкаф")
COUCH_LONG = P("pr_couch_long", "pk:lhotel/lhotel_1_044", foot=[2, 1])
# казино
SLOTS = [P(f"pr_slot{i}", f"pk:casino/casino_1_{n:03d}", foot=[1, 1], sight=True) for i, n in enumerate(range(8))]
ROULETTE = P("pr_roulette", "pk:casino/casino_1_026", foot=[4, 2])
BLACKJACK = P("pr_blackjack", "pk:casino/casino_3_024", foot=[4, 2])
CAGE = P("pr_cashier", "pk:casino/casino_2_017", foot=[4, 2], sight=True)
STOOL = P("pr_stool", "pk:casino/casino_1_044")
JACKPOT_ST = "pr_neon_jackpot"
JACKPOT = P("pr_neon_jackpot", "pk:casino/casino_1_051", block=False,
            light={"r": 90, "color": [255, 200, 90], "at": [0.5, 0.5], "flicker": 0.1})
JUKEBOX = P("pr_jukebox", "pk:town50/town50_1_084", foot=[1, 1], sight=True, light={"r": 90, "color": [255, 170, 90], "at": [0.5, 0.4], "flicker": 0.2})
CHIPS = P("pr_chips", "pk:casino/casino_2_009", foot=[1, 1])
CASINO_RUG = "pk:casino/p3/0,0,2,2"
W_ART = [P("pr_w_window", "pk:west/west_2_027", block=False), P("pr_w_painting", "pk:west/west_2_030", block=False),
         P("pr_w_mirror", "pk:west/west_2_028", block=False), P("pr_w_clock", "pk:west/west_2_011", block=False)]
BAR = P("pr_bar", "pk:west/west_2_108", foot=[4, 1])
BOTTLES = P("pr_bottle_shelf", "pk:west/west_2_110", sight=True, search="shelf", title="полка с бутылками")
OFFICE_DESK = P("pr_office_desk", "pk:west/west_2_000", foot=[2, 1])
CHAIR = P("pr_chair", "pk:west/west_2_001")
GUN_RACK = P("pr_gun_rack", "pk:gcave/p1/14,8,2,2", foot=[2, 1], search="military", title="оружейная стойка")
SAFE = P("pr_safe", "pk:west/west_2_105", search="military", title="сейф")
BOOKS = P("pr_bookcase", "pk:west/west_2_116", sight=True, search="shelf", title="шкаф с делами")
BLOOD = P("pr_blood", "pk:cult/p3/0,15,1,1", block=False, layer="floor")
CELL = P("pr_cell_bars", "pk:cult/cult_3_020", sight=True)
COT = P("pr_cot", "pk:ucamp/ucamp_3_027", foot=[4, 1])
# лагерь культа
TENT_WHITE = P("pr_tent_white", "pk:bazaar/bazaar_1_004", foot=[2, 2], sight=True)
VAN = P("pr_cult_van", "pk:zcity/zcity_2_098", foot=[2, 1], sight=True)
ALTAR = P("pr_altar", "pk:cult/cult_2_045", foot=[2, 1], sight=True)
BANNERS_C = [P("pr_banner_a", "pk:cult/cult_2_141", block=False), P("pr_banner_b", "pk:cult/cult_2_142", block=False)]
BARBED_P = P("pr_barbed", "pk:mbase/p1/8,2,2,2", foot=[2, 1], keybg=True)
TORCH_PR = P("pr_torch", "pk:cult/cult_2_068", block=False, light={"r": 110, "color": [255, 160, 70], "at": [0.5, 0.3], "flicker": 0.5})
CANDELABRA = P("pr_candelabra", "pk:cult/cult_2_068", block=False,
               light={"r": 90, "color": [255, 170, 80], "at": [0.5, 0.3], "flicker": 0.5})
CAMPFIRE_PR = "pr_campfire"
CAMPFIRE = P("pr_campfire", "pk:ucamp/ucamp_2_040", foot=[2, 1],
             light={"r": 120, "color": [255, 150, 70], "at": [0.5, 0.5], "flicker": 0.35})

SAND = ["pk:desnat/p1/0,0,1,1", "pk:desnat/p1/1,0,1,1", "pk:desnat/p1/0,1,1,1"]   # песок под цвет окружающей пустыни, без скачка
GRAVEL = ["noise:pk:destown/p2/4,0,1,1"]
WALK = ["pk:zcity/zcity_f1_22"]
PARK = ["noise:pk:destown/p2/4,0,1,1"]   # вытоптанная площадка парковки — гравий, а не тёмная плитка
PLAZA_ST = cells("apark/p2", [(8, 0), (9, 0), (8, 1), (9, 1)])      # каменные плиты площади
PARK_PAVE = cells("apark/p2", [(6, 0), (7, 0), (6, 1), (7, 1)])      # дорожки парка
ARENA_FL = cells("apark/p2", [(10, 0), (11, 0), (10, 1), (11, 1)])      # гладкая коричневая плитка арены
COASTER_PAD = ["noise:pk:destown/p2/4,0,1,1"]
HOTEL_FL = ["pk:hotel/hotel_f1_23"]          # бежевый мрамор вместо серой плитки
CARPET = ["pk:hotel/hotel_f1_03"]
CASINO_FL = ["pk:store/p1/2,8,1,1"]
WOOD = ["pk:zcity/zcity_f1_00"]
CONCRETE = ["noise:pk:nbunk/p2/0,8,1,1"]          # бетон подвала без ступенчатого узора
RUG = "pk:lhotel/p2/10,12,2,2"


# ================================================================ улица
W, H = 80, 54
pm = CityMap(city, "primm", "Примм", W, H, start=(1, 27), seed=171, music="reno", world_pos=(2260, 650))
pm.floor_code("s", *SAND)
pm.floor_code("g", *GRAVEL)
pm.floor_code("p", *WALK)
pm.floor_code("k", *PARK)
pm.paint("s", 0, 0, W - 1, H - 1)
pm.paint("p", 0, 23, W - 1, 32)                        # тротуары вдоль трассы
pm.paint("a", 0, 25, W - 1, 30)                        # I-15
pm.paint("h", 0, 27, W - 1, 28)
pm.paint("a", 3, 4, 23, 20)                              # стоянка караванов — растрескавшийся асфальт, ровная площадка с мягкой кромкой
pm.floor_code("q", *PLAZA_ST)
pm.floor_code("u", *PARK_PAVE)
pm.floor_code("y", *ARENA_FL)
pm.paint_ragged("g", 52, 1, 78, 22, depth=2)           # земля парка аттракционов
pm.paint("q", 28, 17, 49, 22)                          # площадь перед отелем
pm.paint("q", 30, 33, 62, 35)                          # площадка перед казино
pm.paint("u", 55, 14, 76, 20)                          # променад парка
pm.paint("u", 63, 20, 66, 22)                          # проход от ворот к трассе
pm.paint("y", 57, 9, 65, 12)                           # арена с машинками
pm.exits = [(0, y) for y in range(25, 31)]
pm.reserve(0, 25, W - 1, 30)
pm.reserve(0, 23, W - 1, 32)
pm.npcs += [["deputy_baxter", 44, 32], ["pr_deputy", 50, 33], ["pr_undertaker", 22, 46], ["pr_kid", 34, 22],
            ["pr_old", 52, 21], ["pr_mechanic", 10, 41], ["pr_trader", 11, 20], ["pr_caravan_guard", 6, 21]]
for _, x, y in pm.npcs:
    pm.reserve(x, y, x, y)

# ---- север: отель «Бизон Стив» — кирпичный, с кованой вывеской «MOTEL», пальмами и площадью перед входом
pm.building(30, 5, 18, 12, "planks", south=(8,))
pm.reserve(38, 17, 39, 22)
pm.put(SIGN_MOTEL, 31, 19)
for x, y in ((28, 21), (48, 19), (35, 21), (44, 21), (36, 19), (41, 19)):
    pm.maybe(DPALMS[(x + y) % 4], x, y)
for x, y in ((34, 20), (43, 20)):
    pm.maybe(BENCH, x, y)
for x, y in ((29, 21), (47, 21)):
    pm.maybe(T50LAMP, x, y)
pm.maybe(PHONE, 28, 20)
pm.maybe(HYDRANT, 50, 22)
for x, y in ((24, 21), (52, 21)):
    pm.maybe(LAMPS[0], x, y)
pm.maybe(SIGNPOST, 26, 22)
# парковка перед отелем — 50-е годы: цветные седаны вдоль бордюра
for i, (x, y) in enumerate(((30, 22), (47, 22))):
    pm.maybe(T50CARS[i], x, y, allow_reserved=True)

# ---- северо-восток: парк аттракционов «Огненные горки» — за забором, ворота на трассу
for _x0, _x1, _y in ((54, 77, 2), (54, 77, 22)):
    pm.hwall(PARK_FENCE, _x0, _x1, _y, gaps=(63, 64, 65, 66) if _y == 22 else ())
pm.side_fence("picket", 54, 3, 21)
pm.side_fence("picket", 77, 3, 21)
# горки — главный аттракцион: длинный пролёт, короткий пролёт, петля; опоры в рост (в 2 раза крупнее)
pm.put(COASTER[1], 55, 5, check=False)
pm.put(COASTER[0], 67, 5, check=False)
pm.put(COASTER_LOOP[0], 74, 5, check=False)
# арена с машинками, окружённая бортиком
for x, y in ((57, 9), (63, 9), (58, 11), (62, 11), (60, 10), (65, 11)):
    pm.maybe(BUMPERS[(x + y) % 6], x, y)
pm.hwall(PARK_FENCE, 56, 66, 8)
pm.hwall(PARK_FENCE, 56, 66, 13)
pm.side_fence("picket", 56, 9, 12)
pm.side_fence("picket", 66, 9, 12)
# ларьки: крендели, напитки, сувениры
pm.put(PRETZEL, 69, 10)
pm.put(DRINKS, 72, 10)
pm.put(GIFTS, 69, 13)
# вход: кассы, указатели, живая изгородь, урны, скамьи
pm.put(BOOTHS[0], 61, 19)
pm.put(BOOTHS[1], 68, 19)
pm.maybe(SIGNPOST, 59, 20)
pm.maybe(TICKET, 70, 21)
pm.maybe(HEDGE, 55, 21)
pm.maybe(HEDGE, 71, 21)
for x, y in ((57, 16), (74, 16), (60, 15), (70, 15)):
    pm.maybe(PARK_BENCH[(x + y) % 2], x, y)
for x, y in ((58, 17), (72, 17), (62, 15), (66, 15), (75, 14)):
    pm.maybe((TRASH_A, TRASH_B)[(x + y) % 2], x, y)
for x, y in ((55, 14), (76, 14), (55, 3), (76, 3), (66, 17)):
    pm.maybe(T50LAMP, x, y)
pm.maybe(UMBRELLA, 74, 9)

# ---- юг: казино «Викки и Вэнс» с офисом шерифа; у входа — мешки с песком (помощник ждёт культ)
pm.building(38, 36, 18, 11, "metal", north=(6,))
pm.reserve(44, 33, 45, 36)
for x in (39, 41, 49, 51):
    pm.put(SANDBAGS, x, 34)
pm.put(LAMPS[0], 36, 33)
pm.put(LAMPS[1], 57, 33)
pm.maybe(JACKPOT_ST, 38, 34, allow_reserved=True)
for i, (x, y) in enumerate(((31, 36), (60, 36), (32, 41), (61, 41))):
    pm.maybe(T50CARS[(i + 2) % 6], x, y)
pm.props.append(["x_puddle", 59, 44])
# ---- трасса I-15: брошенные седаны в полосах (проезд свободен), фонари и скамьи на тротуарах, билборд у въезда
for i, (x, y) in enumerate(((16, 26), (36, 29), (62, 26), (74, 29), (50, 26))):
    pm.maybe(T50CARS[(i + 1) % 6], x, y, allow_reserved=True)
for x in range(6, 76, 10):
    pm.maybe(T50LAMP, x, 24, allow_reserved=True)
    pm.maybe(T50LAMP, x + 5, 31, allow_reserved=True)
for x in (12, 26, 58, 68):
    pm.maybe(PARK_BENCH[x % 2], x, 24, allow_reserved=True)
for x in (9, 21, 55, 69):
    pm.maybe(HYDRANT, x, 32, allow_reserved=True)
pm.maybe("r_billboard", 24, 34)
pm.maybe("r_billboard", 66, 20)
# ---- запад: парковка караванов — грузовики, повозки, бочки с водой
pm.put(TRUCK, 4, 6)
pm.put(BRAHMIN_CART, 12, 6)
pm.put(BRAHMIN_CART, 16, 12)
for x in (4, 5, 6):
    pm.put(WATER_BARREL, x, 15)
pm.box(CRATE, 19, 17, "ящик каравана", {"консервы": 2, "патроны": 10}, owner="pr_trader")
pm.put(STALLS[1], 10, 18)
pm.hwall([PICKET], 3, 22, 21)                            # штакетник вдоль парковки
for i, (x, y) in enumerate(((6, 9), (11, 9), (16, 9), (21, 9), (6, 17), (21, 17))):
    pm.maybe(T50CARS[(i + 3) % 6], x, y)                  # караванщики оставили машины рядами
for x, y in ((9, 14), (14, 14), (19, 14)):
    pm.maybe(CAMPFIRE_PR if (x == 14) else TIRES, x, y)
pm.maybe(T50LAMP, 3, 6)
pm.maybe(T50LAMP, 24, 6)
pm.maybe(T50LAMP, 3, 20)
pm.maybe(T50LAMP, 24, 20)
for x, y in ((8, 19), (14, 19), (18, 19)):
    pm.maybe("bench_7", x, y)
pm.maybe(SIGN_DINER, 25, 12)
# ---- юго-запад: заправка — цветные колонки, вывеска «GAS», мастерская с крышей, ржавые машины
pm.building(8, 36, 10, 7, "metal", north=(4,))
pm.put(T50_PUMPS[0], 6, 45)
pm.put(T50_PUMPS[1], 8, 45)
pm.put(T50_PUMPS[0], 10, 45)
pm.put(SIGN_DINER, 13, 44)
pm.put(WRECKS[0], 20, 38)
pm.put(WRECKS[1], 4, 41)
pm.put(T50CARS[3], 14, 47, check=False)
pm.put(TIRES, 20, 44)
pm.maybe(PHONE, 17, 45)
pm.box("r_rocks", 32, 40, "камень с крестом", {"броня «Пустынный рейнджер»": 1, "крышки": 150},
       requires={"item": "лопата", "msg": "На камне вырезан крест. Под ним рыхлая земля — без лопаты не достать."})
# ---- юго-восток: трейлерный посёлок вдоль дороги к горкам
pm.put(STALLS[0], 66, 34)
pm.put(UMBRELLA, 70, 38)
for x, y, n in ((64, 40, "r_camper"), (70, 42, "r_camper"), (74, 36, "r_camper")):
    pm.maybe(n, x, y)
pm.hwall([PICKET], 63, 77, 48)
for x, y in ((26, 33), (60, 24), (66, 31), (20, 33)):
    pm.maybe(WRECKS[(x + y) % len(WRECKS)], x, y)
for _r in ((52, 1, 78, 23), (28, 17, 49, 23), (30, 33, 62, 36)):       # парк, площадь отеля и площадка казино — без случайного мусора
    pm.reserve(*_r)
pm.scatter(["r_dry_bush", "r_rocks", "r_trash"], 1, 1, W - 2, 22, 22)
# кладбище у южной дороги: оградка, кресты, склеп-часовня
pm.hwall([PICKET], 14, 30, 47)
pm.hwall([PICKET], 14, 30, 53, gaps=(21, 22))
for i, (x, y) in enumerate(((16, 49), (19, 49), (22, 49), (25, 49), (28, 49), (16, 51), (19, 51), (25, 51), (28, 51))):
    pm.maybe("x_cross" if i % 2 else "x_grave", x, y)
pm.maybe("x_cross", 33, 46)
# свалка и мастерская за казино: каркасы машин, покрышки, бочки — сюда сваливают всё, что не продали
for i, (x, y) in enumerate(((40, 48), (46, 49), (52, 48), (58, 49))):
    pm.maybe(WRECKS[i % len(WRECKS)], x, y)
for x, y in ((43, 50), (49, 50), (55, 50)):
    pm.maybe(TIRES, x, y)
pm.hwall([PICKET], 38, 62, 52)
pm.scatter(["r_dry_bush", "r_rocks"], 1, 38, W - 2, H - 2, 10)
# случайный мусор не лежит на стоянке, в парке и на площадях — только в пустыне между местами
JUNK_NAMES = {"r_trash", "r_rocks", "r_dry_bush", "r_bones"}
_KEEP_CLEAR = ((3, 4, 23, 20), (52, 1, 78, 23), (28, 17, 49, 23), (30, 33, 62, 36))
pm.props = [e for e in pm.props if not (e[0] in JUNK_NAMES and any(a <= e[1] <= c and b <= e[2] <= d for a, b, c, d in _KEEP_CLEAR))]
pm.put("x_grave", 18, 49)
pm.put("x_cross", 21, 50)
pm.put("x_cross", 24, 49)


# ================================================================ отель «Бизон Стив»
bs = CityMap(city, "primm_bison", "Отель «Бизон Стив»", 40, 28, start=(19, 26), seed=172, interior=True, music="hotel")
bs.floor_code("F", *HOTEL_FL)
bs.floor_code("C", *CARPET)
bs.wall_code("W", "pk:lhotel/lhotel_w2_23")
bs.room(1, 12, 39, 27, "W", "F")                     # холл
bs.room(1, 1, 13, 12, "W", "C")                      # номер 1
bs.room(13, 1, 26, 12, "W", "C")                     # номер 2 — вдова Ривз
bs.room(26, 1, 39, 12, "W", "C")                     # номер 3
bs.opening(19, 27, 20, 27, "F")
pm.portal([(38, 16), (39, 16)], "primm_bison", (19, 25), "Отель «Бизон Стив»")
bs.portal([(19, 27), (20, 27)], "primm", (38, 18), "На улицу")
for x in (6, 19, 32):
    bs.opening(x, 12, x + 1, 14, "C")
# холл: стойка ресепшена лицом к входу, диваны у стен, пальмы, багажная тележка
bs.put(RECEPTION, 17, 18)
bs.put(SOFA[0], 3, 19)
bs.put(SOFA[1], 3, 23)
bs.put(SOFA[0], 35, 19)
bs.put(PALMS[0], 2, 16)
bs.put(PALMS[1], 37, 16)
bs.put(FLOOR_LAMP, 10, 16)
bs.put(LUGGAGE, 28, 16)
bs.stamp("pr_lobby_rug", RUG, 18, 22, water=False)
bs.stamp("pr_lobby_rug_b", RUG, 18, 15, water=False)
bs.stamp("pr_lobby_rug_c", RUG, 8, 21, water=False)
bs.stamp("pr_lobby_rug_d", RUG, 30, 21, water=False)
for x, y in ((8, 24), (30, 24), (14, 25), (26, 25)):
    bs.maybe(ARMCHAIR[(x + y) % 2], x, y)
for x, y in ((11, 24), (28, 22), (6, 14), (33, 14)):
    bs.maybe("pr_hotel_plant", x, y)
for x, y in ((5, 13), (14, 13), (25, 13), (34, 13), (22, 25)):
    bs.maybe(W_ART[(x + y) % 4], x, y)
bs.maybe(JUKEBOX, 34, 24)
bs.maybe("table_2", 9, 22)
bs.maybe("table_2", 31, 22)
bs.maybe(COUCH_LONG, 18, 25)
bs.npcs += [["pr_manager", 18, 17], ["pr_guest", 6, 21]]
# номер 1: семья караванщика
bs.put(BEDS[0], 3, 4)
bs.put(WARDROBE, 9, 4)
bs.put(ARMCHAIR[0], 10, 9)
# номер 2: вдова Ривз — неубранная кровать, кресло у окна, стол с письмами, детская кроватка пуста
bs.put(BEDS[1], 15, 4)
bs.put(BEDS[3], 22, 4)
bs.put(DESK, 15, 9)
bs.put(ARMCHAIR[1], 23, 9)
bs.box(WARDROBE, 19, 4, "шкаф вдовы", {"шаль с пятном": 1},
       requires={"flag": "mae_suspect", "msg": "Шкаф вдовы. Рыться в чужих вещах просто так — не по-соседски."}, owner="mae_reeves")
bs.npcs += [["mae_reeves", 18, 9]]
# номер 3: игрок-постоялец
bs.put(BEDS[2], 28, 4)
bs.put(COUCH_LONG, 34, 9)
bs.box(WARDROBE, 35, 4, "шкаф постояльца", {"крышки": 25, "самогон": 1})


# ================================================================ казино «Викки и Вэнс»
vk = CityMap(city, "primm_vikki", "Казино «Викки и Вэнс»", 42, 28, start=(16, 4), seed=173, interior=True, music="reno")
vk.floor_code("F", *CASINO_FL)
vk.floor_code("O", *WOOD)
vk.wall_code("W", "pk:jtown/jtown_w2_04")
vk.room(1, 1, 30, 27, "W", "F")                      # игровой зал и бар
vk.room(30, 1, 41, 16, "W", "O")                     # офис шерифа
vk.room(30, 16, 41, 27, "W", "O")                    # склад и лестница в подвал
vk.opening(16, 1, 17, 3, "F")
pm.portal([(44, 36), (45, 36)], "primm_vikki", (16, 4), "Казино «Викки и Вэнс»")
vk.portal([(16, 1), (17, 1)], "primm", (44, 34), "На улицу")
vk.opening(30, 8, 30, 9, "O")
vk.opening(35, 16, 36, 18, "O")
# зал: автоматы вдоль западной стены, рулетка и блэкджек в центре, бар у южной стены
for i, y in enumerate(range(5, 13)):
    vk.put(SLOTS[i % 8], 2, y)
vk.put(JACKPOT, 4, 4)
vk.put(ROULETTE, 9, 10)
vk.put(BLACKJACK, 18, 10)
vk.put(STOOL, 14, 11)
vk.maybe(ROULETTE, 22, 10)
vk.maybe(BLACKJACK, 9, 15)
vk.maybe(BLACKJACK, 15, 15)
vk.maybe(CHIPS, 13, 10)
vk.maybe(CHIPS, 21, 12)
vk.maybe(CHIPS, 17, 13)
for i, x in enumerate(range(7, 17, 2)):                    # островок автоматов спиной к спине
    vk.maybe(SLOTS[(i + 2) % 8], x, 5)
    vk.maybe(SLOTS[(i + 5) % 8], x, 6)
vk.maybe(JUKEBOX, 28, 8)
vk.maybe(JUKEBOX, 28, 20)
for x, y in ((9, 18), (20, 19), (5, 16)):                  # кадки с растениями — без них зал голый
    vk.maybe("pr_hotel_plant", x, y)
vk.stamp("pr_casino_rug_a", CASINO_RUG, 7, 8, water=False)
vk.stamp("pr_casino_rug_b", CASINO_RUG, 16, 8, water=False)
vk.stamp("pr_casino_rug_c", CASINO_RUG, 12, 17, water=False)
vk.stamp("pr_casino_rug_d", CASINO_RUG, 22, 21, water=False)
for x, y in ((14, 3), (22, 2), (4, 24), (28, 24)):
    vk.maybe(W_ART[(x + y) % 4], x, y)
vk.put(CAGE, 24, 5)
vk.put(BOTTLES, 6, 22)
vk.put(BOTTLES, 11, 22)
vk.put(BAR, 6, 24)
vk.put(BAR, 10, 24)
vk.npcs += [["barkeep_slim", 9, 23], ["pr_croupier", 11, 13], ["pr_gambler", 20, 13], ["pr_drunk", 16, 20]]
# выставка: «машина смерти» Бонни и Клайда (как в Примме из New Vegas) и музейная табличка
vk.box("r_car_red", 21, 16, "машина Бонни и Клайда", {"пистолет-пулемёт": 1, "крышки": 150, "фото Бонни Паркер": 1},
       requires={"flag": "bc_code", "msg": "Багажник на кодовом замке: три колёсика — день, месяц, год. Код знает тот, кто читал табличку."})
vk.put("x_board", 26, 17, check=False)
vk.terminals.append({"prop": len(vk.props) - 1, "id": "doc:doc_bc_placard"})
# офис шерифа: стол (здесь нашли Ривза), шкаф с делами, оружейная стойка, сейф; кровь на полу
vk.put(OFFICE_DESK, 34, 6)
vk.put(CHAIR, 36, 6)
vk.put(BOOKS, 32, 4)
vk.put(GUN_RACK, 38, 4)
vk.put(BLOOD, 35, 8)
vk.terminal(39, 10, "reeves_office")
vk.box(SAFE, 39, 13, "сейф шерифа", {"письмо культа": 1, "крышки": 60})
vk.put("x_puddle", 40, 8)                            # чёрный ход — дверь в переулок, натоптано
# склад: ящики, бочки, люк в подвал
vk.put(CRATE, 32, 20)
vk.put(CRATE, 34, 20)
vk.put(WATER_BARREL, 39, 19)
vk.props.append(["x_ladder", 36, 24])
vk.portal([(36, 24)], "primm_cellar", (4, 5), "В подвал")
vk.reserve(35, 23, 37, 25)


# ================================================================ подвал: камеры и архив
cl = CityMap(city, "primm_cellar", "Подвал «Викки и Вэнс»", 30, 20, start=(4, 5), seed=174, interior=True, music="caves")
cl.floor_code("C", *CONCRETE)
cl.wall_code("W", "pk:nbunk/nbunk_w3_17")
cl.room(1, 1, 29, 19, "W", "C")
cl.props.append(["x_ladder", 4, 4])
cl.portal([(4, 4)], "primm_vikki", (36, 23), "Наверх, в казино")
cl.reserve(2, 4, 7, 7)
# камеры вдоль южной стены: решётки, койки; в средней — «подозреваемый»
cl.hwall([CELL], 2, 28, 12, gaps=(9, 18, 25))          # решётка поперёк подвала — три камеры с дверями
for x in (6, 15, 22):
    cl.vline([CELL], x, 13, 18)                          # перегородки между камерами
cl.put(COT, 2, 17)
cl.put(COT, 10, 17)
cl.put(COT, 23, 17)
cl.npcs += [["prisoner_jonah", 19, 16]]
# архив шерифа: шкафы с делами, стол, терминал — письмо 2077 года
cl.put(BOOKS, 14, 4)
cl.put(BOOKS, 16, 4)
cl.put(BOOKS, 18, 4)
cl.put(OFFICE_DESK, 23, 7)
cl.terminal(26, 4, "reeves_archive")


# ================================================================ лагерь культа под горками
W, H = 50, 36
cp = CityMap(city, "primm_camp", "Лагерь у горок", W, H, start=(1, 18), seed=175, music="vats")
cp.floor_code("s", *SAND)
cp.floor_code("g", *GRAVEL)
cp.paint("s", 0, 0, W - 1, H - 1)
cp.paint("g", 0, 17, 20, 19)
cp.floor_code("k", "noise:pk:destown/p2/4,0,1,1")           # утоптанный гравий вокруг алтаря
cp.paint_ragged("k", 9, 8, 41, 30, depth=3)                  # обрядовая площадка: земля вытоптана кругом
cp.paint("g", 21, 17, 24, 19)                                # тропа к алтарю
city.road(pm, [(79, y) for y in range(25, 31)], cp, [(0, y) for y in range(16, 22)], "Лагерь у горок", "Примм", step=(1, 0))
cp.reserve(0, 15, 6, 22)
# старые горки над лагерем
for name, x in ((COASTER[1], 1), (COASTER[1], 13), (COASTER[0], 25), (COASTER_LOOP[0], 34)):
    cp.maybe(name, x, 6)               # одна линия горок над лагерем (в рост): без обрывков посреди песка
# шатры по кругу, алтарь в центре, фургон с решёткой — в нём держат детей
for x, y in ((14, 12), (24, 11), (34, 14), (14, 24), (34, 24)):
    cp.put(TENT_WHITE, x, y)
cp.put(ALTAR, 24, 18)
cp.put(CANDELABRA, 22, 18)
cp.put(CANDELABRA, 27, 18)
cp.put(CAMPFIRE, 24, 23)
# лагерь культа живёт: знамёна у алтаря, скамьи кругом, ковры для молитвы, бочки с водой, штабель ящиков
for x, y in ((20, 16), (28, 16)):
    cp.maybe(BANNERS_C[(x + y) % 2], x, y)
for x, y in ((21, 21), (27, 21), (21, 25), (27, 25)):
    cp.maybe("bench_7", x, y)
for x, y in ((22, 14), (26, 14), (24, 21)):
    cp.stamp(f"pr_prayer_rug{x}{y}", RUG, x, y, water=False)
for x, y in ((12, 17), (36, 20), (18, 28), (30, 28)):
    cp.maybe(WATER_BARREL, x, y)
for x, y in ((38, 12), (40, 26), (8, 22)):
    cp.maybe(CRATE, x, y)
cp.maybe(TENT_WHITE, 8, 28)
cp.hwall([BARBED_P], 8, 42, 7, gaps=(20, 21, 22))             # колючка по северной границе лагеря
cp.hwall([BARBED_P], 8, 42, 31)
cp.side_fence("wire", 8, 8, 30, gaps=(17, 18, 19))
cp.side_fence("wire", 42, 8, 30)
for x, y in ((9, 8), (41, 8), (9, 30), (41, 30)):
    cp.maybe(TORCH_PR, x, y)
cp.put(VAN, 42, 18)
cp.box(CRATE, 45, 20, "ящик с печатью круга", {"чистая вода": 2, "святая вода": 2}, owner="brother_job")
cp.npcs += [["brother_job", 25, 16], ["cult_guard_pr", 20, 20], ["cult_guard_pr_b", 30, 20], ["tobi", 43, 20],
            ["cult_sister_pr", 16, 15]]
cp.scatter(["r_dry_bush", "r_rocks", "r_bones"], 1, 1, W - 2, H - 2, 14)
# за колючкой и над горками — заброшенный парк: билборд, сухие деревья, ржавые машины, кости у ограды
for name, x, y in (("r_billboard", 4, 2), ("r_dtree_a", 12, 2), ("r_dtree_a", 30, 3), ("r_camper", 44, 3),
                   ("r_car_wreck", 3, 28), ("r_pickup", 46, 31), ("r_dtree_a", 6, 33), ("r_dumpster", 26, 33),
                   ("pile_tires", 14, 33), ("r_barrels", 40, 33), ("r_logs", 45, 12)):
    cp.maybe(name, x, y)
cp.scatter(["r_rocks", "r_bones", "r_trash", "pile_scrap"], 1, 1, W - 2, 5, 8)
cp.scatter(["r_rocks", "r_bones", "r_trash", "pile_scrap"], 1, 32, W - 2, H - 2, 8)
print("лагерь обжит:", cp.dress_empty([
    [("r_tent_beige", 0, 0), ("campfire", 2, 2), ("r_logs", 4, 2), ("sack", 0, 2)],
    [("crate", 0, 0), ("crate", 1, 0), ("barrel_wood", 3, 0), ("sack", 0, 2), ("bucket", 2, 2)],
    [("r_tent_low", 0, 0), ("r_trash", 3, 1), ("pile_cans", 0, 2)],
    [("x_cross", 0, 0), ("x_grave", 0, 1), ("x_cross", 2, 0), ("x_grave", 2, 1), ("r_dtree_a", 4, 0)],
    [("r_awning", 0, 0), ("crate", 0, 2), ("barrel_wood", 3, 2)],
], block=6, margin=1, chance=0.9))


# пустыри обживаются сценками (экскурсия по городам показала голый песок)
print("обжито:", pm.dress_empty([
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

# подвал казино: склад выпивки и реквизита, ящики с фишками, бочки, битые бутылки
cl.scatter(["crate", "crate_b", "barrel_wood", "pile_bottles", "crate_broken", "sack", "pile_cans", "pile_rags"], 3, 3, 28, 18, 18)
entry_door(city, vk, 16)
city.save()
L = json.load(open("data/locations.json", encoding="utf-8"))
L["primm"].update({"world_name": "Примм", "discover": True})
L["primm_camp"]["clear_flag"] = "primm_camp_cleared"     # лагерь культа разогнан — Тоби можно увести
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
