"""
Сёрчлайт и Форт Сёрчлайт — шахтёрский посёлок и довоенная военная база, где роботы сорок четыре года
проводят учения. Третий акт. Сценарий — docs/story.md, раздел «Сёрчлайт и Форт Сёрчлайт — „Генерал“».

  searchlight            «Сёрчлайт» (64×46): посёлок шахтёров — пожарная часть (дом брандмейстера Хоуп и
                         штаб посёлка), церковь, дома, лавка, копёр над шахтой; на востоке — лагерь
                         паладинов Братства; дорога на восток — к Форту.
  searchlight_firehouse  пожарная часть: гараж с ржавыми машинами, стойки с касками, штаб посёлка.
  searchlight_mine       угольная шахта: рельсы, вагонетки, крепь; в глубине — старый вентиляционный штрек,
                         который выходит прямо под базу.
  fort_searchlight       «Форт Сёрчлайт» (70×50): колючая проволока, вышки, мешки с песком, танк и хаммеры,
                         ангар; плац, где маршируют «новобранцы» под командой робота-сержанта; вход в бункер.
  fort_bunker            бункер базы: казарма новобранцев, оружейная, узел связи (канал «Посейдона-7»),
                         ядро ИИ «Генерал» под охраной турелей.

Наборы: abandoned-military-base (mbase), modern-fire-station (fstation), abandoned-coal-mine (cmine),
abandoned-rural-village (rvill), nuclear-bunker (nbunk), cult-temple (cult), grave, ucamp, west, zcity.
Запуск из папки game_project:  .venv/bin/python tools/build_searchlight.py
"""
import json

from citykit import City, CityMap

city = City("searchlight", "Сёрчлайт")


def P(name, img, **kw):
    city.prop(name, img, **kw)
    return name


def cells(page, pts):
    return [f"pk:{page}/{x},{y},1,1" for x, y in pts]


S = 1.5
# ------------------------------------------------------------ посёлок
HOUSES = [P(f"sl_house{i}", f"pk:rvill/rvill_1_{n:03d}", scale=S, foot=[3, 2], sight=True)
          for i, n in enumerate((0, 24, 26, 4, 41, 27))]
CHAPEL = P("sl_chapel", "pk:grave/grave_1_004", scale=1.2, foot=[2, 2], sight=True)
WELL = P("sl_well", "pk:rvill/rvill_1_060", foot=[2, 1])
TREES = [P(f"sl_tree{i}", f"pk:rvill/rvill_2_{n:03d}", scale=S, foot=[2, 1]) for i, n in enumerate((10, 11, 12))]
GRASS = [P(f"sl_grass{i}", f"pk:rvill/rvill_2_{n:03d}", block=False) for i, n in enumerate((14, 15, 16, 17))]
FENCE = [P("sl_fence", "pk:west/west_1_013", foot=[2, 1]), P("sl_fence_b", "pk:west/west_1_014")]
CRATE = P("sl_crate", "pk:cmine/cmine_1_048", search="crate", title="ящик")
CRATE_B = P("sl_crate_b", "pk:cmine/cmine_1_058", search="crate", title="ящик")
BARRELS = [P(f"sl_barrel{i}", f"pk:cmine/cmine_1_{n:03d}", search="junk", title="бочка") for i, n in enumerate((72, 76))]
COAL = [P("sl_coal", "pk:cmine/cmine_1_029", foot=[2, 1]), P("sl_coal_b", "pk:cmine/cmine_1_023")]
CART = [P("sl_cart", "pk:cmine/cmine_1_001", foot=[2, 1], sight=True), P("sl_cart_b", "pk:cmine/cmine_1_002", foot=[2, 1], sight=True)]
HEADFRAME = P("sl_headframe", "pk:cmine/cmine_1_018", foot=[2, 1], sight=True)       # копёр над стволом
SUPPORTS = [P(f"sl_support{i}", f"pk:cmine/cmine_1_{n:03d}", foot=[2, 1], sight=True) for i, n in enumerate((15, 16, 19))]
LANTERNS = [P("sl_lantern", "pk:cmine/cmine_1_032", light={"r": 100, "color": [255, 190, 110], "at": [0.5, 0.5], "flicker": 0.3}),
            P("sl_lantern_b", "pk:cmine/cmine_1_034", light={"r": 100, "color": [255, 190, 110], "at": [0.5, 0.5], "flicker": 0.3})]
