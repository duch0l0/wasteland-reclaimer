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
from vaultkit import Lamps

city = City("zzyzx", "Зайзикс")
LM = Lamps(city)


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
STALL = P("zz_stall", "pk:destown/p3/4,8,2,2", foot=[2, 1], keybg=True)
STALL_B = P("zz_stall_b", "pk:destown/p3/0,8,2,2", foot=[2, 1], keybg=True)
RUG = P("zz_rug", "pk:destown/destown_3_008", block=False, layer="floor")
WELL = P("zz_well", "pk:desnat/desnat_3_006", foot=[2, 1])
WELL_B = P("zz_well_b", "pk:desnat/desnat_3_027", foot=[2, 1])
POTS = [P(f"zz_pot{i}", f"pk:desnat/desnat_3_{n:03d}", search="shelf", title="кувшин") for i, n in enumerate((16, 41, 59, 85))]
CRATE = P("zz_crate", "pk:desnat/desnat_3_018", search="crate", title="ящик")
BARREL = P("zz_barrel", "pk:desnat/desnat_3_014", search="junk", title="бочка")
FIRE = P("zz_campfire", "pk:destown/destown_3_034", block=False, layer="floor")
LAKE = "pk:destown/p5/8,5,8,11"
ADOBE_WALL = [P(f"zz_wall{i}", f"pk:destown/p3/{x},8,2,1", foot=[2, 1], keybg=True) for i, x in enumerate((6, 8, 10, 12))]
ADOBE_GATE = P("zz_gate_arch", "pk:destown/p3/12,10,4,2", foot=[4, 1], sight=True, keybg=True)     # арка: проход 2 клетки посередине
RUG_R = P("zz_rug_red", "pk:destown/p3/2,11,2,1", block=False, layer="floor", keybg=True)
RUG_B = P("zz_rug_blue", "pk:destown/p3/4,11,2,1", block=False, layer="floor", keybg=True)
SACKS = [P(f"zz_sack{i}", f"pk:destown/p3/{x},8,1,1", search="crate", title="мешок") for i, x in enumerate((2, 3))]
SKIN = [P(f"zz_skin{i}", f"pk:destown/p3/{x},11,1,1", block=False, layer="floor", keybg=True) for i, x in enumerate((5, 6))]
REEDS = [P(f"zz_reeds{i}", f"pk:desnat/p4/{x},{y},1,1", block=False, keybg=True) for i, (x, y) in enumerate(((8, 10), (9, 10), (7, 12), (9, 12)))]
LANTERN_ZZ = P("zz_lantern", "pk:destown/p4/14,4,1,1", block=False, keybg=True, light={"r": 110, "color": [255, 190, 110], "at": [0.5, 0.4], "flicker": 0.25})

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

SAND = ["pk:desnat/p1/0,0,1,1", "pk:desnat/p1/1,0,1,1", "pk:desnat/p1/0,1,1,1"]   # песок под цвет окружающей пустыни, без скачка
CRACK = ["noise:pk:destown/p2/8,0,1,1"]
COBBLE = cells("destown/p2", [(4, 0), (5, 0), (4, 1), (5, 1)])   # утоптанный гравий бульвара
TILE_W = ["pk:zcity/zcity_f1_23"]
TILE_B = ["pk:zcity/zcity_f1_22"]
WOOD = ["pk:hotel/hotel_f1_02"]
CARPET = ["pk:hotel/hotel_f1_03"]
METAL = cells("nbunk/p2", [(4, 8), (5, 9), (6, 10), (4, 10)])
POOL_WATER = "pk:pool/p1/4,4,4,2"
DIRTY_WATER = "pk:pool/p1/4,8,4,4"
SEWER_PIPE_ZZ = P("zz_pipes", "pk:sewer/sewer_1_042", foot=[2, 1])


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
z.paint("p", 0, 24, 10, 27)                          # въезд с запада — тот же утоптанный гравий, что и бульвар
z.paint("p", 11, 24, 60, 27)                         # Бульвар Мечты — к озеру
z.paint("p", 20, 18, 21, 23)                         # к купальням — проход арки
z.paint("p", 56, 19, 57, 23)                         # к «Замку» — проход арки
z.paint("p", 30, 28, 31, 32)                         # к лагерю — проход арки
z.paint_ragged("k", 5, 31, 37, 47)                        # вытоптанная земля лагеря
z.reserve(0, 23, 60, 28)
z.reserve(18, 17, 23, 23)
z.reserve(55, 18, 59, 23)
z.reserve(28, 28, 33, 32)
z.reserve(44, 28, 49, 32)

