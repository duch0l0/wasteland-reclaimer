"""
Охранник Красного каравана (docs/city_plan.md, этап 2): рейс из трёх событий с выбором и навыками,
плата за довезённый груз, герой приезжает в город назначения; путник предупреждает о засаде; пять чистых рейсов — партнёр.

    .venv/bin/python tests/test_caravan.py
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
    g.player.max_hp = g.player.hp = 500
    go(g, "hub")
    return g


def opts(g):
    return [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]


# ---- рейс в Джанктаун: всё по навыкам — груз цел, плата полная
g = fresh()
g.player.skills.update({"guns": 80, "science": 60, "survival": 60, "medicine": 50})
talk(g, "crimson_boss"); say(g, "охранником")
ok(not any("Вегас" in o for o in opts(g)), "Вегас — только если о нём знаешь")
g.dialogue.active_node = None
g.caravan_start("junktown", ["ambush", "wheel", "storm"])
ok(g.dialogue.is_active() and "Засада" in g.dialogue.current_node()["text"], "день первый — засада на перевале")
say(g, "Стрельба"); say(g, "Дальше")
say(g, "Наука"); say(g, "Дальше")
say(g, "Выживание"); say(g, "Дальше")
c0 = g.inventory.count("крышки")
say(g, "Сдать груз")
fr(g)
ok(g.loc.id == "junktown" and g.inventory.count("крышки") - c0 == 90 and g.flags.get("caravan_runs") == 1,
   "караван в Джанктауне: три вьюка из трёх, 90 крышек")

# ---- без навыков: груз теряется, плата меньше
g = fresh()
for k in g.player.skills:
    g.player.skills[k] = 10
g.caravan_start("needles", ["ambush", "storm", "scorpions"])
say(g, "Держать оборону"); say(g, "Дальше")
say(g, "Переждать"); say(g, "Дальше")
say(g, "Обойти"); say(g, "Дальше")
c0 = g.inventory.count("крышки")
say(g, "Сдать груз")
fr(g)
ok(g.loc.id == "needles" and g.inventory.count("крышки") == c0 and not g.flags.get("caravan_runs"),
   "все три вьюка потеряны — ни крышки, рейс не засчитан")

# ---- путник с водой предупреждает о засаде
g = fresh()
g.inventory.add("чистая вода", 1)
g.caravan_start("junktown", ["thirsty", "ambush", "wheel"])
say(g, "чистой воды"); say(g, "Дальше")
ok("Путник был прав" in g.dialogue.current_node()["text"] and len(opts(g)) == 1, "засады нет — караван идёт руслом")
say(g, "Дальше")

# ---- контрабанда культа: сказать Крэйн
g = fresh()
g.caravan_start("junktown", ["smuggle", "stowaway", "wheel"])
say(g, "Сказать Крэйн"); say(g, "Дальше"); say(g, "помощники"); say(g, "Дальше"); say(g, "Перегрузить"); say(g, "Дальше"); say(g, "Сдать")
fr(g)
ok(g.flags.get("caravan_smuggle_reported") and g.flags.get("caravan_kid"), "контрабанда замечена, мальчишка-заяц взят в помощники")
go(g, "hub")
c0 = g.inventory.count("крышки")
talk(g, "crimson_boss"); say(g, "товар культа"); say(g, "...")
ok(g.inventory.count("крышки") - c0 == 100, "Крэйн выгнала погонщика культа — сотня за имя каравана")

# ---- пять чистых рейсов — партнёр
g = fresh()
g.player.skills.update({"guns": 80, "science": 60, "survival": 60})
for _ in range(5):
    go(g, "hub")
    g.caravan_start("junktown", ["ambush", "wheel", "storm"])
    say(g, "Стрельба"); say(g, "Дальше"); say(g, "Наука"); say(g, "Дальше"); say(g, "Выживание"); say(g, "Дальше"); say(g, "Сдать")
    fr(g)
ok(g.flags.get("caravan_partner") and g.flags.get("caravan_runs") == 5, "пять чистых рейсов — партнёр Красного каравана")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
