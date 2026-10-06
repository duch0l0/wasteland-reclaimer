"""
База Марипоза — финал игры. Чаны Создателя, первые супермутанты, брат Т.
Сценарий — docs/story.md, раздел «База Марипоза — финал».

  mariposa          «База Марипоза» (68×48): военная база в скалах — колючая проволока, вышки, разбитые ангары;
                    шатры «Детей Единства», фургоны с людьми; супермутанты охраняют спуск вниз.
  mariposa_lab      «Марипоза: лаборатория»: клетки для «сосудов» (сюда попадают те, кого не успели спасти —
                    Тоби, Иезекииль, люди Ниптона), операционная, «часовня» брата Т.
  mariposa_vats     «Марипоза: чаны»: зал чанов с ВРЭ — сердце армии Создателя; командный бункер 2077 года
                    с пультом базы — здесь решается судьба ВРЭ и включается эпилог.

Наборы: abandoned-military-base (mbase), wasteland-laboratory (wlab), nuclear-power-plant (npower), cult-temple
(cult), futuristic-military-base (fmbase), nbunk, desert-natural (скалы), bazaar (шатры), zcity (фургоны).
Запуск из папки game_project:  .venv/bin/python tools/build_mariposa.py
"""
import json

from citykit import City, CityMap

city = City("mariposa", "База Марипоза")


def P(name, img, **kw):
    city.prop(name, img, **kw)
    return name


def cells(page, pts):
    return [f"pk:{page}/{x},{y},1,1" for x, y in pts]


GREEN = {"r": 130, "color": [140, 255, 140], "at": [0.5, 0.4], "flicker": 0.2}
CLIFFS = [P(f"mp_cliff{i}", f"pk:desnat/p1/{x},14,2,2", foot=[2, 2], sight=True) for i, x in enumerate((8, 10, 12))]
WATCHTOWER = P("mp_watchtower", "pk:mbase/mbase_2_005", foot=[2, 1], sight=True,
               light={"r": 160, "color": [255, 250, 210], "at": [0.5, 0.1]})
BARRACKS = P("mp_barracks", "pk:mbase/mbase_2_006", foot=[2, 2], sight=True)
BUNKER = P("mp_bunker", "pk:mbase/mbase_2_004", foot=[4, 3], sight=True)
HANGAR = P("mp_hangar", "pk:mbase/mbase_2_015", foot=[6, 3], sight=True)
TANK = P("mp_tank", "pk:mbase/mbase_2_002", foot=[4, 1], sight=True)
BARBED = P("mp_barbed", "pk:mbase/p1/8,2,2,2", foot=[2, 1])
AMMO = P("mp_ammo", "pk:mbase/mbase_2_001", foot=[2, 1], search="military", title="армейский ящик")
DEBRIS = [P("mp_helmet", "pk:mbase/p1/6,8,1,1", block=False), P("mp_gasmask", "pk:mbase/p1/7,9,1,1", block=False)]
TENT_WHITE = P("mp_tent_white", "pk:bazaar/bazaar_1_004", foot=[2, 2], sight=True)
VAN = P("mp_cult_van", "pk:zcity/zcity_2_098", foot=[2, 1], sight=True)
ALTAR = P("mp_altar", "pk:cult/cult_2_045", foot=[2, 1], sight=True)
CANDELABRA = P("mp_candelabra", "pk:cult/cult_2_068", block=False,
               light={"r": 90, "color": [255, 170, 80], "at": [0.5, 0.3], "flicker": 0.5})
BANNERS = [P("mp_banner", "pk:cult/cult_2_141", block=False), P("mp_banner_b", "pk:cult/cult_2_142", block=False)]
PILLAR = P("mp_pillar", "pk:cult/cult_2_143", sight=True)
CAGE = P("mp_cage", "pk:cult/cult_3_020", sight=True)
CAGE_HELD = P("mp_cage_held", "pk:cult/cult_3_020", block=False)
VAT = P("mp_vat", "pk:wlab/wlab_1_000", sight=True, light=GREEN)
VATS = P("mp_vats", "pk:wlab/wlab_1_002", foot=[2, 1], sight=True, light=GREEN)
TUBES = [P("mp_tube", "pk:wlab/wlab_3_101", foot=[2, 1], sight=True, light=GREEN),
         P("mp_tube_b", "pk:wlab/wlab_3_102", foot=[2, 1], sight=True, light=GREEN),
         P("mp_tube_broken", "pk:wlab/wlab_3_103", foot=[2, 1], sight=True)]
BIG_VAT = P("mp_big_vat", "pk:npower/npower_1_007", foot=[4, 3], sight=True,
            light={"r": 180, "color": [140, 255, 140], "at": [0.5, 0.4], "flicker": 0.25})