z.npcs += [["springer", 32, 21], ["gus", 47, 30], ["pilgrim_hank", 15, 36],
           ["pilgrim_maria", 24, 38], ["pilgrim_timmy", 26, 39], ["healer_girl", 50, 37], ["merchant_zz", 13, 31]]
for _, x, y in z.npcs:
    z.reserve(x, y, x, y)

# озеро Туэнде — восточнее конца бульвара, вода непроходима
z._palm = "zz_palm0"
# водоём — обычная вода карты: берег, мелководье и пена рисуются сами (src/townmap.py _shore)
z.floor_code("~", *["pk:mport/p1/8,4,1,1", "pk:mport/p1/9,4,1,1", "pk:mport/p1/10,4,1,1", "pk:mport/p1/11,4,1,1"])
z.water_codes = tuple(set(getattr(z, "water_codes", ())) | {"~"})
import math as _m, random as _r
_rr = _r.Random(11)
_k = [_rr.uniform(0, 6.3) for _ in range(3)]
for _y in range(26 - 5 - 2, 26 + 5 + 3):
    for _x in range(64 - 4 - 2, 64 + 4 + 3):
        _a = _m.atan2((_y - 26) / 5, (_x - 64) / 4)
        _wob = 1 + 0.12 * _m.sin(2 * _a + _k[0]) + 0.08 * _m.sin(3 * _a + _k[1]) + 0.05 * _m.sin(5 * _a + _k[2])
        if ((_x - 64) / 4) ** 2 + ((_y - 26) / 5) ** 2 <= _wob ** 2:
            z.ground[_y][_x] = "~"
            z.blocked.add((_x, _y))
for _px, _py in [(58, 21), (69, 22), (58, 31), (69, 30)]:                                  # пальмы по берегу
    z.maybe(z._palm, _px, _py)
for _px, _py in [(59, 24), (68, 27)]:                                  # камыш у воды
    z.maybe("grass_big", _px, _py)

# стены из самана вдоль бульвара: север — к купальням и «Замку», юг — к лагерю и домам целителей; арки — проходы
z.paint("p", 45, 28, 46, 32)                         # к домам целителей — проход арки
for gx, gy in ((19, 20), (55, 20), (29, 30), (45, 30)):
    z.put(ADOBE_GATE, gx, gy, check=False, allow_reserved=True)
z.hwall(ADOBE_WALL, 12, 62, 20, gaps=tuple(range(19, 23)) + tuple(range(55, 59)))
z.hwall(ADOBE_WALL, 21, 62, 30, gaps=tuple(range(29, 33)) + tuple(range(45, 49)))
for x in (18, 23, 54, 59, 28, 33, 44, 49):           # фонари у арок
    z.maybe(LANTERN_ZZ, x, 21 if x < 40 and x in (18, 23) or x in (54, 59) else 31, allow_reserved=True)
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

# мощёные дворы перед купальнями и «Замком» — между зданием и стеной
z.paint("p", 14, 18, 27, 19)
z.paint("p", 50, 18, 65, 19)
for x, y in ((15, 19), (26, 19), (51, 19), (64, 19)):
    z.maybe(PLANT, x, y)
for x in (17, 24, 52, 62):
    z.maybe("bench_7", x, 19)
# родник «Сладкая вода» между купальнями и «Замком»: небольшой пруд в пальмовой роще
for _y in range(7, 15):
    for _x in range(34, 44):
        if ((_x - 39) / 4.3) ** 2 + ((_y - 10.5) / 3.2) ** 2 <= 1:
            z.ground[_y][_x] = "~"
            z.blocked.add((_x, _y))
for _px, _py in ((31, 6), (32, 11), (33, 15), (37, 17), (41, 17), (46, 14), (47, 9), (43, 4), (36, 4), (30, 12)):
    z.maybe(PALMS[(_px + _py) % 4], _px, _py)
