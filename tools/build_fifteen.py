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
# «Солнечная долина», школьный двор. Уличная карта — значит ×1.56 по каждой стороне от прежних 64×44
# (docs/furnish_guide.md «Масштаб»): 100×70. Автообстановка выключена, всё поставлено поштучно.
# Планировка (logic.md §1: сначала планировка, потом мебель), с юга на север:
#   трасса с переходом в Пятнадцатую (x=0) → ограда с калиткой → двор;
#   запад двора — огород с дорожкой, грядками и пересохшим колодцем, центр — баскетбольная площадка
#   у корпуса и детская площадка восточнее оси, восток — спортивный угол и футбольное поле;
#   за корпусом — задворки: ржавый школьный автобус, хлам, баки, сарай.
# Корпус под целой крышей; вход в школу — дверь на южном фасаде, она ведёт в fifteen_school_in
# (портал, logic.md §6).
P("ws_gate", "pk:wschool/wschool_4_041", foot=[2, 1])                  # створка школьной калитки
P("ws_entrance", "pk:wschool/p3/12,4,4,2", foot=[4, 1], block=False, sight=True)   # дверь с вывеской

W, H = 100, 70
y_road = 45                             # трасса: асфальт 45..48, обочины-трава 44 и 49
AXIS = (46, 47, 48, 49)                 # ось двора: от двери корпуса к калитке и на переход
GATE = (47, 48)                         # проход в калитке — против двери школы
DOOR = (48, 49)                         # дверь корпуса: две клетки южного фасада (y=20)
out = CityMap(city, "fifteen_school", "Пятнадцатая: старая школа", W, H, start=(2, 46), seed=57,
              music="desert", furnish=False)


def owhy(name, x, y, blocked=None, soft=None, reserved=None):
    """Почему предмет не встал — как why_not() в build_town.py."""
    foot = out.footprint(name, x, y)
    blocked = out.blocked if blocked is None else blocked
    soft = out.soft_obj if soft is None else soft
    reserved = out.reserved if reserved is None else reserved
    why = []
    if any(t in blocked for t in foot):
        why.append("блок: " + str([t for t in foot if t in blocked]))
    if any(t in soft for t in foot):
        why.append("мягкий предмет: " + str([t for t in foot if t in soft]))
    if any(t in reserved for t in foot):
        why.append("резерв")
    h = out.hides(name, x, y)
    if h:
        why.append(f"заслоняет {h[0]} ({h[1]}, {h[2]})")
    why.append("земля: " + "".join(out.ground[yy][xx] for xx, yy in foot))
    return f"«{name}» не встал в ({x}, {y}): " + "; ".join(why)


def _undo(n_props, n_conts, blocked, soft_obj, reserved):
    """Неудачная попытка не оставляет следов: предмет, его клетки и контейнер убираются."""
    del out.props[n_props:], out.containers[n_conts:]
    out.blocked, out.soft_obj, out.reserved = blocked, soft_obj, reserved
    out._reach = None


def place(name, x, y, **kw):
    """Явная расстановка: предмет обязан встать и остаться там, куда его поставили (logic.md §2)."""
    snap = (len(out.props), len(out.containers), set(out.blocked), set(out.soft_obj), set(out.reserved))
    ok = out.put(name, x, y, **kw)
    if ok and out.props[-1][1:3] == [x, y]:
        return True
    why = owhy(name, x, y, blocked=snap[2], soft=snap[3], reserved=snap[4])
    _undo(*snap)
    raise AssertionError(why + ("" if not ok else f"; встал в ({out.props and 0 or 0})"))


def oskin(name, x, y):
    """Мелочь на полу (бумаги, стекло, щепки): не блокирует, но и в стену не лезет."""
    if not out.put(name, x, y, check=False) or out.props[-1][1:3] != [x, y]:
        raise AssertionError(owhy(name, x, y))


def obox(name, x, y, *a, **kw):
    """Ящик с добычей — как place(): не встал — объяснить почему."""
    try:
        return out.box(name, x, y, *a, **kw)
    except AssertionError:
        raise AssertionError(owhy(name, x, y)) from None


# ------------------------------------------------------------ земля, трасса, дорожки
out.floors = getattr(out, "floors", {})
out.floor_code("t", "pk:desnat/p1/4,4,1,1", "pk:desnat/p1/5,4,1,1", "pk:desnat/p1/6,4,1,1")
out.floor_code("q", "pk:desnat/p1/10,4,1,1")
out.floor_code("s", "pk:desnat/p1/0,0,1,1", "pk:desnat/p1/1,0,1,1", "pk:desnat/p1/0,1,1,1")
out.paint("s", 0, 0, W - 1, H - 1)                      # пустошь вокруг
out.patchwork("s", ["t"], 70, 2, 5, seed=21)
out.patchwork("s", ["q"], 30, 1, 3, seed=22)
out.paint("g", 0, 0, W - 1, 43)                         # двор и задворки — трава
out.paint("a", 0, y_road, W - 1, y_road + 3)            # трасса
for x in range(0, W, 4):                                # прерывистая разметка
    out.ground[y_road + 1][x] = out.ground[y_road + 1][x + 1] = "h"
