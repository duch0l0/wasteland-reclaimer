"""
Звёзды городов (docs/city_plan.md, этап 3): Гизмо и его статуя, Мать-Змея и дочь из Ниптона, Сет и море,
Мамаша Кейт и «Упрямая Мэри», Декер и последняя страница гроссбуха — выборы, изменения города, эпилог.

    .venv/bin/python tests/test_stars.py
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


def epilogue_has(g, text):
    for s in SLIDES["epilogue"]["slides"]:
        for p in s.get("parts", []):
            if text in p["text"] and g.check_condition(p.get("if", {})):
                return True
    return False


# ---- Гизмо: статуя «ровно такой»
g = Game(intro=False)
go(g, "junktown_casino")
talk(g, "gizmo"); say(g, "о себе"); say(g, "чего ты хочешь"); say(g, "Отнесу")
ok(g.inventory.has("эскиз статуи Гизмо"), "Гизмо отдал эскиз: стройный, с перстом")
go(g, "junktown")
talk(g, "jt_tinker"); say(g, "статую"); say(g, "настоящего"); say(g, "...")
go(g, "junktown")
ok(g.flags.get("gizmo_statue_true") and any(o.get("changed") and o["name"] == "cu_statue" for o in g.level.objects),
   "посреди Джанктауна — Гизмо из поршней, «ровно такой»")
ok(epilogue_has(g, "Ровно такой"), "строка в эпилоге")

# ---- Мать-Змея: Роуз из Ниптона
g = Game(intro=False)
go(g, "vegas_den")
talk(g, "mother_snake"); say(g, "откуда ты"); say(g, "...")
g.flags["know_cult_west"] = True
talk(g, "mother_snake"); say(g, "Роуз"); say(g, "Марипозе"); say(g, "...")
ok(g.flags.get("snakes_reformed") and epilogue_has(g, "рыжий волос"), "Змеи больше не продают людей — Мать порвала книгу")

# ---- Сет: море с Каталины
g = Game(intro=False)
go(g, "necropolis_hall")
g.flags["know_v12_truth"] = True
talk(g, "set"); say(g, "по морю"); say(g, "...")
go(g, "catalina")
talk(g, "fisher_ana"); say(g, "морской воды"); say(g, "Передам")
go(g, "necropolis_hall")
talk(g, "set"); say(g, "привёз вам море"); say(g, "...")
ok(g.flags.get("set_sea") and epilogue_has(g, "пахло солью"), "вышка №12 всё ещё на посту — бутылка моря на столе Сета")

# ---- Кейт: «Упрямая Мэри» — Билли
g = Game(intro=False)
go(g, "needles")
g.flags.update({"ferry_done": True, "billy_turned": True})
talk(g, "kate"); say(g, "Не устала"); say(g, "Отдай ему паром"); say(g, "...")
ok(g.flags.get("kate_retired") and epilogue_has(g, "Билли водил"), "ключ от мотора — Билли, Кейт на берегу")

# ---- Декер: выкуп
g = Game(intro=False)
go(g, "hub_old")
g.inventory.add("гроссбух Декера", 1)
g.item_action("гроссбух Декера")[1]()
g.close_terminal()
ok(g.flags.get("know_decker_ransom"), "последняя страница гроссбуха: «ВЫКУП»")
g.inventory.add("крышки", 200)
talk(g, "decker"); say(g, "Выкуп"); say(g, "Двести"); say(g, "...")
ok(g.flags.get("decker_ransom_paid") and g.karma >= 25 and epilogue_has(g, "сотней имён"), "двести в выкуп — Декер запишет ещё одно имя")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
