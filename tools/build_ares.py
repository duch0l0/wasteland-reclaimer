"""
«Арес» — довоенная марсианская станция и полигон REPCONN, откуда к ней можно долететь. Тайная локация.
Сценарий — docs/story.md, раздел «„Арес“ — станция на Марсе».

  repconn        «Полигон REPCONN» (56×40): испытательная площадка в пустыне к югу от Вегаса — ангары, ракета
                 «Гелиос» на стартовом столе, бункер управления; бродят гули из бывшего персонала.
  ares           «Арес: поверхность» (66×46): красная равнина с кратерами, купола-оранжереи, вышки связи,
                 марсоход, солнечные панели, шлюз жилого модуля; посадочная площадка «Гелиоса».
  ares_hab       «Арес: жилой модуль»: каюты, кают-компания, медблок, оранжерея, рубка связи с Землёй.
  ares_lab       «Арес: лаборатория»: криокапсулы экипажа, ВРЭ-опыты «Проекта Арес», реактор станции.

Наборы: mars-base DLC (mars), pixel-mars-base (pmars), futuristic-military-base (fmbase), abandoned-military-base (mbase),
wasteland-laboratory (wlab), nuclear-power-plant (npower).
Запуск из папки game_project:  .venv/bin/python tools/build_ares.py
"""
import json

from citykit import City, CityMap, tech_scenes
from vaultkit import Lamps

city = City("ares", "«Арес»")
LM = Lamps(city)


def P(name, img, **kw):
    city.prop(name, img, **kw)
    return name


def cells(page, pts):
    return [f"pk:{page}/{x},{y},1,1" for x, y in pts]


GLOW = lambda c: {"r": 110, "color": c, "at": [0.5, 0.4], "flicker": 0.1}
# ------------------------------------------------------------ полигон REPCONN
HANGAR = P("ar2_hangar", "pk:mbase/mbase_2_015", foot=[6, 3], sight=True)
BUNKER = P("ar2_bunker", "pk:mbase/mbase_2_004", foot=[4, 3], sight=True)
WATCHTOWER = P("ar2_watchtower", "pk:mbase/mbase_2_005", foot=[2, 1], sight=True)
FUEL = [P("ar2_fuel", "pk:pmars/pmars_1_019", foot=[4, 1], sight=True), P("ar2_fuel_b", "pk:pmars/pmars_1_013", foot=[2, 1], sight=True)]
RADAR = P("ar2_radar", "pk:pmars/pmars_1_002", foot=[2, 1], sight=True,
          light={"r": 80, "color": [255, 90, 80], "at": [0.5, 0.05], "flicker": 0.5})
BARBED = P("ar2_barbed", "pk:mbase/p1/8,2,2,2", foot=[2, 1], keybg=True)
CONTROL = P("ar2_control", "pk:mars/mars_2_020", foot=[2, 1], sight=True)
# ------------------------------------------------------------ Марс
DOMES = [P("ar2_dome_lab", "pk:mars/mars_1_000", foot=[4, 2], sight=True, light=GLOW([170, 230, 255])),
         P("ar2_dome_hab", "pk:mars/mars_1_001", foot=[4, 2], sight=True, light=GLOW([170, 230, 255]))]
GREENHOUSES = [P(f"ar2_greenhouse{i}", f"pk:pmars/pmars_1_{n:03d}", foot=[2, 1], sight=True, light=GLOW([150, 255, 150]))
               for i, n in enumerate((5, 6, 7))]
SILO = [P("ar2_silo", "pk:mars/mars_1_004", foot=[2, 1], sight=True), P("ar2_silo_b", "pk:mars/mars_1_005", foot=[2, 1], sight=True)]
MODULES = [P(f"ar2_module{i}", f"pk:mars/mars_1_{n:03d}", foot=[2, 1], sight=True) for i, n in enumerate((7, 8, 9, 11, 16, 17, 18))]
AIRLOCK = P("ar2_airlock", "pk:mars/mars_1_010", foot=[2, 1], sight=True, light=GLOW([255, 160, 90]))
COMM_TOWER = [P("ar2_tower", "pk:pmars/pmars_1_001", foot=[2, 1], sight=True,
                light={"r": 90, "color": [255, 90, 80], "at": [0.5, 0.05], "flicker": 0.5}),
              P("ar2_tower_b", "pk:pmars/pmars_1_002", foot=[2, 1], sight=True)]