out.paint("g", 0, y_road - 1, W - 1, y_road - 1)        # обочины
out.paint("g", 0, y_road + 4, W - 1, y_road + 4)
out.paint("c", AXIS[0], 21, AXIS[3], 44)                # ось: крыльцо → калитка → обочина
out.paint("c", AXIS[0], 45, AXIS[3], y_road + 3)        # переход через трассу
out.paint("c", 3, 22, 96, 23)                           # аллея вдоль фасада
out.paint("c", 3, 39, 96, 40)                           # аллея вдоль ограды
out.paint("c", 3, 7, 4, 40)                             # западный обход корпуса
out.paint("c", 95, 7, 96, 40)                           # восточный обход
out.paint("c", 5, 6, 94, 6)                             # проход за корпусом — в задворки
out.patchwork("g", ["t"], 16, 2, 4, seed=23)            # протоптанная земля на газоне задворок…
for y in range(21, 45):                                 # …а не во дворе: там пятна выглядят кляксами
    for x in range(W):
        if out.ground[y][x] == "t":
            out.ground[y][x] = "g"
out.reserve(0, y_road, W - 1, y_road + 3)               # по трассе ничего не ставим
out.portal([(0, y) for y in range(y_road, y_road + 4)], "ruins", (147, 49), "Пятнадцатая")

# ------------------------------------------------------------ ограда с калиткой
# Сетка вдоль трассы: сплошная от западного края до калитки и от калитки до восточного;
# створка откинута в сторону, проход — против двери школы (logic.md §2: вход должен читаться).
out.hwall([FENCE], 1, 44, 42)
out.hwall([FENCE], 49, 96, 42)
place("ws_gate", 45, 42, force=True)                    # створка калитки откинута к западу
out.reserve(*GATE, *GATE)

# ------------------------------------------------------------ корпус школы
# Корпус под целой крышей (решение автора 24.10): зал внутри — отдельная карта fifteen_school_in,
# сюда ведёт дверь на южном фасаде, над ней вывеска «EXIT / SCHOOL». Под окнами ничего не ставим:
# высокий спрайт у фасада залезает на стену (замечание автора, logic.md §2а).
out.building(28, 8, 44, 13, "brick", south=(20,), worn=False)   # под целой крышей — без проломов
out.portal([(48, 20), (49, 20)], "fifteen_school_in", (43, 15), "Школа «Солнечная долина»")
for x in (32, 38, 54, 60, 66):                          # окна — поверх кирпичного фасада
    out.put(WINDOW, x, 20, force=True)
out.put("ws_entrance", 47, 20, force=True)              # дверь-портал с вывеской, поверх фасада


# ------------------------------------------------------------ огород (запад двора)
# Огород на земле, а не на стене: грядки в два ряда с дорожкой посередине, штакетник с калиткой,
# за грядками — пересохший школьный колодец (Макар проверяет его каждый день), вёдра, бочки, тележка;
# у южного штакетника — сарай с инвентарём (logic.md §3, «двор: огород — грядки рядом, вёдра и лопата»).
out.paint("t", 6, 25, 26, 38)                           # земля огорода
out.paint("c", 14, 24, 15, 38)                          # дорожка между грядками
out.hwall(["gs_fence"], 6, 26, 24, gaps=(14, 15))       # штакетник со стороны двора, с калиткой
out.hwall(["gs_fence"], 6, 26, 38, gaps=(14, 15))       # и со стороны аллеи у ограды
for y in range(25, 38):                                 # боковины — короткие секции столбиком
    place("gs_fence_b", 6, y)
    place("gs_fence_b", 26, y)
GARDEN = {                                              # грядки: капуста, помидоры, вскопанная земля
    (8, 27): "x_garden", (11, 27): "v22_cabbage", (18, 27): "x_garden", (21, 27): "v22_tomato",
    (24, 27): "x_garden",
    (8, 30): "v22_cabbage_b", (11, 30): "x_garden", (18, 30): "v22_tomato_b", (21, 30): "x_garden",
    (24, 30): "v22_cabbage",
    (8, 33): "x_garden", (11, 33): "v22_tomato", (18, 33): "x_garden", (21, 33): "v22_cabbage_b",
    (24, 33): "x_garden",
    (8, 36): "v22_tomato_b", (11, 36): "x_garden", (18, 36): "x_garden", (21, 36): "v22_cabbage",
}
for (x, y), bed in sorted(GARDEN.items()):
    place(bed, x, y)
place("w_well", 16, 36)                                 # пересохший колодец у южной калитки
place("bucket", 17, 36)
place("bucket", 16, 37)
place("barrel_wood", 17, 37)                            # бочка под дождь
place("x_cart", 12, 35)                                 # тележка с мешками — между грядок
place("crate", 9, 37)
place("sack", 10, 37)
oskin("shovel", 12, 37)                                 # лопата брошена в земле
oskin("pickaxe", 13, 37)
place("r_shed_tin", 23, 36)                             # сарай с инвентарём у южного штакетника

