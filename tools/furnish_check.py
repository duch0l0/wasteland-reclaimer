"""
Проверка расстановки по замечаниям автора (24.10) — то, что раньше находил он, а не я:
  * «на чём стоит»: мелочь на столешнице (6-й элемент пропа) стоит не на столе/полке/тумбе — на терминале,
    стуле, ящике;
  * «лицом в стену»: мебель, которая ставится спиной к стене (верстак, стеллаж, шкаф, прилавок), стоит так,
    что стена у неё спереди (снизу), а сзади пусто;
  * «масштаб»: высота картинки в клетках выходит за рамки, которые предмет имеет в жизни рядом с героем
    (рост героя — 1,67 клетки).
Это подсказка, а не приёмка: после неё всё равно смотрю каждую комнату глазами.

  .venv/bin/python tools/furnish_check.py ruins fifteen_school station …
"""
import json
import os
import re
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))
from src import props, settings as S  # noqa: E402

T = S.TILE
# на что можно ставить мелочь
SURFACE = re.compile(r"table|desk|counter|bench|workbench|nightstand|stand|shelf|rack|cabinet|dresser|bar\b|"
                     r"barrel|crate|filecab|locker|sideboard|cupboard|stove|fridge|freezer|cooler|piano|chest|"
                     r"box|stash|tanks|safe|lab|vb_|cl_|counter|scales")   # x_scales — прилавок с чашечными весами
NOT_SURFACE = re.compile(r"terminal|chair|stool|sofa|armchair|bed|bunk|door|ladder|lamp|lantern")
# ставится спиной к стене
WALL_BACK = re.compile(r"workbench|bookcase|bookshelf|shelf|rack|locker|cabinet|cupboard|dresser|wardrobe|"
                       r"fridge|freezer|cooler|toolboard|vending|bottle_shelf|liquor")
# высота в клетках: (шаблон, мин, макс)
HEIGHT = [(r"extinguish|fireext", 0.3, 0.75), (r"lantern(?!_post)", 0.25, 0.8), (r"jerrycan|canister", 0.3, 0.8),
          (r"register", 0.3, 0.9), (r"\bradio\b|_radio", 0.25, 0.9), (r"stool", 0.4, 1.0), (r"bucket", 0.2, 0.7),
          (r"medbox|medkit", 0.2, 0.7), (r"backpack", 0.3, 0.8), (r"phone(?!_booth)", 0.3, 2.0),
          (r"_car\d|car_|wreck|taxi|sedan", 1.3, 3.5), (r"truck|pickup|humvee|camper|^ws_bus$|_bus\b", 1.8, 4.5),
          (r"door", 1.4, 2.6)]


def walls_of(d):
    codes = {"x", "_"} | set(d.get("walls", {}))
    out = {(x, y) for y, row in enumerate(d["ground"]) for x, c in enumerate(row) if c in codes}
    for o in d["props"]:                                  # в городах стены зданий — предметы wall_* / vwall_*
        if o[0].startswith(("wall_", "vwall_")) and o[0] in props.CATALOG:
            fw, fh = props.info(o[0])["foot"]
            out |= {(o[1] + i, o[2] + j) for i in range(fw) for j in range(fh)}
    return out


def check(loc):
    d = json.load(open(f"data/maps/{loc}.json", encoding="utf-8"))
    walls = walls_of(d)
    term_idx = {t["prop"] for t in d.get("terminals", [])}
    cells = {}                                            # клетка -> [(индекс, имя)] мебели на полу
    for i, o in enumerate(d["props"]):
        n, x, y = o[0], o[1], o[2]
        if len(o) > 5:
            continue
        try:
            fw, fh = props.info(n)["foot"]
        except Exception:
            fw, fh = 1, 1
        for dx in range(fw):
            for dy in range(fh):
                cells.setdefault((x + dx, y + dy), []).append((i, n))
    out = []
    for i, o in enumerate(d["props"]):
        n, x, y = o[0], o[1], o[2]
        if n not in props.CATALOG:
            continue
        if len(o) > 5:                                    # мелочь на столешнице
            under = [(j, m) for j, m in cells.get((x, y), []) if m != n]
            bad = [m for j, m in under if j in term_idx or NOT_SURFACE.search(m)]
            ok = [m for j, m in under if j not in term_idx and SURFACE.search(m) and not NOT_SURFACE.search(m)]
            if bad or not ok:
                out.append(("на чём стоит", n, x, y, "под ним: " + (", ".join(m for _, m in under) or "пол")))
            continue
        info = props.info(n)
        fw, fh = info["foot"]
        h = info["size"][1] / T
        if WALL_BACK.search(n) and not info.get("layer") == "floor":
            front = all((x + k, y + fh) in walls for k in range(fw))
            back = any((x + k, y - 1) in walls for k in range(fw))
            if front and not back:
                out.append(("лицом в стену", n, x, y, "стена спереди, сзади пусто"))
        for pat, lo, hi in HEIGHT:
            if re.search(pat, n):
                if not lo <= h <= hi:
                    out.append(("масштаб", n, x, y, f"высота {h:.2f} кл., в жизни {lo}–{hi}"))
                break
    return out


if __name__ == "__main__":
    total = 0
    for loc in sys.argv[1:]:
        res = check(loc)
        total += len(res)
        print(f"== {loc}: {len(res)}")
        for kind, n, x, y, why in res:
            print(f"   {kind:14} {n:24} ({x}, {y})  {why}")
    print("всего:", total)
