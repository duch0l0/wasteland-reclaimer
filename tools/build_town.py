"""
Генератор карты стартового города Пятнадцатая (data/maps/town.json).

Районы (96×64 клетки), подробно — docs/story.md, раздел «Стартовый город»:
  запад            — въезд с трассы, остановка; отсюда начинается игра;
  северо-запад     — жилой квартал: дом деда, дома жителей, дворы;
  север            — салун «Последний глоток», склад «Пасифик Фрейт»;
  центр-север      — рынок: лавка Гены, палатка проповедника «Детей Единства», доска объявлений;
  северо-восток    — водокачка за сеткой: баки, контора, светящиеся мутанты, Блонди;
  юг у дороги      — дом Черепана, пост шерифа, клиника, ратуша;
  юго-запад        — руины склада со спуском в ливнёвку (крысы), кладбище;
  юг-центр         — сквер (панцирный жук) и скала с дверью Убежища 57;
  юго-восток       — свалка: лагерь рейдеров, пёс на цепи, лачуга Панка-одиночки.
Через весь город — улица (трасса I-15) с выходами на запад и на юг.

Спуск в ливнёвку и дверь убежища — порталы в подземные карты
(tools/build_underground.py).

Запуск из папки game_project:  .venv/bin/python tools/build_town.py
"""
from mapkit import (MapKit, BARRELS, CRATES, GRASS, BUSHES, STONES, FLOOR_BITS, DIRT_DECALS, JUNK_PILES,
                    CLOTH_PILES, RUBBLE, FURNITURE, LOCKERS, POLES, SIGNS, SEATS, BENCHES)

W, H = 96, 64
m = MapKit(W, H, start=(3, 31), seed=7)
rnd = m.rnd
put, box, terminal, scatter = m.put, m.box, m.terminal, m.scatter
m.exits = [(0, y) for y in range(30, 34)] + [(x, H - 1) for x in range(44, 48)]

# ------------------------------------------------------------ кто и что где (резервируется до расстановки)
m.pickups += [
    ["лом", 1, 9, 20],                  # в доме деда
    ["чей-то глаз", 1, 8, 18],          # в доме деда
    ["ткань", 1, 19, 10],
    ["химикаты", 1, 72, 13],
    ["химикаты", 1, 76, 58],
    ["лопата", 1, 24, 60],              # в сторожке кладбища
    ["ткань", 1, 30, 14],
]
m.npcs += [
    ["gena", 44, 22],
    ["silas", 52, 20],                  # проповедник «Детей Единства» у своей палатки
    ["blondie", 88, 4],
    ["mo", 21, 19],                     # за стойкой салуна
    ["lenny", 26, 23],                  # за столиком салуна
    ["marta", 9, 9],                    # во дворе своего дома
    ["turtle", 8, 40],                  # Черепан — в доме без крыши за дорогой
    ["sheriff", 19, 39],                # пост шерифа у въезда
    ["doc", 27, 40],                    # клиника
    ["ada", 38, 40],                    # ратуша
    ["dale", 52, 54],                   # помощник шерифа — часовой у двери убежища
    ["loner", 69, 60],
    ["dog", 90, 46],                    # пёс на цепи у ящика с патронами в лагере рейдеров
]
m.enemies += [
    ["rad_mutant", 68, 16], ["rad_mutant", 77, 19],     # водокачка
    ["rat", 5, 57], ["rat", 13, 58], ["rat", 10, 50],   # руины над ливнёвкой
    ["beetle", 56, 41],                                 # высохший сквер
    ["raider", 85, 45], ["raider", 87, 54],             # лагерь на свалке
]
for _, x, y in m.enemies + m.npcs:
    m.reserve(x, y, x, y)
for *_, x, y in m.pickups:
    m.reserve(x, y, x, y)


# ------------------------------------------------------------ дороги
m.paint("a", 0, 30, W - 1, 33)                    # главная улица
for x in range(0, W, 4):
    m.ground[31][x] = m.ground[31][x + 1] = "h"  # прерывистая разметка
m.paint("g", 0, 29, W - 1, 29)                    # тротуары
m.paint("g", 0, 34, W - 1, 34)
m.paint("a", 44, 34, 47, H - 1)                   # улица на юг
for y in range(36, H, 4):
    m.ground[y][45] = m.ground[y + 1][45] = "v"
