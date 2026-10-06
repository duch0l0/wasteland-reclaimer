"""
Побочные квесты: грузовик под горой (Джанктаун), мальчишка в Вегас (Хаб), пустая могила (Некрополь → Купер),
мотоцикл Дасти (Вегас). Каждый попадает в журнал и закрывается.

    .venv/bin/python tests/test_sidequests.py
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


def say(g, part):
    opts = [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]
    idx = next((i for i, l in enumerate(opts) if part in l), None)
    assert idx is not None, f"нет реплики «{part}» среди {opts}"
    g.handle_key(pygame.K_1 + idx)
    fr(g, 1)


def talk(g, nid):
    g.dialogue.active_node = None
    npc = next(n for n in g.npcs if n.npc_id == nid)
    for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1)):
        c = (tile_of(npc)[0] + dx, tile_of(npc)[1] + dy)
        if not g.level.is_wall(*c):
            g.player.rect.topleft = rect_pos_for_tile(g.player, c)
            break
    g.handle_key(pygame.K_e)
    assert g.dialogue.is_active(), nid


g = Game(intro=False)
g.player.max_hp = g.player.hp = 10 ** 6
g.player.skills["speech"] = 80

g.enter_location("junktown_dump"); fr(g)
for e in g.enemies:
    e.alive = False
talk(g, "scrapper"); say(g, "Поищу")
ok(g.stage("sq_truck") == 10, "журнал: грузовик под горой")
g.dialogue.active_node = None
g.inventory.add("динамит", 1)
talk(g, "scrapper"); say(g, "Держи динамит")
ok(g.stage("sq_truck") == 100 and g.inventory.has("армейский бронежилет"), "грузовик вскрыт — армейский бронежилет")

g.dialogue.active_node = None
g.enter_location("hub"); fr(g)
talk(g, "hub_kid"); say(g, "Красным караваном")
g.dialogue.active_node = None
talk(g, "crimson_boss"); say(g, "лишние руки")
ok(g.stage("sq_runaway") == 100, "мальчишка уехал с Красным караваном")

g.dialogue.active_node = None
g.inventory.add("жетон Vault-Tec", 1)
g.enter_location("boneyard_vt"); fr(g)
for e in g.enemies:
    e.alive = False
talk(g, "cooper"); say(g, "Бад Аскинс"); say(g, "Спасибо")
ok(g.stage("sq_tag") == 100, "жетон Бада Аскинса — у Купера")

g.dialogue.active_node = None
g.enter_location("vegas_boots"); fr(g)
talk(g, "boots_rider"); say(g, "Найду")
g.dialogue.active_node = None
g.enter_location("vegas_snakes"); fr(g)
talk(g, "snake_trader"); say(g, "Сапоги не узнают"); say(g, "Скажу")
ok(g.stage("sq_bike") == 100, "мотоцикл Дасти вернулся к Сапогам")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
