"""
Ниптон — городок, который каждый год тянет жребий. Третий акт.
Сценарий — docs/story.md, раздел «Ниптон — „Лотерея“».

  nipton        «Ниптон» (72×50): главная улица; ратуша мэра Кэрролла; ярмарочная площадь с помостом и
                барабаном жребия (флажки, фонари — праздник через три дня); лавка, дома; сарай-тюрьма,
                где держат «невест»; на востоке — дорога к лагерю «женихов».
  nipton_hall   ратуша: кабинет мэра (сейф со списком жребия), зал совета, архив.
  nipton_shed   сарай-тюрьма: «невесты» прошлых лет, которых не успели увезти.
  nipton_camp   лагерь «женихов» в холмах: шатры, клетки, костёр, вход в старую шахту.
  nipton_mine   старая шахта: здесь брат Т. покупает людей у «женихов»; рельсы, вагонетки, клетки.

Наборы: wild-west (west), abandoned-rural-village (rvill), amusement-park (apark), desert-town (destown),
desert-natural (desnat), cult-temple (cult), underground-survivor-camp (ucamp), goblin-cave (gcave).
Запуск из папки game_project:  .venv/bin/python tools/build_nipton.py
"""
import json

from citykit import City, CityMap

city = City("nipton", "Ниптон")


def P(name, img, **kw):
    city.prop(name, img, **kw)
    return name


def cells(page, pts):
    return [f"pk:{page}/{x},{y},1,1" for x, y in pts]


S = 1.5
HOUSES = [P(f"np_house{i}", f"pk:rvill/rvill_1_{n:03d}", scale=S, foot=[3, 2], sight=True)
          for i, n in enumerate((3, 11, 27, 1, 26, 25))]
SHACK = P("np_shack", "pk:rvill/rvill_1_036", scale=S, foot=[3, 2], sight=True)
WELL = P("np_well", "pk:rvill/rvill_1_060", foot=[2, 1])
TREES = [P(f"np_tree{i}", f"pk:rvill/rvill_2_{n:03d}", scale=S, foot=[2, 1]) for i, n in enumerate((10, 11, 12))]
GRASS = [P(f"np_grass{i}", f"pk:rvill/rvill_2_{n:03d}", block=False) for i, n in enumerate((14, 15, 16, 17))]
CACTUS = P("np_cactus", "pk:west/west_1_008")
FENCE = [P("np_fence", "pk:west/west_1_013", foot=[2, 1]), P("np_fence_b", "pk:west/west_1_014")]
TROUGH = P("np_trough", "pk:west/west_1_016")
BARREL = P("np_barrel", "pk:west/west_1_017", search="junk", title="бочка")
CRATE = P("np_crate", "pk:west/west_1_018", search="crate", title="ящик")
WAGON = P("np_wagon", "pk:west/west_1_012", foot=[4, 1], sight=True)
SIGN = P("np_sign", "pk:west/p1/12,4,2,2", foot=[2, 1])
# ярмарка
STAGE = P("np_stage", "pk:cult/cult_3_042", foot=[2, 1], sight=True)          # помост с жребием
DRUM = P("np_drum", "pk:west/west_1_017", search="junk", title="барабан жребия")
BUNTING = [P("np_bunting", "pk:apark/apark_3_066", block=False), P("np_lights", "pk:apark/apark_3_063", block=False)]
STALLS = [P("np_stall", "pk:apark/apark_1_022", foot=[2, 1], sight=True), P("np_stall_b", "pk:apark/apark_1_030", foot=[2, 1], sight=True)]
TICKET = P("np_ticket", "pk:apark/apark_1_078", foot=[2, 1], sight=True)
LAMP = P("np_lamp", "pk:apark/apark_3_070", light={"r": 140, "color": [255, 200, 130], "at": [0.5, 0.1]})
BENCH = P("np_bench", "pk:apark/apark_1_066", foot=[2, 1])
# лагерь и шахта
TENTS = [P(f"np_tent{i}", f"pk:ucamp/ucamp_2_{n:03d}", foot=[2, 1], sight=True) for i, n in enumerate((0, 3, 19, 21))]
CAGE = P("np_cage", "pk:cult/cult_3_020", sight=True)
CAGE_HELD = P("np_cage_held", "pk:cult/cult_3_020", block=False)       # клетка, в которой сидит пленник
CAMPFIRE = P("np_campfire", "pk:ucamp/ucamp_2_040", foot=[2, 1],
             light={"r": 120, "color": [255, 150, 70], "at": [0.5, 0.5], "flicker": 0.35})