ROVER = P("ar2_rover", "pk:pmars/pmars_1_000", foot=[2, 1], sight=True)
SOLAR = P("ar2_solar", "pk:pmars/p1/1,8,1,2")
TANKS = [P("ar2_tank_water", "pk:pmars/pmars_1_014", foot=[2, 1], sight=True),
         P("ar2_tank_green", "pk:pmars/pmars_1_013", foot=[2, 1], sight=True)]
FACTORY = P("ar2_factory", "pk:pmars/pmars_1_008", foot=[4, 1], sight=True)
CRATES = [P("ar2_crate", "pk:pmars/pmars_1_035", foot=[2, 1], search="crate", title="контейнер снабжения"),
          P("ar2_crate_b", "pk:pmars/p1/12,14,1,1", search="crate", title="ящик")]
CRATER = "pk:pmars/p1/4,2,2,2"
CRATER_BIG = "pk:pmars/p1/2,4,2,2"
ROCKS = [P("ar2_rock", "pk:pmars/p1/1,1,1,1", block=False, soft=14), P("ar2_rock_b", "pk:pmars/p1/2,2,1,1", block=False, soft=14),
         P("ar2_boulder", "pk:pmars/p1/0,2,1,1", soft=14)]                  # края тают в грунт — без квадратов
FENCE = P("ar2_fence", "pk:mars/p1/12,14,4,2", foot=[4, 1], sight=True)
# интерьеры
BUNKS = [P(f"ar2_bunk{i}", f"pk:mars/mars_2_{n:03d}", foot=[2, 1], sight=True) for i, n in enumerate((0, 2, 3, 4, 7))]
CONSOLES = [P(f"ar2_console{i}", f"pk:mars/mars_2_{n:03d}", foot=[2, 1], sight=True) for i, n in enumerate((5, 6, 13, 14, 20, 21, 24, 25))]
SCREENS = [P(f"ar2_screen{i}", f"pk:mars/mars_2_{n:03d}", foot=[2, 1], sight=True) for i, n in enumerate((26, 27, 28, 29))]
DESKS = [P("ar2_desk", "pk:mars/mars_2_015", foot=[4, 1]), P("ar2_desk_b", "pk:mars/mars_2_016", foot=[2, 1])]
PLANTS = [P(f"ar2_plant{i}", f"pk:mars/mars_2_{n:03d}") for i, n in enumerate((32, 40, 42, 47, 48, 49, 50))]
PLANTERS = [P("ar2_planter", "pk:mars/mars_2_051", foot=[2, 1]), P("ar2_planter_b", "pk:mars/mars_2_052", foot=[2, 1]),
            P("ar2_planter_c", "pk:mars/mars_2_053", foot=[2, 1])]
LOCKERS = [P("ar2_locker", "pk:mars/mars_2_055", foot=[2, 1], sight=True, search="locker", title="шкафчик экипажа"),
           P("ar2_locker_b", "pk:mars/mars_2_061", foot=[2, 1], sight=True, search="locker", title="шкафчик экипажа")]
KITCHEN = P("ar2_kitchen", "pk:mars/mars_2_023", foot=[4, 1])
TABLE = P("ar2_table", "pk:mars/mars_2_035", foot=[2, 1])
CRYO = [P("ar2_cryo", "pk:wlab/wlab_3_101", foot=[2, 1], sight=True, light=GLOW([140, 220, 255])),
        P("ar2_cryo_b", "pk:wlab/wlab_3_102", foot=[2, 1], sight=True, light=GLOW([140, 220, 255])),
        P("ar2_cryo_dead", "pk:wlab/wlab_3_103", foot=[2, 1], sight=True)]
