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

from citykit import City, CityMap, tech_scenes

city = City("vegas", "Руины Вегаса")
NIGHT = [92, 98, 140]


def P(name, img, **kw):
    city.prop(name, img, **kw)
    return name


def cells(page, pts):
    return [f"pk:{page}/{x},{y},1,1" for x, y in pts]


NEON = lambda c: {"r": 120, "color": c, "at": [0.5, 0.5], "flicker": 0.15}
# ------------------------------------------------------------ руины Стрипа
TOWERS = [P(f"vg_tower{i}", f"pk:zcity/zcity_5_{n:03d}", scale=2.4, foot=[4, 2], sight=True) for i, n in enumerate((0, 1, 2, 3, 5))]
TOWER_BROKEN = P("vg_tower_broken", "pk:zcity/zcity_5_004", scale=2.4, foot=[4, 2], sight=True)
LUCKY38 = P("vg_lucky38", "pk:zcity/zcity_5_000", scale=2.4, foot=[4, 2], sight=True,
            light={"r": 90, "color": [255, 230, 150], "at": [0.5, 0.1], "flicker": 0.5})
VT_TOWER = P("vg_vt_tower", "pk:zcity/zcity_5_004", scale=2.4, foot=[4, 2], sight=True)
CASINO_FRONT = P("vg_casino_front", "pk:casino/casino_4_051", foot=[4, 1], sight=True,
                 light=NEON([255, 120, 200]))
CASINO_SIGN = P("vg_casino_sign", "pk:casino/casino_4_002", block=False, light={"r": 130, "color": [255, 90, 180], "at": [0.5, 0.5], "flicker": 0.4})
PALM_POTS = [P(f"vg_palmpot{i}", f"pk:casino/casino_4_{n:03d}", foot=[1, 1], keybg=True) for i, n in enumerate((13, 14, 15, 16, 17, 19, 34, 35, 36, 37))]
ROPE = [P("vg_rope_a", "pk:casino/casino_4_045", foot=[1, 1], keybg=True), P("vg_rope_b", "pk:casino/casino_4_050", foot=[1, 1], keybg=True)]
CARPETS_V = ["pk:casino/casino_4_047", "pk:casino/casino_4_048", "pk:casino/casino_4_049"]
CAM = P("vg_camera", "pk:casino/casino_4_000", block=False)
TRASHCAN = [P("vg_trash_a", "pk:casino/casino_4_052", foot=[1, 1], keybg=True), P("vg_trash_b", "pk:casino/casino_4_053", foot=[1, 1], keybg=True)]
HYDRANT_V = P("vg_hydrant", "pk:town50/town50_1_109", block=False)
PHONE_V = P("vg_phone", "pk:town50/town50_1_100", foot=[1, 1])
CHANDELIER = P("vg_chandelier", "pk:casino/casino_4_007", block=False, light={"r": 110, "color": [255, 220, 150], "at": [0.5, 0.5], "flicker": 0.08})
JUKE_V = P("vg_jukebox", "pk:town50/town50_1_084", foot=[1, 1], sight=True, light={"r": 90, "color": [255, 170, 90], "at": [0.5, 0.4], "flicker": 0.2})
SPOT_V = P("vg_spotlight", "pk:apark/apark_3_064", light={"r": 190, "color": [210, 230, 255], "at": [0.5, 0.1]})
JACKPOT = P("vg_jackpot", "pk:casino/casino_1_062", foot=[6, 2], sight=True, light=NEON([255, 210, 90]))
NEON_CASH = P("vg_neon_cash", "pk:casino/casino_1_052", block=False, light={"r": 130, "color": [120, 255, 140], "at": [0.5, 0.5], "flicker": 0.5})
NEON_JP = P("vg_neon_jp", "pk:casino/casino_1_054", block=False, light={"r": 130, "color": [255, 200, 90], "at": [0.5, 0.5], "flicker": 0.45})
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
WELL_V = P("vg_well", "pk:desnat/desnat_3_006", foot=[2, 1])
GARDEN = [P("vg_garden", "pk:ghouse/ghouse_3_048", foot=[2, 1]), P("vg_garden_b", "pk:ghouse/ghouse_3_024", foot=[2, 1])]
# туннели, башня, хранилище
VG_PALMS = [P(f"vg_palm{i}", f"pk:desnat/desnat_4_{n:03d}", foot=[1, 1]) for i, n in enumerate((49, 50, 51, 52))]
SW_FLOOR = ["noise:pk:sewer/p1/6,0,1,1"]
SW_MOSS = cells("sewer/p1", [(2, 0), (3, 0), (2, 1), (3, 1)])
SW_WATER = ["pk:sewer/p1/10,1,1,1", "pk:sewer/p1/11,1,1,1", "pk:sewer/p1/10,2,1,1"]
SW_PLANK = ["pk:sewer/p1/8,0,1,1", "pk:sewer/p1/9,0,1,1"]
SW_OUTLET = P("vg_sw_outlet", "pk:sewer/sewer_1_008", foot=[3, 1], sight=True)
SW_GATE = P("vg_sw_gate", "pk:sewer/sewer_1_007", foot=[3, 1], sight=True)
SW_BARREL = P("vg_sw_barrel", "pk:sewer/sewer_1_003", foot=[1, 1], search="junk", title="бочка")
SW_CRATE = P("vg_sw_crate", "pk:sewer/sewer_1_002", foot=[1, 1], search="crate", title="ящик")
SW_MUSH = [P(f"vg_sw_mush{i}", f"pk:sewer/sewer_1_{n:03d}", foot=[1, 1], keybg=True, light={"r": 60, "color": [150, 255, 170], "at": [0.5, 0.5]}) for i, n in enumerate((24, 25, 46))]
SW_HEAP = [P("vg_sw_heap_a", "pk:sewer/sewer_1_041", foot=[2, 2], keybg=True), P("vg_sw_heap_b", "pk:sewer/sewer_1_042", foot=[2, 2], keybg=True),
           P("vg_sw_heap_c", "pk:sewer/sewer_1_074", foot=[2, 2], keybg=True)]
