"""
Музей Сфинкса в Боунъярде (docs/city_plan.md, этап 2): находки из пустоши — в экспонаты, у каждой своя табличка;
три — премия, пять — звание попечителя и ключ от запасника; витрины появляются у музея.

    .venv/bin/python tests/test_museum.py
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


def talk(g, nid):
    g.dialogue.active_node = None
    npc = next(n for n in g.npcs if n.npc_id == nid)
    for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (-1, 1)):
        c = (tile_of(npc)[0] + dx, tile_of(npc)[1] + dy)
        if not g.level.is_wall(*c):
            g.player.rect.topleft = rect_pos_for_tile(g.player, c)
            break
    g.handle_key(pygame.K_e)
    assert g.dialogue.is_active(), nid


def say(g, part):
    opts = [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]
    idx = next((i for i, l in enumerate(opts) if part in l), None)
    assert idx is not None, f"нет реплики «{part}» среди {opts}"
    g.handle_key(pygame.K_1 + idx)
    fr(g, 1)


def go(g, lid):
    g.dialogue.active_node = None
    g.enter_location(lid)
    g.slides = None
    for e in g.enemies:
        e.alive = False
    fr(g)


def read(g, item):
    g.item_action(item)[1]()
    g.close_terminal()


def take(g, title):
    box = next(c for c in g.level.containers if c["name"] == title)
    for t in box["tiles"]:
        for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (-1, -1)):
            c = (t[0] + dx, t[1] + dy)
            if not g.level.is_wall(*c) and c not in box["tiles"]:
                g.player.rect.topleft = rect_pos_for_tile(g.player, c)
                g.handle_key(pygame.K_e)
                fr(g, 1)
                if g.loot:
                    g.handle_key(pygame.K_r)
                    g.loot = None
                return



g = Game(intro=False)
g.player.max_hp = g.player.hp = 500
go(g, "boneyard")
g.flags["sphinx_done"] = True
talk(g, "sphinx")
opts = [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]
ok(not any("экспонат" in o for o in opts), "без находок — нечего дарить")
g.dialogue.active_node = None
for it in ("амбра", "записка петунии", "инопланетная батарея", "свисток спасателя", "рисунок углём"):
    g.inventory.add(it, 1)
c0 = g.inventory.count("крышки")
talk(g, "sphinx"); say(g, "экспонат"); say(g, "Амбра"); say(g, "..."); say(g, "Бывай")
ok(g.flags.get("museum_count") == 1 and not g.inventory.has("амбра") and g.inventory.count("крышки") - c0 == 40,
   "амбра — экспонат «Море в пустыне», музейная премия 40")
fr(g)
statues = [o for o in g.level.objects if o.get("changed")]
ok(len(statues) == 1, "у музея появилась первая витрина")
for name in ("Записка петунии", "Инопланетная батарея"):
    talk(g, "sphinx"); say(g, "экспонат"); say(g, name); say(g, "..."); say(g, "Бывай")
talk(g, "sphinx"); say(g, "коллекция"); say(g, "Три экспоната"); say(g, "Спасибо")
ok(g.flags.get("museum_prize3") and g.inventory.count("стимулятор") >= 2, "три экспоната — набор юного натуралиста")
for name in ("Свисток спасателя", "Рисунок углём"):
    talk(g, "sphinx"); say(g, "экспонат"); say(g, name); say(g, "..."); say(g, "Бывай")
talk(g, "sphinx"); say(g, "коллекция"); say(g, "Пять экспонатов"); say(g, "Спасибо")
ok(g.flags.get("museum_key") and any(t[0] == "patron" for t in g.titles()), "пять экспонатов — попечитель музея")
take(g, "запасник музея")
ok(g.inventory.has("лазерная винтовка"), "запасник: «Оружие будущего» — лазерная винтовка")
go(g, "boneyard")
ok(len([o for o in g.level.objects if o.get("changed")]) >= 4, "у музея — витрины и табличка")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