# ------------------------------------------------------------ баскетбольная площадка (центр у корпуса)
# Разметка, щиты с двух сторон, трибуны вдоль северного края лицом к площадке, мячи забыты за линией.
# Доска объявлений и урна — у входа во двор, лицом к аллее.
out.stamp("court", COURT, 30, 26, water=False)
out.stamp("court", COURT, 33, 26, water=False)
place("ws_hoop", 29, 27)
place("ws_hoop_b", 36, 27)
place("ws_bleachers", 30, 24)
place("ws_bleachers_b", 34, 24)
place("ws_ball", 33, 29)
place("ws_ball", 39, 23)
place("t50_bench", 39, 25)
place("ws_bin", 44, 25)
place("x_board", 42, 21)                                # доска объявлений у входа во двор

# ------------------------------------------------------------ детская площадка (восточнее оси)
# Песок, качели, «рукоход», скамьи нянек у северного края; мяч, урна, забытый рюкзак.
out.paint("q", 52, 25, 70, 32)                          # песок — только под снарядами и скамьями
place("ws_swings", 54, 27)
place("ws_monkey_bars", 58, 27)
place("ws_swings", 64, 27)
place("ws_ball", 67, 30)
place("bench_7", 60, 25)
place("bench_7", 66, 25)
place("ws_trash", 52, 24)                               # баки у входа на площадку (обыскиваются)
place("ws_bin", 69, 31)
place("ws_ball", 62, 28)                                # мяч в песке
place("ws_backpack", 56, 30)                            # чей-то рюкзак в песке

# ------------------------------------------------------------ спортивный угол и футбольное поле (восток)
# Турники и «качалка» у восточной ограды, маты под ними; южнее — утоптанное поле с воротами,
# ворота на концах поля в один ряд, лицом друг к другу: целые на востоке, выбитые лежат на западе. Здесь же стоит тот, кто был когда-то физруком.
place("ws_pullup", 74, 25)
place("ws_weights", 79, 25)
place("ws_barbell", 82, 25)
place("barrel_wood", 86, 25)
place("bucket", 87, 25)
place("t50_bench", 89, 25)
place("ws_mat", 74, 27)
place("ws_mat", 79, 27)
out.paint("t", 72, 31, 94, 38)                          # утоптанное поле
place("ws_goal_broken", 73, 35)
place("ws_goal", 90, 35)
place("ws_ball", 82, 34)
place("ws_bin", 93, 31)

# ------------------------------------------------------------ задворки (за корпусом)
# Тот самый автобус, что ушёл за детьми и вернулся пустым: стоит за школой, двери открыты, у колёс
# брошены детские рюкзаки. Кругом хлам, шины, баки, сарай и сгоревшая бочка — сюда не заходят.
place("ws_bus", 8, 4)
place("ws_junk", 18, 4)
place("pile_tires", 24, 4)
place("r_dumpster", 28, 4)
place("crate", 32, 4)
place("crate_b", 33, 4)
place("pile_scrap", 36, 4)
place("x_fire_barrel", 40, 4)
place("r_shed_tin", 44, 3)
place("pile_junk", 50, 4)
place("r_barrels", 54, 4)
place("metal_sheets", 57, 4)
place("ws_backpack", 10, 5)                             # рюкзаки у открытой двери автобуса
place("ws_backpack", 11, 5)
place("sack", 13, 5)
place("ws_trash", 62, 4)
place("barrel_wood", 65, 4)
place("pile_scrap", 72, 4)
place("r_barrels", 75, 4)
place("crate", 78, 4)
place("ws_junk", 82, 4)
place("pile_tires", 88, 4)
place("x_cart", 91, 4)
for x, y in ((3, 4), (59, 4), (68, 4), (86, 4)):         # сухие деревья по задворкам
    place("dead_tree", x, y)
for x, y in ((11, 11), (20, 15), (74, 12), (88, 15)):    # и вдоль боковых обходов корпуса
    place("dead_tree", x, y)
place("pile_junk", 22, 13)
place("r_barrels", 24, 16)
place("pile_scrap", 76, 16)
place("crate_broken", 90, 11)

# ------------------------------------------------------------ через трассу: закусочная, машины, стан
# Разбитая закусочная «DINER / GAS» с колонками, машины пятидесятых у обочины и на стоянке,
# телефонная будка и почтовый ящик на северной обочине; западнее — стоянка бродяг, восточнее — свалки.
place("r_shanty_big", 33, 52)                           # закусочная
place("t50_diner_sign", 38, 52)
place("t50_pump", 42, 53)
place("t50_pump", 43, 53)
obox("crate", 32, 54, "ящик закусочной", {"консервы": 2, "энергетический батончик": 1, "крышки": 12})
obox("r_dumpster", 29, 54, "мусорный бак", {"пружина": 1, "изолента": 1})
place("t50_phone", 24, 52)
place("t50_hydrant", 20, 44)
place("t50_mailbox", 54, 44)
place("t50_bench", 12, 44)
for x in range(8, W - 6, 16):                           # фонари по северной обочине
    place("t50_lamp", x, 44, allow_reserved=True)
