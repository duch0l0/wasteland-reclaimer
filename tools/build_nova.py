"""
«Нова» — город под куполом. Довоенный проект RobCo «Город завтрашнего дня» в пустыне Невады: купол закрыли
23 октября 2077 года и открыли только в 2119-м. Тайная локация.
Сценарий — docs/story.md, раздел «„Нова“ — город под куполом».

  nova          «Нова: Верхний ярус» (68×46): белый город — башни, скайвеи, сады в кадках, «Хаб чистоты»
                (санпропускник), клиника, городские службы; горожане с идеальными улыбками.
  nova_under    «Нова: Нижний ярус» (68×46): неоновое дно купола — бары, раменные, оружейная лавка,
                стоянка аэрокаров; здесь живут те, кого Верх «отсеял», и роботы-уборщики.
  nova_core     «Ядро НОВЫ»: серверный зал ИИ, который управляет куполом — воздухом, водой и «отбором».

Наборы: bright-cyberpunk (bcyber), cyberpunk-city (cyber), futuristic-military-base (fmbase), nuclear-power-plant.
Запуск из папки game_project:  .venv/bin/python tools/build_nova.py
"""
import json

from citykit import City, CityMap

city = City("nova", "«Нова»")


def P(name, img, **kw):
    city.prop(name, img, **kw)
    return name


def cells(page, pts):
    return [f"pk:{page}/{x},{y},1,1" for x, y in pts]


NEON = lambda c: {"r": 110, "color": c, "at": [0.5, 0.5], "flicker": 0.15}
COOL = {"r": 120, "color": [190, 240, 255], "at": [0.5, 0.15]}
# ------------------------------------------------------------ Верх
TOWERS_W = [P(f"nv_tower{i}", f"pk:bcyber/bcyber_3_{n:03d}", foot=[3, 2], sight=True, scale=2) for i, n in enumerate((4, 5, 6, 7))]
HOUSES_W = [P(f"nv_house{i}", f"pk:bcyber/bcyber_3_{n:03d}", foot=[4, 2], sight=True, scale=2) for i, n in enumerate((0, 1, 2, 8, 9))]
CLINIC = P("nv_clinic", "pk:bcyber/p3/8,8,4,4", foot=[4, 2], sight=True)
SHOPPING = P("nv_shopping", "pk:bcyber/p3/12,8,4,4", foot=[4, 2], sight=True)
SERVICES = P("nv_services", "pk:bcyber/p3/0,8,4,2", foot=[4, 1], sight=True)
OFFICE = P("nv_office", "pk:bcyber/p3/4,8,4,4", foot=[4, 2], sight=True)
FOUNTAINS = [P("nv_fountain_a", "pk:bcyber/bcyber_2_012", foot=[1, 1], keybg=True), P("nv_fountain_b", "pk:bcyber/bcyber_2_013", foot=[1, 1], keybg=True),
             P("nv_fountain_c", "pk:bcyber/bcyber_2_015", foot=[1, 1], keybg=True)]
HEDGE_G = P("nv_hedge_green", "pk:bcyber/p1/4,8,1,3", foot=[1, 1], keybg=True)
HEDGE_H = P("nv_hedge_long", "pk:bcyber/p1/5,11,3,1", foot=[3, 1], keybg=True)
FLOWER_BED = [P("nv_flowers_a", "pk:bcyber/p1/12,8,2,1", foot=[2, 1], keybg=True), P("nv_flowers_b", "pk:bcyber/p1/12,9,2,1", foot=[2, 1], keybg=True)]
PLANTERS = P("nv_planters", "pk:bcyber/bcyber_2_007", foot=[4, 2])
KIOSK = [P("nv_kiosk", "pk:bcyber/bcyber_2_008", sight=True), P("nv_kiosk_b", "pk:bcyber/bcyber_2_009", sight=True)]
LAMPS_W = [P("nv_lamp", "pk:bcyber/bcyber_2_004", light=COOL), P("nv_lamp_b", "pk:bcyber/bcyber_2_006", light=COOL)]
TREE_W = P("nv_tree", "pk:bcyber/p1/0,12,2,3", foot=[2, 1], sight=True)
TREE_SMALL = P("nv_tree_small", "pk:bcyber/p1/8,12,1,2")
BENCH_W = P("nv_bench", "pk:bcyber/p1/12,9,2,1", foot=[2, 1])
TERMINAL_W = P("nv_terminal", "pk:bcyber/p1/14,8,1,2", light={"r": 70, "color": [150, 230, 255], "at": [0.5, 0.4]})
SIGNS_W = [P("nv_sign_sector", "pk:bcyber/bcyber_2_019", block=False), P("nv_sign_clinic", "pk:bcyber/bcyber_2_020", block=False),
           P("nv_sign_market", "pk:bcyber/bcyber_2_021", block=False)]
