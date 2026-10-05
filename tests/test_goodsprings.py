"""
Гудспрингс (tools/build_goodsprings.py) — без окна: «Колокол и мальчик» — мальчик-беглец из культа,
голоса Создателя, решение посёлка, брат-ловчий у ворот.

    .venv/bin/python tests/test_goodsprings.py
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










g.enter_location("primm")
fr(g)
g.sync_story()
ok("goodsprings" in g.worldmap.known, "после Примма на карте — Гудспрингс")
g.enter_location("goodsprings")
fr(g)
ok(g.loc.id == "goodsprings" and len(g.npcs) >= 7, "Гудспрингс: улица, площадь с колодцем, кладбище")
for to in ("goodsprings_doc", "goodsprings_cave"):
    goto(g, sorted(portal(g, to)["tiles"])[0])
    ok(g.loc.id == to, f"вход: {g.loc.name}")
    for e in g.enemies:
        e.alive = False
    g.dialogue.active_node = None
    goto(g, sorted(next(p for p in g.level.portals if p["to"] == "goodsprings")["tiles"])[0])

# мальчик в салуне: голоса Создателя — наводка на Ниптон
goto(g, sorted(portal(g, "goodsprings_saloon")["tiles"])[0])
talk("ezekiel")
say("голоса")
say("Тише")
ok(g.flags.get("know_nipton_lottery") and g.flags.get("know_brother_t_nipton"), "голоса: брат Т. в Ниптоне, лотерея")

# док советует вести мальчика к лечению — уводим, брат-ловчий уходит ни с чем
g.dialogue.active_node = None
g.flags["know_shaw_serum"] = True
goto(g, sorted(portal(g, "goodsprings")["tiles"])[0])
goto(g, sorted(portal(g, "goodsprings_doc")["tiles"])[0])
talk("doc_mitchell")
say("ВРЭ")
say("Поведу")
g.dialogue.active_node = None
goto(g, sorted(portal(g, "goodsprings")["tiles"])[0])
goto(g, sorted(portal(g, "goodsprings_saloon")["tiles"])[0])
talk("ezekiel")
say("Пойдём")
say("Договорились")
ok(g.flags.get("ezekiel_with_hero") and not any(n.npc_id == "ezekiel" for n in g.npcs), "Иезекииль уходит с героем")
g.dialogue.active_node = None
goto(g, sorted(portal(g, "goodsprings")["tiles"])[0])
talk("cult_hunter")
say("ушёл")
ok(g.flags.get("gs_decided") and not g.flags.get("ezekiel_to_cult"), "брат-ловчий уходит ни с чем — посёлок цел")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
