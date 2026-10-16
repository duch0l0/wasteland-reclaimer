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
    door = set()
    for y in range(H):
        for x in range(W):
            if wall(x, y):
                continue
            x0 = x
            while not wall(x0 - 1, y):
                x0 -= 1
                if x - x0 > 3:
                    break
            x1 = x
            while not wall(x1 + 1, y):
                x1 += 1
                if x1 - x > 3:
                    break
            hl = x1 - x0 + 1
            y0 = y
            while not wall(x, y0 - 1):
                y0 -= 1
                if y - y0 > 3:
                    break
            y1 = y
            while not wall(x, y1 + 1):
                y1 += 1
                if y1 - y > 3:
                    break
            vl = y1 - y0 + 1
            if hl <= 3 and vl > 4:                       # короткий поперёк, длинный вдоль — проём или узкий коридор
                door.add((x, y))
            elif vl <= 3 and hl > 4:
                door.add((x, y))
    near_door = set(door)
    for (x, y) in door:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            near_door.add((x + dx, y + dy))
    ports = [tuple(t) for p in d.get("portals", []) for t in p["tiles"]] + [tuple(t) for t in d.get("exits", [])]
    near_port = {(x + dx, y + dy) for x, y in [tuple(t) for p in d.get('portals', []) for t in p['tiles']] for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
    out = []
    seen = set()
    for name, x, y, cells, block, layer in items:
        if layer == "floor" or name.startswith(FLAT):
            if name.startswith(FLAT) and (x, y) in door and name.startswith(("x_vd_plaque", "x_vd_num", "x_vd_exit", "x_vd_map", "x_vd_sheet", "x_vd_tally", "x_vd_drawing")):
                out.append(("дверь", name, (x, y), "вывеска/декор висит в проёме"))
            continue
        if all(not (0 <= c[0] < W and 0 <= c[1] < H) or g[c[1]][c[0]] in ("x", "_") for c in cells) and not name.startswith(("x_cliff", "x_vault", "x_mesa", "vwall_", "wall_")):
            out.append(("вынос", name, (x, y), "целиком на пустоте"))
        if block and any(c in near_door for c in cells) and name not in ("x_door", "x_manhole", "x_ladder"):
            if not name.startswith(("vwall_", "wall_", "x_cliff", "x_vault_door", "x_vault_gear")) and (name, x, y) not in seen:
                seen.add((name, x, y))
                out.append(("дверь", name, (x, y), "предмет в проёме или перед ним"))
        if any(c in near_port for c in cells) and block and not name.startswith(("vwall_", "wall_", "x_cliff", "x_vault", "x_mesa", "x_ladder", "x_manhole", "x_door")):
            out.append(("портал", name, (x, y), "вплотную к порталу"))
        if name.startswith(LAMPS_FLOOR) and not name.startswith("x_fire_barrel") and not block:
            if not any(wall(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                out.append(("лампа", name, (x, y), "напольная лампа посреди прохода"))
    for key in ("npcs", "enemies"):
        for it in d.get(key, []):
            c = (it[1], it[2])
            if c in door:
                out.append(("жилец", it[0], c, "стоит в проёме"))
    for t in d.get("containers", []) + d.get("terminals", []):
        pr = d["props"][t["prop"]]
        if (pr[1], pr[2]) in near_door:
            out.append(("жилец", pr[0], (pr[1], pr[2]), "ящик/терминал в проёме"))
    return mid, out


if __name__ == "__main__":
    files = sys.argv[1:] or sorted(glob.glob("data/maps/*.json"))
    files = [f if f.endswith(".json") else f"data/maps/{f}.json" for f in files]
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
