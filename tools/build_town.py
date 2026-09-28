"""
Генератор большой карты города (data/maps/town.json) из объектов набора «wasteland town».

Районы (96×64 клетки):
  запад       — въезд с трассы, автобусная остановка, отсюда начинается игра;
  северо-запад — жилой квартал: разрушенные дома, дворы с заборами и мебелью;
  центр-север — рынок на гравийной площади: палатки, прилавки, лавка Гены;
  северо-восток — водокачка за сеткой: баки, бочки, светящиеся мутанты, Блонди;
  юго-запад   — развалины квартала, логово крысолюдов с вожаком;
  юг-центр    — высохший сквер: скамейки, мёртвые деревья, панцирный жук;
  юго-восток  — свалка: покрышки, хлам, лагерь рейдеров, лачуга Панка-одиночки;
  через весь город — асфальтовая улица с тротуарами, выходы на запад и на юг.

Каждый загораживающий объект ставится, только если после него все места,
куда можно было дойти, остаются достижимыми — карта не запирает проходы.
Случайность фиксирована (SEED), так что карта каждый раз одна и та же.

Запуск из папки game_project:  .venv/bin/python tools/build_town.py
"""
import json
import os
import random
import sys
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import props as P  # noqa: E402

SEED = 7
W, H = 96, 64
T = 48
START = (3, 31)
rnd = random.Random(SEED)

ground = [["d"] * W for _ in range(H)]
props = []          # [имя, x, y]
decals = []         # [имя, px, py]
containers = []     # {"prop": i, "name", "loot", "owner"}
blocked = set()     # занятые загораживающими объектами клетки
soft = set()        # клетки с незагораживающим декором (чтобы не громоздить)
reserved = set()    # дороги и проходы: сюда не ставим ничего загораживающего
enemies, npcs, pickups = [], [], []
exits = [(0, y) for y in range(30, 34)] + [(x, H - 1) for x in range(44, 48)]


# ------------------------------------------------------------ помощники
def paint(code, x0, y0, x1, y1):
    for y in range(max(0, y0), min(H, y1 + 1)):
        for x in range(max(0, x0), min(W, x1 + 1)):
            ground[y][x] = code


def reserve(x0, y0, x1, y1):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            reserved.add((x, y))


def footprint(name, x, y):
    fw, fh = P.info(name)["foot"]
    return [(x + i, y + j) for i in range(fw) for j in range(fh)]


def reachable_count(extra_blocked=()):
    seen = {START}
    q = deque([START])
    bad = blocked | set(extra_blocked)
    while q:
        cx, cy = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (cx + dx, cy + dy)
            if 0 <= n[0] < W and 0 <= n[1] < H and n not in seen and n not in bad:
                seen.add(n)
                q.append(n)
    return len(seen), seen


_reach = [None]


def put(name, x, y, check=True, allow_reserved=False, search_owner=None, force=False):
    """Поставить объект; False — не влез или перекрыл бы проход.
    force — без проверок (угловой кусок боковой стены поверх фасада)."""
    inf = P.info(name)
    foot = footprint(name, x, y)
    if force:
        props.append([name, x, y])
        if inf["block"]:
            blocked.update(foot)
            _reach[0] = None
        return True
    if any(not (1 <= fx < W - 1 and 1 <= fy < H - 1) for fx, fy in foot):
        return False
    if name in OUTDOOR and any(ground[fy][fx] == "c" for fx, fy in foot):
        return False  # трава, кусты, знаки и камни — только снаружи зданий
    if inf["block"]:
        if any(t in blocked for t in foot):
            return False
        if not allow_reserved and any(t in reserved for t in foot):
            return False
        if check:
            if _reach[0] is None:
                _reach[0] = reachable_count()[0]
            n, _ = reachable_count(foot)
            if n < _reach[0] - len([t for t in foot if t not in blocked]):
                return False  # отрезал бы кусок карты
        blocked.update(foot)
        _reach[0] = None
    else:
        if any(t in soft or t in blocked for t in foot):
            return False
        soft.update(foot)
    props.append([name, x, y])
    if inf.get("search"):
        containers.append({"prop": len(props) - 1, "name": inf.get("title", "ящик"),
                           "loot": roll_loot(inf["search"]), "owner": search_owner})
    return True


def roll_loot(table):
    loot = {}
    for item, (lo, hi, chance) in P.LOOT_TABLES[table].items():
        if rnd.randint(1, 100) <= chance:
            loot[item] = rnd.randint(lo, hi)
    return loot