PIPES = P("mp_pipes", "pk:npower/npower_1_029", foot=[2, 1])
PUDDLE = P("mp_vre_puddle", "pk:gcave/p1/2,4,1,1", block=False, light={"r": 70, "color": [140, 255, 140], "at": [0.5, 0.5], "flicker": 0.3})
CONSOLES = [P("mp_console", "pk:npower/npower_2_036", foot=[2, 1]), P("mp_console_b", "pk:npower/npower_2_006", foot=[2, 1])]
SERVER = P("mp_server", "pk:npower/npower_2_042")
ARM = P("mp_arm", "pk:wlab/wlab_1_029", foot=[2, 1])
CHEM = P("mp_chem", "pk:wlab/wlab_1_012", foot=[2, 1])
OP_TABLE = P("mp_op_table", "pk:hosp/hosp_1_001", foot=[4, 2])
BIOHAZ = P("mp_biohazard", "pk:hosp/hosp_1_012")
BONES = [P("mp_bones", "pk:grave/grave_2_022", block=False), P("mp_bones_b", "pk:grave/grave_2_027", block=False)]
VRE_CRATE = P("mp_vre_crate", "pk:wlab/wlab_2_024", foot=[2, 1], sight=True)

SAND = cells("destown/p2", [(0, 0), (1, 0), (0, 1), (1, 1)])
GRAVEL = cells("mbase/p1", [(8, 8), (9, 9), (10, 10), (9, 8), (8, 10), (10, 9)])
PLATE = ["pk:fstation/fstation_f2_09"]
TILE = ["pk:store/p1/12,0,1,1"]
GRATE = cells("nbunk/p2", [(0, 12), (1, 13), (2, 14), (3, 12)])
SLIME = cells("gcave/p1", [(1, 4), (1, 5), (2, 6), (3, 6)])


# ================================================================ двор базы
W, H = 68, 48
mp = CityMap(city, "mariposa", "База Марипоза", W, H, start=(1, 24), seed=241, music="vats", world_pos=(1180, 760),
             night=[60, 70, 90])
mp.floor_code("s", *SAND)
mp.floor_code("g", *GRAVEL)
mp.paint("s", 0, 0, W - 1, H - 1)
FLOOR = set()
for x0, y0, x1, y1 in ((0, 21, 14, 27), (10, 4, 62, 44)):
    FLOOR |= {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}
mp.paint("g", 12, 6, 60, 42)
mp.exits = [(0, y) for y in range(22, 27)]
mp.reserve(0, 22, 16, 26)
mp.hwall([BARBED], 12, 60, 5)
mp.hwall([BARBED], 12, 60, 43)
for y in range(6, 43):
    if y not in range(21, 28):
        mp.maybe(BARBED, 12, y, check=False)
for x, y in ((14, 8), (58, 8), (14, 40), (58, 40)):
    mp.put(WATCHTOWER, x, y)
# север: разбитые ангары и казармы 2077 года, танк
mp.put(HANGAR, 18, 8)
mp.put(BARRACKS, 28, 9)
mp.put(BARRACKS, 32, 9)
mp.put(TANK, 40, 10)
mp.box(AMMO, 46, 10, "армейский ящик 2077 года", {"патроны": 20, "граната": 2, "стимулятор": 1,
                                                 "силовая броня T-51b": 1})
# центр: лагерь культа — шатры, алтарь, фургоны с «сосудами»
for x, y in ((22, 20), (28, 18), (34, 20), (22, 30), (34, 30)):
    mp.put(TENT_WHITE, x, y)
mp.put(ALTAR, 28, 25)
mp.put(CANDELABRA, 26, 25)
mp.put(CANDELABRA, 31, 25)
mp.put(VAN, 42, 22)
mp.put(VAN, 42, 27)
# восток: бункер — спуск к лаборатории и чанам; супермутанты на часах
mp.put(BUNKER, 50, 20)
mp.portal([(51, 23), (52, 23)], "mariposa_lab", (20, 5), "Спуск в лабораторию")
mp.reserve(50, 23, 54, 26)
for i, (x, y) in enumerate(((18, 36), (30, 38), (44, 36), (52, 32))):
    mp.maybe(DEBRIS[i % 2], x, y)
mp.npcs += [["cult_herald", 28, 27], ["mp_acolyte", 24, 24], ["mp_acolyte_b", 33, 23]]
mp.enemies += [["super_mutant", 48, 28], ["super_mutant", 55, 24], ["super_mutant", 46, 16], ["cult_guard", 40, 32]]
for y in range(0, H, 2):
    for x in range(0, W, 2):
        if not {(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)} & FLOOR:
            mp.props.append([CLIFFS[(x * 7 + y * 3) % 3], x, y])
            mp.blocked.update({(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)})


# ================================================================ лаборатория
W, H = 44, 32
lb = CityMap(city, "mariposa_lab", "Марипоза: лаборатория", W, H, start=(20, 5), seed=242, interior=True, music="vats",
             night=[60, 66, 80])
