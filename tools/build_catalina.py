"""
Остров Санта-Каталина — городок Авалон, который не знает, что была война. Тайная локация.
Сценарий — docs/story.md, раздел «Остров Санта-Каталина — „Карантин“».

  catalina         «Авалон» (72×50): бухта с причалом и лодками, пляж с пальмами и зонтиками, набережная,
                   дома островитян, рынок рыбы; на севере — круглое «Казино» (бальный зал, теперь — Совет);
                   на мысе — маяк; у причала — карантинный барак для «людей с Большой земли».
  catalina_casino  «Казино Авалона»: бальный зал совета, кабинет Основателя, архив.
  catalina_light   маяк: комната смотрителя, радиорубка — радио 2077 года всё ещё ловит эфир.
  catalina_cove    грот контрабандистов: обломки корабля, тайник — лодка на Большую землю.

Наборы: island-resort (iresort), survival-island (sisland), medieval-coastal-fishing-village (fishv),
abandoned-rural-village (rvill), luxury-restaurant (lrest), library (lib), nuclear-power-plant (npower), gcave.
Запуск из папки game_project:  .venv/bin/python tools/build_catalina.py
"""
import json

from citykit import City, CityMap

city = City("catalina", "Остров Санта-Каталина")


def P(name, img, **kw):
    city.prop(name, img, **kw)
    return name


def cells(page, pts):
    return [f"pk:{page}/{x},{y},1,1" for x, y in pts]


S = 1.5
PALMS = [P(f"ct_palm{i}", f"pk:iresort/iresort_1_{n:03d}", foot=[1, 1]) for i, n in enumerate((27, 28, 15))]
PALM_BIG = [P("ct_palm_big", "pk:sisland/p1/12,8,1,2", foot=[1, 1]), P("ct_palm_big_b", "pk:sisland/p1/13,8,1,2", foot=[1, 1])]
UMBRELLAS = [P(f"ct_umbrella{i}", f"pk:iresort/iresort_1_{n:03d}", foot=[2, 1]) for i, n in enumerate((9, 10, 11, 14))]
LOUNGERS = [P("ct_lounger", "pk:iresort/iresort_1_018", foot=[2, 1]), P("ct_lounger_b", "pk:iresort/iresort_1_022", foot=[2, 1])]
TORCH = P("ct_torch", "pk:iresort/iresort_1_036", light={"r": 120, "color": [255, 170, 80], "at": [0.5, 0.1], "flicker": 0.5})
TIKI_BAR = P("ct_tiki_bar", "pk:iresort/iresort_1_057", foot=[2, 1], sight=True)
TIKI_SHOP = P("ct_tiki_shop", "pk:iresort/iresort_1_071", foot=[2, 1], sight=True)
SANDCASTLE = P("ct_sandcastle", "pk:iresort/iresort_1_047", foot=[2, 1])
SURFBOARDS = [P("ct_surf", "pk:iresort/iresort_1_050"), P("ct_surf_b", "pk:iresort/iresort_1_051")]
BUSHES = [P(f"ct_bush{i}", f"pk:iresort/iresort_2_{n:03d}", foot=[2, 1]) for i, n in enumerate((16, 17, 20, 21))]
FLOWERS = [P(f"ct_flower{i}", f"pk:iresort/iresort_1_{n:03d}") for i, n in enumerate((59, 60, 61, 62, 66, 67))]
PIER = "pk:iresort/p1/0,12,4,2"
BOARDWALK = "pk:iresort/p1/2,14,4,2"
CAFE = [P(f"ct_cafe{i}", f"pk:iresort/iresort_2_{n:03d}", foot=[2, 1]) for i, n in enumerate((2, 4, 6, 9))]
GAZEBO = P("ct_gazebo", "pk:iresort/iresort_4_013", foot=[2, 2], sight=True)
STONE_WALL = [P("ct_stone_wall", "pk:iresort/iresort_4_045", foot=[2, 1]), P("ct_stone_wall_b", "pk:iresort/iresort_4_046", foot=[2, 1])]
FENCE = P("ct_fence", "pk:iresort/iresort_4_049", foot=[2, 1])
HAMMOCK = P("ct_hammock", "pk:iresort/iresort_4_000", foot=[2, 1])
HOUSES = [P(f"ct_house{i}", f"pk:town50/town50_3_{n:03d}", scale=1.7, foot=[3, 2], sight=True) for i, n in enumerate((0, 1, 7, 8))]
HOUSE_BLUE = P("ct_house_blue", "pk:town50/p3/10,2,2,2", scale=1.7, foot=[3, 2], sight=True)
BOATS = [P("ct_boat", "pk:fishv/fishv_2_083", foot=[1, 2], sight=True), P("ct_boat_b", "pk:fishv/p2/12,12,4,2", foot=[4, 1], sight=True)]
WRECK = [P("ct_wreck", "pk:fishv/fishv_1_000", foot=[2, 1], sight=True), P("ct_wreck_b", "pk:fishv/fishv_1_001", foot=[2, 1], sight=True)]
SHIPWRECK = P("ct_shipwreck", "pk:sisland/p1/14,8,2,2", foot=[2, 2], sight=True)
NETS = [P("ct_nets", "pk:fishv/fishv_1_012", foot=[2, 1]), P("ct_nets_b", "pk:fishv/fishv_1_013", foot=[2, 1])]
FISH_RACK = [P("ct_fish_rack", "pk:fishv/fishv_1_078", foot=[2, 1], sight=True), P("ct_fish_rack_b", "pk:fishv/fishv_1_079", foot=[2, 1], sight=True)]
FISH_CRATE = [P("ct_fish_crate", "pk:fishv/fishv_2_008", foot=[2, 1], search="crate", title="ящик с рыбой"),
              P("ct_fish_crate_b", "pk:fishv/fishv_2_019", foot=[2, 1])]
