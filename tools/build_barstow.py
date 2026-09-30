"""
Барстоу — изометрический город из нескольких локаций (тайлы «Zombie City», см. README → «Изометрия»).

  barstow         трасса I-15: мотель «Сансет», стоянка караванщиков (Роза), выходы на карту мира;
  barstow_depot   сортировочная: пути, платформы, водонапорная башня, контора депо — гули;
  barstow_center  центр: отель, магазин MART, кинотеатр «Мираж», руины — гули и светящиеся;
  barstow_order   тайное святилище Ордена Тайн за кинотеатром (пускает только с брошью Ордена).

Переходы между локациями — порталы (жёлтые ромбы на земле), на карту мира — с трассы.
Зачистка: когда в депо или в центре не остаётся гулей, район отмечается (clear_flag в
data/locations.json), это двигает квест «Зачистка Барстоу».

Запуск из папки game_project:  .venv/bin/python tools/build_barstow.py
"""
import json
import os

from isokit import Town, make_neon_tile

GHOULS = ["feral", "feral", "ghoul_runner"]
HORDE = ["feral", "feral", "feral", "ghoul_runner", "ghoul_runner"]


def horde(k, trigger, door, count, msg, kinds=HORDE):
    """Толпа в доме: подошёл к зоне trigger (x0, y0, x1, y1) — из клетки door вываливаются count гулей."""
    k.hordes.append({"trigger": list(trigger), "door": list(door), "count": count, "kinds": kinds, "msg": msg})


def ghouls(k, x0, y0, x1, y1, n, glowing=0):
    """Стая гулей в прямоугольнике (на свободных клетках)."""
    placed = 0
    for _ in range(n * 40):
        if placed >= n + glowing:
            break
        x, y = k.rnd.randint(x0, x1), k.rnd.randint(y0, y1)
        if not k.free(x, y) or (x, y) in {(e[1], e[2]) for e in k.enemies}:
            continue
        kind = "rad_mutant" if placed < glowing else k.rnd.choice(GHOULS)
        k.enemies.append([kind, x, y])
        k.taken.add((x, y))
        placed += 1


# ================================================================ трасса
def build_road():
    W, H = 44, 34
    k = Town(W, H, start=(2, 21), seed=31)
    k.dust(0, 0, W - 1, H - 1)
    k.road_x(20, 22)
    k.pavers(0, 18, W - 1, 19)
    k.pavers(0, 23, W - 1, 24)
    k.road_y(31, 33, 0, 17)                        # на север, к депо
    k.road_y(20, 22, 25, H - 1)                    # на юг, в центр
    k.exits = [(0, y) for y in (20, 21, 22)] + [(W - 1, y) for y in (20, 21, 22)]
    for t in k.exits:
        k.taken.add(t)
    k.portal([(x, 0) for x in (31, 32, 33)], "barstow_depot", (20, 31), "Депо")
    k.portal([(x, H - 1) for x in (20, 21, 22)], "barstow_center", (21, 2), "Центр Барстоу")

    # мотель «Сансет»: контора с неоном и четыре номера
    k.building(3, 10, 9, 16, "D", floor="Ground C1_N", doors=[("s", 3, 12)], windows=[("s", 1, 21), ("s", 5, 21)],
               sign="МОТЕЛЬ")
    k.sign("WallDetail 8", 6, 16, "s")
    k.terminal("Object22_S", 5, 10, "barstow_motel")
    k.box("Object26_S", 8, 10, "касса мотеля", {"крышки": 25, "отмычка": 1})
    for i, x0 in enumerate((12, 17, 22, 27)):
        k.building(x0, 11, x0 + 3, 16, "B", floor="Ground E1_N", doors=[("s", 1, 12)], windows=[("s", 3, 18)],
                   sign=f"{i + 4}")
        if i == 3:   # номер 7 — заперт, внутри тайник
            k.box("Object26_N", x0 + 2, 11, "тайник в номере 7", {"стимулятор": 1, "патроны": 15, "крышки": 40},
                  requires={"item": "отмычка", "msg": "Номер 7 заперт на два замка. Нужна отмычка."})
        else:
            k.box("Object17_N", x0 + 1, 11, "тумбочка", {"бинт": 1} if i == 0 else {"крышки": 6})
    k.sign("WallDetail 5", 30, 13, "e")            # пожарная лестница на торце

    # стоянка караванщиков
    camp = [(x, 9) for x in range(35, 43)]
    k.edge_line("Fence A1", camp, "n")
    k.edge_line("Fence A1", [(42, y) for y in range(9, 17)], "e")
    k.pavers(35, 9, 42, 16, broken=0.4)
    for x, y, t in [(36, 10, "Object25_N"), (37, 10, "Object19_N"), (41, 10, "Object1_N"), (41, 11, "Object23_E"),
                    (36, 14, "Object17_E"), (40, 15, "Object10_S")]:
        k.obj(t, x, y)
    k.npcs.append(["rose", 38, 13])

    # за дорогой — пустырь, машины, пара гулей у развалин
    k.building(4, 27, 11, 32, "A", floor="Ground A6_N", doors=[("n", 3, 3)], ruined=True)
    ghouls(k, 5, 28, 10, 31, 2)
    ghouls(k, 1, 25, W - 2, H - 2, 6)
    horde(k, (4, 24, 11, 26), (7, 28), 15, "Из развалин за дорогой вываливается толпа гулей!")
    k.car(1, 12, 20, "E")
    k.car(9, 26, 21, "E")
    k.car(4, 36, 27, "N")
    for x in range(3, W - 2, 6):
        k.lamp(x, 18)
        k.lamp(x + 3, 24)
    k.obj("Object20_N", 30, 19)
    k.obj("Object28_N", 23, 24)
    k.splats(1, 20, W - 2, 22, 10)
    k.scatter(["Object18_N", "Object13_N", "Object12_N"], 1, 1, W - 2, H - 2, 14, block=False, only_dust=True)
    k.grass(1, 1, W - 2, H - 2, 30)
    k.scatter(["Tree A1_N"], 1, 1, W - 2, 8, 3, only_dust=True)
    k.check()
    k.save("data/maps/barstow.json", hordes=k.hordes)
    return k


