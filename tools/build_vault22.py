"""
Убежище 22 (Fallout: New Vegas) — убежище-оранжерея: «растения и еда будущего». В 2121 году ещё живое;
канон: в 2130-х его погубят споры. Третий акт. Сценарий — docs/story.md, раздел «Убежище 22 — „Сад будущего“».

  vault22         «Убежище 22» (46×34): лесистый склон над Гудспрингсом, дверь-шестерня в скале, огороды снаружи.
  vault22_living  «Убежище 22: жилой ярус»: входной зал, столовая, жилой блок, пост охраны Хьюго Ли,
                  кабинет смотрителя Кин.
  vault22_garden  «Убежище 22: оранжереи»: три зала грядок под лампами — томаты, капуста, огурцы на шпалерах;
                  гидропоника, склад семян.
  vault22_lab     «Убежище 22: лаборатория и нижняя ферма»: лаборатория пестицидов, грибная ферма —
                  споры уже ползут по стенам; споровики.

Наборы: modern-greenhouse (ghouse), nuclear-bunker (nbunk), wasteland-laboratory (wlab), abandoned-rural-village
(rvill), desert-natural (desnat), zombie-city (zcity), goblin-cave (gcave).
Запуск из папки game_project:  .venv/bin/python tools/build_vault22.py
"""
import json

from citykit import City, CityMap

city = City("vault22", "Убежище 22")


def P(name, img, **kw):
    city.prop(name, img, **kw)
    return name


def cells(page, pts):
    return [f"pk:{page}/{x},{y},1,1" for x, y in pts]


CLIFFS = [P(f"v22_cliff{i}", f"pk:desnat/p1/{x},14,2,2", foot=[2, 2], sight=True) for i, x in enumerate((8, 10, 12))]
TREES = [P(f"v22_tree{i}", f"pk:rvill/rvill_2_{n:03d}", scale=1.5, foot=[2, 1]) for i, n in enumerate((32, 33, 34))]
GRASS = [P(f"v22_grass{i}", f"pk:rvill/rvill_2_{n:03d}", block=False) for i, n in enumerate((1, 2, 5, 6, 8))]
# оранжереи
BEDS = [P(f"v22_bed{i}", f"pk:ghouse/ghouse_1_{n:03d}", foot=[4, 1]) for i, n in enumerate((7, 8, 9, 13))]
BED_EMPTY = P("v22_bed_empty", "pk:ghouse/ghouse_1_014", foot=[4, 1])
ROWS = [P(f"v22_row{i}", f"pk:ghouse/ghouse_3_{n:03d}", foot=[4, 1]) for i, n in enumerate((0, 1, 2, 3, 5, 6))]
TOMATO = [P("v22_tomato", "pk:ghouse/ghouse_3_024", foot=[2, 1]), P("v22_tomato_b", "pk:ghouse/ghouse_3_025", foot=[2, 1])]
CUCUMBER = [P("v22_cucumber", "pk:ghouse/ghouse_3_027", foot=[2, 1]), P("v22_cucumber_b", "pk:ghouse/ghouse_3_028", foot=[2, 1])]
CABBAGE = [P("v22_cabbage", "pk:ghouse/ghouse_3_048", foot=[2, 1]), P("v22_cabbage_b", "pk:ghouse/ghouse_3_050", foot=[2, 1]),
           P("v22_lettuce", "pk:ghouse/ghouse_3_052", foot=[2, 1])]
HYDRO = P("v22_hydroponics", "pk:ghouse/ghouse_1_052", foot=[4, 2], sight=True)
PIPES = P("v22_pipes", "pk:ghouse/ghouse_1_018", foot=[8, 1])
POTTING = P("v22_potting", "pk:ghouse/ghouse_1_036", foot=[2, 1])
SEEDS = [P("v22_seeds", "pk:ghouse/ghouse_1_037", foot=[2, 1], search="shelf", title="стеллаж с семенами"),
         P("v22_ferts", "pk:ghouse/ghouse_1_038", foot=[2, 1], search="shelf", title="стеллаж с удобрениями")]
