"""
Зайзикс — курорт «целебных источников» у солёного озера Сода (реальное место: Zzyzx Mineral Springs
Кёртиса Спрингера, 1944 год, — жульничество с «чудо-водой»). Сценарий — docs/story.md, раздел 8.

  zzyzx          «Зайзикс: Бульвар Мечты» (70×50): въезд по старой дороге с запада, мощёный бульвар
                 с пальмами к озеру Туэнде (оазис с лодками), купальни и «Замок» Спрингера к северу,
                 лагерь паломников и рынок к югу, глинобитные дома целителей, колодец.
  zzyzx_bath     купальни (интерьер): приёмная, раздевалки, зал с целебным бассейном, кабинет
                 целителя (терминал), насосная (люк вниз — по ключу смотрителя Гаса).
  zzyzx_hotel    «Замок» Спрингера (интерьер): холл, столовая, гостевые номера, покои Спрингера.
  zzyzx_cistern  цистерна под купальнями: каналы с водой, фильтр Vault-Tec «Чистый лист», терминал.

Наборы: desert-town (destown), desert-natural-environment (desnat), backrooms-poolcore (pool),
modern-hotel (hotel), nuclear-bunker-interior (nbunk), wasteland-laboratory (wlab).
Запуск из папки game_project:  .venv/bin/python tools/build_zzyzx.py
"""
import json

from citykit import City, CityMap

city = City("zzyzx", "Зайзикс")


def P(name, img, **kw):
    city.prop(name, img, **kw)
    return name


def cells(page, pts):
    return [f"pk:{page}/{x},{y},1,1" for x, y in pts]


# ------------------------------------------------------------ объекты
PALMS = [P(f"zz_palm{i}", f"pk:desnat/desnat_4_{n:03d}", foot=[1, 1]) for i, n in enumerate((49, 50, 51, 52))]
BUSHES = [P(f"zz_bush{i}", f"pk:desnat/desnat_4_{n:03d}", block=False) for i, n in enumerate((20, 21, 24, 46, 47, 48))]
CACTI = [P(f"zz_cactus{i}", f"pk:destown/destown_1_{n:03d}", foot=[1, 1]) for i, n in enumerate((0, 2, 5, 28, 39, 66))]
DEAD = [P(f"zz_deadtree{i}", f"pk:destown/destown_1_{n:03d}", foot=[1, 1]) for i, n in enumerate((8, 9, 43, 96))]
ROCKS = [P(f"zz_rock{i}", f"pk:destown/destown_2_{n:03d}") for i, n in enumerate((46, 47, 60, 67))]
HOUSE_A = P("zz_adobe_a", "pk:destown/destown_3_000", foot=[3, 2], sight=True)
HOUSE_B = P("zz_adobe_b", "pk:destown/destown_3_002", foot=[3, 2], sight=True)
HOUSE_C = P("zz_adobe_c", "pk:destown/destown_3_003", foot=[4, 2], sight=True)
HOUSE_BIG = P("zz_adobe_big", "pk:destown/destown_3_014", foot=[4, 2], sight=True)
TENT_BIG = P("zz_tent_big", "pk:destown/destown_3_004", foot=[3, 2], sight=True)
TENT_AWN = P("zz_tent_awning", "pk:destown/destown_3_011", foot=[4, 2], sight=True)
TENT = P("zz_tent", "pk:destown/destown_3_015", foot=[2, 2], sight=True)
TENT_S = P("zz_tent_small", "pk:destown/destown_3_018", foot=[2, 1])
STALL = P("zz_stall", "pk:destown/destown_3_029", foot=[2, 1])
STALL_B = P("zz_stall_b", "pk:destown/destown_3_032", foot=[2, 1])
RUG = P("zz_rug", "pk:destown/destown_3_008", block=False, layer="floor")
WELL = P("zz_well", "pk:desnat/desnat_3_006", foot=[2, 1])
WELL_B = P("zz_well_b", "pk:desnat/desnat_3_027", foot=[2, 1])
POTS = [P(f"zz_pot{i}", f"pk:desnat/desnat_3_{n:03d}", search="shelf", title="кувшин") for i, n in enumerate((16, 41, 59, 85))]
CRATE = P("zz_crate", "pk:desnat/desnat_3_018", search="crate", title="ящик")
BARREL = P("zz_barrel", "pk:desnat/desnat_3_014", search="junk", title="бочка")
FIRE = P("zz_campfire", "pk:destown/destown_3_034", block=False, layer="floor")
LAKE = "pk:destown/p5/8,5,8,11"

