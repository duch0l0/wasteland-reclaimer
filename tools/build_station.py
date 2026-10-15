"""
Заправка «Последний шанс» (data/maps/station.json, 64×40) — логово банды Шрама на трассе, куда сбежал Дэкс с глазом деда.
Была текстовой картой 40×14; теперь — настоящая заправка: трасса с выездом на запад (карта мира), бетонная площадка с
колонками под навесом, магазин с кассой, терминалом и сейфом, гараж с тайником Панка, а к югу — лагерь банды
из палаток, машин-баррикад и бочек с огнём. Шрам (talk) сидит у костра в центре лагеря и заговаривает первым.

Что требуют тесты (tests/test_story.py, test_dog.py, test_save.py): локация station, враги gang×4 и boss (Шрам),
терминал station, два контейнера (сейф заправщика, тайник Панка — владелец gang), вход слева.

Запуск из папки game_project:  .venv/bin/python tools/build_station.py
"""
import json

from citykit import City, CityMap
from vaultkit import Lamps

city = City("station", "Заправка «Последний шанс»")
LM = Lamps(city)


def P(name, img, **kw):
    city.prop(name, img, **kw)
    return name


SAFE = P("st_safe", "pk:west/west_2_105", search="military", title="сейф заправщика")
STASH = P("st_stash", "pk:ucamp/ucamp_2_030", search="crate", title="тайник Панка")
COUNTER = P("st_counter", "pk:pmall/pmall_2_017", foot=[4, 1])
SHELF = P("st_shelf", "pk:store/store_1_000", foot=[2, 1], sight=True)
FRIDGE = P("st_fridge", "pk:aoffice/aoffice_1_017", search="shelf", title="холодильник")
TOOLWALL = P("st_toolwall", "pk:nbunk/nbunk_2_007", foot=[2, 1], sight=True)
LIFT = P("st_lift", "pk:nbunk/nbunk_2_014", foot=[2, 1])
CAMPFIRE = "campfire"

W, H = 64, 40
m = CityMap(city, "station", "Заправка «Последний шанс»", W, H, start=(2, 17), seed=77, music="raiders",
            world_pos=(1760, 900), night=[150, 136, 140])
rnd = m.rnd
SAND = ["pk:desnat/p1/0,0,1,1", "pk:desnat/p1/1,0,1,1", "pk:desnat/p1/0,1,1,1"]
m.floor_code("s", *SAND)
m.floor_code("t", "pk:desnat/p1/4,4,1,1", "pk:desnat/p1/5,4,1,1", "pk:desnat/p1/6,4,1,1")
m.floor_code("q", "pk:desnat/p1/10,4,1,1")
m.paint("s", 0, 0, W - 1, H - 1)
m.patchwork("s", ["t"], 34, 3, 6, seed=3)
m.patchwork("s", ["q"], 18, 2, 3, seed=4)
m.exits = [(0, y) for y in range(15, 20)]
m.reserve(0, 14, 8, 20)

# ---- трасса вдоль всей карты, разметка по оси, обочины
m.paint("a", 0, 15, W - 1, 19)
for x in range(0, W, 4):
    m.ground[17][x] = m.ground[17][x + 1] = "h"
m.paint("g", 0, 14, W - 1, 14)
m.paint("g", 0, 20, W - 1, 20)
m.reserve(0, 14, W - 1, 20)
# площадка заправки: бетон, въезд с трассы
m.paint("c", 14, 8, 46, 13)
m.paint("c", 22, 14, 28, 14)
m.paint("c", 36, 14, 42, 14)
for x in (22, 25, 36, 39):                       # колонки под навесом
    m.put("bk_pump_red" if x % 2 else "bk_pump_yellow", x, 10)
m.put("hb_awning", 21, 8, check=False, allow_reserved=True)
m.put("hb_awning", 35, 8, check=False, allow_reserved=True)

# ---- магазин (север): касса, полки, холодильник, терминал и сейф в подсобке
ix0, iy0, ix1, iy1 = m.building(14, 1, 14, 6, "concrete", south=(6,), sign="ЗАПРАВКА")
m.terminal(ix0 + 2, iy0 + 1, "station")
m.box(SAFE, ix1 - 2, iy0 + 1, "сейф заправщика", {"крышки": 70, "бронежилет из дорожных знаков": 1, "тоник": 1},
      owner="gang", requires={"item": "лом", "msg": "Сейф заправщика. Замок не открыть — разве что вскрыть ломом."})
m.maybe(COUNTER, ix0 + 4, iy1 - 1, check=False)
m.maybe(SHELF, ix0 + 6, iy0 + 1, check=False)
m.maybe(SHELF, ix0 + 9, iy0 + 1, check=False)
m.maybe(FRIDGE, ix1, iy1, check=False)
for x, y in ((ix0 + 3, iy0 + 1), (ix0 + 10, iy0 + 1)):
    m.maybe("candles", x, y, check=False)