BARRELS = [P("ct_barrel", "pk:fishv/fishv_1_057", search="junk", title="бочка"), P("ct_barrel_b", "pk:fishv/fishv_1_072")]
ANCHOR = P("ct_anchor", "pk:fishv/fishv_1_020", foot=[2, 1])
LANTERN = P("ct_lantern", "pk:fishv/fishv_1_070", light={"r": 100, "color": [255, 190, 110], "at": [0.5, 0.5], "flicker": 0.3})
ROCKS = [P("ct_rock", "pk:sisland/p1/4,0,1,1"), P("ct_rock_b", "pk:sisland/p1/4,1,1,1"), P("ct_rock_c", "pk:sisland/p1/5,0,1,1")]
SEA_ROCK = P("ct_sea_rock", "pk:sisland/p1/4,9,2,2", foot=[2, 2], sight=True)
TENT = P("ct_tent", "pk:sisland/p1/10,11,1,1")
CAMPFIRE = P("ct_campfire", "pk:sisland/p1/8,12,1,1", light={"r": 110, "color": [255, 150, 70], "at": [0.5, 0.5], "flicker": 0.4})
BONES = P("ct_bones", "pk:sisland/p1/11,12,1,1", block=False)
LIGHTHOUSE = P("ct_lighthouse", "pk:rvill/rvill_1_061", scale=1.8, foot=[2, 2], sight=True,
               light={"r": 200, "color": [255, 250, 200], "at": [0.5, 0.05]})
# интерьеры
CHANDELIER = P("ct_chandelier", "pk:lrest/lrest_2_032", light={"r": 110, "color": [255, 220, 160], "at": [0.5, 0.2], "flicker": 0.2})
ARMCHAIR = [P("ct_armchair", "pk:lrest/lrest_1_041"), P("ct_armchair_b", "pk:lrest/lrest_1_042")]
PAINTINGS = [P("ct_painting", "pk:lrest/lrest_3_011", block=False), P("ct_painting_b", "pk:lrest/lrest_3_012", block=False)]
COUNCIL = P("ct_council_table", "pk:lib/lib_1_061", foot=[2, 2])
BOOKCASES = [P("ct_bookcase", "pk:lib/lib_1_004", foot=[2, 1], sight=True, search="shelf", title="книжный шкаф"),
             P("ct_bookcase_b", "pk:lib/lib_1_005", foot=[2, 1], sight=True, search="shelf", title="книжный шкаф")]
