"""
Некрополь: «Чем кончился „Атомный рейнджер“» (плёнка из Убежища 12, проектор), «Еда у шлюза» (дикие гули и Шоу-44),
«Пляж в Санта-Монике» (чужая память — загадка по реестру) — улики, навыки, связь с Джанктауном, выборы.

    .venv/bin/python tests/test_ncquests.py
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



def fresh(lid="necropolis"):
    g = Game(intro=False)
    g.player.max_hp = g.player.hp = 10 ** 5
    go(g, lid)
    return g


# ===================================================== Атомный рейнджер
g = fresh()
talk(g, "nc_old"); say(g, "Какой был кинотеатр"); say(g, "последнюю часть"); say(g, "Посмотрю")
ok(g.stage("sq_fox") == 10, "Эд хочет знать финал")
go(g, "vault12")
take(g, "шкафчик жильца")
ok(g.inventory.has("кинолента «Атомный рейнджер»") and g.stage("sq_fox") == 50, "плёнка нашлась в Убежище 12")
go(g, "necropolis")
talk(g, "harry_mech"); say(g, "Проектор")
opts = [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]
ok(not any("Наука" in o for o in opts) and not any("Сорок" in o for o in opts), "без крышек и Науки Гарри не возьмётся")
g.dialogue.active_node = None
g.inventory.add("крышки", 40)
talk(g, "harry_mech"); say(g, "Проектор"); say(g, "Сорок"); say(g, "...")
talk(g, "nc_old"); say(g, "плёнка у меня"); say(g, "покажем"); say(g, "...")
ok(g.flags.get("fox_truth") and g.stage("sq_fox") == 100, "сеанс в «Фоксе»: продолжение следует")

g = fresh()
g.inventory.add("кинолента «Атомный рейнджер»", 1)
g.player.skills["speech"] = 60
talk(g, "nc_old"); say(g, "плёнка у меня"); say(g, "расскажу финал"); say(g, "...")
ok(g.flags.get("fox_lie") and g.stage("sq_fox") == 100, "Красноречие: счастливый финал на словах")

# ===================================================== Еда у шлюза
g = fresh("necropolis_under")
talk(g, "under_ghoul_b"); say(g, "Кто перестал"); say(g, "злее"); say(g, "Узнаю")
ok(g.stage("sq_ferals") == 10, "дикие кричат — Сет грозит выжечь")
talk(g, "ghoul_healer")
opts = [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]
ok(not any("Шлюз" in o for o in opts), "без улик Дейва не спросить")
g.dialogue.active_node = None
talk(g, "under_barkeep"); say(g, "шлюзу"); say(g, "Спасибо")
ok(g.stage("sq_ferals") == 50, "Бетти: Дейв ходит к шлюзу с сумкой")
go(g, "junktown_clinic")
talk(g, "anna_shaw"); say(g, "Железы"); say(g, "Передам")
go(g, "necropolis_under")
talk(g, "ghoul_healer"); say(g, "Шлюз"); say(g, "наркоз"); say(g, "...")
ok(g.flags.get("ferals_humane") and g.stage("sq_ferals") == 100, "наркоз от доктора Шоу — диких режут по-людски, Лоррейн держится")

g = fresh("necropolis_under")
g.player.rect.topleft = rect_pos_for_tile(g.player, (40, 8))      # со стороны, где Дейв не загораживает
g.handle_key(pygame.K_e)
fr(g, 1)
g.handle_key(pygame.K_r)
g.loot = None
ok(g.inventory.has("журнал Дейва"), "журнал Дейва — в его аптечном шкафу")
talk(g, "ghoul_healer"); say(g, "журнал"); say(g, "Сет должен знать"); say(g, "...")
fr(g)
ok(g.flags.get("shaw44_stopped") and not any(n.npc_id == "ghoul_healer" for n in g.npcs), "рассказал Сету — Дейв ушёл, Шоу-44 больше не варят")

g = fresh("necropolis_under")
g.flags["ferals_clue"] = True; g.flags["ferals_job"] = True
talk(g, "ghoul_healer"); say(g, "Шлюз"); say(g, "Продолжай"); say(g, "...")
ok(g.flags.get("ferals_burned") and g.karma < 0, "отмахнулся — Сет выжег канализацию")

# ===================================================== Пляж в Санта-Монике
g = fresh()
talk(g, "water_queue_b"); say(g, "чего не было"); say(g, "с пляжа"); say(g, "Найду")
ok(g.stage("sq_beach") == 10, "гулька помнит чужой пляж")
go(g, "necropolis_hall")
talk(g, "lorraine"); say(g, "реестр"); say(g, "Спасибо")
ok(g.inventory.has("реестр Лоррейн"), "реестр у героя")
go(g, "necropolis")
talk(g, "water_queue_b"); say(g, "чьё это детство"); say(g, "Мод"); say(g, "Подумаю")
ok(not g.flags.get("beach_known"), "Мод — неверно (Санта-Моника, но детей не было)")
talk(g, "water_queue_b"); say(g, "чьё это детство"); say(g, "Гарри"); say(g, "Подумаю")
ok(not g.flags.get("beach_known"), "Гарри — неверно (шрам, но холост)")
talk(g, "water_queue_b"); say(g, "чьё это детство"); say(g, "Сета"); say(g, "...")
ok(g.stage("sq_beach") == 50, "вышка №12, свисток — Лили, дочь Сета")
talk(g, "water_queue_b"); say(g, "Дочери Сета"); say(g, "должен знать"); say(g, "...")
ok(g.inventory.has("свисток спасателя") and g.stage("sq_beach") == 100, "Сет отдал свисток: очередь пьёт без очереди")
talk(g, "water_queue_b")
ok(g.dialogue.active_node == "bc_after", "гулька теперь видит хороший сон")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
