"""
Боунъярд (tools/build_boneyard.py) — без окна: руины Лос-Анджелеса, Адитум, «Лезвия», фундамент Собора,
офис Vault-Tec и Купер Говард.

    .venv/bin/python tests/test_boneyard.py
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






g.enter_location("aradesh")
fr(g)
g.sync_story()
ok("boneyard" in g.worldmap.known, "после лагеря Арадеша на карте — Боунъярд")
g.enter_location("boneyard")
fr(g)
for e in g.enemies:
    e.hostile = False
ok(g.loc.id == "boneyard" and len(g.npcs) >= 10, "Боунъярд: руины, Адитум, «Лезвия», стройка")
for to in ("boneyard_adytum", "boneyard_cathedral", "boneyard_vt"):
    goto(g, sorted(portal(g, to)["tiles"])[0])
    ok(g.loc.id == to, f"вход: {g.loc.name}")
    for e in g.enemies:
        e.alive = False
    g.dialogue.active_node = None
    goto(g, sorted(next(p for p in g.level.portals if p["to"] == "boneyard")["tiles"])[0])
    ok(g.loc.id == "boneyard", "обратно на улицу")

# «Лезвия» подставлены: куртка со склада Собора — Нике, приказ брата Т. — мэру
talk("blade_nika")
g.inventory.add("куртка «Лезвий»", 1)
g.dialogue.active_node = None
talk("blade_nika")
say("Собора")
say("бумагу")
ok(g.flags.get("nika_knows"), "Ника узнала метку на куртке")
g.dialogue.active_node = None
g.inventory.add("приказ брата Т.", 1)
goto(g, sorted(portal(g, "boneyard_adytum")["tiles"])[0])
talk("adytum_mayor")
say("приказ брата")
say("Передам")
ok(g.flags.get("adytum_truce"), "мэр Адитума узнал, кто устраивал налёты, и рвёт договор с Морфеем")

# Купер Говард в офисе Vault-Tec
g.dialogue.active_node = None
goto(g, sorted(portal(g, "boneyard")["tiles"])[0])
goto(g, sorted(portal(g, "boneyard_vt")["tiles"])[0])
for e in g.enemies:
    e.alive = False
g.open_terminal("vt_server")
g.term_open_entry(0)
g.close_terminal()
g.flags["know_vt_vre"] = True        # запись о поставках ВРЭ — под паролем, её открывает взлом терминала
talk("cooper")
say("серверной")
say("Спасибо")
ok(g.flags.get("cooper_card") and g.flags.get("know_vault4"), "Купер: ВРЭ ушёл в Убежище 4, ключ-карта директора — герою")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
