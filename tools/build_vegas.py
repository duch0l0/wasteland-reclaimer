"""
Руины Вегаса — «Три Короны». Главный город третьего акта, ночь.
Сценарий — docs/story.md, раздел «Руины Вегаса — „Три Короны“».

  vegas_strip    «Стрип» (80×56): ничья земля между тремя племенами — разбитые казино с неоном, запечатанная
                 башня «Лаки 38», руины башни Vault-Tec (над хранилищем «Ноль»), рынок и судья Стрипа.
                 Север — к Сапогам, юг — к Змеям, восток — к Ладоням.
  vegas_boots    «Сапоги Мохаве»: электростанция (градирни, реактор, щиты), гараж с мотоциклами, виселица.
  vegas_snakes   «Змеиная родня»: рынок, вход в игорный подвал, люк в змеиные ходы.
  vegas_den      игорный подвал Змей: столы, бар, угол Матери-Змеи.
  vegas_palms    «Белые Ладони»: библиотека, лазарет, сад.
  vegas_library  библиотека Ладоней: читальный зал, салон Матушки Агаты, кухня.
  vegas_tunnels  змеиные ходы: канализация под Стрипом — до подвала башни Vault-Tec.
  vegas_tower    башня Vault-Tec: холл, архив, лифтовая шахта.
  vegas_zero     хранилище «Ноль»: шлюз с армейским замком (двое из трёх: сетчатка, голос, код).
  vegas_vault    за дверью: десять контейнеров ВРЭ и криокапсула члена совета Vault-Tec.

Наборы: zombie-city (zcity), modern-casino (casino), nuclear-power-plant (npower), modern-library (lib),
luxury-restaurant (lrest), abandoned-coal-mine (cmine), junkyard (jtown), bazaar, nbunk, wlab, apark, west, gcave.
Запуск из папки game_project:  .venv/bin/python tools/build_vegas.py
"""
import json

from citykit import City, CityMap

city = City("vegas", "Руины Вегаса")
NIGHT = [70, 76, 120]


def P(name, img, **kw):
    city.prop(name, img, **kw)
    return name


def cells(page, pts):
    return [f"pk:{page}/{x},{y},1,1" for x, y in pts]


NEON = lambda c: {"r": 120, "color": c, "at": [0.5, 0.5], "flicker": 0.15}
# ------------------------------------------------------------ руины Стрипа
TOWERS = [P(f"vg_tower{i}", f"pk:zcity/zcity_5_{n:03d}", scale=1.6, foot=[3, 2], sight=True) for i, n in enumerate((0, 1, 2, 3, 5))]
TOWER_BROKEN = P("vg_tower_broken", "pk:zcity/zcity_5_004", scale=1.6, foot=[3, 2], sight=True)
LUCKY38 = P("vg_lucky38", "pk:zcity/zcity_5_000", scale=2.4, foot=[4, 2], sight=True,
            light={"r": 90, "color": [255, 230, 150], "at": [0.5, 0.1], "flicker": 0.5})
VT_TOWER = P("vg_vt_tower", "pk:zcity/zcity_5_004", scale=2.4, foot=[4, 2], sight=True)
CASINO_FRONT = P("vg_casino_front", "pk:casino/casino_4_051", foot=[4, 1], sight=True,
                 light=NEON([255, 120, 200]))
CASINO_SIGN = P("vg_casino_sign", "pk:casino/casino_4_002", block=False, light=NEON([255, 90, 180]))
JACKPOT = P("vg_jackpot", "pk:casino/casino_1_062", foot=[6, 2], sight=True, light=NEON([255, 210, 90]))
NEON_CASH = P("vg_neon_cash", "pk:casino/casino_1_052", block=False, light=NEON([120, 255, 140]))
NEON_JP = P("vg_neon_jp", "pk:casino/casino_1_054", block=False, light=NEON([255, 200, 90]))
SHOP_ROW = P("vg_shop_row", "pk:zcity/zcity_5_022", foot=[6, 1], sight=True)
WRECKS = [P(f"vg_wreck{i}", f"pk:zcity/zcity_2_{n:03d}", foot=[2, 1], sight=True) for i, n in enumerate((1, 5, 13, 21, 34, 45, 97))]
RUBBLE = [P(f"vg_rubble{i}", f"pk:zcity/zcity_4_{n:03d}", foot=[2, 1]) for i, n in enumerate((7, 8, 9, 21, 22, 23))]
LAMPS = [P("vg_lamp", "pk:apark/apark_3_064", light={"r": 140, "color": [255, 200, 140], "at": [0.5, 0.1]}),
         P("vg_lamp_b", "pk:apark/apark_3_089", light={"r": 140, "color": [255, 200, 140], "at": [0.5, 0.1]})]
