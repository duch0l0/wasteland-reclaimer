"""
Убежище 15 (Fallout 1, за сорок лет до Выходца): убежище «разнородного населения». Дверь открыта с 2097-го,
жители разошлись — Арадеш, Ханы, Гадюки, Шакалы. Внутри остались девять.
Второй акт. Сценарий — docs/story.md, раздел 15.

  vault15        «Убежище 15» (56×40): холмы и скалы, дверь-шестерня в склоне; у подножия — лагерь
                 Шакалов: палатки, костёр, клетки с пленниками, которых продают «Детям Единства».
  vault15_atrium «Убежище 15: верхний ярус»: входной зал за баррикадой из столов и мешков, атриум,
                 столовая, жилой блок девяти, кабинет смотрителя с главным терминалом.
  vault15_lower  «Убежище 15: нижний ярус»: затопленные коридоры, склад, генераторная — генератор
                 заглох, жилой ярус живёт на аккумуляторах; радтараканы и крысы.

Наборы: nuclear-bunker (nbunk), underground-survivor-camp (ucamp), cult-temple (cult), desert-natural (desnat),
desert-town (destown), medieval-sewer (sewer).
Запуск из папки game_project:  .venv/bin/python tools/build_vault15.py
"""
import json

from citykit import City, CityMap

city = City("vault15", "Убежище 15")


def P(name, img, **kw):
    city.prop(name, img, **kw)
    return name


def cells(page, pts):
    return [f"pk:{page}/{x},{y},1,1" for x, y in pts]


CLIFFS = [P(f"v15_cliff{i}", f"pk:desnat/p1/{x},14,2,2", foot=[2, 2], sight=True) for i, x in enumerate((8, 10, 12))]
OUTCROP = P("v15_outcrop", "pk:desnat/p1/12,4,3,2", foot=[3, 2], sight=True)
TENTS = [P(f"v15_tent{i}", f"pk:ucamp/ucamp_2_{n:03d}", foot=[2, 1], sight=True) for i, n in enumerate((3, 8, 19, 21))]
SHACK = P("v15_shack", "pk:ucamp/ucamp_2_024", foot=[2, 1], sight=True)
CAMPFIRE = P("v15_campfire", "pk:ucamp/ucamp_2_040", foot=[2, 1],
             light={"r": 120, "color": [255, 150, 70], "at": [0.5, 0.5], "flicker": 0.35})
CAGE = P("v15_cage", "pk:cult/cult_3_020", block=False)            # пленник стоит внутри клетки
HANG_CAGE = P("v15_hang_cage", "pk:cult/cult_3_112")
SPIKES = P("v15_spikes", "pk:gcave/p1/12,8,2,2", foot=[2, 1])
SKULL_POLE = P("v15_skull_pole", "pk:gcave/p1/2,8,1,2")
LOOT = P("v15_loot", "pk:gcave/p1/10,10,2,2", search="military", title="добыча Шакалов")
TIRES = P("v15_tires", "pk:ucamp/ucamp_2_043", foot=[2, 1])
# убежище
BUNKS = [P(f"v15_bunk{i}", f"pk:nbunk/nbunk_2_{n:03d}", foot=[2, 1], sight=True) for i, n in enumerate((0, 1, 2, 3))]
BED = P("v15_bed", "pk:nbunk/nbunk_2_012", foot=[2, 1])
SHELF = P("v15_shelf", "pk:nbunk/nbunk_2_004", foot=[2, 1], sight=True, search="shelf", title="стеллаж с припасами")
LOCKER = P("v15_locker", "pk:nbunk/nbunk_2_005", search="locker", title="шкафчик")
LOCKER2 = P("v15_locker2", "pk:nbunk/nbunk_2_006", search="locker", title="шкаф")
TOOLBOARD = P("v15_toolboard", "pk:nbunk/nbunk_2_007", foot=[2, 1], sight=True, search="tools", title="щит с инструментами")
WORKBENCH = P("v15_workbench", "pk:nbunk/nbunk_2_014", foot=[2, 1])
DESK_PC = [P("v15_desk_pc", "pk:nbunk/nbunk_2_015", foot=[2, 1]), P("v15_desk_pc_b", "pk:nbunk/nbunk_2_016", foot=[2, 1]),
           P("v15_desk_pc_c", "pk:nbunk/nbunk_2_017", foot=[2, 1])]
DESK_CANS = P("v15_desk_cans", "pk:nbunk/nbunk_2_020", foot=[3, 1])
TANKS = P("v15_tanks", "pk:nbunk/nbunk_2_021", foot=[3, 1], sight=True)
GEN = [P("v15_gen", "pk:nbunk/nbunk_2_028", foot=[2, 2], sight=True), P("v15_gen_b", "pk:nbunk/nbunk_2_029", foot=[2, 2], sight=True)]
GEN_Y = P("v15_gen_yellow", "pk:nbunk/nbunk_2_027", foot=[2, 1], sight=True)
CRATES = [P(f"v15_crate{i}", f"pk:nbunk/nbunk_2_{n:03d}", search="crate", title="ящик") for i, n in enumerate((30, 31, 34, 35))]
TABLE = P("v15_table", "pk:west/west_2_000", foot=[2, 1])
CHAIR = P("v15_chair", "pk:west/west_2_001")
SANDBAGS = "x_sandbags"
BONES = [P("v15_bones", "pk:grave/grave_2_022", block=False), P("v15_bones_b", "pk:grave/grave_2_027", block=False)]
DEBRIS = P("v15_debris", "pk:pmall/pmall_2_042")

