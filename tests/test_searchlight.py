"""
Сёрчлайт (tools/build_searchlight.py) — без окна: «Генерал»: посёлок, шахта со штреком под базу, Форт с плацем,
бункер — узел связи «Посейдона-7» и ядро ИИ.

    .venv/bin/python tests/test_searchlight.py
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













g.enter_location("nipton")
fr(g)
g.sync_story()
ok("searchlight" in g.worldmap.known, "после Ниптона на карте — Сёрчлайт")
g.enter_location("searchlight")
fr(g)
ok(g.loc.id == "searchlight" and len(g.npcs) >= 8, "Сёрчлайт: посёлок, копёр, пожарная часть, паладины")
talk("fire_chief_hope")
say("схожу на Форт")
say("Найду Гаса")
g.dialogue.active_node = None
talk("foreman_gus")
say("Дай ключ")
say("Спасибо")
ok(g.inventory.has("ключ от штрека"), "старшина Гас даёт ключ от вентиляционного штрека")

# путь Тени: шахта — штрек — прямо в бункер, мимо часового
g.dialogue.active_node = None
goto(g, sorted(portal(g, "searchlight_mine")["tiles"])[0])
ok(g.loc.id == "searchlight_mine", "шахта")
for e in g.enemies:
    e.alive = False
goto(g, sorted(portal(g, "fort_bunker")["tiles"])[0])
ok(g.loc.id == "fort_bunker", "по штреку — в казарму бункера")
g.open_terminal("fort_comm")
g.term_open_entry(0)
g.close_terminal()
ok(g.flags.get("know_poseidon") and g.flags.get("know_general_puppet"), "узел связи: Генералом управляет «Посейдон-7»")
g.open_terminal("fort_comm")
g.term_open_entry(2)
g.close_terminal()
ok(g.flags.get("fort_enclave_deal") and g.flags.get("recruits_free"), "сделка с Холлисом: новобранцев отпускают, питание для «Ноля» — от Анклава")

# на плацу: Дэнни идёт домой
goto(g, sorted(portal(g, "fort_searchlight")["tiles"])[0])
ok(g.loc.id == "fort_searchlight", "наверх — на плац Форта")
talk("recruit_danny")
say("Иди к маме")
ok(g.flags.get("danny_home"), "Дэнни возвращается к матери")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