PURITY_GATE = P("nv_purity_gate", "pk:bcyber/p1/8,4,8,4", foot=[8, 2], sight=True)
HEDGE = P("nv_hedge", "pk:bcyber/p1/8,8,4,1", foot=[4, 1])
# ------------------------------------------------------------ Низ
TOWERS_N = [P("nv_n_tower", "pk:cyber/cyber_2_005", foot=[4, 2], sight=True, light=NEON([120, 200, 255])),
            P("nv_n_tower_b", "pk:cyber/cyber_2_003", foot=[4, 2], sight=True, light=NEON([120, 200, 255]))]
CYBERBAR = P("nv_cyberbar", "pk:cyber/cyber_1_035", foot=[2, 2], sight=True, light=NEON([255, 90, 200]))
RESTAURANT = P("nv_restaurant", "pk:cyber/cyber_2_019", foot=[4, 2], sight=True, light=NEON([255, 180, 90]))
WEAPONS = P("nv_weapons", "pk:cyber/cyber_2_020", foot=[4, 2], sight=True, light=NEON([255, 90, 90]))
CAFE = P("nv_cafe", "pk:cyber/cyber_3_012", foot=[4, 2], sight=True, light=NEON([255, 220, 120]))
NOODLES = P("nv_noodles", "pk:cyber/cyber_2_004", foot=[2, 1], sight=True, light=NEON([255, 150, 90]))
RAMEN_BAR = P("nv_ramen_bar", "pk:cyber/cyber_3_015", foot=[2, 1], sight=True, light=NEON([255, 120, 160]))
STALLS_N = [P("nv_stall_poster", "pk:cyber/cyber_3_038", foot=[2, 1], sight=True), P("nv_stall_food", "pk:cyber/cyber_3_039", foot=[2, 1], sight=True)]
VENDING = [P(f"nv_vending{i}", f"pk:cyber/cyber_1_{n:03d}", sight=True, search="junk", title="автомат") for i, n in enumerate((1, 2, 3, 4))]
NEON_SIGNS = [P("nv_neon_neon", "pk:cyber/cyber_2_000", block=False, light=NEON([255, 90, 220])),
              P("nv_neon_neon_b", "pk:cyber/cyber_2_001", block=False, light=NEON([90, 200, 255])),
              P("nv_neon_ramen", "pk:cyber/cyber_2_006", block=False, light=NEON([255, 160, 90]))]
BILLBOARDS = [P("nv_billboard", "pk:cyber/cyber_2_028", foot=[2, 1], sight=True, light=NEON([255, 120, 200])),
              P("nv_billboard_b", "pk:cyber/cyber_2_029", foot=[2, 1], sight=True, light=NEON([255, 90, 220]))]
LAMP_N = P("nv_n_lamp", "pk:cyber/cyber_1_030", light={"r": 130, "color": [255, 200, 140], "at": [0.5, 0.1]})
CARS = [P("nv_taxi", "pk:cyber/cyber_1_015", foot=[2, 1], sight=True), P("nv_car", "pk:cyber/cyber_1_017", foot=[2, 1], sight=True),
        P("nv_car_b", "pk:cyber/cyber_1_018", foot=[2, 1], sight=True)]
AEROCAR = P("nv_aerocar", "pk:cyber/cyber_1_012", foot=[4, 1], sight=True)
DRONE = P("nv_drone", "pk:cyber/cyber_1_016", foot=[2, 1], sight=True)
ROBOTS = [P("nv_robot", "pk:cyber/cyber_1_007"), P("nv_robot_b", "pk:cyber/cyber_1_008")]
TRASH = P("nv_trash", "pk:cyber/cyber_2_007")
PUDDLE = P("nv_puddle", "pk:cyber/p1/4,4,2,2", block=False, layer="floor", keybg=True)
STEAM = P("nv_holo", "pk:cyber/cyber_3_019", light=NEON([120, 220, 255]))
FENCE_N = P("nv_fence", "pk:cyber/cyber_1_034", foot=[4, 1])
# ядро
SERVERS = [P("nv_server", "pk:npower/npower_2_042"), P("nv_server_b", "pk:cyber/cyber_3_022", foot=[2, 1])]
HOLO = P("nv_core_holo", "pk:cyber/cyber_3_060", light={"r": 160, "color": [140, 220, 255], "at": [0.5, 0.4], "flicker": 0.1})
LAB_ARM = P("nv_lab_arm", "pk:cyber/cyber_3_025", foot=[2, 1])
TANKS = [P("nv_tank", "pk:fmbase/fmbase_1_004", sight=True, light=NEON([120, 200, 255])),
         P("nv_tank_b", "pk:fmbase/fmbase_1_010", sight=True, light=NEON([140, 255, 160]))]