for x in (18, 34, 62, 78, 94):                          # и по южной — не на переходе
    place("t50_lamp", x, 49)
for name, x, y in ((CARS[0], 28, 45), (CARS[1], 60, 48)):   # брошенные машины на трассе
    place(name, x, y, allow_reserved=True)
for name, x, y in ((CARS[2], 46, 51), (CARS[3], 52, 51), (CARS[4], 30, 57)):
    place(name, x, y)
place("r_tent_beige", 12, 58)                           # стоянка бродяг через дорогу
place("campfire", 16, 60)
place("r_logs", 15, 61)
place("barrel_wood", 12, 61)
place("pile_rags", 17, 58)
place("r_cabin", 8, 57)
place("r_car_wreck", 58, 60)
place("pile_tires", 62, 62)
place("r_trash", 58, 62)
place("r_shack", 70, 55)
place("r_billboard", 78, 52)
place("r_pickup", 84, 56)
place("r_barrels", 89, 56)
for x, y in ((6, 54), (22, 64), (44, 64), (68, 66), (92, 62), (95, 52)):
    place("dead_tree", x, y)
out.scatter(STONES + ["r_rocks", "r_trash"], 1, 51, W - 2, H - 2, 16)

# ------------------------------------------------------------ что ещё во дворе
# Двор не пустует: по бокам корпуса хозяйственный тыл (компост, ящики, бочки, мусор), на аллее —
# скамьи, на газоне — забытый мяч, за полем и через дорогу — свалки и сухие деревья.
place("bench_7", 41, 23)                                # скамьи у аллеи: ждут после уроков
place("bench_7", 44, 23)
place("pile_junk", 8, 12)                               # компостная куча у западной стены
place("crate", 14, 10)
place("barrel_wood", 16, 10)
place("r_barrels", 18, 12)
place("plank_block", 16, 14)
place("ws_junk", 11, 17)
place("bench_7", 9, 18)
place("dead_tree", 5, 11)
place("dead_tree", 22, 8)
place("r_barrels", 76, 10)                              # тыл с востока: бочки, баки, ящики
place("barrel_wood", 77, 10)
place("r_dumpster", 84, 11)
place("crate", 88, 14)
place("crate_b", 89, 14)
place("pile_scrap", 82, 17)
place("ws_junk", 92, 12)
place("dead_tree", 94, 10)
place("dead_tree", 73, 16)
place("ws_ball", 40, 34)                                # мяч на газоне внутри дорожки
place("r_car_wreck", 50, 54)                            # разбитые машины через дорогу
place("pile_tires", 54, 55)
place("r_trash", 50, 56)
place("r_barrels", 48, 56)
place("crate_broken", 52, 57)
place("pile_scrap", 57, 55)
place("by_road_sign_a", 5, 44)                          # знак на подъезде к школе
for x, y in ((14, 64), (28, 62), (40, 66), (52, 66), (62, 68), (74, 64), (86, 66), (2, 26), (98, 30)):
    place("dead_tree", x, y)                            # сухие деревья по краям
place("pile_tires", 46, 62)
place("r_trash", 34, 64)
place("r_bones", 60, 64)
place("r_rocks", 66, 62)
place("dead_tree", 1, 22)                               # бурьян у западного края
place("r_barrels", 20, 18)                              # хлам у западного торца корпуса
place("crate", 23, 19)
place("pile_scrap", 90, 19)                             # и у восточного
place("barrel_wood", 92, 18)
place("ws_ball", 36, 35)                                # мяч на газоне внутри дорожки
place("bench_7", 33, 38)                                # скамья на прямой дорожки
place("pile_tires", 10, 52)                             # шины у стоянки бродяг
place("r_trash", 14, 52)
place("dead_tree", 2, 60)

# ------------------------------------------------------------ кто где
# Уолт, бывший сторож, — у калитки (и ходит вдоль ограды); радтараканы — в хламе за корпусом,
# крысы — у закусочной, мутант-«физрук» — на матах спортивного угла (logic.md §2а).
out.npcs += [["walt", 42, 40]]
out.enemies += [["radroach", 13, 3], ["radroach", 19, 3], ["radroach", 25, 3], ["radroach", 33, 3],
                ["rat", 31, 55], ["rat", 35, 57], ["mutant", 80, 28]]
for _, x, y in out.npcs + out.enemies:
    out.reserve(x, y, x, y)
