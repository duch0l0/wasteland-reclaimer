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

from citykit import City, CityMap

city = City("ares", "«Арес»")


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
BARBED = P("ar2_barbed", "pk:mbase/p1/8,2,2,2", foot=[2, 1])
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
ROCKS = [P("ar2_rock", "pk:pmars/p1/1,1,1,1", block=False), P("ar2_rock_b", "pk:pmars/p1/2,2,1,1", block=False),
         P("ar2_boulder", "pk:pmars/p1/0,2,1,1")]
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

SAND = cells("destown/p2", [(0, 0), (1, 0), (0, 1), (1, 1)])
CONCRETE = cells("mbase/p1", [(8, 8), (9, 9), (10, 10), (9, 8)])
MARS = cells("pmars/p1", [(0, 0), (1, 0), (0, 1), (0, 4), (1, 4)])
MARS_PAD = ["pk:fstation/fstation_f2_09"]
FLOOR = ["pk:fstation/fstation_f2_04"]
FLOOR_B = ["pk:store/p1/12,0,1,1"]
GRATE = cells("nbunk/p2", [(0, 12), (1, 13), (2, 14), (3, 12)])


# ================================================================ полигон REPCONN
W, H = 56, 40
rp = CityMap(city, "repconn", "Полигон REPCONN", W, H, start=(1, 20), seed=271, music="desert", world_pos=(2680, 640))
rp.floor_code("s", *SAND)
rp.floor_code("c", *CONCRETE)
rp.paint("s", 0, 0, W - 1, H - 1)
rp.paint("c", 10, 4, 52, 36)
rp.exits = [(0, y) for y in range(18, 23)]
rp.reserve(0, 18, 12, 22)
rp.hwall([BARBED], 10, 52, 3)
rp.hwall([BARBED], 10, 52, 37)
for x, y in ((11, 5), (50, 5), (11, 34), (50, 34)):
    rp.put(WATCHTOWER, x, y)
rp.put(HANGAR, 14, 6)
rp.put(HANGAR, 14, 26)
rp.put(BUNKER, 24, 16)
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
rp.enemies += [["feral", 20, 30], ["ghoul_runner", 28, 10], ["feral", 46, 24]]
rp.npcs += [["repconn_ghoul", 30, 22]]


# ================================================================ Марс: поверхность
W, H = 66, 46
mr = CityMap(city, "ares", "«Арес»: поверхность Марса", W, H, start=(32, 40), seed=272, music="lab",
             night=[150, 96, 80])                              # красное небо, тусклое солнце
mr.tint = [255, 214, 190]
mr.floor_code("m", *MARS)
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
for i, (x, y) in enumerate(((4, 38), (54, 40), (60, 22), (2, 12), (22, 42))):
    mr.stamp(f"ar2_crater{i}", CRATER if i % 2 else CRATER_BIG, x, y, water=False)
mr.npcs += [["rover_bot", 24, 30]]
mr.scatter(ROCKS, 1, 1, W - 2, H - 2, 40)
for x, y in ((24, 20), (40, 20), (12, 36), (50, 12), (60, 30), (6, 26)):   # ещё купола и модули — станция большая
    mr.maybe([DOMES[0], MODULES[3], MODULES[4], GREENHOUSES[1], MODULES[5], MODULES[6]][(x + y) % 6], x, y)


# ================================================================ жилой модуль
W, H = 40, 30
hb = CityMap(city, "ares_hab", "«Арес»: жилой модуль", W, H, start=(16, 26), seed=273, interior=True, music="lab")
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


# ================================================================ лаборатория
W, H = 40, 30
lb = CityMap(city, "ares_lab", "«Арес»: лаборатория", W, H, start=(6, 26), seed=274, interior=True, music="vats",
             night=[60, 70, 96])
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

city.save(gap_exempt=("repconn_ghoul",))
L = json.load(open("data/locations.json", encoding="utf-8"))
L["repconn"].update({"world_name": "Полигон REPCONN"})
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
