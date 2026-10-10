"""
Личные квесты спутников: Искра — в ученицы к доктору Шоу (Панк), маска для Сэм (Хьюго),
Коббс сдаёт пост в Бейкере; у каждого — отклик спутника и слайд эпилога «Спутники».

    .venv/bin/python tests/test_companions.py
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
        while g.perk_choices:
            g.handle_key(pygame.K_1)


def talk(g, nid):
    g.dialogue.active_node = None
    npc = next(n for n in g.npcs if n.npc_id == nid)
    for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (-1, 1)):
        c = (tile_of(npc)[0] + dx, tile_of(npc)[1] + dy)
        if not g.level.is_wall(*c):
            g.player.rect.topleft = rect_pos_for_tile(g.player, c)
            break
    g.handle_key(pygame.K_e)
    assert g.dialogue.is_active(), nid


def say(g, part):
    opts = [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]
    idx = next((i for i, l in enumerate(opts) if part in l), None)
    assert idx is not None, f"нет реплики «{part}» среди {opts}"
    g.handle_key(pygame.K_1 + idx)
    fr(g, 1)


def go(g, lid):
    g.dialogue.active_node = None
    g.enter_location(lid)
    g.slides = None
    for e in g.enemies:
        e.alive = False
    fr(g)


def read(g, item):
    g.item_action(item)[1]()
    g.close_terminal()


def take(g, title):
    box = next(c for c in g.level.containers if c["name"] == title)
    for t in box["tiles"]:
        for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (-1, -1)):
            c = (t[0] + dx, t[1] + dy)
            if not g.level.is_wall(*c) and c not in box["tiles"]:
                g.player.rect.topleft = rect_pos_for_tile(g.player, c)
                g.handle_key(pygame.K_e)
                fr(g, 1)
                if g.loot:
                    g.handle_key(pygame.K_r)
                    g.loot = None
                return



from src.game.slides import SLIDES  # noqa: E402


def wait(g, ms=16000):
    for _ in range(ms // 16):
        g.update(16)
        while g.perk_choices:
            g.handle_key(pygame.K_1)


def ally_talk(g):
    g.dialogue.active_node = None
    g.player.rect.topleft = rect_pos_for_tile(g.player, (tile_of(g.ally)[0] - 1, tile_of(g.ally)[1]))
    g.handle_key(pygame.K_e)


# ---- Искра
g = Game(intro=False)
go(g, "baker")
g.flags["iskra_free"] = True
go(g, "baker")
iskra = next((n for n in g.npcs if n.npc_id == "iskra_out"), None)
if iskra is None:
    for loc in ("baker_outskirts", "baker_mission"):
        go(g, loc)
        iskra = next((n for n in g.npcs if n.npc_id == "iskra_out"), None)
        if iskra:
            break
ok(iskra is not None, "Искра на свободе в Бейкере")
talk(g, "iskra_out"); say(g, "заниматься"); say(g, "отнесу")
go(g, "junktown_clinic")
talk(g, "anna_shaw"); say(g, "учиться"); say(g, "Передам")
ok(g.flags.get("iskra_student"), "Анна Шоу берёт Искру в ученицы: «комната над клиникой»")
g.join_ally("punk")
wait(g)
ok(any("Пыль. Просто пыль" in l for l in g.log_lines), "Панк: «Пыль. Просто пыль»")

# ---- Сэм
g = Game(intro=False)
go(g, "vault22_living")
g.inventory.add("противогаз", 1)
talk(g, "sam_botanist"); say(g, "споры"); say(g, "противогаз"); say(g, "...")
ok(g.flags.get("sam_safe"), "Сэм носит маску в оранжерее")

# ---- Коббс
g = Game(intro=False)
g.flags.update({"baker_done": True, "cobbs_knows_reid": True})
go(g, "necropolis")
g.join_ally("cobbs")
fr(g)
ally_talk(g)
ok(not any("последний пост" in g.dialogue.option_label(o) for o in g.dialogue.visible_options()), "в Некрополе — не к месту")
g.dialogue.active_node = None
go(g, "baker")
g.join_ally("cobbs") if g.ally is None else None
fr(g)
ally_talk(g); say(g, "последний пост"); say(g, "Идём")
ok(g.flags.get("cobbs_post_relieved"), "в Бейкере Коббс сдаёт пост: «Меня сменили»")

ep = next(s for s in SLIDES["epilogue"]["slides"] if s["title"] == "СПУТНИКИ")
ok(sum(1 for p in ep["parts"] if g.check_condition(p.get("if", {}))) >= 1, "слайд эпилога «Спутники»")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