lb.floor_code("T", *TILE)
lb.floor_code("G", *GRATE)
lb.wall_code("W", "pk:fstation/fstation_w1_10")
lb.wall_code("C", "pk:cult/cult_w1_22")
lb.room(1, 1, 43, 12, "W", "T")                       # коридор 2077 года
lb.room(1, 12, 22, 31, "W", "G")                      # клетки «сосудов»
lb.room(22, 12, 43, 31, "C", "T")                     # «часовня» брата Т. и операционная
lb.props.append(["x_ladder", 20, 4])
lb.portal([(20, 4)], "mariposa", (51, 25), "Наверх, во двор")
lb.reserve(18, 4, 23, 7)
lb.opening(10, 12, 11, 14, "G")
lb.opening(32, 12, 33, 14, "T")
lb.props.append(["x_ladder", 40, 9])
lb.portal([(40, 9)], "mariposa_vats", (6, 5), "Вниз, к чанам")
lb.reserve(38, 8, 42, 10)
for x in (4, 8, 26, 30):
    lb.put(CONSOLES[x % 2], x, 4)
lb.put(BIOHAZ, 35, 4)
# клетки: в каждой — «сосуд»; кого не успели спасти, тот здесь
for i, (x, y) in enumerate(((3, 16), (7, 16), (11, 16), (15, 16), (3, 24), (7, 24), (11, 24), (15, 24))):
    lb.put(CAGE_HELD if i in (0, 2, 5) else CAGE, x, y)
lb.npcs += [["tobi_mp", 3, 16], ["ezekiel_mp", 11, 16], ["nipton_bride_mp", 7, 24]]
lb.put(BONES[0], 18, 28)
# часовня брата Т.: колонны, знамёна, алтарь; операционная — стол, манипулятор
for y in (17, 23):
    lb.put(PILLAR, 25, y)
    lb.put(PILLAR, 40, y)
lb.put(BANNERS[0], 28, 15)
lb.put(BANNERS[1], 37, 15)
lb.put(ALTAR, 31, 18)
lb.put(CANDELABRA, 29, 19)
lb.put(CANDELABRA, 35, 19)
lb.put(OP_TABLE, 28, 26)
lb.put(ARM, 34, 26)
lb.put(CHEM, 37, 28)
lb.terminal(41, 27, "mariposa_lab_log")
lb.npcs += [["brother_t_mp", 32, 21]]
lb.enemies += [["super_mutant", 14, 29]]


# ================================================================ чаны и командный бункер
W, H = 48, 34
vt = CityMap(city, "mariposa_vats", "Марипоза: чаны", W, H, start=(6, 5), seed=243, interior=True, music="vats",
             night=[40, 56, 48])                          # полумрак — светятся только чаны
vt.floor_code("M", *PLATE)
vt.floor_code("S", *GRATE)
vt.wall_code("W", "pk:fstation/fstation_w1_08")
vt.room(1, 1, 33, 33, "W", "S")                       # зал чанов
vt.room(33, 1, 47, 20, "W", "M")                      # командный бункер 2077 года
vt.room(33, 20, 47, 33, "W", "M")                     # склад контейнеров
vt.props.append(["x_ladder", 6, 4])
vt.portal([(6, 4)], "mariposa_lab", (40, 10), "Наверх, в лабораторию")
vt.reserve(4, 4, 9, 7)
vt.opening(33, 10, 33, 11, "M")
vt.opening(39, 20, 40, 20, "M")
# чаны рядами — зелёное свечение на весь зал; трубы между ними
vt.put(BIG_VAT, 13, 12)
for i, (x, y) in enumerate(((5, 12), (5, 18), (21, 12), (21, 18), (5, 26), (13, 26), (21, 26))):
    vt.put([VAT, VATS, TUBES[0], TUBES[1], VAT, VATS, TUBES[2]][i], x, y)
for x in (10, 18, 26):
    vt.put(PIPES, x, 22)
for x, y in ((9, 9), (17, 17), (25, 15), (11, 30), (24, 31), (29, 24)):
    vt.maybe(PUDDLE, x, y)                             # пролитое ВРЭ светится на решётке
vt.put(BIOHAZ, 29, 4)
vt.enemies += [["super_mutant", 16, 20], ["super_mutant", 26, 8], ["super_mutant", 28, 28], ["joined", 10, 30]]
# командный бункер: пульт базы, серверы — отсюда управляли Марипозой в 2077-м
for x in (35, 37, 39):
    vt.put(SERVER, x, 4)
vt.put(CONSOLES[0], 42, 5)
vt.terminal(40, 12, "mariposa_core")
vt.terminal(36, 16, "mariposa_1977")
# склад: контейнеры, которые культ свёз отовсюду
for x, y in ((35, 24), (39, 24), (43, 24), (35, 29), (39, 29)):
    vt.put(VRE_CRATE, x, y)

city.save(gap_exempt=("tobi_mp", "ezekiel_mp", "nipton_bride_mp", "brother_t_mp"))
L = json.load(open("data/locations.json", encoding="utf-8"))
L["mariposa"].update({"world_name": "База Марипоза", "discover": True})
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