VAT = P("ar2_vat", "pk:wlab/wlab_1_002", foot=[2, 1], sight=True, light=GLOW([140, 255, 140]))
REACTOR = P("ar2_reactor", "pk:fmbase/fmbase_1_003", foot=[2, 1], sight=True, light=GLOW([110, 200, 255]))
MED_BED = P("ar2_med_bed", "pk:hosp/hosp_1_007", foot=[3, 1])

SAND = ["pk:desnat/p1/0,0,1,1", "pk:desnat/p1/1,0,1,1", "pk:desnat/p1/0,1,1,1"]   # песок под цвет окружающей пустыни
CONCRETE = ["noise:pk:mbase/p1/9,9,1,1"]            # гравий полигона — бесшовный шум, без сетки выбоин
PAVE = ["noise:pk:zcity/zcity_f2_26"]             # асфальт дорог полигона
MARS = cells("pmars/p1", [(0, 0), (0, 1), (1, 0)])        # гладкий грунт; дюны (0–1, 4–5) — цельный кусок 2×2, по клетке шьются швами
MARS_PAD = ["pk:fstation/fstation_f2_09"]
FLOOR = ["pk:fstation/fstation_f2_04"]
FLOOR_B = ["pk:store/p1/12,0,1,1"]
GRATE = cells("nbunk/p2", [(0, 12), (1, 13), (2, 14), (3, 12)])


# ================================================================ полигон REPCONN
W, H = 56, 40
rp = CityMap(city, "repconn", "Полигон REPCONN", W, H, start=(1, 20), seed=271, music="desert", world_pos=(2680, 640),
             night=[176, 152, 150])
rp.floor_code("s", *SAND)
rp.floor_code("c", *CONCRETE)
rp.paint("s", 0, 0, W - 1, H - 1)
rp.floor_code("r", *PAVE)
rp.floor_code("p", *MARS_PAD)
rp.floor_code("k", "pk:desnat/p1/10,4,1,1")
rp.floor_code("t", "pk:desnat/p1/4,4,1,1", "pk:desnat/p1/5,4,1,1")
rp.paint_ragged("c", 7, 1, 55, 38, depth=3)          # площадка с рваным краем, как вытоптанная земля
rp.paint("a", 0, 19, 31, 21)                          # дорога от ворот к стартовому столу
rp.paint("p", 35, 11, 47, 23)                         # стартовый стол — плиты
rp.paint("a", 20, 6, 22, 36)                          # магистраль вдоль ангаров и бункера
for _y in range(6, 37, 4):
    rp.ground[_y][21] = rp.ground[_y + 1][21] = "v" if _y not in range(19, 22) else "a"
for _x in range(2, 31, 4):
    rp.ground[20][_x] = rp.ground[20][_x + 1] = "h"
rp.exits = [(0, y) for y in range(18, 23)]
rp.reserve(0, 18, 12, 22)
rp.reserve(10, 19, 31, 21)
rp.reserve(20, 6, 22, 36)
rp.hwall([BARBED], 10, 52, 4)
rp.hwall([BARBED], 10, 52, 36)
for x, y in ((11, 5), (50, 5), (11, 34), (50, 34)):
    rp.put(WATCHTOWER, x, y)
rp.put(HANGAR, 14, 6)
rp.put(HANGAR, 14, 26)
rp.put(BUNKER, 25, 14)
rp.put(FUEL[0], 34, 30)
rp.put(FUEL[1], 40, 30)
rp.put(RADAR, 44, 8)
# стартовый стол: ракета «Гелиос» и пульт запуска
rp.put("x_rocket", 40, 16)
rp.put(CONTROL, 32, 18)
rp.terminal(34, 20, "repconn_launch")
rp.portal([(40, 17), (41, 17)], "ares", (32, 40), "Борт «Гелиоса» — на Марс",
          requires={"flag": "rocket_ready", "msg": "Люк «Гелиоса» задраен. Пульт запуска: «Топливо — 0 %. Навигация — не задана»."})
