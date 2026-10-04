"""
Пятнадцатая, переработка: новые районы и уровни вокруг прежней карты (tools/build_town.py — центр
города со всеми квестами, его не трогаем). Сценарий — docs/story.md, раздел 6.

  fifteen_school         «Пятнадцатая: старая школа» — к востоку по трассе: школьный двор, баскетбольная
                         площадка, беговая дорожка, ржавый школьный автобус; через дорогу — разбитая
                         закусочная и машины 50-х. Старик Уолт, бывший школьный сторож, у ворот.
  fifteen_school_in      здание начальной школы «Солнечная долина»: коридор с ящиками, три класса,
                         библиотека (радтараканы), кабинет директора (терминал — дневник октября 2077),
                         спортзал (мисс Лейн, гуль-учительница, и её «класс»), кладовка.
  fifteen_cellar         подвал под домом деда: его личное убежище (люк открывается по записке в терминале).
  fifteen_saloon_cellar  подвал салуна: самогонный аппарат Мо и беглянка из культа Тесс.

Наборы: wasteland-school (wschool), 1950s American town (town50), nuclear bunker interior (nbunk).
Нарезка — tools/packs.py slice. Запуск из папки game_project:  .venv/bin/python tools/build_fifteen.py
"""
from citykit import City, CityMap
from mapkit import GRASS, BUSHES, STONES

city = City("fifteen", "Пятнадцатая")


def cells(page, pts):
    return [f"pk:{page}/{x},{y},1,1" for x, y in pts]


def P(name, img, **kw):
    city.prop(name, img, **kw)
    return name


# ------------------------------------------------------------ объекты наборов
DESK = P("ws_desk", "pk:wschool/wschool_2_000")
DESK_B = P("ws_desk_b", "pk:wschool/wschool_2_001")
DESK_PILE = P("ws_desk_pile", "pk:wschool/wschool_2_143")
DESK_PILE_B = P("ws_desk_pile_b", "pk:wschool/wschool_2_144")
TEACHER = P("ws_teacher_desk", "pk:wschool/wschool_2_080")
BOARD = P("ws_board", "pk:wschool/p1/8,8,4,2", foot=[4, 1], sight=True)
CORK = P("ws_cork", "pk:wschool/p1/12,8,4,2", foot=[4, 1], sight=True)
WINDOW = P("ws_window", "pk:wschool/p1/4,8,2,2", foot=[2, 1], sight=True)
LOCKER = P("ws_lockers", "pk:wschool/p1/6,12,2,2", foot=[2, 1], sight=True)
LOCKER_B = P("ws_lockers_b", "pk:wschool/p1/8,12,2,2", foot=[2, 1], sight=True)
SHELF = P("ws_bookshelf", "pk:wschool/wschool_3_021", sight=True)
SHELF_B = P("ws_bookshelf_b", "pk:wschool/wschool_3_054", sight=True)
SOFA = P("ws_sofa", "pk:wschool/wschool_3_010")
PLANT = P("ws_plant", "pk:wschool/wschool_3_041")
FILECAB = P("ws_filecab", "pk:wschool/wschool_3_000", search="drawer", title="картотека")
CABINET = P("ws_cabinet", "pk:wschool/wschool_3_033", search="shelf", title="шкаф")
MICRO = P("ws_microscope", "pk:wschool/wschool_3_038")
HOPE = P("ws_hope", "pk:wschool/p3/12,2,2,2", foot=[2, 1], sight=True)
EXIT_SIGN = P("ws_exit", "pk:wschool/p3/12,4,4,2", foot=[4, 1], sight=True)
TRASH = P("ws_trash", "pk:wschool/wschool_2_116", search="junk", title="мусорные баки")
BLEACH = P("ws_bleachers", "pk:wschool/wschool_4_009")
BLEACH_B = P("ws_bleachers_b", "pk:wschool/wschool_4_010")
HOOP = P("ws_hoop", "pk:wschool/wschool_4_005")
HOOP_B = P("ws_hoop_b", "pk:wschool/wschool_4_006")
GOAL = P("ws_goal", "pk:wschool/wschool_4_016")
FLOWERS = P("ws_flowerbed", "pk:wschool/wschool_4_027")
FENCE = P("ws_fence", "pk:wschool/wschool_4_037", sight=False)
BUS = P("ws_bus", "pk:wschool/wschool_4_042", sight=True, search="junk", title="школьный автобус")
JUNK = P("ws_junk", "pk:wschool/wschool_4_046", search="junk", title="куча хлама")
MAT = P("ws_mat", "pk:wschool/wschool_5_031", block=False, layer="floor")
COURT = "pk:wschool/p4/0,0,3,3"
TRACK = "pk:wschool/p4/9,0,3,3"
GYM_COURT = "pk:wschool/p5/0,3,3,5"