PLANT_SHELF = [P("v22_plant_shelf", "pk:ghouse/ghouse_2_024", foot=[2, 1]), P("v22_plant_shelf_b", "pk:ghouse/ghouse_2_027", foot=[2, 1])]
BIG_PLANT = P("v22_big_plant", "pk:ghouse/ghouse_2_046")
POTS = [P(f"v22_pot{i}", f"pk:ghouse/ghouse_1_{n:03d}") for i, n in enumerate((26, 27, 28, 29, 30))]
CONSOLE = P("v22_console", "pk:ghouse/ghouse_1_059", foot=[2, 1])
COOLER = P("v22_cooler", "pk:ghouse/ghouse_1_048")
WORKTABLE = P("v22_worktable", "pk:ghouse/ghouse_3_128", foot=[2, 1])
# жилой ярус
BUNKS = [P(f"v22_bunk{i}", f"pk:nbunk/nbunk_2_{n:03d}", foot=[2, 1], sight=True) for i, n in enumerate((0, 1, 2, 3))]
LOCKER = P("v22_locker", "pk:nbunk/nbunk_2_005", search="locker", title="шкафчик")
DESK_PC = [P("v22_desk_pc", "pk:nbunk/nbunk_2_016", foot=[2, 1]), P("v22_desk_pc_b", "pk:nbunk/nbunk_2_017", foot=[2, 1])]
GUN_RACK = P("v22_gun_rack", "pk:gcave/p1/14,8,2,2", foot=[2, 1], search="military", title="оружейная стойка")
TABLE = P("v22_table", "pk:west/west_2_000", foot=[2, 1])
CHAIR = P("v22_chair", "pk:west/west_2_001")
TANKS = P("v22_tanks", "pk:nbunk/nbunk_2_021", foot=[3, 1], sight=True)
# лаборатория и грибы
CHEM = [P("v22_chem", "pk:wlab/wlab_1_012", foot=[2, 1]), P("v22_chem_b", "pk:wlab/wlab_1_035", foot=[2, 1])]
VAT = P("v22_vat", "pk:wlab/wlab_1_000", sight=True)
LAB_CAB = P("v22_lab_cab", "pk:wlab/wlab_2_037", foot=[2, 1], sight=True, search="drawer", title="шкаф с реактивами")
MUSH = [P("v22_spore", "pk:gcave/p1/2,4,1,1", light={"r": 70, "color": [160, 255, 120], "at": [0.5, 0.5], "flicker": 0.2}),
        P("v22_spore_b", "pk:gcave/p1/2,5,1,1", light={"r": 60, "color": [200, 255, 140], "at": [0.5, 0.5], "flicker": 0.2}),
        P("v22_spore_c", "pk:gcave/p1/7,4,1,1")]
BIOHAZ = P("v22_biohazard", "pk:hosp/hosp_1_012")
BONES = P("v22_bones", "pk:grave/grave_2_022", block=False)

GRASS_FL = ["pk:zcity/zcity_f2_00"]
SAND = cells("destown/p2", [(0, 0), (1, 0), (0, 1), (1, 1)])
SOIL = cells("rvill/p2", [(0, 11), (1, 11), (0, 12), (1, 12)])
PLATES = cells("nbunk/p2", [(4, 8), (5, 9), (6, 10), (4, 10)])
TILE_W = ["pk:store/p1/12,0,1,1"]
MOLD = cells("gcave/p1", [(1, 4), (1, 5), (2, 6), (3, 6)])            # пол фермы, затянутый грибницей
GRATE = cells("nbunk/p2", [(0, 12), (1, 13), (2, 14), (3, 12)])
VWALL = "pk:nbunk/nbunk_w3_17"
GWALL = "pk:ghouse/ghouse_w3_09"


# ================================================================ поверхность
W, H = 46, 34
sf = CityMap(city, "vault22", "Убежище 22", W, H, start=(1, 26), seed=191, music="desert", world_pos=(2390, 470))
sf.floor_code("g", *GRASS_FL)
sf.floor_code("s", *SAND)
sf.floor_code("o", *SOIL)
sf.paint("s", 0, 0, W - 1, H - 1)
FLOOR = set()
for x0, y0, x1, y1 in ((0, 23, 24, 29), (10, 8, 38, 30)):
    FLOOR |= {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}
sf.paint("g", 10, 8, 38, 30)
sf.paint("o", 0, 25, 24, 27)
sf.paint("o", 21, 12, 24, 27)
sf.exits = [(0, y) for y in range(24, 29)]
sf.reserve(0, 24, 6, 28)
sf.put("x_vault_door22", 21, 7, check=False, allow_reserved=True)
sf.put("x_vault_sign22", 26, 9)
sf.portal([(22, 9), (23, 9)], "vault22_living", (20, 6), "Убежище 22")
sf.reserve(21, 9, 24, 13)
# огороды снаружи: грядки и плодовые кусты — жители выходят работать днём
for i, (x, y) in enumerate(((12, 14), (12, 18), (28, 14), (28, 18))):
    sf.put(ROWS[i], x, y)