# ---- гараж (северо-восток): подъёмник, стена с инструментом, тайник Панка
gx0, gy0, gx1, gy1 = m.building(32, 1, 14, 6, "planks", south=(6,), sign="ГАРАЖ")
m.maybe(LIFT, gx0 + 3, gy1 - 1, check=False)
m.maybe(TOOLWALL, gx0 + 8, gy0 + 1, check=False)
m.box(STASH, gx1 - 1, gy0 + 1, "тайник Панка", {"доля Панка": 1, "крышки": 15}, owner="gang")
m.maybe("pile_tires", gx0 + 1, gy0 + 1, check=False)
m.maybe("barrel_wood", gx1, gy1, check=False)
m.maybe("x_barrel_boom", gx0 + 11, gy1, check=False)

# ---- вывеска на шесте у трассы
m.maybe("by_sign", 8, 12)
m.put("by_billboard0", 50, 11)

# ---- лагерь банды (юг): баррикады из машин, палатки по кругу у костра, бочки с огнём
m.paint("t", 20, 24, 48, 35)
for x, y, n in ((18, 22, "by_wreck0"), (22, 22, "by_wreck3"), (40, 22, "by_wreck5"), (46, 23, "by_wreck7")):
    m.maybe(n, x, y)
m.maybe("x_sandbags", 26, 22, check=False)
m.maybe("x_sandbags", 33, 22, check=False)
m.maybe("ar_spikes", 29, 22)
m.maybe("ar_spikes", 37, 22)
m.maybe(CAMPFIRE, 33, 29)
for x, y, n in ((26, 26, "r_tent_big"), (40, 26, "r_tent_yellow"), (25, 32, "r_tent_green"), (41, 32, "r_tent_orange"), (33, 34, "r_tent_beige")):
    m.maybe(n, x, y)
for x, y in ((29, 31), (37, 28), (30, 26), (36, 33)):
    m.maybe("x_fire_barrel", x, y)
for x, y in ((28, 29), (38, 30)):
    m.maybe("r_logs" if x % 2 else "barrel_wood", x, y)
m.maybe("pile_rags", 31, 27)
m.maybe("pile_bottles", 35, 27)
for x, y in ((22, 30), (44, 30), (22, 34), (44, 35)):
    m.maybe("pile_junk", x, y)
m.pickups += [["лом", 1, 30, 24], ["химикаты", 1, 24, 28], ["ткань", 1, 44, 28], ["патроны", 3, 38, 24]]
m.enemies += [["gang", 29, 24], ["gang", 38, 25], ["gang", 28, 31], ["gang", 39, 31], ["boss", 33, 32]]
m.scatter(["r_dry_bush", "r_rocks", "r_bones"], 1, 1, W - 2, H - 2, 26)
m.scatter(["r_trash", "pile_cans", "pile_scrap"], 1, 21, W - 2, H - 2, 12)
m.grow(1, 1, W - 2, H - 2, 12)

print("обжито:", m.dress_empty([
    [("r_tent_beige", 0, 0), ("pile_rags", 3, 1), ("barrel_wood", 0, 3)],
    [("r_car_wreck", 0, 0), ("pile_tires", 3, 2), ("r_trash", 0, 3)],
    [("r_pickup", 0, 0), ("r_barrels", 3, 0), ("pile_scrap", 2, 3)],
    [("r_dumpster", 0, 0), ("pile_cans", 2, 0), ("r_trash", 0, 2), ("crate_broken", 3, 2)],
    [("x_cross", 0, 0), ("x_grave", 0, 1), ("x_cross", 2, 0), ("x_grave", 2, 1), ("r_dtree_a", 4, 1)],
    [("r_billboard", 0, 0), ("r_dtree_a", 2, 1), ("r_bones", 3, 2), ("r_rocks", 4, 2)],
    [("r_shack", 0, 0), ("pile_junk", 5, 1), ("x_fire_barrel", 3, 3)],
], ground=("s", "t", "q"), block=7, margin=1, chance=0.95, max_uses=2))
# свет: навес — жёлтый, лагерь — костёр и огонь бочек (уже у объектов), лампы над въездом
LM.lamps(m, "warm", [(21, 9), (35, 9)])

city.save(gap_exempt=("boss",))
L = json.load(open("data/locations.json", encoding="utf-8"))
for k in ("containers", "terminals", "entry", "npcs"):
    L["station"].pop(k, None)
L["station"].update({"name": "Заправка «Последний шанс»", "known": False})
json.dump(L, open("data/locations.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