BED = P("ht_bed", "pk:hotel/hotel_1_007", foot=[2, 2])
BED_S = P("ht_bed_single", "pk:hotel/hotel_1_004", foot=[1, 2])
NIGHT = P("ht_nightstand", "pk:hotel/hotel_1_000", search="drawer", title="тумбочка")
WARDROBE = P("ht_wardrobe", "pk:hotel/hotel_1_084", foot=[2, 1], sight=True, search="cloth", title="шкаф")
DESK = P("ht_desk", "pk:hotel/hotel_1_086", foot=[2, 1])
DESK_B = P("ht_desk_b", "pk:hotel/hotel_1_079", foot=[2, 1])
ARMCHAIR = P("ht_armchair", "pk:hotel/hotel_1_092")
LAMP = P("ht_lamp", "pk:hotel/hotel_1_102")
SINK = P("ht_sink", "pk:hotel/hotel_1_095")
TOILET = P("ht_toilet", "pk:hotel/hotel_1_096")
PLANT = P("ht_plant", "pk:hotel/hotel_1_127")
LOCKERS = P("zz_lockers", "pk:wschool/p1/6,12,2,2", foot=[2, 1], sight=True)
TANK = P("zz_tank", "pk:wlab/wlab_1_008", sight=True)
VATS = P("zz_vats", "pk:wlab/wlab_1_002", sight=True)
DESK_LAB = P("zz_desk_lab", "pk:wlab/wlab_1_012")
GEN = P("zz_generator", "pk:nbunk/nbunk_2_028")
TANKS_W = P("zz_water_tanks", "pk:nbunk/nbunk_2_021", sight=True)

SAND = cells("destown/p2", [(0, 0), (1, 0), (0, 1), (1, 1)])
CRACK = cells("destown/p2", [(8, 0), (9, 0), (8, 1), (9, 1)])
COBBLE = cells("destown/p2", [(4, 0), (5, 0), (4, 1), (5, 1)])   # утоптанный гравий бульвара
TILE_W = ["pk:hotel/hotel_f1_12", "pk:hotel/hotel_f1_11"]
TILE_B = ["pk:hotel/hotel_f1_18"]
WOOD = ["pk:hotel/hotel_f1_02"]
CARPET = ["pk:hotel/hotel_f1_03"]
METAL = cells("nbunk/p2", [(4, 8), (5, 9), (6, 10), (4, 10)])
POOL_WATER = "pk:pool/p1/4,4,4,2"
DIRTY_WATER = "pk:pool/p1/4,8,4,4"


# ================================================================ Бульвар Мечты
W, H = 70, 50
z = CityMap(city, "zzyzx", "Зайзикс: Бульвар Мечты", W, H, start=(2, 25), seed=81, music="desert",
            world_pos=(1880, 1140))
z.floor_code("s", *SAND)
z.floor_code("k", *CRACK)
z.floor_code("p", *COBBLE)
z.paint("s", 0, 0, W - 1, H - 1)
z.tint = None
z.exits = [(0, y) for y in range(24, 28)]
z.paint("a", 0, 24, 10, 27)                          # старая дорога с запада
z.paint("p", 11, 24, 60, 27)                         # Бульвар Мечты — к озеру
z.paint("p", 20, 18, 22, 23)                         # к купальням
z.paint("p", 57, 19, 59, 23)                         # к «Замку»
z.paint("p", 30, 28, 32, 31)                         # к лагерю
z.paint("k", 6, 32, 36, 46)                          # вытоптанная земля лагеря
z.reserve(0, 23, 60, 28)
z.reserve(19, 17, 23, 23)
z.reserve(56, 18, 60, 23)
z.reserve(29, 28, 33, 32)