CARS = [P(f"t50_car{i}", f"pk:town50/town50_1_{n:03d}") for i, n in enumerate((29, 30, 37, 38, 45, 53))]
PHONE = P("t50_phone", "pk:town50/town50_1_100")
HYDRANT = P("t50_hydrant", "pk:town50/town50_1_108")
LAMP = P("t50_lamp", "pk:town50/town50_1_120")
MAILBOX = P("t50_mailbox", "pk:town50/town50_1_118")
DINER_SIGN = P("t50_diner_sign", "pk:town50/town50_1_116", sight=True)
PUMP = P("t50_pump", "pk:town50/town50_1_102")
BENCH = P("t50_bench", "pk:town50/town50_1_130")

BUNK = P("nb_bunk", "pk:nbunk/nbunk_2_000", sight=True)
CANS = P("nb_shelf_cans", "pk:nbunk/nbunk_2_004", sight=True, search="shelf", title="полка с консервами")
LOCKER_M = P("nb_locker", "pk:nbunk/nbunk_2_006", sight=True, search="locker", title="шкаф")
BENCH_W = P("nb_workbench", "pk:nbunk/nbunk_2_014")
DESK_PC = P("nb_desk_pc", "pk:nbunk/nbunk_2_016")
TANKS = P("nb_tanks", "pk:nbunk/nbunk_2_021", sight=True)
GEN = P("nb_generator", "pk:nbunk/nbunk_2_028")

TILE = cells("wschool/p1", [(0, 0), (1, 0), (2, 0), (1, 1), (2, 1), (0, 2), (3, 2), (1, 3), (2, 3), (1, 5), (2, 6)])
WOOD = cells("wschool/p5", [(1, 0), (2, 0), (1, 1), (2, 1), (0, 2), (1, 2)])
METAL = cells("nbunk/p2", [(4, 8), (5, 9), (6, 10), (4, 10)])


# ================================================================ двор школы
W, H = 64, 44
y_road = 29
out = CityMap(city, "fifteen_school", "Пятнадцатая: старая школа", W, H, start=(2, 30), seed=57, music="desert")
out.npcs += [["walt", 33, 25]]
out.enemies += [["radroach", 55, 22], ["radroach", 58, 24], ["radroach", 56, 26], ["radroach", 60, 21],
                ["rat", 10, 38], ["rat", 14, 40], ["mutant", 52, 39]]
for _, x, y in out.enemies + out.npcs:
    out.reserve(x, y, x, y)
out.paint("a", 0, y_road, W - 1, y_road + 3)
for x in range(0, W, 4):
    out.ground[y_road + 1][x] = out.ground[y_road + 1][x + 1] = "h"
out.paint("g", 0, y_road - 1, W - 1, y_road - 1)
out.paint("g", 0, y_road + 4, W - 1, y_road + 4)
out.paint("g", 29, 20, 32, y_road - 2)            # дорожка от ворот к дверям
out.reserve(0, y_road - 1, W - 1, y_road + 4)
out.reserve(29, 19, 32, y_road - 1)
out.portal([(0, y) for y in range(y_road, y_road + 4)], "ruins", (93, 31), "Пятнадцатая")

# здание школы: стены и крыша; внутри — отдельная карта
out.building(14, 6, 36, 14, "brick", south=(16,))
out.portal([(30, 19), (31, 19)], "fifteen_school_in", (43, 15), "Школа «Солнечная долина»")
for x in (20, 25, 36, 41):
    out.put(WINDOW, x, 19, force=True)        # окна — поверх кирпичного фасада

# двор: забор с воротами, площадка, беговая дорожка, трибуны, автобус
out.hwall([FENCE], 12, 52, 27, gaps=(29, 30, 31, 32))
out.stamp("court", COURT, 16, 21, water=False)
out.put(HOOP, 15, 22)
out.put(HOOP_B, 19, 22)
out.stamp("track", TRACK, 41, 21, water=False)
out.put(GOAL, 44, 24)
out.put(BLEACH, 24, 22)
out.put(BLEACH_B, 35, 24)
for x in (21, 25, 34, 38):              # клумбы вдоль фасада, по обе стороны от дорожки к дверям
    out.put(FLOWERS, x, 20)