# ================================================================ депо
def build_depot():
    W, H = 42, 34
    k = Town(W, H, start=(20, 31), seed=32)
    k.dust(0, 0, W - 1, H - 1)
    for y in (6, 10, 14):                          # три пути
        k.rails_x(y)
    k.ground("Ground E1_N", 0, 8, W - 1, 8, rot=False)   # платформы между путями
    k.ground("Ground E1_N", 0, 12, W - 1, 12, rot=False)
    k.road_y(19, 21, 17, H - 1)
    k.portal([(x, H - 1) for x in (19, 20, 21)], "barstow", (32, 2), "Трасса")

    # грузы на платформах и у путей
    k.scatter(["Object25_N", "Object26_N", "Object17_E", "Object24_N", "Object23_N"], 1, 8, W - 2, 8, 10)
    k.scatter(["Object25_E", "Object26_E", "Object19_N", "Object1_N"], 1, 12, W - 2, 12, 9)
    k.scatter(["Object10_S", "Object11_S", "Object16_N"], 1, 15, W - 2, 17, 6)
    k.obj("Object6_N", 6, 3)                       # водонапорная башня
    for x in (3, 15, 27, 39):                      # семафоры
        if k.free(x, 5):
            k.obj("StreetLamp 2_N", x, 5)

    # контора депо
    k.building(24, 19, 36, 27, "D", floor="Ground E1_N", doors=[("s", 3, 12)],
               windows=[("s", 1, 21), ("s", 7, 21), ("s", 10, 21), ("w", 3, 21)], sign="ДЕПО")
    k.sign("WallDetail 5", 36, 22, "e")
    k.terminal("Object22_S", 26, 19, "barstow_depot")
    k.box("Object26_S", 30, 19, "сейф депо", {"крышки": 80, "патроны": 20, "стимулятор": 1},
          requires={"flag": "depot_safe_open", "msg": "Сейф депо. Электронный замок — открывается с терминала конторы."})
    k.box("Object17_N", 35, 23, "шкаф кладовщика", {"бинт": 2, "химикаты": 1})
    # склад-ангар без крыши (крышу снесло)
    k.building(4, 19, 14, 27, "B", floor="Ground E1_N", doors=[("e", 4, 3)], ruined=True)
    k.scatter(["Object25_N", "Object26_N", "Object24_N"], 5, 20, 13, 26, 6)
    k.box("Object24_N", 12, 25, "ящик с маркировкой West Tek", {"химикаты": 3, "антирадин": 1})

    ghouls(k, 2, 2, W - 3, 17, 14, glowing=2)
    ghouls(k, 5, 20, 13, 26, 3)
    ghouls(k, 25, 20, 35, 26, 2)
    horde(k, (15, 20, 18, 26), (12, 23), 18, "Ворота ангара трещат — изнутри лезет целая стая!")
    horde(k, (24, 28, 31, 31), (27, 25), 12, "Из конторы депо с воем выбегают гули!",
          kinds=HORDE + ["rad_mutant"])
    k.grass(1, 1, W - 2, H - 2, 18)
    k.splats(1, 1, W - 2, H - 2, 8)
    k.check()
    k.save("data/maps/barstow_depot.json", hordes=k.hordes)
    return k


