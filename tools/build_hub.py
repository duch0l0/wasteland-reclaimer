"""
Хаб — торговая столица у оазиса (Fallout 1, за сорок лет до прихода Выходца из Убежища).
Начало второго акта. Сценарий — docs/story.md, раздел 10.

  hub          «Хаб: Оазис» (78×58): площадь вокруг оазиса с пальмами, базар (прилавки с едой,
               специями, тканями, оружием), двор Красного каравана (повозки, коновязь), башня водной
               артели Долорес Веги, бар «Мальтийский сокол», пост Хабской стражи, шатёр «Детей
               Единства» с бесплатной водой. Выходы: запад и восток — пустошь, юг — Старый город.
  hub_old      «Хаб: Старый город» (64×44): трущобы из лачуг и палаток, костры, свалка, притон
               молодого Декера, вход в старый акведук.
  hub_falcon   бар «Мальтийский сокол» (интерьер): стойка, столы, сцена, задняя комната.
  hub_water    водная артель Долорес Веги (интерьер): контора, зал с бочками, покои Долорес.
  hub_tunnels  старый акведук под Хабом: каналы, откуда берётся вода оазиса; крысолюды и чужие следы.

Наборы: desert-bazaar (bazaar), desert-town (destown), desert-natural (desnat), wild-west (west),
wasteland-port (wport), nuclear-bunker (nbunk).
Запуск из папки game_project:  .venv/bin/python tools/build_hub.py
"""
import json

from citykit import City, CityMap

city = City("hub", "Хаб")


def P(name, img, **kw):
    city.prop(name, img, **kw)
    return name


def cells(page, pts):
    return [f"pk:{page}/{x},{y},1,1" for x, y in pts]


# ------------------------------------------------------------ объекты
STALL_BREAD = P("hb_stall_bread", "pk:bazaar/bazaar_2_002", foot=[2, 1], sight=True)
STALL_VEG = P("hb_stall_veg", "pk:bazaar/bazaar_2_003", foot=[2, 1], sight=True)
STALL_FRUIT = P("hb_stall_fruit", "pk:bazaar/bazaar_2_004", foot=[2, 1], sight=True)
STALL_MEAT = P("hb_stall_meat", "pk:bazaar/bazaar_2_005", foot=[2, 1], sight=True)
STALL_CHEESE = P("hb_stall_cheese", "pk:bazaar/bazaar_2_014", foot=[2, 1], sight=True)
SPICES = P("hb_spices", "pk:bazaar/bazaar_2_006", foot=[2, 1])
SPICES_B = P("hb_spices_b", "pk:bazaar/bazaar_2_007", foot=[2, 1])
CLOTH_RACK = P("hb_cloth", "pk:bazaar/bazaar_2_035", foot=[2, 1], sight=True)
SCARVES = P("hb_scarves", "pk:bazaar/bazaar_2_036", foot=[2, 1], sight=True)
SWORDS = P("hb_blades", "pk:bazaar/bazaar_2_015", foot=[2, 1], sight=True)
SHIELDS = P("hb_shields", "pk:bazaar/bazaar_2_016", foot=[2, 1], sight=True)
ARMOR = P("hb_armor_rack", "pk:bazaar/bazaar_2_017", foot=[2, 1], sight=True)
JARS = P("hb_jars", "pk:bazaar/bazaar_2_048", foot=[1, 1], search="shelf", title="кувшины")
POTS = P("hb_pots", "pk:bazaar/bazaar_2_049", foot=[2, 1])
CART = P("hb_cart", "pk:bazaar/bazaar_1_023", foot=[2, 1], sight=True)
CART_B = P("hb_cart_b", "pk:bazaar/bazaar_1_029", foot=[2, 1], sight=True)
TENT_RED = P("hb_tent_red", "pk:bazaar/bazaar_1_003", foot=[2, 2], sight=True)
TENT_W = P("hb_tent_white", "pk:bazaar/bazaar_1_004", foot=[2, 2], sight=True)
TENT_G = P("hb_tent_green", "pk:bazaar/bazaar_1_014", foot=[2, 2], sight=True)
TENT_Y = P("hb_tent_yellow", "pk:bazaar/bazaar_1_007", foot=[2, 2], sight=True)
CARPET_STALL = P("hb_carpet_stall", "pk:bazaar/bazaar_1_017", foot=[4, 2], sight=True)
RUG = P("hb_rug", "pk:bazaar/bazaar_1_089", block=False, layer="floor")
RUG_B = P("hb_rug_b", "pk:bazaar/bazaar_1_103", block=False, layer="floor")
SCALES = P("hb_scales", "pk:bazaar/bazaar_1_022", foot=[2, 1])
CRATE = P("hb_crate", "pk:bazaar/bazaar_3_000", search="crate", title="ящик")
BARREL = P("hb_barrel", "pk:desnat/desnat_3_014", search="junk", title="бочка")
WATER_BARREL = P("hb_water_barrel", "pk:desnat/desnat_3_037")
PALM_POT = P("hb_palm_pot", "pk:bazaar/bazaar_3_206")
LANTERN = P("hb_lantern", "pk:bazaar/bazaar_2_088", block=False,
            light={"r": 120, "color": [255, 180, 90], "at": [0.5, 0.4], "flicker": 0.3})