STALLS = [P("vg_stall", "pk:jtown/jtown_1_009", foot=[2, 1]), P("vg_stall_b", "pk:apark/apark_1_030", foot=[2, 1], sight=True)]
FIRE_BARREL = "x_fire_barrel"
CRATE = P("vg_crate", "pk:bazaar/bazaar_3_000", search="crate", title="ящик")
SAFE = P("vg_safe", "pk:west/west_2_105", search="military", title="сейф")
# Сапоги
COOLING = P("vg_cooling", "pk:npower/npower_1_022", foot=[2, 2], sight=True)
REACTOR = P("vg_reactor", "pk:npower/npower_1_007", foot=[4, 3], sight=True,
            light={"r": 150, "color": [140, 255, 160], "at": [0.5, 0.4], "flicker": 0.2})
TANK_RAD = [P("vg_tank_rad", "pk:npower/npower_1_000", foot=[2, 1], sight=True), P("vg_tank_rad_b", "pk:npower/npower_1_008", foot=[2, 1], sight=True)]
FAN = P("vg_fan", "pk:npower/npower_1_005", foot=[2, 1], sight=True)
PUMP = [P("vg_pump", "pk:npower/npower_1_013", foot=[2, 1]), P("vg_pump_b", "pk:npower/npower_1_032", foot=[2, 1])]
PANEL = [P("vg_panel", "pk:npower/npower_2_036", foot=[2, 1]), P("vg_panel_b", "pk:npower/npower_2_002", foot=[2, 1])]
WARN = P("vg_warn", "pk:npower/npower_1_069")
BIKES = [P("vg_bike", "pk:jtown/jtown_2_010", foot=[2, 1], sight=True), P("vg_bike_b", "pk:jtown/jtown_2_022", foot=[2, 1], sight=True),
         P("vg_bike_c", "pk:jtown/jtown_2_028", foot=[2, 1], sight=True)]
WAGON = P("vg_wagon", "pk:west/west_1_012", foot=[4, 1], sight=True)
TROUGH = P("vg_trough", "pk:west/west_1_016")
HAY = P("vg_hay", "pk:west/west_1_004", block=False)
GALLOWS = P("vg_gallows", "pk:cmine/cmine_1_101", scale=1.6, foot=[3, 1], sight=True)
TIRES = P("vg_tires", "pk:ucamp/ucamp_2_043", foot=[2, 1])
CAMPFIRE = P("vg_campfire", "pk:ucamp/ucamp_2_040", foot=[2, 1],
             light={"r": 120, "color": [255, 150, 70], "at": [0.5, 0.5], "flicker": 0.35})
# Змеи
TENTS = [P(f"vg_tent{i}", f"pk:ucamp/ucamp_2_{n:03d}", foot=[2, 1], sight=True) for i, n in enumerate((0, 3, 19, 21))]
BAZ_STALLS = [P("vg_bz_spice", "pk:bazaar/bazaar_2_006", foot=[2, 1]), P("vg_bz_cloth", "pk:bazaar/bazaar_2_035", foot=[2, 1], sight=True),
              P("vg_bz_blades", "pk:bazaar/bazaar_2_015", foot=[2, 1], sight=True), P("vg_bz_jars", "pk:bazaar/bazaar_2_048", foot=[1, 1])]
LANTERN = P("vg_lantern", "pk:bazaar/bazaar_2_088", block=False,
            light={"r": 110, "color": [255, 180, 90], "at": [0.5, 0.4], "flicker": 0.3})
ROULETTE = P("vg_roulette", "pk:casino/casino_1_026", foot=[4, 2])
BLACKJACK = P("vg_blackjack", "pk:casino/casino_3_024", foot=[4, 2])
POKER = P("vg_poker", "pk:casino/casino_4_030", foot=[4, 2])
SLOTS = [P(f"vg_slot{i}", f"pk:casino/casino_1_{n:03d}", foot=[1, 1], sight=True) for i, n in enumerate(range(8))]
BAR = P("vg_bar", "pk:west/west_2_108", foot=[4, 1])
BOTTLES = P("vg_bottles", "pk:west/west_2_110", sight=True, search="shelf", title="полка с бутылками")
SOFA = P("vg_sofa", "pk:casino/casino_4_038", foot=[2, 1])
# Ладони
BOOKCASES = [P(f"vg_bookcase{i}", f"pk:lib/lib_1_{n:03d}", foot=[2, 1], sight=True, search="shelf", title="книжный шкаф")
             for i, n in enumerate((4, 5, 20, 21))]
