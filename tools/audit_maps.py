"""
Аудит карт на логические и визуальные дефекты, которые не видны при расстановке по координатам:
  дверь     — предмет (шкаф, стеллаж, бочка, вывеска) стоит в проёме стены или прямо перед ним (один флаг на проём)
  портал    — предмет реально отрезает портал: 0 свободных клеток подхода, клетка портала занята или
              без предмета портал связывается со стартом карты, а с ним — нет (BFS с/без предмета);
              ищется по всей карте, а не только у кольца портала: блокирующий проп, снятие которого
              соединяет портал со стартом (обрыв коридора, завал в проходе), — «отрезает портал от старта»
  лампа     — лампа стоит на клетке блокирующего пропа (наложение); лампы без стены в 8 соседях — счётчик «косметика»
  жилец     — житель/враг/ящик/терминал стоит в проёме
  вынос     — предмет стоит на клетке пустоты/стены
Геометрия стен: тайлы ground/стен + пропы-стены (wall_*, vwall_*, x_cliff*, roof_*); для «стены в 8 соседях»
и BFS дополнительно считаются футы блокирующих пропов.
Запуск из папки game_project:  .venv/bin/python tools/audit_maps.py [карта …]
"""
import glob
import json
import os
import sys
from collections import deque

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, ".")
import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))
from src import props as P  # noqa: E402

LAMPS_FLOOR = ("x_vd_stand_", "lantern_lit", "ct_torch", "x_fire_barrel", "x_vd_sparks")
FLAT = ("x_vd_wl_", "x_vd_plaque", "x_vd_num", "x_vd_fr_", "x_vd_exit", "x_vd_map", "x_vd_sheet", "x_vd_tally", "x_vd_drawing",
        "x_vd_nine", "x_vd_waterline", "x_vd_drip", "x_vd_hz_", "x_vd_cab_", "x_vd_wet", "x_vd_rust", "x_vd_oil", "x_vd_blood",
        "x_vd_steps", "x_vd_ruts", "x_vd_dragh", "x_vd_dragv", "x_vd_caps")
# свет-эффекты и настенный аварийный светильник — не лампы и не вывески: не аудируем вовсе
NOT_A_LAMP = ("x_vd_sparks",)
NOT_A_SIGN = ("x_vd_exitlight", "x_vd_exitlight_far")
# пропы-стены: реальная геометрия карт часто собрана из них, а не из тайлов ground
WALL_PROPS = ("wall_", "vwall_", "x_cliff", "roof_")
# входы-здания: сам портал внутри такого пропа — норма, а не «предмет у портала»
PORTAL_BUILDINGS = ("ar2_airlock", "p7_command", "r_bunker", "sl_bunker")
PORTAL_SKIP = ("vwall_", "wall_", "x_cliff", "x_vault", "x_mesa", "x_ladder", "x_manhole", "x_door")
# PORTAL_SKIP ниже используется как список префиксов; для аудита дверей есть отдельный точечный список:
# задуманные преграды-решётки, которые стоят в проёме по логике места (перекрывают устье стока/канала).
# Формат: (карта, проп, x, y) — как x_door/x_manhole/x_ladder, но не по всему проекту, а по одной клетке.
AUDIT_OK = {("drain", "bar_fence_a", 46, 12)}


def load(path):
    d = json.load(open(path, encoding="utf-8"))
    if d.get("iso") or "ground" not in d:
        return None
    return d


def foot_cells(name, x, y):
    try:
        inf = P.info(name)
    except Exception:
        return [], False, "obj"
    fw, fh = inf["foot"]
    return [(x + i, y + j) for i in range(fw) for j in range(fh)], bool(inf["block"]), inf.get("layer", "obj")