sf.put(TOMATO[0], 32, 22)
sf.put(CUCUMBER[0], 13, 22)
for y in range(0, H, 2):
    for x in range(0, W, 2):
        if not {(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)} & FLOOR and not (21 <= x <= 24 and 6 <= y <= 9):
            sf.props.append([CLIFFS[(x * 7 + y) % 3], x, y])
            sf.blocked.update({(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)})
sf.npcs += [["v22_gardener_out", 17, 16]]
sf.grow(10, 8, 38, 30, 6, names=TREES)
sf.scatter(GRASS, 10, 8, 38, 30, 24)


# ================================================================ жилой ярус
W, H = 44, 32
lv = CityMap(city, "vault22_living", "Убежище 22: жилой ярус", W, H, start=(20, 6), seed=192, interior=True, music="lab")
lv.floor_code("F", *PLATES)
lv.floor_code("T", *TILE_W)
lv.wall_code("W", VWALL)
lv.room(1, 1, 43, 12, "W", "F")                       # входной зал
lv.room(1, 12, 15, 31, "W", "T")                      # столовая
lv.room(15, 12, 29, 31, "W", "F")                     # жилой блок
lv.room(29, 12, 43, 22, "W", "F")                     # пост охраны Хьюго
lv.room(29, 22, 43, 31, "W", "T")                     # кабинет смотрителя
lv.put("x_vault_gear22", 19, 3, force=True)
lv.portal([(19, 4), (20, 4)], "vault22", (22, 11), "Наружу")
lv.reserve(17, 4, 23, 7)
lv.opening(7, 12, 8, 14, "T")
lv.opening(19, 12, 20, 14, "F")
lv.opening(29, 16, 29, 17, "F")
lv.opening(36, 22, 37, 24, "T")
# входной зал: кадки с растениями, кулер, стенд «Еда будущего», проход в оранжереи на восток
for x in (4, 8, 13, 27, 31):
    lv.put(POTS[x % 5], x, 4)
lv.put(BIG_PLANT, 35, 4)
lv.put(COOLER, 38, 4)
lv.put(PLANT_SHELF[0], 3, 9)
lv.props.append(["x_ladder", 41, 9])
lv.portal([(41, 9)], "vault22_garden", (4, 5), "В оранжереи")
lv.reserve(39, 8, 42, 10)
lv.npcs += [["v22_greeter", 25, 8]]
# столовая: столы со стульями, салаты на стеллаже
for y in (17, 21, 25):
    lv.put(TABLE, 2, y)
    lv.put(CHAIR, 4, y)
    lv.put(TABLE, 10, y)
    lv.put(CHAIR, 12, y)
lv.put(TANKS, 3, 28)
lv.npcs += [["v22_cook", 7, 28], ["v22_kid", 12, 26]]
# жилой блок
for i, (x, y) in enumerate(((16, 17), (24, 16), (26, 19), (16, 22), (25, 23), (16, 28), (21, 28), (25, 28))):
    lv.put(BUNKS[i % 4], x, y)
lv.box(LOCKER, 27, 20, "шкафчик Сэм", {"книга по ботанике": 1, "сушёные травы": 2}, owner="sam_botanist")
lv.npcs += [["sam_botanist", 21, 22]]
# пост охраны: стол, оружейная стойка, койка Хьюго
lv.put(DESK_PC[0], 32, 15)
lv.box(GUN_RACK, 40, 15, "стойка охраны", {"патроны": 20, "10-мм пистолет": 1}, owner="hugo_lee")
lv.put(BUNKS[0], 38, 19)
lv.npcs += [["hugo_lee", 34, 18]]
# кабинет смотрителя
lv.put(DESK_PC[1], 33, 26)
lv.terminal(40, 25, "v22_overseer")
lv.put(PLANT_SHELF[1], 31, 29)
lv.npcs += [["overseer_keene", 36, 28]]


