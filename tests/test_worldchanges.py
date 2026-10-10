"""
Город меняется на глазах (docs/city_plan.md, этап 1): для каждого изменения в data/world_changes.json —
до решения объектов нет, после — стоят, не в проходе, путь не отрезан, доски читаются.

    .venv/bin/python tests/test_worldchanges.py
"""
import os
import sys
import tempfile

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import pygame  # noqa: E402

pygame.mouse.get_pos = lambda: (-50, -50)
pygame.mouse.get_focused = lambda: True

from src.game import Game, saveload  # noqa: E402
from src.combat import tile_of, rect_pos_for_tile  # noqa: E402

saveload.SAVE_DIR = tempfile.mkdtemp()
failed = []


def ok(cond, msg):
    print(("OK   " if cond else "FAIL ") + msg)
    if not cond:
        failed.append(msg)


def fr(g, n=3):
    for _ in range(n):
        g.update(16)
        g.draw()
        while g.perk_choices:
            g.handle_key(pygame.K_1)


import json  # noqa: E402
from collections import deque  # noqa: E402

CH = {k: v for k, v in json.load(open("data/world_changes.json", encoding="utf-8")).items() if not k.startswith("_")}
SHOTS = sys.argv[1] if len(sys.argv) > 1 else None


def reach(level, start):
    seen, q = {start}, deque([start])
    while q:
        x, y = q.popleft()
        for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if n not in seen and not level.is_wall(*n):
                seen.add(n)
                q.append(n)
    return seen


def satisfy(g, cond):
    if "flag" in cond:
        g.flags[cond["flag"]] = True
    if "flags_any" in cond:
        g.flags[cond["flags_any"][0]] = True
    if "flag_ge" in cond:
        g.flags[cond["flag_ge"][0]] = cond["flag_ge"][1]


total = 0
for lid, changes in CH.items():
    for ch in changes:
        g = Game(intro=False)
        g.enter_location(lid)
        g.slides = None
        before = len([o for o in g.level.objects if o.get("changed")])
        ok(before == 0, f"{lid}: до решения ничего не изменилось")
        start = tile_of(g.player)
        r0 = reach(g.level, start)
        targets = [t for p in g.level.portals for t in p["tiles"]] + list(g.level.exits)
        satisfy(g, ch["if"])
        g.enter_location(lid)
        g.slides = None
        fr(g, 1)
        added = [o for o in g.level.objects if o.get("changed")]
        want = sum(len(c.get("add", [])) for c in changes if g.check_condition(c.get("if", {})))   # условия «не меньше N» накапливаются
        ok(len(added) == want, f"{lid} [{ch['if']}]: поставлено {len(added)} из {want}")
        r1 = reach(g.level, tile_of(g.player))
        cut = [t for t in targets if t in r0 and t not in r1]
        ok(not cut, f"{lid}: путь к выходам и порталам не отрезан {cut[:3]}")
        docs = [a["doc"] for a in ch.get("add", []) if a.get("doc")]
        for d in docs:
            ok(any(t["id"] == "doc:" + d for t in g.level.terminals), f"{lid}: доска «{d}» читается")
        g.enter_location(lid)
        ok(len([o for o in g.level.objects if o.get("changed")]) == want, f"{lid}: при повторном входе не дублируется")
        if SHOTS and added:
            o = added[0]
            g.player.rect.topleft = rect_pos_for_tile(g.player, (o["foot"][0][0], o["foot"][0][1] + 2))
            fr(g, 2)
            pygame.image.save(g.screen, os.path.join(SHOTS, f"wc_{lid}_{total}.png"))
        total += 1

print(f"\nизменений проверено: {total}")
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
