"""
Лагерь Арадеша (tools/build_aradesh.py) — без окна: лагерь переселенцев из Убежища 15, дом собраний, каньон
со сгоревшим фургоном культа и стоянкой Ханов, пещера радскорпионов с подземным родником.

    .venv/bin/python tests/test_aradesh.py
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





g.enter_location("necropolis")
fr(g)
g.sync_story()
ok("aradesh" in g.worldmap.known, "после Некрополя на карте — лагерь Арадеша")
g.enter_location("aradesh")
fr(g)
ok(g.loc.id == "aradesh" and len(g.npcs) >= 9, "лагерь: палатки, поле, колодец, жители")
goto(g, sorted(portal(g, "aradesh_hall")["tiles"])[0])
ok(g.loc.id == "aradesh_hall", "вход: дом собраний")
g.dialogue.active_node = None
goto(g, sorted(portal(g, "aradesh")["tiles"])[0])
talk("aradesh")
say("колодцем")
say("очищу")
say("Найду")
ok(g.flags.get("aradesh_job"), "Арадеш просит очистить пещеру с родником")

# каньон: фургон культа, Ханы
g.dialogue.active_node = None
goto(g, sorted(portal(g, "aradesh_canyon")["tiles"])[0])
ok(g.loc.id == "aradesh_canyon", "на восток — каньон")
for e in g.enemies:
    e.alive = False
g.open_terminal("convoy_wreck")
g.term_open_entry(0)
g.term_open_entry(1)
g.close_terminal()
ok(g.flags.get("know_convoy_cargo") and g.flags.get("know_enclave_hint"), "фургон: груз ВРЭ, огни в небе — первый след Анклава")
talk("khan_chief")
say("фургона")
say("Понятно")
ok(True, "Хан Тагар рассказал про людей в чёрной броне")

# пещера: перебить радскорпионов — родник свободен
g.dialogue.active_node = None
goto(g, sorted(portal(g, "aradesh_cave")["tiles"])[0])
ok(g.loc.id == "aradesh_cave", "вход в пещеру радскорпионов")
ok(any(e.type_id == "radscorpion_queen" for e in g.enemies), "в пещере — матка радскорпионов")
for e in g.enemies:
    e.alive = False
g._check_cleared()          # в игре проверка идёт после каждого убийства
fr(g)
ok(g.flags.get("aradesh_spring_cleared"), "пещера чиста — родник свободен")
goto(g, sorted(portal(g, "aradesh_canyon")["tiles"])[0])
goto(g, sorted(portal(g, "aradesh")["tiles"])[0])
talk("aradesh")
say("Родник")
say("родит")
ok(g.flags.get("aradesh_free_water"), "колодец ожил — культу здесь больше нечего предложить")
g.dialogue.active_node = None
talk("settler_kai")
say("не вода")
say("Правильно")
ok(g.flags.get("kai_stays"), "Кай остаётся в лагере")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
