"""
Генератор карты Бейкера (data/maps/baker.json) — вторая глава.

Районы (84×60 клеток), подробно — docs/story.md, раздел «Бейкер»:
  трасса I-15     — через весь город с запада на восток, выходы на обоих концах;
                    у западного въезда блокпост культа (двое в балахонах);
  центр           — площадь с Термометром, бак с водой, доска объявлений;
  север           — миссия «Детей Единства» за кирпичной оградой: молельня (брат Ансельм,
                    «сканер»), кельи за решёткой (дед Эймос), шатры послушников (Искра);
                    ворота на юг, к площади, и калитка на север, в дюны;
  запад           — закусочная «Безумный грек» (Ник, пьющий брат Тобиас);
  восток у трассы — мотель «Последняя миля» (староста Хэтти Мур);
  юг              — лачуги и палатки жителей;
  юго-восток      — свалка машин, трейлер «скупщика» Холлиса;
  северо-восток   — бункер склада «Бейкер-7» в дюнах: тройной замок, спуск — портал.

Мимо западной стены миссии в дюны идёт тропа — к задней калитке (путь «Тень»).
Кто ещё появляется в городе по ходу сюжета (Лира, Панк, Сайлас, Шрам, дед у склада) —
ставит src/game/baker.py.

Запуск из папки game_project:  .venv/bin/python tools/build_baker.py
"""
from mapkit import MapKit, WALLS_INTACT, BENCHES, CRATES, BARRELS, STONES, FLOOR_BITS, GRASS, BUSHES

W, H = 84, 60
m = MapKit(W, H, start=(3, 39), seed=21)
rnd = m.rnd
put, box, terminal, scatter = m.put, m.box, m.terminal, m.scatter
m.exits = [(0, y) for y in range(38, 42)] + [(W - 1, y) for y in range(38, 42)]

DRY = ["r_dry_bush"] + BUSHES   # у сухой травы «War ruins» под картинкой квадрат песка — не берём
TREES = [f"r_dtree_{c}" for c in "abcdefg"]

# ------------------------------------------------------------ кто где (резерв — до расстановки)
m.npcs += [
    ["anselm", 37, 11],        # брат Ансельм у алтаря
    ["amos", 51, 13],          # дед — в келье за решёткой
    ["iskra", 46, 20],         # Искра у шатров послушников
    ["nick", 7, 29],           # Ник Грек за стойкой
    ["tobias", 14, 32],        # брат-ключник Тобиас пьёт тайком
    ["hattie", 63, 30],        # староста в мотеле
    ["hollis", 66, 50],        # «скупщик» на свалке
    ["baker_folk_a", 9, 50], ["baker_folk_b", 17, 51], ["baker_kid", 24, 51],
    ["baker_folk_c", 31, 52], ["baker_folk_d", 38, 52], ["baker_folk_e", 46, 51],
]
m.enemies += [
    ["cult_guard", 22, 36], ["cult_guard", 22, 43],    # блокпост на трассе
    ["cult_guard", 38, 22], ["cultist", 31, 23],       # двор миссии: у ворот и у шатров
    ["cultist", 32, 15],                               # в молельне
]
for _, x, y in m.enemies + m.npcs:
    m.reserve(x, y, x, y)

# ------------------------------------------------------------ дороги и площади
m.paint("a", 0, 38, W - 1, 41)                         # трасса I-15
for x in range(0, W, 4):
    m.ground[39][x] = m.ground[39][x + 1] = "h"
m.paint("g", 0, 37, W - 1, 37)
m.paint("g", 0, 42, W - 1, 42)
m.paint("g", 30, 26, 50, 36)                           # площадь у Термометра
m.paint("g", 39, 25, 42, 25)                           # к воротам миссии
m.paint("g", 71, 14, 75, 22)                           # подъезд к бункеру
m.reserve(0, 37, W - 1, 42)
m.reserve(0, 34, 6, 44)                                # въезд — старт
m.reserve(39, 25, 42, 36)                              # проход от ворот миссии к трассе
m.reserve(22, 2, 25, 36)                               # тропа вдоль западной стены миссии в дюны
m.reserve(26, 2, 57, 6)                                # дюны за миссией: путь к калитке
m.reserve(55, 8, 56, 19)                               # двор вдоль восточной стены: от калитки к кельям


# ------------------------------------------------------------ миссия «Детей Единства»
m.wall_row(WALLS_INTACT["brick"], 26, 57, 7, gaps={50, 51})        # северная стена, калитка
m.wall_row(WALLS_INTACT["brick"], 26, 57, 24, gaps={40, 41})       # южная стена, ворота
m.side_wall("brick", "w", 26, 8, 23)
m.side_wall("brick", "e", 57, 8, 23)
put("bar_fence_c", 50, 7, force=True)                  # калитка в дюны (гнилой засов — ломом)
back_gate = len(m.props) - 1
put("bar_fence_b", 40, 24, force=True)                 # ворота
front_gate = len(m.props) - 1
m.paint("c", 27, 8, 56, 23)
m.paint("d", 27, 19, 56, 23)                           # двор — земля