def audit(path):
    d = load(path)
    if d is None:
        return None
    mid = os.path.basename(path)[:-5]
    g = d["ground"]
    H, W = len(g), len(g[0])
    walls = set(d.get("walls", {})) | {"x", "_"}
    water = set(map(tuple, d.get("blocked", [])))
    props = []
    blocked_by = {}                                    # клетка -> имя блокирующего предмета
    wall_cells = set()                                 # футы пропов-стен (wall_*, vwall_*, x_cliff*, roof_*)
    for e in d["props"]:
        cells, block, layer = foot_cells(e[0], e[1], e[2])
        props.append((e[0], e[1], e[2], cells, block, layer))
        if block:
            for c in cells:
                blocked_by.setdefault(c, e[0])
        if e[0].startswith(WALL_PROPS):
            wall_cells.update(cells)
    outside = lambda c: not (0 <= c[0] < W and 0 <= c[1] < H)
    # стена — тайл ground/стен или проп-стена (структура карты); предметы-декор стеной не считаем,
    # иначе проп, стоящий в проёме, сам «замурует» проём и перестанет находиться
    wall = lambda x, y: not (0 <= x < W and 0 <= y < H) or g[y][x] in walls or (x, y) in wall_cells
    # сплошная преграда — стена или фут блокирующего пропа: по ней считается «стена в 8 соседях» и BFS
    solid = lambda x, y: wall(x, y) or (x, y) in blocked_by
    free = lambda c: not solid(*c) and c not in water
    cosmetics = 0                                      # лампы без стены в соседях: вид, а не дефект прохода
    # проёмы: клетка прохода сквозь стену (с двух сторон стена, вдоль — свободно)
    def run(x, y, dx, dy, cap=4):
        """Свободный пробег от клетки в направлении (dx, dy); обрезанный пробег возвращает cap+1 («длиннее»)."""
        n = 0
        while not wall(x + dx * (n + 1), y + dy * (n + 1)):
            n += 1
            if n > cap:
                break
        return n

    door = set()
    for y in range(H):
        for x in range(W):
            if wall(x, y):
                continue
            hl = run(x, y, -1, 0) + run(x, y, 1, 0) + 1
            vl = run(x, y, 0, -1) + run(x, y, 0, 1) + 1
            if hl <= 3 and 4 < vl <= 6:                  # короткий поперёк, длинный вдоль — проём; коридор/тоннель длиннее 6 — не проём
                door.add((x, y))
            elif vl <= 3 and 4 < hl <= 6:
                door.add((x, y))
    # склейка соседних клеток проёма в один проём: одна проблема = один флаг
    cluster = {}
    for c in door:
        if c in cluster:
            continue
        stack, cid = [c], len(cluster) + 1
        while stack:
            cur = stack.pop()
            if cur in cluster:
                continue
            cluster[cur] = cid
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nb = (cur[0] + dx, cur[1] + dy)
                if nb in door and nb not in cluster:
                    stack.append(nb)
    def clusters_of(cells):
        """Проёмы, которые предмет задевает сам или вплотную (4 стороны) — ключ дедупа «один флаг на проём»."""
        touched = set()
        for cx, cy in cells:
            if (cx, cy) in cluster:
                touched.add(cluster[(cx, cy)])
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if (cx + dx, cy + dy) in cluster:
                    touched.add(cluster[(cx + dx, cy + dy)])
        return touched
    near_door = set(door)
    for (x, y) in door:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            near_door.add((x + dx, y + dy))

    # кто «виновен» за проём: сначала предметы, стоящие в самом проёме, потом — прямо перед ним
    door_claim = {}
    for inside_pref in (True, False):
        for name, x, y, cells, block, layer in props:
            if not block or layer == "floor" or name in ("x_door", "x_manhole", "x_ladder") \
                    or (mid, name, x, y) in AUDIT_OK \
                    or name.startswith(("vwall_", "wall_", "x_cliff", "x_vault_door", "x_vault_gear")):
                continue
            if any(c in door for c in cells) != inside_pref:
                continue
            if all(wall(*c) for c in cells):        # настенный декор/встройка — не в проёме и не перед ним
                continue
            for cid in sorted(clusters_of(cells)):
                door_claim.setdefault(cid, (name, x, y))
    claim = set(door_claim.values())

    def reach(seeds, extra_free=()):
        """Связная область прохода от seeds по 4 направлениям; клетки extra_free считаются свободными."""
        seen = set(seeds)
        stack = list(seeds)
        while stack:
            cx, cy = stack.pop()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (cx + dx, cy + dy)
                if n in seen or outside(n) or n in water:
                    continue
                if n not in extra_free and not free(n):
                    continue
                seen.add(n)
                stack.append(n)
        return seen

    out = []
    seen = set()                                     # (имя, x, y) — один объект считается один раз, между категориями тоже
    mounted = set()                                  # предметы, весь фут которых лежит на стенах (настенный декор, не в проёме)
    for name, x, y, cells, block, layer in props:
        key = (name, x, y)
        if layer == "floor" or name.startswith(FLAT):
            if name.startswith(FLAT) and not name.startswith(NOT_A_SIGN) and (x, y) in door and name.startswith(("x_vd_plaque", "x_vd_num", "x_vd_exit", "x_vd_map", "x_vd_sheet", "x_vd_tally", "x_vd_drawing")):
                out.append(("дверь", name, (x, y), "вывеска/декор висит в проёме"))
            continue
        if all(not (0 <= c[0] < W and 0 <= c[1] < H) or g[c[1]][c[0]] in ("x", "_") for c in cells) and not name.startswith(("x_cliff", "x_vault", "x_mesa", "vwall_", "wall_")):
            out.append(("вынос", name, (x, y), "целиком на пустоте"))
        if name.startswith(LAMPS_FLOOR) and not name.startswith(("x_fire_barrel",) + NOT_A_LAMP) and not block:
            if any(c in blocked_by for c in cells):      # лампа и блокирующий проп в одной клетке — наложение
                if key not in seen:
                    seen.add(key)
                    out.append(("лампа", name, (x, y), f"лампа на клетке пропа {blocked_by[(x, y)]}"))
            elif not any(solid(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                cosmetics += 1                           # ни стены/пропа в 8 соседях: флаг не дефект, только счётчик
            continue
        if all(wall(*c) for c in cells):             # шкаф-встройка, вывеска, окно на стене — проёма тут нет
            mounted.add(key)
            continue
        if block and key in claim and key not in seen:   # один флаг на проём: победил предмет в самом проёме
            seen.add(key)
            out.append(("дверь", name, (x, y), "предмет в проёме или перед ним"))
    # порталы: важен не факт «предмет рядом», а реально ли он отрезает подход
    player_cell = tuple(d["player"])
    anchors = [player_cell] + [tuple(t) for t in d.get("exits", [])]
    anchors = [a for a in anchors if not outside(a) and free(a)]
    linked = reach(anchors) if anchors else set()    # куда реально дойти от старта игрока/выходов карты
    pseen = set()                                    # предметы, уже названные виновниками по порталу

    def portal_flag(name, x, y, why):
        if (name, x, y) in pseen:
            return
        pseen.add((name, x, y))
        seen.add((name, x, y))
        out.append(("портал", name, (x, y), why))

    # «отрезал» ищем по всей карте, а не только у кольца портала: блокирующий проп, который задевает
    # достижимую область и граничит с проходимой клеткой вне неё. Проп в глубине недостижимой зоны
    # снятие не меняет — он отбрасывается, поэтому BFS считается на единицы пропов, а не на все
    def ground_field(seeds):
        """Расстояние по земле от портала без учёта пропов: отсекает пропы «сбоку от цели», оставляя
        только те, что реально стоят на пути к порталу (в т.ч. в глубине недостижимой зоны)."""
        dist = {c: 0 for c in seeds if not outside(c)}
        dq = deque(dist)
        while dq:
            cx, cy = dq.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (cx + dx, cy + dy)
                if n in dist or outside(n) or n in water or wall(*n):
                    continue
                dist[n] = dist[(cx, cy)] + 1
                dq.append(n)
        return dist

    alt_cache = {}

    def alt_reach(name, x, y, cells):
        """BFS «без предмета»: считается один раз на предмет, сколько бы порталов он ни резал."""
        key = (name, x, y)
        if key not in alt_cache:
            alt_cache[key] = reach(anchors, extra_free=set(cells))
        return alt_cache[key]

    def cut_chain(target):
        """Наращиваем достижимость от старта, снимая блокирующие пропы с границы. Возвращает цепочку
        виновников: длина 1 — один предмет отрезал, больше — завал подряд. Пусто — отрезано не пропами
        (стены/геометрия), это не дефект пропа. Жадно и с лимитом шагов: без экспоненты."""
        freed = set()
        chain = []
        cur = linked
        for _ in range(8):                           # завал длиннее 8 предметов — уже не «проп в проходе»
            if target & cur:
                return chain
            # уже пройденная клетка недостижима, если её нельзя обойти по земле без учёта пропов:
            # считаем поле расстояний от портала один раз и берём только пропы «по пути» к нему
            frontier = []
            for name, x, y, cells, block, layer in props:
                if not block or layer == "floor" or name in PORTAL_BUILDINGS or name.startswith(PORTAL_SKIP):
                    continue
                if any(c[0] == name and c[1] == (x, y) for c in chain):
                    continue
                touch_in = touch_out = False
                for cx, cy in cells:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        n = (cx + dx, cy + dy)
                        if outside(n) or n in water:
                            continue
                        if n in cur:
                            touch_in = True
                        elif not wall(*n) and ground_dist.get(n, -1) >= 0:
                            touch_out = True
                if touch_in and touch_out:
                    frontier.append((name, x, y, cells))
            if not frontier:
                return chain                        # граница пуста: пробивать нечем
            if len(frontier) > 60:                  # страховка от карт с тысячами пропов: берём ближайшие к порталу
                frontier.sort(key=lambda c: min((ground_dist.get((cx + dx, cy + dy), 10 ** 9)
                                                 for cx, cy in c[3]
                                                 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))), default=10 ** 9))
                frontier = frontier[:60]
            best = None
            for cand in frontier:
                r = reach(anchors, extra_free=freed | set(cand[3]))
                near = min((ground_dist.get((cx + dx, cy + dy), 10 ** 9)
                            for cx, cy in cand[3]
                            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))), default=10 ** 9)
                score = (len(r), -near)              # больше открылось — лучше; при равенстве — ближе к порталу
                if best is None or score > best[2]:
                    best = (cand, r, score)
            if best is None or len(best[1]) <= len(cur):
                return chain                        # дальше не пробиться: дело не в пропах
            chain.append((best[0][0], (best[0][1], best[0][2])))
            freed |= set(best[0][3])
            cur = best[1]
        return chain if target & cur else []        # 8 шагов не хватило — не завал, а геометрия

    for p in d.get("portals", []):
        ptiles = {tuple(t) for t in p["tiles"]}
        ring = {(px + dx, py + dy) for px, py in ptiles for dx in (-1, 0, 1) for dy in (-1, 0, 1)} - ptiles
        ring = {c for c in ring if not outside(c)}
        approach = [c for c in ring if free(c)]
        cands = []
        for name, x, y, cells, block, layer in props:
            if not block or layer == "floor" or name in PORTAL_BUILDINGS or name.startswith(PORTAL_SKIP):
                continue
            if any(c in ring or c in ptiles for c in cells):
                cands.append((name, x, y, cells))
        # клетка портала занята — флаг независимо от связности: даже с подходом войти некуда
        for name, x, y, cells in cands:
            if any(c in ptiles for c in cells):
                portal_flag(name, x, y, "клетка портала занята предметом")
        if not approach and cands:                   # кольцо занято целиком: виновник — проп в кольце
            name, x, y, cells = max(cands, key=lambda c: sum(1 for cc in c[3] if cc in ring))
            portal_flag(name, x, y, "нет свободных клеток подхода к порталу")
            continue
        if not anchors or (set(approach) & linked):
            continue                                 # подход к порталу от старта есть
        target = set(approach) | set(ptiles)
        ground_dist = ground_field(target)
        # 1) виновники у самого портала (текст со счётчиками клеток)
        for name, x, y, cells in cands:
            if (name, x, y) in pseen:
                continue
            alt = alt_reach(name, x, y, cells)       # BFS «без предмета»
            if target & alt:
                portal_flag(name, x, y, f"предмет отрезает портал ({len(reach(approach))} свободных клеток подхода против {len(alt)} со старта карты)")
        # 2) любой блокирующий проп на карте: без него портал достижим, с ним — нет
        chain = cut_chain(target)
        for name, pos in chain:
            why = "отрезает портал от старта" if len(chain) == 1 \
                else f"отрезает портал от старта (завал из {len(chain)} предметов подряд)"
            portal_flag(name, pos[0], pos[1], why)
    for key in ("npcs", "enemies"):
        for it in d.get(key, []):
            c = (it[1], it[2])
            if c in door and (it[0], c[0], c[1]) not in seen:
                hit = clusters_of([c])
                if hit & set(door_claim):
                    continue
                seen.add((it[0], c[0], c[1]))
                out.append(("жилец", it[0], c, "стоит в проёме"))
    for t in d.get("containers", []) + d.get("terminals", []):
        pr = d["props"][t["prop"]]
        key = (pr[0], pr[1], pr[2])
        if (pr[1], pr[2]) in near_door and key not in seen and key not in mounted:
            hit = clusters_of(foot_cells(pr[0], pr[1], pr[2])[0]) or clusters_of([(pr[1], pr[2])])
            if hit & set(door_claim):
                continue
            seen.add(key)
            out.append(("жилец", pr[0], (pr[1], pr[2]), "ящик/терминал в проёме"))
    return mid, out, cosmetics