BOOK_TALL = [P("vg_book_tall", "pk:lib/lib_1_008", sight=True), P("vg_book_tall_b", "pk:lib/lib_1_024", sight=True)]
READ_TABLE = [P("vg_read_table", "pk:lib/lib_1_060", foot=[2, 2]), P("vg_read_table_b", "pk:lib/lib_1_061", foot=[2, 2])]
LIB_LAMP = P("vg_lib_lamp", "pk:lib/lib_1_066", light={"r": 100, "color": [255, 220, 160], "at": [0.5, 0.2]})
PLANTS = [P("vg_plant", "pk:lib/lib_1_084"), P("vg_plant_b", "pk:lib/lib_1_085")]
DESK_LIB = P("vg_desk_lib", "pk:lib/lib_1_112", foot=[2, 1])
PAINTINGS = [P("vg_painting", "pk:lrest/lrest_3_003", block=False), P("vg_painting_b", "pk:lrest/lrest_3_004", block=False),
             P("vg_painting_c", "pk:lrest/lrest_3_011", block=False)]
WINE = [P("vg_wine", "pk:lrest/lrest_3_018", foot=[2, 1], sight=True, search="shelf", title="винный шкаф"),
        P("vg_wine_b", "pk:lrest/lrest_3_037", foot=[2, 1], sight=True)]
CANDELABRA = P("vg_candelabra", "pk:lrest/lrest_2_032",
               light={"r": 100, "color": [255, 190, 110], "at": [0.5, 0.2], "flicker": 0.4})
ARMCHAIR = [P("vg_armchair", "pk:lrest/lrest_1_041"), P("vg_armchair_b", "pk:lrest/lrest_1_042")]
LOUNGE = P("vg_lounge", "pk:lrest/lrest_2_097", foot=[2, 1])
HOOKS = P("vg_hooks", "pk:cmine/cmine_1_102", scale=1.5, foot=[3, 1], sight=True)
CHAIN = P("vg_chain", "pk:cmine/cmine_1_112", foot=[2, 1])
BUTCHER = P("vg_butcher", "pk:west/west_2_000", foot=[2, 1])
BONES = [P("vg_bones", "pk:grave/grave_2_022", block=False), P("vg_bones_b", "pk:grave/grave_2_027", block=False)]
HOSP_BED = P("vg_hosp_bed", "pk:hosp/hosp_1_007", foot=[3, 1])
MED_SHELF = P("vg_med_shelf", "pk:hosp/hosp_1_009", sight=True, search="drawer", title="шкаф с лекарствами")
TENT_WHITE = P("vg_tent_white", "pk:bazaar/bazaar_1_004", foot=[2, 2], sight=True)
GARDEN = [P("vg_garden", "pk:ghouse/ghouse_3_048", foot=[2, 1]), P("vg_garden_b", "pk:ghouse/ghouse_3_024", foot=[2, 1])]
# туннели, башня, хранилище
SEWER_RUBBLE = [P("vg_sewer_rubble", "pk:sewer/sewer_1_042", foot=[2, 1]), P("vg_sewer_moss", "pk:sewer/sewer_1_041", foot=[2, 1])]
DESKS = [P("vg_vt_desk", "pk:aoffice/aoffice_1_000"), P("vg_vt_desk_b", "pk:aoffice/aoffice_1_004")]
CABINETS = P("vg_cabinets", "pk:aoffice/aoffice_3_013", sight=True, search="drawer", title="картотека")
RECEPTION = P("vg_reception", "pk:lhotel/lhotel_1_012", foot=[4, 1])
DEBRIS = P("vg_debris", "pk:pmall/pmall_2_042")
SERVER = P("vg_server", "pk:npower/npower_2_042")
CONSOLES = [P("vg_console", "pk:npower/npower_2_006", foot=[2, 1]), P("vg_console_b", "pk:npower/npower_2_013", foot=[2, 1])]
VRE_CRATE = P("vg_vre_crate", "pk:wlab/wlab_2_024", foot=[2, 1], sight=True)
CRYO = P("vg_cryo", "pk:wlab/wlab_3_101", foot=[2, 1], sight=True,
         light={"r": 110, "color": [140, 220, 255], "at": [0.5, 0.5], "flicker": 0.05})
TUBE_DEAD = P("vg_tube_dead", "pk:wlab/wlab_3_103", foot=[2, 1], sight=True)
BIOHAZ = P("vg_biohazard", "pk:hosp/hosp_1_012")

