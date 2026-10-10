"""
Крючки к местам: житель, который рассказывает о месте, отмечает его на карте мира; у барменов и старожилов —
«Что интересного в округе?» с наводками на придорожные места.

    .venv/bin/python tests/test_hooks.py
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
go(g, "hub_falcon")
ok("spot_diner" not in g.worldmap.known and "spot_radio" not in g.worldmap.known, "закусочная и радиовышка ещё не на карте")
talk(g, "falcon_barkeep"); say(g, "в округе")
ok("spot_diner" in g.worldmap.known and "spot_radio" in g.worldmap.known, "Винни рассказал — обе на карте")
say(g, "Спасибо")
talk(g, "falcon_barkeep")
opts = [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]
ok(not any("в округе" in o for o in opts), "второй раз не спрашивается")
g.dialogue.active_node = None

go(g, "primm")
ok("nipton" not in g.worldmap.known, "Ниптон ещё не на карте")
talk(g, "pr_caravan_guard")
ok("nipton" in g.worldmap.known and "searchlight" in g.worldmap.known, "охранник каравана упомянул Ниптон и Сёрчлайт — на карте")
g.dialogue.active_node = None

hooks = [k for k, d in g.dialogue.trees.items() if "hook_places" in d.get("nodes", {})]
ok(len(hooks) >= 6, f"наводки у барменов и старожилов: {len(hooks)}")
from src.location import LOCATION_DEFS  # noqa: E402
bad = [(k, n, l) for k, d in g.dialogue.trees.items() for n, node in d["nodes"].items()
       for l in node.get("reveal", []) if l not in LOCATION_DEFS or not LOCATION_DEFS[l].get("world_pos")]
ok(not bad, f"все отмечаемые места есть на карте мира {bad[:3]}")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
