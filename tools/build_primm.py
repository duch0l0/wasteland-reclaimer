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

city = City("primm", "Примм")


def P(name, img, **kw):
    city.prop(name, img, **kw)
    return name


def cells(page, pts):
    return [f"pk:{page}/{x},{y},1,1" for x, y in pts]


# ------------------------------------------------------------ улица
COASTER = [P("pr_coaster", "pk:apark/apark_2_121", foot=[4, 1], sight=True),
           P("pr_coaster_long", "pk:apark/apark_2_133", foot=[6, 1], sight=True)]
COASTER_LOOP = [P("pr_coaster_loop", "pk:apark/apark_2_120", foot=[2, 1], sight=True),
                P("pr_coaster_ring", "pk:apark/apark_2_131", foot=[2, 1], sight=True)]
BOOTHS = [P(f"pr_booth{i}", f"pk:apark/apark_2_{n:03d}") for i, n in enumerate((100, 101, 102))]
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
JACKPOT = P("pr_neon_jackpot", "pk:casino/casino_1_051", block=False,
            light={"r": 90, "color": [255, 200, 90], "at": [0.5, 0.5], "flicker": 0.1})
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
CANDELABRA = P("pr_candelabra", "pk:cult/cult_2_068", block=False,
               light={"r": 90, "color": [255, 170, 80], "at": [0.5, 0.3], "flicker": 0.5})
CAMPFIRE = P("pr_campfire", "pk:ucamp/ucamp_2_040", foot=[2, 1],
             light={"r": 120, "color": [255, 150, 70], "at": [0.5, 0.5], "flicker": 0.35})

SAND = cells("destown/p2", [(0, 0), (1, 0), (0, 1), (1, 1)])
GRAVEL = cells("destown/p2", [(4, 0), (5, 0), (4, 1), (5, 1)])
WALK = ["pk:zcity/zcity_f1_22"]
PARK = ["pk:wpark/p1/1,9,1,1"]
PARK_PATCH = "pk:wpark/p1/4,9,4,3"
HOTEL_FL = ["pk:store/p1/12,0,1,1"]
CARPET = ["pk:aoffice/p3/3,1,1,1"]
CASINO_FL = ["pk:store/p1/2,8,1,1"]
WOOD = ["pk:zcity/zcity_f1_00"]
CONCRETE = cells("nbunk/p2", [(0, 8), (1, 9)])
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
pm.paint("k", 3, 4, 22, 20)                            # парковка караванов
pm.paint("p", 30, 19, 33, 22)                          # дорожка к отелю
pm.paint("p", 44, 33, 47, 36)                          # дорожка к казино
pm.exits = [(0, y) for y in range(25, 31)]
pm.reserve(0, 25, W - 1, 30)

# север: отель «Бизон Стив» — большой, с крышей; у входа пальмы, скамьи
pm.building(26, 3, 26, 16, "brick", south=(6,))
pm.reserve(32, 19, 33, 22)
pm.put(BENCH, 28, 21)
pm.put(BENCH, 36, 21)
pm.put(LAMPS[0], 26, 22)
pm.put(LAMPS[1], 51, 22)
pm.put(SIGNPOST, 40, 21)
# американские горки — над восточной частью города: опоры и рельсы змейкой
pm.put(COASTER[1], 56, 5)
pm.put(COASTER[0], 62, 8)
pm.put(COASTER_LOOP[0], 68, 5)
pm.put(COASTER[1], 66, 12)
pm.put(COASTER_LOOP[1], 72, 15)
pm.put(COASTER[0], 56, 15)
pm.put(TICKET, 58, 20)
pm.put(BOOTHS[0], 63, 20)
# юг: казино «Викки и Вэнс» с офисом шерифа; у входа — мешки с песком (помощник ждёт культ)
pm.building(36, 36, 22, 14, "concrete", north=(8,))
pm.reserve(44, 33, 45, 36)
for x in (39, 41, 49, 51):
    pm.put(SANDBAGS, x, 34)
pm.put(LAMPS[0], 36, 33)
pm.put(LAMPS[1], 57, 33)
# переулок за казино — чёрный ход офиса шерифа (запертая дверь, следы)
pm.props.append(["x_puddle", 59, 44])
# запад: парковка караванов — грузовики, повозки, бочки с водой
pm.stamp("pr_park_patch", PARK_PATCH, 8, 8, water=False)
pm.put(TRUCK, 4, 6)
pm.put(BRAHMIN_CART, 12, 6)
pm.put(BRAHMIN_CART, 16, 12)
for x in (4, 5, 6):
    pm.put(WATER_BARREL, x, 15)