# ================================================================ центр
def build_center():
    W, H = 44, 40
    k = Town(W, H, start=(21, 2), seed=33)
    k.dust(0, 0, W - 1, H - 1)
    k.road_y(20, 22)
    k.road_x(18, 20)
    k.pavers(17, 0, 19, H - 1)
    k.pavers(23, 0, 25, H - 1)
    k.pavers(0, 16, 16, 17)
    k.pavers(26, 16, W - 1, 17)
    k.pavers(0, 21, 16, 22)
    k.pavers(26, 21, W - 1, 22)
    k.portal([(x, 0) for x in (20, 21, 22)], "barstow", (21, 31), "Трасса")

    # отель
    k.building(2, 3, 14, 14, "B", floor="Ground E1_N", doors=[("s", 6, 17)],
               windows=[("s", 2, 22), ("s", 4, 21), ("s", 9, 22), ("s", 11, 21), ("e", 3, 21), ("e", 7, 22)],
               sign="HOTEL")
    k.sign("WallDetail 10", 8, 14, "s")
    k.sign("WallDetail 5", 14, 9, "e")
    k.scatter(["Object17_N", "Object25_N", "Object23_E", "Object14_N"], 3, 4, 13, 13, 7)
    k.box("Object26_N", 3, 3, "сейф портье", {"крышки": 50, "отмычка": 1})
    ghouls(k, 4, 5, 12, 12, 3)

    # магазин MART
    k.building(27, 3, 40, 14, "D", floor="Ground E1_N", doors=[("s", 5, 16)],
               windows=[("s", 2, 22), ("s", 9, 22), ("s", 11, 21)], sign="MART")
    k.sign("WallDetail 11", 33, 14, "s")
    k.scatter(["Object17_N", "Object25_E", "Object19_N", "Object24_N"], 28, 4, 39, 13, 8)
    k.box("Object26_S", 30, 3, "касса MART", {"крышки": 35, "бинт": 1, "самогон": 1})
    ghouls(k, 29, 5, 38, 12, 3)

    # кинотеатр «Мираж»: вход с улицы (восточная стена), неон на южной, за экраном — тайная дверь
    k.building(3, 24, 16, 36, "D", floor="Ground E1_N", doors=[("e", 5, 10)],
               windows=[("s", 3, 21), ("s", 10, 21)], sign="МИРАЖ")
    neon = make_neon_tile("МИРАЖ", "x_neon_mirage")
    k.obj(neon, 7, 36, block=False, k=(16 + 36 + 2.3) - (7 + 36))   # поверх крыши, как вывески набора
    for x in range(6, 14, 2):                      # ряды кресел — скамейки
        for y in (29, 31, 33):
            if k.free(x, y):
                k.obj("Object14_N", x, y)
    k.portal([(4, 25)], "barstow_order", (6, 8), "Тайная дверь",
             requires={"item": "знак Ордена Тайн",
                       "msg": "За экраном — дверь без ручки. На косяке выцарапан глаз в треугольнике. Не открывается."})
    k.box("Object24_N", 15, 35, "будка киномеханика", {"патроны": 6, "химикаты": 1})

    # руины квартала, светящиеся
    k.building(27, 25, 40, 37, "A", floor="Ground A6_N", doors=[("n", 5, 3)], ruined=True)
    k.scatter(["Object18_N", "Object13_N"], 28, 26, 39, 36, 6, block=False)
    ghouls(k, 28, 26, 39, 36, 3, glowing=1)

    # улицы: машины, фонари, мусор, гули
    k.car(2, 21, 7, "N")
    k.car(6, 20, 27, "N")
    k.car(11, 6, 18, "E")
    k.car(8, 33, 19, "E")
    for y in range(3, H - 2, 6):
        k.lamp(19, y)
        k.lamp(23, y + 3)
    k.obj("Object20_N", 19, 17)
    for x, y in ((24, 17), (24, 21), (18, 21)):
        if k.free(x, y):
            k.obj("Object27_N", x, y, block=False)
    ghouls(k, 17, 10, 25, 36, 8)
    ghouls(k, 0, 15, W - 1, 22, 6)
    horde(k, (5, 15, 11, 17), (8, 12), 20, "Двери отеля распахиваются — оттуда валит толпа постояльцев. Мёртвых.")
    horde(k, (29, 15, 35, 17), (32, 12), 16, "Витрина «D-MART» лопается — покупатели идут за скидками. На тебя.")
    horde(k, (17, 26, 19, 32), (13, 29), 15, "Сеанс окончен: из «Миража» выходят зрители.")
    horde(k, (29, 22, 35, 24), (32, 28), 15, "Руины оживают — гули лезут из-под обломков!",
          kinds=HORDE + ["rad_mutant"])
    k.splats(17, 0, 25, H - 1, 14)
    k.splats(0, 18, W - 1, 20, 8)
    k.grass(1, 1, W - 2, H - 2, 16)
    k.check()
    k.save("data/maps/barstow_center.json", hordes=k.hordes)
    return k