z.npcs += [["springer", 32, 21], ["gus", 47, 30], ["pilgrim_hank", 15, 36],
           ["pilgrim_maria", 24, 38], ["pilgrim_timmy", 26, 39], ["healer_girl", 50, 37], ["merchant_zz", 13, 31]]
for _, x, y in z.npcs:
    z.reserve(x, y, x, y)

# озеро Туэнде — восточнее конца бульвара, вода непроходима
z.stamp("zz_lake", LAKE, 61, 21, water=True)
# пальмы вдоль бульвара — через одну клетку, с обеих сторон
for i, x in enumerate(range(13, 52, 4)):      # через каждые 4 клетки, кроме мест, где отходят дорожки
    if not 19 <= x <= 23 and not 56 <= x <= 60:
        z.put(PALMS[i % 4], x, 22)
    if not 29 <= x + 2 <= 33:
        z.put(PALMS[(i + 1) % 4], x + 2, 29)

# купальни (север, у начала бульвара): здание с крышей, вход с юга
z.building(14, 8, 14, 10, "concrete", south=(6,), sign="КУПАЛЬНИ")
z.portal([(20, 17), (21, 17)], "zzyzx_bath", (19, 23), "Купальни")
# «Замок» Спрингера (северо-восток): большое кирпичное здание
z.building(50, 6, 16, 13, "brick", south=(6,), sign="ЗАМОК")
z.portal([(56, 18), (57, 18)], "zzyzx_hotel", (21, 23), "«Замок» Спрингера")
# у купален — колодец и скамьи для ждущих
z.put(WELL, 30, 19)
z.put("bench_7", 25, 21)
z.put("bench_16", 35, 21)

# лагерь паломников (юго-запад): шатры по кругу у кострищ, коврики, кувшины
for name, x, y in ((TENT_BIG, 8, 33), (TENT_AWN, 14, 33), (TENT, 22, 33), (TENT_S, 9, 40), (TENT, 16, 42),
                   (TENT_BIG, 26, 43), (TENT_S, 33, 40)):
    z.put(name, x, y)
z.put(FIRE, 19, 38)
z.put(FIRE, 29, 37)
z.put(RUG, 12, 38)
z.put(RUG, 21, 40)
for i, (x, y) in enumerate(((7, 37), (31, 34), (11, 45), (35, 44))):
    z.put(POTS[i % 4], x, y)

# рынок у дороги: прилавки вдоль бульвара
for name, x in ((STALL, 8), (STALL_B, 12), (STALL, 16)):
    z.put(name, x, 30)
z.box(CRATE, 6, 30, "ящик торговца", {"чистая вода": 2, "консервы": 2, "вяленое мясо": 1}, owner="merchant_zz")

# дома целителей (юго-восток) — глинобитные, в ряд вдоль улочки
for name, x in ((HOUSE_A, 40), (HOUSE_B, 45), (HOUSE_C, 50), (HOUSE_BIG, 56)):
    z.put(name, x, 33)
z.put(WELL_B, 47, 40)
z.box(BARREL, 43, 41, "бочка с «чудо-водой»", {"вода Зайзикса": 3}, owner="springer")
z.put(POTS[1], 61, 41)

# пустыня вокруг
z.scatter(CACTI + DEAD, 1, 1, W - 2, 6, 10)
z.scatter(CACTI + ROCKS, 1, 46, W - 2, H - 2, 8)
z.scatter(BUSHES, 1, 1, W - 2, H - 2, 26)
z.scatter(ROCKS + DEAD, 36, 30, W - 2, H - 2, 6)
z.enemies += [["rat", 66, 46], ["rat", 64, 47], ["radroach", 3, 47]]