ROAD = ["pk:zcity/zcity_f3_09"]
WALK = ["pk:zcity/zcity_f1_22"]
RUBBLE_FL = ["pk:zcity/zcity_f2_26"]
DIRT = ["pk:zcity/zcity_f2_00"]
SAND = cells("destown/p2", [(0, 0), (1, 0), (0, 1), (1, 1)])
GRAVEL = cells("mbase/p1", [(8, 8), (9, 9), (10, 10), (9, 8), (8, 10), (10, 9)])
PLATES = ["pk:fstation/fstation_f2_09"]
CASINO_FL = ["pk:store/p1/2,8,1,1"]
WOOD = ["pk:fstation/fstation_f2_22"]
CARPET = ["pk:aoffice/p3/3,1,1,1"]
TILE_W = ["pk:store/p1/12,0,1,1"]
STONE = ["pk:zcity/zcity_f1_23"]
WATER = cells("sewer/p1", [(10, 1), (11, 1)])


def vegas_map(mid, name, w, h, start, seed, **kw):
    m = CityMap(city, mid, name, w, h, start=start, seed=seed, night=NIGHT, **kw)
    return m


# ================================================================ Стрип
W, H = 80, 56
st = vegas_map("vegas_strip", "Руины Вегаса: Стрип", W, H, (1, 27), 221, music="reno", world_pos=(2620, 500))
st.floor_code("r", *RUBBLE_FL)
st.floor_code("a", *ROAD)
st.floor_code("p", *WALK)
st.paint("r", 0, 0, W - 1, H - 1)
st.paint("p", 34, 0, 45, H - 1)                        # Стрип — с юга на север
st.paint("a", 36, 0, 43, H - 1)
st.paint("p", 0, 24, W - 1, 31)                        # поперечная улица
st.paint("a", 0, 26, W - 1, 29)
st.exits = [(0, y) for y in range(26, 30)]
st.reserve(0, 26, W - 1, 29)
st.reserve(36, 0, 43, H - 1)

# северо-запад: «Лаки 38» — запертая башня, в окнах иногда мигает свет
st.put(LUCKY38, 22, 8)
st.terminal(27, 12, "lucky38_door")
# северо-восток: руины башни Vault-Tec — над хранилищем «Ноль»; вход завален
st.put(VT_TOWER, 52, 8)
st.terminal(51, 12, "vt_tower_door")
st.portal([(54, 11), (55, 11)], "vegas_tower", (18, 26), "Башня Vault-Tec",
          requires={"flag": "tower_front_open", "msg": "Вход в башню завален бетоном. Нужен динамит — или другой путь, снизу."})
st.reserve(53, 11, 56, 13)
# казино вдоль улиц: фасады с неоном, вывески
for x, y in ((4, 20), (12, 20), (60, 20), (68, 20)):
    st.put(CASINO_FRONT, x, y)
st.put(CASINO_SIGN, 5, 18)
st.put(CASINO_SIGN, 69, 18)
st.put(JACKPOT, 4, 34)
st.put(NEON_CASH, 14, 33)
st.put(NEON_JP, 62, 33)
st.put(SHOP_ROW, 60, 34)
for i, (x, y) in enumerate(((8, 6), (14, 6), (62, 4), (70, 6), (4, 42), (12, 46), (60, 44), (70, 46))):
    st.put((TOWERS + [TOWER_BROKEN])[i % 6], x, y)
# вдоль самого Стрипа — фасады казино с неоном: здесь ещё помнят, каким был город
for x, y in ((29, 4), (46, 4), (29, 40), (46, 40), (29, 48), (46, 48)):
    st.maybe(CASINO_FRONT, x, y)
for x, y in ((30, 16), (47, 16), (30, 44), (47, 44)):
    st.maybe([NEON_CASH, NEON_JP, CASINO_SIGN][(x + y) % 3], x, y)
# ничья земля у перекрёстка: рынок, бочки с огнём, судья Стрипа
for x in (26, 30):
    st.put(STALLS[x % 2], x, 34)
st.put(STALLS[1], 48, 34)
for x, y in ((33, 23), (46, 23), (33, 32), (46, 32)):
    st.put(FIRE_BARREL, x, y)
for x, y in ((31, 22), (48, 22), (31, 33), (48, 33)):
    st.put(LAMPS[(x + y) % 2], x, y)
for i, (x, y) in enumerate(((20, 25), (56, 30), (38, 14), (40, 42), (24, 30))):
    st.maybe(WRECKS[i % len(WRECKS)], x, y)
st.npcs += [["judge_sol", 40, 32], ["strip_trader", 28, 36], ["strip_drunk", 50, 36], ["grey_buyer", 32, 30],
            ["strip_kid", 47, 24]]
for _, x, y in st.npcs:
    st.reserve(x, y, x, y)
