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
TOWERS_W = [P(f"nv_tower{i}", f"pk:bcyber/bcyber_3_{n:03d}", foot=[2, 2], sight=True) for i, n in enumerate((4, 5, 6, 7))]
HOUSES_W = [P(f"nv_house{i}", f"pk:bcyber/bcyber_3_{n:03d}", foot=[2, 1], sight=True) for i, n in enumerate((0, 1, 2, 8, 9))]
CLINIC = P("nv_clinic", "pk:bcyber/p3/8,8,4,4", foot=[4, 2], sight=True)
SHOPPING = P("nv_shopping", "pk:bcyber/p3/12,8,4,4", foot=[4, 2], sight=True)
SERVICES = P("nv_services", "pk:bcyber/p3/0,8,4,2", foot=[4, 1], sight=True)
OFFICE = P("nv_office", "pk:bcyber/p3/4,8,4,4", foot=[4, 2], sight=True)
PLANTERS = P("nv_planters", "pk:bcyber/bcyber_2_007", foot=[4, 2])
KIOSK = [P("nv_kiosk", "pk:bcyber/bcyber_2_008", sight=True), P("nv_kiosk_b", "pk:bcyber/bcyber_2_009", sight=True)]
LAMPS_W = [P("nv_lamp", "pk:bcyber/p1/0,2,1,2", light=COOL), P("nv_lamp_b", "pk:bcyber/p1/3,2,1,2", light=COOL)]
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
PUDDLE = P("nv_puddle", "pk:cyber/p1/4,4,2,2", block=False, layer="floor")
STEAM = P("nv_holo", "pk:cyber/cyber_3_019", light=NEON([120, 220, 255]))
FENCE_N = P("nv_fence", "pk:cyber/cyber_1_034", foot=[4, 1])
# ядро
SERVERS = [P("nv_server", "pk:npower/npower_2_042"), P("nv_server_b", "pk:cyber/cyber_3_022", foot=[2, 1])]
HOLO = P("nv_core_holo", "pk:cyber/cyber_3_060", light={"r": 160, "color": [140, 220, 255], "at": [0.5, 0.4], "flicker": 0.1})
LAB_ARM = P("nv_lab_arm", "pk:cyber/cyber_3_025", foot=[2, 1])
TANKS = [P("nv_tank", "pk:fmbase/fmbase_1_004", sight=True, light=NEON([120, 200, 255])),
         P("nv_tank_b", "pk:fmbase/fmbase_1_010", sight=True, light=NEON([140, 255, 160]))]

WHITE = ["pk:bcyber/p2/0,0,1,1"]
WHITE_ROAD = ["pk:bcyber/p1/9,9,1,1"]
CIRCUIT = ["pk:bcyber/p2/4,0,1,1"]
DARK = ["pk:cyber/p1/0,4,1,1"]
DARK_B = ["pk:cyber/p2/0,4,1,1"]
GRATE = ["pk:cyber/p3/0,12,1,1"]


# ================================================================ Верхний ярус
W, H = 68, 46
up = CityMap(city, "nova", "«Нова»: Верхний ярус", W, H, start=(33, 43), seed=261, music="lab", world_pos=(2960, 380))
up.floor_code("w", *WHITE)
up.floor_code("r", *WHITE_ROAD)
up.floor_code("c", *CIRCUIT)
up.paint("w", 0, 0, W - 1, H - 1)
up.paint("r", 30, 0, 37, H - 1)                        # проспект с севера на юг
up.paint("r", 0, 20, W - 1, 25)                        # поперечный проспект
up.paint("c", 26, 34, 41, 42)                          # «Хаб чистоты» у шлюза
up.exits = [(x, H - 1) for x in range(31, 37)]
up.reserve(31, 0, 36, H - 1)
up.reserve(0, 20, W - 1, 25)
# шлюз купола и «Хаб чистоты» — санпропускник: всех, кто входит, сканируют
up.put(PURITY_GATE, 38, 36, check=False)               # пост санпропускника сбоку от шлюза — проход открыт
up.npcs += [["purity_officer", 29, 41], ["purity_bot", 38, 41]]
# башни по краям, дома горожан, сады
for i, (x, y) in enumerate(((3, 3), (8, 3), (58, 3), (63, 3))):
    up.put(TOWERS_W[i], x, y)
for i, (x, y) in enumerate(((14, 6), (19, 6), (42, 6), (47, 6), (52, 6), (14, 13), (47, 13))):
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
up.scatter([TREE_SMALL], 1, 1, W - 2, H - 2, 10)


# ================================================================ Нижний ярус
W, H = 68, 46
dn = CityMap(city, "nova_under", "«Нова»: Нижний ярус", W, H, start=(6, 6), seed=262, music="reno",
             night=[60, 52, 90])
dn.floor_code("d", *DARK)
dn.floor_code("e", *DARK_B)
dn.floor_code("g", *GRATE)
dn.paint("d", 0, 0, W - 1, H - 1)
dn.paint("e", 0, 18, W - 1, 24)                         # главная улица дна
dn.paint("e", 30, 0, 36, H - 1)
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
dn.scatter([TRASH] + ROBOTS, 1, 1, W - 2, H - 2, 8)


# ================================================================ Ядро НОВЫ
W, H = 40, 30
cr = CityMap(city, "nova_core", "Ядро НОВЫ", W, H, start=(6, 26), seed=263, interior=True, music="lab",
             night=[40, 50, 80])                           # полумрак, светятся только серверы и голограмма
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
cr.enemies += [["robot_guard", 10, 15], ["robot_guard", 30, 15], ["turret", 19, 4]]
# «Звездочёт»: инженер купола собрал лазер из оптики обсерватории — ИИ запер его в ядре
STASH = P("nv_stash", "pk:pmars/pmars_1_035", foot=[2, 1], search="military", title="оружейный ящик")
cr.box(STASH, 34, 26, "ящик инженера Оками", {"лазер «Звездочёт»": 1, "ядерный элемент": 20})

city.save(gap_exempt=("purity_officer", "purity_bot"))
L = json.load(open("data/locations.json", encoding="utf-8"))
L["nova"].update({"world_name": "Купол «Нова»"})
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
