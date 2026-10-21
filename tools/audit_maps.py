"""
Аудит карт на логические и визуальные дефекты, которые не видны при расстановке по координатам:
  дверь     — предмет (шкаф, стеллаж, бочка, вывеска) стоит в проёме стены или прямо перед ним
  портал    — предмет рядом с порталом/выходом (ближе 2 клеток) мешает подойти
  лампа     — напольная лампа посреди тропы: ни одной стены в соседних клетках
  жилец     — житель/враг/ящик/терминал стоит в проёме
  вынос     — предмет стоит на клетке пустоты/стены
  зажат     — предмет, из-за которого сужается проход до 1 клетки в коридоре шире (бутылочное горлышко)
Запуск из папки game_project:  .venv/bin/python tools/audit_maps.py [карта …]
"""
import glob
import json
import os
import sys

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
    wall = lambda x, y: not (0 <= x < W and 0 <= y < H) or g[y][x] in walls
    water = set(map(tuple, d.get("blocked", [])))
    blocked_by = {}                                    # клетка -> имя предмета
    items = []
    for e in d["props"]:
        cells, block, layer = foot_cells(e[0], e[1], e[2])
        items.append((e[0], e[1], e[2], cells, block, layer))
        if block:
            for c in cells:
                blocked_by[c] = e[0]
    free = lambda c: not wall(*c) and c not in water
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
    near_door = set(door)
    for (x, y) in door:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            near_door.add((x + dx, y + dy))
    ports = [tuple(t) for p in d.get("portals", []) for t in p["tiles"]] + [tuple(t) for t in d.get("exits", [])]
    near_port = {(x + dx, y + dy) for x, y in [tuple(t) for p in d.get('portals', []) for t in p['tiles']] for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
    out = []
    seen = set()                                     # (имя, x, y) — один объект считается один раз, между категориями тоже
    mounted = set()                                  # предметы, весь фут которых лежит на стенах (настенный декор, не в проёме)
    for name, x, y, cells, block, layer in items:
        key = (name, x, y)
        if layer == "floor" or name.startswith(FLAT):
            if name.startswith(FLAT) and (x, y) in door and name.startswith(("x_vd_plaque", "x_vd_num", "x_vd_exit", "x_vd_map", "x_vd_sheet", "x_vd_tally", "x_vd_drawing")):
                out.append(("дверь", name, (x, y), "вывеска/декор висит в проёме"))
            continue
        if all(not (0 <= c[0] < W and 0 <= c[1] < H) or g[c[1]][c[0]] in ("x", "_") for c in cells) and not name.startswith(("x_cliff", "x_vault", "x_mesa", "vwall_", "wall_")):
            out.append(("вынос", name, (x, y), "целиком на пустоте"))
        if all(wall(*c) for c in cells):             # шкаф-встройка, вывеска, окно на стене — проёма тут нет
            mounted.add(key)
            continue
        if block and any(c in near_door for c in cells) and name not in ("x_door", "x_manhole", "x_ladder"):
            if not name.startswith(("vwall_", "wall_", "x_cliff", "x_vault_door", "x_vault_gear")) and key not in seen:
                seen.add(key)
                out.append(("дверь", name, (x, y), "предмет в проёме или перед ним"))
        if any(c in near_port for c in cells) and block and not name.startswith(("vwall_", "wall_", "x_cliff", "x_vault", "x_mesa", "x_ladder", "x_manhole", "x_door")) and key not in seen:
            seen.add(key)
            out.append(("портал", name, (x, y), "вплотную к порталу"))
        if name.startswith(LAMPS_FLOOR) and not name.startswith("x_fire_barrel") and not block:
            if not any(wall(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                out.append(("лампа", name, (x, y), "напольная лампа посреди прохода"))
    for key in ("npcs", "enemies"):
        for it in d.get(key, []):
            c = (it[1], it[2])
            if c in door and (it[0], c[0], c[1]) not in seen:
                seen.add((it[0], c[0], c[1]))
                out.append(("жилец", it[0], c, "стоит в проёме"))
    for t in d.get("containers", []) + d.get("terminals", []):
        pr = d["props"][t["prop"]]
        key = (pr[0], pr[1], pr[2])
        if (pr[1], pr[2]) in near_door and key not in seen and key not in mounted:
            seen.add(key)
            out.append(("жилец", pr[0], (pr[1], pr[2]), "ящик/терминал в проёме"))
    return mid, out


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
    for f in files:
        r = audit(f)
        if not r or not r[1]:
            continue
        mid, out = r
        total += len(out)
        print(f"\n== {mid}: {len(out)}")
        for kind, name, pos, why in out[:40]:
            print(f"   {kind:7s} {name:22s} {pos}  {why}")
    print(f"\nвсего: {total}")

