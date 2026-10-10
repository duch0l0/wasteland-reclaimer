"""
Джанктаун: «Гизмо и стена» (заказ на мэра: диктофон, яд в кармане, мир), «Кровь на балахонах» (дети и культ),
«Последняя стена» (кости со свинцом) — улики, карманы, Красноречие, выборы и их цена.

    .venv/bin/python tests/test_jtquests.py
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


def fresh(lid="junktown_casino"):
    g = Game(intro=False)
    g.player.max_hp = g.player.hp = 10 ** 5
    go(g, lid)
    return g


def offer(g):
    go(g, "junktown_casino")
    talk(g, "gizmo"); say(g, "работа"); say(g, "Давай флягу")


# ===================================================== Гизмо и стена
# 1. диктофон
g = fresh()
offer(g)
ok(g.stage("sq_gizmo") == 10 and g.inventory.has("фляга с ядом"), "Гизмо дал флягу с ядом")
go(g, "junktown_hall")
talk(g, "mayor_darkwater"); say(g, "Гизмо заказал"); say(g, "Пойду")
go(g, "junktown_store")
talk(g, "marsha"); say(g, "диктофон"); say(g, "ничего не случится")
go(g, "junktown_casino")
talk(g, "gizmo"); say(g, "Повтори"); say(g, "Всё")
ok(g.inventory.has("запись: признание Гизмо"), "голос Гизмо на плёнке")
go(g, "junktown_hall")
talk(g, "mayor_darkwater"); say(g, "голос Гизмо"); say(g, "...")
go(g, "junktown_casino")
ok(g.stage("sq_gizmo") == 100 and g.flags.get("gizmo_exiled") and not any(n.npc_id == "gizmo" for n in g.npcs),
   "Гизмо выставлен за ворота — в казино его больше нет")

# 2. яд в кармане мэра
g = fresh()
offer(g)
go(g, "junktown_hall")
g.player.skills["steal"] = 150
for n in list(g.npcs):
    if n.npc_id != "mayor_darkwater":
        g.npcs.remove(n)
mayor = next(n for n in g.npcs if n.npc_id == "mayor_darkwater")
t = tile_of(mayor)
g.player.rect.topleft = rect_pos_for_tile(g.player, (t[0], t[1] - 1) if not g.level.is_wall(t[0], t[1] - 1) else (t[0] + 1, t[1]))
fr(g, 1)
g.handle_key(pygame.K_k)
_ri = random.randint
random.randint = lambda a, b: a
g.loot_put("фляга с ядом")
random.randint = _ri
g.loot = None
fr(g)
ok(g.flags.get("mayor_poisoned") and not any(n.npc_id == "mayor_darkwater" for n in g.npcs) and g.karma <= -60,
   "фляга подменена — мэр пьёт мятный чай, карма −60")
go(g, "junktown_casino")
c0 = g.inventory.count("крышки")
talk(g, "gizmo"); say(g, "Мэр мёртв"); say(g, "...")
ok(g.inventory.count("крышки") - c0 == 500 and g.stage("sq_gizmo") == 100, "Гизмо заплатил пятьсот")
go(g, "junktown_hall")
ok(not any(n.npc_id == "mayor_darkwater" for n in g.npcs), "мэра нет и после возвращения")

# 3. мир
g = fresh()
offer(g)
g.player.skills["speech"] = 80
talk(g, "gizmo"); say(g, "Красноречие"); say(g, "Передам")
go(g, "junktown_hall")
talk(g, "mayor_darkwater"); say(g, "мир"); say(g, "...")
ok(g.flags.get("gizmo_treaty") and g.stage("sq_gizmo") == 100, "Красноречие: мэр и Гизмо договорились")

# ===================================================== Кровь на балахонах
g = fresh("junktown")
talk(g, "jt_woman"); say(g, "бледная"); say(g, "Дай сюда")
ok(g.stage("sq_robes") == 10 and g.inventory.has("записка из балахона"), "Дина отдала записку из балахона")
go(g, "junktown_hall")
talk(g, "mayor_darkwater"); say(g, "детей Джанктауна"); say(g, "...")
go(g, "junktown")
ok(g.flags.get("robes_mayor") and not any(n.npc_id == "cult_recruiter" for n in g.npcs) and any(n.npc_id == "jt_kid" for n in g.npcs),
   "мэр устроил засаду у южных ворот: Офира выгнали, Пип дома")

g = fresh("junktown")
talk(g, "jt_woman"); say(g, "бледная"); say(g, "Дай сюда")
talk(g, "cult_recruiter"); say(g, "Чистые"); say(g, "Двести"); say(g, "...")
fr(g)
ok(g.flags.get("robes_sold") and not any(n.npc_id == "jt_kid" for n in g.npcs) and g.karma <= -80, "продал записку — Пипа увезли, карма −80")
talk(g, "jt_woman")
ok(g.dialogue.active_node == "r_lost", "Дина трёт чистый балахон: «он ушёл сам»")

g = fresh("junktown")
g.player.skills["speech"] = 60
talk(g, "jt_woman"); say(g, "бледная"); say(g, "Дай сюда")
talk(g, "cult_recruiter"); say(g, "Чистые"); say(g, "Беги"); say(g, "...")
ok(g.flags.get("robes_flee") and g.stage("sq_robes") == 100, "Красноречие: Офир сбежал, фургон уехал пустым")

# ===================================================== Последняя стена
g = fresh()
talk(g, "gambler_jt_b"); say(g, "Сколько ты должен"); say(g, "разберусь")
ok(g.stage("sq_fred") == 10, "Фред ставит стены")
g.player.skills["speech"] = 70
talk(g, "croupier"); say(g, "Кости"); say(g, "Отдай"); say(g, "Спасибо")
fr(g)
ok(g.inventory.has("кости Гизмо") and "кости Гизмо" not in g.pocket("croupier") and g.stage("sq_fred") == 50,
   "Вера отдала кости — в её кармане их больше нет")
talk(g, "gizmo"); say(g, "Твои кости"); say(g, "Купчая"); say(g, "...")
talk(g, "gambler_jt_b"); say(g, "Купчая"); say(g, "Удачи")
ok(g.stage("sq_fred") == 100 and g.flags.get("fred_home"), "Гизмо вернул купчую — Фред идёт к жене")

g = fresh()
talk(g, "gambler_jt_b"); say(g, "Сколько ты должен"); say(g, "разберусь")
ok("кости Гизмо" in g.pocket("croupier"), "кости — в кармане у Веры (можно стащить)")
g.inventory.add("кости Гизмо", 1)
go(g, "junktown_hall")
talk(g, "mayor_darkwater"); say(g, "со свинцом"); say(g, "...")
ok(g.flags.get("dice_exposed") and g.stage("sq_fred") == 100, "мэр списал долги по костям")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
