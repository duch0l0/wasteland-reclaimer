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
from citykit import City

city = City("underground", "Подземелья")     # реестр объектов из наборов: data/props/underground.json


def P(name, img, **kw):
    city.prop(name, img, **kw)
    return name


STEEL = ["pk:nbunk/p2/4,8,1,1"]
GRILLE = ["pk:nbunk/p2/0,12,1,1"]
PLATES_UG = ["pk:fstation/fstation_f2_09"]
BUNK_U = P("ug_bunk", "pk:nbunk/nbunk_2_000", foot=[2, 1], sight=True)
LOCKER_U = [P("ug_locker_a", "pk:nbunk/nbunk_2_005", foot=[1, 1], search="locker", title="шкафчик"), P("ug_locker_b", "pk:nbunk/nbunk_2_006", foot=[1, 1], search="locker", title="шкафчик")]
GEN_U = P("ug_gen", "pk:nbunk/nbunk_2_028", foot=[2, 2], sight=True, light={"r": 100, "color": [255, 200, 120], "at": [0.5, 0.5], "flicker": 0.25})
WARN_U = P("ug_warn", "pk:npower/npower_1_069", foot=[1, 1])
CONSOLE_U = [P("ug_console_a", "pk:npower/npower_2_006", foot=[2, 1]), P("ug_console_b", "pk:npower/npower_2_013", foot=[2, 1])]
SERVER_U = P("ug_server", "pk:npower/npower_2_042", foot=[1, 1])
VRE_U = P("ug_vre", "pk:wlab/wlab_2_024", foot=[2, 1], sight=True)
BIOHAZ_U = P("ug_biohaz", "pk:hosp/hosp_1_012", foot=[1, 1])
TUBE_U = P("ug_tube", "pk:wlab/wlab_3_101", foot=[2, 1], sight=True, light={"r": 80, "color": [150, 255, 160], "at": [0.5, 0.5], "flicker": 0.3})
LAMP_U = P("ug_lamp", "pk:cmine/cmine_1_032", foot=[1, 1], block=False, light={"r": 120, "color": [255, 190, 110], "at": [0.5, 0.5], "flicker": 0.3})
CHAIR_U = P("ug_chair", "pk:aoffice/aoffice_1_002", foot=[1, 1])


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
v.enemies += [["turret", 19, 27], ["feral", 8, 27], ["ghoul_runner", 30, 29], ["radroach", 33, 26]]   # ярус — на 2–3 уровне
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

# атмосфера: ярус А — тусклый жёлтый (аварийное питание города), ярус Б — красный и мёртвая зелень лаборатории
def lamp(kind, x, y):
    put(f"x_vd_stand_{kind}", x, y, check=False, allow_reserved=True)


for x, y in ((15, 3), (24, 3), (9, 11), (16, 11), (24, 11), (30, 11), (3, 11), (35, 11), (4, 15), (35, 15)):
    lamp("amber", x, y)
for x, y in ((8, 22), (18, 22), (28, 22), (4, 26), (12, 30), (26, 26), (35, 30), (20, 26)):
    lamp("red", x, y)
lamp("green", 7, 26)
lamp("green", 4, 31)
for x, y in ((12, 21), (24, 21)):
    put("x_vd_blood0", x, y, check=False, allow_reserved=True)
put("x_vd_hz_h", 19, 21, check=False, allow_reserved=True)
put("x_vd_hz_h", 20, 21, check=False, allow_reserved=True)
for x in range(9, 31):
    put("x_vd_cab_h", x, 17, check=False, allow_reserved=True)
put("x_vd_sparks", 30, 22, check=False, allow_reserved=True)

