"""
Гудспрингс: «Перестрелка в городе-призраке» (Ринго, Джо Кобб, Маргарет Крэйн из Хаба; союзники в полдень),
«Двор Санни» (ящеры у родника и тухлое мясо Чета) — подготовка к бою, связь с Хабом и квестом караванов.

    .venv/bin/python tests/test_gsquests.py
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



def fresh(lid="goodsprings_saloon"):
    g = Game(intro=False)
    g.player.max_hp = g.player.hp = 10 ** 5
    go(g, lid)
    return g


# ===================================================== Перестрелка
g = fresh()
go(g, "goodsprings")
ok(not any(n.npc_id == "joe_cobb" for n in g.npcs), "Кобба нет, пока Ринго не сознался")
go(g, "goodsprings_saloon")
talk(g, "gs_drunk"); say(g, "прячешься"); say(g, "разберусь")
ok(g.stage("sq_ringo") == 10, "Ринго сознался: Красный караван, мешок")
talk(g, "trudy"); say(g, "Кобб пришёл"); say(g, "Спасибо")
go(g, "goodsprings")
ok(any(n.npc_id == "joe_cobb" for n in g.npcs), "Джо Кобб ждёт у дороги")
g.inventory.add("крышки", 50)
talk(g, "chet"); say(g, "патроны для Ринго"); say(g, "Пятьдесят")
talk(g, "joe_cobb"); say(g, "под защитой"); say(g, "выйти на улицу)"); say(g, "...")
ok(g.flags.get("ringo_town") and g.stage("sq_ringo") == 100, "Труди и Чет — двое стволов: Кобб снял шляпу")

g = fresh()
talk(g, "gs_drunk"); say(g, "прячешься"); say(g, "разберусь")
go(g, "goodsprings")
talk(g, "joe_cobb"); say(g, "под защитой")
opts = [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]
ok(not any(o == "(полдень; выйти на улицу)" for o in opts), "без союзников — только одному")
say(g, "одному"); say(g, "...")
fr(g)
ok(g.flags.get("ringo_handed") and g.player.hp < g.player.max_hp, "один против Кобба — ранен, Ринго увезли")

g = fresh()
talk(g, "gs_drunk"); say(g, "прячешься"); say(g, "разберусь")
go(g, "hub")
g.player.skills["speech"] = 70
talk(g, "crimson_boss"); say(g, "Ринго не крал"); say(g, "Красноречие"); say(g, "Передам")
go(g, "goodsprings")
talk(g, "joe_cobb"); say(g, "отозвала"); say(g, "...")
ok(g.flags.get("ringo_free") and g.stage("sq_ringo") == 100, "Крэйн отозвала заказ — Кобб уехал")

# ===================================================== Двор Санни
g = fresh("goodsprings")
talk(g, "sunny"); say(g, "у родника"); say(g, "с тобой")
ok(g.stage("sq_spring") == 10 and g.flags.get("sunny_ally"), "Санни зовёт к роднику")
talk(g, "gs_kid"); say(g, "ночью к роднику"); say(g, "можно")
go(g, "goodsprings_cave")
ok(len(g.enemies) > 0, "в пещере ящеры")
for e in g.enemies:
    e.alive = False
g._check_cleared()
ok(g.flags.get("gs_cave_cleared") and g.stage("sq_spring") == 50, "пещера чиста")
go(g, "goodsprings")
talk(g, "sunny"); say(g, "Пещера чиста"); say(g, "Чет"); say(g, "...")
ok(g.flags.get("chet_shamed") and g.inventory.has("охотничья винтовка") and g.stage("sq_spring") == 100, "Чет пойман — винтовка Санни герою")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