GRAY = ["pk:bcyber/p1/0,0,1,1", "pk:bcyber/p1/0,1,1,1", "pk:bcyber/p1/0,4,1,1", "pk:bcyber/p1/0,5,1,1", "pk:bcyber/p1/0,8,1,1", "pk:bcyber/p1/0,9,1,1"]       # тротуар: серая плитка с белой сеткой, как в превью набора
ROAD_W = ["pk:bcyber/p1/2,1,1,1", "pk:bcyber/p1/2,2,1,1", "pk:bcyber/p1/2,8,1,1", "pk:bcyber/p1/1,8,1,1"]   # проезжая часть: гладкий белый композит
WHITE = ["pk:bcyber/p2/0,0,1,1"]
WHITE_ROAD = ["pk:bcyber/p2/1,1,1,1", "pk:bcyber/p2/2,1,1,1", "pk:bcyber/p2/1,2,1,1"]   # проезжая часть: белая с тонкими линиями, как в наборе
CIRCUIT = ["pk:bcyber/p2/4,0,1,1"]
DARK = ["pk:cyber/p1/0,4,1,1"]
DARK_B = ["pk:cyber/p2/0,4,1,1"]
GRATE = ["pk:cyber/p3/0,12,1,1"]


# ================================================================ Верхний ярус
W, H = 68, 46
up = CityMap(city, "nova", "«Нова»: Верхний ярус", W, H, start=(33, 43), seed=261, music="lab", world_pos=(2960, 380))
up.floor_code("g", *GRAY)
up.floor_code("w", *WHITE)
up.floor_code("r", *ROAD_W)
up.floor_code("c", *CIRCUIT)
up.paint("g", 0, 0, W - 1, H - 1)
up.paint("r", 31, 0, 36, H - 1)                        # проспект с севера на юг
up.paint("r", 0, 21, W - 1, 24)                        # поперечный проспект
for _x0, _y0, _x1, _y1 in ((17, 14, 30, 20), (17, 32, 30, 37), (37, 32, 51, 37), (37, 14, 51, 20), (2, 28, 14, 38), (53, 28, 66, 38)):
    up.paint("w", _x0, _y0, _x1, _y1)                  # белые площади перед входами и скверы — отдельные «кварталы»
for _x in (31, 33, 35):                                # пешеходные переходы через проспект у перекрёстка
    up.stamp(f"nv_zebra_n{_x}", "pk:bcyber/p1/1,4,2,1", _x, 19, water=False)
    up.stamp(f"nv_zebra_s{_x}", "pk:bcyber/p1/1,4,2,1", _x, 26, water=False)
for _y in (21, 23):
    up.stamp(f"nv_zebra_w{_y}", "pk:bcyber/p1/3,1,2,2", 28, _y, water=False)
    up.stamp(f"nv_zebra_e{_y}", "pk:bcyber/p1/3,1,2,2", 38, _y, water=False)
up.stamp("nv_emblem", "pk:bcyber/p1/4,5,4,2", 32, 22, water=False)     # эмблема «Хаб чистоты» на перекрёстке проспектов
up.crisp = True                                        # город из плитки: стыки ровные, как уложено
up.exits = [(x, H - 1) for x in range(31, 37)]
up.reserve(31, 0, 36, H - 1)
up.reserve(0, 20, W - 1, 25)
# шлюз купола и «Хаб чистоты» — санпропускник: всех, кто входит, сканируют
up.put(PURITY_GATE, 38, 36, check=False)               # пост санпропускника сбоку от шлюза — проход открыт
up.npcs += [["purity_officer", 29, 41], ["purity_bot", 38, 41]]
# башни по краям, дома горожан, сады
for i, (x, y) in enumerate(((2, 9), (7, 9), (58, 9), (63, 9))):
    up.put(TOWERS_W[i], x, y)
