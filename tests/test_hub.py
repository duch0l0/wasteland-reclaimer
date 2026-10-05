"""
Хаб (tools/build_hub.py) — без окна: оазис, базар, артель Веги, «Мальтийский сокол», Старый город, акведук.

  - по трассе на восток — двор старой школы, через дверь — здание; мисс Лейн и терминал директора;
  - люк в подвал деда закрыт, пока не прочитана записка в его терминале; в подвале — сундук и терминал;
  - люк в подвал салуна — после разговора с Мо; внизу Тесс.

    .venv/bin/python tests/test_fifteen.py
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


g.reveal_location("hub")
g.enter_location("hub")
fr(g)
ok(g.loc.id == "hub" and len(g.npcs) >= 10, "Хаб: оазис, базар, жители")
ok(any(g.level.is_wall(x, y) for x in range(35, 43) for y in range(15, 24)), "оазис — вода, не пройти")
for to in ("hub_falcon", "hub_water"):
    goto(g, sorted(portal(g, to)["tiles"])[0])
    ok(g.loc.id == to, f"вход: {g.loc.name}")
    g.dialogue.active_node = None
    goto(g, sorted(next(p for p in g.level.portals if p["to"] == "hub")["tiles"])[0])
    ok(g.loc.id == "hub", "обратно на площадь")
g.flags["know_baker"] = True
talk("dolores")
say("внук Эймоса")
say("раньше них")
ok(g.flags.get("dolores_trust"), "Долорес Вега — ветеран Марипозы — доверяет внуку Рида")
g.dialogue.active_node = None
goto(g, sorted(portal(g, "hub_old")["tiles"])[0])
ok(g.loc.id == "hub_old", "на юг — Старый город")
for e in g.enemies:
    e.hostile = False
goto(g, sorted(portal(g, "hub_tunnels")["tiles"])[0])
ok(g.loc.id == "hub_tunnels", "через люк — в старый акведук")
for e in g.enemies:
    e.alive = False
g.open_terminal("hub_sluice")
g.term_open_entry(1)
g.close_terminal()
g.open_terminal("hub_sluice")
g.term_open_entry(0)
g.close_terminal()
ok(g.flags.get("know_sluice"), "шлюз: культ по ночам уводит воду оазиса, чтобы Вега продала родник")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
