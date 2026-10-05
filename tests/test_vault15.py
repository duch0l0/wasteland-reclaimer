"""
Убежище 15 (tools/build_vault15.py) — без окна: лагерь Шакалов у двери, верхний ярус девяти оставшихся,
нижний ярус с генераторной.

    .venv/bin/python tests/test_vault15.py
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







g.enter_location("boneyard")
fr(g)
g.sync_story()
ok("vault15" in g.worldmap.known, "после Боунъярда на карте — Убежище 15")
g.enter_location("vault15")
fr(g)
ok(g.loc.id == "vault15" and any(n.npc_id == "captive_mira" for n in g.npcs), "у двери — лагерь Шакалов и пленница в клетке")

# Красноречием — Шакалы отпускают Миру
g.player.skills["speech"] = 80
talk("jackal_boss")
say("Следующими будут Шакалы")
say("Правильное")
ok(g.flags.get("mira_free") and not any(n.npc_id == "captive_mira" for n in g.npcs), "Гриз отпустил Миру")

# внутрь: Беатрис, ключ от нижнего яруса
g.dialogue.active_node = None
goto(g, sorted(portal(g, "vault15_atrium")["tiles"])[0])
ok(g.loc.id == "vault15_atrium", "через дверь-шестерню — на верхний ярус")
goto(g, sorted(portal(g, "vault15_lower")["tiles"])[0])
ok(g.loc.id == "vault15_atrium", "люк на нижний ярус задраен")
talk("beatrice")
say("дочь у Шакалов")
say("Понятно")
say("ключ от люка")
say("Найду")
ok(g.flags.get("beatrice_trust") and g.flags.get("v15_lower_ok"), "Беатрис доверяет и даёт ключ от люка")
g.dialogue.active_node = None
goto(g, sorted(portal(g, "vault15_lower")["tiles"])[0])
ok(g.loc.id == "vault15_lower", "нижний ярус")
for e in g.enemies:
    e.alive = False
g.inventory.add("предохранитель Vault-Tec", 1)
g.open_terminal("v15_generator")
g.term_open_entry(1)
g.close_terminal()
ok(g.flags.get("v15_power"), "предохранитель заменён — генератор и насос работают")
goto(g, sorted(portal(g, "vault15_atrium")["tiles"])[0])
g.open_terminal("v15_mainframe")
g.term_open_entry(1)
g.close_terminal()
ok(g.flags.get("know_vault4"), "сеть убежищ: Убежище 4 на побережье до сих пор отвечает")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