# ================================================================ купальни
bt = CityMap(city, "zzyzx_bath", "Купальни Зайзикса", 40, 26, start=(19, 23), seed=82, interior=True, music="caves")
bt.floor_code("T", *TILE_W)
bt.floor_code("B", *TILE_B)
bt.wall_code("W", "pk:hotel/hotel_w1_13")
bt.wall_code("Q", "pk:hotel/hotel_w1_11")
LOBBY = bt.room(10, 15, 29, 25, "W", "T")          # приёмная у входа
CHANGE_L = bt.room(1, 15, 10, 25, "W", "T")         # мужская раздевалка
CHANGE_R = bt.room(29, 15, 38, 25, "W", "T")        # женская раздевалка
HALL = bt.room(1, 1, 30, 15, "Q", "B")             # зал с бассейном
OFFICE = bt.room(30, 1, 38, 8, "W", "T")            # кабинет целителя
PUMP = bt.room(30, 8, 38, 15, "W", "T")             # насосная
bt.opening(19, 25, 20, 25, "T")
bt.portal([(19, 25), (20, 25)], "zzyzx", (20, 18), "На бульвар")
bt.opening(10, 19, 10, 20, "T")
bt.opening(29, 19, 29, 20, "T")
bt.opening(19, 15, 20, 17, "B")
bt.opening(30, 5, 30, 6, "T")
bt.opening(34, 8, 35, 10, "T")
# приёмная: стойка лицом к двери, скамьи для ждущих вдоль стен, растения в углах
bt.put("counter", 17, 19)
bt.put("counter", 21, 19)
bt.put("bench_7", 12, 22)
bt.put("bench_7", 25, 22)
bt.put(PLANT, 12, 18)
bt.put(PLANT, 27, 18)
# раздевалки: шкафчики вдоль северной стены, скамья посредине
for x in (2, 6):
    bt.put(LOCKERS, x, 18)
bt.put("bench_16", 4, 22)
for x in (30, 35):
    bt.put(LOCKERS, x, 18)
bt.put("bench_16", 32, 22)
bt.box("locker_1", 8, 23, "шкафчик паломника", {"крышки": 12, "бинт": 1})
# зал: целебный бассейн в центре, по краям — лежаки (скамьи)
bt.stamp("zz_pool_a", POOL_WATER, 9, 6, water=True)
bt.stamp("zz_pool_b", POOL_WATER, 13, 6, water=True)
bt.stamp("zz_pool_c", POOL_WATER, 9, 8, water=True)
bt.stamp("zz_pool_d", POOL_WATER, 13, 8, water=True)
bt.put("bench_16", 4, 7)
bt.put("bench_16", 22, 7)
bt.put("bench_16", 4, 11)
bt.put("bench_16", 22, 11)
bt.put(PLANT, 2, 4)
bt.put(PLANT, 28, 4)
# кабинет целителя: стол с терминалом у стены, шкаф с «лекарствами»
bt.terminal(31, 4, "zz_healer")
bt.put(DESK_B, 34, 4)
bt.box("glass_cabinet", 37, 4, "шкаф целителя", {"вода Зайзикса": 2, "антирадин": 1, "крышки": 40})
# насосная: насосы и бак, люк в цистерну
bt.put(TANKS_W, 36, 11)
bt.put(GEN, 31, 13)
bt.props.append(["x_manhole", 34, 12])
bt.portal([(34, 12)], "zzyzx_cistern", (4, 5), "Цистерна",
          requires={"item": "ключ от насосной",
                    "msg": "Люк в полу насосной, на нём замок. Ключ — у смотрителя источника Гаса."})
bt.npcs += [["bath_pilgrim", 6, 10], ["bath_pilgrim_b", 25, 10], ["nurse_ava", 17, 18]]   # Ава — за стойкой


# ================================================================ «Замок» Спрингера
ht = CityMap(city, "zzyzx_hotel", "«Замок» Спрингера", 44, 26, start=(21, 23), seed=83, interior=True, music="hub")
ht.floor_code("C", *CARPET)
ht.floor_code("D", *WOOD)
ht.wall_code("V", "pk:hotel/hotel_w1_23")
ht.wall_code("Y", "pk:hotel/hotel_w1_15")
LOBBY = ht.room(12, 13, 31, 25, "V", "C")          # холл
DINE = ht.room(1, 13, 12, 25, "V", "D")             # столовая
SUITE = ht.room(31, 13, 43, 25, "V", "C")           # покои Спрингера
ROOMS = [ht.room(x, 1, x + 8, 13, "Y", "D") for x in (1, 9, 17, 25, 33)]
ht.opening(21, 25, 22, 25, "C")
ht.portal([(21, 25), (22, 25)], "zzyzx", (57, 19), "На бульвар")
ht.opening(12, 19, 12, 20, "C")
ht.opening(31, 19, 31, 20, "C")
for x0 in (1, 9, 17, 25, 33):
    ht.opening(x0 + 4, 13, x0 + 4, 15, "C")
