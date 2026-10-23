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
GOAL_BROKEN = P("ws_goal_broken", "pk:wschool/p4/3,6,3,2", foot=[3, 1])
PULLUP = P("ws_pullup", "pk:wschool/p4/4,8,4,2", foot=[4, 1])
SWINGS = P("ws_swings", "pk:wschool/p4/0,10,2,2", foot=[2, 1])
MONKEY = P("ws_monkey_bars", "pk:wschool/p4/2,10,2,2", foot=[2, 1])
WEIGHTS = P("ws_weights", "pk:wschool/p4/10,6,2,2", foot=[2, 1])
BARBELL = P("ws_barbell", "pk:wschool/p4/12,6,2,2", foot=[2, 1])
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
out.floors = getattr(out, "floors", {})
out.floor_code("t", "pk:desnat/p1/4,4,1,1", "pk:desnat/p1/5,4,1,1", "pk:desnat/p1/6,4,1,1")
out.floor_code("q", "pk:desnat/p1/10,4,1,1")
out.floor_code("s", "pk:desnat/p1/0,0,1,1", "pk:desnat/p1/1,0,1,1", "pk:desnat/p1/0,1,1,1")
out.paint("s", 0, 0, W - 1, H - 1)
out.patchwork("s", ["t"], 70, 2, 5, seed=21)
out.patchwork("s", ["q"], 30, 1, 3, seed=22)
out.paint("a", 0, y_road, W - 1, y_road + 3)
for x in range(0, W, 4):
    out.ground[y_road + 1][x] = out.ground[y_road + 1][x + 1] = "h"
out.paint("g", 0, y_road - 1, W - 1, y_road - 1)
out.paint("g", 0, y_road + 4, W - 1, y_road + 4)
out.paint("g", 29, 20, 32, y_road - 2)            # дорожка от ворот к дверям
out.reserve(0, y_road - 1, W - 1, y_road + 4)
out.reserve(29, 19, 32, y_road - 1)
out.portal([(0, y) for y in range(y_road, y_road + 4)], "ruins", (147, 49), "Пятнадцатая")

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
# футбольное поле на утоптанной земле: ворота друг напротив друга, рядом — турники и «качалка» физрука
out.put(GOAL, 40, 22)
out.put(GOAL_BROKEN, 47, 24)
out.put(PULLUP, 3, 25)
out.put(WEIGHTS, 47, 20)
out.put(BARBELL, 49, 21)
out.put(SWINGS, 5, 21)
out.put(MONKEY, 8, 21)
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
out.grow(1, 1, W - 2, 5, 16, GRASS + BUSHES)
out.grow(1, 20, 12, 27, 4, GRASS)
out.grow(1, 34, W - 2, H - 2, 14, GRASS + BUSHES)
out.scatter(STONES + ["r_rocks", "r_trash"], 1, 1, W - 2, H - 2, 14)
print("обжито out:", out.dress_empty([
    [("r_tent_beige", 0, 0), ("campfire", 3, 2), ("r_logs", 2, 3), ("barrel_wood", 0, 3)],
    [("r_car_wreck", 0, 0), ("pile_tires", 3, 2), ("r_trash", 0, 3)],
    [("r_pickup", 0, 0), ("r_barrels", 3, 0), ("pile_scrap", 2, 3)],
    [("r_dumpster", 0, 0), ("pile_cans", 2, 0), ("r_trash", 0, 2), ("crate_broken", 3, 2)],
    [("x_cross", 0, 0), ("x_grave", 0, 1), ("x_cross", 2, 0), ("r_dtree_a", 4, 1)],
    [("r_billboard", 0, 0), ("r_dtree_a", 2, 1), ("r_bones", 3, 2), ("r_rocks", 4, 2)],
    [("r_shack", 0, 0), ("pile_junk", 5, 1), ("x_fire_barrel", 3, 3)],
], ground=("s", "t", "q"), block=7, margin=1, chance=0.9, max_uses=2))
for x, y in ((4, 3), (9, 4), (58, 4), (61, 12), (6, 15)):
    out.put("dead_tree", x, y)


# ================================================================ здание школы
# Расстановка поштучная (docs/furnish/fifteen.md §8): автообстановка выключена, каждый предмет — по смыслу
# комнаты. Правило взгляда (logic.md §2а): ученик сидит южнее своей парты (стул спинкой к камере) — лицом
# к доске на северной стене; учитель за столом у доски лицом в класс; посетитель перед столом хозяина.
W, H = 46, 30
sin = CityMap(city, "fifteen_school_in", "Школа «Солнечная долина»", W, H, start=(43, 15), seed=58,
              interior=True, music="caves", furnish=False)
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