def scatter(names, x0, y0, x1, y1, n, tries=40):
    placed = 0
    for _ in range(n * tries):
        if placed >= n:
            break
        if put(rnd.choice(names), rnd.randint(x0, x1), rnd.randint(y0, y1)):
            placed += 1
    return placed


def decal(names, x0, y0, x1, y1, n):
    for _ in range(n):
        x, y = rnd.randint(x0, x1), rnd.randint(y0, y1)
        if ground[y][x] == "c":
            continue  # пятна земли — не на полу зданий
        decals.append([rnd.choice(names), x * T + rnd.randint(8, 40), y * T + rnd.randint(8, 40)])


def hwall(names, x0, x1, y, gaps=()):
    """Ряд стен/заборов по строке y от x0 до x1, с проходами в клетках gaps."""
    x = x0
    while x <= x1:
        if x in gaps:
            x += 1
            continue
        name = rnd.choice(names)
        fw = P.info(name)["foot"][0]
        if x + fw - 1 > x1 or any(g in range(x, x + fw) for g in gaps) or not put(name, x, y, check=False):
            x += 1
            continue
        x += fw


def vline(names, x, y0, y1, gaps=()):
    """Столбик однoклеточных объектов (бочки, ящики, столбы) — вертикальная граница."""
    for y in range(y0, y1 + 1):
        if y not in gaps:
            put(rnd.choice(names), x, y, check=False)


# стили зданий: целые фасады для северной стены (по ширине в клетках),
# для южной — вперемешку целые и обветшалые; боковые стены — vwall_<стиль>_w/e
WALLS_INTACT = {
    "brick": {4: ["wall_brick_long"], 2: ["wall_concrete_brick"]},
    "concrete": {2: ["wall_concrete", "wall_concrete_brick"]},
    "metal": {2: ["wall_metal", "wall_metal2", "wall_corrugated"]},
    "planks": {2: ["wall_planks", "wall_planks_blue", "wall_planks_dark"]},
}
WALLS_WORN = {
    "brick": {4: ["wall_brick_long", "wall_brick_crumble"], 2: ["wall_concrete_brick"]},
    "concrete": {4: ["wall_grey_broken"], 2: ["wall_concrete", "wall_concrete_broken", "wall_concrete_broken2"]},
    "metal": {2: ["wall_metal", "wall_metal2", "wall_corrugated", "wall_corrugated2", "wall_corrugated_rust"]},
    "planks": {2: ["wall_planks", "wall_planks_blue", "wall_planks_dark", "wall_corrugated_small"]},
}


def wall_row(pieces, x0, x1, y, gaps=()):
    """Сплошной ряд фасадов от x0 до x1 по строке y, кроме клеток-проёмов gaps.
    Отрезки между проёмами должны быть чётной длины (фасады — по 2 и 4 клетки)."""
    x = x0
    while x <= x1:
        if x in gaps:
            x += 1
            continue
        end = x
        while end + 1 <= x1 and end + 1 not in gaps:
            end += 1
        left = end - x + 1
        while left > 0:
            w = 4 if left >= 4 and 4 in pieces and rnd.random() < 0.6 else 2
            if w not in pieces or left < w:
                w = 2
            put(rnd.choice(pieces[w]), x, y, check=False, allow_reserved=True)
            x += w
            left -= w
        x = end + 1


def side_wall(style, side, x, y0, y1, gaps=()):
    """Отдельно стоящая стена с севера на юг (ограда) от y0 до y1, с проходами gaps."""
    for y in range(y0, y1 + 1):
        if y not in gaps:
            put(f"vwall_{style}_{side}", x, y, check=False, allow_reserved=True)


def building(x0, y0, w, h, style, south=(), west=(), east=()):
    """Здание со всеми стенами: северная — целая, южная — с проёмами дверей
    (south: смещения от x0, чётные, проём 2 клетки), боковые — с проёмами в
    строках west/east (смещения от y0). Пол бетонный. w — чётное.
    Возвращает внутренность (x0, y0, x1, y1) для обстановки."""
    assert w % 2 == 0, "ширина здания — чётная (фасады по 2 клетки)"
    x1, y1 = x0 + w - 1, y0 + h - 1
    paint("c", x0, y0 + 1, x1, y1)
    wall_row(WALLS_INTACT[style], x0, x1, y0)
    doors = set()
    for off in south:
        assert off % 2 == 0, "дверь на южной стене — с чётного смещения"
        doors.update((x0 + off, x0 + off + 1))
    wall_row(WALLS_WORN[style], x0, x1, y1, gaps=doors)
    for side, x, gaps in (("w", x0, west), ("e", x1, east)):
        put(f"vwall_{style}_{side}", x, y0, force=True, allow_reserved=True)  # угол: верх стены над фасадом
        for y in range(y0 + 1, y1):
            if y - y0 not in gaps:
                put(f"vwall_{style}_{side}", x, y, check=False, allow_reserved=True)
    return (x0 + 1, y0 + 1, x1 - 1, y1 - 1)