def overlaps(path):
    """Предметы, спрайты которых заметно налезают друг на друга (стопка из двух), и спрайты, торчащие за край карты."""
    d = load(path)
    if d is None:
        return None
    mid = os.path.basename(path)[:-5]
    T = 48
    W, H = d["w"], d["h"]
    rects = []
    for e in d["props"]:
        try:
            inf = P.info(e[0])
        except Exception:
            continue
        if inf.get("layer") == "floor" or e[0].startswith(FLAT) or not inf["block"]:
            continue
        w, h = inf["size"]
        fw, fh = inf["foot"]
        x = e[1] * T + (e[3] if len(e) > 3 else 0)
        y = (e[2] + fh) * T - h + (e[4] if len(e) > 4 else 0)
        rects.append((e[0], pygame.Rect(x, y, w, h), (e[1], e[2])))
    out = []
    for i in range(len(rects)):
        n1, r1, p1 = rects[i]
        if r1.right > W * T + 12 or r1.left < -12:
            out.append(("край", n1, p1, "спрайт выходит за край карты"))
        for j in range(i + 1, len(rects)):
            n2, r2, p2 = rects[j]
            if p1 == p2:
                continue
            ov = r1.clip(r2)
            if ov.w <= 0 or ov.h <= 0:
                continue
            small = min(r1.w * r1.h, r2.w * r2.h)
            if small and ov.w * ov.h / small > 0.55 and not n1.startswith(("x_cliff", "vwall_", "wall_")) and not n2.startswith(("x_cliff", "vwall_", "wall_")):
                out.append(("стопка", f"{n1} + {n2}", p1, f"спрайты накладываются на {int(100 * ov.w * ov.h / small)}%"))
    return mid, out


def run_overlaps(files):
    total = 0
    for f in files:
        r = overlaps(f)
        if not r or not r[1]:
            continue
        mid, out = r
        total += len(out)
        print(f"\n== {mid}: {len(out)}")
        for kind, name, pos, why in out[:25]:
            print(f"   {kind:7s} {name:44s} {pos}  {why}")
    print(f"\nвсего наложений: {total}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--overlaps"]
    files = args or sorted(glob.glob("data/maps/*.json"))
    files = [f if f.endswith(".json") else f"data/maps/{f}.json" for f in files]
    if "--overlaps" in sys.argv:
        run_overlaps(files)
        sys.exit(0)
    total = 0
    cos_total = 0
    shown = 0
    for f in files:
        r = audit(f)
        if r is None:
            continue
        mid, out, cos = r
        cos_total += cos
        shown += 1
        if not out:
            continue
        total += len(out)
        print(f"\n== {mid}: {len(out)}")
        for kind, name, pos, why in out[:40]:
            print(f"   {kind:7s} {name:22s} {pos}  {why}")
    print(f"\nвсего: {total}")
    print(f"карт проверено: {shown}, косметика (лампы без стены в 8 соседях, не дефект): {cos_total}")