sin.npcs += [["miss_lane", 23, 23], ["ghoul_kid_a", 21, 25], ["ghoul_kid_b", 25, 25], ["ghoul_kid_c", 23, 25]]
sin.enemies += [["radroach", 37, 6], ["radroach", 41, 8], ["radroach", 43, 5], ["rat", 37, 24], ["rat", 42, 26]]
for _, x, y in sin.npcs + sin.enemies:      # места жителей и врагов — не для мебели
    sin.reserve(x, y, x, y)


# ------------------------------------------------------------ мебель и мелочь школы (набор wschool)
# У столов и шкафов картинка выше клетки: пятно задаётся явно, иначе спрайт налезает на соседа.
CHAIR = P("ws_chair", "pk:wschool/wschool_3_062")                     # стул спинкой к камере: сидящий смотрит на доску
CHAIR_F = P("ws_chair_f", "pk:wschool/wschool_2_089")                 # стул лицом к камере: посетитель перед столом
CHAIR_L = P("ws_chair_l", "pk:wschool/wschool_2_088")                 # стул в профиль, лицом влево
CHAIR_R = P("ws_chair_r", "pk:wschool/wschool_2_086")                 # стул в профиль, лицом вправо
DESK2 = P("ws_school_desk", "pk:wschool/wschool_2_094")               # ученическая парта
TEACHER2 = P("ws_teacher_desk2", "pk:wschool/wschool_2_083", foot=[2, 2])   # стол учителя: кресло позади, лицом к классу
TABLE = P("ws_table", "pk:wschool/wschool_3_011", foot=[2, 1])        # деревянный стол 2×1
BENCH = P("ws_bench", "pk:wschool/wschool_2_064", foot=[2, 1])        # скамья со спинкой 2×1
CLOCK = P("ws_clock", "pk:wschool/wschool_3_043", foot=[1, 1], block=False)
MAP_W = P("ws_wallmap", "pk:wschool/wschool_3_065", block=False)       # карта страны на стене
POSTER = P("ws_poster", "pk:wschool/wschool_3_067", block=False)       # старая афиша
PIC = P("ws_pic", "pk:wschool/wschool_3_119", block=False)             # картина в раме
CORK_BIG = P("ws_cork_big", "pk:wschool/wschool_3_025", foot=[2, 1], block=False, sight=True)
WINDOW_BROKEN = P("ws_window_broken", "pk:wschool/wschool_3_027", foot=[2, 1], block=False, sight=True)  # выбитая рама
CAB2 = P("ws_cabinet_open", "pk:wschool/wschool_3_033", foot=[2, 2], sight=True)   # шкаф с открытыми ящиками
FILE2 = P("ws_filecab2", "pk:wschool/wschool_3_072", sight=True)      # картотека
BIN = P("ws_bin", "pk:wschool/wschool_3_107")                         # урна
BROOM = P("ws_broom", "pk:wschool/wschool_2_072")                     # швабра
BALL = P("ws_ball", "pk:wschool/wschool_4_021")                       # мяч
PACK = P("ws_backpack", "pk:wschool/wschool_3_048")                   # рюкзак
BOOK_OPEN = P("ws_book_open", "pk:wschool/wschool_3_102", block=False)      # открытая тетрадь
BOOKS = P("ws_books", "pk:wschool/wschool_3_018")                     # стопка книг
FOLDERS = P("ws_folders", "pk:wschool/wschool_3_014", block=False)    # папки
PAPERS = P("ws_papers", "pk:wschool/wschool_2_092", block=False, layer="floor")
GLASS = P("ws_glass", "pk:wschool/wschool_2_045", block=False, layer="floor")
CHAIR_DOWN = P("ws_chair_down", "pk:wschool/wschool_3_127")
DESK_TILT = P("ws_desk_tilt", "pk:wschool/wschool_2_014")
DESK_TOP = P("ws_desk_top", "pk:wschool/wschool_2_015", block=False, layer="floor")
PILE = P("ws_desk_pile2", "pk:wschool/wschool_2_143", foot=[2, 2])
PILE_B = P("ws_desk_pile2_b", "pk:wschool/wschool_2_144", foot=[2, 2])
DEBRIS = P("ws_debris", "pk:wschool/wschool_2_124")
CRAYONS = P("ws_crayons", "pk:wschool/wschool_2_050", block=False)
PENCIL = P("ws_pencil", "pk:wschool/wschool_2_061", block=False)
CHALK = P("ws_chalk", "pk:wschool/wschool_3_108", block=False)
FERN = P("ws_fern", "pk:wschool/wschool_3_031")
EASEL = "x_easel"
KIDS_DRAWINGS = "x_kids_drawings"     # детский рисунок на стене — свой проп из data/props.json