SAND = cells("destown/p2", [(0, 0), (1, 0), (0, 1), (1, 1)])
GRAVEL = cells("destown/p2", [(4, 0), (5, 0), (4, 1), (5, 1)])
PLATES = cells("nbunk/p2", [(4, 8), (5, 9), (6, 10), (4, 10)])
GRATE = cells("nbunk/p2", [(0, 12), (1, 13), (2, 14), (3, 12)])
CONCRETE = cells("nbunk/p2", [(0, 8), (1, 9)])
WATER = cells("sewer/p1", [(10, 1), (11, 1)])
VWALL = "pk:nbunk/nbunk_w3_17"


# ================================================================ поверхность
W, H = 56, 40
sf = CityMap(city, "vault15", "Убежище 15", W, H, start=(1, 30), seed=151, music="raiders", world_pos=(880, 780))
sf.floor_code("s", *SAND)
sf.floor_code("g", *GRAVEL)
sf.paint("s", 0, 0, W - 1, H - 1)
FLOOR = set()
for x0, y0, x1, y1 in ((0, 27, 30, 33),                # тропа с запада
                       (14, 8, 44, 30),                # долина перед дверью
                       (28, 26, 54, 38)):              # лощина Шакалов
    FLOOR |= {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}
sf.paint("g", 0, 29, 26, 31)
sf.paint("g", 24, 12, 27, 31)
sf.exits = [(0, y) for y in range(28, 33)]
sf.reserve(0, 28, 6, 32)
# дверь Убежища в северном склоне: скала с шестернёй, табличка
sf.put("x_vault_door15", 24, 7, check=False, allow_reserved=True)
sf.put("x_vault_sign15", 29, 9)
sf.portal([(25, 9), (26, 9)], "vault15_atrium", (20, 6), "Убежище 15")
sf.reserve(24, 9, 27, 13)
# лагерь Шакалов: палатки по кругу у костра, клетки с пленниками, частокол из шипов
sf.put(TENTS[0], 34, 28)
sf.put(TENTS[1], 40, 28)
sf.put(TENTS[2], 47, 30)
sf.put(SHACK, 50, 35)
sf.put(CAMPFIRE, 41, 32)
sf.put(CAGE, 33, 34)
sf.put(CAGE, 35, 34)
sf.blocked.update({(35, 34)})              # вторая клетка пустая — сквозь неё не пройти
sf.put(HANG_CAGE, 45, 27)
sf.put(SPIKES, 30, 30)
sf.put(SPIKES, 52, 28)
sf.put(SKULL_POLE, 38, 36)
sf.put(TIRES, 45, 36)
sf.box(LOOT, 48, 33, "добыча Шакалов", {"крышки": 60, "патроны": 15, "расписка культа": 1}, owner="jackal_boss")
sf.npcs += [["jackal_boss", 43, 30], ["captive_mira", 33, 34], ["jackal_a", 37, 31], ["jackal_b", 46, 33],
            ["jackal_c", 51, 31]]                       # Шакалы торгуют, пока им выгодно; драка — по слову вожака
# скалы вокруг долины
for y in range(0, H, 2):
    for x in range(0, W, 2):
        if not {(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)} & FLOOR and not (24 <= x <= 27 and 6 <= y <= 9):
            sf.props.append([CLIFFS[(x * 5 + y * 3) % 3], x, y])
            sf.blocked.update({(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)})
for x, y in ((16, 10), (40, 12), (18, 24)):
    sf.maybe(OUTCROP, x, y)
sf.scatter(["r_dry_bush", "r_rocks", "r_bones"], 14, 8, 44, 26, 12)


# ================================================================ верхний ярус
W, H = 44, 34
at = CityMap(city, "vault15_atrium", "Убежище 15: верхний ярус", W, H, start=(20, 6), seed=152, interior=True, music="lab")
at.floor_code("F", *PLATES)
at.floor_code("C", *CONCRETE)
at.wall_code("W", VWALL)
at.room(1, 1, 43, 12, "W", "C")                       # входной зал
at.room(1, 12, 16, 33, "W", "F")                      # столовая
at.room(16, 12, 30, 33, "W", "F")                     # атриум
at.room(30, 12, 43, 22, "W", "F")                     # кабинет смотрителя
at.room(30, 22, 43, 33, "W", "F")                     # жилой блок девяти
at.put("x_vault_gear15", 19, 3, force=True)
at.portal([(19, 4), (20, 4)], "vault15", (25, 11), "Наружу")
at.reserve(17, 4, 23, 7)
at.opening(22, 12, 23, 14, "F")
at.opening(16, 20, 16, 21, "F")
at.opening(30, 16, 30, 17, "F")
at.opening(30, 27, 30, 28, "F")
# баррикада поперёк зала: мешки и перевёрнутые столы, проход посередине — у прохода часовой
for x in list(range(10, 19)) + list(range(26, 35)):
    at.maybe(SANDBAGS, x, 9, check=False)
