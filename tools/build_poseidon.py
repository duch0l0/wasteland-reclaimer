"""
«Посейдон-7» — станция Анклава, замаскированная под ретранслятор Poseidon Energy. Тайная локация третьего акта.
Сценарий — docs/story.md, раздел «„Посейдон-7“ — станция Анклава».

  poseidon7        «Посейдон-7» (64×46): внешний периметр — забор, вышка ретранслятора, купола, радары,
                   посадочная площадка винтокрыла; у ворот — шагоход Анклава.
  poseidon7_base   станция: узел связи (канал «П-7» на Форт Сёрчлайт), казарма, кабинет Холлиса,
                   лаборатория — в клетке паладин Дарнелл, брат Лиры.
  poseidon7_hangar подземный ангар: винтокрыл, стойки силовой брони, склад — сюда свозят контейнеры культа.

Наборы: futuristic-military-base (fmbase), abandoned-military-base (mbase), fire-station (fstation),
nuclear-power-plant (npower), wasteland-laboratory (wlab), nbunk, cult (клетки), desert-natural (скалы).
Запуск из папки game_project:  .venv/bin/python tools/build_poseidon.py
"""
import json

from citykit import City, CityMap

city = City("poseidon", "«Посейдон-7»")


def P(name, img, **kw):
    city.prop(name, img, **kw)
    return name


def cells(page, pts):
    return [f"pk:{page}/{x},{y},1,1" for x, y in pts]


GLOW = lambda c: {"r": 110, "color": c, "at": [0.5, 0.4], "flicker": 0.1}
CLIFFS = [P(f"p7_cliff{i}", f"pk:desnat/p1/{x},14,2,2", foot=[2, 2], sight=True) for i, x in enumerate((8, 10, 12))]
RELAY = P("p7_relay", "pk:fmbase/fmbase_1_012", foot=[2, 2], sight=True, light=GLOW([255, 90, 80]))
COMMAND = P("p7_command", "pk:fmbase/fmbase_1_000", foot=[2, 1], sight=True, light=GLOW([120, 255, 160]))
CONTROL = P("p7_control", "pk:fmbase/fmbase_1_001", foot=[2, 1], sight=True)
SATELLITE = P("p7_satellite", "pk:fmbase/fmbase_1_002", foot=[2, 1], sight=True)
GENERATOR = P("p7_generator", "pk:fmbase/fmbase_1_003", foot=[2, 1], sight=True, light=GLOW([110, 200, 255]))
DOME = P("p7_dome", "pk:fmbase/fmbase_1_007", foot=[2, 1], sight=True, light=GLOW([110, 200, 255]))
TURRET = [P("p7_turret", "pk:fmbase/fmbase_1_008", foot=[2, 1], sight=True), P("p7_turret_b", "pk:fmbase/fmbase_1_013", foot=[2, 1], sight=True)]
PAD = P("p7_pad", "pk:fmbase/fmbase_1_006", block=False, layer="floor")
TANKS = [P("p7_tank_blue", "pk:fmbase/fmbase_1_004", sight=True, light=GLOW([110, 200, 255])),
         P("p7_tank_green", "pk:fmbase/fmbase_1_010", sight=True, light=GLOW([140, 255, 140])),
         P("p7_tank_vre", "pk:fmbase/fmbase_1_011", sight=True, light=GLOW([160, 255, 120]))]
PIPELINE = P("p7_pipeline", "pk:fmbase/fmbase_1_016", foot=[8, 1], sight=True)
SUIT_RACK = [P("p7_suit_rack", "pk:fmbase/fmbase_2_080", foot=[4, 1], sight=True),
             P("p7_suit_rack_b", "pk:fmbase/fmbase_2_084", foot=[4, 1], sight=True)]
SUIT_STAND = P("p7_suit_stand", "pk:fmbase/fmbase_2_085", sight=True)
BAY_DOOR = P("p7_bay_door", "pk:fmbase/fmbase_2_081", foot=[2, 1], sight=True)
VERTIBIRD = P("p7_vertibird", "pk:fmbase/p1/0,8,4,4", foot=[4, 3], sight=True)     # отсек с машиной
BAY_EMPTY = P("p7_bay_empty", "pk:fmbase/p1/8,8,4,4", foot=[4, 3], sight=True)
FENCE = P("p7_fence", "pk:mbase/p2/12,6,4,2", foot=[4, 1])
SANDBAGS = "x_sandbags"
CONSOLES = [P("p7_console", "pk:npower/npower_2_006", foot=[2, 1]), P("p7_console_b", "pk:npower/npower_2_013", foot=[2, 1]),
            P("p7_console_c", "pk:npower/npower_2_036", foot=[2, 1])]
