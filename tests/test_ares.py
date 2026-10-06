"""
«Арес» (tools/build_ares.py) — без окна: полигон REPCONN и ракета «Гелиос», марсианская станция: экипаж, «Проект Арес»,
криоблок, два контейнера ВРЭ.

    .venv/bin/python tests/test_ares.py
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



















g.enter_location("repconn")
fr(g)
for e in g.enemies:
    e.alive = False
goto(g, sorted(portal(g, "ares")["tiles"])[0])
ok(g.loc.id == "repconn", "без топлива и курса ракета не летит")
g.inventory.add("изолента", 3)
g.inventory.add("пружина", 1)
talk("repconn_ghoul")
say("взлететь")
say("Держи")
ok(g.flags.get("antenna_up"), "гуль-техник поднимает антенну")
g.dialogue.active_node = None


def press(tid, part):
    g.open_terminal(tid)
    idx = next(k for k, (_, e) in enumerate(g.term_entries()) if part in e.get("label", ""))
    g.term_open_entry(idx)
    g.close_terminal()


for part in ("Заправить", "сигнал", "Подготовить"):
    press("repconn_launch", part)
ok(g.flags.get("rocket_ready"), "«Гелиос» заправлен, курс на «Арес»")
goto(g, sorted(portal(g, "ares")["tiles"])[0])
ok(g.loc.id == "ares" and g.level.night, "Марс: красное небо")
goto(g, sorted(portal(g, "ares_hab")["tiles"])[0])
ok(g.loc.id == "ares_hab", "шлюз — жилой модуль")
talk("cmdr_hale")
say("Проект Арес")
say("ВРЭ здесь")
say("Америки нет")
ok(g.flags.get("know_ares_vre") and g.flags.get("hale_persuaded"), "Хейл: два контейнера ВРЭ, хранилище совета Vault-Tec")
g.dialogue.active_node = None
goto(g, sorted(portal(g, "ares_lab")["tiles"])[0])
press("ares_project", "Стерилизовать")
ok(g.flags.get("ares_vre_destroyed"), "контейнеры на Марсе стерилизованы")
goto(g, sorted(portal(g, "ares_hab")["tiles"])[0])
talk("cmdr_hale")
say("вернуться домой")
say("Летите")
ok(g.flags.get("ares_crew_home"), "Хейл и Юки летят на Землю")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