rp.reserve(39, 17, 42, 19)
rp.put(FUEL[1], 46, 30)
for x, y in ((30, 7), (36, 9), (46, 14), (48, 20), (30, 26), (36, 30), (18, 14), (18, 22), (48, 34), (14, 33)):
    rp.maybe(CRATES[(x + y) % 2], x, y)
rp.scatter(["r_trash", "pile_junk", "barrel_wood", "r_rocks"], 12, 6, 50, 34, 14)

# ---- полигон живёт: блокпост на въезде, прожекторы, стоянка машин, ряды бочек, засевшие в бункере; подсветка вечернего дня
rp.patchwork("s", ["t"], 16, 2, 5, seed=11)
rp.patchwork("c", ["k"], 20, 1, 3, seed=12)
for x in list(range(4, 32, 8)) + [50]:
    rp.maybe("r_streetlamp", x, 18)
    rp.maybe("r_streetlamp", x + 4, 22)
for x, y in ((8, 17), (8, 23)):
    rp.maybe("r_sandbag_row", x, y)
for x, y in ((6, 18), (6, 22), (23, 12), (31, 24), (38, 26), (42, 11)):
    rp.maybe("x_fire_barrel", x, y, check=False)
for x, y in ((24, 6), (26, 30), (36, 33)):
    rp.maybe("r_army_truck", x, y)
for x, y in ((30, 14), (44, 25), (30, 32)):
    rp.maybe("r_pickup", x, y)
rp.maybe("r_tanker", 38, 34)
for x, y in ((28, 6), (33, 7), (47, 11), (46, 27), (28, 28), (24, 33)):
    rp.maybe("r_barrels", x, y)
for x, y in ((26, 11), (28, 11), (30, 11)):
    rp.maybe("r_sandbag_row_b", x, y)
rp.maybe("sign_72", 3, 17)
rp.maybe("sign_stop", 9, 17)
rp.maybe("r_billboard", 3, 24)
for x, y in ((44, 14), (36, 21)):
    rp.maybe("lantern_lit", x, y)
LM.decals(rp, "x_vd_hz_h", [(36, 17), (37, 17), (38, 17)])
LM.decals(rp, "x_vd_blood0", [(24, 20), (29, 20), (34, 24)])
LM.decals(rp, "x_vd_oil0", [(18, 8), (30, 28), (44, 32)])
LM.decals(rp, "x_vd_ruts_h", [(12, 20), (16, 20), (24, 20)])
rp.enemies += [["feral", 20, 30], ["ghoul_runner", 28, 10], ["feral", 46, 24]]
rp.npcs += [["repconn_ghoul", 30, 22]]


# ================================================================ Марс: поверхность
W, H = 66, 46
mr = CityMap(city, "ares", "«Арес»: поверхность Марса", W, H, start=(32, 40), seed=272, music="lab",
             night=[150, 96, 80])                              # красное небо, тусклое солнце
mr.tint = [255, 214, 190]
mr.floor_code("m", "noise:pk:pmars/p1/0,0,1,1")         # грунт — бесшовный шум в цветах марсианского тайла (без сетки)
mr.floor_code("p", *MARS_PAD)
mr.paint("m", 0, 0, W - 1, H - 1)
mr.paint("p", 28, 36, 37, 44)                          # посадочная площадка
mr.paint("p", 31, 14, 34, 36)                          # дорожка к шлюзу
mr.put("x_rocket", 32, 39, check=False)
mr.portal([(30, 42), (31, 42)], "repconn", (40, 19), "Борт «Гелиоса» — домой")
mr.reserve(28, 36, 37, 44)
mr.reserve(30, 14, 35, 36)
# жилой купол и лабораторный купол, шлюз между ними
mr.put(DOMES[1], 22, 6)
mr.put(DOMES[0], 38, 6)
mr.put(AIRLOCK, 32, 10)
mr.portal([(32, 12), (33, 12)], "ares_hab", (16, 26), "Шлюз жилого модуля")
mr.reserve(31, 11, 34, 14)
# оранжереи, баки, мастерская
for i, (x, y) in enumerate(((10, 14), (14, 14), (10, 20))):
    mr.put(GREENHOUSES[i], x, y)
