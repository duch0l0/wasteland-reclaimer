"""
Ранги в Коронах Вегаса (docs/city_plan.md, этап 2): по три задания у Сапогов, Змей и Ладоней —
ступени 1→4, звание «правой руки», голос на совете Корон и последствия для других Корон.

    .venv/bin/python tests/test_crowns.py
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



import random  # noqa: E402


def fresh(crown, lid):
    g = Game(intro=False)
    g.player.max_hp = g.player.hp = 10 ** 5
    g.flags[f"{crown}_member"] = True
    go(g, lid)
    g.sync_story()
    return g


# ===================================================== Сапоги
g = fresh("boots", "vegas_boots")
ok(g.flags.get("boots_rank") == 1, "вступил в Сапоги — первая ступень")
talk(g, "boots_rider_b"); say(g, "работа"); say(g, "Найду")
go(g, "vegas_strip")
talk(g, "strip_kid"); say(g, "медной стружке"); say(g, "поговорю")
go(g, "vegas_boots")
g.player.skills["speech"] = 50
talk(g, "boots_rider_b"); say(g, "отработает"); say(g, "...")
ok(g.flags.get("boots_rank") == 2 and g.flags.get("tim_boots") and g.inventory.has("мотошлем"), "Тим отрабатывает у Розы — ранг 2, мотошлем")
g.inventory.add("ядерный элемент", 1)
talk(g, "boots_engineer"); say(g, "турбина"); say(g, "ядерный элемент"); say(g, "...")
ok(g.flags.get("boots_rank") == 3 and g.flags.get("boots_turbine"), "турбина поёт ровно — ранг 3")
talk(g, "boots_rider_b"); say(g, "Ещё работа"); say(g, "Найду")
ok("расписка Змей за ток" in g.pocket("boots_rider"), "расписка — в кармане у Дасти")
g.inventory.add("расписка Змей за ток", 1)
g.player.skills["speech"] = 70
talk(g, "boots_rider_b"); say(g, "Расписка"); say(g, "Красноречие"); say(g, "...")
ok(g.flags.get("boots_rank") == 4 and g.flags.get("dusty_confessed") and any(t[0] == "boots_hand" for t in g.titles()),
   "Дасти сознался Хэнку — правая рука Сапогов")
go(g, "vegas_strip")
talk(g, "judge_sol")
opts = [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]
ok(any("правая рука" in o for o in opts), "правая рука Короны может созвать совет без трёх тайн")

# Тима по кодексу — выпороли и выгнали
g = fresh("boots", "vegas_boots")
talk(g, "boots_rider_b"); say(g, "работа"); say(g, "Найду")
go(g, "vegas_strip")
talk(g, "strip_kid"); say(g, "медной стружке"); say(g, "поговорю")
go(g, "vegas_boots")
g.player.skills["speech"] = 10
talk(g, "boots_rider_b"); say(g, "Вор — Тим"); say(g, "...")
go(g, "vegas_strip")
ok(g.flags.get("boots_rank") == 2 and not any(n.npc_id == "strip_kid" for n in g.npcs) and g.karma < 0, "кодекс без жалости — Тима выгнали")

# ===================================================== Змеи
g = fresh("snakes", "vegas_den")
g.flags["palms_secret"] = True
talk(g, "mother_snake"); say(g, "дело"); say(g, "Агата"); say(g, "...")
ok(g.flags.get("snakes_rank") == 2 and g.flags.get("palms_secret_sold"), "продал тайну Агаты — ранг 2")
talk(g, "mother_snake"); say(g, "Ещё дело"); say(g, "Получу")
go(g, "vegas_strip")
g.player.skills["speech"] = 50
talk(g, "strip_drunk"); say(g, "двести"); say(g, "Красноречие"); say(g, "...")
go(g, "vegas_den")
talk(g, "mother_snake"); say(g, "Фрэнки"); say(g, "...")
ok(g.flags.get("snakes_rank") == 3 and g.flags.get("frankie_spy"), "Фрэнки стал слушателем у «Лаки 38» — ранг 3")
talk(g, "mother_snake"); say(g, "нужно родне"); say(g, "Доставлю")
go(g, "vegas_strip")
g.player.skills["science"] = 50
talk(g, "grey_buyer"); say(g, "Наука"); say(g, "отдать"); say(g, "...")
ok(g.inventory.has("копия схемы ходов") and g.flags.get("rk_s4_delivered"), "посылка Анклаву доставлена — а копия схемы у героя")
go(g, "vegas_den")
talk(g, "mother_snake"); say(g, "доставлена"); say(g, "...")
ok(g.flags.get("snakes_rank") == 4, "правая рука Змей")
go(g, "hub")
talk(g, "bos_scout"); say(g, "Схема ходов"); say(g, "Мало")
ok(g.flags.get("bos_vegas_map"), "копия — Братству: Анклав в Вегасе")

# ===================================================== Ладони
g = fresh("palms", "vegas_library")
g.inventory.add("книга «Уличная драка»", 1)
talk(g, "mother_agatha"); say(g, "полезен"); say(g, "Вот"); say(g, "...")
ok(g.flags.get("palms_rank") == 2 and not g.inventory.has("книга «Уличная драка»"), "книга в библиотеку — ранг 2")
g.player.skills["speech"] = 60
talk(g, "mother_agatha"); say(g, "Что ещё"); say(g, "диете"); say(g, "...")
ok(g.flags.get("palms_rank") == 3 and not g.flags.get("palms_ate"), "бобы на серебре — ранг 3 без людоедства")
talk(g, "mother_agatha"); say(g, "прекратить"); say(g, "Поговорю")
talk(g, "palms_librarian"); say(g, "страшное"); say(g, "Спасибо")
go(g, "vegas_palms")
talk(g, "palms_gardener"); say(g, "томаты"); say(g, "Спасибо")
go(g, "vegas_library")
talk(g, "mother_agatha"); say(g, "голосовать"); say(g, "...")
ok(g.flags.get("palms_reformed") and g.flags.get("palms_rank") == 4, "двое из трёх старейшин — Ладони больше не едят людей")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
