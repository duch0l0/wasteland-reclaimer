"""
Генератор Бейкера — вторая глава. Город ночной (src/lighting.py) и разбит на три района,
каждый — своя карта, переходы — порталы на дорогах (как районы Нью-Рено в Fallout 2):

  data/maps/baker.json           «Бейкер: трасса» (72×48) — сюда приходят с карты мира.
      Трасса I-15 с запада на восток, фонари и остовы машин по обочинам, блокпост культа у
      въезда; закусочная «Безумный грек» (Ник, пьющий брат Тобиас), площадь с Термометром,
      мотель «Последняя миля» (староста Хэтти), дом Роя, гараж. Дорога на север — к миссии,
      на юг — на окраину.
  data/maps/baker_mission.json   «Бейкер: миссия» (70×50). Миссия «Детей Единства» за
      кирпичной оградой: молельня (брат Ансельм, сканер), кельи за решёткой (дед Эймос),
      трапезная (послушники, Марла), дом Ансельма (книга даров), кладбище «вознесённых».
      Ворота на юг, к дороге; калитка на север — в дюны, куда ведёт тропа вдоль западной стены.
  data/maps/baker_outskirts.json «Бейкер: окраина» (76×52). Лачуги и палатки у костров,
      свалка машин со «скупщиком» Холлисом, водонапорная башня, бункер склада «Бейкер-7».

Кто появляется по ходу сюжета (Лира, Панк, Сайлас, Шрам, дед у склада, Искра, Марла у Роя),
ставит src/game/baker.py.

Запуск из папки game_project:  .venv/bin/python tools/build_baker.py
"""
from mapkit import MapKit, WALLS_INTACT, BENCHES, STONES, GRASS, BUSHES

NIGHT = [86, 92, 134]       # цвет ночной темноты
TINT = [255, 238, 206]      # песок пожелтее
DRY = ["r_dry_bush"] + BUSHES   # у сухой травы «War ruins» под картинкой квадрат песка — не берём
TREES = [f"r_dtree_{c}" for c in "abcdefg"]
TABLES = ["round_table_42", "round_table_45", "round_table_58"]
STOOLS = ["stool_round_41", "stool_round_55", "stool_round_56"]