PALMS = [P(f"hb_palm{i}", f"pk:desnat/desnat_4_{n:03d}", foot=[1, 1]) for i, n in enumerate((49, 50, 51, 52))]
WELL = P("hb_well", "pk:desnat/desnat_3_026", foot=[2, 1])
OASIS = "pk:destown/p5/8,5,8,11"
TENT_SHABBY = P("hb_tent_shabby", "pk:destown/destown_3_015", foot=[2, 2], sight=True)
TENT_LOW = P("hb_tent_low", "pk:destown/destown_3_018", foot=[2, 1])
FIRE = P("hb_fire", "pk:destown/destown_3_034", block=False, layer="floor")
JUNK = P("hb_junk", "pk:wport/wport_3_013", foot=[2, 1], search="junk", title="куча хлама")
TIRES = P("hb_tires", "pk:wport/wport_1_013", foot=[2, 1])
BAR_COUNTER = P("hb_bar", "pk:west/west_2_108", foot=[4, 1])
SHELF_BOTTLES = P("hb_bottle_shelf", "pk:west/west_2_110", sight=True, search="shelf", title="полка с бутылками")
TABLE = P("hb_table", "pk:west/west_2_000", foot=[2, 1])
POKER = P("hb_poker", "pk:west/west_2_020", foot=[2, 1])
CHAIR = P("hb_chair", "pk:west/west_2_001")
PIANO = P("hb_piano", "pk:west/west_2_012", foot=[2, 1])
BED = P("hb_bed", "pk:west/west_2_005", foot=[2, 2])
DESK = P("hb_desk", "pk:west/west_2_000", foot=[2, 1])
SAFE = P("hb_safe", "pk:west/west_2_105", search="military", title="сейф")
BOOKS = P("hb_bookcase", "pk:west/west_2_116", sight=True, search="shelf", title="шкаф с бумагами")
CLOCK = P("hb_clock", "pk:west/west_2_019", sight=True)
TANKS = P("hb_tanks", "pk:nbunk/nbunk_2_021", sight=True)
PUMP = P("hb_pump", "pk:nbunk/nbunk_2_028")

SAND = cells("destown/p2", [(0, 0), (1, 0), (0, 1), (1, 1)])
GRAVEL = cells("destown/p2", [(4, 0), (5, 0), (4, 1), (5, 1)])
CRACK = cells("destown/p2", [(8, 0), (9, 0), (8, 1), (9, 1)])
PLAZA = ["pk:bazaar/bazaar_f1_27"]
COBBLE = ["pk:bazaar/bazaar_f1_26"]
PLANK = ["pk:bazaar/bazaar_f1_21"]
STONE_IN = ["pk:bazaar/bazaar_f1_19"]
METAL = cells("nbunk/p2", [(4, 8), (5, 9), (6, 10), (4, 10)])
WATER = cells("mport/p1", [(8, 4), (9, 4), (10, 4), (11, 4)])