DESK = P("ct_desk", "pk:lib/lib_1_112", foot=[2, 1])
PIANO = P("ct_piano", "pk:west/west_2_012", foot=[2, 1])
SAFE = P("ct_safe", "pk:west/west_2_105", search="military", title="сейф Основателя")
RADIO = P("ct_radio", "pk:npower/npower_2_079", foot=[2, 1], light={"r": 70, "color": [120, 255, 160], "at": [0.5, 0.4]})
BED = P("ct_bed", "pk:west/west_2_005", foot=[2, 2])
TABLE = P("ct_table", "pk:west/west_2_000", foot=[2, 1])
CHAIR = P("ct_chair", "pk:west/west_2_001")

SAND = cells("sisland/p1", [(0, 0), (1, 0), (0, 1), (1, 1)])
GRASS = cells("sisland/p1", [(8, 0), (9, 0), (8, 1), (9, 2)])
SEA = cells("mport/p1", [(8, 4), (9, 4), (10, 4), (11, 4)])
SEA_DEEP = cells("mport/p1", [(8, 4), (9, 4), (10, 4), (11, 4)])
PATH = ["pk:iresort/iresort_f1_02"]
WOOD = ["pk:iresort/iresort_f1_23"]
MARBLE = ["pk:lrest/p1/0,12,1,1"]
CAVE = cells("gcave/p1", [(1, 4), (1, 5), (2, 6), (3, 6)])


# ================================================================ Авалон
W, H = 72, 50
av = CityMap(city, "catalina", "Остров Санта-Каталина: Авалон", W, H, start=(36, 43), seed=251, music="hub",
             world_pos=(210, 1420))
av.floor_code("s", *SAND)
av.floor_code("g", *GRASS)
av.floor_code("~", *SEA)
av.floor_code("w", *SEA_DEEP)
av.floor_code("p", *PATH)
av.water_codes = ("~", "w")
av.paint("g", 0, 0, W - 1, H - 1)
av.paint("s", 0, 30, W - 1, 42)                         # пляж вдоль бухты
av.paint("~", 0, 43, W - 1, H - 1)                       # бухта
av.paint("w", 0, 47, W - 1, H - 1)
av.paint("p", 4, 26, 66, 28)                             # набережная
av.paint("p", 34, 8, 37, 26)                             # аллея к Казино
# причал в бухту — сюда пристаёт лодка героя
av.paint("s", 34, 43, 37, 46)
av.stamp("ct_pier", PIER, 34, 43, water=False)
av.stamp("ct_pier2", PIER, 34, 45, water=False)

av.exits = [(35, 46), (36, 46)]
av.reserve(33, 40, 38, 46)
av.reserve(4, 26, 66, 28)
av.reserve(34, 8, 37, 25)
for x in (28, 31, 40, 44):
    av.put(BOATS[0], x, 44)
av.put(BOATS[1], 22, 46)
av.put(ANCHOR, 30, 41)
# карантинный барак у причала — сюда ведут всех «с Большой земли»
av.building(42, 32, 10, 8, "planks", north=(4,), worn=False)
av.reserve(46, 29, 47, 32)
av.put(LANTERN, 45, 31)
# пляж: зонтики, шезлонги, замки из песка, бар-хижина
for i, x in enumerate((6, 12, 18, 56, 62)):
    av.put(UMBRELLAS[i % 4], x, 34)
    av.put(LOUNGERS[i % 2], x, 37)
av.put(TIKI_BAR, 24, 31)
av.put(SANDCASTLE, 14, 40)
av.put(SURFBOARDS[0], 9, 31)
av.put(SURFBOARDS[1], 10, 31)
for x in (4, 22, 30, 41, 52, 66):
    av.put(TORCH, x, 29)