def swhy(name, x, y):
    """Почему предмет не встал — как why_not() в build_town.py."""
    foot = sin.footprint(name, x, y)
    why = []
    if any(t in sin.blocked for t in foot):
        why.append("блок: " + str([t for t in foot if t in sin.blocked]))
    if any(t in sin.soft_obj for t in foot):
        why.append("мягкий предмет: " + str([t for t in foot if t in sin.soft_obj]))
    if any(t in sin.reserved for t in foot):
        why.append("резерв")
    h = sin.hides(name, x, y)
    if h:
        why.append(f"заслоняет {h[0]} ({h[1]}, {h[2]})")
    why.append("земля: " + "".join(sin.ground[yy][xx] for xx, yy in foot))
    return f"«{name}» не встал в ({x}, {y}): " + "; ".join(why)


def splace(name, x, y, **kw):
    """Явная расстановка: предмет обязан встать — молча потерянная мебель и была дефектом (logic.md §2).
    Встал, но не туда (citykit сдвигает выросшую декорацию) — тоже дефект: место выбрано по смыслу."""
    try:
        ok = sin.put(name, x, y, **kw)
    except AssertionError:
        raise AssertionError(swhy(name, x, y)) from None
    if ok and sin.props[-1][1:3] == [x, y]:
        return True
    raise AssertionError(swhy(name, x, y) + f"; встал в ({sin.props[-1][1]}, {sin.props[-1][2]})")


def sbox(name, x, y, *a, **kw):
    """Ящик с добычей — как splace(): не встал — объяснить почему."""
    try:
        return sin.box(name, x, y, *a, **kw)
    except AssertionError:
        raise AssertionError(swhy(name, x, y)) from None


def swall(name, x, y, dx=0, dy=-26):
    """Настенное (доска, карта, часы, портрет): ставится на клетки стены-кода и поднимается так, чтобы низ
    картинки был на стене. Выше — только если под ним высокая мебель (иначе аудит «стена»)."""
    fw, fh = props_info(name)["foot"]
    cells = [(x + i, y + j) for i in range(fw) for j in range(fh)]
    assert all(sin.ground[cy][cx] in sin.walls for cx, cy in cells), \
        f"«{name}» в ({x}, {y}): там нет стены — {' '.join(sin.ground[cy][cx] for cx, cy in cells)}"
    sin.props.append([name, x, y, dx, dy])
    sin.blocked.update(cells)              # клетка стены занята: автосвет не повесит плафон на доску
    sin._reach = None


def s_piece(name, x, y):
    """Кусок страницы набора (доска, окно, шкафчики, плакат): спрайт уже включает полосу стены, поэтому
    ставится на клетки стены без сдвига — как ставил put(check=False) до ручной расстановки."""
    fw, fh = props_info(name)["foot"]
    cells = [(x + i, y + j) for i in range(fw) for j in range(fh)]
    assert all(sin.ground[cy][cx] in sin.walls for cx, cy in cells), \
        f"«{name}» в ({x}, {y}): там нет стены — {' '.join(sin.ground[cy][cx] for cx, cy in cells)}"
    sin.props.append([name, x, y])
    sin.blocked.update(cells)              # клетка стены занята: автосвет не повесит плафон на доску
    sin._reach = None


def s_table(name, x, y, dx=0, dy=-20):
    """Мелочь на столешнице: на клетке стола, поднята на его высоту, рисуется сразу после стола
    (6-й элемент — поправка порядка отрисовки, src/townmap.py)."""
    assert (x, y) in sin.blocked, f"«{name}» в ({x}, {y}): под ним нет стола"
    sin.props.append([name, x, y, dx, dy, 1 - dy])


from src import props as _school_props  # noqa: E402


def props_info(name):
    return _school_props.info(name)


