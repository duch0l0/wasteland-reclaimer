"""
Подземные карты Пятнадцатой: Убежище 57 (data/maps/vault57.json) и
ливнёвка (data/maps/drain.json). Вход — порталы на карте города
(tools/build_town.py), выход — порталы обратно.

Убежище 57 (40×34):
  шлюз с дверью-шестернёй → атриум (ярус А: склад города, жилые каюты,
  кабинет смотрителя) → гермодверь яруса Б (ключ-карта или терминал) →
  ярус Б: коридор с турелью, лаборатория «Проекта Панцирь», архив.
Ливнёвка (50×28):
  лестница из люка → тоннели с тиной и трубами → развилка, где культисты
  обронили сумку → логово крысолюдов с вожаком и кормушкой → решётка
  стока, через которую крысолюды лезут в город.

Склад «Бейкер-7» (36×26) — под бункером на окраине Бейкера (tools/build_baker.py):
  лестница → коридор с охранным роботом → караулка → хранилище: десять контейнеров ВРЭ
  (пять пустых, пять опломбированных), турель и терминал с журналом отгрузки — он и
  заканчивает главу (слайды baker_finale).

Запуск из папки game_project:  .venv/bin/python tools/build_underground.py
"""
from mapkit import MapKit, CRATES, BARRELS, LOCKERS, JUNK_PILES, CLOTH_PILES, RUBBLE


def room(m, code, x0, y0, x1, y1):
    m.paint(code, x0, y0, x1, y1)


# ================================================================ Убежище 57
v = MapKit(40, 34, start=(19, 5), seed=57, fill="x")
put, box, terminal, scatter = v.put, v.box, v.terminal, v.scatter

# --- ярус А
room(v, "m", 14, 2, 25, 7)            # шлюз
room(v, "m", 18, 8, 21, 9)            # проход в атриум
room(v, "m", 8, 10, 31, 16)           # атриум
room(v, "m", 2, 10, 6, 16)            # кабинет смотрителя
room(v, "m", 7, 12, 7, 13)            # дверь кабинета
room(v, "m", 33, 10, 38, 16)          # жилые каюты
room(v, "m", 32, 12, 32, 13)
room(v, "m", 18, 17, 21, 19)          # спуск к ярусу Б
room(v, "m", 19, 20, 20, 20)          # гермодверь
# --- ярус Б
room(v, "m", 6, 21, 33, 23)           # коридор
room(v, "m", 2, 24, 15, 32)           # лаборатория
room(v, "m", 24, 24, 37, 32)          # архив и кабинет Кросса
room(v, "m", 18, 24, 21, 28)          # тупик с турелью

put("x_vault_gear", 19, 1, force=True)                              # дверь-шестерня изнутри
v.portal([(19, 2), (20, 2)], "ruins", (55, 53), "Пятнадцатая")
v.reserve(17, 3, 22, 9)
put("x_vault_sign", 16, 3, check=False)
put("x_sandbags", 22, 5, check=False)
terminal(15, 2, "vault_door")

# атриум: город хранит здесь воду и припасы
for x in range(9, 16, 2):
    put(v.rnd.choice(BARRELS), x, 10, check=False)
scatter(CRATES, 23, 10, 30, 11, 5)
scatter(LOCKERS, 9, 15, 30, 16, 4)
put("table_2", 13, 13, check=False)
put("chair_1", 14, 13, check=False)
put("bench_16", 25, 14, check=False)
box("locker_double", 29, 15, "шкафчик кладовой", {"бинт": 1, "антирадин": 1, "крышки": 12})
# кабинет смотрителя
terminal(3, 10, "vault_upper")
put("filecab_3", 5, 10, check=False)
put("table_5", 3, 14, check=False)
put("chair_3", 4, 14, check=False)
box("metal_box_open", 2, 16, "сейф смотрителя", {"крышки": 35, "стимулятор": 1},
    requires={"flag": "vault_safe_open", "msg": "Сейф Кросса. Замок электронный — открывается с его терминала."})
