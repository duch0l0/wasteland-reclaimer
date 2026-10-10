"""
Убежище 11 (Fallout: New Vegas) — убежище жребия. Двадцать лет жители каждый год выбирали смотрителя, которого
потом отдавали машине: иначе, говорил компьютер, умрут все. Последние пятеро отказались выбирать — и дверь
открылась: угроза была ложью, опыт проверял, решатся ли люди сказать «нет». Выжившие ушли — и основали Ниптон.
В 2121 году убежище пустое; квест «Кровь Убежища 11» (docs/story.md, раздел 17б).

  vault11         склон над пересохшим руслом, дверь-шестерня в скале с цифрой 11.
  vault11_hall    «Зал выборов»: кресло смотрителя на помосте, плакаты шести блоков, скелеты у стен;
                  терминал выборов (хроника, приказ 745), жилой блок.
  vault11_core    «Вычислительный центр»: терминал эксперимента — правда о двери; сейф смотрителя.

Наборы: nuclear-bunker (nbunk), desert-natural (desnat), wasteland-laboratory (wlab), graveyard (grave).
Запуск из папки game_project:  .venv/bin/python tools/build_vault11.py
"""
import json

from citykit import City, CityMap, tech_scenes

city = City("vault11", "Убежище 11")


def P(name, img, **kw):
    city.prop(name, img, **kw)
    return name


def cells(page, pts):
    return [f"pk:{page}/{x},{y},1,1" for x, y in pts]


CLIFFS = [P(f"v11_cliff{i}", f"pk:desnat/p1/{x},14,2,2", foot=[2, 2], sight=True) for i, x in enumerate((8, 10, 12))]
BUNKS = [P(f"v11_bunk{i}", f"pk:nbunk/nbunk_2_{n:03d}", foot=[2, 1], sight=True) for i, n in enumerate((0, 1, 2, 3))]
LOCKER = P("v11_locker", "pk:nbunk/nbunk_2_005", search="locker", title="шкафчик")
DESK_PC = [P("v11_desk_pc", "pk:nbunk/nbunk_2_016", foot=[2, 1]), P("v11_desk_pc_b", "pk:nbunk/nbunk_2_017", foot=[2, 1])]
TABLE = P("v11_table", "pk:west/west_2_000", foot=[2, 1])
CHAIR = P("v11_chair", "pk:west/west_2_001")
THRONE = P("v11_throne", "pk:lrest/lrest_1_041")                 # кресло смотрителя на помосте
POSTERS = [P(f"v11_poster{i}", f"pk:lrest/lrest_3_{n:03d}", block=False) for i, n in enumerate((11, 12))]
SERVERS = [P("v11_server", "pk:npower/npower_2_042"), P("v11_server_b", "pk:npower/npower_2_036", foot=[2, 1])]
SAFE = P("v11_safe", "pk:west/west_2_105", search="military", title="сейф смотрителя")
BONES = [P("v11_bones", "pk:grave/grave_2_022", block=False), P("v11_bones_b", "pk:grave/grave_2_027", block=False)]

SAND = cells("destown/p2", [(0, 0), (1, 0), (0, 1), (1, 1)])
PLATES = cells("nbunk/p2", [(4, 8), (5, 9), (6, 10), (4, 10)])
GRATE = cells("nbunk/p2", [(0, 12), (1, 13), (2, 14), (3, 12)])
CARPET = ["pk:lrest/p1/0,12,1,1"]
VWALL = "pk:nbunk/nbunk_w3_17"


# ================================================================ склон
W, H = 40, 30
sf = CityMap(city, "vault11", "Убежище 11", W, H, start=(1, 22), seed=111, music="desert", world_pos=(2330, 820))
sf.floor_code("s", *SAND)
sf.paint("s", 0, 0, W - 1, H - 1)
FLOOR = set()
for x0, y0, x1, y1 in ((0, 19, 22, 25), (14, 8, 30, 25)):
    FLOOR |= {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}
sf.exits = [(0, y) for y in range(20, 25)]
sf.reserve(0, 20, 6, 24)
sf.put("x_vault_door11", 19, 7, check=False, allow_reserved=True)
sf.put("x_vault_sign11", 24, 10)
sf.portal([(20, 9), (21, 9)], "vault11_hall", (20, 6), "Убежище 11")
sf.reserve(19, 9, 22, 13)
for x, y in ((16, 18), (27, 14), (25, 22)):
    sf.maybe("r_rocks", x, y)
