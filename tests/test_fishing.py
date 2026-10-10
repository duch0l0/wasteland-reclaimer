"""
Рыбалка в Нидлсе (docs/city_plan.md, этап 2): удочка и наживка у Роуз, поклёвка, подсечка в зелёной зоне;
улов зависит от баржи (чистый или «светящийся» карп); бутылка с запиской — письмо мужа Кейт.

    .venv/bin/python tests/test_fishing.py
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



SHOTS = sys.argv[1] if len(sys.argv) > 1 else None


def strike_in_zone(g):
    for _ in range(600):
        g.update(16)
        f = g.fishing
        if f["state"] == "bite" and f["zone"][0] + 0.01 <= f["pos"] <= f["zone"][1] - 0.01:
            g.handle_key(pygame.K_SPACE)
            return
    raise AssertionError("поплавок так и не попал в зону")


g = Game(intro=False)
go(g, "needles")
talk(g, "fisher_joe"); say(g, "порыбачить")
opts = [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]
ok("Закидываю." not in opts, "без удочки и наживки не закинуть")
g.dialogue.active_node = None
g.inventory.add("удочка", 1)
g.inventory.add("наживка", 6)
talk(g, "fisher_joe"); say(g, "порыбачить"); say(g, "Закидываю")
ok(g.fishing and g.fishing["state"] == "wait" and g.inventory.count("наживка") == 5, "заброс: наживка ушла, поплавок качается")
g.handle_key(pygame.K_SPACE)
ok(g.fishing["state"] == "done" and "Рано" in g.fishing["msg"], "подсёк до поклёвки — рыба ушла")
g.handle_key(pygame.K_SPACE)
g.fishing["fish"] = "карп"
strike_in_zone(g)
ok(g.inventory.has("светящийся карп"), "баржа течёт — карп светится")
g.draw()
if SHOTS:
    pygame.image.save(g.screen, os.path.join(SHOTS, "fishing.png"))
g.flags["barge_done"] = True
g.handle_key(pygame.K_SPACE)
g.fishing["fish"] = "карп"
strike_in_zone(g)
ok(g.inventory.has("карп"), "баржа залита — чистый карп")
g.handle_key(pygame.K_SPACE)
g.fishing["fish"] = "бутылка с запиской"
strike_in_zone(g)
ok(g.inventory.has("бутылка с запиской"), "выловил бутылку с запиской")
g.handle_key(pygame.K_ESCAPE)
ok(g.fishing is None, "Esc — смотать удочку")
talk(g, "kate"); say(g, "бутылку"); say(g, "...")
ok(g.flags.get("kate_bottle"), "Кейт читает письмо Джека: «Упрямую Мэри» придумал он")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