SERVER = P("p7_server", "pk:npower/npower_2_042")
SCREENS = P("p7_screens", "pk:npower/npower_2_079", foot=[2, 1])
BUNKS = [P(f"p7_bunk{i}", f"pk:nbunk/nbunk_2_{n:03d}", foot=[2, 1], sight=True) for i, n in enumerate((0, 1, 2, 3))]
LOCKER = P("p7_locker", "pk:nbunk/nbunk_2_005", search="locker", title="шкафчик")
DESK = P("p7_desk", "pk:nbunk/nbunk_2_016", foot=[2, 1])
CAGE = P("p7_cage", "pk:cult/cult_3_020", block=False)
LAB = [P("p7_chem", "pk:wlab/wlab_1_012", foot=[2, 1]), P("p7_chem_b", "pk:wlab/wlab_1_035", foot=[2, 1])]
TUBE = P("p7_tube", "pk:wlab/wlab_3_101", foot=[2, 1], sight=True, light=GLOW([160, 255, 120]))
VRE_CRATE = P("p7_vre_crate", "pk:wlab/wlab_2_024", foot=[2, 1], sight=True)
AMMO = P("p7_ammo", "pk:mbase/mbase_2_001", foot=[2, 1], search="military", title="ящик Анклава")
SAFE = P("p7_safe", "pk:west/west_2_105", search="military", title="сейф коменданта")

SAND = cells("destown/p2", [(0, 0), (1, 0), (0, 1), (1, 1)])
PLATE = ["pk:fstation/fstation_f2_09"]
PLATE_B = ["pk:fstation/fstation_f2_04"]
PLATE_C = ["pk:fstation/fstation_f2_00"]
TILE = ["pk:fstation/fstation_f1_08"]


# ================================================================ периметр
W, H = 64, 46
pe = CityMap(city, "poseidon7", "«Посейдон-7»", W, H, start=(1, 23), seed=231, music="lab", world_pos=(2820, 900))
pe.floor_code("s", *SAND)
pe.floor_code("m", *PLATE)
pe.paint("s", 0, 0, W - 1, H - 1)
FLOOR = set()
for x0, y0, x1, y1 in ((0, 20, 14, 26), (10, 4, 58, 42)):
    FLOOR |= {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}
pe.paint("m", 14, 6, 56, 40)
pe.exits = [(0, y) for y in range(21, 26)]
pe.reserve(0, 21, 16, 25)
# забор с воротами на запад; у ворот — мешки, турели
pe.hwall([FENCE], 14, 56, 6)
pe.hwall([FENCE], 14, 56, 40)
for y in range(7, 40):
    if y not in range(21, 26):
        pe.maybe(SANDBAGS, 14, y, check=False)
    pe.maybe(SANDBAGS, 56, y, check=False)
pe.put(TURRET[0], 16, 18)
pe.put(TURRET[1], 16, 27)
# вышка ретранслятора Poseidon Energy — то, что видно с дороги
pe.put(RELAY, 30, 8)
pe.put(SATELLITE, 26, 10)
pe.put(SATELLITE, 36, 10)
# купола и генераторы, трубопровод
pe.put(DOME, 44, 9)
pe.put(DOME, 50, 9)
pe.put(GENERATOR, 44, 14)
pe.put(PIPELINE, 40, 34)
# посадочная площадка винтокрыла
pe.put(PAD, 22, 28)
pe.box(AMMO, 20, 33, "ящик у площадки", {"форма Анклава": 1, "патроны": 15})   # сменная форма пилотов
# командный пункт — вход в станцию
pe.put(COMMAND, 32, 18)
pe.put(CONTROL, 36, 18)
pe.portal([(33, 19), (34, 19)], "poseidon7_base", (20, 28), "Станция",
          requires={"flags_any": ["p7_invited", "p7_disguise", "p7_storm_won"],
                    "msg": "Солдат Анклава: «Гражданским вход воспрещён. Комендант примет вас, если пожелает»."})
pe.reserve(32, 19, 35, 22)
pe.npcs += [["enclave_gate", 18, 23], ["enclave_officer", 34, 23]]
pe.enemies += [["enclave_mech", 27, 27]]               # шагоход у ворот — молчит, пока нет тревоги
for _, x, y in pe.npcs:
    pe.reserve(x, y, x, y)
for y in range(0, H, 2):
    for x in range(0, W, 2):
        if not {(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)} & FLOOR:
            pe.props.append([CLIFFS[(x * 5 + y * 3) % 3], x, y])
            pe.blocked.update({(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)})