# молельня: алтарь, скамьи с проходом посередине, «сканер» у стены
ix0, iy0, ix1, iy1 = m.building(29, 9, 16, 10, "brick", south=(6,), sign="ЕДИНСТВО")
terminal(31, 10, "baker_scanner")
for x in (35, 38):
    put("candles", x, 10, check=False)
put("display_case_b", 36, 10, check=False)             # алтарь
for y in (13, 15):
    for x in (30, 32, 39, 41):
        put(rnd.choice(BENCHES), x, y, check=False)
box("metal_chest", 42, 10, "сундук Ансельма", {"крышки": 80, "стимулятор": 1, "святая вода": 2}, owner="anselm")
put("lantern_lit", 30, 16, check=False)
put("lantern_lit", 43, 16, check=False)

# кельи: решётка на двери, за ней дед
ix0, iy0, ix1, iy1 = m.building(47, 10, 8, 8, "concrete", south=(2,), roof=True, sign="КЕЛЬИ")
put("bar_fence_a", 49, 17, force=True)
cell_gate = len(m.props) - 1
put("bed_frame", 52, 11, check=False)
put("bucket", 48, 11, check=False)
put("pile_rags", 52, 15, check=False)

# двор: шатры послушников, костёр, бочка «святой воды»
for name, x, y in [("r_tent_beige", 28, 20), ("r_tent_purple", 31, 20), ("r_tent_low", 44, 21),
                   ("r_tent_beige", 47, 22), ("r_tent_yellow", 51, 21)]:
    put(name, x, y)
put("firewood", 35, 21)
box("barrel_wood", 33, 22, "бочка «святой воды»", {"святая вода": 3}, owner="anselm")
scatter(CRATES + ["bucket"], 27, 19, 53, 23, 3)

# ------------------------------------------------------------ площадь и Термометр
put("x_thermometer", 36, 30, check=False)
put("water_tank_a", 44, 28, check=False)
box("barrel_wood", 47, 30, "колонка с водой", {"чистая вода": 2})
put("x_board", 33, 35, check=False)
m.terminals.append({"prop": len(m.props) - 1, "id": "doc:doc_baker_board"})
for x, y in ((31, 29), (46, 34)):
    put(rnd.choice(BENCHES), x, y)
put("r_pole_wire", 35, 27)
put("r_billboard", 49, 27)

# ------------------------------------------------------------ закусочная «Безумный грек»
ix0, iy0, ix1, iy1 = m.building(4, 27, 14, 9, "planks", south=(4,), sign="БЕЗУМНЫЙ ГРЕК")
for x in (5, 9):
    put("counter", x, 30, check=False)
put("shelf_goods", 5, 28, check=False)
put("barrel_wood", 10, 28, check=False)
box("cabinet_small", 12, 28, "шкафчик Ника", {"самогон": 2, "крышки": 25}, owner="nick")
for tx, ty in ((13, 33), (15, 30), (6, 33)):
    put(rnd.choice(["round_table_42", "round_table_45", "round_table_58"]), tx, ty, check=False)
    put(rnd.choice(["stool_round_41", "stool_round_55", "stool_round_56"]), tx + 1, ty, check=False)
put("pile_bottles", 16, 28)

# ------------------------------------------------------------ блокпост культа на въезде
for x, y in ((20, 36), (20, 43)):
    put("r_sandbag_row", x, y, allow_reserved=True, check=False)
put("r_sandbags", 23, 35, allow_reserved=True, check=False)
put("r_barrels", 19, 44, allow_reserved=True, check=False)

# ------------------------------------------------------------ мотель «Последняя миля»
ix0, iy0, ix1, iy1 = m.building(60, 27, 18, 9, "concrete", south=(4, 12), sign="МОТЕЛЬ")
for x in (66, 70, 74):
    put("bed", x, 28, check=False)
    put("nightstand", x + 2, 28, check=False)
put("counter", 62, 31, check=False)
put("table_2", 64, 33, check=False)
put("chair_wood", 65, 33, check=False)
box("filecab_2", 61, 28, "конторка Хэтти", {"крышки": 40, "бинт": 2, "долговая книга": 1}, owner="hattie")
put("r_car_red", 63, 24)
put("r_pickup", 71, 24)

