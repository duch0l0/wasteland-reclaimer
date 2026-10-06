"""
Остров Санта-Каталина (tools/build_catalina.py) — без окна: Авалон, который не знает о войне: «чума», дань «флоту»
(Анклаву), правда старейшины Моры, сигнал с маяка, лодка Джуда.

    .venv/bin/python tests/test_catalina.py
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

















g.flags["know_catalina"] = True
g.sync_story()
ok("catalina" in g.worldmap.known, "Анклав проговорился про остров — он на карте")
g.enter_location("catalina")
fr(g)
ok(g.loc.id == "catalina" and len(g.npcs) >= 8, "Авалон: пляж, причал, рыбный рынок, дома")
talk("quarantine_nurse")
say("Спасибо")
ok(g.flags.get("ct_cleared"), "карантин пройден: никакой чумы")
g.dialogue.active_node = None
goto(g, sorted(portal(g, "catalina_light")["tiles"])[0])
ok(g.loc.id == "catalina_light", "маяк")
g.open_terminal("catalina_radio")
g.term_open_entry(0)
g.term_open_entry(1)
g.close_terminal()
ok(g.flags.get("know_ct_lie") and g.flags.get("know_ct_tribute"), "радио 2077 года и эфир Анклава: «флот» — это Анклав")
goto(g, sorted(portal(g, "catalina")["tiles"])[0])
goto(g, sorted(portal(g, "catalina_casino")["tiles"])[0])
talk("elder_mora")
say("«Флот»")
say("Анклав")
say("маяка")
ok(g.flags.get("ct_tribute_stop_ask"), "Мора: ни одного ребёнка больше")
g.dialogue.active_node = None
goto(g, sorted(portal(g, "catalina")["tiles"])[0])
goto(g, sorted(portal(g, "catalina_light")["tiles"])[0])
talk("keeper_silas")
say("сигнал")
g.dialogue.active_node = None
g.open_terminal("catalina_radio")
idx = next(k for k, (_, e) in enumerate(g.term_entries()) if "чумы" in e.get("label", ""))
g.term_open_entry(idx)
g.close_terminal()
ok(g.flags.get("ct_tribute_stopped"), "сигнал «чума» — корабль Анклава больше не придёт за данью")
goto(g, sorted(portal(g, "catalina")["tiles"])[0])
goto(g, sorted(portal(g, "catalina_cove")["tiles"])[0])
ok(g.loc.id == "catalina_cove", "грот с обломками корабля")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