# холл: стойка портье, кресла у стен, растения
ht.put("counter", 18, 17)
ht.put("counter", 22, 17)
ht.put(ARMCHAIR, 14, 20)
ht.put(ARMCHAIR, 28, 20)
ht.put(PLANT, 15, 16)
ht.put(PLANT, 27, 16)
ht.put(LAMP, 15, 23)
ht.put(LAMP, 28, 23)
# столовая: столы со стульями рядами
for x, y in ((3, 17), (7, 17), (3, 21), (7, 21)):
    ht.put("round_table_42", x, y)
    ht.put("stool_round_41", x + 1, y)
ht.box("cabinet_small", 10, 16, "буфет", {"консервы": 2, "энергетический батончик": 1})
# номера: кровать у стены, тумбочка, шкаф; в одном — постоялец
for i, x0 in enumerate((1, 9, 17, 25, 33)):
    ht.put(BED if i % 2 == 0 else BED_S, x0 + 2, 4)
    ht.put(NIGHT, x0 + 1, 4)
    ht.put(WARDROBE, x0 + 6, 4)
ht.npcs += [["guest_widow", 22, 8]]
# покои Спрингера: широкая кровать, письменный стол с терминалом, сейф
ht.put(BED, 39, 17)
ht.put(NIGHT, 41, 17)
ht.terminal(33, 17, "zz_springer")
ht.put(DESK, 34, 17)
ht.box("metal_chest", 41, 22, "сейф Спрингера",
       {"крышки": 220, "стимулятор": 2, "ключ от насосной": 1},
       requires={"flag": "springer_safe", "msg": "Сейф с кодом. Код Спрингер держит в голове — или в терминале."})
ht.put(PLANT, 32, 23)


# ================================================================ цистерна
cs = CityMap(city, "zzyzx_cistern", "Цистерна под купальнями", 34, 22, start=(4, 5), seed=84, interior=True,
             music="lab")
cs.floor_code("M", *METAL)
cs.wall_code("K", "pk:nbunk/nbunk_w1_12")
cs.room(1, 1, 33, 21, "K", "M")
cs.props.append(["x_ladder", 4, 4])
cs.portal([(4, 4)], "zzyzx_bath", (34, 13), "Наверх, в насосную")
cs.reserve(2, 4, 7, 7)
# каналы с водой: две полосы воды через зал, между ними — мостки
cs.stamp("zz_canal_a", DIRTY_WATER, 10, 6, water=True)
cs.stamp("zz_canal_b", DIRTY_WATER, 14, 6, water=True)
cs.stamp("zz_canal_c", DIRTY_WATER, 10, 14, water=True)
cs.stamp("zz_canal_d", DIRTY_WATER, 14, 14, water=True)
# фильтр «Чистый лист»: баки и чаны у восточной стены, терминал управления рядом
cs.put(TANK, 26, 4)
cs.put(TANK, 28, 4)
cs.put(VATS, 30, 4)
cs.terminal(24, 4, "zz_cistern")
cs.put(DESK_LAB, 26, 9)
cs.put(GEN, 29, 12)
cs.box(CRATE, 31, 18, "ящик Vault-Tec", {"антирадин": 2, "образец «Чистый лист»": 1, "батарейки": 2})
cs.enemies += [["radroach", 12, 11], ["radroach", 16, 12], ["radroach", 20, 18], ["rat", 7, 17], ["rat", 6, 19],
               ["robot_skel", 27, 16]]

city.save(gap_exempt=("springer", "nurse_ava", "gus", "bath_pilgrim", "bath_pilgrim_b"))
# на карте мира — «Зайзикс»; открывается, если пройти рядом, или после Бейкера (src/game/quests.py)
L = json.load(open("data/locations.json", encoding="utf-8"))
L["zzyzx"].update({"world_name": "Зайзикс", "discover": True})
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