st.scatter(RUBBLE + ["r_trash"], 1, 1, 33, 22, 10)
st.scatter(RUBBLE + ["r_trash"], 46, 1, W - 2, 22, 10)
st.scatter(RUBBLE + ["r_trash", "r_bones"], 1, 33, 33, H - 2, 10)
st.scatter(RUBBLE + ["r_trash", "r_bones"], 46, 33, W - 2, H - 2, 10)


# ================================================================ Сапоги Мохаве
W, H = 64, 44
bt = vegas_map("vegas_boots", "Вегас: Сапоги Мохаве", W, H, (39, 42), 222, music="junktown")
bt.floor_code("s", *SAND)
bt.floor_code("g", *GRAVEL)
bt.floor_code("a", *ROAD)
bt.paint("s", 0, 0, W - 1, H - 1)
bt.paint("g", 4, 3, 60, 18)                            # территория электростанции
bt.paint("a", 36, 18, 43, H - 1)
city.road(st, [(x, 0) for x in range(36, 44)], bt, [(x, H - 1) for x in range(36, 44)], "Сапоги Мохаве", "Стрип", step=(0, -1))
bt.reserve(35, 30, 44, H - 1)
# электростанция: градирни, реактор, баки, насосы, щит управления — Сапоги держат свет Вегаса
bt.put(COOLING, 6, 4)
bt.put(COOLING, 10, 4)
bt.put(REACTOR, 18, 5)
bt.put(TANK_RAD[0], 26, 5)
bt.put(TANK_RAD[1], 29, 5)
bt.put(FAN, 34, 5)
bt.put(PUMP[0], 26, 10)
bt.put(PUMP[1], 30, 10)
bt.put(PANEL[0], 40, 6)
bt.put(PANEL[1], 43, 6)
bt.terminal(47, 6, "boots_power")
bt.box(SAFE, 52, 6, "сейф электростанции", {"чертёж электростанции": 1},
       requires={"item": "отмычка", "msg": "Сейф инженеров. Без отмычки не открыть."}, owner="boots_engineer")
for x in (6, 22, 50):
    bt.put(WARN, x, 15)
# гараж и стойла: мотоциклы рядом, повозки, поилки, сено
for i, x in enumerate((5, 8, 11)):
    bt.put(BIKES[i], x, 23)
bt.put(WAGON, 5, 28)
bt.put(TROUGH, 14, 27)
bt.put(HAY, 12, 30)
bt.put(TIRES, 16, 23)
bt.box(CRATE, 4, 33, "ящик с книгами", {"книги Ладоней": 1}, owner="hank_spur")
# виселица посреди двора — закон Сапогов
bt.put(GALLOWS, 26, 26)
bt.put(CAMPFIRE, 30, 32)
# штаб Хэнка «Шпоры» — дом с крышей на востоке
bt.building(48, 22, 12, 10, "planks", south=(4,))
bt.npcs += [["hank_spur", 28, 29], ["boots_engineer", 45, 9], ["boots_rider", 9, 26], ["boots_rider_b", 33, 35],
            ["boots_rider_c", 54, 34]]
for _, x, y in bt.npcs:
    bt.reserve(x, y, x, y)
bt.scatter(["r_rocks", "r_dry_bush", "r_trash"], 1, 19, W - 2, H - 2, 12)


# ================================================================ Змеиная родня
W, H = 64, 44
sn = vegas_map("vegas_snakes", "Вегас: Змеиная родня", W, H, (39, 1), 223, music="raiders")
sn.floor_code("r", *RUBBLE_FL)
sn.floor_code("a", *ROAD)
sn.floor_code("d", *DIRT)
sn.paint("r", 0, 0, W - 1, H - 1)
sn.paint("a", 36, 0, 43, 20)
sn.paint("d", 8, 14, 58, 38)                           # рынок
city.road(st, [(x, 55) for x in range(36, 44)], sn,
          [(x, 0) for x in range(36, 44)], "Змеиная родня", "Стрип", step=(0, 1))
sn.reserve(35, 0, 44, 12)
# рынок: ряды прилавков, палатки, фонари — продаётся всё
for i, (x, y) in enumerate(((12, 18), (16, 18), (20, 18), (12, 23), (20, 23), (46, 18), (50, 18), (54, 18))):
    sn.put(BAZ_STALLS[i % 4], x, y)
for x, y in ((10, 30), (16, 32), (48, 30), (54, 32)):
    sn.put(TENTS[(x + y) % 4], x, y)
for x, y in ((14, 16), (22, 16), (48, 16), (56, 16), (30, 34)):
    sn.put(LANTERN, x, y)