BARRELS = [f"barrel_{i}" for i in (0, 1, 2, 3, 4, 5, 9, 10, 11, 12, 13, 18)]
CRATES = ["crate", "crate_b", "crate_small", "cardboard", "crate_empty", "crate_open", "crate_broken"]
GRASS = [f"grass_{i}" for i in (5, 6, 10, 13, 18, 26, 28, 29, 35, 36, 53, 54, 65, 66, 68, 78, 80)]
BUSHES = ["bush_11", "bush_37", "bush_79", "grass_big"]
STONES = ["stones_12", "stones_19", "stones_21", "stones_62", "stones_63", "clods_67", "clods_81"]
FLOOR_BITS = ["bricks_a", "brick_b", "bricks_c", "brick_d", "bricks_e", "concrete_bit", "concrete_bit_b",
              "concrete_bits", "plank_floor", "log", "rebar_bits", "cloth_bit", "cloth_bit_b", "sock", "rag", "bits"]
# только пятна с рваными краями: квадратные куски (cobble, dirt_slabs, dirt_planks,
# metal_sheet) выглядят вырезанными и вставленными — их на карту не кладём
DIRT_DECALS = ["dirt_patch"]
JUNK_PILES = ["pile_cans", "pile_tires", "pile_scrap", "pile_electronics", "pile_bottles", "pile_tech_tire",
              "pile_barrel_junk", "pile_tires_pc", "pile_junk", "pile_bottles_b", "pile_tires_cans",
              "pile_appliances", "pile_computers", "pile_electronics_b", "pile_sink_junk"]
CLOTH_PILES = ["pile_rags", "pile_cloth", "pile_cloth_bottle", "pile_cloth_b", "pile_clothes", "pile_bags",
               "pile_cloth_scrap"] + [f"clothes_{i}" for i in (55, 56, 72, 73, 74, 75, 76, 77, 78)]
RUBBLE = ["rubble_a", "rubble_b", "brick_pile_a", "brick_pile_b", "concrete_block", "cinder_a", "cinder_b",
          "cinder_c", "rubble_heap", "rubble_rebar", "rebar_fence", "plank_block", "planks", "metal_sheets_b"]
FURNITURE = ["table_1", "table_2", "table_3", "table_4", "table_5", "chair_wood", "chair_b", "chair_c", "chair_1",
             "chair_2", "chair_3", "sofa", "sofa_corner", "bed", "bed_frame", "table_upside", "stool_1", "stool_2",
             "armchair", "nightstand", "cabinet_small", "wardrobe", "wardrobe_junk", "shelf_goods", "table_chair"]
LOCKERS = ["locker_1", "locker_2", "locker_3", "locker_4", "filecab_1", "filecab_2", "filecab_3", "locker_double"]
POLES = [f"pole_{i}" for i in (8, 9, 17, 25, 38, 49, 51, 52, 76, 77)]
SIGNS = ["sign_stop"] + [f"sign_{i}" for i in (43, 44, 50, 70, 71, 72, 73, 74)]
OUTDOOR = set(GRASS + BUSHES + POLES + SIGNS + STONES + ["rock_grass", "rock_grass_b", "dead_tree", "lamp_post"])
SEATS = [f"seat_{i}" for i in (14, 15, 22, 23, 32, 33, 39, 40, 46, 47)]
BENCHES = [f"bench_{i}" for i in (7, 16, 24, 34, 48)]