m.paint("g", 43, 35, 43, H - 1)
m.paint("g", 48, 35, 48, H - 1)
m.paint("g", 36, 14, 57, 28)                      # рыночная площадь
m.paint("a", 70, 22, 72, 28)                      # подъезд к водокачке
m.paint("g", 60, 35, 62, 40)                      # въезд на свалку
m.paint("g", 49, 51, 60, 57)                      # площадка перед убежищем
m.reserve(0, 29, W - 1, 34)
m.reserve(43, 34, 48, H - 1)
m.reserve(70, 22, 72, 28)
m.reserve(0, 26, 8, 36)                           # площадка у въезда — старт
m.reserve(20, 27, 24, 28)                         # у дверей салуна
m.reserve(49, 51, 60, 57)


# ------------------------------------------------------------ запад: въезд и остановка
put("bench_7", 3, 27, allow_reserved=True, check=False)
put("sign_stop", 6, 27, allow_reserved=True, check=False)
put("seat_22", 1, 27, allow_reserved=True, check=False)
put("sign_72", 2, 36, allow_reserved=True, check=False)
put("lamp_post", 9, 28, allow_reserved=True, check=False)
for x in range(18, W - 4, 12):                    # фонари вдоль улицы
    put("lamp_post", x, 28, allow_reserved=True)
    put("lamp_post", x + 6, 35, allow_reserved=True)


# ------------------------------------------------------------ северо-запад: жилой квартал
# дом деда Эймоса — первый у въезда: разгром, чужой глаз на полу, включённый терминал, сейф
m.building(3, 14, 10, 8, "brick", south=(4,))
terminal(5, 15, "grandpa")
box("metal_chest", 10, 15, "сейф деда",
    {"10-мм пистолет": 1, "голозапись деда": 1, "медаль за Анкоридж": 1, "патроны": 12},
    requires={"flag": "safe_code", "msg": "Сейф с кодовым замком: три колёсика по две цифры. Код должен быть где-то у деда."})
for name, x, y in [("table_upside", 7, 16), ("chair_broken", 9, 17), ("bed_frame", 4, 19), ("bits", 6, 18),
                   ("plank_floor", 10, 19), ("rag", 5, 17), ("wardrobe_broken", 11, 17)]:
    put(name, x, y, check=False)

yard_fences = ["fence_picket", "fence_picket2", "fence_broken", "plank_fence_b", "post_fence_a"]
for name, hx, hy in [("house_a", 3, 2), ("house_b", 14, 2), ("ruin_facade_a", 24, 2)]:
    put(name, hx, hy, check=False)
    m.hwall(yard_fences, hx - 1, hx + 6, hy + 9, gaps=(hx + 2, hx + 3))
    scatter(FURNITURE[:6], hx - 1, hy + 3, hx + 5, hy + 7, 1)
    scatter(GRASS, hx - 2, hy + 3, hx + 6, hy + 8, 4)
box("wardrobe", 4, 7, "шкаф Марты", {"ткань": 2, "бинт": 1, "крышки": 6}, owner="marta")
box("metal_box_open", 12, 7, "ящик с бельём", {"ткань": 1})
put("clothes_73", 6, 8)
put("bucket", 11, 9)
put("locker_2", 26, 7)


# ------------------------------------------------------------ север: салун «Последний глоток»
ix0, iy0, ix1, iy1 = m.building(15, 16, 14, 11, "planks", south=(6,))
for x in (16, 18, 23):                            # стойка, проход к Мо — посередине
    put("counter", x, 20, check=False)
put("counter", 25, 20, check=False)
put("shelf_goods", 16, 17, check=False)
put("shelf_stuff_1", 18, 17, check=False)
put("shelf_goods", 21, 17, check=False)
put("barrel_wood", 24, 17, check=False)
put("barrel_wood", 26, 17, check=False)
box("cabinet_small", 27, 17, "шкафчик Мо", {"крышки": 30, "самогон": 2}, owner="mo")
for tx, ty in ((17, 23), (23, 23), (17, 25)):     # столики
    put(rnd.choice(["round_table_42", "round_table_45", "round_table_58"]), tx, ty, check=False)
    put(rnd.choice(["stool_round_41", "stool_round_55", "stool_round_56"]), tx + 1, ty, check=False)
put("stool_round_41", 27, 23, check=False)
put("stool_1", 19, 22, check=False)
put("stool_2", 25, 22, check=False)
put("candles", 23, 24)
put("pile_bottles", 27, 25)