# ================================================================ Оазис
W, H = 78, 58
hb = CityMap(city, "hub", "Хаб: Оазис", W, H, start=(2, 29), seed=101, music="hub", world_pos=(1020, 1235))
hb.floor_code("s", *SAND)
hb.floor_code("g", *GRAVEL)
hb.floor_code("p", *PLAZA)
hb.paint("s", 0, 0, W - 1, H - 1)
hb.exits = [(0, y) for y in range(27, 32)] + [(W - 1, y) for y in range(27, 32)]
hb.paint("g", 0, 27, W - 1, 31)                         # караванная дорога через весь город
hb.paint("p", 24, 14, 54, 26)                           # площадь у оазиса
hb.paint("g", 37, 32, 40, H - 1)                        # на юг — к Старому городу
hb.reserve(0, 26, W - 1, 32)
hb.reserve(36, 32, 41, H - 1)
hb.portal([(x, H - 1) for x in (37, 38, 39, 40)], "hub_old", (32, 1), "Старый город")

hb.npcs += [["dolores", 36, 9], ["hub_guard", 20, 25], ["hub_guard_b", 58, 33], ["crimson_boss", 64, 36],
            ["spice_seller", 28, 24], ["arms_seller", 49, 24], ["cult_preacher", 13, 36], ["bos_scout", 70, 22],
            ["hub_kid", 44, 34], ["water_clerk", 34, 12]]
for _, x, y in hb.npcs:
    hb.reserve(x, y, x, y)

# оазис в центре площади: пальмы по кругу, колодец у края
hb.stamp("hb_oasis", OASIS, 35, 14, water=True)
for x, y in ((33, 15), (33, 21), (44, 15), (44, 22), (36, 25)):
    hb.put(PALMS[(x + y) % 4], x, y)
hb.put(WELL, 30, 19)

# базар вдоль площади: ряды прилавков по краям — продукты на западе, ремесло на востоке
for i, (name, x) in enumerate(((STALL_BREAD, 25), (STALL_VEG, 28), (STALL_FRUIT, 25), (STALL_MEAT, 28))):
    hb.put(name, x, 16 if i < 2 else 20)
hb.put(SPICES, 25, 23)
hb.put(SPICES_B, 30, 23)
hb.put(CLOTH_RACK, 47, 16)
hb.put(SCARVES, 50, 16)
hb.put(SWORDS, 47, 20)
hb.put(SHIELDS, 50, 20)
hb.put(ARMOR, 52, 23)
hb.put(CARPET_STALL, 43, 23)             # ковровый ряд у южного края площади
hb.put(SCALES, 32, 25)
for x, y in ((24, 14), (54, 14), (24, 26), (54, 26)):
    hb.put(LANTERN, x, y)

# север: башня водной артели (каменная, с крышей) и бар «Мальтийский сокол»
hb.building(28, 2, 16, 10, "concrete", south=(6,))       # водная артель Долорес Веги
hb.portal([(34, 11), (35, 11)], "hub_water", (15, 21), "Водная артель Веги")
hb.building(48, 3, 14, 9, "planks", south=(4,))          # «Мальтийский сокол»
hb.portal([(52, 11), (53, 11)], "hub_falcon", (13, 19), "Бар «Мальтийский сокол»")
hb.put(PALM_POT, 46, 12)
hb.put(PALM_POT, 63, 12)
# северо-запад: пост Хабской стражи (кирпич), коновязь
hb.building(6, 6, 12, 9, "brick", south=(4,))
hb.box(CRATE, 8, 16, "ящик стражи", {"патроны": 12, "бинт": 2}, owner="hub_guard")