# ------------------------------------------------------------ класс А — «как в последний день»
# 2-й класс, урок шёл до сирены. Порядок: доска и карта на северной стене, стол учителя под доской лицом
# к классу, два ряда парт лицом к доске (стул каждой — южнее парты), у стен — полка с учебниками и шкаф.
s_piece(BOARD, 4, 3)                   # доска на 4 клетки стены
swall(MAP_W, 9, 3)                     # карта страны справа от доски
swall(CLOCK, 3, 3)                     # часы у входа, рядом с доской
splace(TEACHER2, 5, 4)                 # стол учителя 2×2: кресло севернее, лицом к партам
s_table(FOLDERS, 5, 5, dy=-26)         # раскрытый классный журнал
s_table(CHALK, 6, 5, dx=10, dy=-26)    # мел на столе
splace(FILE2, 2, 4)                    # шкаф с наглядными пособиями у западной стены
splace(SHELF, 11, 4)                   # полка с учебниками у восточной
for y in (6, 8):                       # парты рядами лицом к доске: два блока по две парты, между ними проход
    for x in (2, 4, 8, 10):
        splace(DESK2, x, y)
        splace(CHAIR, x, y + 1)
s_table(BOOK_OPEN, 2, 6)               # открытая тетрадь — урок прервался
s_table(BOOK_OPEN, 8, 8, dx=-8)
s_table(PENCIL, 4, 6, dy=-20)
s_table(PACK, 10, 8, dy=-26)           # ранец на парте: за ним никто не вернулся
splace(FERN, 2, 10)                    # растение в юго-западном углу
splace(BIN, 8, 10)                     # урна у двери

# ------------------------------------------------------------ класс Б — разгромлен
# Здесь пытались закрыться: парты и шкафчик сворочены к стенам, у двери — баррикада из парт,
# под выбитым окном стекло, по полу рассыпаны тетради.
s_piece(WINDOW, 14, 3)                 # целое окно
s_piece(BOARD, 16, 3)                  # доска между окнами
swall(WINDOW_BROKEN, 20, 3)            # выбитая рама
splace(GLASS, 14, 4)                   # стекло под окном
splace(GLASS, 15, 4)
splace(PAPERS, 16, 4)                  # бумаги с доски
splace(DESK2, 13, 5)                   # парты, сдвинутые к западной стене
splace(CHAIR_R, 13, 6)
splace(DESK2, 13, 8)
splace(CHAIR_R, 13, 9)
splace(DESK_TOP, 17, 5)                # перевёрнутая столешница
splace(PAPERS, 19, 6)
splace(LOCKER_B, 21, 6)                # шкафчик сворочён к восточной стене
splace(PILE, 16, 7)                    # баррикада: куча парт у двери
splace(PILE_B, 19, 8)
splace(DESK_TILT, 15, 9)
splace(CHAIR_DOWN, 21, 9)
splace(CHAIR_DOWN, 15, 10)

# ------------------------------------------------------------ класс В — «Моё будущее»
# Младшие рисовали 22.10 «своё будущее»: рисунки на пробковой доске (сюжетный терминал) и рядом на стене,
# стол учителя под доской лицом к партам (кресло севернее — как в классе А), поделки — на этом столе,
# парты рядами лицом к доске.
swall(KIDS_DRAWINGS, 24, 3, dy=-36)    # детский рисунок на стене, выше микроскопа
s_piece(CORK, 26, 3)                   # пробковая доска с рисунками
sin.terminals.append({"prop": len(sin.props) - 1, "id": "doc:doc_kids_drawings"})
swall(KIDS_DRAWINGS, 32, 3, dx=8)       # второй рисунок — со сдвигом, чтобы не читался копией
splace(TEACHER2, 27, 4)                # стол учителя под доской (2×2): кресло севернее, лицом к классу
s_table(FOLDERS, 27, 5, dy=-26)        # папка с рисунками учителя
s_table(CRAYONS, 28, 5, dx=10, dy=-26)  # детские поделки — на столе учителя
splace(MICRO, 24, 4)                   # микроскоп в «уголке природы»
splace(SHELF, 33, 4)                   # полка с красками и пластилином
for y in (6, 8):
    for x in (25, 27, 30, 32):
        splace(DESK2, x, y)
        splace(CHAIR, x, y + 1)
s_table(PACK, 32, 8, dy=-26)           # ранец на парте
s_table(CRAYONS, 27, 6, dy=-20)        # мелки на парте — урок прервался
splace(BIN, 33, 10)