out.walk_zones = {"walt": [38, 39, 44, 41]}             # сторож у калитки, но не в самом проходе
out.folk_spots = {"makar": [12, 31],                    # Макар с метлой — у грядок
                  "raya": [57, 28],                     # Рая — на качелях
                  "vlas": [51, 22],                     # Влас — у двери в завал, ищет глобус
                  "critter:cat": [[23, 30]],            # кот у огорода
                  "critter:dog": [[52, 41]]}            # пёс у калитки


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
sin.portal([(45, 14), (45, 15)], "fifteen_school", (48, 21), "Школьный двор")
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
s_piece(WINDOW, 20, 3)                 # второе окно в стене
splace(WINDOW_BROKEN, 20, 4)           # выбитая рама — упала на пол под окном
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
sbox(CABINET, 40, 4, "библиотечный шкаф",
     {"консервы": 1, "батарейки": 1, "спички": 1, "Наша Америка, 5 класс": 1})   # «Последний урок»: учебник 5-Б
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
sbox("metal_box_open", 43, 20, "ящик завхоза",
     {"изолента": 2, "гаечный ключ": 1, "фонарик": 1, "вяленое мясо": 2},   # мясо — детям мисс Лейн
     requires={"item": "ключ-карта школы", "msg": "Железный ящик с табличкой «ЗАВХОЗ». Замок с прорезью для карты."})
splace("barrel_wood", 43, 26)          # бочки и ящики в юго-восточном углу
splace("barrel_wood", 44, 26)
splace("crate_b", 44, 27)
splace(TRASH, 37, 27)                  # баки у южной стены




# ================================================================ подвал деда
# Тайник ветерана под домом Эймоса (сюжет «Тайна деда», docs/furnish/fifteen.md §10). Планировка по
# назначению (logic.md §1): мебель набора nbunk нарисована в две клетки, поэтому пол расширен с 12×6 до
# 18×11 — иначе на северную стену влезают четыре предмета из двенадцати. Расстановка поштучная,
# автообстановка выключена. С севера на юг:
#   СЗ люк-лестница → С верстак с доской инструмента → С терминал со стулом → С шкаф → С полка с
#   консервами → С стеллаж → СВ койка с тумбочкой и ковриком → ЮЗ генератор, канистра, огнетушитель →
#   Ю баки с водой и армейские ящики → ЮВ сундук деда.
CW, CH = 22, 14
cel = CityMap(city, "fifteen_cellar", "Подвал деда", CW, CH, start=(2, 5), seed=59, interior=True,
              music="lab", furnish=False)
cel.floor_code("M", *METAL)
cel.wall_code("K", "pk:nbunk/nbunk_w1_12")
cel.room(1, 1, CW - 2, CH - 2, "K", "M")

# Мебель подвала — набор nbunk (тот же, что стены), пятно задаётся явно: картинка у большинства
# предметов 1.9×1.9 клетки, и с пятном 1×1 они налезают друг на друга (logic.md §2а, «двойники стеллажей»).
C_BED = P("cl_bed", "pk:nbunk/nbunk_3_000", foot=[2, 1], sight=True)          # койка с шинелью
C_STAND = P("cl_nightstand", "pk:nbunk/nbunk_3_005", foot=[1, 1], sight=True)  # тумбочка
C_BENCH = P("cl_workbench", "pk:nbunk/nbunk_3_006", foot=[2, 1], sight=True)  # верстак с тисками
C_TOOLS = P("cl_toolboard", "pk:nbunk/nbunk_2_007", foot=[2, 1], block=False, sight=True)   # доска с инструментом
C_LOCKER = P("cl_locker", "pk:nbunk/nbunk_3_008", foot=[1, 1], sight=True, search="locker",
             title="шкаф деда")
C_SHELF = P("cl_shelf_cans", "pk:nbunk/nbunk_3_002", foot=[2, 1], sight=True)  # полка с консервами
C_RACK = P("cl_rack", "pk:nbunk/nbunk_3_004", foot=[2, 1], sight=True)       # пустой стеллаж
C_GEN = P("cl_generator", "pk:nbunk/nbunk_3_026", foot=[2, 1], sight=True,
          light={"r": 110, "color": [255, 190, 110], "at": [0.5, 0.4], "flicker": 0.25})
C_TANKS = P("cl_tanks", "pk:nbunk/nbunk_2_021", foot=[3, 1], sight=True)     # два бака с водой
C_CAN = P("cl_jerrycan", "pk:nbunk/nbunk_3_041")                             # канистра
C_CRATES = P("cl_crates", "pk:nbunk/nbunk_3_029", foot=[2, 1])               # штабель ящиков
C_MILBOX = P("cl_milbox", "pk:nbunk/nbunk_3_030", foot=[2, 1], search="military", title="армейский ящик")
C_MAP = P("cl_map", "x_vd_map", foot=[2, 1], block=False, sight=True)        # карта на стене
C_LOCKERS = P("cl_lockers", "pk:nbunk/nbunk_3_003", foot=[2, 1], sight=True)  # ряд шкафчиков с формой
C_PILE = P("cl_supply_pile", "pk:nbunk/nbunk_3_020", foot=[2, 1], sight=True)  # штабель ящиков с консервами
C_MEDS = P("cl_medbox", "pk:nbunk/nbunk_3_017")                              # аптечка на тумбочке


