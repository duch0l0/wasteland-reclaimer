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
from vaultkit import Lamps

city = City("vault11", "Убежище 11")
LM = Lamps(city)


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

SAND = ["pk:desnat/p1/0,0,1,1", "pk:desnat/p1/1,0,1,1", "pk:desnat/p1/0,1,1,1"]   # песок под цвет окружающей пустыни
PLATES = cells("nbunk/p2", [(4, 8), (5, 9), (6, 10), (4, 10)])
GRATE = cells("nbunk/p2", [(0, 12), (1, 13), (2, 14), (3, 12)])
CARPET = ["pk:lrest/p1/0,12,1,1"]
VWALL = "pk:nbunk/nbunk_w3_17"


# ================================================================ склон
W, H = 40, 30
sf = CityMap(city, "vault11", "Убежище 11", W, H, start=(1, 22), seed=111, music="desert", world_pos=(2330, 820), night=[150, 142, 145])
sf.floor_code("s", *SAND)
sf.paint("s", 0, 0, W - 1, H - 1)
FLOOR = set()
for x0, y0, x1, y1 in ((0, 19, 22, 25), (14, 8, 30, 25)):
    FLOOR |= {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}
sf.exits = [(0, y) for y in range(20, 25)]
sf.reserve(0, 20, 6, 24)
sf.put("x_vault_door11", 20, 6, check=False, allow_reserved=True)   # дверь врезана в фасад обрыва
sf.put("x_vault_sign11", 24, 10)
sf.portal([(21, 8), (22, 8)], "vault11_hall", (20, 6), "Убежище 11")
sf.reserve(19, 9, 22, 13)
for x, y in ((16, 18), (27, 14), (25, 22)):
    sf.maybe("r_rocks", x, y)
sf.maybe(BONES[0], 18, 15)
sf.floor_code("Q", *["pk:desnat/p1/0,0,1,1", "pk:desnat/p1/1,0,1,1", "pk:desnat/p1/0,1,1,1"])   # верх плато — песок, как верх скал
sf.cliff_walls(CLIFFS, FLOOR, skip=lambda x, y: 20 <= x <= 23 and 6 <= y <= 7, decor=["r_rocks", "r_dry_bush", "r_bones"], plateau="Q")

# склон после жребия: ступени «тех, кто вышел» — колея на восток, остатки их первого лагеря, пять крестов у скалы, табличка «Ниптон»
sf.floor_code("t", "pk:desnat/p1/4,4,1,1", "pk:desnat/p1/5,4,1,1", "pk:desnat/p1/6,4,1,1")
sf.floor_code("q", "pk:desnat/p1/10,4,1,1")
sf.patchwork("s", ["t"], 10, 2, 4, seed=71)
sf.patchwork("s", ["q"], 7, 1, 2, seed=72)
for x in range(7, 22, 2):
    sf.maybe("x_vd_ruts_h", x, 22, check=False)
for x, y in ((9, 21), (12, 23), (16, 21), (19, 23), (23, 24)):
    sf.maybe("x_vd_steps", x, y, check=False)
for i, x in enumerate((26, 28, 30, 32, 34)):
    sf.maybe("x_cross" if i % 2 == 0 else "x_tombstone", x, 12 + i % 2)
sf.maybe("r_tent_low", 30, 19)
sf.maybe("campfire", 28, 21)
sf.maybe("r_logs", 27, 22)
sf.maybe("barrel_wood", 31, 21)
sf.maybe("pile_bags", 33, 20)
for x, y in ((6, 8), (10, 6), (34, 7), (36, 12), (4, 14), (3, 27), (33, 26), (37, 22)):
    sf.maybe(["r_dtree_a", "r_dtree_b", "r_dry_bush"][(x + y) % 3], x, y)
sf.scatter(["r_dry_bush", "r_rocks", "r_bones", "r_trash", "pile_cans"], 1, 1, 38, 28, 22)
sf.enemies += [["radroach", 24, 18], ["radroach", 17, 22]]


# ================================================================ зал выборов и жилой блок
W, H = 44, 32
hl = CityMap(city, "vault11_hall", "Убежище 11: зал выборов", W, H, start=(20, 6), seed=112, interior=True,
             music="lab", night=[112, 118, 128])