SKULL_POLE = P("np_skull_pole", "pk:gcave/p1/2,8,1,2")
SPIKES = P("np_spikes", "pk:gcave/p1/12,8,2,2", foot=[2, 1])
LOOT = P("np_loot", "pk:gcave/p1/10,10,2,2", search="military", title="добыча «женихов»")
CLIFFS = [P(f"np_cliff{i}", f"pk:desnat/p1/{x},14,2,2", foot=[2, 2], sight=True) for i, x in enumerate((8, 10, 12))]
MINE_CART = P("np_mine_cart", "pk:west/p1/13,7,1,1")
RAILS = P("np_rails", "pk:west/p1/8,8,8,2", block=False, layer="floor")
BOULDERS = [P("np_boulder", "pk:gcave/p1/4,4,1,1"), P("np_boulder_b", "pk:gcave/p1/5,4,1,1")]
LANTERN = P("np_lantern", "pk:bazaar/bazaar_2_088", block=False,
            light={"r": 110, "color": [255, 180, 90], "at": [0.5, 0.4], "flicker": 0.3})
ALTAR = P("np_altar", "pk:cult/cult_2_045", foot=[2, 1], sight=True)
# интерьеры
TABLE = P("np_table", "pk:west/west_2_000", foot=[2, 1])
CHAIR = P("np_chair", "pk:west/west_2_001")
DESK = P("np_desk", "pk:west/west_2_000", foot=[2, 1])
SAFE = P("np_safe", "pk:west/west_2_105", search="military", title="сейф")
BOOKS = P("np_bookcase", "pk:west/west_2_116", sight=True, search="shelf", title="шкаф с бумагами")
CLOCK = P("np_clock", "pk:west/west_2_019", sight=True)
COT = P("np_cot", "pk:ucamp/ucamp_3_027", foot=[4, 1])
HAY = P("np_hay", "pk:west/west_1_004", block=False)

DIRT = cells("rvill/p2", [(0, 11), (1, 11), (0, 12), (1, 12)])
ROAD = cells("west/p1", [(0, 1), (1, 1), (0, 2), (1, 2)])
STONE = cells("west/p1", [(4, 0), (5, 0), (4, 1), (5, 1)])
SAND = cells("destown/p2", [(0, 0), (1, 0), (0, 1), (1, 1)])
PLANK = ["pk:bazaar/bazaar_f1_21"]
CAVE = cells("gcave/p1", [(1, 4), (1, 5), (2, 6), (3, 6)])


# ================================================================ город
W, H = 72, 50
np_ = CityMap(city, "nipton", "Ниптон", W, H, start=(1, 26), seed=201, music="desert", world_pos=(2480, 720))
np_.floor_code("s", *SAND)
np_.floor_code("d", *DIRT)
np_.floor_code("r", *ROAD)
np_.floor_code("t", *STONE)
np_.paint("s", 0, 0, W - 1, H - 1)
np_.paint("d", 5, 6, 64, 44)
np_.paint("r", 0, 24, W - 1, 28)                        # главная улица
np_.paint("t", 26, 10, 46, 22)                          # ярмарочная площадь
np_.exits = [(0, y) for y in range(24, 29)]
np_.reserve(0, 24, W - 1, 28)

# площадь: помост с барабаном жребия, гирлянды, прилавки, скамьи для зрителей
np_.put(STAGE, 35, 12)
np_.box(DRUM, 37, 12, "барабан жребия", {"жетон жребия": 1},
        requires={"item": "отмычка", "msg": "Барабан жребия заперт на замок. Ключ — у мэра. Или отмычка."})
np_.put(BUNTING[0], 27, 10)
np_.put(BUNTING[1], 27, 15)
for x in (28, 32, 40, 44):
    np_.put(BENCH, x, 18)
