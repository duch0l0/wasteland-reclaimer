"""
Убежище 4 (сериал Fallout): учёные Vault-Tec и их потомки до сих пор живут внутри и «исследуют мутации».
Сюда ушли 8 контейнеров ВРЭ. Второй акт. Сценарий — docs/story.md, раздел 16.

  vault4         «Убежище 4» (48×34): прибрежные холмы, дверь-шестерня в склоне, интерком у двери;
                 у подножия — пустой фургон культа и следы: кто-то уже стучался.
  vault4_upper   «Убежище 4: жилой ярус»: чистый, светлый — атриум с оранжереей, класс, столовая,
                 кабинет смотрительницы; жители, в том числе мирные мутанты.
  vault4_lower   «Убежище 4: нижний ярус»: лаборатория — колбы, клетки, хранилище ВРЭ;
                 то, что вышло из «исследований», бродит по коридорам.

Наборы: wasteland-laboratory (wlab), nuclear-bunker (nbunk), post-apocalyptic-wasteland-survival-farm (wfarm),
desert-natural (desnat), desert-town (destown), zombie-city (zcity), cult-temple (cult), west, hospital (hosp).
Запуск из папки game_project:  .venv/bin/python tools/build_vault4.py
"""
import json

from citykit import City, CityMap

city = City("vault4", "Убежище 4")


def P(name, img, **kw):
    city.prop(name, img, **kw)
    return name


def cells(page, pts):
    return [f"pk:{page}/{x},{y},1,1" for x, y in pts]


CLIFFS = [P(f"v4_cliff{i}", f"pk:desnat/p1/{x},14,2,2", foot=[2, 2], sight=True) for i, x in enumerate((8, 10, 12))]
OUTCROP = P("v4_outcrop", "pk:desnat/p1/12,4,3,2", foot=[3, 2], sight=True)
VAN = P("v4_van", "pk:zcity/zcity_2_097", foot=[2, 1], sight=True)
# жилой ярус
BUNKS = [P(f"v4_bunk{i}", f"pk:nbunk/nbunk_2_{n:03d}", foot=[2, 1], sight=True) for i, n in enumerate((0, 1, 2, 3))]
SHELF = P("v4_shelf", "pk:nbunk/nbunk_2_004", foot=[2, 1], sight=True, search="shelf", title="стеллаж с припасами")
LOCKER = P("v4_locker", "pk:nbunk/nbunk_2_005", search="locker", title="шкафчик")
DESK_PC = [P("v4_desk_pc", "pk:nbunk/nbunk_2_016", foot=[2, 1]), P("v4_desk_pc_b", "pk:nbunk/nbunk_2_017", foot=[2, 1])]
TANKS = P("v4_tanks", "pk:nbunk/nbunk_2_021", foot=[3, 1], sight=True)
TABLE = P("v4_table", "pk:west/west_2_000", foot=[2, 1])
CHAIR = P("v4_chair", "pk:west/west_2_001")
PLANTERS = [P(f"v4_planter{i}", f"pk:wfarm/wfarm_{n}", foot=[2, 1]) for i, n in
            enumerate(("1_058", "1_059", "1_072", "1_073", "1_074"))]
SHELF_PLANTS = P("v4_shelf_plants", "pk:wfarm/wfarm_1_085", foot=[2, 1], sight=True)
POT_PLANT = P("v4_pot_plant", "pk:wfarm/wfarm_1_027")
BOOKS = P("v4_bookcase", "pk:west/west_2_116", sight=True, search="shelf", title="книжный шкаф")
BOARD = P("v4_board", "pk:aoffice/aoffice_2_010")
# лаборатория
VAT = P("v4_vat", "pk:wlab/wlab_1_000", sight=True)
VATS = P("v4_vats", "pk:wlab/wlab_1_002", foot=[2, 1], sight=True)
TANK = P("v4_tank", "pk:wlab/wlab_1_008", sight=True)
TANK_B = P("v4_tank_b", "pk:wlab/wlab_1_034", sight=True)
CONSOLE = [P("v4_console", "pk:wlab/wlab_1_009", foot=[2, 1]), P("v4_console_b", "pk:wlab/wlab_1_010", foot=[2, 1])]
CHEM = [P("v4_chem", "pk:wlab/wlab_1_012", foot=[2, 1]), P("v4_chem_b", "pk:wlab/wlab_1_035", foot=[2, 1])]
ARM = P("v4_arm", "pk:wlab/wlab_1_029", foot=[2, 1])
CABINETS = [P("v4_cabinet", "pk:wlab/wlab_2_037", foot=[2, 1], sight=True, search="drawer", title="шкаф с препаратами"),
            P("v4_cabinet_b", "pk:wlab/wlab_2_070", foot=[2, 1], sight=True, search="drawer", title="полка с реактивами")]