mr.put(TANKS[0], 48, 16)
mr.put(TANKS[1], 52, 16)
mr.put(FACTORY, 46, 22)
for i, (x, y) in enumerate(((16, 24), (44, 28), (52, 28))):
    mr.put(MODULES[i], x, y)
mr.put(SILO[0], 56, 8)
mr.put(SILO[1], 60, 8)
# связь и марсоход
mr.put(COMM_TOWER[0], 6, 6)
mr.put(COMM_TOWER[1], 58, 34)
mr.put(ROVER, 20, 32)
for x in range(4, 16, 2):
    mr.put(SOLAR, x, 30)
mr.box(CRATES[0], 40, 32, "контейнер снабжения 2077", {"консервы": 3, "стимулятор": 2})
# кратеры, камни
mr.npcs += [["rover_bot", 24, 30]]
for x, y in ((24, 20), (40, 20), (12, 36), (50, 12), (60, 30), (6, 26)):   # ещё купола и модули — станция большая
    mr.maybe([DOMES[0], MODULES[3], MODULES[4], GREENHOUSES[1], MODULES[5], MODULES[6]][(x + y) % 6], x, y)
for i, (x, y) in enumerate(((4, 38), (54, 40), (60, 22), (2, 12), (22, 42))):
    mr.stamp(f"ar2_crater{i}", CRATER if i % 2 else CRATER_BIG, x, y, water=False, soft=True)
# камни и воронки — на открытом грунте, не ближе 3 клеток к постройкам (а не «дом на кратере»)
from src import props as P_  # noqa: E402
_busy = set(mr.reserved)
for _e in mr.props:
    if P_.CATALOG.get(_e[0], {}).get("layer") != "floor":
        for _t in mr.footprint(_e[0], _e[1], _e[2]):
            _busy.update((_t[0] + dx, _t[1] + dy) for dx in range(-3, 4) for dy in range(-3, 4))
_rnd = __import__("random").Random(272)
_n = 0
for _ in range(600):
    if _n >= 22:
        break
    _x, _y = _rnd.randint(2, W - 4), _rnd.randint(2, H - 4)
    if any((_x + i, _y + j) in _busy for i in range(-1, 3) for j in range(-1, 3)):
        continue
    if mr.maybe(_rnd.choice(ROCKS), _x, _y):
        _busy.update((_x + i, _y + j) for i in range(-2, 4) for j in range(-2, 4))
        _n += 1


# ---- станция обжита: плиточные дорожки между куполами, маячки, кабели, следы колёс марсохода, трубы и ящики
mr.paint("p", 11, 18, 54, 19)
mr.paint("p", 12, 14, 13, 30)
mr.paint("p", 50, 14, 51, 30)
mr.paint("p", 24, 9, 25, 13)
mr.paint("p", 24, 12, 31, 12)
mr.paint("p", 39, 9, 40, 13)
mr.paint("p", 33, 12, 40, 12)
for x, y in ((14, 18), (22, 18), (28, 20), (38, 20), (46, 18), (52, 18), (12, 24), (51, 24), (26, 11), (39, 11)):
    LM.lamp(mr, "cold", x, y)
for x, y in ((8, 28), (18, 34), (42, 36), (30, 30)):
    mr.maybe("x_vd_ruts_h", x, y)
    mr.maybe("x_vd_ruts_h", x + 1, y)
for x, y in ((44, 18), (36, 24), (22, 26), (54, 24)):
    mr.maybe(CRATES[(x + y) % 2], x, y)
for x, y in ((46, 36), (50, 38), (8, 34)):
    mr.maybe(FUEL[1], x, y)
LM.decals(mr, "x_vd_oil0", [(14, 22), (47, 24), (26, 20)])