# ------------------------------------------------------------ кто и что где (резервируется до расстановки)
pickups.append(["самопал", 1, 27, 7])           # тайник с самопалом во дворе развалин
pickups.append(["патроны", 3, 25, 6])
pickups.append(["лом", 1, 9, 20])
pickups.append(["ткань", 1, 19, 10])
enemies.append(["rad_mutant", 11, 11])
npcs.append(["gena", 44, 22])
npcs.append(["blondie", 88, 4])
enemies += [["rad_mutant", 68, 16], ["rad_mutant", 77, 19]]
pickups.append(["химикаты", 1, 72, 13])
enemies += [["ratman", 12, 52], ["ratman", 16, 56], ["ratman", 8, 57], ["ratman_boss", 13, 59]]
pickups.append(["лом", 1, 30, 52])
pickups.append(["патроны", 3, 5, 43])
enemies.append(["beetle", 54, 46])
npcs.append(["loner", 63, 59])
enemies += [["raider", 85, 45], ["raider", 87, 54]]
pickups.append(["химикаты", 1, 76, 58])
for _, x, y in enemies + npcs:
    reserve(x, y, x, y)
for *_, x, y in pickups:
    reserve(x, y, x, y)


# ------------------------------------------------------------ дороги
paint("a", 0, 30, W - 1, 33)                    # главная улица
for x in range(0, W, 4):
    ground[31][x] = ground[31][x + 1] = "h"    # прерывистая разметка
paint("g", 0, 29, W - 1, 29)                    # тротуары
paint("g", 0, 34, W - 1, 34)
paint("a", 44, 34, 47, H - 1)                   # улица на юг
for y in range(36, H, 4):
    ground[y][45] = ground[y + 1][45] = "v"
paint("g", 43, 35, 43, H - 1)
paint("g", 48, 35, 48, H - 1)
paint("g", 36, 16, 56, 28)                      # рыночная площадь
paint("a", 70, 22, 72, 28)                      # подъезд к водокачке
paint("g", 60, 35, 62, 40)                      # въезд на свалку
reserve(0, 29, W - 1, 35)
reserve(43, 34, 48, H - 1)
reserve(70, 22, 72, 28)
reserve(0, 26, 8, 36)                           # площадка у въезда — старт


# ------------------------------------------------------------ запад: въезд и остановка
put("bench_7", 3, 27, allow_reserved=True, check=False)
put("sign_stop", 6, 27, allow_reserved=True, check=False)
put("seat_22", 1, 27, allow_reserved=True, check=False)
put("sign_72", 2, 36, allow_reserved=True, check=False)
put("lamp_post", 9, 28, allow_reserved=True, check=False)
for x in range(18, W - 4, 12):                  # фонари вдоль улицы
    put("lamp_post", x, 28, allow_reserved=True)
    put("lamp_post", x + 6, 35, allow_reserved=True)


# ------------------------------------------------------------ северо-запад: жилой квартал
houses = [("house_a", 4, 3), ("house_b", 14, 3), ("ruin_facade_a", 24, 3), ("ruin_facade_b", 4, 15),
          ("house_a", 16, 15), ("house_b", 28, 15)]
yard_fences = ["fence_picket", "fence_picket2", "fence_broken", "plank_fence_b", "post_fence_a"]
for name, hx, hy in houses:
    put(name, hx, hy, check=False)
    hwall(yard_fences, hx - 1, hx + 6, hy + 8, gaps=(hx + 2, hx + 3))
    scatter(FURNITURE, hx - 1, hy + 2, hx + 5, hy + 6, 2)
    if rnd.random() < 0.4:
        scatter(CLOTH_PILES + JUNK_PILES[:4], hx - 1, hy + 2, hx + 5, hy + 6, 1)
    scatter(GRASS, hx - 2, hy + 2, hx + 6, hy + 7, 5)
put("locker_2", 26, 7)
ix0, iy0, ix1, iy1 = building(32, 1, 10, 9, "brick", south=(4,))      # склад
scatter(LOCKERS + ["shelf_goods", "metal_shelf", "shelf_stuff_1"], ix0, iy0, ix1, iy0, 4)
scatter(CRATES + ["ammo_box", "toolbox_blue", "pile_scrap"], ix0, iy0 + 2, ix1, iy1, 3)
scatter(BARRELS + CRATES, 1, 1, 40, 26, 4)
scatter(JUNK_PILES + CLOTH_PILES, 1, 1, 40, 26, 3)


# ------------------------------------------------------------ рынок
put("shelter_a", 43, 18, check=False)           # лавка Гены
put("counter", 43, 20, check=False)
put("display_case_b", 45, 20, check=False)
put("barrel_wood", 42, 20)
put("crate_small", 47, 18)
put("lantern_lit", 46, 22)
stalls = [("shelter_b", 37, 18), ("shelter_a", 50, 18), ("shelter_b", 37, 24), ("shelter_a", 50, 24)]
for name, sx, sy in stalls:
    put(name, sx, sy)
    scatter(["table_1", "table_4", "table_7", "display_case_a", "display_case_c", "counter", "table_8"],
            sx - 1, sy + 1, sx + 3, sy + 2, 1)