# Помощники ручной расстановки — общие для обоих подвалов (подвал деда, подвал салуна): почему предмет
# не встал (как why_not() в build_town.py), явная постановка, сюжетный ящик, настенное, мелочь на столе.
def _why(m, name, x, y):
    foot = m.footprint(name, x, y)
    why = []
    if any(t in m.blocked for t in foot):
        why.append("блок: " + str([t for t in foot if t in m.blocked]))
    if any(t in m.soft_obj for t in foot):
        why.append("мягкий предмет: " + str([t for t in foot if t in m.soft_obj]))
    if any(t in m.reserved for t in foot):
        why.append("резерв")
    h = m.hides(name, x, y)
    if h:
        why.append(f"заслоняет {h[0]} ({h[1]}, {h[2]})")
    why.append("земля: " + "".join(m.ground[yy][xx] for xx, yy in foot))
    return f"«{name}» не встал в ({x}, {y}): " + "; ".join(why)


def _place(m, name, x, y, **kw):
    """Явная расстановка: мебель — только на полу комнаты, встать обязана ровно туда, куда ставили."""
    foot = m.footprint(name, x, y)
    assert all(m.ground[yy][xx] in m.floors for xx, yy in foot), \
        f"«{name}» в ({x}, {y}): не на полу — " + " ".join(m.ground[yy][xx] for xx, yy in foot)
    try:
        ok = m.put(name, x, y, **kw)
    except AssertionError:
        raise AssertionError(_why(m, name, x, y)) from None
    if ok and m.props[-1][1:3] == [x, y]:
        return True
    raise AssertionError(_why(m, name, x, y) + f"; встал в ({m.props[-1][1]}, {m.props[-1][2]})")


def _box(m, name, x, y, title, loot, **kw):
    """Сюжетный ящик/сундук — как _place(): не встал, так с причиной."""
    foot = m.footprint(name, x, y)
    assert all(m.ground[yy][xx] in m.floors for xx, yy in foot), \
        f"«{name}» в ({x}, {y}): не на полу — " + " ".join(m.ground[yy][xx] for xx, yy in foot)
    try:
        return m.box(name, x, y, title, loot, **kw)
    except AssertionError:
        raise AssertionError(_why(m, name, x, y)) from None


def _wall(m, name, x, y, dx=0, dy=-26):
    """Настенное (доска с инструментом, карта): ставится на клетки стены-кода и поднимается на стену.
    Выше пола — на столько, чтобы высокая мебель под ним не заслоняла картинку (аудит «стена»)."""
    fw, fh = props_info(name)["foot"]
    cells = [(x + i, y + j) for i in range(fw) for j in range(fh)]
    assert all(m.ground[cy][cx] in m.walls for cx, cy in cells), \
        f"«{name}» в ({x}, {y}): там нет стены — " + " ".join(m.ground[cy][cx] for cx, cy in cells)
    m.props.append([name, x, y, dx, dy])
    m.blocked.update(cells)              # клетка стены занята: автосвет не повесит плафон на карту
    m._reach = None


def _table(m, name, x, y, dx=0, dy=-20):
    """Мелочь на столешнице: на клетке мебели, поднята на её высоту, рисуется сразу после неё
    (6-й элемент — поправка порядка отрисовки, src/townmap.py)."""
    assert (x, y) in m.blocked, f"«{name}» в ({x}, {y}): под ним нет стола"
    m.props.append([name, x, y, dx, dy, 1 - dy])


def cwhy(name, x, y):
    return _why(cel, name, x, y)


def cplace(name, x, y, **kw):
    return _place(cel, name, x, y, **kw)


def cbox(name, x, y, title, loot, **kw):
    return _box(cel, name, x, y, title, loot, **kw)


def cwall(name, x, y, dx=0, dy=-26):
    return _wall(cel, name, x, y, dx=dx, dy=dy)


def ctable(name, x, y, dx=0, dy=-20):
    return _table(cel, name, x, y, dx=dx, dy=dy)


# ------------------------------------------------------------ люк и лестница (СЗ)
# Люк деда сверху, лестница по стене; площадка под ней пустая — выходишь и сразу видно весь подвал
# (logic.md §2: вход не за спинами и не в заставленном углу).
cel.props.append(["x_ladder_wall", 2, 4, 0, -18])       # в упор к стене, во всю её высоту — до люка под потолком
cel.portal([(2, 4)], "ruins", (7, 32), "Наверх, в дом")          # люк — (7, 33), выход рядом

# ------------------------------------------------------------ рабочий угол (С, запад)
# Верстак с тисками у северной стены, доска с инструментом на стене выше верстака, ящик под рукой.
cwall(C_TOOLS, 5, 3, dy=-44)                          # доска с инструментом — выше верстака
cplace(C_BENCH, 5, 4)
cplace("toolbox_red", 6, 5)                           # ящик с инструментом под верстаком

# ------------------------------------------------------------ терминал (С, центр)
# Стол с монитором у северной стены, карта над ним, стул перед столом (дед сидит лицом к экрану),
# газета брошена на пол.
cwall(C_MAP, 7, 3, dy=-40)                            # карта над терминалом
cel.terminal(8, 4, "amos_cellar")
cplace("stool_1", 8, 5)                               # табурет перед терминалом: дед сидит лицом к экрану
cplace("w_newspaper", 7, 5)                           # газета брошена у стола