# ------------------------------------------------------------ склад «Пасифик Фрейт»
ix0, iy0, ix1, iy1 = m.building(32, 1, 10, 9, "brick", south=(4,))
terminal(34, 2, "warehouse")
scatter(LOCKERS + ["shelf_goods", "metal_shelf", "shelf_stuff_1"], ix0, iy0, ix1, iy0, 4)
scatter(CRATES + ["ammo_box", "toolbox_blue", "pile_scrap"], ix0, iy0 + 2, ix1, iy1, 3)
scatter(BARRELS + CRATES, 1, 1, 33, 26, 3)
scatter(JUNK_PILES + CLOTH_PILES, 28, 10, 34, 27, 3)


# ------------------------------------------------------------ рынок
put("shelter_a", 43, 18, check=False)             # лавка Гены
put("counter", 43, 20, check=False)
put("display_case_b", 45, 20, check=False)
put("barrel_wood", 42, 20)
put("crate_small", 47, 18)
put("lantern_lit", 46, 22)
for name, sx, sy in [("shelter_b", 37, 18), ("shelter_b", 37, 24), ("shelter_a", 43, 25)]:
    put(name, sx, sy)
    scatter(["table_1", "table_4", "table_7", "display_case_a", "display_case_c", "counter", "table_8"],
            sx - 1, sy + 1, sx + 3, sy + 2, 1)
# палатка «Детей Единства»: бочка со «святой водой», кружки, свечи
put("tent_round_tan", 50, 15, check=False)
box("barrel_wood", 54, 18, "бочка «святой воды»", {"святая вода": 3}, owner="silas")
put("candles", 49, 19)
put("round_table_60", 50, 21)
put("stool_round_55", 49, 21)
put("tent_green", 36, 13)
put("tent_blue", 55, 13)
put("x_board", 40, 27, allow_reserved=True, check=False)  # доска объявлений у улицы
m.terminals.append({"prop": len(m.props) - 1, "id": "doc:doc_board_market"})
put("shack_a", 56, 20, check=False)               # лачуга, за ней — заначка Гены
box("metal_chest", 57, 18, "заначка Гены", {"крышки": 45, "тоник": 1, "патроны": 8}, owner="gena")
scatter(BARRELS + CRATES + ["firewood", "round_table_42", "stool_round_41", "chair_0", "chair_4"],
        35, 15, 57, 28, 6)
scatter(["lantern", "backpack"], 35, 15, 57, 28, 2)


# ------------------------------------------------------------ северо-восток: водокачка
m.hwall(["chain_a", "chain_b", "chain_c", "chain_d", "chain_e", "chain_broken_a", "chain_broken_d"],
        60, 94, 24, gaps=(70, 71, 72))
m.side_wall("metal", "e", 59, 2, 23, gaps=(11, 12))
put("water_tank_a", 64, 5, check=False)
put("water_tank_b", 74, 5, check=False)
put("water_tank_a", 86, 7, check=False)           # за этим баком прячется Блонди
ix0, iy0, ix1, iy1 = m.building(81, 13, 12, 8, "metal", south=(4,), west=(4,))  # контора водокачки
terminal(83, 14, "pump")
box("locker_1", 88, 14, "шкафчик Уоллеса", {"записка техника": 1, "бинт": 1})
scatter(LOCKERS + ["filecab_1", "filecab_4"], ix0, iy0, ix1, iy0, 4)
scatter(["table_2", "table_6", "chair_wood", "chair_1", "toolbox_open_b"], ix0, iy0 + 2, ix1, iy1, 3)
put("shelter_b", 61, 14)
for x in (64, 65, 66, 67):
    put(rnd.choice(LOCKERS), x, 10)
scatter(BARRELS, 62, 12, 80, 22, 6)
put("x_barrel_boom", 66, 18)
put("x_barrel_boom", 75, 15)
scatter(["tool_rack", "metal_sheets", "toolbox_red", "ammo_box", "canister"], 61, 12, 80, 22, 4)


