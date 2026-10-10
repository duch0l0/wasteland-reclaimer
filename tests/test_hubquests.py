"""
Хаб: «Мальтийский сокол» (нуар-расследование), «Лихорадка в Старом городе» (лечить симптом или причину),
«Голубые ментаты» (культ травит базар) — улики, проверки навыков, связи с Джанктауном, выборы и последствия.

    .venv/bin/python tests/test_hubquests.py
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



def fresh():
    g = Game(intro=False)
    g.player.max_hp = g.player.hp = 10 ** 5
    go(g, "hub_falcon")
    return g


# ===================================================== Мальтийский сокол
# путь 1: Лулу → Ленни → Декер (купить ключ) → сейф → правда Винни
g = fresh()
talk(g, "falcon_barkeep"); say(g, "серый"); say(g, "Кто знал"); say(g, "Поспрашиваю")
ok(g.stage("sq_falcon") == 10, "Винни нанял искать птицу")
talk(g, "falcon_gambler"); say(g, "Где птица")
ok(not g.flags.get("know_falcon_decker"), "Ленни без улик отпирается")
g.dialogue.active_node = None
talk(g, "falcon_singer"); say(g, "Кто был в баре"); say(g, "Спасибо")
talk(g, "falcon_gambler"); say(g, "Лулу видела"); say(g, "Посмотрим")
ok(g.stage("sq_falcon") == 50, "Ленни сознался: птица у Декера")
go(g, "hub_old")
g.inventory.add("крышки", 100)
talk(g, "decker"); say(g, "Птица Винни"); say(g, "Сто крышек"); say(g, "...")
ok(g.inventory.has("ключ от сейфа Декера"), "Декер продал ключ от сейфа")
take(g, "сейф Декера")
ok(g.inventory.has("статуэтка сокола"), "птица из сейфа")
go(g, "hub_falcon")
c0 = g.inventory.count("крышки")
talk(g, "falcon_barkeep"); say(g, "Твоя птица"); say(g, "Свинец"); say(g, "...")
ok(g.stage("sq_falcon") == 100 and g.flags.get("falcon_truth") and g.inventory.count("крышки") - c0 == 100, "правда о свинце: сотня и песня Лулу")

# путь 2: свалить на Ленни
g = fresh()
talk(g, "falcon_barkeep"); say(g, "серый"); say(g, "Кто знал"); say(g, "Поспрашиваю")
talk(g, "falcon_barkeep"); say(g, "Птицу взял Ленни"); say(g, "...")
fr(g)
ok(g.flags.get("falcon_lenny_blamed") and not any(n.npc_id == "falcon_gambler" for n in g.npcs) and g.karma < 0,
   "оговорил Ленни — его выгнали, карма вниз")

# путь 3: беспризорник + Красноречие у Декера + промолчать
g = fresh()
talk(g, "falcon_barkeep"); say(g, "серый"); say(g, "Кто знал"); say(g, "Поспрашиваю")
go(g, "hub_old")
g.inventory.add("крышки", 10)
talk(g, "street_kid"); say(g, "мешок"); say(g, "...")
g.player.skills["speech"] = 70
talk(g, "decker"); say(g, "Птица Винни"); say(g, "Красноречие"); say(g, "...")
take(g, "сейф Декера")
go(g, "hub_falcon")
talk(g, "falcon_barkeep"); say(g, "Твоя птица"); say(g, "Скол"); say(g, "...")
ok(g.flags.get("falcon_returned") and g.stage("sq_falcon") == 100, "беспризорник, Красноречие, ложь во спасение — тоже конец")

# ===================================================== Лихорадка
g = fresh()
go(g, "hub_old")
talk(g, "slum_mother"); say(g, "весь красный"); say(g, "найду")
ok(g.stage("sq_fever") == 10, "мать рассказала о лихорадке")
opts = [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]
ok(not any("Жаропонижающее" in o for o in opts), "без лекарства — только вода культа или «пока нечего»")
g.inventory.add("стимулятор", 1)
g.player.skills["medicine"] = 15
say(g, "Целиком"); say(g, "Прости")
ok(g.inventory.has("стимулятор") and not g.flags.get("fever_cured"), "стимулятор целиком без Медицины — старик не дал")
go(g, "junktown_clinic")
talk(g, "anna_shaw"); say(g, "ребёнок с лихорадкой"); say(g, "Бегу")
go(g, "hub_old")
talk(g, "slum_mother"); say(g, "лекарство"); say(g, "Жаропонижающее"); say(g, "колодцем")
ok(g.stage("sq_fever") == 50, "лекарство доктора Шоу из Джанктауна помогло")
talk(g, "slum_old"); say(g, "колодцем"); say(g, "Вегой")
go(g, "hub")
talk(g, "dolores"); say(g, "кран"); say(g, "...")
ok(g.stage("sq_fever") == 50, "чужаку Долорес кран не откроет")
g.flags["dolores_trust"] = True
talk(g, "dolores"); say(g, "кран"); say(g, "Спасибо")
ok(g.stage("sq_fever") == 100 and g.flags.get("fever_tap"), "внук Рида уговорил Вегу открыть кран Старому городу")
go(g, "hub_old")
talk(g, "slum_mother"); say(g, "Спасибо")
ok(g.inventory.has("рисунок углём"), "мальчишка нарисовал героя")

# вода культа
g = fresh()
go(g, "hub_old")
talk(g, "slum_mother"); say(g, "весь красный"); say(g, "найду"); say(g, "воды Единства"); say(g, "...")
ok(g.flags.get("fever_cult") and g.karma <= -25, "вода Единства: жар прошёл, ребёнка не стало")

# фильтр своими руками
g = fresh()
go(g, "hub_old")
talk(g, "slum_mother"); say(g, "весь красный"); say(g, "найду"); say(g, "Пока нечего")
g.player.skills["science"] = 60
g.inventory.add("пружина", 1)
talk(g, "slum_old"); say(g, "колодцем"); say(g, "Наука"); say(g, "...")
ok(g.flags.get("fever_filter") and g.stage("sq_fever") == 100, "Наука: фильтр в колодце починен")

# ===================================================== Голубые ментаты
g = fresh()
go(g, "hub_old")
talk(g, "junkie"); say(g, "синий"); say(g, "Найду")
ok(g.stage("sq_blue") == 10, "торчок рассказал о Тощем Сэме")
go(g, "hub")
talk(g, "arms_seller"); say(g, "голубыми"); say(g, "Спасибо")
g.inventory.add("крышки", 6)
talk(g, "spice_seller"); say(g, "голубых"); say(g, "купить")
ok(g.stage("sq_blue") == 50 and g.inventory.count("голубые ментаты") == 3, "купил голубые у торговца пряностями")
go(g, "junktown_clinic")
talk(g, "anna_shaw"); say(g, "таблетки"); say(g, "Спасибо")
ok(g.inventory.has("антидот Анны") and g.flags.get("know_cult_water"), "доктор Шоу узнала чаны Марипозы и дала антидот")
go(g, "hub_old")
talk(g, "junkie"); say(g, "Антидот"); say(g, "...")
ok(g.flags.get("blue_junkie_saved"), "торчок Вилли спасён")
go(g, "hub")
talk(g, "spice_seller"); say(g, "Тощий Сэм"); say(g, "к страже"); say(g, "...")
fr(g)
ok(g.stage("sq_blue") == 100 and g.flags.get("blue_arrested") and not any(n.npc_id == "spice_seller" for n in g.npcs),
   "стража забрала торговца")

# накладная из кармана → шантаж
g = fresh()
go(g, "hub")
g.inventory.add("накладная Единства", 1)
talk(g, "spice_seller"); say(g, "накладная"); say(g, "Тощему Сэму"); say(g, "Двести"); say(g, "...")
ok(g.flags.get("blue_blackmail") and g.karma < 0 and g.stage("sq_blue") == 100, "шантаж: двести крышек, карма вниз")
ok("накладная Единства" in g.pocket("spice_seller"), "накладная — в кармане торговца (её можно стащить)")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