# ------------------------------------------------------------ склад (С, восток)
# Шкаф с формой, полка с консервами (контейнер), пустой стеллаж; у полки — мешки с крупой.
cplace(C_LOCKER, 10, 4)                               # шкаф деда
cbox(C_SHELF, 12, 4, "полка с консервами",
     {"консервы": 4, "крышки": 15, "химикаты": 1, "патроны": 1})
cplace(C_LOCKERS, 15, 4)                              # ряд шкафчиков: форма, снаряжение
cplace("w_sacks", 2, 9)                               # мешки с крупой у западной стены
cplace("w_sacks", 3, 9)
cplace(C_PILE, 2, 7)                                  # штабель ящиков с консервами у западной стены

# ------------------------------------------------------------ стол деда (середина, западнее центра)
# Письменный стол деда в пустой середине подвала: радио и настольная лампа на столешнице, табурет лицом
# к столу, под столешницей — коробка с патронами. Вокруг стола проход: ряды 6, 9 и 10 свободны, как и
# колонки 8 и 11; путь от люка (2,4) к сундуку (18,11) остаётся сквозным по y=6 и y=9.
C_DESK = "fifteen_f_home_table"                       # письменный стол с ящиками (набор fifteen_f_home)
# Стол взят из автообстановки «жилой комнаты» (citykit.home_scenes). В подвалах автообстановка выключена,
# поэтому предмет регистрируется явно — теми же полями, что у home_scenes.
city.prop("fifteen_f_home_table", "pk:west/west_2_000", foot=[2, 1])
cplace(C_DESK, 9, 7)                                  # стол 2 клетки: (9..10, 7)
ctable("x_radio", 9, 7, dx=2, dy=-40)                 # рация деда — на западной половине, в глубине столешницы
ctable("w_table_lamp", 10, 7, dx=-16, dy=-40)         # лампа — на восточной, отступив от переднего края (logic.md §2)
cplace("stool_1", 10, 8)                              # табурет перед столом: дед сидит лицом к рации
cplace("ammo_box", 9, 8)                              # коробка с патронами под столешницей

# ------------------------------------------------------------ койка (СВ)
# Койка в северо-восточном углу, тумбочка с фонарём в изголовье, лоскутный коврик перед койкой.
cplace(C_BED, 18, 4)
cplace(C_STAND, 17, 4)
ctable(C_MEDS, 17, 4, dy=-32)                         # аптечка на тумбочке
cel.ceiling(18, 5, r=150, color=(255, 190, 110), flick=0.03)   # лампочка под потолком над койкой
cplace("w_rug_quilt", 18, 5)                          # коврик 2×2 перед койкой

# ------------------------------------------------------------ генератор (ЮЗ)
# Генератор у южной стены (сам светит, чуть мерцает), канистра рядом, огнетушитель у стены.
cplace(C_GEN, 3, 11)
cplace(C_CAN, 5, 11)
cplace("x_fireext", 6, 11)

# ------------------------------------------------------------ вода и ящики (Ю)
# Два бака с водой, два армейских ящика, штабель ящиков; к сундуку — ведро.
cplace(C_TANKS, 8, 11)                                # баки с водой 3 клетки
cplace(C_MILBOX, 12, 11)                              # армейский ящик
cplace(C_CRATES, 15, 11)                              # штабель ящиков
cplace("bucket", 14, 11)                              # ведро под рукой у ящиков

# ------------------------------------------------------------ сундук (ЮВ)
# Армейский сундук деда — то, за чем сюда лезут: бронежилет, патроны, стимуляторы, фотография.
cbox("metal_chest", 18, 11, "армейский сундук деда",
     {"армейский бронежилет": 1, "патроны": 20, "стимулятор": 2, "фотография": 1})


# ================================================================ подвал салуна
# Подвал под стойкой Мо (docs/furnish/fifteen.md §3.5): самогонный аппарат, склад зерна и угол Тесс,
# шестнадцатилетней беглянки. Пол 12×6 оказался мал для трёх зон сразу (26 предметов на 72 клетки —
# свалка), поэтому подвал расширен до 22×14, как у деда: пол 18×8, 144 клетки. Люк и точка прибытия
# прежние (tools/build_town.py: hatch → (3,5)), лестница — тоже (3,4). Расстановка поштучная, авто-
# обстановка выключена (свет — auto_ambient в citykit.save). С севера на юг и с запада на восток:
#   СЗ люк-лестница во всю стену → С пустые бутылки и стол Мо с лампой → СВ шкаф с бутылками →
#   З зерно, тайник и ящик с бутылками, ведро со шваброй → ЮЗ огонь, котёл, змеевик, бочка браги,
#   бутыли и лужа → В ширма-занавеска, койка Тесс с тумбочкой, её стол со стулом → В ящик с пробками.
sal = CityMap(city, "fifteen_saloon_cellar", "Подвал салуна", 22, 14, start=(3, 5), seed=60, interior=True,
              music="caves", furnish=False)
sal.floor_code("G", *WOOD)
sal.wall_code("D", "pk:nbunk/nbunk_w1_00")
sal.room(1, 1, 20, 12, "D", "G")


