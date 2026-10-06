"""
База Марипоза (tools/build_mariposa.py) — без окна: финал: кого не спасли — те в клетках, брат Т. (Тобиас),
пульт базы и три концовки с эпилогом.

    .venv/bin/python tests/test_mariposa.py
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
















g.flags["brother_t_flees"] = True
g.sync_story()
ok("mariposa" in g.worldmap.known, "брат Т. ушёл в Марипозу — она на карте")

# Тоби не спасли в Примме — он здесь; Иезекииля не отдавали культу — его здесь нет
g.enter_location("mariposa_lab")
fr(g)
ids = {n.npc_id for n in g.npcs}
ok("tobi_mp" in ids and "ezekiel_mp" not in ids, "в клетках — только те, кого не успели спасти")
talk("tobi_mp")
say("домой")
ok(g.flags.get("tobi_home") and g.flags.get("tobi_saved_late"), "Тоби спасён в последний момент")

# брат Т. — Тобиас: достучаться и получить код
g.dialogue.active_node = None
g.flags["tobias_done"] = True
g.player.skills["speech"] = 80
talk("brother_t_mp")
say("Ник из закусочной")
say("Спасибо")
ok(g.flags.get("tobias_redeemed") and g.flags.get("mariposa_code"), "Тобиас вспомнил, кем был, — код пульта")

# пульт: код и концовка «Пепел» (Орден) — эпилог
g.dialogue.active_node = None
g.enter_location("mariposa_vats")
fr(g)
for e in g.enemies:
    e.alive = False
g.flags["order_contact"] = True
g.flags["sluice_restored"] = True


def press(part):
    g.open_terminal("mariposa_core")
    idx = next(k for k, (_, e) in enumerate(g.term_entries()) if part in e.get("label", ""))
    g.term_open_entry(idx)
    g.close_terminal()


press("Код от Тобиаса")
ok(g.flags.get("mariposa_unlocked"), "пульт базы разблокирован")
press("Пепел")
ok(g.flags.get("game_ending") and g.flags.get("ending_ash"), "концовка «Пепел»: чаны взорваны")
ok(g.slides is not None and g.slides["id"] == "epilogue", "эпилог — слайдами")
texts = " ".join(p["text"] for sl in g.slides["list"] for p in sl["parts"])
ok("Пепел" in texts and "Долорес" in texts and "Тобиас" in texts and "Сталь." not in texts, "в эпилоге — только то, что случилось")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