# ------------------------------------------------------------ библиотека
# Стеллажи вдоль северной стены, стол для чтения посередине, диван в углу; под стеллажами — радтараканы.
swall(MAP_W, 36, 3, dy=-48)            # карта над стеллажами — выше полок
swall(PIC, 43, 3, dy=-48)              # картина в раме
splace(SHELF, 35, 4)
splace(SHELF, 36, 4)
splace(SHELF_B, 37, 4)                 # 2 клетки: 37..38
sbox(CABINET, 40, 4, "библиотечный шкаф", {"консервы": 1, "батарейки": 1, "спички": 1})
splace(SHELF_B, 42, 4)                 # 42..43
splace(SHELF, 44, 4)
splace(TABLE, 37, 8)                   # стол для чтения
splace(CHAIR_F, 37, 7)                 # читатели лицом к столу
splace(CHAIR_F, 38, 7)
splace(CHAIR, 37, 9)                   # с другой стороны — спиной к камере
splace(CHAIR, 38, 9)
s_table(BOOK_OPEN, 37, 8, dy=-24)      # открытая книга на столе
s_table(PENCIL, 38, 8, dx=8, dy=-24)
splace(BOOKS, 36, 6)                   # книги на полу под стеллажом
splace(DEBRIS, 41, 6)                  # гнездо радтараканов
splace(SOFA, 43, 9)                    # диван в углу
splace(FERN, 35, 10)

# ------------------------------------------------------------ коридор
# Перемена 23.10.2077: шкафчики вдоль северной стены между дверями, объявления и часы на стене,
# скамьи у южной стены — здесь ждали автобус.
for x, kind in ((9, LOCKER), (14, LOCKER_B), (22, LOCKER), (24, LOCKER_B), (26, LOCKER),
                (33, LOCKER_B), (35, LOCKER), (37, LOCKER_B)):
    splace(kind, x, 14)
swall(CORK_BIG, 11, 13)                # доска объявлений — над промежутком между шкафчиками
swall(CLOCK, 19, 13)                   # часы
s_piece(HOPE, 30, 13)                  # «HOPE?» — плакат у спортзала
s_piece(EXIT_SIGN, 41, 13)             # «EXIT / SCHOOL» у выхода на двор
splace(TRASH, 4, 16)                   # баки (обыскиваются)
splace(FERN, 19, 16)                   # растение у южной стены коридора (западный закуток — проём по аудиту)
splace(BENCH, 12, 16)                  # скамья у южной стены
splace(BENCH, 26, 16)

# ------------------------------------------------------------ кабинет директора
# Х. Лейн, и. о. директора: терминал и картотеки — вдоль северной стены, портрет и часы на стене.
# Стол директора придвинут к северу: хозяйка за ним (кресло севернее стола, лицом в комнату — logic.md §2а),
# перед столом коврик, дальше стул посетителя лицом к директору. Дверь (6..7 по северной стене) — сбоку,
# не за спиной. Проход к терминалу и к картотеке с ключ-картой свободен.
swall(PIC, 4, 19)                      # портрет над терминалом
swall(CLOCK, 9, 19)                    # часы
sin.terminal(3, 20, "school_office")
splace(FILECAB, 2, 20)                 # картотека у терминала
splace(FILE2, 5, 20)                   # картотека с делами (второй ящик — в библиотеке)
sbox(FILECAB, 9, 20, "картотека директора", {"крышки": 25, "ключ-карта школы": 1})
splace(SHELF, 10, 20)                  # шкаф с папками
splace(CHAIR_F, 8, 21)                 # кресло директора за столом, лицом в комнату
splace(TABLE, 8, 22)                   # стол директора 2×1, ближе к северу
s_table(PENCIL, 8, 22, dx=-8, dy=-24)
s_table(FOLDERS, 9, 22, dx=8, dy=-24)  # папки с делами — справа, чтобы не заслонять кресло
splace("x_carpet", 8, 23)              # коврик перед столом — сюда подходят посетители
splace(CHAIR, 8, 24)                   # стул посетителя лицом к директору, через коврик
splace(SHELF, 2, 27)                   # шкаф с папками у южной стены
splace(FERN, 10, 26)
splace(BIN, 11, 27)