sn.box(CRATE, 24, 26, "склад Змей", {"патроны": 20, "самогон": 2}, owner="snake_guard")
# игорный подвал — дом с неоном; люк в змеиные ходы во дворе
sn.building(26, 30, 12, 9, "brick", north=(4,))
sn.put(NEON_CASH, 27, 29)
sn.props.append(["x_manhole", 52, 38])
sn.portal([(52, 38)], "vegas_tunnels", (4, 5), "Змеиный ход",
          requires={"flag": "snakes_passage", "msg": "Люк сторожат. «Ходы — только для родни и тех, за кого родня поручилась»."})
sn.reserve(50, 36, 54, 40)
sn.npcs += [["snake_kid", 18, 26], ["snake_guard", 51, 35], ["snake_trader", 50, 21], ["snake_gambler", 33, 27]]
for _, x, y in sn.npcs:
    sn.reserve(x, y, x, y)
sn.scatter(RUBBLE + ["r_trash", "r_bones"], 1, 1, W - 2, 12, 10)
sn.scatter(["r_trash", "pile_cans"], 8, 14, 58, 38, 10)


# ================================================================ игорный подвал
dn = CityMap(city, "vegas_den", "Подвал Змей", 32, 22, start=(15, 4), seed=224, interior=True, music="reno")
dn.floor_code("F", *CASINO_FL)
dn.floor_code("O", *WOOD)
dn.wall_code("W", "pk:jtown/jtown_w2_04")
dn.room(1, 1, 22, 21, "W", "F")                       # игорный зал
dn.room(22, 1, 31, 21, "W", "O")                      # угол Матери-Змеи
dn.opening(15, 1, 16, 3, "F")
sn.portal([(30, 30), (31, 30)], "vegas_den", (15, 4), "Игорный подвал")
dn.portal([(15, 1), (16, 1)], "vegas_snakes", (30, 28), "Наверх")
dn.opening(22, 11, 22, 12, "O")
for i, y in enumerate(range(6, 14)):
    dn.put(SLOTS[i % 8], 2, y)
dn.put(ROULETTE, 6, 8)
dn.put(BLACKJACK, 13, 8)
dn.put(POKER, 6, 14)
dn.put(BOTTLES, 13, 17)
dn.put(BAR, 13, 19)
dn.put(SOFA, 26, 5)
dn.put(SOFA, 28, 5)
dn.terminal(29, 9, "snakes_ledger")
dn.box(SAFE, 29, 18, "сундук Матери-Змеи", {"чертёж змеиных ходов": 1, "крышки": 150},
       requires={"item": "отмычка", "msg": "Сундук Матери-Змеи. Замок хитрый, как она сама."}, owner="mother_snake")
dn.npcs += [["mother_snake", 26, 12], ["den_dealer", 9, 11], ["den_barkeep", 15, 18]]


# ================================================================ Белые Ладони
W, H = 60, 42
pl = vegas_map("vegas_palms", "Вегас: Белые Ладони", W, H, (1, 21), 225, music="hub")
pl.floor_code("r", *RUBBLE_FL)
pl.floor_code("s", *STONE)
pl.floor_code("d", *DIRT)
pl.paint("r", 0, 0, W - 1, H - 1)
pl.paint("s", 0, 19, 40, 23)                           # чистая мощёная дорожка — Ладони метут её каждое утро
pl.paint("d", 44, 26, 58, 40)                          # сад
city.road(st, [(79, y) for y in range(26, 30)], pl, [(0, y) for y in range(19, 23)], "Белые Ладони", "Стрип", step=(1, 0))
pl.reserve(0, 18, 6, 24)
pl.building(14, 4, 20, 14, "brick", south=(8,))      # библиотека
pl.reserve(22, 18, 23, 20)
pl.put(TENT_WHITE, 42, 8)                             # лазарет
pl.put(HOSP_BED, 46, 12)
pl.put(HOSP_BED, 46, 15)
pl.box(MED_SHELF, 51, 9, "шкаф с лекарствами", {"стимулятор": 1, "бинт": 2}, owner="palms_doctor")
pl.terminal(53, 14, "palms_infirmary")
for i, (x, y) in enumerate(((46, 28), (50, 28), (54, 28), (46, 33), (54, 33))):
    pl.put(GARDEN[i % 2], x, y)
for x, y in ((12, 20), (36, 20), (40, 6), (40, 18)):
    pl.put(LAMPS[(x + y) % 2], x, y)
pl.npcs += [["palms_doorman", 24, 21], ["palms_doctor", 49, 12], ["palms_gardener", 50, 31], ["palms_reader", 30, 25]]
for _, x, y in pl.npcs:
    pl.reserve(x, y, x, y)
pl.scatter(RUBBLE + ["r_trash"], 1, 25, 40, H - 2, 8)