for _px, _py in ((35, 15), (39, 15), (43, 14), (33, 9), (45, 11), (38, 6), (44, 7)):
    z.maybe(REEDS[(_px + _py) % 4], _px, _py)
z.paint("p", 38, 16, 39, 19)                         # тропа от родника к бульвару
for x, y in ((29, 17), (48, 17)):
    z.maybe(LANTERN_ZZ, x, y)
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

# лагерь живёт: шатёр-лазарет у входа, ряд ковриков для молитвы, мешки, шкуры, фонари, круг пальм у костра
for name, x, y in ((TENT_BIG, 6, 44), (TENT, 20, 45), (TENT_S, 28, 40), (TENT_AWN, 31, 44), (TENT_S, 13, 36)):
    z.maybe(name, x, y)
for i, (x, y) in enumerate(((17, 36), (21, 36), (25, 35), (13, 41), (19, 42), (24, 41))):
    z.maybe((RUG_R, RUG_B)[i % 2], x, y)
for x, y in ((18, 40), (30, 39), (11, 43), (23, 38), (28, 34), (34, 37)):
    z.maybe(SACKS[(x + y) % 2], x, y)
    z.maybe(SKIN[(x + y) % 2], x + 1, y + 1)
for x, y in ((20, 34), (28, 36), (15, 40), (24, 44)):
    z.maybe(LANTERN_ZZ, x, y)
for x, y in ((18, 37), (30, 36), (21, 38), (27, 38)):
    z.maybe(PALMS[(x + y) % 4], x, y)
z.hwall(ADOBE_WALL, 5, 20, 32)                       # низкая стенка лагеря со стороны бульвара
# рынок у дороги: прилавки вдоль бульвара
for name, x in ((STALL, 8), (STALL_B, 12), (STALL, 16)):
    z.put(name, x, 30)
z.box(CRATE, 6, 30, "ящик торговца", {"чистая вода": 2, "консервы": 2, "вяленое мясо": 1}, owner="merchant_zz")

# дома целителей (юго-восток) — глинобитные, в ряд вдоль улочки
for name, x in ((HOUSE_A, 40), (HOUSE_B, 45), (HOUSE_C, 50), (HOUSE_BIG, 56)):
    z.put(name, x, 33)
z.paint_ragged("k", 36, 31, 66, 46, depth=3)          # квартал целителей — вытоптанная земля
for name, x, y in ((STALL, 40, 41), (STALL_B, 52, 41), (TENT_S, 57, 41), (TENT_AWN, 61, 41), (RUG_R, 44, 38),
                   (RUG_B, 54, 38)):
    z.maybe(name, x, y)
for x, y in ((38, 43), (44, 43), (50, 43), (57, 44), (64, 43), (64, 38)):
    z.maybe(PALMS[(x + y) % 4], x, y)
for x, y in ((43, 36), (49, 37), (55, 36), (62, 36)):
    z.maybe(LANTERN_ZZ, x, y)