for i, (x, y) in enumerate(((13, 6), (19, 6), (41, 6), (47, 6), (52, 6), (13, 14), (50, 14),
                            (12, 43), (18, 43), (44, 43), (50, 43), (56, 43), (62, 43))):   # южный ряд — жилой квартал
    up.put(HOUSES_W[i % 5], x, y)
up.put(OFFICE, 22, 11)                                  # мэрия: «Совет Чистоты»
up.put(SIGNS_W[0], 23, 15)
up.put(CLINIC, 40, 28)
up.put(SIGNS_W[1], 41, 32)
up.put(SHOPPING, 22, 28)
up.put(SIGNS_W[2], 23, 32)
up.put(SERVICES, 50, 28)
up.put(PLANTERS, 4, 28)
up.put(PLANTERS, 58, 28)
for x, y in ((12, 18), (24, 18), (44, 18), (56, 18), (12, 27), (56, 37)):
    up.put(TREE_W, x, y)
for x, y in ((29, 19), (38, 19), (29, 26), (38, 26), (29, 4), (38, 4), (29, 32), (38, 32)):
    up.put(LAMPS_W[(x + y) % 2], x, y)
for x, y in ((16, 19), (50, 19), (16, 26), (50, 26)):
    up.put(BENCH_W, x, y)
up.put(KIOSK[0], 26, 18)
up.put(KIOSK[1], 41, 18)
up.terminal(39, 13, "nova_info")
# лифт вниз — в Нижний ярус: служебный, «для отсеянных»
up.props.append(["x_ladder", 6, 40])
up.portal([(6, 40)], "nova_under", (6, 5), "Служебный лифт — Нижний ярус")
up.reserve(4, 39, 8, 42)
up.npcs += [["councillor_vale", 25, 15], ["nv_citizen", 18, 21], ["nv_citizen_b", 46, 24], ["nv_doctor", 43, 33],
            ["nv_child", 15, 27]]
for _, x, y in up.npcs:
    up.reserve(x, y, x, y)
# Бульвары: ряды деревьев в кадках и фонарей вдоль проспектов, живая изгородь по краям скверов, скамьи и урны
for y in range(2, 19, 4):
    up.maybe(TREE_SMALL, 29, y)
    up.maybe(TREE_SMALL, 38, y)
for y in range(28, 44, 4):
    up.maybe(TREE_SMALL, 29, y)
    up.maybe(TREE_SMALL, 38, y)
for x in range(4, 28, 5):
    up.maybe(LAMPS_W[x % 2], x, 20)
    up.maybe(LAMPS_W[(x + 1) % 2], x, 25)
for x in range(40, 66, 5):
    up.maybe(LAMPS_W[x % 2], x, 20)
    up.maybe(LAMPS_W[(x + 1) % 2], x, 25)
for x, y in ((6, 31), (9, 33), (11, 31), (6, 35), (12, 36)):
    up.maybe(TREE_W if (x + y) % 3 == 0 else TREE_SMALL, x, y)
for x, y in ((56, 31), (59, 34), (61, 31), (57, 36), (63, 36)):
    up.maybe(TREE_W if (x + y) % 3 == 0 else TREE_SMALL, x, y)
for x, y in ((8, 29), (60, 29), (20, 33), (46, 33), (20, 16), (46, 16)):
    up.maybe(BENCH_W, x, y)
for x, y in ((7, 37), (11, 37), (57, 37), (62, 37)):
    up.maybe(PLANTERS, x, y)
# верхние кварталы: ряд малоэтажных домов и офисов у северной границы, антенны и солнечные панели на плоских крышах
for i, x in enumerate((3, 9, 15, 21, 42, 48, 54, 60)):
    up.maybe(HOUSES_W[(i + 2) % 5], x, 1)
up.maybe(OFFICE, 3, 20 - 6)
up.maybe(OFFICE, 60, 20 - 6)
for x, y in ((24, 8), (27, 8), (40, 8), (43, 8)):
    up.maybe(TREE_W, x, y)
for x, y in ((2, 17), (10, 17), (24, 17), (56, 17), (64, 17)):
    up.maybe(PLANTERS, x, y)
for x, y in ((4, 24), (14, 24), (44, 24), (54, 24), (64, 24)):
    up.maybe(BENCH_W, x, y)
