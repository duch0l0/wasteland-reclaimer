"""
Убежище 4 (tools/build_vault4.py) — без окна: дверь с интеркомом, жилой ярус учёных и мирных мутантов,
лаборатория и хранилище ВРЭ на нижнем ярусе.

    .venv/bin/python tests/test_vault4.py
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








g.flags["know_vault4"] = True
g.sync_story()
ok("vault4" in g.worldmap.known, "узнал про Убежище 4 — оно на карте")
g.enter_location("vault4")
fr(g)
for e in g.enemies:
    e.alive = False
goto(g, sorted(portal(g, "vault4_upper")["tiles"])[0])
ok(g.loc.id == "vault4", "дверь закрыта, пока интерком не откроет")
g.inventory.add("ключ-карта Vault-Tec", 1)
g.open_terminal("v4_intercom")
g.term_open_entry(1)
g.close_terminal()
ok(g.flags.get("v4_open"), "ключ-карта директора открывает дверь")
goto(g, sorted(portal(g, "vault4_upper")["tiles"])[0])
ok(g.loc.id == "vault4_upper", "жилой ярус Убежища 4")
goto(g, sorted(portal(g, "vault4_lower")["tiles"])[0])
ok(g.loc.id == "vault4_upper", "лифт вниз — только для персонала")

# письмо брата Т. и сыворотка Анны Шоу: смотрительница отменяет сделку с культом
g.inventory.add("письмо смотрительнице", 1)
g.inventory.add("сыворотка Шоу-44", 1)
talk("overseer_sim")
say("письмо брата")
say("Шоу-44")
say("Передам")
ok(g.flags.get("v4_deal_off") and g.flags.get("v4_lower_ok"), "сделка с культом отменена, лифт открыт")
g.dialogue.active_node = None
goto(g, sorted(portal(g, "vault4_lower")["tiles"])[0])
ok(g.loc.id == "vault4_lower", "нижний ярус — лаборатория")
for e in g.enemies:
    e.alive = False
g.open_terminal("v4_vault")
g.term_open_entry(2)
g.close_terminal()
ok(g.flags.get("v4_vre_destroyed"), "три контейнера ВРЭ уничтожены")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