RAILS = P("sl_rails", "pk:cmine/cmine_1_006", block=False, layer="floor")
RAILS_S = P("sl_rails_s", "pk:cmine/cmine_1_009", block=False, layer="floor")
LOCO = P("sl_loco", "pk:cmine/cmine_1_005", foot=[8, 1], sight=True)
FAN = P("sl_fan", "pk:cmine/cmine_1_079")
ROCKS = [P("sl_rock", "pk:cmine/cmine_1_088"), P("sl_rock_b", "pk:cmine/cmine_1_124")]
DANGER = P("sl_danger", "pk:cmine/cmine_1_119")
CAMPFIRE = P("sl_campfire", "pk:ucamp/ucamp_2_040", foot=[2, 1],
             light={"r": 120, "color": [255, 150, 70], "at": [0.5, 0.5], "flicker": 0.35})
TENT_BOS = P("sl_tent_bos", "pk:bazaar/bazaar_1_014", foot=[2, 2], sight=True)
STALL = P("sl_stall", "pk:jtown/jtown_1_009", foot=[2, 1])
# пожарная часть
FIRETRUCK = [P("sl_firetruck", "pk:fstation/fstation_1_000", foot=[4, 1], sight=True),
             P("sl_firetruck_b", "pk:fstation/fstation_1_005", foot=[4, 1], sight=True),
             P("sl_tanker", "pk:fstation/fstation_1_001", foot=[4, 1], sight=True)]
HELMETS = [P("sl_helmets", "pk:fstation/fstation_1_083", foot=[2, 1], sight=True, search="locker", title="стойка со снаряжением"),
           P("sl_helmets_b", "pk:fstation/fstation_1_085", foot=[2, 1], sight=True)]
HOSE = P("sl_hose", "pk:fstation/fstation_1_053")
OXYGEN = P("sl_oxygen", "pk:fstation/fstation_1_048", foot=[2, 1])
EXTING = P("sl_extinguisher", "pk:fstation/fstation_1_047")
LADDER = P("sl_ladder", "pk:fstation/fstation_1_051")
MEDKIT = P("sl_medkit", "pk:fstation/fstation_1_061", search="drawer", title="аптечка")
TABLE = P("sl_table", "pk:west/west_2_000", foot=[2, 1])
CHAIR = P("sl_chair", "pk:west/west_2_001")
BOOKS = P("sl_bookcase", "pk:west/west_2_116", sight=True, search="shelf", title="шкаф с бумагами")
BED = P("sl_bed", "pk:west/west_2_005", foot=[2, 2])
# база
BUNKER = P("sl_bunker", "pk:mbase/mbase_2_004", foot=[4, 3], sight=True)
WATCHTOWER = P("sl_watchtower", "pk:mbase/mbase_2_005", foot=[2, 1], sight=True)
BARRACKS = P("sl_barracks", "pk:mbase/mbase_2_006", foot=[2, 2], sight=True)
HANGAR = P("sl_hangar", "pk:mbase/mbase_2_015", foot=[6, 3], sight=True)
MISSILE = P("sl_missile", "pk:mbase/mbase_2_017", foot=[2, 2], sight=True)
TANK = P("sl_tank", "pk:mbase/mbase_2_002", foot=[4, 1], sight=True)
HUMVEE = [P("sl_humvee", "pk:mbase/mbase_2_003", foot=[2, 1], sight=True), P("sl_humvee_b", "pk:mbase/mbase_2_007", foot=[3, 1], sight=True)]
AMMO = [P("sl_ammo", "pk:mbase/mbase_2_001", foot=[2, 1], search="military", title="армейский ящик"),
        P("sl_ammo_b", "pk:mbase/mbase_2_009", foot=[2, 1], search="military", title="ящик с патронами")]