# рыбный рынок на западе набережной: сети, вешала, ящики
av.put(FISH_RACK[0], 4, 22)
av.put(FISH_RACK[1], 8, 22)
av.put(NETS[0], 12, 23)
av.box(FISH_CRATE[0], 16, 23, "ящик с рыбой", {"вяленое мясо": 2})
av.put(FISH_CRATE[1], 20, 23)
av.put(BARRELS[0], 24, 23)
av.put(TIKI_SHOP, 28, 22)
# дома островитян: два ряда за набережной, сады с цветами
# дома островитян — целые, крашеные: война сюда не дошла
for i, (x, y) in enumerate(((3, 15), (9, 15), (15, 15), (46, 15), (52, 15), (58, 15))):
    av.put((HOUSES + [HOUSE_BLUE])[i % 5], x, y)
for x, y in ((7, 21), (17, 21), (49, 21), (59, 21), (65, 21)):
    av.put(FLOWERS[(x + y) % 6], x, y)
av.put(GAZEBO, 26, 15)
av.put(HAMMOCK, 21, 19)
# север: круглое «Казино» — бальный зал, ныне Совет острова
av.building(28, 2, 18, 9, "planks", south=(6,), worn=False)
av.reserve(34, 11, 35, 13)
for x in (30, 42):
    av.put(PALM_BIG[x % 2], x, 12)
# мыс на востоке: маяк и дом смотрителя
av.building(60, 2, 10, 8, "planks", south=(2,), worn=False)
av.reserve(62, 10, 63, 12)
av.put(LIGHTHOUSE, 66, 11)
av.hwall(STONE_WALL, 56, 70, 13, gaps=(62, 63))
# запад: тропа к гроту контрабандистов
av.props.append(["x_puddle", 1, 38])
av.portal([(0, 36), (0, 37), (0, 38)], "catalina_cove", (34, 18), "Грот")
av.reserve(0, 35, 3, 39)
for x, y in ((2, 30), (8, 42), (68, 41), (60, 44), (12, 46)):
    av.maybe(SEA_ROCK if y > 42 else ROCKS[(x + y) % 3], x, y)
av.npcs += [["harbor_master", 37, 39], ["quarantine_nurse", 48, 30], ["fisher_ana", 10, 25], ["tiki_barkeep", 25, 33],
            ["island_kid", 15, 38], ["island_old", 27, 18], ["sailor_finn", 30, 39], ["island_teacher", 20, 26]]
for _, x, y in av.npcs:
    av.reserve(x, y, x, y)
av.grow(1, 1, W - 2, 25, 10, names=PALMS + BUSHES)
av.scatter(FLOWERS + ROCKS, 1, 1, W - 2, 25, 18)


# ================================================================ Казино — Совет
cs = CityMap(city, "catalina_casino", "Казино Авалона", 40, 26, start=(19, 24), seed=252, interior=True, music="hub")
cs.floor_code("F", *WOOD)
cs.floor_code("M", *MARBLE)
cs.wall_code("W", "pk:lhotel/lhotel_w2_23")
cs.room(1, 1, 28, 25, "W", "F")                       # бальный зал
cs.room(28, 1, 39, 13, "W", "M")                      # кабинет Основателя
cs.room(28, 13, 39, 25, "W", "M")                     # архив
cs.opening(19, 25, 20, 25, "F")
av.portal([(34, 10), (35, 10)], "catalina_casino", (19, 23), "Казино — Совет острова")
cs.portal([(19, 25), (20, 25)], "catalina", (34, 12), "На аллею")
cs.opening(28, 7, 28, 8, "M")
cs.opening(28, 19, 28, 20, "M")
# зал: люстры, стол совета посередине, кресла, рояль на сцене у северной стены
for x in (6, 14, 22):
    cs.put(CHANDELIER, x, 4)
cs.put(PIANO, 12, 5)
cs.put(COUNCIL, 12, 12)
cs.put(COUNCIL, 15, 12)
for x, y in ((10, 11), (19, 11), (10, 15), (19, 15)):
    cs.put(ARMCHAIR[(x + y) % 2], x, y)
for x in (3, 25):
    cs.put(PAINTINGS[x % 2], x, 3)