BIG_TUBES = [P("v4_tube", "pk:wlab/wlab_3_101", foot=[2, 1], sight=True), P("v4_tube_b", "pk:wlab/wlab_3_102", foot=[2, 1], sight=True),
             P("v4_tube_broken", "pk:wlab/wlab_3_103", foot=[2, 1], sight=True)]
LAB_DESK = P("v4_lab_desk", "pk:wlab/wlab_3_054", foot=[2, 1])
CRATE = P("v4_crate", "pk:wlab/wlab_2_024", foot=[2, 1], search="military", title="армейский ящик")
CAGE = P("v4_cage", "pk:cult/cult_3_020", sight=True)
BONES = [P("v4_bones", "pk:grave/grave_2_022", block=False), P("v4_bones_b", "pk:grave/grave_2_027", block=False)]
BIOHAZ = P("v4_biohazard", "pk:hosp/hosp_1_012")

SAND = cells("destown/p2", [(0, 0), (1, 0), (0, 1), (1, 1)])
GRAVEL = cells("destown/p2", [(4, 0), (5, 0), (4, 1), (5, 1)])
PLATES = cells("nbunk/p2", [(4, 8), (5, 9), (6, 10), (4, 10)])
TILE_W = ["pk:store/p1/12,0,1,1"]
GRATE = cells("nbunk/p2", [(0, 12), (1, 13), (2, 14), (3, 12)])
GRASS = ["pk:zcity/zcity_f2_00"]
VWALL = "pk:nbunk/nbunk_w3_17"
LWALL = "pk:pmall/pmall_w3_10"


# ================================================================ поверхность
W, H = 48, 34
sf = CityMap(city, "vault4", "Убежище 4", W, H, start=(1, 26), seed=161, music="desert", world_pos=(720, 1380))
sf.floor_code("s", *SAND)
sf.floor_code("g", *GRAVEL)
sf.paint("s", 0, 0, W - 1, H - 1)
FLOOR = set()
for x0, y0, x1, y1 in ((0, 23, 26, 29), (14, 8, 40, 30)):
    FLOOR |= {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}
sf.paint("g", 0, 25, 22, 27)
sf.paint("g", 21, 12, 24, 27)
sf.exits = [(0, y) for y in range(24, 29)]
sf.reserve(0, 24, 6, 28)
sf.put("x_vault_door4", 21, 7, check=False, allow_reserved=True)
sf.put("x_vault_sign4", 26, 9)
sf.terminal(18, 10, "v4_intercom")                       # интерком у двери: «Всё хорошо. Как погода?»
sf.portal([(22, 9), (23, 9)], "vault4_upper", (20, 6), "Убежище 4",
          requires={"flag": "v4_open", "msg": "Дверь-шестерня закрыта. На интеркоме мигает зелёная лампочка: внутри кто-то слушает."})
sf.reserve(21, 9, 24, 13)
# пустой фургон культа у подножия: культ уже стучался в эту дверь
sf.put(VAN, 30, 18)
sf.box("hb_crate", 33, 19, "ящик с печатью круга", {"письмо смотрительнице": 1})
for y in range(0, H, 2):
    for x in range(0, W, 2):
        if not {(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)} & FLOOR and not (21 <= x <= 24 and 6 <= y <= 9):
            sf.props.append([CLIFFS[(x * 3 + y * 5) % 3], x, y])
            sf.blocked.update({(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)})
for x, y in ((15, 12), (36, 10), (34, 26)):
    sf.maybe(OUTCROP, x, y)
sf.enemies += [["radscorpion", 36, 14]]
sf.scatter(["r_dry_bush", "r_rocks"], 14, 8, 40, 28, 10)


# ================================================================ жилой ярус
W, H = 46, 36
up = CityMap(city, "vault4_upper", "Убежище 4: жилой ярус", W, H, start=(20, 6), seed=162, interior=True, music="lab")
up.floor_code("F", *PLATES)
up.floor_code("T", *TILE_W)
up.floor_code("g", *GRASS)
up.wall_code("W", VWALL)
up.room(1, 1, 45, 12, "W", "F")                       # входной зал
up.room(1, 12, 15, 35, "W", "T")                      # столовая и класс
up.room(15, 12, 31, 35, "W", "g")                     # атриум-оранжерея
up.room(31, 12, 45, 22, "W", "T")                     # кабинет смотрительницы
up.room(31, 22, 45, 35, "W", "F")                     # жилой блок
up.put("x_vault_gear4", 19, 3, force=True)
up.portal([(19, 4), (20, 4)], "vault4", (22, 11), "Наружу")
up.reserve(17, 4, 23, 7)
up.opening(22, 12, 23, 14, "g")
up.opening(15, 19, 15, 20, "T")
up.opening(31, 16, 31, 17, "T")
up.opening(31, 28, 31, 29, "F")
# входной зал: стойка дезинфекции, шкафчики, табличка — здесь встречают гостей
up.put(LOCKER, 3, 4)
up.put(LOCKER, 4, 4)
up.put(DESK_PC[0], 29, 5)
up.put(POT_PLANT, 13, 4)
up.put(POT_PLANT, 26, 4)
up.npcs += [["v4_greeter", 22, 9]]
# столовая: столы со стульями; класс у южной стены — доска и парты
for y in (16, 20):
    up.put(TABLE, 3, y)
    up.put(CHAIR, 5, y)
    up.put(TABLE, 9, y)
    up.put(CHAIR, 11, y)