BARBED = P("sl_barbed", "pk:mbase/p1/8,2,2,2", foot=[2, 1])
CANNON = P("sl_cannon", "pk:mbase/mbase_3_041", foot=[4, 1], sight=True)
RADAR = P("sl_radar", "pk:mbase/mbase_3_008")
SANDBAGS = "x_sandbags"
# бункер
BUNKS = [P(f"sl_bunk{i}", f"pk:nbunk/nbunk_2_{n:03d}", foot=[2, 1], sight=True) for i, n in enumerate((0, 1, 2, 3))]
LOCKER = P("sl_locker", "pk:nbunk/nbunk_2_005", search="locker", title="шкафчик")
DESK_PC = [P("sl_desk_pc", "pk:nbunk/nbunk_2_016", foot=[2, 1]), P("sl_desk_pc_b", "pk:nbunk/nbunk_2_017", foot=[2, 1])]
GEN = P("sl_gen", "pk:nbunk/nbunk_2_028", foot=[2, 2], sight=True)
CONSOLE = P("sl_console", "pk:mbase/mbase_3_010")
SERVER = P("sl_server", "pk:mbase/mbase_3_016")
MACHINE = [P("sl_machine", "pk:mbase/mbase_3_022"), P("sl_machine_b", "pk:mbase/mbase_3_024")]
GUN_RACK = P("sl_gun_rack", "pk:gcave/p1/14,8,2,2", foot=[2, 1], search="military", title="оружейная стойка")

SAND = cells("destown/p2", [(0, 0), (1, 0), (0, 1), (1, 1)])
DIRT = cells("rvill/p2", [(0, 11), (1, 11), (0, 12), (1, 12)])
ROAD = cells("west/p1", [(0, 1), (1, 1), (0, 2), (1, 2)])
ASPHALT = ["pk:zcity/zcity_f3_09"]
GARAGE = ["pk:fstation/fstation_f1_08"]
WOOD = ["pk:fstation/fstation_f2_22"]
METAL = ["pk:fstation/fstation_f2_09"]
METAL_B = ["pk:fstation/fstation_f2_04"]
WALK = ["pk:zcity/zcity_f1_22"]
GROUND = cells("mbase/p1", [(8, 8), (9, 9), (10, 10), (9, 8), (8, 10), (10, 9)])   # гравий плаца с выбоинами
DEBRIS = [P("sl_helmet", "pk:mbase/p1/6,8,1,1", block=False), P("sl_gasmask", "pk:mbase/p1/7,9,1,1", block=False),
          P("sl_shells", "pk:mbase/mbase_3_047", block=False), P("sl_radio", "pk:mbase/p1/13,8,2,1", block=False)]
CAVE = cells("gcave/p1", [(1, 4), (1, 5), (2, 6), (3, 6)])


# ================================================================ посёлок
W, H = 64, 46
sl = CityMap(city, "searchlight", "Сёрчлайт", W, H, start=(1, 22), seed=211, music="desert", world_pos=(2430, 870))
sl.floor_code("s", *SAND)
sl.floor_code("d", *DIRT)
sl.floor_code("r", *ROAD)
sl.paint("s", 0, 0, W - 1, H - 1)
sl.paint("d", 4, 4, 58, 42)
sl.paint("r", 0, 21, W - 1, 24)                         # улица посёлка и дорога на Форт
sl.paint("r", 28, 6, 31, 21)                            # к копру
sl.exits = [(0, y) for y in range(21, 25)]
sl.reserve(0, 21, W - 1, 24)
sl.reserve(28, 6, 31, 20)

# север: копёр над стволом шахты, вагонетки, кучи угля, узкоколейка
sl.put(HEADFRAME, 29, 3, check=False, allow_reserved=True)
sl.props.append(["x_puddle", 30, 5])
sl.portal([(29, 5), (30, 5)], "searchlight_mine", (6, 30), "Шахта")
sl.put(RAILS, 32, 10)
sl.put(CART[0], 33, 9)
sl.put(CART[1], 37, 9)
sl.put(COAL[0], 22, 8)
sl.put(COAL[0], 24, 11)
sl.put(COAL[1], 26, 14)
sl.put(DANGER, 27, 5)
sl.put(LANTERNS[0], 27, 7)
sl.put(LANTERNS[1], 32, 7)
# северо-запад: пожарная часть — штаб посёлка
sl.building(6, 7, 14, 11, "brick", south=(6,))
sl.reserve(12, 18, 13, 20)
sl.put(HOSE, 6, 19)
sl.put(EXTING, 19, 19)
# северо-восток: церковь и кладбище шахтёров
sl.put(CHAPEL, 44, 8)
for x in range(48, 58, 2):
    sl.maybe("x_cross", x, 10)
    sl.maybe("x_grave", x, 13)