# жилые каюты — радтараканы
for y in (10, 13):
    put("bed", 36, y, check=False)
put("nightstand", 34, 10, check=False)
box("wardrobe", 38, 14, "шкаф в каюте", {"ткань": 2, "самогон": 1})
v.enemies += [["radroach", 35, 12], ["radroach", 34, 15]]
# спуск и гермодверь яруса Б
put("x_vault_gear", 19, 20, check=False, allow_reserved=True)
gate_prop = len(v.props) - 1
terminal(21, 18, "vault_gate")
v.pickups.append(["патроны", 4, 18, 18])

# ярус Б: турель в тупике напротив гермодвери, гули, тараканы
v.enemies += [["turret", 19, 27], ["feral", 8, 27], ["feral", 12, 30], ["feral", 30, 29],
              ["radroach", 27, 22], ["radroach", 33, 26]]
# лаборатория «Проекта Панцирь»
terminal(4, 24, "vault_lab")
for x, y in ((3, 28), (3, 31)):
    put("bed", x, y, check=False)
box("glass_cabinet", 9, 24, "холодильник с сывороткой", {"сыворотка «Панцирь»": 2, "антирадин": 1})
put("sink", 11, 24, check=False)
put("table_3", 7, 30, check=False)
put("x_barrel_boom", 14, 31, check=False)
put("shelf_metal_tall", 13, 24, check=False)
# архив и кабинет Кросса
terminal(35, 24, "vault_overseer")
box("filecab_4", 27, 24, "шкаф с журналами", {"журнал «Проект Панцирь»": 1, "крышки": 15})
scatter(["filecab_1", "filecab_2", "filecab_3"], 25, 24, 33, 24, 3)
put("table_5", 30, 28, check=False)
put("chair_2", 31, 28, check=False)
box("locker_4", 37, 31, "шкафчик охраны", {"стимулятор": 1, "патроны": 8, "граната": 1})
scatter(["pile_computers", "pile_electronics", "pile_rags"], 24, 29, 37, 32, 3)

v.check(npc_enemy_gap=0, passable=v.footprint(*v.props[gate_prop]))
v.save("data/maps/vault57.json", style="vault", dark=140,   # верхний ярус город освещает
       gates=[{"prop": gate_prop, "flag": "vault_b_open", "key": "ключ-карта Б",
               "msg": "Гермодверь яруса Б. Табло: «ДОПУСК: СМОТРИТЕЛЬ». Нужна ключ-карта — или терминал рядом."}])
print(f"Убежище 57: объектов {len(v.props)}, врагов {len(v.enemies)}, контейнеров {len(v.containers)}")


# ================================================================ Ливнёвка
d = MapKit(50, 28, start=(3, 4), seed=15, fill="x")
put, box, terminal, scatter = d.put, d.box, d.terminal, d.scatter
room(d, "w", 2, 2, 6, 6)              # колодец под люком
room(d, "w", 7, 4, 24, 5)             # главный тоннель
room(d, "w", 22, 6, 24, 16)           # сток вниз
room(d, "w", 12, 14, 30, 16)          # нижний тоннель
room(d, "w", 10, 8, 13, 16)           # боковой рукав
room(d, "w", 25, 4, 40, 5)            # тоннель на восток
room(d, "w", 31, 6, 33, 12)
room(d, "w", 28, 10, 44, 20)          # логово
room(d, "w", 44, 12, 47, 14)          # решётка стока
room(d, "w", 2, 18, 11, 24)           # затопленная камера
room(d, "w", 10, 17, 11, 17)

put("x_ladder", 3, 2, check=False)
d.portal([(3, 2)], "ruins", (9, 52), "Пятнадцатая")
d.reserve(2, 3, 5, 6)
for x, y in ((9, 4), (17, 5), (23, 9), (15, 15), (26, 16), (35, 5), (5, 21), (8, 23)):
    put("x_puddle", x, y, check=False)
for x, y in ((12, 4), (20, 4), (22, 12), (30, 4), (38, 4)):
    put("x_pipe", x, y, check=False)