# ================================================================ станция
W, H = 44, 32
bs = CityMap(city, "poseidon7_base", "«Посейдон-7»: станция", W, H, start=(20, 28), seed=232, interior=True, music="lab")
bs.floor_code("M", *PLATE)
bs.floor_code("N", *PLATE_B)
bs.floor_code("T", *TILE)
bs.wall_code("W", "pk:fmbase/fmbase_w2_08")
bs.wall_code("L", "pk:fmbase/fmbase_w1_18")
bs.room(1, 18, 43, 31, "W", "M")                      # шлюз и коридор
bs.room(1, 1, 15, 18, "W", "N")                       # узел связи
bs.room(15, 1, 29, 18, "W", "T")                      # кабинет Холлиса
bs.room(29, 1, 43, 18, "L", "M")                      # лаборатория
bs.opening(20, 31, 21, 31, "M")
bs.portal([(20, 31), (21, 31)], "poseidon7", (33, 21), "Наружу")
bs.opening(8, 18, 9, 20, "N")
bs.opening(22, 18, 23, 20, "T")
bs.opening(36, 18, 37, 20, "M")
# коридор: шкафчики, стойка брони, лифт в ангар
for x in (3, 5, 7):
    bs.put(LOCKER, x, 22)
bs.put(SUIT_STAND, 12, 22)
bs.put(SUIT_STAND, 30, 22)
bs.props.append(["x_ladder", 40, 28])
bs.portal([(40, 28)], "poseidon7_hangar", (6, 5), "Лифт в ангар")
bs.reserve(38, 27, 42, 30)
bs.npcs += [["enclave_trooper", 26, 25]]
# узел связи: экраны, серверы, терминал канала
bs.put(SCREENS, 3, 4)
bs.put(SCREENS, 6, 4)
bs.put(SERVER, 10, 4)
bs.put(SERVER, 12, 4)
bs.put(CONSOLES[0], 3, 10)
bs.terminal(11, 12, "p7_comm")
bs.npcs += [["enclave_tech", 7, 13]]
# кабинет Холлиса: стол, экран, сейф — и кресло для гостя
bs.put(DESK, 21, 7)
bs.put(CONSOLES[2], 17, 4)
bs.put(SCREENS, 24, 4)
bs.box(SAFE, 27, 4, "сейф коменданта", {"код винтокрыла": 1, "крышки": 200},
       requires={"item": "отмычка", "msg": "Сейф коменданта. Замок армейский, но всего лишь замок."}, owner="hollis_p7")
bs.npcs += [["hollis_p7", 22, 10]]
# лаборатория: колбы с зелёным, столы, клетка с паладином
bs.put(TUBE, 31, 4)
bs.put(TUBE, 34, 4)
bs.put(TANKS[2], 38, 4)
bs.put(LAB[0], 31, 9)
bs.put(LAB[1], 35, 9)
bs.terminal(41, 9, "p7_lab")
bs.put(CAGE, 38, 14)
bs.npcs += [["darnell", 38, 14], ["enclave_scientist", 33, 13]]


# ================================================================ ангар
W, H = 46, 32
hg = CityMap(city, "poseidon7_hangar", "«Посейдон-7»: ангар", W, H, start=(6, 5), seed=233, interior=True, music="vats")
hg.floor_code("M", *PLATE_C)
hg.wall_code("W", "pk:fmbase/fmbase_w2_08")
hg.room(1, 1, 45, 31, "W", "M")
hg.props.append(["x_ladder", 6, 4])
hg.portal([(6, 4)], "poseidon7_base", (40, 27), "Лифт наверх")
hg.reserve(4, 4, 9, 8)
# винтокрыл на площадке посередине, ворота ангара на восток
hg.put(VERTIBIRD, 18, 11)
hg.put(BAY_EMPTY, 26, 11)                                # второй отсек пуст — винтокрыл на задании
hg.put(BAY_DOOR, 42, 14)
hg.terminal(36, 20, "p7_vertibird")
# стойки силовой брони вдоль северной стены
hg.put(SUIT_RACK[0], 14, 4)
hg.put(SUIT_RACK[1], 26, 4)
hg.box(SUIT_STAND, 36, 4, "стойка силовой брони", {"улучшенная силовая броня": 1, "шлем Анклава": 1,
                                                    "голозапись «Курс оператора СБ»": 1},
       requires={"item": "код винтокрыла", "msg": "Стойка заблокирована. Нужен код доступа офицера."})
# склад: контейнеры культа, перехваченные Анклавом
for x, y in ((4, 22), (8, 22), (12, 22), (4, 26), (8, 26)):
    hg.put(VRE_CRATE, x, y)
hg.box(AMMO, 16, 27, "ящик Анклава", {"патроны": 30, "граната": 2, "стимулятор": 1})
hg.enemies += [["enclave_soldier", 24, 24], ["enclave_soldier", 32, 10], ["enclave_soldier", 38, 26]]

city.save(gap_exempt=("enclave_gate", "enclave_officer"))
L = json.load(open("data/locations.json", encoding="utf-8"))
L["poseidon7"].update({"world_name": "Ретранслятор Poseidon", "discover": True})
L["poseidon7"]["clear_flag"] = "p7_storm_won"
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