sl.put(TREES[1], 41, 13)
# юг: дома шахтёров, лавка, колодец
for i, (x, y) in enumerate(((6, 28), (12, 28), (18, 28), (6, 35), (18, 35), (40, 30))):
    sl.put(HOUSES[i], x, y)
sl.put(WELL, 26, 30)
sl.put(STALL, 32, 27)
sl.box(CRATE, 35, 27, "ящик лавки", {"консервы": 1}, owner="sl_trader")
sl.put(BARRELS[0], 24, 37)
sl.hwall(FENCE, 4, 22, 42)
# восток: лагерь паладинов Братства — шатёр, костёр, ящики
sl.put(TENT_BOS, 50, 28)
sl.put(CAMPFIRE, 50, 33)
sl.put(AMMO[0], 55, 30)
sl.put(SANDBAGS, 47, 27)
sl.put(SANDBAGS, 47, 29)
sl.npcs += [["fire_chief_hope", 14, 20], ["marta_kane", 22, 32], ["foreman_gus", 34, 13], ["father_clement", 44, 14],
            ["sl_trader", 33, 26], ["sl_kid", 27, 28], ["sl_miner", 25, 9], ["paladin_ross", 52, 32], ["bos_knight", 55, 27]]
for _, x, y in sl.npcs:
    sl.reserve(x, y, x, y)
sl.grow(1, 1, W - 2, H - 2, 6, names=TREES)
sl.scatter(GRASS + ["r_rocks", "r_dry_bush"] + ROCKS, 1, 1, W - 2, H - 2, 26)


# ================================================================ пожарная часть
fh = CityMap(city, "searchlight_firehouse", "Пожарная часть", 34, 22, start=(16, 20), seed=212, interior=True, music="desert")
fh.floor_code("G", *GARAGE)
fh.floor_code("W", *WOOD)
fh.wall_code("B", "pk:fstation/fstation_w1_14")
fh.room(1, 1, 22, 21, "B", "G")                       # гараж
fh.room(22, 1, 33, 21, "B", "W")                      # штаб посёлка
fh.opening(16, 21, 17, 21, "G")
sl.portal([(12, 17), (13, 17)], "searchlight_firehouse", (16, 19), "Пожарная часть")
fh.portal([(16, 21), (17, 21)], "searchlight", (12, 19), "На улицу")
fh.opening(22, 12, 22, 13, "W")
# гараж: две машины носом к воротам, стойки со снаряжением вдоль стены, баллоны, лестница
fh.put(FIRETRUCK[0], 3, 6)
fh.put(FIRETRUCK[2], 3, 11)
fh.put(FIRETRUCK[1], 13, 6)
fh.put(HELMETS[0], 3, 16)
fh.put(HELMETS[1], 6, 16)
fh.put(OXYGEN, 10, 17)
fh.put(LADDER, 20, 4)
fh.put(HOSE, 18, 17)
fh.put(EXTING, 21, 9)
fh.box(MEDKIT, 13, 17, "аптечка", {"бинт": 2, "стимулятор": 1}, owner="fire_chief_hope")
# штаб: стол совета, шкаф, карта — и кровать брандмейстера
fh.put(TABLE, 26, 8)
fh.put(TABLE, 28, 8)
fh.put(CHAIR, 25, 10)
fh.put(CHAIR, 30, 10)
fh.put(BOOKS, 24, 4)
fh.terminal(30, 4, "searchlight_log")
fh.put(BED, 29, 16)
fh.npcs += [["sl_firefighter", 8, 14]]


# ================================================================ шахта
W, H = 50, 36
mn = CityMap(city, "searchlight_mine", "Шахта Сёрчлайта", W, H, start=(6, 30), seed=213, interior=True, music="caves")
mn.floor_code("c", *CAVE)
mn.paint("x", 0, 0, W - 1, H - 1)
mn.paint("c", 3, 26, 14, 33)                           # околоствольный двор
mn.paint("c", 7, 10, 11, 26)                           # главный штрек на север
mn.paint("c", 4, 4, 34, 10)                            # откаточный штрек
mn.paint("c", 14, 14, 30, 22)                          # выработка
mn.paint("c", 11, 17, 14, 19)                          # просечка к выработке
mn.paint("c", 30, 4, 46, 9)                            # старый вентиляционный штрек — к базе
mn.portal([(6, 33), (7, 33)], "searchlight", (29, 6), "Наверх")
mn.reserve(4, 29, 9, 33)
mn.put(RAILS, 5, 6)
mn.put(RAILS, 18, 6)
mn.put(CART[0], 9, 5)
mn.put(CART[1], 24, 5)
mn.put(LOCO, 4, 28)
for x, y in ((7, 12), (9, 18), (7, 23), (16, 15), (26, 19)):
    mn.maybe(SUPPORTS[(x + y) % 3], x, y)                 # крепь — где влезает в штрек