# развилка: сумка культиста — её обронили, таща деда
box("bag", 13, 8, "сумка культиста", {"листовка Единства": 1, "крышки": 12})
# затопленная камера — тайник
box("metal_chest", 3, 18, "ржавый ящик", {"патроны": 6, "химикаты": 1, "коктейль Молотова": 1})
scatter(RUBBLE + JUNK_PILES[:4], 2, 18, 11, 24, 3)
# логово: гнёзда, кости, кормушка
for name, x, y in [("bed_frame", 30, 11), ("sofa_frame", 38, 18), ("pile_rags", 34, 13), ("clothes_74", 41, 11),
                   ("clothes_76", 29, 18), ("pile_bags", 42, 17)]:
    put(name, x, y, check=False)
box("crate_open", 32, 7, "кормушка крысолюдов", {"ткань": 2, "лом": 1})   # в проходе к логову
d.containers[-1]["on_put"] = {"item": "отравленная приманка", "effects": [
    {"type": "set_flag", "flag": "rats_poisoned"}, {"type": "kill_pack", "pack": "ratmen"}]}
scatter(CLOTH_PILES, 28, 10, 44, 20, 4)
d.enemies += [["ratman", 16, 15], ["ratman", 34, 17], ["ratman", 40, 12], ["ratman", 33, 18],
              ["ratman", 43, 16], ["ratman_boss", 38, 16], ["rat", 7, 22]]
# решётка стока: отсюда крысолюды лезут в город
put("bar_fence_a", 46, 12, check=False)
d.pickups.append(["лом", 1, 45, 14])

d.check(npc_enemy_gap=0)
d.save("data/maps/drain.json", style="drain", dark=195)
print(f"Ливнёвка: объектов {len(d.props)}, врагов {len(d.enemies)}, контейнеров {len(d.containers)}")


# ================================================================ Склад «Бейкер-7»
b = MapKit(36, 26, start=(4, 18), seed=7, fill="x")
put, box, terminal, scatter = b.put, b.box, b.terminal, b.scatter
room(b, "m", 2, 16, 7, 21)            # площадка у лестницы
room(b, "m", 8, 18, 25, 19)           # коридор
room(b, "m", 8, 10, 14, 16)           # караулка
room(b, "m", 10, 17, 11, 17)          # дверь караулки
room(b, "m", 18, 3, 33, 16)           # хранилище
room(b, "m", 22, 17, 23, 17)          # проход в хранилище

put("x_ladder", 4, 16, check=False)
b.portal([(4, 16)], "baker_outskirts", (66, 12), "Бейкер: окраина")
b.reserve(3, 17, 6, 20)
put("x_vault_sign", 6, 16, check=False)
# караулка: шкафчики охраны
box("locker_4", 9, 10, "шкафчик охраны", {"стимулятор": 1, "патроны": 10, "граната": 1})
box("locker_2", 12, 10, "шкафчик сержанта", {"бинт": 2, "антирадин": 1, "автомат": 1, "патроны": 30})
put("table_5", 10, 13, check=False)
put("chair_2", 11, 13, check=False)
# хранилище: два ряда контейнеров — дальний опломбирован, ближний пуст
SEALED = {"flag": "never", "msg": "Пломба армии США: «ВРЭ. ПАРТИЯ 7». Вскрывать голыми руками — безумие."}
for x in (19, 22, 25, 28, 31):
    box("crate_b", x, 6, "контейнер ВРЭ", {}, requires=SEALED)
    box("crate_open", x, 11, "пустой контейнер", {})
terminal(30, 4, "baker7_log")
scatter(["ammo_box", "metal_sheets", "toolbox_red"], 18, 13, 33, 16, 3)
b.enemies += [["robot_guard", 18, 18], ["robot_guard", 24, 9], ["robot_guard", 32, 14], ["turret", 20, 4]]

b.check(npc_enemy_gap=0)
b.save("data/maps/baker7.json", style="vault", dark=170)
print(f"Бейкер-7: объектов {len(b.props)}, врагов {len(b.enemies)}, контейнеров {len(b.containers)}")