out.put(BUS, 52, 21)
out.put(JUNK, 57, 26)
out.put(TRASH, 12, 21)

# через дорогу — разбитая закусочная, машины пятидесятых, телефонная будка
out.put("r_shanty_big", 24, 36)
out.put(DINER_SIGN, 33, 34)
out.put(PUMP, 40, 35)
out.put(PUMP, 43, 35)
out.put(PHONE, 18, 34)
out.put(HYDRANT, 14, 34)
out.put(MAILBOX, 47, 34)
out.put(BENCH, 8, 27)
for i, (x, y) in enumerate(((6, 33), (50, 33), (56, 28), (20, 28), (38, 28))):
    out.put(CARS[i % len(CARS)], x, y, allow_reserved=True)
for x in range(4, W - 2, 10):             # фонари по обочинам, в шахматном порядке
    out.put(LAMP, x, y_road - 1, allow_reserved=True)
    out.put(LAMP, x + 5, y_road + 4, allow_reserved=True)
out.box("crate", 30, 38, "ящик за закусочной", {"консервы": 2, "энергетический батончик": 1, "крышки": 12})
out.box("r_dumpster", 22, 41, "мусорный бак", {"пружина": 1, "изолента": 1})
for name, x, y in (("r_shack", 4, 38), ("r_cabin", 48, 40), ("r_shed_tin", 56, 38)):
    out.put(name, x, y)
out.grow(1, 1, W - 2, 5, 10, GRASS + BUSHES)
out.grow(1, 20, 12, 27, 4, GRASS)
out.grow(1, 34, W - 2, H - 2, 14, GRASS + BUSHES)
out.scatter(STONES + ["r_rocks", "r_trash"], 1, 1, W - 2, H - 2, 14)
for x, y in ((4, 3), (9, 4), (58, 4), (61, 12), (6, 15)):
    out.put("dead_tree", x, y)


# ================================================================ здание школы
W, H = 46, 30
sin = CityMap(city, "fifteen_school_in", "Школа «Солнечная долина»", W, H, start=(43, 15), seed=58,
              interior=True, music="caves")
sin.floor_code("F", *TILE)
sin.floor_code("G", *WOOD)
sin.wall_code("W", "pk:nbunk/nbunk_w3_13")      # школьная стена: кремовая с бирюзовой полосой
sin.wall_code("V", "pk:nbunk/nbunk_w3_04")      # деревянные панели спортзала
sin.wall_code("O", "pk:nbunk/nbunk_w3_23")      # кабинет директора
A = sin.room(1, 1, 12, 11, "W", "F")
B = sin.room(12, 1, 23, 11, "W", "F")
C = sin.room(23, 1, 34, 11, "W", "F")
LIB = sin.room(34, 1, 45, 11, "W", "G")
HALL = sin.room(1, 11, 45, 17, "W", "F")
OFF = sin.room(1, 17, 12, 28, "O", "G")
GYM = sin.room(12, 17, 34, 28, "V", "G")
ST = sin.room(34, 17, 45, 28, "W", "F")
for x in (6, 17, 28, 39):
    sin.opening(x, 11, x + 1, 13, "F")
for x in (6, 22, 39):
    sin.opening(x, 17, x + 1, 19, "F")
sin.opening(45, 14, 45, 15, "F")
sin.portal([(45, 14), (45, 15)], "fifteen_school", (30, 20), "Школьный двор")
sin.reserve(42, 14, 44, 16)

sin.npcs += [["miss_lane", 23, 24], ["ghoul_kid_a", 20, 25], ["ghoul_kid_b", 26, 25], ["ghoul_kid_c", 23, 26]]
sin.enemies += [["radroach", 37, 6], ["radroach", 41, 8], ["radroach", 43, 5], ["rat", 37, 24], ["rat", 42, 26]]

# класс А — как в последний день: доска, парты рядами
sin.put(BOARD, 4, 3, check=False)
sin.put(TEACHER, 9, 4)
for y in (6, 8):
    for x in (3, 5, 7):
        sin.put(DESK, x, y)
# класс Б — разгромлен
sin.put(WINDOW, 14, 3, check=False)
sin.put(WINDOW, 20, 3, check=False)
sin.put(DESK_PILE, 14, 6)
sin.put(DESK_PILE_B, 18, 8)
sin.put(DESK_B, 20, 5)
# класс В — рисунки детей на пробковой доске
sin.put(CORK, 26, 3, check=False)
sin.terminals.append({"prop": len(sin.props) - 1, "id": "doc:doc_kids_drawings"})
for y in (6, 8):
    for x in (25, 28, 31):
        sin.put(DESK, x, y)
