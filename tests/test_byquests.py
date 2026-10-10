"""
Боунъярд: «Брат Карл» (вернуть мужа из культа гармошкой сына), «Почерк не его» (письма «родным» со склада Собора),
«Колокольня» (маяк Марипозы: динамит, Наука или Братство из Хаба) — улики, навыки, выборы, связь с Хабом.

    .venv/bin/python tests/test_byquests.py
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



def fresh(lid="boneyard_adytum"):
    g = Game(intro=False)
    g.player.max_hp = g.player.hp = 10 ** 5
    go(g, lid)
    return g


# ===================================================== Брат Карл
g = fresh()
talk(g, "adytum_mom"); say(g, "Кто ушёл"); say(g, "Как его зовут"); say(g, "не буду стрелять")
ok(g.stage("sq_karl") == 10, "Элен рассказала о Карле")
talk(g, "adytum_kid"); say(g, "папина гармошка"); say(g, "Постараюсь")
ok(g.stage("sq_karl") == 50 and g.inventory.has("губная гармошка Карла"), "Джимми отдал гармошку")
go(g, "boneyard_cathedral")
talk(g, "cult_listener"); say(g, "сыграть"); say(g, "Идём"); say(g, "...")
fr(g)
ok(g.flags.get("karl_home") and not any(n.npc_id == "cult_listener" for n in g.npcs), "Карл вспомнил «ре» и ушёл домой")
go(g, "boneyard_adytum")
talk(g, "adytum_mom")
ok(g.dialogue.active_node == "k_home", "Элен: он свистит без «до»")

g = fresh()
talk(g, "adytum_mom"); say(g, "Кто ушёл"); say(g, "Как его зовут"); say(g, "не буду стрелять")
talk(g, "adytum_kid"); say(g, "папина гармошка"); say(g, "Постараюсь")
go(g, "boneyard_cathedral")
talk(g, "cult_listener"); say(g, "сыграть"); say(g, "ночью"); say(g, "...")
ok(g.flags.get("karl_west"), "отложил побег — Морфей увёз Карла на запад")

g = fresh()
g.player.skills["speech"] = 80
talk(g, "adytum_mom"); say(g, "Кто ушёл"); say(g, "Как его зовут"); say(g, "не буду стрелять")
go(g, "boneyard_cathedral")
talk(g, "cult_listener"); say(g, "Красноречие"); say(g, "домой"); say(g, "...")
ok(g.flags.get("karl_home"), "Красноречие: ботинки и обещание — без гармошки")

# ===================================================== Почерк не его
g = fresh("boneyard")
talk(g, "adytum_farmer"); say(g, "Чем платят"); say(g, "письма брата"); say(g, "Узнаю")
ok(g.stage("sq_letters_by") == 10, "Пол показал письма брата")
go(g, "boneyard_cathedral")
g.inventory.add("отмычка", 1)
for n in list(g.npcs):
    g.npcs.remove(n)
take(g, "сундук на складе")
ok(g.inventory.has("пачка писем «родным»") and g.stage("sq_letters_by") == 50, "пачка писем со склада Собора")
go(g, "boneyard")
talk(g, "adytum_farmer"); say(g, "нашёл письма"); say(g, "жив"); say(g, "...")
ok(g.flags.get("lt_truth") and g.stage("sq_letters_by") == 100, "Пол знает правду: посадит грядку за брата")
go(g, "boneyard_adytum")
talk(g, "adytum_mayor"); say(g, "Письма со стройки"); say(g, "...")
ok(g.flags.get("lt_mayor") and not g.inventory.has("пачка писем «родным»"), "мэр читает письма на площади")

# ===================================================== Колокольня
g = fresh("boneyard")
talk(g, "adytum_worker"); say(g, "Что строит"); say(g, "медный кабель"); say(g, "Спасибо")
ok(g.stage("sq_bell") == 10, "колокольня — не колокол")
g.inventory.add("динамит", 1)
talk(g, "adytum_worker"); say(g, "динамит"); say(g, "...")
ok(g.flags.get("bell_blown") and g.stage("sq_bell") == 100, "динамит в тачке с кирпичами — колокольни нет")

g = fresh("boneyard")
g.player.skills["science"] = 60
g.inventory.add("изолента", 1)
talk(g, "adytum_worker"); say(g, "Что строит"); say(g, "медный кабель"); say(g, "Спасибо")
talk(g, "adytum_worker"); say(g, "Наука"); say(g, "...")
ok(g.flags.get("bell_jammed") and g.inventory.has("дубликат передатчика"), "Наука: маяк шипит, плата у героя")
go(g, "hub")
c0 = g.inventory.count("крышки")
talk(g, "bos_scout"); say(g, "маяк 3"); say(g, "...")
ok(g.flags.get("bos_beacon_card") and g.inventory.count("крышки") - c0 == 200, "плата — разведчице Братства в Хабе")

g = fresh("boneyard")
talk(g, "cult_foreman"); 
opts = [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]
ok(not any("маяк" in o for o in opts), "Ахаву нечего предъявить, пока не знаешь")
g.dialogue.active_node = None
talk(g, "adytum_worker"); say(g, "Что строит"); say(g, "медный кабель"); say(g, "Спасибо")
go(g, "hub")
talk(g, "bos_scout"); say(g, "Боунъярде"); say(g, "Пусть идут"); say(g, "...")
ok(g.flags.get("bell_bos") and g.karma < 0, "Братство разнесло стройку вместе с рабочими — карма вниз")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