z.hwall(ADOBE_WALL, 37, 66, 45)                      # задняя стена квартала
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
bt.wall_code("W", "pk:bazaar/bazaar_w2_12")
bt.wall_code("Q", "pk:bazaar/bazaar_w2_12")
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
bt.floor_code("~", "pk:mport/p1/8,4,1,1", "pk:mport/p1/9,4,1,1")
bt.water_codes = ("~",)
bt.paint("~", 8, 5, 21, 10)                           # чаша бассейна — настоящая вода с каменной кромкой
for x in (6, 12, 17, 24):
    bt.maybe(PLANT, x, 3)
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
ht.floor_code("C", "pk:hotel/hotel_f1_23")           # холл и покои — бежевый мрамор вместо шахматки
ht.floor_code("D", "pk:zcity/zcity_f1_00")          # столовая и номера — доски
ht.floor_code("R", "pk:aoffice/p3/3,1,1,1")         # ковровое покрытие номеров
ht.wall_code("V", "pk:hotel/hotel_w1_23")
ht.wall_code("Y", "pk:hotel/hotel_w1_15")
LOBBY = ht.room(12, 13, 31, 25, "V", "C")          # холл
DINE = ht.room(1, 13, 12, 25, "V", "D")             # столовая
SUITE = ht.room(31, 13, 43, 25, "V", "C")           # покои Спрингера
ROOMS = [ht.room(x, 1, x + 8, 13, "Y", "R") for x in (1, 9, 17, 25, 33)]
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
ht.box("cabinet_small", 10, 16, "буфет", {"консервы": 2, "энергетический батончик": 1, "обрывок карты (север)": 1})
# номера: кровать у стены, тумбочка, шкаф; в одном — постоялец
for i, x0 in enumerate((1, 9, 17, 25, 33)):
    ht.put(BED if i % 2 == 0 else BED_S, x0 + 2, 4)
    ht.put(NIGHT, x0 + 1, 4)
    ht.put(WARDROBE, x0 + 6, 4)
    ht.stamp(f"zz_room_rug{i}", "pk:lhotel/p2/10,12,2,2", x0 + 2, 7, water=False)
    ht.put(ARMCHAIR, x0 + 6, 9)
    ht.put(LAMP, x0 + 1, 10)
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
ht.stamp("zz_lobby_rug", "pk:lhotel/p2/10,12,2,2", 20, 21, water=False)
ht.stamp("zz_suite_rug", "pk:lhotel/p2/10,12,2,2", 36, 20, water=False)
ht.put(ARMCHAIR, 37, 16)          # кресло в покоях, у северной стены рядом с кроватью
ht.put(LAMP, 33, 22)


# ================================================================ цистерна
cs = CityMap(city, "zzyzx_cistern", "Цистерна под купальнями", 34, 22, start=(4, 5), seed=84, interior=True,
             music="lab", night=[78, 92, 104])
cs.floor_code("M", *METAL)
cs.wall_code("K", "pk:nbunk/nbunk_w1_12")
cs.room(1, 1, 33, 21, "K", "M")
cs.props.append(["x_ladder", 4, 4])
cs.portal([(4, 4)], "zzyzx_bath", (34, 13), "Наверх, в насосную")
cs.reserve(2, 4, 7, 7)
# каналы с водой: две полосы воды через зал, между ними — мостки
cs.floor_code("~", "pk:mport/p1/8,4,1,1", "pk:mport/p1/9,4,1,1")
cs.water_codes = ("~",)
cs.paint("~", 9, 6, 18, 9)                            # отстойники — настоящая вода с каменной кромкой
cs.paint("~", 9, 14, 18, 17)
for x, y in ((6, 8), (20, 8), (6, 16), (20, 16), (13, 11), (13, 12), (22, 12), (8, 19)):
    cs.maybe(SEWER_PIPE_ZZ, x, y)
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

# цистерна: сырость, подтёки, зелёная подсветка воды и красные лампы у фильтра, тросы и трубы по стенам
LM.lamps(cs, "green", [(8, 5), (20, 5), (13, 13), (22, 15), (8, 18)])
LM.lamps(cs, "cold", [(26, 7), (30, 10)])
LM.lamps(cs, "red", [(24, 14), (31, 15)])
LM.decals(cs, "x_vd_wet0", [(5, 10), (20, 11), (7, 12), (24, 18), (14, 4)])
LM.decals(cs, "x_vd_wet1", [(11, 19), (28, 8)])
LM.decals(cs, "x_vd_waterline", [(8, 7), (19, 7), (8, 15), (19, 15)])
LM.decals(cs, "x_vd_drip", [(10, 4), (17, 4), (30, 3)])
LM.decals(cs, "x_vd_rust0", [(3, 12), (23, 5)])
LM.decals(cs, "x_vd_hz_h", [(24, 11), (25, 11)])
LM.doors(cs)

city.save(gap_exempt=("springer", "nurse_ava", "gus", "bath_pilgrim", "bath_pilgrim_b"))
# на карте мира — «Зайзикс»; открывается, если пройти рядом, или после Бейкера (src/game/quests.py)
L = json.load(open("data/locations.json", encoding="utf-8"))
L["zzyzx"].update({"world_name": "Зайзикс", "discover": True})
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