for x, y in ((12, 8), (28, 8), (20, 20), (12, 31)):
    mn.put(LANTERNS[(x + y) % 2], x, y)
mn.put(COAL[0], 22, 16)
mn.put(COAL[1], 28, 16)
mn.box(CRATE_B, 27, 21, "ящик с инструментом", {"динамит": 1, "изолента": 1}, owner="foreman_gus")
mn.put(FAN, 44, 5)
mn.put(DANGER, 32, 5)
mn.portal([(45, 7), (45, 8)], "fort_bunker", (4, 30), "Вентиляционный штрек",
          requires={"item": "ключ от штрека", "msg": "Решётка вентиляционного штрека на замке. Ключ — у старшины Гаса."})
mn.enemies += [["radroach", 18, 18], ["radroach", 25, 6], ["rat", 38, 7]]


# ================================================================ Форт Сёрчлайт
W, H = 70, 50
ft = CityMap(city, "fort_searchlight", "Форт Сёрчлайт", W, H, start=(1, 23), seed=214, music="lab")
ft.floor_code("s", *SAND)
ft.floor_code("a", *GROUND)
ft.floor_code("a", *GROUND)
ft.floor_code("g", *WALK)
ft.paint("s", 0, 0, W - 1, H - 1)
ft.paint("a", 12, 6, 64, 44)                           # территория базы
ft.paint("g", 30, 16, 50, 32)                          # плац
city.road(sl, [(63, y) for y in range(21, 25)], ft, [(0, y) for y in range(21, 25)], "Форт Сёрчлайт", "Сёрчлайт",
          step=(1, 0))
ft.reserve(0, 20, 13, 25)
# периметр: колючая проволока с воротами на запад, вышки по углам
ft.hwall([BARBED], 10, 66, 4)
ft.hwall([BARBED], 10, 66, 46)
for y in range(5, 46, 2):
    if y not in (21, 23):
        ft.maybe(BARBED, 10, y, check=False)
        ft.maybe(BARBED, 65, y, check=False)
for x, y in ((12, 6), (62, 6), (12, 43), (62, 43)):
    ft.put(WATCHTOWER, x, y)
ft.put(SANDBAGS, 14, 19)
ft.put(SANDBAGS, 14, 26)
# следы войны: каски, противогазы, гильзы — там, где сорок четыре года назад стояли люди
for i, (x, y) in enumerate(((18, 27), (56, 14), (27, 40), (58, 25), (48, 29), (31, 30))):
    ft.maybe(DEBRIS[i % len(DEBRIS)], x, y)
# плац: робот-сержант и строй новобранцев
ft.put(RADAR, 40, 14)
ft.npcs += [["robo_sgt", 40, 18], ["recruit_danny", 34, 22], ["recruit_b", 37, 22], ["recruit_c", 43, 22], ["recruit_d", 46, 22],
            ["recruit_e", 37, 26], ["robo_sentry", 54, 31]]
# север: ангар, танк, хаммеры; склад боеприпасов
ft.put(HANGAR, 16, 8)
ft.put(TANK, 26, 9)
ft.put(HUMVEE[0], 32, 8)
ft.put(HUMVEE[1], 35, 11)
ft.box(AMMO[1], 40, 8, "ящик с патронами", {"патроны": 25})
ft.put(AMMO[0], 43, 8)
ft.put(CANNON, 48, 8)
ft.put(MISSILE, 58, 8)
# юг: казармы-бараки, вход в бункер
for x in (16, 22):
    ft.put(BARRACKS, x, 35)
ft.put(BUNKER, 52, 34)
ft.portal([(53, 37), (54, 37)], "fort_bunker", (23, 5), "Бункер",
          requires={"flag": "fort_access", "msg": "Робот-часовой: «Вход в бункер — только для личного состава. Предъявите жетон»."})
