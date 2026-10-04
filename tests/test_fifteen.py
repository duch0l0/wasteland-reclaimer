"""
Пятнадцатая, новые районы и уровни (tools/build_fifteen.py) — без окна.

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
for e in g.enemies:
    e.hostile = False

# ------------------------------------------------------------ школа
goto(g, sorted(portal(g, "fifteen_school")["tiles"])[0])
ok(g.loc.id == "fifteen_school", "по трассе на восток — двор старой школы")
for e in g.enemies:
    e.hostile = False
goto(g, sorted(portal(g, "fifteen_school_in")["tiles"])[0])
ok(g.loc.id == "fifteen_school_in", "через дверь — в здание школы")
ok(any(n.npc_id == "miss_lane" for n in g.npcs) and sum(n.npc_id.startswith("ghoul_kid") for n in g.npcs) == 3,
   "в спортзале мисс Лейн и трое детей")
lane = next(n for n in g.npcs if n.npc_id == "miss_lane")
stand_near(g, tile_of(lane))
g.handle_key(pygame.K_e)
ok(g.dialogue.is_active(), "с мисс Лейн можно поговорить")
g.dialogue.active_node = None
t = next(t for t in g.level.terminals if t["id"] == "school_office")
stand_near(g, t["tiles"][0])
g.handle_key(pygame.K_e)
ok(g.term and g.term["id"] == "school_office", "терминал директора открывается")
g.close_terminal()
goto(g, sorted(portal(g, "fifteen_school")["tiles"])[0])
goto(g, sorted(portal(g, "ruins")["tiles"])[0])
ok(g.loc.id == "ruins", "обратно — в Пятнадцатую")

# ------------------------------------------------------------ подвал деда
hatch = portal(g, "fifteen_cellar")
goto(g, sorted(hatch["tiles"])[0])
ok(g.loc.id == "ruins", "люк в подвал без записки не открывается")
g.open_terminal("grandpa")
entries = g.term_entries()
g.term_open_entry(next(i for i, (_, e) in enumerate(entries) if "Записка" in e["label"]))
g.close_terminal()
ok(g.flags.get("cellar_found"), "записка деда: как открыть погреб")
goto(g, (8, 18))
goto(g, sorted(hatch["tiles"])[0])
ok(g.loc.id == "fifteen_cellar", "по записке — в подвал деда")
box = next(c for c in g.level.containers if c["name"] == "армейский сундук деда")
ok("армейский бронежилет" in box["loot"], "в сундуке — армейский бронежилет")
goto(g, sorted(portal(g, "ruins")["tiles"])[0])
ok(g.loc.id == "ruins", "по лестнице — наверх в дом")

# ------------------------------------------------------------ подвал салуна
hatch = portal(g, "fifteen_saloon_cellar")
goto(g, sorted(hatch["tiles"])[0])
ok(g.loc.id == "ruins", "люк в подвал салуна закрыт")
g.flags["mo_cellar"] = True
goto(g, (21, 18))
goto(g, sorted(hatch["tiles"])[0])
ok(g.loc.id == "fifteen_saloon_cellar" and any(n.npc_id == "tess" for n in g.npcs), "в подвале салуна — Тесс")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