# равнина живёт: тёмные базальтовые пятна и светлая пыль, следы колёс и ног, кучи камней, брошенные ящики, флажки разметки
for x, y in ((8, 30), (14, 34), (20, 36), (44, 34), (30, 28), (6, 8), (60, 14), (52, 20)):
    mr.maybe("x_vd_ruts_h", x, y, check=False)
    mr.maybe("x_vd_ruts_h", x + 1, y, check=False)
    mr.maybe("x_vd_ruts_h", x + 2, y, check=False)
for x, y in ((20, 28), (24, 33), (36, 33), (40, 36), (28, 22)):
    mr.maybe("x_vd_steps", x, y, check=False)
for x, y in ((6, 20), (14, 4), (26, 3), (46, 4), (62, 18), (4, 42), (58, 42), (44, 42), (12, 41)):
    mr.maybe(ROCKS[2], x, y)
for x, y in ((18, 40), (46, 38), (56, 20), (8, 18), (62, 36), (24, 3)):
    mr.maybe(CRATES[(x + y) % 2], x, y)
for x, y in ((15, 12), (28, 18), (44, 18), (56, 26), (9, 26)):
    mr.maybe(SOLAR, x, y)
for x, y in ((8, 14), (20, 14), (52, 14), (62, 26), (40, 38)):
    LM.lamp(mr, "cold", x, y)
mr.scatter([ROCKS[0].replace("ar2_rock", "ar2_rock") if False else "ar2_rock", "ar2_rock_b", "ar2_boulder"], 1, 1, W - 2, H - 2, 34)


# ================================================================ жилой модуль
W, H = 40, 30
hb = CityMap(city, "ares_hab", "«Арес»: жилой модуль", W, H, start=(16, 26), seed=273, interior=True, music="lab",
             night=[118, 126, 150])
hb.floor_code("F", *FLOOR)
hb.floor_code("B", *FLOOR_B)
hb.floor_code("G", *GRATE)
hb.wall_code("W", "pk:mars/mars_w2_08")
hb.room(1, 14, 39, 29, "W", "F")                       # кают-компания
hb.room(1, 1, 14, 14, "W", "B")                        # каюты
hb.room(14, 1, 27, 14, "W", "G")                       # оранжерея
hb.room(27, 1, 39, 14, "W", "F")                       # рубка связи
hb.opening(16, 29, 17, 29, "F")
hb.portal([(16, 29), (17, 29)], "ares", (32, 14), "Шлюз — на поверхность")
hb.opening(7, 14, 8, 16, "B")
hb.opening(20, 14, 21, 16, "G")
hb.opening(32, 14, 33, 16, "F")
# кают-компания: кухня, столы, медблок в углу
hb.put(KITCHEN, 3, 17)
for x in (10, 16, 22):
    hb.put(TABLE, x, 21)
hb.put(MED_BED, 28, 20)
hb.box(LOCKERS[0], 36, 18, "медицинский шкаф", {"стимулятор": 2, "антирадин": 2}, owner="cmdr_hale")
for x in (3, 36):
    hb.put(PLANTS[x % 7], x, 26)
hb.props.append(["x_ladder", 36, 25])
hb.portal([(36, 25)], "ares_lab", (6, 26), "Вниз, в лабораторию")
hb.reserve(34, 24, 38, 27)
hb.npcs += [["cmdr_hale", 18, 19], ["eng_okoro", 12, 24]]
# каюты: койки, шкафчики
for i, (x, y) in enumerate(((2, 4), (6, 4), (10, 4))):
    hb.put(BUNKS[i], x, y)
hb.box(LOCKERS[1], 2, 10, "шкафчик экипажа", {"фото Земли": 1})
# оранжерея: грядки в кадках, растения
for i, (x, y) in enumerate(((16, 5), (20, 5), (24, 5), (16, 10), (24, 10))):
    hb.put(PLANTERS[i % 3], x, y)
hb.npcs += [["botanist_yuki", 20, 9]]
# рубка: экраны с картой Земли, консоли
for i, x in enumerate((29, 31, 33, 35)):
    hb.put(SCREENS[i], x, 4)
hb.put(CONSOLES[4], 29, 9)
hb.terminal(36, 10, "ares_comm")