# юго-восток: двор Красного каравана — повозки, бочки с водой, тюки
hb.hwall(["fence_picket", "fence_picket2", "post_fence_a"], 56, 74, 34, gaps=(60, 61, 62, 63))
for x, y in ((58, 37), (62, 39), (67, 37), (70, 41)):
    hb.put(CART if (x + y) % 2 else CART_B, x, y)
for x in (57, 59, 72):
    hb.put(WATER_BARREL, x, 44)
hb.box(CRATE, 65, 44, "груз Красного каравана", {"чистая вода": 3, "консервы": 2, "крышки": 30},
       owner="crimson_boss")
hb.put(TENT_Y, 68, 46)

# юго-запад: шатёр «Детей Единства» — бесплатная вода, очередь из бедняков
hb.put(TENT_W, 10, 37)
hb.box(WATER_BARREL, 14, 39, "бочка «святой воды»", {"святая вода": 3}, owner="cult_preacher")
hb.put(RUG, 9, 41)
hb.put(RUG_B, 13, 42)
hb.npcs += [["hub_beggar", 9, 43], ["hub_beggar_b", 12, 44]]

# северо-восток: застава Братства у дороги — разведчица смотрит на караваны культа
hb.put(TENT_G, 70, 18)
hb.put(TIRES, 72, 22)

# дома горожан вдоль дороги (юг)
hb.building(18, 44, 10, 8, "planks", north=(4,))
hb.building(44, 44, 10, 8, "brick", north=(4,))
hb.box("wardrobe", 46, 47, "шкаф горожанина", {"ткань": 2, "крышки": 15})
hb.scatter(PALMS + ["r_dry_bush", "r_rocks"], 1, 1, W - 2, 5, 10)
hb.scatter(["r_dry_bush", "r_rocks", "r_bones"], 1, 33, 34, H - 2, 10)


# ================================================================ Старый город
W, H = 64, 44
od = CityMap(city, "hub_old", "Хаб: Старый город", W, H, start=(32, 2), seed=102, music="raiders")
od.floor_code("s", *SAND)
od.floor_code("k", *CRACK)
od.floor_code("g", *GRAVEL)
od.paint("k", 0, 0, W - 1, H - 1)
od.paint("g", 30, 0, 34, 30)
od.paint("g", 6, 20, 58, 23)
od.reserve(29, 0, 35, 30)
od.reserve(5, 19, 59, 24)
od.portal([(x, 0) for x in (30, 31, 32, 33, 34)], "hub", (38, 56), "Оазис")
od.npcs += [["decker", 10, 36], ["junkie", 44, 13], ["old_woman", 22, 10], ["street_kid", 50, 30]]
od.enemies += [["gang", 6, 30], ["gang", 11, 30], ["raider", 54, 40]]   # охрана у двери притона, бродяга на свалке
for _, x, y in od.npcs:
    od.reserve(x, y, x, y)
# трущобы: лачуги рядами вдоль улицы, палатки во дворах, костры
for name, x, y in (("r_shack", 4, 8), ("r_shack_tin", 12, 7), ("r_cabin", 20, 5), ("r_shed_tin", 40, 7),
                   ("r_hut", 48, 8), ("r_shanty", 55, 7), ("r_cabin_b", 5, 26), ("r_shack_e", 20, 27),
                   ("r_cabin_d", 40, 27), ("r_shack_f", 50, 27)):
    od.put(name, x, y)
for x, y in ((8, 14), (24, 14), (44, 15), (56, 15)):
    od.put(TENT_SHABBY if x % 3 else TENT_LOW, x, y)
for x, y in ((14, 16), (48, 17), (26, 31)):
    od.put(FIRE, x, y)
# притон Декера: кирпичный дом на юго-западе, перед ним — охрана
od.building(4, 32, 12, 9, "brick", north=(4,))
od.box(SAFE, 13, 37, "сейф Декера", {"крышки": 160, "стимулятор": 2, "отмычка": 2},
       requires={"item": "отмычка", "msg": "Сейф Декера. Без отмычки и крепких нервов — никак."}, owner="decker")