at.put(DEBRIS, 6, 6)
at.put(LOCKER, 38, 4)
at.put(LOCKER2, 39, 4)
for x, y in ((8, 4), (31, 6)):
    at.put(BONES[(x + y) % 2], x, y)
at.npcs += [["v15_sentry", 24, 10]]
# столовая: длинные столы со стульями, стеллаж с консервами, баки воды
for y in (17, 21, 25):
    at.put(TABLE, 4, y)
    at.put(TABLE, 9, y)
    at.put(CHAIR, 6, y)
    at.put(CHAIR, 11, y)
at.box(SHELF, 3, 15, "стеллаж столовой", {"консервы": 2})
at.put(TANKS, 11, 15)
at.npcs += [["v15_cook", 8, 29]]
# атриум: стол смотрителя-распорядителя, щит с инструментами, верстак — здесь чинят то, что ещё можно
at.put(WORKBENCH, 18, 16)
at.put(TOOLBOARD, 25, 15)
at.put(DESK_CANS, 18, 28)
at.npcs += [["beatrice", 23, 22], ["v15_tech", 19, 18]]
# кабинет смотрителя: главный терминал, стол, шкаф
at.put(DESK_PC[1], 33, 15)
at.terminal(39, 15, "v15_mainframe")
at.put(LOCKER2, 41, 18)
# жилой блок: двухъярусные койки рядами, тумбочки
for i, (x, y) in enumerate(((32, 25), (36, 25), (40, 25), (32, 30), (36, 30))):
    at.put(BUNKS[i % 4], x, y)
at.box(LOCKER, 41, 30, "шкафчик жильца", {"бинт": 1, "консервы": 1})
at.npcs += [["v15_old", 34, 28], ["v15_girl", 39, 28]]
# люк на нижний ярус — в атриуме, у южной стены
at.props.append(["x_ladder", 27, 31])
at.portal([(27, 31)], "vault15_lower", (6, 5), "Нижний ярус",
          requires={"flag": "v15_lower_ok", "msg": "Люк на нижний ярус задраен изнутри. Беатрис держит ключ при себе."})
at.reserve(26, 30, 28, 32)


# ================================================================ нижний ярус
W, H = 48, 34
lw = CityMap(city, "vault15_lower", "Убежище 15: нижний ярус", W, H, start=(6, 5), seed=153, interior=True, music="caves")
lw.floor_code("F", *GRATE)
lw.floor_code("C", *CONCRETE)
lw.floor_code("~", *WATER)
lw.wall_code("W", VWALL)
lw.water_codes = ("~",)
lw.room(1, 1, 18, 33, "W", "F")                       # технический коридор
lw.room(18, 1, 47, 16, "W", "C")                      # склад
lw.room(18, 16, 47, 33, "W", "F")                     # генераторная — затоплена
lw.props.append(["x_ladder", 6, 4])
lw.portal([(6, 4)], "vault15_atrium", (27, 32), "Наверх, в атриум")
lw.reserve(4, 4, 9, 7)
lw.opening(18, 8, 18, 9, "C")
lw.opening(18, 25, 18, 26, "F")
lw.paint("~", 3, 14, 16, 22)                          # прорвало трубу — коридор залит
lw.paint("F", 9, 14, 10, 22)                          # по трубам вдоль стены — сухая тропа
lw.paint("~", 22, 26, 38, 31)
# склад: стеллажи и ящики рядами — часть разграблена Шакалами (у пролома)
for x in (21, 25, 29):
    lw.put(SHELF, x, 5)
for x, y in ((34, 5), (36, 5), (34, 10), (40, 10)):
    lw.put(CRATES[(x + y) % 4], x, y)
lw.box(CRATES[0], 44, 5, "ящик с предохранителями", {"предохранитель Vault-Tec": 1, "изолента": 1})
lw.put(DEBRIS, 44, 12)
# генераторная: два генератора, один заглох; щит управления; аккумуляторный бак
lw.put(GEN[0], 22, 20)
lw.put(GEN[1], 27, 20)
lw.put(GEN_Y, 40, 20)
lw.put(TOOLBOARD, 33, 19)
lw.terminal(44, 20, "v15_generator")
for x, y in ((5, 27), (12, 30)):
    lw.put(BONES[(x + y) % 2], x, y)
lw.enemies += [["radroach", 12, 10], ["radroach", 8, 25], ["rat", 30, 8], ["rat", 38, 12], ["radroach", 42, 28],
               ["radroach", 25, 24]]

city.save()
L = json.load(open("data/locations.json", encoding="utf-8"))
L["vault15"].update({"world_name": "Убежище 15", "discover": True})
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