hl.floor_code("F", *PLATES)
hl.floor_code("C", *CARPET)
hl.floor_code("D", "pk:lrest/lrest_f1_00")                  # помост — шахматная плитка
hl.floor_code("A", "pk:lrest/lrest_f1_01")                  # проход к помосту
hl.wall_code("W", VWALL)
hl.wall_code("E", "pk:nbunk/nbunk_w3_02")
hl.wall_code("L", "pk:nbunk/nbunk_w3_10")
hl.room(1, 1, 43, 12, "W", "F")                       # входной зал
hl.room(1, 12, 28, 31, "E", "C")                      # зал выборов: ковёр, помост
hl.room(28, 12, 43, 31, "L", "F")                     # жилой блок
hl.put("x_vault_gear11", 19, 3, force=True)
hl.portal([(19, 4), (20, 4)], "vault11", (20, 11), "Наружу")
hl.reserve(17, 4, 23, 7)
hl.opening(13, 12, 14, 14, "C")
hl.opening(28, 20, 28, 21, "F")
hl.props.append(["x_ladder", 40, 4])
hl.portal([(40, 4)], "vault11_core", (6, 5), "Вниз, к вычислительному центру")
hl.reserve(38, 4, 42, 7)
# помост: кресло смотрителя, перед ним — ряды стульев; на стенах плакаты блоков
hl.paint("D", 3, 15, 10, 19)
hl.paint("A", 13, 15, 14, 30)
hl.put(THRONE, 5, 16)
for x, y in ((8, 14), (18, 14), (6, 26), (22, 26)):
    hl.put(POSTERS[(x + y) % 2], x, y)
for row in (21, 24):
    for x in (6, 10, 16, 20):
        hl.put(CHAIR, x, row)
hl.terminal(9, 16, "v11_election")
# входной зал: приёмная — ряды шкафов у стен, стол дежурного, ящики, брошенные вещи
hl.put(TABLE, 10, 8)
hl.put(CHAIR, 10, 9)
hl.put(TABLE, 30, 8)
for x, y in ((5, 9), (14, 9), (26, 5), (34, 10), (41, 9), (3, 6)):
    hl.maybe(LOCKER, x, y)
hl.scatter(["crate", "crate_broken", "barrel_wood", "r_trash"], 2, 5, 42, 11, 8)
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
             music="vats", night=[64, 76, 96])
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

# ---- атмосфера: зал выборов — холодный казённый свет и одна лампа над помостом; вычислительный центр — синий и красный
LM.lamps(hl, "cold", [(8, 3), (16, 3), (29, 3), (36, 3), (7, 18), (21, 18), (7, 26), (21, 26), (34, 16), (40, 16), (34, 26), (40, 26)])
LM.lamps(hl, "warm", [(14, 16), (14, 26)])
LM.decals(hl, "x_vd_plaque", [(23, 2)])
LM.decals(hl, "x_vd_num11", [(12, 2), (30, 2)])
LM.decals(hl, "x_vd_hz_v", [(22, 6), (23, 6), (22, 8), (23, 8)])
LM.decals(hl, "x_vd_tally", [(5, 14), (7, 14), (10, 14)])          # двадцать зарубок — двадцать выборов
LM.decals(hl, "x_vd_plaque", [(16, 14), (22, 14)])
LM.lamp(hl, "amber", 7, 17)
LM.lamp(hl, "amber", 4, 18)
hl.maybe(TABLE, 18, 17)                                             # стол счётной комиссии
hl.maybe(CHAIR, 18, 18)
hl.maybe(CHAIR, 20, 18)
hl.maybe("candles", 19, 17, check=False)
hl.maybe(TABLE, 18, 25)
hl.maybe(CHAIR, 19, 26)
for y in range(16, 30, 2):                                          # свечи вдоль прохода — поминальные
    hl.maybe("candles", 12, y, check=False)
hl.maybe("crate_broken", 24, 22)
hl.maybe("crate_broken", 3, 24)
LM.decals(hl, "x_vd_oil0", [(10, 22), (18, 28)])
LM.lamps(cr, "cold", [(6, 6), (14, 6), (22, 6), (30, 6), (8, 16), (18, 16), (28, 16)])
LM.lamps(cr, "red", [(4, 20), (33, 20), (18, 21)])
for x in (9, 12, 15):                                              # ряды стоек — «машина», которой отдавали смотрителей
    cr.maybe(SERVERS[0], x, 15)
for x in (22, 25, 28):
    cr.maybe(SERVERS[0], x, 15)
for x in (4, 5):
    cr.maybe(SERVERS[1], x * 2 + 8, 20)
LM.lamps(cr, "green", [(20, 13), (20, 19), (10, 12), (28, 12)])
LM.decals(cr, "x_vd_cab_v", [(20, y) for y in range(11, 20)])
LM.decals(cr, "x_vd_cab_h", [(x, 10) for x in range(8, 30)])
LM.decals(cr, "x_vd_sparks", [(26, 14)])
LM.decals(cr, "x_vd_blood0", [(15, 18)])

LM.doors(hl)
LM.doors(cr)
city.save()
L = json.load(open("data/locations.json", encoding="utf-8"))
L["vault11"].update({"world_name": "Убежище 11", "discover": True})
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