# ================================================================ святилище Ордена
def build_order():
    W, H = 14, 12
    k = Town(W, H, start=(6, 8), seed=34)
    k.building(1, 1, 12, 10, "A", floor="Ground C1_N", doors=[("s", 5, 3)], roof="Roof A3", sign="Ω")
    for x, y in ((3, 3), (10, 3), (3, 7), (10, 7)):
        k.obj("Pillar A1_N", x, y)
    k.terminal("Object22_S", 6, 1, "order")
    k.box("Object26_S", 9, 1, "шкатулка Ордена", {"стимулятор": 1, "антирадин": 1, "крышки": 60})
    k.portal([(6, 10)], "barstow_center", (5, 26), "Кинотеатр «Мираж»")
    # за дверью — ничего: святилище под землёй, вокруг тьма
    k.check()
    k.save("data/maps/barstow_order.json", dark=150)
    return k


if __name__ == "__main__":
    for name, fn in (("трасса", build_road), ("депо", build_depot), ("центр", build_center), ("святилище", build_order)):
        m = fn()
        print(f"Барстоу, {name}: {m.W}×{m.H}, объектов {len(m.objs)}, контейнеров {len(m.containers)}, "
              f"врагов {len(m.enemies)}, NPC {len(m.npcs)}")

    path = "data/locations.json"
    L = json.load(open(path, encoding="utf-8"))
    L.pop("town_iso", None)
    L["barstow"] = {"name": "Барстоу", "map": "data/maps/barstow.json", "world_pos": [70, 360], "known": False,
                    "music": "hub", "action": True}
    L["barstow_depot"] = {"name": "Барстоу: депо", "map": "data/maps/barstow_depot.json", "known": False,
                          "clear_flag": "barstow_depot_cleared", "music": "junktown", "action": True}
    L["barstow_center"] = {"name": "Барстоу: центр", "map": "data/maps/barstow_center.json", "known": False,
                           "clear_flag": "barstow_center_cleared", "music": "reno", "action": True}
    L["barstow_order"] = {"name": "Святилище Ордена Тайн", "map": "data/maps/barstow_order.json", "known": False,
                          "music": "vats"}
    json.dump(L, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    if os.path.isfile("data/maps/town_iso.json"):
        os.remove("data/maps/town_iso.json")   # пробный кусок изометрии заменён Барстоу
