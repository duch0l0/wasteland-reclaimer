"""
Нидлс: «Жёлтые треугольники» (залить течь на барже: защита, на одном вдохе или руками стражи Морроу),
«Беглянка в церкви» (Ноа из конвоя культа: паром Кейт, взятка, убежище у Эли или сдать Морроу).

    .venv/bin/python tests/test_ndquests.py
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



def fresh(lid="needles"):
    g = Game(intro=False)
    g.player.max_hp = g.player.hp = 10 ** 5
    go(g, lid)
    return g


# ===================================================== Жёлтые треугольники
g = fresh()
talk(g, "kate"); say(g, "рыба светится"); say(g, "баржа"); say(g, "цементом"); say(g, "Нырну")
ok(g.stage("sq_barge") == 10, "Кейт: залить бочку цементом")
talk(g, "drunk_vic"); say(g, "открытая бочка"); say(g, "Спасибо")
ok(g.stage("sq_barge") == 50, "Вик: третий трюм, у переборки")
g.inventory.add("мешок цемента", 1)
g.inventory.add("противогаз", 1)
r0 = g.player.rads
talk(g, "kate"); say(g, "Цемент у меня"); say(g, "химзащиты"); say(g, "...")
ok(g.flags.get("barge_sealed") and g.stage("sq_barge") == 100 and 0 < g.player.rads - r0 <= 100, "в противогазе — малая доза, баржа залита")

g = fresh()
talk(g, "kate"); say(g, "рыба светится"); say(g, "баржа"); say(g, "цементом"); say(g, "Нырну")
g.inventory.add("мешок цемента", 1)
r0 = g.player.rads
talk(g, "kate"); say(g, "Цемент у меня"); say(g, "одном вдохе"); say(g, "...")
ok(g.flags.get("barge_sealed") and g.player.rads - r0 >= 300, "без защиты — 350 рад")

g = fresh()
talk(g, "kate"); say(g, "рыба светится"); say(g, "баржа"); say(g, "цементом"); say(g, "Нырну")
go(g, "needles_bridge")
g.player.skills["speech"] = 70
talk(g, "captain_morrow"); say(g, "Баржа ниже моста"); say(g, "Красноречие"); say(g, "...")
ok(g.flags.get("barge_morrow") and g.stage("sq_barge") == 100, "Красноречие: стража Морроу залила баржу")

# ===================================================== Беглянка в церкви
g = fresh()
talk(g, "preacher_eli"); say(g, "особенно"); say(g, "Поговорю")
ok(g.stage("sq_noa") == 10, "Эли прячет беглянку")
go(g, "needles_church")
talk(g, "noa_runaway"); say(g, "Что ты видела"); say(g, "в безопасности")
ok(g.stage("sq_noa") == 50 and g.flags.get("know_cult_convoys"), "Ноа: три фургона в неделю через мост Морроу")
opts = [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]
ok(not any("Кейт" in o for o in opts), "паром Кейт — только если ей помог с переправой")
g.flags["ferry_done"] = True
g.dialogue.active_node = None
talk(g, "noa_runaway"); say(g, "Кейт"); say(g, "...")
fr(g)
ok(g.flags.get("noa_ferried") and not any(n.npc_id == "noa_runaway" for n in g.npcs), "ночью на «Упрямой Мэри» — на тот берег")

g = fresh("needles_church")
g.player.skills["speech"] = 60
talk(g, "noa_runaway"); say(g, "вытащу"); say(g, "Останься"); say(g, "...")
go(g, "needles_church")
ok(g.flags.get("noa_stays") and any(n.npc_id == "noa_runaway" for n in g.npcs), "Ноа осталась у Эли — поёт по воскресеньям")

g = fresh("needles_church")
talk(g, "noa_runaway"); say(g, "вытащу"); say(g, "Морроу, где она"); say(g, "...")
go(g, "needles")
talk(g, "preacher_eli")
ok(g.flags.get("noa_sold") and g.karma <= -50 and g.dialogue.active_node == "no_eli_sold", "сдал Ноа — Эли не может за тебя молиться")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