def desert(m, x0, y0, x1, y1, trees=10, bushes=24, junk=12):
    """Пустыня вокруг: сухие деревья, кусты, камни, кости, мусор."""
    for _ in range(trees):
        m.put(m.rnd.choice(TREES), m.rnd.randint(x0, x1), m.rnd.randint(y0, y1))
    m.grow(x0, y0, x1, y1, bushes, DRY)
    m.grow(x0, y0, x1, y1, bushes // 4, DRY + GRASS[:4])
    m.scatter(["r_rocks", "r_bones", "r_trash"] + STONES, x0, y0, x1, y1, junk)


def save(m, path, gates=(), exempt=()):
    gate_tiles = [t for g in gates for t in m.footprint(*m.props[g["prop"]])]
    reach = m.check(passable=gate_tiles, gap_exempt=exempt)
    m.save(path, tint=TINT, night=NIGHT, gates=list(gates))
    print(f"{path}: {m.W}×{m.H}, объектов {len(m.props)}, обыскиваемых {len(m.containers)}, "
          f"врагов {len(m.enemies)}, NPC {len(m.npcs)}; доступно клеток {len(reach)}")


# ================================================================ 1. Трасса
W, H = 72, 48
t = MapKit(W, H, start=(3, 27), seed=21)
put, box, terminal = t.put, t.box, t.terminal
t.exits = [(0, y) for y in range(26, 30)] + [(W - 1, y) for y in range(26, 30)]
t.npcs += [["nick", 6, 12], ["tobias", 13, 16], ["hattie", 55, 11], ["roy", 9, 37],
           ["baker_kid", 33, 21], ["baker_folk_e", 46, 35]]
t.enemies += [["cult_guard", 14, 23], ["cult_guard", 14, 32]]       # блокпост у въезда
for _, x, y in t.enemies + t.npcs:
    t.reserve(x, y, x, y)

t.paint("a", 0, 26, W - 1, 29)                       # трасса I-15
for x in range(0, W, 4):
    t.ground[27][x] = t.ground[27][x + 1] = "h"
t.paint("g", 0, 25, W - 1, 25)
t.paint("g", 0, 30, W - 1, 30)
t.paint("g", 24, 11, 47, 23)                         # площадь у Термометра
t.paint("a", 34, 0, 37, 24)                          # на север — к миссии
t.paint("a", 34, 31, 37, H - 1)                      # на юг — на окраину
for y in list(range(2, 24, 4)) + list(range(33, H - 1, 4)):
    t.ground[y][35] = t.ground[y + 1][35] = "v"
t.portal([(x, 0) for x in range(34, 38)], "baker_mission", (35, 46), "Миссия")
t.portal([(x, H - 1) for x in range(34, 38)], "baker_outskirts", (35, 2), "Окраина")
t.reserve(0, 24, W - 1, 31)
t.reserve(33, 0, 38, H - 1)
t.reserve(0, 23, 6, 32)

# фонари вдоль трассы, бочки с огнём у закусочной и на площади
for x in range(6, W - 4, 12):
    put("r_streetlamp", x, 24, allow_reserved=True, check=False)
    put("r_streetlamp_b", x + 6, 31, allow_reserved=True, check=False)
for x, y in ((18, 21), (27, 21), (44, 21), (50, 22), (24, 34), (60, 33)):
    put("x_fire_barrel", x, y)
# остовы машин по обочинам — как на брошенной трассе
for name, x, y in [("r_car_wreck", 20, 22), ("r_taxi", 44, 33), ("r_van", 62, 21), ("r_car_b", 2, 34),
                   ("r_pickup", 55, 33), ("r_car_red", 26, 33), ("r_army_truck", 64, 33)]:
    put(name, x, y)

# закусочная «Безумный грек»
t.building(3, 10, 14, 10, "planks", south=(4,), sign="БЕЗУМНЫЙ ГРЕК")
for x in (4, 8):
    put("counter", x, 13, check=False)
put("shelf_goods", 4, 11, check=False)
put("barrel_wood", 9, 11, check=False)
box("cabinet_small", 11, 11, "шкафчик Ника", {"самогон": 2, "крышки": 25}, owner="nick")
for tx, ty in ((11, 17), (13, 13), (4, 17)):
    put(t.rnd.choice(TABLES), tx, ty, check=False)
    put(t.rnd.choice(STOOLS), tx + 1, ty, check=False)
put("lantern_lit", 10, 15, check=False)
put("pile_bottles", 15, 11)

# площадь: Термометр, бак, доска объявлений, скамейки
put("x_thermometer", 29, 14, check=False)
put("water_tank_a", 41, 12, check=False)
box("barrel_wood", 44, 16, "колонка с водой", {"чистая вода": 2})
put("x_board", 30, 22, check=False)
t.terminals.append({"prop": len(t.props) - 1, "id": "doc:doc_baker_board"})
for x, y in ((25, 18), (40, 19)):
    put(t.rnd.choice(BENCHES), x, y)
put("r_billboard", 46, 12)

# мотель «Последняя миля»: стойка, номера с кроватями
t.building(52, 8, 18, 12, "concrete", south=(4, 12), sign="МОТЕЛЬ")
put("counter", 54, 13, check=False)
box("filecab_2", 53, 9, "конторка Хэтти", {"крышки": 40, "бинт": 2, "долговая книга": 1}, owner="hattie")
for x in (59, 63, 67):
    put("bed", x, 9, check=False)
    box("cabinet_small", x, 11, "тумбочка в номере", {"ткань": 1, "крышки": t.rnd.randint(2, 9)})
put("lantern_lit", 57, 16, check=False)
put("table_2", 64, 16, check=False)
put("chair_wood", 65, 16, check=False)

# юг трассы: дом Роя, гараж, блокпост
t.building(4, 34, 10, 8, "brick", north=(4,), sign="РОЙ")
put("bed_frame", 11, 35, check=False)
put("table_2", 6, 38, check=False)
put("chair_wood", 7, 38, check=False)
put("lantern_lit", 12, 39, check=False)
box("wardrobe", 5, 35, "шкаф Роя", {"ткань": 2, "крышки": 10}, owner="roy")
t.building(48, 36, 14, 9, "metal", north=(4,), sign="ГАРАЖ")
box("toolbox_red", 50, 38, "ящик механика", {"лом": 3, "химикаты": 1, "дробь": 4})
put("tool_rack", 53, 37, check=False)
put("metal_sheets", 56, 41, check=False)
put("lamp_post", 46, 35, check=False)
for x, y in ((12, 23), (12, 31)):
    put("r_sandbag_row", x, y, allow_reserved=True, check=False)

desert(t, 1, 1, W - 2, 9, trees=6)
desert(t, 1, 33, W - 2, H - 2, trees=6, junk=10)
desert(t, 18, 10, 23, 23, trees=2, bushes=4, junk=3)
# лестница на второй этаж мотеля (tools/build_baker_levels.py) — в углу холла
t.props.append(["mt_stairs", 67, 15])
t.portal([(67, 16), (68, 16)], "baker_motel_2f", (37, 17), "Второй этаж мотеля")
save(t, "data/maps/baker.json", exempt=("nick", "tobias", "roy", "baker_kid"))   # блокпост культа нейтрален


# ================================================================ 2. Миссия
W, H = 70, 50
m = MapKit(W, H, start=(35, 47), seed=31)
put, box, terminal = m.put, m.box, m.terminal
MX0, MY0, MX1, MY1 = 12, 10, 59, 39                  # ограда миссии
m.npcs += [["anselm", 28, 15], ["amos", 52, 16], ["iskra", 45, 26], ["marla", 17, 32],
           ["acolyte_a", 22, 33], ["acolyte_b", 31, 27]]
m.enemies += [["cult_guard", 38, 41], ["cult_guard", 39, 26], ["cultist", 25, 30], ["cultist", 34, 20]]   # страж ворот — снаружи
for _, x, y in m.enemies + m.npcs:
    m.reserve(x, y, x, y)

m.paint("a", 34, 40, 37, H - 1)                      # дорога от ворот к трассе
m.portal([(x, H - 1) for x in range(34, 38)], "baker", (35, 2), "Трасса")
m.reserve(33, 40, 38, H - 1)
m.reserve(2, 2, 10, 46)                              # тропа вдоль западной стены в дюны
m.reserve(2, 1, 67, 8)                               # дюны за миссией: путь к калитке
m.reserve(56, 11, 58, 24)                            # двор вдоль восточной стены: от калитки к кельям

m.wall_row(WALLS_INTACT["brick"], MX0, MX1, MY0, gaps={52, 53})        # северная стена, калитка
m.wall_row(WALLS_INTACT["brick"], MX0, MX1, MY1, gaps={35, 36})        # южная стена, ворота
m.side_wall("brick", "w", MX0, MY0 + 1, MY1 - 1)
m.side_wall("brick", "e", MX1, MY0 + 1, MY1 - 1)
put("bar_fence_c", 52, MY0, force=True)
back_gate = len(m.props) - 1
put("bar_fence_b", 35, MY1, force=True)
front_gate = len(m.props) - 1

# молельня
m.building(18, 13, 20, 12, "brick", south=(8,), sign="ЕДИНСТВО")
terminal(19, 14, "baker_scanner")
put("display_case_b", 27, 14, check=False)           # алтарь
for x in (25, 30):
    put("candles", x, 14, check=False)
for y in (17, 19, 21):
    for x in (20, 22, 24, 30, 32, 34):
        put(m.rnd.choice(BENCHES), x, y, check=False)
for x in (19, 36):
    put("lantern_lit", x, 22, check=False)

# кельи: решётка, за ней дед
m.building(46, 13, 10, 10, "concrete", south=(2,), sign="КЕЛЬИ")
put("bar_fence_a", 48, 22, force=True)
cell_gate = len(m.props) - 1
put("bed_frame", 53, 14, check=False)
put("bucket", 47, 14, check=False)
put("pile_rags", 53, 19, check=False)
put("candles", 50, 14, check=False)

# дом Ансельма: сундук с книгой даров
m.building(40, 28, 8, 7, "brick", north=(2,), sign=None)
box("metal_chest", 45, 30, "сундук Ансельма", {"крышки": 80, "стимулятор": 1, "святая вода": 2,
                                                "книга даров": 1, "ключ от крипты": 1}, owner="anselm")
put("bed", 41, 32, check=False)
put("table_2", 44, 33, check=False)
put("candles", 46, 33, check=False)

# трапезная: столы, нары, «святая вода»
m.building(14, 28, 14, 8, "planks", north=(4,), sign="ТРАПЕЗНАЯ")
for x in (16, 20, 24):
    put("table_2", x, 30, check=False)
    put("chair_wood", x + 1, 30, check=False)
for x in (15, 19, 23):
    put("bed", x, 33, check=False)
box("barrel_wood", 26, 29, "бочка «святой воды»", {"святая вода": 3}, owner="anselm")
box("crate", 15, 29, "ящик с припасами", {"чистая вода": 1, "крышки": 6})
put("lantern_lit", 22, 31, check=False)

# двор: шатры, костёр, бочки с огнём у ворот, кладбище «вознесённых»
for name, x, y in [("r_tent_beige", 29, 26), ("r_tent_purple", 33, 33), ("r_tent_low", 38, 25)]:
    put(name, x, y)
put("campfire", 31, 30)
for x in (33, 38):
    put("x_fire_barrel", x, 37)
for gy in (27, 30, 33):
    for gx in (51, 53, 55):
        put("x_cross", gx, gy - 1, check=False)
        put("x_grave", gx, gy, check=False)
        m.containers[-1]["requires"] = {"item": "лопата", "msg": "Свежая могила «вознесённого». Без лопаты — никак."}
        m.containers[-1]["name"] = "могила «вознесённого»"
put("x_board", 49, 36, check=False)
m.terminals.append({"prop": len(m.props) - 1, "id": "doc:doc_ascended"})

# снаружи: дорога, дюны, фонарь у ворот
put("r_streetlamp", 39, 41, allow_reserved=True, check=False)
put("x_fire_barrel", 32, 42, allow_reserved=True, check=False)
put("campfire", 57, 4, allow_reserved=True)          # костерок Панка в дюнах
desert(m, 1, 1, W - 2, 8, trees=8, bushes=20)
desert(m, 1, 9, 11, H - 2, trees=4, bushes=10, junk=6)
desert(m, 60, 9, W - 2, H - 2, trees=6, bushes=14, junk=8)
desert(m, 12, 41, 32, H - 2, trees=3, bushes=8)
desert(m, 39, 41, 59, H - 2, trees=3, bushes=8)
# плита за алтарём — спуск в крипту (tools/build_baker_levels.py); ключ — в сундуке Ансельма
m.props.append(["x_manhole", 34, 15])
m.portal([(34, 15)], "baker_crypt", (4, 5), "Крипта Единства",
         requires={"item": "ключ от крипты",
                   "msg": "За алтарём — каменная плита с замочной скважиной в форме круга. Ключ — у брата Ансельма."})
save(m, "data/maps/baker_mission.json",
     gates=[{"prop": front_gate, "flag": "mission_gate_open",
             "msg": "Ворота миссии заперты изнутри. За решёткой — шатры, костёр и белые балахоны."},
            {"prop": back_gate, "flag": "mission_back_open", "pry": True,   # лом у героя всегда при себе
             "open_msg": "Вы поддеваете гнилой засов ломом. Калитка со скрипом подаётся."},
            {"prop": cell_gate, "flag": "cells_open", "key": "ключ от келий",
             "open_msg": "Ключ проворачивается в замке. Решётка кельи открыта.",
             "msg": "Решётка кельи на замке. Ключ — у брата-ключника."}],
     exempt=("anselm", "iskra", "amos", "marla", "acolyte_a", "acolyte_b"))


# ================================================================ 3. Окраина
W, H = 76, 52
o = MapKit(W, H, start=(35, 2), seed=41)
put, box, terminal, scatter = o.put, o.box, o.terminal, o.scatter
o.npcs += [["hollis", 60, 40], ["baker_folk_a", 9, 14], ["baker_folk_b", 17, 25], ["baker_folk_c", 24, 33],
           ["baker_folk_d", 12, 41], ["baker_kid_b", 30, 21]]
o.enemies += [["rat", 72, 49], ["rat", 70, 47]]
for _, x, y in o.enemies + o.npcs:
    o.reserve(x, y, x, y)

o.paint("a", 34, 0, 37, 12)                          # дорога с трассы
o.portal([(x, 0) for x in range(34, 38)], "baker", (35, 46), "Трасса")
o.reserve(33, 0, 38, 18)

# жилой запад: лачуги, палатки, костры
homes = [("r_shack", 3, 9), ("r_shack_tin", 10, 9), ("r_cabin", 19, 10), ("r_shed_tin", 25, 9),
         ("r_hut", 3, 19), ("r_tent_big", 9, 20), ("r_shanty", 19, 19), ("r_cabin_b", 26, 20),
         ("r_house_wood", 3, 29), ("r_tent_green", 10, 30), ("r_tent_orange", 14, 30), ("r_shack_e", 20, 29),
         ("r_cabin_d", 28, 29), ("r_shack_f", 4, 38), ("r_shanty_big", 16, 37), ("r_shack_blue", 26, 39)]
for name, x, y in homes:
    put(name, x, y)
for x, y in ((9, 16), (22, 26), (13, 35), (35, 15)):
    put("campfire", x, y)
for x, y in ((16, 14), (28, 34), (8, 45)):
    put("x_fire_barrel", x, y)
for name, x, y in [("r_dumpster", 14, 15), ("r_trash_can", 29, 24), ("r_logs", 24, 36), ("r_barrels", 6, 26),
                   ("r_bin", 31, 41)]:
    put(name, x, y)
box("metal_box_open", 18, 16, "ящик у лачуги", {"ткань": 1, "крышки": 4})
box("wardrobe", 7, 34, "сундук старика", {"крышки": 12, "бинт": 1})
put("r_water_tower_tall", 44, 6)

# свалка машин и трейлер Холлиса
for name, x, y in [("r_rv", 54, 35), ("r_car_wreck", 64, 33), ("r_junk_mound", 70, 36), ("r_tanker", 46, 44),
                   ("r_van", 56, 47), ("r_camper", 66, 44), ("r_car_b", 48, 38), ("r_car_c", 72, 42),
                   ("r_moto", 62, 37), ("r_car_wreck", 44, 32)]:
    put(name, x, y)
box("metal_chest", 58, 39, "сундук Холлиса", {"крышки": 60, "стимулятор": 2, "балахон послушника": 1},
    owner="hollis")
put("r_awning", 61, 41)
put("lantern_lit", 59, 42)
terminal(64, 40, "hollis_radio")
for x, y in ((52, 41), (68, 40)):
    put("x_fire_barrel", x, y)

# склад «Бейкер-7»
put("r_bunker", 64, 8, check=False)
o.portal([(66, 10), (67, 10)], "baker7", (4, 18), "Склад «Бейкер-7»",
         requires={"flag": "baker7_open",
                   "msg": "Бронедверь склада. Табло: «ДОСТУП: ПЕРСОНАЛ МАРИПОЗЫ. СЕТЧАТКА · ГОЛОС · КОД»."})
terminal(70, 11, "baker7_lock")
o.reserve(63, 10, 69, 20)                            # перед дверью склада — свободно
for x, y in ((60, 12), (72, 13)):
    put("x_sandbags", x, y, check=False)
put("r_army_truck", 52, 6)
put("r_derrick", 72, 3)
put("r_streetlamp", 62, 15, allow_reserved=True, check=False)
put("r_streetlamp_b", 71, 17, allow_reserved=True, check=False)
scatter(["ammo_box", "crate", "crate_b"], 56, 21, 74, 28, 3)

desert(o, 1, 1, W - 2, H - 2, trees=12, bushes=30, junk=16)
save(o, "data/maps/baker_outskirts.json", exempt=("hollis",))
