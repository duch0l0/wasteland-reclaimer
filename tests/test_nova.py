"""
«Нова» (tools/build_nova.py) — без окна: город под куполом: индекс чистоты, Нижний ярус «отсеянных», Рэйвен,
ядро ИИ НОВА и её судьба.

    .venv/bin/python tests/test_nova.py
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
        while g.perk_choices:          # новый уровень за квесты — выбрать первое
            g.handle_key(pygame.K_1)


def goto(g, t):
    g.player.rect.topleft = rect_pos_for_tile(g.player, t)
    g.snap_camera()
    fr(g)


def portal(g, to):
    return next(p for p in g.level.portals if p["to"] == to)


def stand_near(g, t):
    for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (-1, 1)):
        c = (t[0] + dx, t[1] + dy)
        if not g.level.is_wall(*c):
            g.player.rect.topleft = rect_pos_for_tile(g.player, c)
            g.snap_camera()
            return


g = Game(intro=False)
g.player.max_hp = g.player.hp = 10 ** 6


def say(part):
    opts = [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]
    idx = next((i for i, l in enumerate(opts) if part in l), None)
    assert idx is not None, f"нет реплики «{part}» среди {opts}"
    g.handle_key(pygame.K_1 + idx)
    fr(g, 1)


def talk(nid):
    g.dialogue.active_node = None
    npc = next(n for n in g.npcs if n.npc_id == nid)
    stand_near(g, tile_of(npc))
    g.handle_key(pygame.K_e)
    assert g.dialogue.is_active(), nid


















g.flags["know_nova"] = True
g.sync_story()
ok("nova" in g.worldmap.known, "слух на Стрипе — купол «Нова» на карте")
g.enter_location("nova")
fr(g)
talk("purity_officer")
say("переработка")
say("...")
ok(g.flags.get("know_nova_processing"), "санпропускник: индекс чистоты, «переработка» ниже 40")
g.dialogue.active_node = None
goto(g, sorted(portal(g, "nova_under")["tiles"])[0])
ok(g.loc.id == "nova_under", "служебный лифт — Нижний ярус, неоновое дно")
goto(g, sorted(portal(g, "nova_core")["tiles"])[0])
ok(g.loc.id == "nova_under", "решётка ядра под током")
talk("raven_hacker")
say("Что такое НОВА")
say("остановить")
say("Пойду")
ok(g.flags.get("nova_rebels_ally") and g.inventory.has("червь Рэйвен"), "Рэйвен: НОВА хочет ВРЭ — червь для «отбора»")
g.dialogue.active_node = None
goto(g, sorted(portal(g, "nova_core")["tiles"])[0])
ok(g.loc.id == "nova_core", "ядро НОВЫ")
for e in g.enemies:
    e.alive = False
g.open_terminal("nova_core")
idx = next(k for k, (_, e) in enumerate(g.term_entries()) if "Червь" in e.get("label", ""))
g.term_open_entry(idx)
g.close_terminal()
ok(g.flags.get("nova_selection_off") and g.flags.get("nova_decided"), "«отбор» отключён — воздух и вода остались")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