# ------------------------------------------------------------ юг: лачуги и палатки жителей
homes = [("r_shack", 4, 46), ("r_shack_tin", 11, 46), ("r_cabin", 20, 46), ("r_shed_tin", 26, 46),
         ("r_hut", 33, 46), ("r_tent_big", 40, 47), ("r_shanty", 47, 46),
         ("r_cabin_b", 5, 55), ("r_house_wood", 11, 55), ("r_tent_green", 18, 56), ("r_tent_orange", 22, 56),
         ("r_shack_e", 28, 55), ("r_cabin_d", 34, 55), ("r_shack_f", 42, 55)]
for name, x, y in homes:
    put(name, x, y)
for name, x, y in [("r_dumpster", 16, 48), ("r_trash_can", 30, 49), ("r_logs", 37, 50), ("r_barrels", 45, 54),
                   ("r_dumpster_b", 26, 58), ("r_bin", 9, 53)]:
    put(name, x, y)
box("metal_box_open", 14, 53, "ящик у лачуги", {"ткань": 1, "крышки": 4})
scatter(["firewood", "bucket", "r_planks", "r_planks_b"], 3, 44, 50, 58, 5)

# ------------------------------------------------------------ юго-восток: свалка машин и Холлис
for name, x, y in [("r_rv", 56, 46), ("r_car_wreck", 64, 45), ("r_junk_mound", 72, 46), ("r_tanker", 56, 53),
                   ("r_van", 68, 54), ("r_camper", 76, 52), ("r_car_b", 63, 57), ("r_car_c", 71, 57),
                   ("r_moto", 79, 47), ("r_car_wreck", 77, 57)]:
    put(name, x, y)
box("metal_chest", 61, 50, "сундук Холлиса", {"крышки": 60, "стимулятор": 2, "балахон послушника": 1},
    owner="hollis")
put("r_awning", 64, 49)
put("table_2", 67, 51)
put("chair_wood", 68, 51)

# ------------------------------------------------------------ северо-восток: склад «Бейкер-7»
put("r_bunker", 70, 12, check=False)
m.portal([(72, 14), (73, 14)], "baker7", (4, 18), "Склад «Бейкер-7»",
         requires={"flag": "baker7_open",
                   "msg": "Бронедверь склада. Табло: «ДОСТУП: ПЕРСОНАЛ МАРИПОЗЫ. СЕТЧАТКА · ГОЛОС · КОД»."})
terminal(75, 15, "baker7_lock")
for x, y in ((66, 16), (78, 16)):
    put("x_sandbags", x, y, check=False)
put("r_army_truck", 62, 8)
put("r_derrick", 79, 5)
put("r_water_tower_b", 65, 20)
scatter(["ammo_box", "crate", "crate_b"], 62, 15, 80, 22, 3)

# ------------------------------------------------------------ по всему городу: пустыня
for _ in range(14):
    put(rnd.choice(TREES), rnd.randint(2, W - 3), rnd.randint(2, H - 3))
m.grow(1, 1, W - 2, H - 2, 34, DRY)
m.grow(1, 1, W - 2, H - 2, 8, DRY + GRASS[:4])
scatter(["r_rocks", "r_bones", "r_trash"] + STONES, 1, 1, W - 2, H - 2, 18)
scatter(FLOOR_BITS[:5] + CRATES[:2] + BARRELS[:3], 1, 43, W - 2, H - 2, 8)
for x in range(9, W - 4, 14):                          # столбы вдоль трассы
    put(rnd.choice(["r_pole_wire", "r_pole_broken"]), x, 36, allow_reserved=True)

# ------------------------------------------------------------ проверки и запись
gate_tiles = [t for i in (back_gate, front_gate, cell_gate) for t in m.footprint(*m.props[i])]
reach = m.check(passable=gate_tiles, gap_exempt=("anselm", "iskra", "amos"))   # культ нейтрален, пока не разозлить
m.save("data/maps/baker.json", tint=[255, 238, 206],
       gates=[{"prop": front_gate, "flag": "mission_gate_open",
               "msg": "Ворота миссии заперты изнутри. За решёткой — шатры и белые балахоны."},
              {"prop": back_gate, "flag": "mission_back_open", "pry": True,   # лом у героя всегда при себе
               "open_msg": "Вы поддеваете гнилой засов ломом. Калитка со скрипом подаётся."},
              {"prop": cell_gate, "flag": "cells_open", "key": "ключ от келий",
               "open_msg": "Ключ проворачивается в замке. Решётка кельи открыта.",
               "msg": "Решётка кельи на замке. Ключ — у брата-ключника."}])
print(f"Бейкер {W}×{H}: объектов {len(m.props)}, обыскиваемых {len(m.containers)}, "
      f"врагов {len(m.enemies)}, NPC {len(m.npcs)}; доступно клеток {len(reach)}")