# дворы трущоб: заборы из хлама, верёвки с тряпьём, ящики, бочки — тесно, как в настоящих трущобах
for x0, y0 in ((3, 12), (18, 12), (38, 12), (52, 12)):
    od.hwall(["fence_broken", "plank_fence_b", "post_fence_a", "chain_broken_a"], x0, x0 + 8, y0 + 5, gaps=(x0 + 3, x0 + 4))
    od.maybe("pile_rags", x0 + 1, y0 + 3)
    od.maybe("barrel_wood", x0 + 7, y0 + 1)
    od.maybe(CRATE, x0 + 6, y0 + 3)
for x0, y0 in ((3, 25), (18, 25), (38, 25), (50, 25)):
    od.maybe("pile_cloth", x0 + 7, y0 + 2)
    od.maybe("r_barrels", x0 + 1, y0 + 4)
    od.maybe("firewood", x0 + 5, y0 + 4)
od.scatter(["r_trash", "r_bones", "pile_cans", "pile_bottles", "pile_scrap", "r_planks"], 1, 1, W - 2, H - 2, 26)
od.scatter(["r_dry_bush", "r_rocks"], 1, 1, W - 2, H - 2, 10)
od.npcs += [["slum_mother", 9, 22], ["slum_old", 42, 24], ["slum_boy", 25, 18]]
od.npcs += [["harold", 36, 30]]          # Гарольд (Fallout 1–3): вернулся из Марипозы в 2102-м — и остался
# свалка на юго-востоке
od.put(JUNK, 46, 34)
od.put(JUNK, 52, 36)
od.put(TIRES, 57, 34)
od.box("r_dumpster", 44, 38, "мусорный бак", {"пружина": 1, "изолента": 1, "батарейки": 1})
# вход в старый акведук — люк у фонтана
od.put("r_water_tower_b", 26, 36)
od.props.append(["x_manhole", 30, 38])
od.portal([(30, 38)], "hub_tunnels", (4, 5), "Старый акведук")


# ================================================================ «Мальтийский сокол»
fc = CityMap(city, "hub_falcon", "Бар «Мальтийский сокол»", 28, 22, start=(13, 19), seed=103, interior=True,
             music="junktown")
fc.floor_code("F", *PLANK)
fc.wall_code("W", "pk:bazaar/bazaar_w2_12")
fc.room(1, 6, 18, 21, "W", "F")                    # зал
fc.room(18, 6, 27, 16, "W", "F")                   # задняя комната — карты на деньги
fc.opening(13, 21, 14, 21, "F")
fc.portal([(13, 21), (14, 21)], "hub", (52, 12), "На площадь")
fc.opening(18, 11, 18, 12, "F")
# стойка вдоль северной стены, полки с бутылками за ней; бармен между
fc.put(SHELF_BOTTLES, 3, 9)
fc.put(SHELF_BOTTLES, 8, 9)
fc.put(BAR_COUNTER, 4, 11)
fc.put(CLOCK, 12, 9)
fc.npcs += [["falcon_barkeep", 6, 10]]
# сцена с пианино в северо-восточном углу, певица у пианино
fc.put(PIANO, 14, 9)
fc.put(RUG, 14, 11)
fc.npcs += [["falcon_singer", 15, 12]]
# зал: столы со стульями рядами, проход от двери к стойке свободен
for x, y in ((3, 14), (8, 14), (3, 17), (8, 17), (14, 15), (14, 18)):
    fc.put(TABLE, x, y)
    fc.put(CHAIR, x + 2, y)
fc.npcs += [["falcon_drunk", 7, 15]]
# задняя комната: стол для покера, сейф
fc.put(POKER, 21, 11)
fc.put(CHAIR, 23, 11)
fc.box(SAFE, 25, 9, "сейф хозяина", {"крышки": 120}, requires={"item": "отмычка", "msg": "Сейф. Нужна отмычка."})
fc.npcs += [["falcon_gambler", 21, 13]]