def salwhy(name, x, y):
    return _why(sal, name, x, y)


def salplace(name, x, y, **kw):
    return _place(sal, name, x, y, **kw)


def salbox(name, x, y, title, loot, **kw):
    return _box(sal, name, x, y, title, loot, **kw)


def saltable(name, x, y, dx=0, dy=-20):
    return _table(sal, name, x, y, dx=dx, dy=dy)


# ------------------------------------------------------------ люк и лестница (СЗ)
# Лестница во всю стену — до люка под потолком, мягкий конус света из люка вниз (x_ladder_wall, как в
# подвале деда). Площадка под ней пустая: выходишь и сразу видишь аппарат и угол Тесс.
sal.props.append(["x_ladder_wall", 3, 4, 0, -18])
sal.portal([(3, 4)], "ruins", (53, 27), "Наверх, в салун")       # люк — (52, 27), за стойкой

# ------------------------------------------------------------ северная стена
# Пустые бутылки рядком у стены, стол, за которым Мо считает бутыли (лампа и пробки делят столешницу
# пополам, logic.md §2), и бочки под следующую партию. Высокого у стены с лестницей нет — люк читается.
salplace("pile_bottles", 5, 4)         # пустые бутылки у северной стены (2 клетки)
salplace("w_table_plain", 9, 4)        # стол Мо (2 клетки)
saltable("w_table_lantern", 9, 4, dy=-40)   # лампа — западная половина, в глубине столешницы
saltable("junk_small_1", 10, 4, dy=-36)     # пробки и мелочь — восточная половина, не у края
salplace("w_barrels", 12, 4)           # две бочки под новую партию (2 клетки)

# ------------------------------------------------------------ склад (запад)
# Зерно для браги, тайник Мо за ящиками, ящик с бутылками у лестницы; ведро со шваброй — тут же:
# «Мо заметает следы» — всё, что не должно попасться на глаза покупателю.
salplace("sack", 2, 6)                 # развязанный мешок на полу
salplace("w_crate_sacks", 2, 7)        # ящик с мешками зерна (2 клетки)
salbox("cabinet_small", 2, 8, "тайник Мо", {"самогон": 3, "крышки": 60, "сигареты": 2})
salbox("crate", 2, 9, "ящик с бутылками", {"самогон": 2, "спички": 1})     # сюжетный, обыскивается
salplace("bucket", 3, 9)               # ведро
salplace("pile_rags", 2, 10)           # тряпки у западной стены (2 клетки)

# ------------------------------------------------------------ самогонный аппарат (ЮЗ)
# Котёл на огне (огонь и свет — в самом спрайте котла, отдельный костёр над ним висел бы в воздухе),
# лужа у котла, бочка с брагой и готовый товар — бутыли в ряд. Одинокую трубу не ставим: без змеевика
# она читается как столб посреди подвала.
# Фонарь стоит на бочке, а не на полу (logic.md §2).
salplace("x_cauldron", 5, 10)          # котёл (сам светит: огонь просвечивает)
salplace("x_puddle", 6, 10)            # лужа у котла
salplace("barrel_wood", 7, 10)         # бочка с брагой
saltable("w_lantern", 7, 10, dy=-46)   # фонарь на бочке — свет над аппаратом
salplace("pile_bottles_b", 8, 10)      # бутыли в ряд — готовый товар (2 клетки)
salplace(BROOM, 7, 4)                  # швабра прислонена к северной стене, не посреди пола

# ------------------------------------------------------------ угол Тесс (В)
# Она живёт здесь не первый месяц: ширма-занавеска отгораживает угол от остального подвала, койка
# вдоль восточной стены, тумбочка со свечами, сумка у койки; за столом — миска и её книга (стол делят
# пополам), стул с торца в профиль к столу (logic.md §2а). Тесс сидит за столом — не в проходе.
sal.npcs += [["tess", 16, 8]]
salplace("x_curtain", 14, 8)           # занавеска на верёвке (2 клетки, до полу — как ширма)
salplace("w_bed", 18, 8)               # койка вдоль восточной стены (2 клетки)
salplace("w_nightstand", 17, 8)        # тумбочка в изголовье
saltable("candles", 17, 8, dy=-30)     # свечи на тумбочке
salplace("bag", 17, 9)                 # её сумка у койки
salplace("w_table_long", 15, 9)        # её стол (2 клетки)
saltable("canteen", 15, 9, dy=-36)     # миска-котелок — западная половина, отступив от края
saltable(BOOK_OPEN, 16, 9, dy=-34)     # открытая книга — восточная половина, отступив от края
salplace("w_chair_r", 14, 9)           # стул с торца стола, лицом к нему

# ------------------------------------------------------------ стены (СВ и В)
# Шкаф с бутылками в северо-восточном углу, ящик с пробками — у восточной стены.
salplace("w_liquor", 18, 4)            # шкаф с бутылками (2 клетки, СВ угол)
salplace("crate_small", 19, 5)         # ящик с пробками

city.save(gap_exempt=("walt",))