v.check(npc_enemy_gap=0, passable=v.footprint(*v.props[gate_prop]))
v.save("data/maps/vault57.json", style="vault", dark=140, night=[96, 92, 88],   # верхний ярус город освещает
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
# крысолюды: разведчик у входа, пара у поворота, гнездо с вожаком — бой по частям, а не всей стаей сразу
# (герою первого уровня с ломом вшестером не выжить — проверено ботом tools/playthrough.py)
d.enemies += [["ratman", 16, 15], ["ratman", 33, 18], ["ratman", 42, 12], ["ratman_boss", 40, 16], ["rat", 7, 22]]
# решётка стока: отсюда крысолюды лезут в город
put("bar_fence_a", 46, 12, check=False)
d.pickups.append(["лом", 1, 45, 14])

# атмосфера ливнёвки: тусклые янтарные лампы у труб, зелёное свечение тины, сырость, кровь у логова, капли с потолка
def dl(kind, x, y):
    d.put(f"x_vd_stand_{kind}", x, y, check=False, allow_reserved=True)


for x, y in ((5, 3), (14, 4), (22, 5), (30, 6), (44, 5), (16, 12), (8, 17), (10, 21)):
    dl("amber", x, y)
for x, y in ((12, 9), (24, 12), (36, 8), (31, 17)):
    dl("green", x, y)
for x, y in ((38, 12), (41, 15)):
    dl("red", x, y)
for x, y in ((8, 5), (18, 6), (27, 5), (36, 14), (4, 14), (10, 20), (22, 11)):
    d.put("x_vd_wet0" if (x + y) % 2 else "x_vd_wet1", x, y, check=False, allow_reserved=True)
for x, y in ((14, 3), (26, 3), (40, 5)):
    d.put("x_vd_drip", x, y, check=False, allow_reserved=True)
for x, y in ((35, 13), (39, 17), (42, 14)):
    d.put("x_vd_blood0", x, y, check=False, allow_reserved=True)
for x, y in ((12, 17), (13, 18)):
    d.put("x_vd_waterline", x, y, check=False, allow_reserved=True)

d.check(npc_enemy_gap=0)
d.save("data/maps/drain.json", style="drain", dark=195, night=[84, 92, 88])
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
b.enemies += [["robot_guard", 18, 18], ["robot_guard", 32, 14], ["turret", 20, 4]]   # двое и турель: склад берут на 3–4 уровне

# обстановка склада: караулка живёт, коридор не пуст, в хранилище — стеллажи партии 7, кабели и светильники
for y in (11, 13, 15):
    b.put(BUNK_U, 9, y)
b.put(LOCKER_U[0], 13, 10, check=False) if False else None
for x, y in ((8, 12), (13, 12), (13, 14)):
    b.put(LOCKER_U[(x + y) % 2], x, y)
b.put(CONSOLE_U[0], 12, 16)
b.put(LAMP_U, 11, 14)
b.put(LAMP_U, 14, 16)
for x in (10, 13, 16, 19, 22):
    b.put(LAMP_U, x, 20)
for x, y in ((9, 21), (16, 17), (24, 17)):
    b.put(WARN_U, x, y)
b.put(GEN_U, 5, 18)
for x in (14, 20):
    b.put(CRATES_U, x, 20) if False else None
for x, y in ((19, 8), (22, 8), (25, 8), (28, 8), (31, 8)):
    b.put(VRE_U, x, y)
for x, y in ((19, 14), (23, 14), (27, 14), (31, 14)):
    b.put(BIOHAZ_U, x, y)
for x, y in ((21, 15), (29, 15)):
    b.put(TUBE_U, x, y)
for x, y in ((19, 4), (24, 4), (28, 5), (32, 4)):
    b.put(SERVER_U, x, y)
for x, y in ((26, 5), (33, 8)):
    b.put(LAMP_U, x, y)
b.paint("G", 19, 12, 32, 12)            # решётчатый настил между рядами контейнеров — кабельный канал
b.paint("G", 3, 19, 5, 19)


# свет склада: холодный аварийный, красные лампы у турели, зелёное свечение чанов
for x, y in ((6, 17), (12, 18), (20, 18), (4, 20)):
    b.put("x_vd_stand_cold", x, y, check=False, allow_reserved=True)
for x, y in ((22, 4), (30, 7), (19, 15), (32, 15)):
    b.put("x_vd_stand_red", x, y, check=False, allow_reserved=True)
for x, y in ((24, 12), (28, 12)):
    b.put("x_vd_stand_green", x, y, check=False, allow_reserved=True)
b.check(npc_enemy_gap=0)
b.save("data/maps/baker7.json", style="vault", dark=170, night=[76, 84, 96], floors={"m": STEEL, "G": GRILLE})
print(f"Бейкер-7: объектов {len(b.props)}, врагов {len(b.enemies)}, контейнеров {len(b.containers)}")
city.save()