sf.maybe(BONES[0], 18, 15)
sf.floor_code("Q", *["pk:desnat/p1/0,0,1,1", "pk:desnat/p1/1,0,1,1", "pk:desnat/p1/0,1,1,1"])   # верх плато — песок, как верх скал
sf.cliff_walls(CLIFFS, FLOOR, skip=lambda x, y: 19 <= x <= 22 and 6 <= y <= 9, decor=["r_rocks", "r_dry_bush", "r_bones"], plateau="Q")
sf.enemies += [["radroach", 24, 18], ["radroach", 17, 22]]


# ================================================================ зал выборов и жилой блок
W, H = 44, 32
hl = CityMap(city, "vault11_hall", "Убежище 11: зал выборов", W, H, start=(20, 6), seed=112, interior=True,
             music="lab", night=[70, 70, 80])
hl.floor_code("F", *PLATES)
hl.floor_code("C", *CARPET)
hl.wall_code("W", VWALL)
hl.room(1, 1, 43, 12, "W", "F")                       # входной зал
hl.room(1, 12, 28, 31, "W", "C")                      # зал выборов: ковёр, помост
hl.room(28, 12, 43, 31, "W", "F")                     # жилой блок
hl.put("x_vault_gear11", 19, 3, force=True)
hl.portal([(19, 4), (20, 4)], "vault11", (20, 11), "Наружу")
hl.reserve(17, 4, 23, 7)
hl.opening(13, 12, 14, 14, "C")
hl.opening(28, 20, 28, 21, "F")
hl.props.append(["x_ladder", 40, 4])
hl.portal([(40, 4)], "vault11_core", (6, 5), "Вниз, к вычислительному центру")
hl.reserve(38, 4, 42, 7)
# помост: кресло смотрителя, перед ним — ряды стульев; на стенах плакаты блоков
hl.put(THRONE, 5, 16)
for x, y in ((8, 14), (18, 14), (6, 26), (22, 26)):
    hl.put(POSTERS[(x + y) % 2], x, y)
for row in (21, 24):
    for x in (6, 10, 16, 20):
        hl.put(CHAIR, x, row)
hl.terminal(9, 16, "v11_election")
for x, y in ((4, 18), (24, 20), (9, 29), (19, 30), (25, 15)):
    hl.put(BONES[(x + y) % 2], x, y)
# жилой блок: койки, шкафчики
for y in (15, 20, 25):
    hl.put(BUNKS[(y // 5) % 4], 31, y)
    hl.put(BUNKS[(y // 5 + 1) % 4], 37, y)
hl.box(LOCKER, 41, 14, "шкафчик Кэтрин Стоун", {"дневник Кэтрин Стоун": 1, "чистая вода": 1})
hl.box(LOCKER, 41, 28, "шкафчик", {"консервы": 2, "бинт": 1})
hl.enemies += [["feral", 34, 18], ["feral", 22, 28], ["radroach", 8, 9]]


# ================================================================ вычислительный центр
W, H = 36, 24
cr = CityMap(city, "vault11_core", "Убежище 11: вычислительный центр", W, H, start=(6, 5), seed=113, interior=True,
             music="vats", night=[50, 60, 80])
cr.floor_code("G", *GRATE)
cr.wall_code("W", VWALL)
cr.room(1, 1, 35, 23, "W", "G")
cr.props.append(["x_ladder", 6, 4])
cr.portal([(6, 4)], "vault11_hall", (40, 6), "Наверх, в зал выборов")
cr.reserve(4, 4, 9, 7)
for x in (14, 18, 22, 26, 30):
    cr.put(SERVERS[0], x, 3)
cr.put(SERVERS[1], 30, 12)
cr.put(DESK_PC[0], 18, 10)
cr.terminal(22, 10, "v11_core")
cr.box(SAFE, 32, 20, "сейф смотрителя", {"крышки": 220, "жетон смотрителя Убежища 11": 1, "стимулятор": 2},
       requires={"item": "отмычка", "msg": "Сейф смотрителя. Пятеро выживших так его и не вскрыли."})
cr.put(BONES[0], 20, 15)
cr.enemies += [["robot_skel", 26, 16]]

print("техзал cr:", cr.dress_empty(tech_scenes(city, "v11"), ground="G", block=7, margin=1, chance=1.0))

city.save()
L = json.load(open("data/locations.json", encoding="utf-8"))
L["vault11"].update({"world_name": "Убежище 11", "discover": True})
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