# ------------------------------------------------------------ юг у дороги: Черепан, шериф, клиника, ратуша
ix0, iy0, ix1, iy1 = m.building(2, 37, 14, 8, "brick", north=(4,))   # дом Черепана без крыши
scatter(["wardrobe", "shelf_goods", "cabinet_small", "nightstand"], ix0, iy0, ix1, iy0, 3)
scatter(["table_1", "table_chair", "sofa", "chair_wood", "armchair"], ix0 + 4, iy0 + 2, ix1, iy1, 3)
put("x_puddle", 4, 42)
put("bucket", 3, 41)
put("pile_rags", 13, 42)

ix0, iy0, ix1, iy1 = m.building(17, 37, 6, 6, "planks", north=(2,))  # пост шерифа
put("table_2", 20, 38, check=False)
put("chair_wood", 21, 39, check=False)
box("locker_double", 18, 41, "оружейный шкаф шерифа", {"патроны": 6}, owner="sheriff")
put("x_board", 23, 35, allow_reserved=True, check=False)
m.terminals.append({"prop": len(m.props) - 1, "id": "doc:doc_board_sheriff"})

ix0, iy0, ix1, iy1 = m.building(24, 37, 8, 8, "concrete", north=(2,))  # клиника
put("bed", 29, 39, check=False)
put("bed", 29, 42, check=False)
put("sink", 25, 43, check=False)
box("glass_cabinet", 25, 38, "аптечный шкаф Дока", {"бинт": 2, "антирадин": 1, "химикаты": 1}, owner="doc")
put("table_3", 27, 43, check=False)

ix0, iy0, ix1, iy1 = m.building(33, 36, 10, 9, "brick", north=(4,))   # ратуша
terminal(35, 37, "council")
box("filecab_2", 40, 37, "стол Смотрительницы", {"ключ-карта Б": 1, "крышки": 20}, owner="ada")
put("filecab_1", 41, 37, check=False)
put("table_5", 37, 41, check=False)
put("chair_2", 36, 42, check=False)
put("chair_3", 39, 42, check=False)
put("x_vault_sign", 34, 43, check=False)
put("shelf_wood", 41, 42, check=False)


# ------------------------------------------------------------ юго-запад: руины над ливнёвкой и кладбище
ix0, iy0, ix1, iy1 = m.building(2, 48, 16, 13, "concrete", north=(6,), east=(6,))
m.paint("c", 3, 49, 16, 59)
put("x_manhole", 9, 54)
m.portal([(9, 54)], "drain", (3, 3), "Ливнёвка")
for name, x, y in [("bed_frame", 4, 50), ("pile_rags", 14, 50), ("clothes_74", 5, 58), ("pile_bags", 15, 57)]:
    put(name, x, y)
scatter(RUBBLE + JUNK_PILES[:4], ix0, iy0, ix1, iy1, 6)
put("x_pipe", 12, 49)

m.paint("d", 20, 48, 41, 62)
m.hwall(["post_fence_a", "post_fence_b", "plank_fence_a", "plank_fence_b", "fence_broken"],
        20, 41, 47, gaps=(30, 31))
m.side_wall("planks", "w", 20, 48, 61)
m.hwall(["post_fence_a", "post_fence_b", "plank_fence_a", "fence_broken"], 20, 41, 62)
graves = []
for gy in (50, 53, 56):
    for gx in range(23, 40, 3):
        if (gx, gy) == (38, 56):
            continue
        graves.append((gx, gy))
for i, (gx, gy) in enumerate(graves):
    put("x_cross" if i % 3 else "x_tombstone", gx, gy - 1, check=False)
    put("x_grave", gx, gy, check=False)
    m.containers[-1]["requires"] = {"item": "лопата", "msg": "Могила. Голыми руками не раскопать — нужна лопата."}
    m.containers[-1]["name"] = "могила"
# могила пса деда: надгробие «КОЛБАСА», внутри — жетон Эймоса со Списком Марипозы
put("x_tombstone", 38, 55, check=False)
box("x_grave", 38, 56, "могила «Колбаса»", {"жетон Эймоса": 1, "патроны": 6},
    requires={"item": "лопата", "msg": "На камне выцарапано: «КОЛБАСА. Лучший пёс. Э.Р.». Без лопаты не раскопать."})
put("shack_b", 22, 58, check=False)                # сторожка кладбища (лопата — рядом)
for x, y in ((34, 60), (26, 49)):
    put("dead_tree", x, y)
scatter(GRASS, 21, 48, 40, 61, 14)


# ------------------------------------------------------------ юг-центр: сквер и Убежище 57
for x, y in [(50, 37), (55, 37), (58, 41)]:
    put("dead_tree", x, y)
