"""
Нидлс (tools/build_needles.py) — без окна: пристань, салун, лавка, церковь, вокзал, мост и журнал пошлин.

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


g.reveal_location("needles")
g.enter_location("needles")
fr(g)
ok(g.loc.id == "needles" and len(g.npcs) >= 7, "Нидлс: пристань и жители")
for to in ("needles_saloon", "needles_shop", "needles_church", "needles_depot"):
    goto(g, sorted(portal(g, to)["tiles"])[0])
    ok(g.loc.id == to, f"вход: {g.loc.name}")
    back = next(p for p in g.level.portals if p["to"] == "needles")
    g.dialogue.active_node = None
    goto(g, sorted(back["tiles"])[0])
    ok(g.loc.id == "needles", f"выход из «{to}» — обратно на улицу")
talk("kate")
say("рыба светится")
say("баржа")
ok(g.flags.get("know_barge"), "Кейт: затонувшая баржа с бочками отравляет реку")
g.dialogue.active_node = None
goto(g, sorted(portal(g, "needles_bridge")["tiles"])[0])
ok(g.loc.id == "needles_bridge", "по дороге на север — мост через Колорадо")
g.open_terminal("needles_toll")
entries = g.term_entries()
g.term_open_entry(next(i for i, (_, e) in enumerate(entries) if "Особые" in e["label"]))
g.close_terminal()
ok(g.flags.get("know_cult_convoys"), "журнал пошлин: фургоны культа идут на запад без досмотра")
ok(not g.level.is_wall(33, 15) and g.level.is_wall(33, 13), "через пролом моста — только по мосткам стражи")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
