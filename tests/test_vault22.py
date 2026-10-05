"""
Убежище 22 (tools/build_vault22.py) — без окна: «Сад будущего»: Хьюго Ли, споры на нижней ферме, выбор —
отдать ВРЭ, сжечь ферму или молчать.

    .venv/bin/python tests/test_vault22.py
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











g.enter_location("goodsprings")
fr(g)
g.sync_story()
ok("vault22" in g.worldmap.known, "после Гудспрингса на карте — Убежище 22")
g.enter_location("vault22")
fr(g)
goto(g, sorted(portal(g, "vault22_living")["tiles"])[0])
ok(g.loc.id == "vault22_living", "жилой ярус Убежища 22")
g.open_terminal("v22_overseer")
g.term_open_entry(0)
g.close_terminal()
goto(g, sorted(portal(g, "vault22_garden")["tiles"])[0])
ok(g.loc.id == "vault22_garden", "оранжереи")
goto(g, sorted(portal(g, "vault22_lab")["tiles"])[0])
ok(g.loc.id == "vault22_garden", "люк в лабораторию закрыт")
g.open_terminal("v22_greenhouse")
g.term_open_entry(1)
g.close_terminal()
g.flags["know_v22_spores"] = True     # пароль смотрителя «ТЛЯ» — взломом; здесь — сразу правда

# смотритель признаётся и даёт сжечь ферму
goto(g, sorted(portal(g, "vault22_living")["tiles"])[0])
talk("overseer_keene")
say("пестицид")
say("сожжём")
say("...")
ok(g.flags.get("v22_lab_ok") and g.flags.get("v22_burn_ok"), "Кин призналась: споры — их пестицид Б-12")
g.dialogue.active_node = None
goto(g, sorted(portal(g, "vault22_garden")["tiles"])[0])
goto(g, sorted(portal(g, "vault22_lab")["tiles"])[0])
ok(g.loc.id == "vault22_lab", "лаборатория и грибная ферма")
for e in g.enemies:
    e.alive = False

# Хьюго Ли едет с героем — ради Сэм
goto(g, sorted(portal(g, "vault22_garden")["tiles"])[0])
goto(g, sorted(portal(g, "vault22_living")["tiles"])[0])
g.flags["dolores_trust"] = True
talk("hugo_lee")
say("Рядовой Ли")
say("споры")
say("Вместе")
ok(g.flags.get("hugo_joins"), "Хьюго Ли — пятый из Списка — готов отдать сетчатку для «Ноля»")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