cs.stamp("ct_dance_floor", "pk:casino/p1/8,13,2,2", 13, 18, water=False)   # паркет для танцев
for x, y in ((2, 22), (26, 22), (2, 4), (26, 4)):
    cs.put(PALMS[x % 3], x, y)
cs.put(TIKI_BAR, 22, 18)
cs.npcs += [["elder_mora", 14, 10], ["elder_bram", 17, 17], ["young_jude", 6, 20]]
# кабинет Основателя: стол, портрет, сейф с правдой
cs.put(DESK, 32, 6)
cs.put(PAINTINGS[1], 34, 3)
cs.box(SAFE, 37, 4, "сейф Основателя", {"дневник Основателя": 1},
       requires={"flag": "council_trust", "msg": "Сейф Основателя. Ключ — у старейшины Моры. Только у неё."}, owner="elder_mora")
# архив: шкафы, терминал с «историей острова»
for x in (30, 32, 34):
    cs.put(BOOKCASES[x % 2], x, 16)
cs.terminal(37, 20, "catalina_archive")


# ================================================================ маяк
lt = CityMap(city, "catalina_light", "Маяк Авалона", 24, 18, start=(11, 16), seed=253, interior=True, music="caves")
lt.floor_code("F", *WOOD)
lt.wall_code("W", "pk:bazaar/bazaar_w2_12")
lt.room(1, 1, 23, 17, "W", "F")
lt.opening(11, 17, 12, 17, "F")
av.portal([(62, 9), (63, 9)], "catalina_light", (11, 15), "Маяк")
lt.portal([(11, 17), (12, 17)], "catalina", (62, 11), "Наружу")
lt.put(RADIO, 16, 4)
lt.terminal(20, 4, "catalina_radio")
lt.put(BED, 3, 4)
lt.put(TABLE, 4, 10)
lt.put(CHAIR, 6, 10)
lt.put(LANTERN, 9, 4)
lt.box(BOOKCASES[0], 12, 4, "шкаф смотрителя", {"карта течений": 1}, owner="keeper_silas")
lt.npcs += [["keeper_silas", 15, 9]]


# ================================================================ грот контрабандистов
W, H = 40, 26
cv = CityMap(city, "catalina_cove", "Грот у Авалона", W, H, start=(34, 18), seed=254, music="caves")
cv.floor_code("c", *CAVE)
cv.floor_code("s", *SAND)
cv.floor_code("~", *SEA)
cv.water_codes = ("~",)
cv.paint("x", 0, 0, W - 1, H - 1)
cv.paint("s", 6, 4, 37, 21)
cv.paint("c", 8, 4, 30, 9)
cv.paint("~", 2, 12, 16, 23)
cv.portal([(37, 17), (37, 18), (37, 19)], "catalina", (2, 37), "Тропа к Авалону")
cv.reserve(32, 15, 37, 20)
cv.put(SHIPWRECK, 6, 10)
cv.put(WRECK[0], 18, 14)
cv.put(WRECK[1], 22, 18)
cv.put(TENT, 26, 6)
cv.put(CAMPFIRE, 22, 7)
cv.box(BARRELS[0], 12, 5, "тайник Джуда", {"карта течений": 1, "чистая вода": 2}, owner="young_jude")
cv.put(BOATS[0], 15, 18)
cv.put(BONES, 28, 15)
cv.enemies += [["river_lizard", 18, 20], ["river_lizard", 28, 12], ["river_lizard", 16, 8]]
# в обломках корабля — ящик ВМФ с супер-кувалдой (ящеры устроили в нём гнездо)
NAVY = P("ct_navy_crate", "pk:pmars/pmars_1_035", foot=[2, 1], search="military", title="ящик ВМФ")
cv.box(NAVY, 12, 7, "затопленный ящик ВМФ", {"супер-кувалда": 1, "граната": 2})

city.save(gap_exempt=("harbor_master", "sailor_finn"))
L = json.load(open("data/locations.json", encoding="utf-8"))
L["catalina"].update({"world_name": "Остров Санта-Каталина"})
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