# кают-компания живёт: диваны, столы со стульями, торговый автомат; каюты — личные вещи; рубка — карты и свет
for x, y in ((6, 24), (14, 24), (20, 24)):
    hb.maybe(TABLE, x, y)
for x, y in ((3, 22), (22, 18), (30, 24), (26, 26)):
    hb.maybe(PLANTS[(x + y) % 7], x, y)
for x, y in ((24, 17), (32, 17), (30, 21)):
    hb.maybe(LOCKERS[(x + y) % 2], x, y)
for x, y in ((3, 8), (6, 8), (11, 8), (3, 12), (11, 12)):
    hb.maybe(LOCKERS[(x + y) % 2], x, y)
for x, y in ((18, 12), (22, 12), (26, 8)):
    hb.maybe(PLANTERS[(x + y) % 3], x, y)
LM.lamps(hb, "cold", [(12, 19), (28, 19), (8, 6), (22, 6), (33, 6)])
LM.decals(hb, "x_vd_hz_h", [(12, 26), (13, 26), (14, 26)])
LM.decals(hb, "x_vd_tally", [(4, 15), (24, 15)])
LM.decals(hb, "x_vd_drawing", [(9, 15), (35, 3)])
LM.decals(hb, "x_vd_map", [(31, 3)])
LM.doors(hb)
print("жилой модуль hb:", hb.dress_empty(tech_scenes(city, "ar6"), ground="F", block=7, margin=1, chance=0.9))


# ================================================================ лаборатория
W, H = 40, 30
lb = CityMap(city, "ares_lab", "«Арес»: лаборатория", W, H, start=(6, 26), seed=274, interior=True, music="vats",
             night=[96, 106, 134])
lb.floor_code("F", *FLOOR)
lb.wall_code("W", "pk:mars/mars_w2_10")
lb.room(1, 1, 39, 29, "W", "F")
lb.props.append(["x_ladder", 6, 27])
lb.portal([(6, 27)], "ares_hab", (36, 24), "Наверх, в жилой модуль")
lb.reserve(3, 24, 9, 28)
# криокапсулы экипажа — шесть, две пустые, одна разбита
for i, x in enumerate((4, 8, 12, 16, 20, 24)):
    lb.put([CRYO[0], CRYO[1], CRYO[0], CRYO[2], CRYO[1], CRYO[2]][i], x, 4)
lb.terminal(28, 5, "ares_cryo")
# опыты «Проекта Арес»: чаны с зелёным, консоли
lb.put(VAT, 8, 14)
lb.put(VAT, 14, 14)
for i, x in enumerate((22, 26, 30)):
    lb.put(CONSOLES[i], x, 14)
lb.terminal(34, 16, "ares_project")
lb.put(REACTOR, 32, 24)
lb.put(REACTOR, 36, 24)
# стенд прототипа: винтовка Гаусса — единственная уцелевшая на пустоши. Охрана проекта ещё на посту.
lb.box(LOCKERS[0], 36, 4, "стенд прототипа «Арес»", {"винтовка Гаусса": 1, "ЭМ-патрон": 24})
lb.enemies += [["robot_guard", 30, 8], ["robot_guard", 20, 20], ["turret", 37, 8]]

print("техзал lb:", lb.dress_empty(tech_scenes(city, "ar5"), ground="F", block=7, margin=1, chance=1.0))

LM.lamps(lb, "cold", [(18, 8), (28, 9), (22, 21)])
LM.lamps(lb, "red", [(3, 14), (37, 12)])
LM.decals(lb, "x_vd_hz_h", [(18, 18), (19, 18), (20, 18)])
LM.decals(lb, "x_vd_blood1", [(20, 22), (12, 18)])
LM.decals(lb, "x_vd_sparks", [(30, 10), (14, 21)])
LM.doors(lb)

city.save(gap_exempt=("repconn_ghoul",))
L = json.load(open("data/locations.json", encoding="utf-8"))
L["repconn"].update({"world_name": "Полигон REPCONN"})
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