# ================================================================ библиотека Ладоней
lb = CityMap(city, "vegas_library", "Библиотека Ладоней", 40, 28, start=(18, 26), seed=226, interior=True, music="hub")
lb.floor_code("F", *WOOD)
lb.floor_code("C", *CARPET)
lb.floor_code("T", *TILE_W)
lb.wall_code("W", "pk:lhotel/lhotel_w2_23")
lb.wall_code("K", "pk:hosp/hosp_w1_00")
lb.room(1, 1, 26, 27, "W", "F")                       # читальный зал
lb.room(26, 1, 39, 14, "W", "C")                      # салон Матушки Агаты
lb.room(26, 14, 39, 27, "K", "T")                     # кухня
lb.opening(18, 27, 19, 27, "F")
pl.portal([(22, 17), (23, 17)], "vegas_library", (18, 25), "Библиотека")
lb.portal([(18, 27), (19, 27)], "vegas_palms", (22, 19), "Наружу")
lb.opening(26, 8, 26, 9, "C")
lb.opening(26, 20, 26, 21, "T")
for i, x in enumerate((2, 4, 8, 10, 14, 16, 20, 22)):
    lb.put(BOOKCASES[i % 4], x, 4)
lb.put(READ_TABLE[0], 4, 10)
lb.put(READ_TABLE[1], 10, 10)
lb.put(READ_TABLE[0], 16, 10)
lb.put(READ_TABLE[1], 4, 16)
lb.put(READ_TABLE[0], 16, 16)
for x, y in ((8, 9), (14, 9), (8, 15), (22, 15)):
    lb.put(LIB_LAMP, x, y)
lb.put(BOOK_TALL[0], 24, 10)
lb.put(BOOK_TALL[1], 24, 16)
for x in (2, 4, 20, 22):                                 # ряд стеллажей поперёк зала — книги Вегаса
    lb.maybe(BOOKCASES[x % 4], x, 19)
lb.put(PLANTS[0], 2, 24)
lb.put(PLANTS[1], 23, 24)
lb.put(DESK_LIB, 10, 22)
lb.npcs += [["palms_librarian", 12, 23]]
# салон: картины, винные шкафы, кресла, канделябры — терминал Агаты
for i, x in enumerate((28, 32, 36)):
    lb.put(PAINTINGS[i], x, 3)
lb.put(WINE[0], 28, 5)
lb.put(WINE[1], 36, 5)
lb.put(ARMCHAIR[0], 30, 9)
lb.put(ARMCHAIR[1], 34, 9)
lb.put(LOUNGE, 31, 12)
lb.put(CANDELABRA, 28, 11)
lb.put(CANDELABRA, 37, 11)
lb.terminal(37, 8, "agatha_salon")
lb.npcs += [["mother_agatha", 32, 7]]
# кухня: разделочные столы, крюки, цепи — и кости в углу
lb.put(HOOKS, 28, 17)
lb.put(HOOKS, 34, 17)
lb.put(BUTCHER, 29, 22)
lb.put(BUTCHER, 34, 22)
lb.put(CHAIN, 36, 25)
for x, y in ((37, 19), (31, 25)):
    lb.put(BONES[(x + y) % 2], x, y)
lb.npcs += [["palms_cook", 32, 20]]


# ================================================================ змеиные ходы
W, H = 50, 30
tn = CityMap(city, "vegas_tunnels", "Змеиные ходы", W, H, start=(4, 5), seed=227, interior=True, music="caves")
tn.floor_code("M", *STONE)
tn.floor_code("~", *WATER)
tn.wall_code("K", "pk:zcity/zcity_w2_03")
tn.water_codes = ("~",)
tn.room(1, 1, 49, 29, "K", "M")
tn.paint("~", 8, 13, 46, 15)
for x in (14, 15, 30, 31):
    tn.paint("M", x, 13, x, 15)
tn.props.append(["x_ladder", 4, 4])
tn.portal([(4, 4)], "vegas_snakes", (52, 37), "Наверх, к Змеям")
tn.reserve(2, 4, 8, 8)
tn.props.append(["x_ladder", 45, 25])
tn.portal([(45, 25)], "vegas_tower", (4, 26), "Подвал башни Vault-Tec")
tn.reserve(42, 23, 47, 27)
tn.put(SEWER_RUBBLE[0], 20, 6)
tn.put(SEWER_RUBBLE[1], 36, 22)
tn.enemies += [["ratman", 22, 8], ["ratman", 34, 20], ["mommy_mutant", 40, 8], ["feral", 26, 24], ["feral", 12, 22]]
tn.scatter(["r_trash", "r_bones"] + SEWER_RUBBLE, 2, 3, 48, 28, 10)