ft.reserve(52, 37, 56, 39)
for _, x, y in ft.npcs:
    ft.reserve(x, y, x, y)
ft.scatter(["r_rocks", "r_dry_bush"], 1, 1, 9, H - 2, 6)
ft.scatter(["r_rocks", "r_dry_bush"], 67, 1, W - 2, H - 2, 4)


# ================================================================ бункер
W, H = 48, 34
bk = CityMap(city, "fort_bunker", "Бункер Форта", W, H, start=(23, 5), seed=215, interior=True, music="lab")
bk.floor_code("M", *METAL)
bk.floor_code("N", *METAL_B)
bk.wall_code("W", "pk:fstation/fstation_w1_10")
bk.wall_code("C", "pk:fstation/fstation_w1_08")
bk.room(1, 1, 47, 11, "W", "M")                       # входной коридор
bk.room(1, 11, 16, 33, "W", "M")                      # казарма новобранцев
bk.room(16, 11, 31, 22, "W", "M")                     # оружейная
bk.room(16, 22, 31, 33, "W", "M")                     # узел связи
bk.room(31, 11, 47, 33, "C", "N")                     # ядро ИИ «Генерал»
bk.props.append(["x_ladder", 23, 4])
bk.portal([(23, 4)], "fort_searchlight", (53, 38), "Наверх")
bk.reserve(21, 4, 26, 7)
bk.opening(8, 11, 9, 13, "M")
bk.opening(23, 11, 24, 13, "M")
bk.opening(16, 27, 16, 28, "M")
bk.opening(31, 16, 31, 17, "N")
# вход из вентиляционного штрека — в углу казармы, за шкафчиками
bk.props.append(["x_ladder", 4, 31])
bk.portal([(4, 31)], "searchlight_mine", (44, 7), "Вентиляционный штрек")
bk.reserve(2, 30, 6, 32)
# коридор: шкафчики, плакаты, консоли
for x in (4, 6, 38, 40):
    bk.put(LOCKER, x, 4)
bk.put(CONSOLE, 30, 4)
# казарма: койки ровными рядами — новобранцы спят по команде
for i, (x, y) in enumerate(((2, 16), (11, 16), (13, 16), (2, 21), (13, 21), (2, 26), (8, 26), (13, 26))):
    bk.put(BUNKS[i % 4], x, y)
bk.npcs += [["recruit_f", 8, 20]]
# оружейная: стойки, ящики — армейская броня
bk.box(GUN_RACK, 18, 15, "оружейная стойка", {"охотничья винтовка": 1, "боевой дробовик": 1, "патроны": 30, "дробь": 15})
bk.box(AMMO[0], 26, 18, "армейский ящик", {"силовая броня T-45": 1, "шлем силовой брони": 1,
                                            "голозапись «Курс оператора СБ»": 1, "граната": 2},
       requires={"flag": "recruits_free", "msg": "Ящик опечатан ИИ: «Имущество части. Выдача — по приказу Генерала»."})
bk.put(AMMO[1], 28, 15)
bk.put(MACHINE[0], 18, 20)
# узел связи: стол, терминал канала, рация
bk.put(DESK_PC[0], 19, 25)
bk.put(SERVER, 26, 24)
bk.put(SERVER, 28, 24)
bk.terminal(22, 30, "fort_comm")
# ядро ИИ: генераторы, серверы, главный терминал; турели и роботы охраняют
bk.put(GEN, 34, 14)
bk.put(GEN, 42, 14)
for x in (34, 37, 40, 43):
    bk.put(SERVER, x, 26)
bk.put(MACHINE[1], 44, 20)
bk.terminal(39, 20, "general_core")
bk.enemies += [["turret", 36, 18], ["turret", 43, 18], ["robot_guard", 38, 30], ["robot_guard", 44, 23]]

city.save(gap_exempt=("robo_sgt", "recruit_danny", "recruit_b", "recruit_c", "recruit_d", "recruit_e", "robo_sentry",
                      "recruit_f"))
L = json.load(open("data/locations.json", encoding="utf-8"))
L["searchlight"].update({"world_name": "Сёрчлайт", "discover": True})
L["fort_searchlight"]["clear_flag"] = "fort_cleared"      # роботы на плацу перебиты (штурм с Братством)
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