np_.put(STALLS[0], 27, 21)
np_.put(STALLS[1], 44, 21)
np_.put(TICKET, 41, 12)
np_.put(LAMP, 26, 22)
np_.put(LAMP, 46, 22)
np_.put(LAMP, 26, 10)
np_.put(LAMP, 46, 10)
# север: ратуша (с крышей), лавка, дома
np_.building(8, 6, 14, 11, "brick", south=(6,))           # ратуша
np_.reserve(14, 17, 15, 23)
np_.put(SIGN, 10, 17)
np_.put(HOUSES[0], 50, 8)
np_.put(HOUSES[1], 56, 8)
np_.put(HOUSES[2], 50, 15)
np_.put(TROUGH, 56, 21)
# юг: сарай-тюрьма, дома, колодец, загон
np_.building(28, 32, 10, 8, "planks", north=(4,))          # сарай-тюрьма
np_.reserve(32, 29, 33, 32)
np_.put(HOUSES[3], 8, 34)
np_.put(HOUSES[4], 14, 34)
np_.put(HOUSES[5], 46, 34)
np_.put(SHACK, 53, 34)
np_.put(WELL, 22, 31)
np_.put(WAGON, 8, 41)
np_.hwall(FENCE, 44, 62, 42, gaps=(52, 53))
np_.put(BARREL, 40, 30)
np_.put(CRATE, 42, 30)
# восток: дорога к лагерю «женихов» — указатель, кресты у обочины (тех, кто пытался бежать)
np_.put("x_cross", 64, 21)
np_.put("x_cross", 66, 22)
np_.put("x_cross", 64, 31)
np_.npcs += [["mayor_carroll", 16, 20], ["grace_widow", 24, 30], ["np_storekeeper", 52, 20], ["np_crier", 36, 17],
             ["np_old_mae", 20, 36], ["np_farmer", 48, 39], ["np_kid", 30, 23], ["np_drunk", 42, 23]]
for _, x, y in np_.npcs:
    np_.reserve(x, y, x, y)
np_.grow(1, 1, W - 2, H - 2, 8, names=[CACTUS] + TREES)
np_.scatter(GRASS + ["r_rocks"], 1, 1, W - 2, H - 2, 24)


# ================================================================ ратуша
hl = CityMap(city, "nipton_hall", "Ратуша Ниптона", 28, 20, start=(8, 17), seed=202, interior=True, music="desert")
hl.floor_code("F", *PLANK)
hl.wall_code("W", "pk:bazaar/bazaar_w2_12")
hl.room(1, 1, 16, 19, "W", "F")                       # зал совета
hl.room(16, 1, 27, 19, "W", "F")                      # кабинет мэра
hl.opening(8, 19, 9, 19, "F")
np_.portal([(14, 16), (15, 16)], "nipton_hall", (8, 17), "Ратуша")
hl.portal([(8, 19), (9, 19)], "nipton", (14, 18), "На улицу")

hl.opening(16, 12, 16, 13, "F")
hl.put(TABLE, 4, 8)
hl.put(TABLE, 8, 8)
hl.put(CHAIR, 6, 10)
hl.put(CHAIR, 10, 10)
hl.put(BOOKS, 3, 4)
hl.put(BOOKS, 5, 4)
hl.put(CLOCK, 12, 4)
hl.terminal(13, 14, "nipton_ledger")
hl.put(DESK, 21, 7)
hl.put(CHAIR, 23, 7)
hl.box(SAFE, 25, 4, "сейф мэра", {"список жребия": 1, "крышки": 140},
       requires={"item": "отмычка", "msg": "Сейф мэра Кэрролла. Без отмычки не открыть."}, owner="mayor_carroll")
hl.put(BOOKS, 18, 4)
hl.npcs += [["np_clerk", 6, 14]]


# ================================================================ сарай-тюрьма
sh = CityMap(city, "nipton_shed", "Сарай у площади", 18, 14, start=(8, 4), seed=203, interior=True, music="caves")
sh.floor_code("F", *PLANK)
sh.wall_code("W", "pk:bazaar/bazaar_w2_12")
sh.room(1, 1, 17, 13, "W", "F")
sh.opening(8, 1, 9, 3, "F")
np_.portal([(32, 32), (33, 32)], "nipton_shed", (8, 4), "Сарай")
sh.portal([(8, 1), (9, 1)], "nipton", (32, 30), "На улицу")
sh.hwall([CAGE], 2, 16, 8, gaps=(8,))
sh.put(COT, 2, 11)
sh.put(COT, 12, 11)
sh.put(HAY, 7, 11)
sh.npcs += [["np_bride", 6, 10], ["np_bride_b", 13, 9]]


