"""
Примм и Бейкер: «Отчаянный» (горки: проверить рельсы или спешить), «Машина смерти» (код — дата засады с таблички),
«Улыбка папы» (три дня ломки, время и поддержка решают), «Термометр» (градусы бога или жара).

    .venv/bin/python tests/test_pbquests.py
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



from src.game.clock import DAY  # noqa: E402


def fresh(lid):
    g = Game(intro=False)
    g.player.max_hp = g.player.hp = 500
    go(g, lid)
    return g


# ---- «Отчаянный»
g = fresh("primm")
talk(g, "pr_mechanic"); say(g, "горки"); say(g, "Найду ток")
g.inventory.add("топливо", 5)
talk(g, "pr_mechanic"); say(g, "Ток для горок"); say(g, "Пять канистр"); say(g, "...")
ok(g.stage("sq_coaster") == 50, "мотор горок гудит")
g.player.skills["science"] = 70
talk(g, "pr_mechanic"); say(g, "Запускай"); say(g, "проверю рельсы"); say(g, "...")
go(g, "primm")
ok(g.flags.get("coaster_ok") and any(o.get("changed") for o in g.level.objects), "рельсы проверены — дети летают, табличка у горок")

g = fresh("primm")
g.flags.update({"coaster_job": True, "coaster_power": True})
talk(g, "pr_mechanic"); say(g, "Запускай"); say(g, "сейчас"); say(g, "...")
ok(g.flags.get("coaster_crash"), "не проверил — Вик висит вниз головой, горки заколочены")

# ---- «Машина смерти»
g = fresh("primm_vikki")
talk(g, "barkeep_slim"); say(g, "Багажник"); say(g, "14 февраля"); say(g, "...")
ok(g.flags.get("bc_jammed"), "неверный код — замок заклинило")
talk(g, "barkeep_slim")
ok(not any("попробовать код" in g.dialogue.option_label(o) for o in g.dialogue.visible_options()), "пока заклинило — не попробовать")
g.dialogue.active_node = None
go(g, "primm")
g.inventory.add("крышки", 20)
talk(g, "pr_mechanic"); say(g, "расклинишь"); say(g, "...")
go(g, "primm_vikki")
ok(any(t["id"] == "doc:doc_bc_placard" for t in g.level.terminals), "табличка у машины читается")
talk(g, "barkeep_slim"); say(g, "Багажник"); say(g, "23 мая 1934"); say(g, "...")
take(g, "машина Бонни и Клайда")
ok(g.stage("sq_bonnie") == 100 and g.inventory.has("фото Бонни Паркер"), "код — дата засады: «последний куш» и фото Бонни")

# ---- «Улыбка папы»
def smile(g, support):
    talk(g, "motel_mom"); say(g, "муж"); say(g, "Узнаю")
    go(g, "baker_crypt")
    talk(g, "oskar"); say(g, "вернулся"); say(g, "Спасибо")
    go(g, "baker_motel_2f")
    g.inventory.add("чистая вода", 3)
    talk(g, "motel_mom"); say(g, "Три дня"); say(g, "Вернусь")
    g.advance_time(DAY + 60)
    if support:
        talk(g, "motel_mom"); say(g, "Держитесь"); say(g, "Не открывайте")
    g.advance_time(2 * DAY + 60)


g = fresh("baker_motel_2f")
smile(g, True)
talk(g, "motel_mom")
ok(g.flags.get("smile_back") and g.dialogue.active_node == "sm_back", "поддержал мать — на третью ночь он заплакал: «Мэгги»")
g.dialogue.active_node = None
g = fresh("baker_motel_2f")
smile(g, False)
ok(g.flags.get("smile_lost") and not g.flags.get("smile_back"), "пропал на три дня — дверь выломана, улыбка шире")

# ---- «Термометр»
g = fresh("baker")
talk(g, "nick"); say(g, "Термометр"); say(g, "Посмотрю")
g.player.skills["science"] = 50
talk(g, "baker_kid"); say(g, "на самом деле"); say(g, "Наука"); say(g, "жара")
talk(g, "nick"); say(g, "работает"); say(g, "...")
ok(g.stage("sq_thermo") == 100 and g.flags.get("thermo_done"), "сорок девять градусов — Термометр снова не врёт")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