pm.box(CRATE, 19, 17, "ящик каравана", {"консервы": 2, "патроны": 10}, owner="pr_trader")
pm.put(STALLS[1], 10, 18)
pm.npcs += [["pr_trader", 11, 20], ["pr_caravan_guard", 6, 21]]
# юго-запад: заправка — колонки, ржавые машины
pm.put(GAS_PUMP, 8, 38)
pm.put(GAS_PUMP, 12, 38)
pm.put(WRECKS[0], 6, 42)
pm.put(WRECKS[1], 14, 44)
pm.put(TIRES, 20, 40)
pm.box("r_rocks", 32, 38, "камень с крестом", {"броня «Пустынный рейнджер»": 1, "крышки": 150},
       requires={"item": "лопата", "msg": "На камне вырезан крест. Под ним рыхлая земля — без лопаты не достать."})
# восток: ворота к лагерю культа под горками
pm.put(STALLS[0], 66, 34)
pm.put(UMBRELLA, 70, 38)
for x, y in ((26, 33), (60, 24), (66, 31), (20, 33)):
    pm.put(WRECKS[(x + y) % len(WRECKS)], x, y)

pm.npcs += [["deputy_baxter", 44, 32], ["pr_deputy", 50, 33], ["pr_undertaker", 22, 46], ["pr_kid", 34, 22],
            ["pr_old", 54, 21], ["pr_mechanic", 10, 41]]
for _, x, y in pm.npcs:
    pm.reserve(x, y, x, y)
pm.scatter(["r_dry_bush", "r_rocks", "r_trash"], 1, 1, W - 2, 22, 10)
pm.scatter(["r_dry_bush", "r_rocks", "r_trash"], 1, 33, W - 2, H - 2, 12)
pm.put("x_grave", 18, 49)
pm.put("x_cross", 21, 50)
pm.put("x_cross", 24, 49)


# ================================================================ отель «Бизон Стив»
bs = CityMap(city, "primm_bison", "Отель «Бизон Стив»", 40, 28, start=(19, 26), seed=172, interior=True, music="hub")
bs.floor_code("F", *HOTEL_FL)
bs.floor_code("C", *CARPET)
bs.wall_code("W", "pk:lhotel/lhotel_w2_23")
bs.room(1, 12, 39, 27, "W", "F")                     # холл
bs.room(1, 1, 13, 12, "W", "C")                      # номер 1
bs.room(13, 1, 26, 12, "W", "C")                     # номер 2 — вдова Ривз
bs.room(26, 1, 39, 12, "W", "C")                     # номер 3
bs.opening(19, 27, 20, 27, "F")
pm.portal([(32, 18), (33, 18)], "primm_bison", (19, 25), "Отель «Бизон Стив»")
bs.portal([(19, 27), (20, 27)], "primm", (32, 20), "На улицу")
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
vk.put(CAGE, 24, 5)
vk.put(BOTTLES, 6, 22)
vk.put(BOTTLES, 11, 22)
vk.put(BAR, 6, 24)
vk.put(BAR, 10, 24)
vk.npcs += [["barkeep_slim", 9, 23], ["pr_croupier", 11, 13], ["pr_gambler", 20, 13], ["pr_drunk", 16, 20]]
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
city.road(pm, [(79, y) for y in range(25, 31)], cp, [(0, y) for y in range(16, 22)], "Лагерь у горок", "Примм", step=(1, 0))
cp.reserve(0, 15, 6, 22)
# старые горки над лагерем
cp.put(COASTER[1], 4, 3)
cp.put(COASTER[1], 12, 6)
cp.put(COASTER_LOOP[0], 20, 3)
cp.put(COASTER[0], 28, 4)
cp.put(COASTER_LOOP[1], 36, 7)
cp.put(COASTER[1], 40, 28)
# шатры по кругу, алтарь в центре, фургон с решёткой — в нём держат детей
for x, y in ((14, 12), (24, 11), (34, 14), (14, 24), (34, 24)):
    cp.put(TENT_WHITE, x, y)
cp.put(ALTAR, 24, 18)
cp.put(CANDELABRA, 22, 18)
cp.put(CANDELABRA, 27, 18)
cp.put(CAMPFIRE, 24, 23)
cp.put(VAN, 42, 18)
cp.box(CRATE, 45, 20, "ящик с печатью круга", {"чистая вода": 2, "святая вода": 2}, owner="brother_job")
cp.npcs += [["brother_job", 25, 16], ["cult_guard_pr", 20, 20], ["cult_guard_pr_b", 30, 20], ["tobi", 43, 20],
            ["cult_sister_pr", 16, 15]]
cp.scatter(["r_dry_bush", "r_rocks", "r_bones"], 1, 1, W - 2, H - 2, 14)

city.save()
L = json.load(open("data/locations.json", encoding="utf-8"))
L["primm"].update({"world_name": "Примм", "discover": True})
L["primm_camp"]["clear_flag"] = "primm_camp_cleared"     # лагерь культа разогнан — Тоби можно увести
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