up.box(SHELF, 12, 15, "стеллаж столовой", {"консервы": 1, "энергетический батончик": 1})
up.put(BOARD, 7, 25)
for x in (3, 7, 11):
    up.put(TABLE, x, 29)
up.npcs += [["v4_teacher", 8, 27], ["v4_kid", 4, 31], ["v4_kid_b", 11, 32]]
# атриум: грядки и стеллажи с рассадой под лампами — гордость Убежища
for i, (x, y) in enumerate(((16, 16), (19, 16), (25, 16), (28, 16), (16, 22), (28, 22), (16, 28), (19, 28), (25, 28))):
    up.put(PLANTERS[i % len(PLANTERS)], x, y)
up.put(SHELF_PLANTS, 21, 22)
up.put(TANKS, 17, 33)
up.npcs += [["v4_gardener", 23, 25], ["v4_mutant", 19, 25]]
# кабинет смотрительницы: стол с терминалом, книжные шкафы
up.put(BOOKS, 33, 15)
up.put(BOOKS, 35, 15)
up.put(DESK_PC[1], 38, 18)
up.terminal(42, 15, "v4_overseer")
up.npcs += [["overseer_sim", 39, 20]]
# жилой блок: койки рядами, шкафчик
for i, (x, y) in enumerate(((33, 25), (37, 25), (41, 25), (33, 31), (37, 31), (41, 31))):
    up.put(BUNKS[i % 4], x, y)
up.npcs += [["v4_resident", 36, 28], ["v4_mutant_b", 40, 29]]
# лифт на нижний ярус — за атриумом, у южной стены
up.props.append(["x_ladder", 29, 33])
up.portal([(29, 33)], "vault4_lower", (6, 5), "Нижний ярус",
          requires={"flag": "v4_lower_ok", "msg": "Лифт на нижний ярус. Панель горит красным: «Только персонал уровня 3»."})
up.reserve(28, 32, 30, 34)


# ================================================================ нижний ярус — лаборатория
W, H = 48, 36
lw = CityMap(city, "vault4_lower", "Убежище 4: нижний ярус", W, H, start=(6, 5), seed=163, interior=True, music="vats")
lw.floor_code("F", *GRATE)
lw.floor_code("T", *TILE_W)
lw.wall_code("W", LWALL)
lw.room(1, 1, 16, 35, "W", "F")                       # коридор с клетками
lw.room(16, 1, 47, 18, "W", "T")                      # лаборатория
lw.room(16, 18, 47, 35, "W", "F")                     # хранилище ВРЭ
lw.props.append(["x_ladder", 6, 4])
lw.portal([(6, 4)], "vault4_upper", (29, 34), "Наверх, в атриум")
lw.reserve(4, 4, 9, 7)
lw.opening(16, 9, 16, 10, "T")
lw.opening(16, 27, 16, 28, "F")
# коридор: клетки вдоль стены — в одних пусто, в других то, что «исследуют»
for y in (10, 14, 18, 22, 26, 30):
    lw.put(CAGE, 3, y)
for x, y in ((9, 13), (11, 24)):
    lw.put(BONES[(x + y) % 2], x, y)
# лаборатория: колбы и баки вдоль северной стены, рабочие столы рядами, манипулятор, консоли
for i, x in enumerate((18, 21, 24, 27)):
    lw.put([VAT, TANK, TANK_B, VAT][i], x, 4)
lw.put(VATS, 30, 4)
lw.put(CABINETS[0], 34, 4)
lw.put(CABINETS[1], 37, 4)
lw.put(CONSOLE[0], 41, 4)
for x in (19, 25, 31):
    lw.put(CHEM[x % 2], x, 9)
    lw.put(LAB_DESK, x, 13)
lw.put(ARM, 38, 10)
lw.terminal(43, 13, "v4_lab")
# хранилище: большие колбы, одна разбита; армейские ящики — контейнеры ВРЭ; знак биологической опасности
for i, x in enumerate((19, 23, 27)):
    lw.put(BIG_TUBES[i], x, 22)
for x, y in ((34, 22), (38, 22), (34, 27), (38, 27)):
    lw.put(CRATE, x, y)
lw.put(BIOHAZ, 43, 21)
lw.terminal(43, 31, "v4_vault")
lw.enemies += [["beast", 10, 20], ["rad_mutant", 30, 15], ["joined", 25, 30], ["rad_mutant", 44, 26]]

city.save(gap_exempt=("v4_mutant", "v4_gardener"))
L = json.load(open("data/locations.json", encoding="utf-8"))
L["vault4"].update({"world_name": "Убежище 4", "discover": True})
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