# ================================================================ водная артель
wa = CityMap(city, "hub_water", "Водная артель Веги", 32, 24, start=(15, 21), seed=104, interior=True, music="hub")
wa.floor_code("F", *STONE_IN)
wa.floor_code("M", *METAL)
wa.wall_code("W", "pk:bazaar/bazaar_w1_22")
OFFICE = wa.room(1, 12, 31, 23, "W", "F")          # контора у входа
HALL = wa.room(1, 1, 20, 12, "W", "M")             # зал с бочками и насосом
ROOMS = wa.room(20, 1, 31, 12, "W", "F")           # покои Долорес
wa.opening(15, 23, 16, 23, "F")
wa.portal([(15, 23), (16, 23)], "hub", (34, 12), "На площадь")
wa.opening(10, 12, 11, 14, "M")
wa.opening(25, 12, 26, 14, "F")
# контора: стойка учёта лицом к двери, шкафы с бумагами вдоль стены, весы
wa.put("counter", 12, 17)
wa.put("counter", 17, 17)
wa.put(BOOKS, 3, 15)
wa.put(BOOKS, 5, 15)
wa.put(SCALES, 27, 17)                     # весы для бочек — у восточной стены
wa.terminal(21, 15, "hub_water_ledger")
# зал: баки и насос у северной стены, бочки рядами
wa.put(TANKS, 3, 4)
wa.put(TANKS, 6, 4)
wa.put(PUMP, 12, 4)
for x in (3, 6, 9, 12, 15):
    wa.put(WATER_BARREL, x, 9)
wa.box(CRATE, 17, 4, "ящик с фильтрами", {"таблетки для очистки воды": 3, "гаечный ключ": 1})
# покои Долорес: кровать, стол, сейф — жетон Марипозы
wa.put(BED, 22, 4)
wa.put(DESK, 27, 4)
wa.put(CHAIR, 29, 4)
wa.box(SAFE, 29, 9, "сейф Долорес", {"крышки": 200, "армейская фотография": 1},
       requires={"flag": "dolores_trust", "msg": "Сейф Долорес. Открыть может только она."}, owner="dolores")


# ================================================================ акведук
tn = CityMap(city, "hub_tunnels", "Старый акведук", 46, 26, start=(4, 5), seed=105, interior=True, music="caves")
tn.floor_code("M", *COBBLE)
tn.floor_code("~", *WATER)
tn.wall_code("K", "pk:bazaar/bazaar_w1_07")
tn.water_codes = ("~",)
tn.room(1, 1, 45, 25, "K", "M")
tn.paint("~", 10, 11, 44, 13)                     # канал через весь акведук — к оазису на север
for x in (18, 19, 30, 31):                         # мостки через канал
    tn.paint("M", x, 11, x, 13)
tn.props.append(["x_ladder", 4, 4])
tn.portal([(4, 4)], "hub_old", (31, 38), "Наверх, в Старый город")
tn.reserve(2, 4, 7, 8)
tn.enemies += [["ratman", 14, 7], ["ratman", 24, 18], ["ratman", 36, 8], ["ratman_boss", 42, 6]]
tn.put("x_pipe", 12, 4)
tn.put("x_pipe", 26, 4)
# у шлюза: следы недавней работы — бочки с жёлтыми треугольниками и чужой ящик
tn.put(BARREL, 38, 17)
tn.put(BARREL, 40, 17)
tn.box(CRATE, 42, 22, "ящик с печатью круга", {"образец ВРЭ": 1, "листовка Единства": 1})
tn.terminal(34, 16, "hub_sluice")

city.save(gap_exempt=("dolores", "water_clerk", "falcon_barkeep", "hub_guard", "decker", "falcon_gambler",
                      "falcon_drunk", "falcon_singer"))
L = json.load(open("data/locations.json", encoding="utf-8"))
L["hub"].update({"world_name": "Хаб", "discover": True})
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