for x, y in ((20, 24), (48, 24)):
    up.maybe(KIOSK[(x // 4) % 2], x, y)
# площади перед ТЦ и клиникой: фонтаны, ряды скамей, кадки с деревьями, терминалы — а не пустые плиты
for x, y in ((21, 34), (26, 34), (41, 34), (47, 34)):
    up.maybe(FOUNTAINS[(x + y) % 3], x, y)
for x in (19, 22, 25, 28):
    up.maybe(BENCH_W, x, 36)
for x in (39, 42, 45, 49):
    up.maybe(BENCH_W, x, 36)
for x, y in ((18, 33), (29, 33), (38, 33), (50, 33)):
    up.maybe(TREE_W, x, y)
for x, y in ((23, 37), (27, 37), (43, 37), (47, 37)):
    up.maybe(PLANTERS, x, y)
# южный жилой пояс: скверики между домами, лавки, фонари
for x in (3, 9, 15, 24, 41, 46, 53, 59, 64):
    up.maybe(TREE_SMALL, x, 41)
for x in (9, 15, 47, 53):
    up.maybe(BENCH_W, x, 40)
for x in (10, 16, 22, 40, 48, 56, 63):
    up.maybe(LAMPS_W[x % 2], x, 39)
# цветные акценты: клумбы и изгороди вдоль площадей, зелёные стены скверов, цветные вывески на углах
for x, y in ((18, 15), (24, 15), (44, 15), (49, 15), (19, 31), (26, 31), (40, 31), (47, 31)):
    up.maybe(FLOWER_BED[(x + y) % 2], x, y)
for x, y in ((17, 19), (27, 19), (40, 19), (50, 19), (17, 38), (27, 38), (40, 38), (50, 38)):
    up.maybe(HEDGE_H, x, y)
for x, y in ((3, 28), (14, 28), (53, 28), (65, 28)):
    for dy in (0, 1, 2):
        up.maybe(HEDGE_G, x, y + dy)
for x, y in ((29, 12), (38, 12), (29, 40), (38, 40)):
    up.maybe(SIGNS_W[(x + y) % 3], x, y)
up.scatter([TREE_SMALL], 1, 1, W - 2, 12, 4)


# ================================================================ Нижний ярус
W, H = 68, 46
dn = CityMap(city, "nova_under", "«Нова»: Нижний ярус", W, H, start=(6, 6), seed=262, music="reno",
             night=[92, 82, 128])
dn.crisp = True
dn.not_water = {"d", "e", "g"}                           # тёмная синеватая плитка — мостовая, а не вода
dn.floor_code("d", *DARK)
dn.floor_code("e", *DARK_B)
dn.floor_code("g", *GRATE)
dn.paint("d", 0, 0, W - 1, H - 1)
dn.paint("e", 0, 18, W - 1, 24)                         # главная улица дна
dn.paint("e", 30, 0, 36, H - 1)
for _x in range(0, W):                                   # решётки водостока по бордюрам главной улицы
    if not 30 <= _x <= 36:
        dn.ground[18][_x] = "g"
        dn.ground[24][_x] = "g"
for _y in range(0, H):
    if not 18 <= _y <= 24:
        dn.ground[_y][30] = "g"
        dn.ground[_y][36] = "g"
dn.props.append(["x_ladder", 6, 4])
dn.portal([(6, 4)], "nova", (6, 41), "Служебный лифт — наверх")
dn.reserve(3, 3, 9, 8)
dn.reserve(0, 18, W - 1, 24)
dn.reserve(30, 0, 36, H - 1)
# неоновые башни-трущобы, бары, лавки
dn.put(TOWERS_N[0], 12, 2)
dn.put(TOWERS_N[1], 50, 2)
dn.put(CYBERBAR, 20, 12)
dn.put(RESTAURANT, 38, 10)
dn.put(CAFE, 44, 10)
dn.put(WEAPONS, 38, 28)
dn.put(NOODLES, 14, 26)
dn.put(RAMEN_BAR, 20, 26)
dn.put(STALLS_N[0], 4, 26)
dn.put(STALLS_N[1], 8, 26)
for i, (x, y) in enumerate(((26, 14), (27, 14), (54, 14), (55, 14))):
    dn.put(VENDING[i], x, y)
for i, (x, y) in enumerate(((22, 10), (40, 8), (16, 24), (40, 26))):
    dn.put(NEON_SIGNS[i % 3], x, y)
dn.put(BILLBOARDS[0], 60, 12)
dn.put(BILLBOARDS[1], 60, 30)
for x, y in ((29, 17), (37, 17), (29, 25), (37, 25)):
    dn.put(LAMP_N, x, y)
# стоянка аэрокаров и мусор, лужи
dn.put(AEROCAR, 46, 34)
dn.put(CARS[0], 52, 38)
dn.put(CARS[1], 44, 40)
dn.put(DRONE, 56, 34)
for x, y in ((24, 30), (12, 36), (40, 36), (58, 22)):
    dn.put(PUDDLE, x, y)
for x, y in ((10, 32), (26, 38), (60, 40)):
    dn.put(TRASH, x, y)
dn.put(STEAM, 18, 36)
dn.hwall([FENCE_N], 2, 26, 42)
# вход в ядро — за решёткой на востоке
dn.props.append(["x_manhole", 62, 21])
dn.portal([(62, 21)], "nova_core", (6, 26), "Шахта ядра",
          requires={"flags_any": ["nova_core_pass", "nova_rebels_ally"],
                    "msg": "Решётка шахты под током. Хакерша Рэйвен в баре знает, как её обесточить. Или Советник Вэйл — как открыть."})
dn.reserve(60, 19, 64, 23)
dn.npcs += [["raven_hacker", 22, 16], ["noodle_cook", 15, 28], ["nv_dealer", 41, 32], ["nv_outcast", 10, 20],
            ["nv_outcast_b", 48, 21], ["cleaner_bot", 30, 34]]
for _, x, y in dn.npcs:
    dn.reserve(x, y, x, y)
# уличная жизнь: автоматы и мусорные баки у стен, голографические вывески, дроны, кучки хлама
for x, y in ((6, 14), (28, 10), (48, 16), (8, 32), (34, 30)):
    dn.maybe(STEAM, x, y)
for x, y in ((4, 20), (46, 21), (58, 24), (14, 40), (36, 42)):
    dn.maybe(TRASH, x, y)
for x, y in ((5, 15), (13, 30), (49, 30), (56, 38)):
    dn.maybe(DRONE, x, y)
for x, y in ((18, 20), (24, 22), (46, 20), (52, 22)):
    dn.maybe(ROBOTS[(x + y) % 2], x, y)
# неон по всему дну: вывески над лавками, лампы вдоль бордюров, светящиеся рекламные щиты — чёрных пятен между огнями нет
for x, y in ((8, 10), (16, 4), (24, 6), (44, 4), (56, 8), (62, 18), (6, 38), (24, 34), (46, 28), (56, 28), (62, 36)):
    dn.maybe(NEON_SIGNS[(x + y) % 3], x, y)
for x in range(4, 62, 8):
    if not 24 <= x <= 40:                                # у перекрёстка лампы уже стоят
        dn.maybe(LAMP_N, x, 17)
    if not 24 <= x + 4 <= 40:
        dn.maybe(LAMP_N, x + 4, 25)
for x, y in ((8, 4), (20, 4), (26, 36), (44, 36), (58, 4)):
    dn.maybe(BILLBOARDS[(x + y) % 2], x, y)
dn.scatter([TRASH] + ROBOTS, 1, 1, W - 2, H - 2, 8)


# ================================================================ Ядро НОВЫ
W, H = 40, 30
cr = CityMap(city, "nova_core", "Ядро НОВЫ", W, H, start=(6, 26), seed=263, interior=True, music="lab",
             night=[84, 100, 136])                           # полумрак, светятся только серверы и голограмма
cr.floor_code("M", *GRATE)
cr.wall_code("W", "pk:cyber/cyber_w1_11")
cr.room(1, 1, 39, 29, "W", "M")
cr.props.append(["x_ladder", 6, 27])
cr.portal([(6, 27)], "nova_under", (62, 22), "Наверх, на дно")
cr.reserve(3, 24, 9, 28)
for x in (4, 7, 10, 28, 31, 34):
    cr.put(SERVERS[0], x, 4)
cr.put(HOLO, 19, 12)
cr.put(TANKS[0], 12, 10)
cr.put(TANKS[1], 26, 10)
for x in (4, 8, 12, 26, 30, 34):                        # ряды серверных шкафов вдоль зала
    cr.maybe(SERVERS[1], x, 22)
for x, y in ((16, 14), (22, 14), (16, 10), (22, 10)):
    cr.put(TERMINAL_W, x, y)
cr.put(LAB_ARM, 14, 18)
cr.put(LAB_ARM, 24, 18)
cr.terminal(19, 8, "nova_core")
# Планировка ядра: север — стена серверов и накопители; центр — голограмма ИИ с кольцом терминалов и двумя капсулами;
# юг — лабораторные столы, ряды стоек охлаждения; боковые коридоры — кабель-каналы и аварийные пульты.
for x in (3, 6, 9, 31, 34, 37):
    cr.maybe(SERVERS[1], x, 7)
for y in (10, 14, 18):
    cr.maybe(SERVERS[0], 3, y)
    cr.maybe(SERVERS[0], 36, y)
for x, y in ((3, 13), (36, 13), (3, 17), (36, 17), (3, 21), (36, 21)):
    cr.maybe(LAB_ARM, x, y)
for x in (6, 14, 18, 22, 30):
    cr.maybe(TANKS[x % 2], x, 25)
for x, y in ((12, 22), (20, 22), (28, 22)):
    cr.maybe(TERMINAL_W, x, y)
for x, y in ((8, 14), (31, 14), (12, 19), (27, 19), (19, 22)):
    cr.maybe(HOLO if (x == 19) else TERMINAL_W, x, y)
for x, y in ((14, 27), (24, 27), (30, 27)):
    cr.maybe(SERVERS[0], x, y)
for x, y in ((8, 11), (31, 11), (4, 26), (35, 24)):
    cr.maybe(STEAM, x, y)
cr.enemies += [["robot_guard", 10, 15], ["robot_guard", 30, 15], ["turret", 19, 4]]
# «Звездочёт»: инженер купола собрал лазер из оптики обсерватории — ИИ запер его в ядре
STASH = P("nv_stash", "pk:pmars/pmars_1_035", foot=[2, 1], search="military", title="оружейный ящик")
cr.box(STASH, 34, 26, "ящик инженера Оками", {"лазер «Звездочёт»": 1, "ядерный элемент": 20})

# ================================================================ обжить пустыри (экскурсия: «белый город голый»)
B = lambda n, **kw: P(f"nv_{n}", f"pk:bcyber/bcyber_{n}", **kw)
FOUNTAIN = B("6_047", foot=[2, 1], sight=True)
PARK_TREE = B("6_017", foot=[2, 1], sight=True)
SNOW_TREE = B("4_040", foot=[2, 1], sight=True)
FLOWERS = B("6_032", foot=[2, 1])
TAXI, LIMO, CAR_W, CART = B("6_001", foot=[3, 1], sight=True), B("6_019", foot=[3, 1], sight=True), \
    B("6_008", foot=[3, 1], sight=True), B("6_024", foot=[2, 1], sight=True)
VEND_W, BIN_W, ATM_W = B("4_020", sight=True), B("4_033"), B("4_027", sight=True)
SOLAR = B("4_022", foot=[2, 1], sight=True)
GREEN_WALL, GREEN_WALL_B = B("6_005", foot=[2, 1], sight=True), B("6_021", foot=[2, 1], sight=True)
PALM_POT, FERN_POT, BALL_TREE = B("6_011"), B("6_039"), B("6_041")
PICKUP = B("7_019", foot=[2, 1], sight=True)
PURIFIER = B("4_024")
DRONE_W = B("4_003", block=False)
SIGN_SKY = B("4_028", block=False)
LAMP_TALL = B("2_003", light=COOL)
# сквер с фонтаном на юго-западе и стоянка аэротакси на юго-востоке
for name, x, y in ((FOUNTAIN, 5, 33), (PARK_TREE, 2, 31), (PARK_TREE, 9, 31), (FLOWERS, 2, 36), (FLOWERS, 8, 36),
                   (BENCH_W, 5, 36), (LAMP_TALL, 11, 34), (BALL_TREE, 1, 34),
                   (TAXI, 57, 32), (LIMO, 57, 34), (CAR_W, 61, 36), (CART, 62, 32), (SIGN_SKY, 55, 32),
                   (LAMP_TALL, 55, 36), (BIN_W, 65, 34), (VEND_W, 54, 38), (ATM_W, 55, 38)):
    up.put(name, x, y)
print("обжито наверху:", up.dress_empty([
    [(FOUNTAIN, 1, 1), (PARK_TREE, 4, 0), (FLOWERS, 0, 3), (BENCH_W, 3, 3), (LAMP_TALL, 5, 2)],
    [(TAXI, 0, 0), (LIMO, 0, 2), (SIGN_SKY, 4, 0), (LAMP_TALL, 4, 2)],
    [(VEND_W, 0, 0), (BIN_W, 1, 0), (ATM_W, 2, 0), (PALM_POT, 4, 0), (BENCH_W, 0, 2), (DRONE_W, 3, 2)],
    [(SOLAR, 0, 0), (SOLAR, 2, 0), (SOLAR, 4, 0), (SOLAR, 0, 2), (SOLAR, 2, 2), (PURIFIER, 4, 2)],
    [(GREEN_WALL, 0, 0), (GREEN_WALL_B, 2, 0), (FERN_POT, 4, 0), (FLOWERS, 0, 2), (BALL_TREE, 3, 2)],
    [(PICKUP, 0, 0), (BALL_TREE, 3, 0), (CART, 0, 2), (BIN_W, 3, 2)],
    [(SNOW_TREE, 0, 0), (BALL_TREE, 3, 0), (BENCH_W, 0, 2), (FLOWERS, 3, 2), (PALM_POT, 5, 1)],
    [(CAR_W, 0, 0), (CART, 3, 2), (LAMP_TALL, 0, 2), (BIN_W, 5, 0)],
], ground="w", block=7, margin=1, chance=1.0))

# серые кварталы между домами тоже жилые: скверики, парковки, площадки, зелёные стены, дроны; движение на проспектах
print("обжито серое:", up.dress_empty([
    [(PARK_TREE, 0, 0), (PARK_TREE, 3, 0), (BENCH_W, 1, 2), (FLOWERS, 4, 2), (LAMP_TALL, 6, 1)],
    [(CAR_W, 0, 0), (TAXI, 0, 2), (LAMP_TALL, 4, 0), (BIN_W, 5, 2)],
    [(FOUNTAIN, 1, 1), (FLOWERS, 0, 3), (FLOWERS, 3, 3), (BENCH_W, 4, 1)],
    [(GREEN_WALL, 0, 0), (GREEN_WALL_B, 2, 0), (BALL_TREE, 4, 0), (FERN_POT, 0, 2), (PALM_POT, 4, 2)],
    [(SOLAR, 0, 0), (SOLAR, 2, 0), (PURIFIER, 4, 0), (VEND_W, 0, 2), (BIN_W, 1, 2), (ATM_W, 2, 2)],
    [(SNOW_TREE, 0, 0), (SNOW_TREE, 3, 0), (BENCH_W, 1, 3), (DRONE_W, 4, 2)],
], ground="g", block=6, margin=1, chance=1.0, max_uses=4))
up.scatter([TREE_SMALL, BALL_TREE, PALM_POT, FERN_POT, BIN_W, FLOWERS], 1, 1, 28, 20, 26)
up.scatter([TREE_SMALL, BALL_TREE, PALM_POT, FERN_POT, BIN_W, FLOWERS], 39, 1, 66, 20, 26)
up.scatter([LAMP_TALL, LAMP_TALL, BENCH_W, FLOWER_BED[0], FLOWER_BED[1], HEDGE_H], 1, 1, 66, 20, 18)
up.scatter([TREE_SMALL, BALL_TREE, PALM_POT, FERN_POT, BIN_W, FLOWERS, LAMP_TALL], 1, 26, 28, 44, 20)
up.scatter([TREE_SMALL, BALL_TREE, PALM_POT, FERN_POT, BIN_W, FLOWERS, LAMP_TALL], 39, 26, 66, 44, 20)
for x, y in ((32, 6), (35, 10), (32, 30), (34, 38), (8, 22), (20, 23), (46, 22), (60, 23), (4, 23), (54, 22)):
    up.maybe([TAXI, LIMO, CAR_W][(x + y) % 3], x, y, check=False)
for x in range(4, 64, 6):
    up.maybe(DRONE_W, x, 17 + (x // 6) % 3)
print("обжито внизу:", dn.dress_empty([
    [(CARS[1], 0, 0), (TRASH, 3, 0), (PUDDLE, 0, 2), (LAMP_N, 4, 2)],
    [(STALLS_N[1], 0, 0), (VENDING[0], 3, 0), (TRASH, 0, 2), (NEON_SIGNS[2], 2, 2)],
    [(ROBOTS[0], 0, 0), (TRASH, 2, 1), (PUDDLE, 3, 2), (STEAM, 0, 3)],
    [(DRONE, 0, 0), (CARS[0], 0, 2), (LAMP_N, 3, 0)],
    [(BILLBOARDS[0], 0, 0), (TRASH, 3, 1), (VENDING[2], 0, 2), (PUDDLE, 2, 3)],
], ground="d", block=7, margin=1, chance=0.8, max_uses=2))

city.save(gap_exempt=("purity_officer", "purity_bot"))
L = json.load(open("data/locations.json", encoding="utf-8"))
L["nova"].update({"world_name": "Купол «Нова»"})
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