sin.put(MICRO, 32, 4)
# библиотека
for x in (35, 37, 42):
    sin.put(SHELF if x != 37 else SHELF_B, x, 4)
sin.put(SOFA, 38, 8)
sin.put(PLANT, 43, 9)
sin.box(CABINET, 40, 4, "библиотечный шкаф", {"консервы": 1, "батарейки": 1, "спички": 1})
# коридор
for x in (9, 14, 20, 25, 33, 36):
    sin.put(LOCKER if x % 2 else LOCKER_B, x, 14)
sin.put(HOPE, 30, 13, check=False)           # на стене коридора (фасад — ряды 12–13)
sin.put(EXIT_SIGN, 41, 13, check=False)      # у выхода: дверь EXIT и доска SCHOOL
sin.put(TRASH, 3, 16)
# кабинет директора
sin.terminal(3, 20, "school_office")
sin.box(FILECAB, 9, 20, "картотека директора", {"крышки": 25, "ключ-карта школы": 1})
sin.put(TEACHER, 6, 22)             # стол директора — лицом к двери
sin.put(PLANT, 10, 26)
# спортзал: разметка, маты, трибуны
sin.stamp("gym_court", GYM_COURT, 22, 21, water=False)
sin.put(BLEACH, 13, 20)
sin.put(BLEACH_B, 28, 20)
sin.put(MAT, 15, 25)
sin.put(MAT, 30, 25)
# кладовка
# кладовка: стеллажи и ящики вдоль стен, проход от двери свободен
sin.put(SHELF_B, 35, 20)
sin.box("crate", 37, 20, "ящик со списанными учебниками", {"ткань": 2, "спички": 1})
sin.box("metal_box_open", 43, 20, "ящик завхоза", {"изолента": 2, "гаечный ключ": 1, "фонарик": 1},
        requires={"item": "ключ-карта школы", "msg": "Железный ящик с табличкой «ЗАВХОЗ». Замок с прорезью для карты."})
sin.put("barrel_wood", 35, 26)
sin.put("crate_b", 36, 26)
sin.put("barrel_wood", 43, 26)


# ================================================================ подвал деда
cel = CityMap(city, "fifteen_cellar", "Подвал деда", 16, 12, start=(3, 5), seed=59, interior=True, music="lab")
cel.floor_code("M", *METAL)
cel.wall_code("K", "pk:nbunk/nbunk_w1_12")
cel.room(1, 1, 14, 10, "K", "M")
cel.props.append(["x_ladder", 3, 4])
cel.portal([(3, 4)], "ruins", (8, 18), "Наверх, в дом")          # люк — (9, 19), выход рядом
cel.terminal(6, 4, "amos_cellar")
cel.put(CANS, 8, 4, check=False)
cel.put(BUNK, 11, 4, check=False)
cel.put(BENCH_W, 2, 8)
cel.put(GEN, 6, 8)
cel.put(TANKS, 11, 8)
cel.box("metal_chest", 13, 6, "армейский сундук деда",
        {"армейский бронежилет": 1, "патроны": 20, "стимулятор": 2, "фотография": 1})


# ================================================================ подвал салуна
sal = CityMap(city, "fifteen_saloon_cellar", "Подвал салуна", 16, 12, start=(3, 5), seed=60, interior=True,
              music="caves")
sal.floor_code("G", *WOOD)
sal.wall_code("D", "pk:nbunk/nbunk_w1_00")
sal.room(1, 1, 14, 10, "D", "G")
sal.props.append(["x_ladder", 3, 4])
sal.portal([(3, 4)], "ruins", (21, 18), "Наверх, в салун")       # люк — (20, 18)
sal.npcs += [["tess", 11, 8]]
for x in (6, 7, 8):
    sal.put("barrel_wood", x, 4)
sal.put(GEN, 5, 8)                  # «аппарат» — котёл и змеевик
sal.put("bed", 12, 5)
sal.put("candles", 10, 6)
sal.box("cabinet_small", 13, 8, "тайник Мо", {"самогон": 3, "крышки": 60, "сигареты": 2})
sal.box("crate", 2, 8, "ящик с бутылками", {"самогон": 2, "спички": 1})

city.save(gap_exempt=("walt",))