# ================================================================ башня Vault-Tec
W, H = 40, 30
tw = CityMap(city, "vegas_tower", "Башня Vault-Tec", W, H, start=(18, 26), seed=228, interior=True, music="lab")
tw.floor_code("T", *TILE_W)
tw.floor_code("C", *CARPET)
tw.wall_code("W", "pk:pmall/pmall_w3_10")
tw.room(1, 12, 39, 29, "W", "T")                      # холл
tw.room(1, 1, 22, 12, "W", "C")                       # архив
tw.room(22, 1, 39, 12, "W", "T")                      # лифтовая шахта
tw.opening(18, 29, 19, 29, "T")
tw.portal([(18, 29), (19, 29)], "vegas_strip", (54, 13), "На Стрип")
tw.props.append(["x_ladder", 4, 27])
tw.portal([(4, 27)], "vegas_tunnels", (45, 26), "Вниз, в змеиные ходы")
tw.reserve(2, 26, 6, 28)
tw.opening(10, 12, 11, 14, "C")
tw.opening(30, 12, 31, 14, "T")
tw.put(RECEPTION, 16, 18)
for x, y in ((6, 16), (28, 22), (34, 16), (12, 24)):
    tw.put(DEBRIS, x, y)
for i, x in enumerate((3, 5, 7, 9)):
    tw.put(CABINETS, x, 4)
tw.put(DESKS[0], 14, 6)
tw.terminal(18, 4, "tower_archive")
tw.put(CONSOLES[0], 24, 4)
tw.put(SERVER, 36, 4)
tw.props.append(["x_ladder", 31, 7])
tw.portal([(31, 7)], "vegas_zero", (19, 26), "Лифтовая шахта — вниз, к «Нолю»",
          requires={"flag": "zero_power", "msg": "Лифт мёртв уже сорок четыре года. Нужно питание: электростанция Сапогов — или кто-то ещё."})
tw.reserve(29, 6, 33, 9)
tw.enemies += [["robot_guard", 30, 20], ["feral", 8, 22], ["feral", 34, 26]]


# ================================================================ хранилище «Ноль»: шлюз
W, H = 40, 30
zr = CityMap(city, "vegas_zero", "Хранилище «Ноль»", W, H, start=(19, 26), seed=229, interior=True, music="vats")
zr.floor_code("M", *PLATES)
zr.wall_code("W", "pk:fstation/fstation_w1_10")
zr.room(1, 1, 39, 29, "W", "M")
zr.props.append(["x_ladder", 19, 27])
zr.portal([(19, 27)], "vegas_tower", (31, 8), "Наверх, в шахту лифта")
zr.reserve(17, 25, 22, 28)
zr.put("x_vault_gear0", 18, 3, force=True)
zr.portal([(19, 4), (20, 4)], "vegas_vault", (19, 26), "Хранилище",
          requires={"flag": "zero_open", "msg": "Армейский замок «Ноля»: питание, коды совета — и двое из Списка Марипозы."})
zr.reserve(17, 4, 22, 7)
zr.terminal(13, 6, "zero_door")
for x in (4, 8, 30, 34):
    zr.put(CONSOLES[x % 2], x, 4)
zr.enemies += [["turret", 6, 14], ["turret", 33, 14]]


# ================================================================ хранилище «Ноль»: внутри
W, H = 40, 30
vt = CityMap(city, "vegas_vault", "«Ноль»: хранилище", W, H, start=(19, 26), seed=230, interior=True, music="vats")
vt.floor_code("M", *PLATES)
vt.wall_code("W", "pk:fstation/fstation_w1_08")
vt.room(1, 1, 39, 29, "W", "M")
vt.opening(19, 29, 20, 29, "M")
vt.portal([(19, 29), (20, 29)], "vegas_zero", (19, 6), "К шлюзу")
for i, (x, y) in enumerate(((4, 5), (8, 5), (12, 5), (4, 10), (8, 10), (28, 5), (32, 5), (28, 10), (32, 10), (36, 10))):
    vt.put(VRE_CRATE, x, y)
vt.put(BIOHAZ, 16, 5)
vt.put(BIOHAZ, 24, 5)
vt.terminal(20, 8, "zero_vault")
vt.put(CRYO, 18, 17)
vt.put(TUBE_DEAD, 14, 17)
vt.put(TUBE_DEAD, 24, 17)
vt.terminal(21, 20, "cryo_capsule")
vt.npcs += [["cooper_zero", 26, 22]]

city.save(gap_exempt=("cooper_zero",))
L = json.load(open("data/locations.json", encoding="utf-8"))
L["vegas_strip"].update({"world_name": "Руины Вегаса", "discover": True})
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