SW_SKULL = P("vg_sw_skull", "pk:sewer/sewer_1_027", foot=[1, 1], keybg=True)
SW_PIPE = P("vg_sw_pipe", "pk:sewer/sewer_1_038", foot=[1, 2], keybg=True)
SW_LANTERN = P("vg_sw_lantern", "pk:sewer/sewer_1_010", foot=[1, 1], keybg=True, light={"r": 110, "color": [255, 170, 80], "at": [0.5, 0.4], "flicker": 0.35})
SEWER_RUBBLE = [P("vg_sewer_rubble", "pk:sewer/sewer_1_042", foot=[2, 1]), P("vg_sewer_moss", "pk:sewer/sewer_1_041", foot=[2, 1])]
DESKS = [P("vg_vt_desk", "pk:aoffice/aoffice_1_000"), P("vg_vt_desk_b", "pk:aoffice/aoffice_1_004")]
CABINETS = P("vg_cabinets", "pk:aoffice/aoffice_3_013", sight=True, search="drawer", title="картотека")
LOCKERS_V = [P("vg_locker_a", "pk:nbunk/nbunk_2_005", foot=[1, 1], search="locker", title="шкафчик"), P("vg_locker_b", "pk:nbunk/nbunk_2_006", foot=[1, 1], search="locker", title="шкафчик")]
BUNK_V = P("vg_bunk", "pk:nbunk/nbunk_2_000", foot=[2, 1], sight=True)
GEN_V = P("vg_gen", "pk:nbunk/nbunk_2_028", foot=[2, 2], sight=True)
CHAIR_V = P("vg_office_chair", "pk:aoffice/aoffice_1_002")
PLANT_V = [P("vg_office_plant_a", "pk:aoffice/aoffice_3_025"), P("vg_office_plant_b", "pk:aoffice/aoffice_1_002")]
COPIER_V = P("vg_copier", "pk:aoffice/aoffice_3_021")
WHITEBOARD_V = P("vg_whiteboard", "pk:aoffice/aoffice_2_010", block=False)
CHART_V = P("vg_chart", "pk:aoffice/aoffice_2_036", block=False)
SOFA_V = P("vg_sofa_wait", "pk:lhotel/lhotel_1_022", foot=[2, 1])
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
RUBBLE_FL = ["noise:pk:zcity/zcity_f2_26"]
DIRT = ["noise:pk:zcity/zcity_f2_22"]
SAND = ["pk:desnat/p1/0,0,1,1", "pk:desnat/p1/1,0,1,1", "pk:desnat/p1/0,1,1,1"]   # песок под цвет пустыни вокруг
GRAVEL = ["noise:pk:zcity/zcity_f3_10"]
PLATES = ["pk:fstation/fstation_f2_09"]
CASINO_FL = ["pk:store/p1/2,8,1,1"]
WOOD = ["pk:fstation/fstation_f2_22"]
CARPET = ["pk:aoffice/p3/3,1,1,1"]
MARBLE = ["pk:hotel/hotel_f1_23"]
STEEL = ["pk:nbunk/p2/4,8,1,1"]
GRILLE = ["pk:nbunk/p2/0,12,1,1"]
VT_LOGO = "pk:casino/casino_4_049"
TILE_W = ["pk:store/p1/12,0,1,1"]
STONE = ["pk:zcity/zcity_f1_23"]
WATER = cells("sewer/p1", [(10, 1), (11, 1)])


def vegas_map(mid, name, w, h, start, seed, **kw):
    kw.setdefault("night", NIGHT)
    m = CityMap(city, mid, name, w, h, start=start, seed=seed, **kw)
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
st.floor_code("h", "pk:zcity/zcity_f3_09")
for _y in range(2, H - 2, 6):                          # разметка Стрипа: осевая из коротких штрихов
    st.paint("h", 39, _y, 40, _y + 2)
for _x in range(2, W - 2, 6):
    st.paint("h", _x, 27, _x + 2, 28)
st.floor_code("d", "noise:pk:desnat/p1/0,0,1,1")
st.floor_code("c", "noise:pk:zcity/zcity_f3_10")
st.exits = [(0, y) for y in range(26, 30)]
st.reserve(0, 26, W - 1, 29)
st.reserve(36, 0, 43, H - 1)