# ================================================================ лагерь «женихов»
W, H = 56, 40
cp = CityMap(city, "nipton_camp", "Лагерь «женихов»", W, H, start=(1, 20), seed=204, music="raiders")
cp.floor_code("s", *SAND)
cp.paint("s", 0, 0, W - 1, H - 1)
FLOOR = set()
for x0, y0, x1, y1 in ((0, 17, 22, 23), (14, 6, 50, 34)):
    FLOOR |= {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}
city.road(np_, [(71, y) for y in range(24, 29)], cp, [(0, y) for y in range(18, 23)], "Лагерь «женихов»", "Ниптон", step=(1, 0))
cp.reserve(0, 17, 6, 23)
for x, y in ((24, 10), (34, 9), (42, 14), (24, 28), (40, 29)):
    cp.put(TENTS[(x + y) % 4], x, y)
cp.put(CAMPFIRE, 32, 19)
cp.put(CAGE, 46, 22)
cp.put(CAGE, 48, 22)
cp.put(SKULL_POLE, 20, 15)
cp.put(SKULL_POLE, 20, 25)
cp.put(SPIKES, 17, 12)
cp.put(SPIKES, 17, 27)
cp.box(LOOT, 44, 30, "добыча «женихов»", {"крышки": 90, "патроны": 20, "медальон": 1}, owner="groom_cal")
# вход в шахту — в северной скале
cp.props.append(["x_puddle", 33, 6])
cp.portal([(32, 5), (33, 5), (34, 5)], "nipton_mine", (6, 26), "Старая шахта")
cp.reserve(31, 5, 35, 9)
cp.put(LANTERN, 30, 7)
cp.put(LANTERN, 36, 7)
for y in range(0, H, 2):
    for x in range(0, W, 2):
        if not {(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)} & FLOOR and not (31 <= x <= 35 and 4 <= y <= 6):
            cp.props.append([CLIFFS[(x * 3 + y * 7) % 3], x, y])
            cp.blocked.update({(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)})
cp.npcs += [["groom_cal", 34, 21], ["groom_a", 28, 17], ["groom_b", 40, 24], ["groom_c", 26, 30]]
cp.scatter(["r_bones", "r_rocks", "r_dry_bush"], 14, 6, 50, 34, 14)


# ================================================================ шахта: брат Т.
W, H = 44, 30
mn = CityMap(city, "nipton_mine", "Старая шахта", W, H, start=(6, 26), seed=205, interior=True, music="vats")
mn.floor_code("c", *CAVE)
mn.paint("x", 0, 0, W - 1, H - 1)
mn.paint("c", 3, 20, 12, 28)                            # вход
mn.paint("c", 6, 8, 10, 20)                             # штольня
mn.paint("c", 4, 3, 40, 10)                             # главная выработка
mn.paint("c", 30, 10, 40, 24)                           # дальний зал — «часовня»
mn.portal([(6, 27), (7, 27)], "nipton_camp", (33, 7), "Наружу")
mn.reserve(4, 24, 9, 27)
mn.put(RAILS, 12, 5)
mn.put(MINE_CART, 14, 4)
mn.put(MINE_CART, 24, 4)
for x in (16, 22, 25):
    mn.put(CAGE, x, 8)
mn.put(CAGE_HELD, 19, 8)
mn.put(LANTERN, 7, 9)
mn.put(LANTERN, 28, 4)
mn.put(LANTERN, 32, 12)
# «часовня» брата Т.: алтарь, свечи, ящики с новенькими крышками
mn.put(ALTAR, 34, 20)
mn.put("candles", 32, 20)
mn.put("candles", 37, 20)
mn.box(CRATE, 38, 14, "ящик с печатью круга", {"крышки": 200, "приказ о «Ноле»": 1}, owner="brother_t")
for x, y in ((5, 5), (38, 6), (31, 12)):
    mn.put(BOULDERS[(x + y) % 2], x, y)
mn.npcs += [["brother_t", 35, 17], ["cult_guard_np", 32, 15], ["cult_guard_np_b", 38, 18], ["np_captive", 19, 8]]

city.save(gap_exempt=("groom_cal", "groom_a", "groom_b", "groom_c"))
L = json.load(open("data/locations.json", encoding="utf-8"))
L["nipton"].update({"world_name": "Ниптон", "discover": True})
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