put("tent_green", 36, 14)
put("tent_blue", 52, 13)
put("tent_round_tan", 40, 13)
put("shack_a", 55, 19)                          # лачуга, за ней — заначка Гены
put("metal_chest", 56, 17, search_owner="gena")
containers[-1].update({"name": "заначка Гены", "loot": {"крышки": 45, "тоник": 1, "патроны": 8}})
scatter(BARRELS + CRATES + ["firewood", "round_table_42", "stool_round_41", "chair_0", "chair_4"],
        35, 15, 57, 28, 8)
scatter(["lantern", "candles", "backpack"], 35, 15, 57, 28, 3)


# ------------------------------------------------------------ северо-восток: водокачка
hwall(["chain_a", "chain_b", "chain_c", "chain_d", "chain_e", "chain_broken_a", "chain_broken_d"],
      60, 94, 24, gaps=(70, 71, 72))
side_wall("metal", "e", 59, 2, 23, gaps=(11, 12))                     # западная ограда водокачки
put("water_tank_a", 64, 5, check=False)
put("water_tank_b", 74, 5, check=False)
put("water_tank_a", 86, 7, check=False)         # за этим баком прячется Блонди
ix0, iy0, ix1, iy1 = building(81, 13, 12, 8, "metal", south=(4,), west=(4,))  # контора водокачки
scatter(LOCKERS + ["filecab_1", "filecab_4"], ix0, iy0, ix1, iy0, 4)
scatter(["table_2", "table_6", "chair_wood", "chair_1", "toolbox_open_b"], ix0, iy0 + 2, ix1, iy1, 3)
put("shelter_b", 61, 14)
for x in (64, 65, 66, 67):
    put(rnd.choice(LOCKERS), x, 10)
scatter(BARRELS, 62, 12, 80, 22, 7)
scatter(["tool_rack", "metal_sheets", "toolbox_red", "ammo_box", "canister"], 61, 12, 80, 22, 4)


# ------------------------------------------------------------ юго-запад: развалины и логово крысолюдов
ix0, iy0, ix1, iy1 = building(3, 37, 16, 8, "brick", south=(4, 10))   # жилой дом без крыши
scatter(["wardrobe", "shelf_goods", "cabinet_small", "nightstand"], ix0, iy0, ix1, iy0, 3)
scatter(["table_1", "table_chair", "sofa", "bed", "chair_wood", "armchair"], ix0, iy0 + 2, ix1, iy1, 4)
put("ruin_facade_a", 22, 37, check=False)
put("ruin_facade_b", 30, 37, check=False)
building(2, 48, 22, 14, "concrete", south=(8,), east=(6,))            # большой склад — логово крысолюдов
ix0, iy0, ix1, iy1 = building(28, 50, 10, 9, "planks", south=(4,), west=(4,))  # мастерская
scatter(["tool_rack", "shelf_stuff_5", "shelf_stuff_2"], ix0, iy0, ix1, iy0, 3)
scatter(["toolbox_red", "toolbox_blue", "table_3", "canister"], ix0, iy0 + 2, ix1, iy1, 3)
ix0, iy0, ix1, iy1 = building(33, 40, 8, 7, "concrete", south=(2,))    # лавка у дороги
scatter(["shelf_goods", "shelf_stuff_4"], ix0, iy0, ix1, iy0, 2)
scatter(["display_case_a", "counter", "cardboard"], ix0, iy0 + 2, ix1, iy1, 2)
scatter(RUBBLE, 1, 39, 42, 62, 8)
# логово: гнёзда из тряпья, старые кровати
for name, x, y in [("bed_frame", 9, 54), ("sofa_frame", 17, 53), ("pile_rags", 12, 57), ("clothes_74", 6, 58),
                   ("clothes_76", 18, 59), ("pile_bags", 14, 51)]:
    put(name, x, y)
scatter(JUNK_PILES + CLOTH_PILES, 3, 49, 22, 60, 3)


# ------------------------------------------------------------ сквер
for x, y in [(50, 38), (54, 41), (51, 45), (55, 48)]:
    put("dead_tree", x, y)