# северо-запад: «Лаки 38» — запертая башня, в окнах иногда мигает свет
st.put(LUCKY38, 22, 8)
st.terminal(27, 12, "lucky38_door")
# площадь «Лаки 38»: гранитная площадка с круглой клумбой, прожекторы по краям, бархатные канаты, афиши, страж у входа
st.floor_code("g", "pk:zcity/zcity_f1_23")
st.paint("g", 16, 13, 34, 21)
for x in (16, 20, 24, 28, 32, 34):
    st.maybe(SPOT_V, x, 13, allow_reserved=True)
for x in (18, 22, 26, 30):
    st.maybe(ROPE[(x // 4) % 2], x, 20, allow_reserved=True)
for x, y in ((17, 15), (33, 15), (17, 19), (33, 19)):
    st.maybe(PALM_POTS[(x + y) % len(PALM_POTS)], x, y, allow_reserved=True)
for x in (19, 29):
    st.maybe([NEON_CASH, NEON_JP, CASINO_SIGN][(x // 10) % 3], x, 17, allow_reserved=True)
# северо-восток: руины башни Vault-Tec — над хранилищем «Ноль»; вход завален
st.put(VT_TOWER, 52, 8)
st.terminal(51, 12, "vt_tower_door")
st.portal([(54, 11), (55, 11)], "vegas_tower", (18, 26), "Башня Vault-Tec",
          requires={"flag": "tower_front_open", "msg": "Вход в башню завален бетоном. Нужен динамит — или другой путь, снизу."})
st.reserve(53, 11, 56, 13)
# казино — целые здания: бетонные стены и крыша, на южном фасаде — неоновый вход и вывеска над ним
CASINO_DONE = []
NEON_FLASH = [NEON_CASH, NEON_JP, CASINO_SIGN]


def casino(x0, y1, w=10, h=7):
    """Закрытое казино: x0 — левый край, y1 — строка южной стены (фасад смотрит на улицу)."""
    y0 = y1 - h + 1
    area = [(x, y) for x in range(x0 - 1, x0 + w + 1) for y in range(y0 - 1, y1 + 2)]
    if any(t in st.reserved or st.solid(*t) or not (0 < t[0] < st.W - 1 and 0 < t[1] < st.H - 1) for t in area):
        return False
    k = len(CASINO_DONE)
    CASINO_DONE.append((x0, y1))
    st.building(x0, y0, w, h, ("concrete", "brick", "metal", "planks")[k % 4], worn=False)    # крыши разные: казино не клоны
    fx = x0 + (w - 8) // 2
    st.put(CASINO_FRONT, fx, y1, force=True, allow_reserved=True)                 # вход поверх южной стены
    # у входа: красная дорожка, канаты, кадки с пальмами, урны — у каждого казино по-своему
    st.maybe(NEON_FLASH[k % 3], fx + 4, y1 + 3, allow_reserved=True)
    for dx in ((0, 7), (1, 6), (0, 3, 7))[k % 3]:
        st.maybe(PALM_POTS[(k * 3 + dx) % len(PALM_POTS)], fx + dx, y1 + 2, allow_reserved=True)
    for dx in (2, 5):
        st.maybe(ROPE[(k + dx) % 2], fx + dx, y1 + 2, allow_reserved=True)
    st.maybe(TRASHCAN[k % 2], x0 + w, y1 + 1, allow_reserved=True)
    st.maybe(CAM, fx + 3, y1 - 1, allow_reserved=True)
    return True


for x0, y1 in ((2, 22), (14, 22), (58, 22), (68, 22)):
    casino(x0, y1)
st.put(JACKPOT, 4, 34)
st.put(NEON_CASH, 14, 33)
st.put(NEON_JP, 62, 33)
st.put(SHOP_ROW, 60, 34)
for i, (x, y) in enumerate(((8, 6), (14, 6), (62, 4), (70, 6), (4, 42), (12, 46), (60, 44), (70, 46))):
    st.put((TOWERS + [TOWER_BROKEN])[i % 6], x, y)
# вдоль самого Стрипа — фасады казино с неоном: здесь ещё помнят, каким был город
for x0, y1 in ((22, 30), (46, 30), (22, 50), (46, 50)):   # казино вдоль самого Стрипа — фасадом на дорогу
    casino(x0, y1)
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
# Стрип: фонари по тротуарам в шахматном порядке, у обочин — брошенные машины; проезжая часть свободна
for i, y in enumerate((4, 11, 18, 36, 44, 51)):
    st.maybe(LAMPS[i % 2], 35 if i % 2 else 44, y, allow_reserved=True)
for i, (x, y) in enumerate(((36, 7), (41, 21), (36, 39), (41, 47))):
    st.maybe(WRECKS[(i + 3) % len(WRECKS)], x, y, allow_reserved=True)
# люк в подвал разрушенного «Первого банка Мохаве» — «Последний банк Вегаса»
st.props.append(["x_manhole", 22, 38])
st.portal([(22, 38)], "vegas_bank", (6, 5), "Люк в подвал банка",
          requires={"flag": "know_bank", "msg": "Тяжёлый люк с гербом банка. Заварен изнутри? Нет — просто никто не знает, что он открывается."})
st.reserve(21, 37, 23, 39)
st.npcs += [["strip_busker", 34, 37], ["strip_showgirl", 22, 34], ["strip_scav", 58, 34], ["strip_vendor", 44, 37], ["strip_guard_l38", 27, 14],
            ["judge_sol", 40, 32], ["strip_trader", 28, 36], ["strip_drunk", 50, 36], ["grey_buyer", 32, 30],
            ["strip_kid", 47, 24]]
for _, x, y in st.npcs:
    st.reserve(x, y, x, y)
# земля между кварталами — не сплошная тьма: песчаные намёты и растрескавшийся бетон пятнами, проседания у люков
st.patchwork("r", ["c", "c", "c", "d"], 40, 1, 3, seed=3)
# уличная жизнь Стрипа: баррикады Легиона из мешков и бочек, будки, гидранты, лавки, выгоревшие машины, афиши
for x, y in ((33, 20), (46, 20), (33, 35), (46, 35)):
    st.maybe("x_sandbags", x, y, allow_reserved=True)
for x in (13, 24, 54, 66, 74):
    st.maybe(HYDRANT_V, x, 32, allow_reserved=True)
for x in (8, 30, 50, 70):
    st.maybe(PHONE_V, x, 24, allow_reserved=True)
for x in (10, 20, 52, 62, 72):
    st.maybe("bench_7", x, 31, allow_reserved=True)
for x, y in ((31, 8), (48, 8), (31, 46), (48, 46), (31, 38), (48, 18)):
    st.maybe(PALM_POTS[(x + y) % len(PALM_POTS)], x, y, allow_reserved=True)
for x, y in ((32, 12), (47, 40), (32, 48), (47, 4)):
    st.maybe("r_billboard", x, y, allow_reserved=True)
for x, y in ((40, 6), (41, 14), (39, 22), (40, 34), (41, 42), (39, 50)):
    st.maybe(WRECKS[(x + y) % len(WRECKS)], x, y, allow_reserved=True)
st.scatter(RUBBLE + ["r_trash"], 1, 1, 33, 22, 10)
st.scatter(RUBBLE + ["r_trash"], 46, 1, W - 2, 22, 10)
st.scatter(RUBBLE + ["r_trash", "r_bones"], 1, 33, 33, H - 2, 10)
st.scatter(RUBBLE + ["r_trash", "r_bones"], 46, 33, W - 2, H - 2, 10)


# ================================================================ Сапоги Мохаве
W, H = 64, 44
bt = vegas_map("vegas_boots", "Вегас: Сапоги Мохаве", W, H, (39, 42), 222, music="junktown", night=[124, 122, 156])
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
bt.floor_code("o", "noise:pk:zcity/zcity_f2_26")
bt.floor_code("z", "pk:fstation/fstation_f2_09")
bt.patchwork("g", ["o"], 10, 1, 2, seed=7)            # бетонные плиты и тёмные масляные пятна на площадке станции
bt.hwall([CHAIN], 4, 60, 19, gaps=(36, 37, 38, 39, 40, 41, 42, 43))     # сетка вокруг станции, ворота к дороге
for x, y in ((8, 16), (16, 16), (24, 16), (30, 16), (46, 16), (54, 16)):
    bt.maybe(TANK_RAD[(x // 8) % 2], x, y)
for x, y in ((8, 14), (28, 14), (44, 14), (56, 14)):
    bt.maybe(PANEL[(x // 4) % 2], x, y)
for x in (10, 18, 26, 44, 52):
    bt.maybe(WARN, x, 7)
for x, y in ((9, 9), (14, 12), (22, 14), (33, 13), (38, 10), (48, 12), (57, 10), (58, 15)):
    bt.maybe(["pile_junk", "barrel_wood", "pile_cans", "r_trash"][x % 4], x, y)
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
sn = vegas_map("vegas_snakes", "Вегас: Змеиная родня", W, H, (39, 1), 223, music="raiders", night=[118, 108, 146])
sn.floor_code("r", *RUBBLE_FL)
sn.floor_code("a", *ROAD)
sn.floor_code("d", *DIRT)
sn.paint("r", 0, 0, W - 1, H - 1)
sn.paint("a", 36, 0, 43, 20)
sn.floor_code("q", "noise:pk:zcity/zcity_f1_22")
sn.paint_ragged("d", 6, 12, 60, 40, depth=3)                           # рынок
sn.paint_ragged("q", 7, 13, 59, 39, depth=2)                           # весь рынок — утоптанный светлый настил, а не тёмная пыль
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
sn.building(26, 30, 12, 9, "metal", north=(4,))
sn.put(NEON_CASH, 27, 29)
sn.props.append(["x_manhole", 52, 38])
sn.portal([(52, 38)], "vegas_tunnels", (4, 5), "Змеиный ход",
          requires={"flag": "snakes_passage", "msg": "Люк сторожат. «Ходы — только для родни и тех, за кого родня поручилась»."})
sn.reserve(50, 36, 54, 40)
sn.npcs += [["snake_kid", 18, 26], ["snake_guard", 51, 35], ["snake_trader", 50, 21], ["snake_gambler", 33, 27]]
for _, x, y in sn.npcs:
    sn.reserve(x, y, x, y)
for i, (x, y) in enumerate(((24, 20), (28, 20), (32, 20), (14, 28), (50, 24), (56, 24), (44, 28))):
    sn.maybe(BAZ_STALLS[(i + 2) % 4], x, y)
for x, y in ((8, 20), (60, 20), (8, 36), (58, 36), (22, 34), (42, 34)):
    sn.maybe(FIRE_BARREL, x, y)
for x, y in ((10, 16), (34, 16), (40, 16), (46, 36), (52, 30)):
    sn.maybe(LANTERN, x, y)
for x, y in ((12, 22), (16, 22), (20, 22), (34, 22), (46, 22), (52, 22), (14, 34), (46, 34), (52, 34)):
    sn.maybe(BAZ_STALLS[(x + y) % 4], x, y)
sn.maybe(NEON_CASH, 33, 28)
sn.maybe(NEON_JP, 45, 28)
for x, y in ((9, 14), (57, 14), (9, 38), (57, 38)):
    sn.maybe(FIRE_BARREL, x, y)
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
# игорный зал: ковры, люстры, бархатные канаты, острова столов, второй ряд автоматов у северной стены, картины и бра
dn.stamp("vg_den_rug_a", "pk:casino/p3/0,0,2,2", 5, 6, water=False)
dn.stamp("vg_den_rug_b", "pk:casino/p3/0,0,2,2", 12, 6, water=False)
dn.stamp("vg_den_rug_c", "pk:casino/p3/0,0,2,2", 6, 14, water=False)
dn.stamp("vg_den_rug_d", "pk:casino/p3/0,0,2,2", 16, 12, water=False)
for x, y in ((5, 4), (11, 4), (17, 4)):
    dn.maybe(CHANDELIER, x, y)
for x in (4, 9, 14):
    dn.maybe(SLOTS[x % 8], x, 3)
for x, y in ((4, 18), (8, 18), (18, 18), (3, 10), (19, 10)):
    dn.maybe(ROPE[(x + y) % 2], x, y)
for x, y in ((19, 6), (19, 15), (3, 20), (20, 20)):
    dn.maybe(PALM_POTS[(x + y) % len(PALM_POTS)], x, y)
dn.maybe(JUKE_V, 20, 8)
# покои Матери-Змеи: ковры, широкая кровать за ширмой, шкафы, полки с трофеями, лампы — хозяйка живёт не в подвале, а во дворце
dn.stamp("vg_den_rug_e", "pk:casino/p3/0,0,2,2", 25, 9, water=False)
dn.stamp("vg_den_rug_f", "pk:casino/p3/0,0,2,2", 24, 16, water=False)
dn.maybe("bed", 28, 3)
dn.maybe("wardrobe", 24, 3)
dn.maybe("shelf_wood", 30, 3)
dn.maybe("shelf_stuff_1", 24, 19)
dn.maybe("armchair", 24, 6)
dn.maybe("armchair", 29, 14)
dn.maybe("lantern_lit", 23, 12)
dn.maybe("lantern_lit", 30, 12)
dn.maybe("lantern_lit", 29, 20)
dn.maybe(PALM_POTS[2], 30, 16)
dn.maybe(PALM_POTS[5], 23, 20)
dn.npcs += [["mother_snake", 26, 12], ["den_dealer", 9, 11], ["den_barkeep", 15, 18]]


# ================================================================ Белые Ладони
W, H = 60, 42
pl = vegas_map("vegas_palms", "Вегас: Белые Ладони", W, H, (1, 21), 225, music="hub")
pl.floor_code("r", *RUBBLE_FL)
pl.floor_code("s", *STONE)
pl.floor_code("d", *DIRT)
pl.paint("r", 0, 0, W - 1, H - 1)
pl.paint("s", 0, 19, 40, 23)                           # чистая мощёная дорожка — Ладони метут её каждое утро
pl.paint_ragged("d", 42, 24, 60, 42, depth=3)
pl.paint_ragged("s", 6, 28, 34, 40, depth=2)            # южная площадь Ладоней — читальный дворик под открытым небом                          # сад
city.road(st, [(79, y) for y in range(26, 30)], pl, [(0, y) for y in range(19, 23)], "Белые Ладони", "Стрип", step=(1, 0))
pl.reserve(0, 18, 6, 24)
pl.building(14, 4, 20, 14, "planks", south=(8,))      # библиотека
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
# сад и двор Ладоней: пальмы вдоль дорожки и вокруг библиотеки, кадки, скамьи, клумбы, колодец — «белый» оазис среди руин
for i, x in enumerate(range(4, 40, 5)):
    pl.maybe(VG_PALMS[i % 4], x, 18)
    pl.maybe(VG_PALMS[(i + 1) % 4], x + 2, 24)
for x, y in ((12, 3), (36, 3), (10, 9), (38, 9), (12, 15), (36, 15)):
    pl.maybe(VG_PALMS[(x + y) % 4], x, y)
for x, y in ((44, 20), (58, 20), (44, 40), (58, 40), (51, 26), (51, 38)):
    pl.maybe(VG_PALMS[(x + y) % 4], x, y)
for x in (8, 18, 28, 34):
    pl.maybe("bench_7", x, 25)
for x, y in ((16, 19), (30, 19), (10, 22), (36, 22)):
    pl.maybe(GARDEN[(x + y) % 2], x, y)
for x, y in ((48, 36), (52, 36), (56, 36), (47, 38), (55, 38)):
    pl.maybe(GARDEN[(x + y) % 2], x, y)
pl.maybe(WELL_V, 52, 31)
pl.maybe(WELL_V, 20, 33)
for x, y in ((10, 30), (28, 30), (10, 38), (28, 38), (16, 29), (24, 29)):
    pl.maybe(VG_PALMS[(x + y) % 4], x, y)
for x, y in ((14, 34), (18, 36), (22, 36), (26, 34)):
    pl.maybe("bench_7", x, y)
for x, y in ((8, 33), (32, 33), (20, 29), (20, 38)):
    pl.maybe(LAMPS[(x + y) % 2], x, y)
for x, y in ((12, 32), (30, 36), (24, 32)):
    pl.maybe(GARDEN[(x + y) % 2], x, y)
pl.maybe(STALLS[0], 12, 36)
pl.maybe(STALLS[1], 28, 33)
pl.maybe(TENT_WHITE, 55, 8)
pl.maybe(HOSP_BED, 57, 12)
pl.maybe(HOSP_BED, 57, 15)
pl.scatter(RUBBLE + ["r_trash"], 1, 28, 40, H - 2, 5)


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
tn.floor_code("M", *SW_FLOOR)
tn.floor_code("m", *SW_MOSS)
tn.floor_code("~", *SW_WATER)
tn.floor_code("k", *SW_PLANK)
tn.piers = ("k",)
tn.wall_code("K", "pk:zcity/zcity_w2_03")
tn.water_codes = ("~",)
# Планировка: три камеры — западный лагерь у лестницы, центральный зал-коллектор с протокой, восточная камера с лазом в башню.
# Протока идёт с севера на юг, в ней мостки; из камеры в камеру — арки у мостков.
tn.room(1, 1, 18, 29, "K", "M")
tn.room(18, 1, 34, 29, "K", "M")
tn.room(34, 1, 49, 29, "K", "M")
tn.opening(18, 6, 18, 11, "M")
tn.opening(18, 17, 18, 23, "M")
tn.opening(34, 6, 34, 11, "M")
tn.opening(34, 17, 34, 23, "M")
tn.paint("~", 24, 2, 28, 28)                          # проток коллектора
for y0 in (7, 19):
    tn.paint("k", 24, y0, 28, y0 + 2)                 # мостки
tn.blob("m", 8, 22, 5, 3)                             # мох в западной камере
tn.blob("m", 41, 8, 5, 3)
tn.blob("m", 21, 14, 2, 3)
tn.blob("m", 31, 25, 2, 3)
tn.props.append(["x_ladder", 4, 4])
tn.portal([(4, 4)], "vegas_snakes", (52, 37), "Наверх, к Змеям")
tn.reserve(2, 4, 8, 8)
tn.props.append(["x_ladder", 45, 25])
tn.portal([(45, 25)], "vegas_tower", (4, 26), "Подвал башни Vault-Tec")
tn.reserve(42, 23, 47, 27)
# центральный зал: коллектор с выпуском на севере, решётки, трубы, фонари на мостках
tn.maybe(SW_OUTLET, 25, 2)
tn.maybe(SW_GATE, 21, 2)
for y in (5, 11, 16, 24):
    tn.maybe(SW_LANTERN, 23, y)
    tn.maybe(SW_LANTERN, 29, y)
tn.maybe(SW_HEAP[0], 19, 13)
tn.maybe(SW_HEAP[1], 31, 12)
tn.maybe(SW_HEAP[2], 20, 23)
# западная камера: стоянка Змей — койки из бочек, ящики, костёр, мох, грибы
for x, y in ((4, 10), (6, 10), (10, 12), (12, 25), (15, 6)):
    tn.maybe(SW_BARREL, x, y)
for x, y in ((3, 14), (5, 14), (13, 14), (14, 22), (3, 26)):
    tn.maybe(SW_CRATE, x, y)
for x, y in ((9, 20), (11, 24), (7, 24), (14, 10)):
    tn.maybe(SW_MUSH[(x + y) % 3], x, y)
tn.maybe(SW_LANTERN, 9, 14)
tn.maybe(SW_LANTERN, 15, 24)
tn.maybe("campfire", 9, 6)
for x, y in ((6, 18), (12, 17)):
    tn.maybe(SW_SKULL, x, y)
# восточная камера: гнёзда мутантов и выход в башню
for x, y in ((38, 5), (44, 4), (38, 14), (46, 14), (37, 24), (40, 27)):
    tn.maybe(SW_HEAP[(x + y) % 3], x, y)
for x, y in ((41, 10), (43, 12), (36, 18), (45, 22)):
    tn.maybe(SW_MUSH[(x + y) % 3], x, y)
for x, y in ((37, 8), (47, 6), (47, 20)):
    tn.maybe(SW_SKULL, x, y)
tn.maybe(SW_LANTERN, 40, 22)
tn.maybe(SW_LANTERN, 38, 3)
tn.enemies += [["ratman", 21, 8], ["ratman", 31, 20], ["mommy_mutant", 42, 8], ["feral", 21, 24], ["feral", 12, 22]]
tn.scatter(["r_bones", "pile_cans"], 2, 3, 48, 28, 8)


# ================================================================ башня Vault-Tec
W, H = 40, 30
tw = CityMap(city, "vegas_tower", "Башня Vault-Tec", W, H, start=(18, 26), seed=228, interior=True, music="lab")
tw.floor_code("T", *MARBLE)
tw.floor_code("C", *CARPET)
tw.floor_code("P", *STEEL)
tw.wall_code("W", "pk:pmall/pmall_w3_10")
tw.room(1, 12, 39, 29, "W", "T")                      # холл — бежевый мрамор: так «Волт-Тек» принимал гостей
tw.room(1, 1, 22, 12, "W", "C")                       # архив — ковёр, стеллажи, рабочие места
tw.room(22, 1, 39, 12, "W", "P")                      # лифтовая шахта — сталь
tw.opening(18, 29, 19, 29, "T")
tw.portal([(18, 29), (19, 29)], "vegas_strip", (54, 13), "На Стрип")
tw.props.append(["x_ladder", 4, 27])
tw.portal([(4, 27)], "vegas_tunnels", (45, 26), "Вниз, в змеиные ходы")
tw.reserve(2, 26, 6, 28)
tw.opening(10, 12, 11, 14, "C")
tw.opening(30, 12, 31, 14, "P")
# холл: стойка по центру, зона ожидания с диванами и ковром, растения, логотип на стене, колонны из шкафов, обломки по углам
tw.put(RECEPTION, 16, 18)
tw.stamp("vg_lobby_rug", "pk:lhotel/p2/10,12,2,2", 15, 22, water=False)
tw.stamp("vg_lobby_rug_b", "pk:lhotel/p2/10,12,2,2", 27, 18, water=False)
for x, y in ((4, 17), (8, 17), (31, 17), (35, 17)):
    tw.maybe(SOFA_V, x, y)
for x, y in ((3, 14), (37, 14), (12, 27), (26, 27), (3, 22), (36, 24)):
    tw.maybe(PLANT_V[(x + y) % 2], x, y)
for x, y in ((14, 14), (20, 14), (26, 14)):
    tw.maybe(CHART_V, x, y)
for x, y in ((6, 16), (28, 22), (34, 16), (12, 24)):
    tw.put(DEBRIS, x, y)
for x in (22, 25, 28):
    tw.maybe(CHAIR_V, x, 19)
tw.maybe(COPIER_V, 36, 22)
tw.maybe(CABINETS, 33, 26)
tw.maybe(CABINETS, 35, 26)
# архив: стеллажи двумя рядами, рабочие места с лампами, доска, ксерокс
for i, x in enumerate((3, 5, 7, 9)):
    tw.put(CABINETS, x, 4)
for x in (11, 12, 20, 21):
    tw.maybe(CABINETS, x, 4)
tw.put(DESKS[0], 14, 6)
for x, y in ((4, 8), (8, 8), (16, 8), (20, 8)):
    tw.maybe(DESKS[(x // 4) % 2], x, y)
    tw.maybe(CHAIR_V, x + 1, y + 1)
tw.maybe(WHITEBOARD_V, 12, 2)
tw.maybe(COPIER_V, 3, 10)
tw.maybe(PLANT_V[0], 21, 10)
tw.terminal(18, 4, "tower_archive")
# лифтовая: консоли, генератор, сервер, жёлтые ограждения
tw.put(CONSOLES[0], 24, 4)
tw.put(SERVER, 36, 4)
tw.maybe(CONSOLES[1], 27, 4)
tw.maybe(SERVER, 34, 4)
tw.maybe(GEN_V, 35, 9)
tw.maybe(VRE_CRATE, 24, 10)
tw.maybe(VRE_CRATE, 36, 11)
tw.props.append(["x_ladder", 31, 7])
tw.portal([(31, 7)], "vegas_zero", (19, 26), "Лифтовая шахта — вниз, к «Нолю»",
          requires={"flag": "zero_power", "msg": "Лифт мёртв уже сорок четыре года. Нужно питание: электростанция Сапогов — или кто-то ещё."})
tw.reserve(29, 6, 33, 9)
tw.enemies += [["robot_guard", 30, 20], ["feral", 8, 22], ["feral", 34, 26]]


# ================================================================ хранилище «Ноль»: шлюз
W, H = 40, 30
zr = CityMap(city, "vegas_zero", "Хранилище «Ноль»", W, H, start=(19, 26), seed=229, interior=True, music="vats")
zr.floor_code("M", *STEEL)
zr.floor_code("G", *GRILLE)
zr.floor_code("S", *PLATES)
zr.wall_code("W", "pk:fstation/fstation_w1_10")
zr.room(1, 1, 39, 29, "W", "M")
zr.room(1, 11, 11, 21, "W", "S")                       # караулка у западной стены
zr.room(29, 11, 39, 21, "W", "S")                      # оружейная у восточной
zr.opening(11, 14, 11, 17, "S")
zr.opening(29, 14, 29, 17, "S")
zr.paint("G", 14, 8, 25, 22)                           # решётчатый настил шлюза — кабельные каналы под ногами
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
# караулка: койки, шкафчики, стол, стойка с картой; оружейная: стеллажи, ящики, стойки
for y in (13, 16, 19):
    zr.maybe(BUNK_V, 3, y)
for y in (14, 18):
    zr.maybe(LOCKERS_V[y % 2], 9, y)
zr.maybe("table_2", 6, 17)
zr.maybe("chair_0", 6, 19)
for y in (13, 15, 17, 19):
    zr.maybe(VRE_CRATE, 31, y)
    zr.maybe(VRE_CRATE, 36, y)
zr.maybe(GEN_V, 33, 12)
# шлюз: баррикады из мешков и ящики перед дверью, пульты охраны по бокам, лампы
for x, y in ((14, 24), (24, 24), (14, 9), (24, 9)):
    zr.maybe("x_sandbags", x, y)
for x, y in ((17, 22), (22, 22)):
    zr.maybe(CONSOLES[x % 2], x, y)
for x, y in ((13, 6), (26, 6), (13, 26), (26, 26)):
    zr.maybe(SERVER, x, y)
zr.enemies += [["turret", 6, 14], ["turret", 33, 14]]


# ================================================================ хранилище «Ноль»: внутри
W, H = 40, 30
vt = CityMap(city, "vegas_vault", "«Ноль»: хранилище", W, H, start=(19, 26), seed=230, interior=True, music="vats")
vt.floor_code("M", *STEEL)
vt.floor_code("G", *GRILLE)
vt.floor_code("S", *PLATES)
vt.wall_code("W", "pk:fstation/fstation_w1_08")
vt.room(1, 1, 39, 29, "W", "M")
vt.paint("G", 12, 14, 27, 20)                          # решётчатый настил вокруг капсул
vt.room(1, 22, 10, 29, "W", "S")                       # шкаф-кладовая образцов
vt.room(30, 22, 39, 29, "W", "S")                      # пост медиков
vt.opening(10, 24, 10, 27, "S")
vt.opening(30, 24, 30, 27, "S")
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
for y in (24, 26, 28):
    vt.maybe(LOCKERS_V[y % 2], 3, y)
    vt.maybe(LOCKERS_V[(y + 1) % 2], 7, y)
vt.maybe(BIOHAZ, 5, 23)
for x, y in ((32, 24), (36, 24), (33, 27), (37, 27)):
    vt.maybe(CONSOLES[(x + y) % 2], x, y)
vt.maybe(GEN_V, 35, 22)
for x, y in ((3, 14), (36, 14), (3, 18), (36, 18)):
    vt.maybe(VRE_CRATE, x, y)
for x, y in ((12, 12), (27, 12)):
    vt.maybe(SERVER, x, y)
for x, y in ((14, 22), (25, 22)):
    vt.maybe(TUBE_DEAD, x, y)
vt.npcs += [["cooper_zero", 26, 22]]


# пустыри обживаются сценками (экскурсия по городам показала голый песок)
print("обжито:", st.dress_empty([
    [("vg_rubble1", 0, 0), ("vg_debris", 2, 1), ("r_car_wreck", 0, 3), ("x_fire_barrel", 4, 1)],
    [("vg_lantern", 0, 0), ("r_tent_low", 1, 0), ("pile_cans", 3, 2), ("r_trash", 0, 2)],
    [("vg_rubble2", 0, 0), ("x_fire_barrel", 3, 1), ("r_bones", 2, 3), ("r_streetlamp", 5, 0)],
    [("by_wreck1", 0, 0), ("vg_debris", 3, 2), ("x_fire_barrel", 0, 2)],
    [("r_dumpster", 0, 0), ("pile_junk", 2, 0), ("x_fire_barrel", 4, 1), ("r_trash", 0, 2)],
    [("r_streetlamp", 0, 0), ("by_car_pile", 1, 1), ("pile_tires", 4, 1)],
], block=7, margin=1, chance=1.0))
print("обжито у Сапогов:", bt.dress_empty([
    [("r_army_truck", 0, 0), ("x_fire_barrel", 4, 2), ("pile_tires", 0, 2)],
    [("r_sandbag_row", 0, 0), ("r_sandbag_row", 2, 0), ("x_fire_barrel", 1, 2), ("r_barrels", 4, 1)],
    [("pile_scrap", 0, 0), ("pile_junk", 2, 0), ("r_streetlamp", 4, 0), ("crate", 0, 2)],
    [("r_tent_low", 0, 0), ("campfire", 2, 2), ("r_logs", 3, 2), ("barrel_wood", 0, 2)],
], block=7, margin=1, chance=1.0))

print("техзал zr:", zr.dress_empty(tech_scenes(city, "vg"), ground="M", block=7, margin=1, chance=1.0))
print("техзал vt:", vt.dress_empty(tech_scenes(city, "vg"), ground="M", block=7, margin=1, chance=1.0))

city.save(gap_exempt=("cooper_zero",))
L = json.load(open("data/locations.json", encoding="utf-8"))
L["vegas_strip"].update({"world_name": "Руины Вегаса", "discover": True})
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