# ================================================================ оранжереи
W, H = 48, 34
gd = CityMap(city, "vault22_garden", "Убежище 22: оранжереи", W, H, start=(4, 5), seed=193, interior=True, music="lab")
gd.floor_code("F", *GRATE)
gd.floor_code("o", *SOIL)
gd.wall_code("W", GWALL)
gd.room(1, 1, 16, 33, "W", "F")                       # склад семян и гидропоника
gd.room(16, 1, 47, 17, "W", "o")                      # зал 1: овощи
gd.room(16, 17, 47, 33, "W", "o")                     # зал 2: томаты и огурцы — урожай гибнет
gd.props.append(["x_ladder", 4, 4])
gd.portal([(4, 4)], "vault22_living", (41, 10), "В жилой ярус")
gd.reserve(2, 4, 7, 7)
gd.opening(16, 8, 16, 9, "F")
gd.opening(16, 24, 16, 25, "F")
gd.opening(30, 17, 31, 17, "o")
# склад: стеллажи с семенами, гидропонная установка, трубы, рабочий стол
gd.put(SEEDS[0], 9, 4)
gd.put(SEEDS[1], 12, 4)
gd.put(HYDRO, 4, 12)
gd.put(POTTING, 11, 14)
gd.put(WORKTABLE, 4, 20)
gd.put(CONSOLE, 10, 20)
gd.terminal(13, 27, "v22_greenhouse")
gd.props.append(["x_ladder", 8, 31])
gd.portal([(8, 31)], "vault22_lab", (5, 5), "Вниз, в лабораторию",
          requires={"flag": "v22_lab_ok", "msg": "Люк вниз. Табличка: «Лаборатория. Только научный персонал». Замок свежий."})
gd.reserve(6, 30, 10, 32)
# зал 1: грядки рядами под лампами — здесь ещё всё растёт
for y in (5, 9, 13):
    for i, x in enumerate((19, 25, 31, 37)):
        gd.put(ROWS[(i + y) % len(ROWS)] if y != 9 else BEDS[i % 4], x, y)
gd.npcs += [["v22_farmer", 29, 11]]
# зал 2: томаты и огурцы на шпалерах — половина почернела
for i, x in enumerate((19, 23, 27, 35, 39, 43)):
    gd.put((TOMATO + CUCUMBER)[i % 4], x, 21)
for i, x in enumerate((19, 23, 35, 39)):
    gd.put(CABBAGE[i % 3], x, 26)
gd.put(BED_EMPTY, 27, 26)
gd.put(BED_EMPTY, 27, 30)
gd.put(MUSH[2], 44, 30)                               # на дальней грядке — первый гриб
gd.npcs += [["v22_scientist", 32, 24]]


# ================================================================ лаборатория и грибная ферма
W, H = 46, 32
lb = CityMap(city, "vault22_lab", "Убежище 22: лаборатория", W, H, start=(5, 5), seed=194, interior=True, music="vats")
lb.floor_code("T", *TILE_W)
lb.floor_code("o", *MOLD)
lb.wall_code("W", "pk:pmall/pmall_w3_10")
lb.wall_code("K", GWALL)
lb.room(1, 1, 20, 31, "W", "T")                       # лаборатория
lb.room(20, 1, 45, 31, "K", "o")                      # грибная ферма
lb.props.append(["x_ladder", 5, 4])
lb.portal([(5, 4)], "vault22_garden", (8, 30), "Наверх, в оранжереи")
lb.reserve(3, 4, 8, 7)
lb.opening(20, 15, 20, 16, "T")
# лаборатория: столы с реактивами, баки с пестицидом, шкафы, терминал журнала
for x in (4, 9, 14):
    lb.put(CHEM[x % 2], x, 10)
lb.put(VAT, 4, 15)
lb.put(VAT, 7, 15)
lb.put(LAB_CAB, 13, 15)
lb.put(BIOHAZ, 17, 15)
lb.terminal(16, 24, "v22_lab")
lb.box(LAB_CAB, 4, 24, "шкаф с пестицидами", {"канистра пестицида": 1}, owner="overseer_keene")
lb.put(BONES, 10, 28)
# грибная ферма: споры повсюду, корни по полу, светящиеся шляпки — а среди них то, что было людьми
for x, y in ((23, 5), (28, 9), (34, 4), (40, 8), (25, 14), (31, 18), (38, 15), (43, 22), (24, 25), (33, 28), (41, 28)):
    lb.put(MUSH[(x + y) % 3], x, y)
lb.terminal(42, 4, "v22_spore_valve")
lb.enemies += [["spore_carrier", 30, 10], ["spore_carrier", 38, 20], ["spore_carrier", 27, 27], ["radroach", 42, 14]]
for _, x, y in lb.enemies:
    lb.reserve(x, y, x, y)
lb.scatter(MUSH + [BONES], 21, 3, 44, 30, 40)            # грибница расползлась по всему залу


city.save(gap_exempt=("hugo_lee",))
L = json.load(open("data/locations.json", encoding="utf-8"))
L["vault22"].update({"world_name": "Убежище 22", "discover": True})
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