# ------------------------------------------------------------ спортзал
# Мисс Лейн заперла здесь детей: разметка площадки, трибуны вдоль южной стены, шведская стенка и канат
# на стене. В середине — её «класс»: доска на подставке, она лицом к детям, три парты и трое детей.
# Северо-запад пустой: перед шведской стенкой нужно место. Скамьи запасных — вдоль южной стены лицом
# в зал, по краям трибун.
swall("x_wallbars", 15, 19, dy=0)      # шведская стенка от пола
swall("x_wallbars", 16, 19, dy=0)
swall("x_climb_rope", 31, 19, dy=0)    # канат
splace(CAB2, 24, 20)                   # инвентарный шкаф справа от двери
splace(MAT, 15, 24)                    # маты у стены
splace(MAT, 30, 24)
splace("x_easel", 23, 22)              # доска на подставке — «урок» мисс Лейн
splace(DESK2, 21, 24)                  # три парты её класса
splace(DESK2, 23, 24)
splace(DESK2, 25, 24)
splace(PACK, 19, 26)                   # рюкзаки у трибуны — их так и не забрали
splace(PACK, 20, 26)
splace(BALL, 18, 27)
splace(BALL, 27, 26)
splace(BLEACH, 14, 27)                 # трибуны вдоль южной стены
splace(BLEACH_B, 28, 27)
splace(BENCH, 19, 27)                  # скамьи запасных — у трибун, лицом в зал
splace(BENCH, 32, 27)

# ------------------------------------------------------------ кладовка
# Школьный инвентарь: стеллажи (след 2×1) вдоль северной и восточной стен, штабели ящиков в юго-западном
# углу, бочки — в юго-восточном, сломанные парты — стопкой у западной стены, швабра с ведром у двери.
# Ящик завхоза под ключ-карту — у северной стены в северо-восточном углу; проход от двери к нему свободен.
splace(SHELF_B, 35, 20)                # северная стена: стеллажи 35..38
splace(SHELF_B, 37, 20)
sbox("crate", 35, 21, "ящик со списанными учебниками", {"ткань": 2, "спички": 1})
splace("crate_b", 35, 22)              # штабель ящиков под стеллажами
splace("crate", 36, 22)
splace(PILE, 35, 24)                   # сломанные парты стопкой у западной стены (35..36, 24..25)
splace("crate", 35, 26)                # штабель ящиков в юго-западном углу
splace("crate_b", 35, 27)
splace("bucket", 41, 21)               # ведро и швабра — сразу у двери
splace(BROOM, 42, 21)
splace(SHELF_B, 43, 22)                # восточная стена: стеллажи 43..44
splace(SHELF_B, 43, 24)
splace(SHELF, 44, 20)                  # стеллаж в северо-восточном углу
sbox("metal_box_open", 43, 20, "ящик завхоза", {"изолента": 2, "гаечный ключ": 1, "фонарик": 1},
     requires={"item": "ключ-карта школы", "msg": "Железный ящик с табличкой «ЗАВХОЗ». Замок с прорезью для карты."})
splace("barrel_wood", 43, 26)          # бочки и ящики в юго-восточном углу
splace("barrel_wood", 44, 26)
splace("crate_b", 44, 27)
splace(TRASH, 37, 27)                  # баки у южной стены




# ================================================================ подвал деда
cel = CityMap(city, "fifteen_cellar", "Подвал деда", 16, 12, start=(3, 5), seed=59, interior=True, music="lab")
cel.floor_code("M", *METAL)
cel.wall_code("K", "pk:nbunk/nbunk_w1_12")
cel.room(1, 1, 14, 10, "K", "M")
cel.props.append(["x_ladder", 3, 4])
cel.portal([(3, 4)], "ruins", (7, 32), "Наверх, в дом")          # люк — (7, 33), выход рядом
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
sal.portal([(3, 4)], "ruins", (53, 27), "Наверх, в салун")       # люк — (52, 27), за стойкой
sal.npcs += [["tess", 11, 8]]
for x in (6, 7, 8):
    sal.put("barrel_wood", x, 4)
sal.put(GEN, 5, 8)                  # «аппарат» — котёл и змеевик
sal.put("bed", 12, 5)
sal.put("candles", 10, 6)
sal.box("cabinet_small", 13, 8, "тайник Мо", {"самогон": 3, "крышки": 60, "сигареты": 2})
sal.box("crate", 2, 8, "ящик с бутылками", {"самогон": 2, "спички": 1})

city.save(gap_exempt=("walt",))