for x, y in [(49, 40), (53, 44), (50, 48)]:
    put(rnd.choice(BENCHES), x, y)
scatter(["round_table_45", "round_table_58", "stool_round_55", "stool_round_56", "stone_table", "rock_grass",
         "rock_grass_b"], 49, 37, 58, 50, 6)
scatter(GRASS + BUSHES, 49, 36, 58, 52, 30)


# ------------------------------------------------------------ юго-восток: свалка
hwall(["wall_corrugated", "wall_corrugated2", "wall_metal", "wall_metal2", "wall_corrugated_rust",
       "corrugated_panel", "corrugated_b"], 60, 94, 37, gaps=(60, 61, 62))
side_wall("metal", "e", 59, 38, 62, gaps=(45, 46, 58))                # западная ограда свалки
put("shack_b", 62, 56, check=False)             # лачуга Панка
ix0, iy0, ix1, iy1 = building(66, 40, 12, 8, "metal", south=(4,), west=(3,))  # контора свалки
scatter(LOCKERS + ["filecab_2"], ix0, iy0, ix1, iy0, 3)
scatter(["table_5", "chair_2", "sofa", "cardboard"], ix0, iy0 + 2, ix1, iy1, 3)
ix0, iy0, ix1, iy1 = building(78, 55, 10, 6, "planks", south=(4,))     # сторожка
scatter(["bed", "chair_3", "table_4", "locker_3"], ix0, iy0, ix1, iy1, 3)
scatter(JUNK_PILES, 63, 39, 93, 62, 18)
scatter(SEATS + ["metal_sheets", "barrel_lying_a"], 64, 39, 93, 62, 4)
for name, x, y in [("tent_green", 84, 41), ("tent_tan", 88, 49), ("firewood", 86, 46), ("ammo_box", 90, 45),
                   ("crate", 83, 46), ("crate_b", 91, 53)]:
    put(name, x, y)


# ------------------------------------------------------------ по всему городу
for _ in range(40):                                                    # трава растёт куртинами
    cx, cy = rnd.randint(2, W - 3), rnd.randint(2, H - 3)
    scatter(GRASS + BUSHES[:2], cx - 3, cy - 2, cx + 3, cy + 2, rnd.randint(3, 7), tries=8)
scatter(GRASS, 1, 1, W - 2, H - 2, 220)
scatter(BUSHES, 1, 1, W - 2, H - 2, 30)
scatter(POLES + SIGNS, 1, 1, W - 2, H - 2, 6)
scatter(STONES + FLOOR_BITS[:5], 1, 1, W - 2, H - 2, 45)
scatter(["rock_grass", "rock_grass_b", "barrel_0", "barrel_9"], 1, 1, W - 2, H - 2, 8)
decal(DIRT_DECALS, 1, 1, W - 2, H - 2, 70)
scatter(RUBBLE, 1, 1, W - 2, 3, 3)                                     # по краям — немного завалов
scatter(RUBBLE, 1, H - 4, W - 2, H - 2, 3)


# ------------------------------------------------------------ проверки
_, reach = reachable_count()
for kind, x, y in enemies + [[n, x, y] for n, x, y in npcs]:
    assert (x, y) in reach and (x, y) not in blocked, f"{kind} в недоступной клетке {x, y}"
for item, _, x, y in pickups:
    assert (x, y) in reach, f"{item} недоступен {x, y}"
for c in containers:
    foot = footprint(*props[c["prop"]])
    assert any((fx + dx, fy + dy) in reach for fx, fy in foot for dx in (-1, 0, 1) for dy in (-1, 0, 1)), \
        f"к {c['name']} не подойти"
for t in exits:
    assert t in reach, f"выход {t} недоступен"
for kind, ex, ey in enemies:
    for nid, nx, ny in npcs:
        assert max(abs(ex - nx), abs(ey - ny)) >= 6, f"{kind} слишком близко к {nid}"

out = {"w": W, "h": H, "player": list(START), "exits": [list(t) for t in exits],
       "ground": ["".join(r) for r in ground], "decals": decals, "props": props, "containers": containers,
       "enemies": enemies, "npcs": npcs, "pickups": pickups}
with open("data/maps/town.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
print(f"город {W}×{H}: объектов {len(props)}, пятен {len(decals)}, обыскиваемых {len(containers)}, "
      f"врагов {len(enemies)}, NPC {len(npcs)}, предметов {len(pickups)}; доступно клеток {len(reach)}")