for x, y in [(49, 39), (52, 41)]:
    put(rnd.choice(BENCHES), x, y)
scatter(["round_table_45", "stool_round_55", "stone_table", "rock_grass", "rock_grass_b"], 49, 36, 58, 42, 3)
scatter(GRASS + BUSHES, 49, 36, 58, 42, 14)
# столовая гора, в южном склоне — дверь-шестерня; перед ней площадка с часовым
put("x_mesa_vault", 49, 48, check=False, allow_reserved=True)
m.portal([(55, 51), (56, 51)], "vault57", (19, 5), "Убежище 57")
put("x_vault_sign", 59, 52, allow_reserved=True, check=False)
put("x_sandbags", 50, 53, allow_reserved=True, check=False)
put("x_sandbags", 58, 55, allow_reserved=True, check=False)
put("lamp_post", 53, 52, allow_reserved=True, check=False)
put("lamp_post", 58, 52, allow_reserved=True, check=False)
scatter(CRATES + BARRELS, 49, 56, 62, 62, 5)


# ------------------------------------------------------------ юго-восток: свалка
m.hwall(["wall_corrugated", "wall_corrugated2", "wall_metal", "wall_metal2", "wall_corrugated_rust",
         "corrugated_panel", "corrugated_b"], 60, 94, 37, gaps=(60, 61, 62))
m.side_wall("metal", "e", 64, 38, 62, gaps=(45, 46, 58))
put("shack_b", 66, 56, check=False)               # лачуга Панка
ix0, iy0, ix1, iy1 = m.building(68, 40, 12, 8, "metal", south=(4,), west=(3,))  # контора свалки
terminal(70, 41, "junk")
box("metal_chest", 77, 41, "сейф конторы", {"крышки": 60, "патроны": 10, "тоник": 1},
    requires={"flag": "junk_safe_open", "msg": "Сейф конторы. Электронный замок — открывается с терминала."})
scatter(LOCKERS + ["filecab_2"], ix0, iy0, ix1, iy0, 3)
scatter(["table_5", "chair_2", "sofa", "cardboard"], ix0, iy0 + 2, ix1, iy1, 3)
ix0, iy0, ix1, iy1 = m.building(80, 55, 10, 6, "planks", south=(4,))     # сторожка
scatter(["bed", "chair_3", "table_4", "locker_3"], ix0, iy0, ix1, iy1, 3)
scatter(JUNK_PILES, 66, 39, 93, 62, 16)
scatter(SEATS + ["metal_sheets", "barrel_lying_a"], 66, 39, 93, 62, 4)
for name, x, y in [("tent_green", 84, 41), ("tent_tan", 88, 49), ("firewood", 86, 46), ("ammo_box", 90, 45),
                   ("crate", 83, 46), ("crate_b", 91, 53), ("x_barrel_boom", 82, 50), ("x_sandbags", 83, 44)]:
    put(name, x, y)
# между оградой свалки и сквером — пустырь с хламом
scatter(JUNK_PILES[:6] + RUBBLE[:4], 59, 38, 63, 62, 5)


# ------------------------------------------------------------ по всему городу
for _ in range(34):                                                    # трава растёт куртинами
    cx, cy = rnd.randint(2, W - 3), rnd.randint(2, H - 3)
    scatter(GRASS + BUSHES[:2], cx - 3, cy - 2, cx + 3, cy + 2, rnd.randint(3, 6), tries=8)
scatter(GRASS, 1, 1, W - 2, H - 2, 180)
scatter(BUSHES, 1, 1, W - 2, H - 2, 24)
scatter(POLES + SIGNS, 1, 1, W - 2, H - 2, 5)
scatter(STONES + FLOOR_BITS[:5], 1, 1, W - 2, H - 2, 40)
m.decal(DIRT_DECALS, 1, 1, W - 2, H - 2, 60)
scatter(RUBBLE, 1, 1, W - 2, 3, 2)


# ------------------------------------------------------------ проверки и запись
reach = m.check(gap_exempt=("dog",))
m.save("data/maps/town.json")
print(f"город {W}×{H}: объектов {len(m.props)}, пятен {len(m.decals)}, обыскиваемых {len(m.containers)}, "
      f"врагов {len(m.enemies)}, NPC {len(m.npcs)}, предметов {len(m.pickups)}; доступно клеток {len(reach)}")
