"""
Ниптон: «Луис из Примма» (клетка в шахте → мать в Примме), «Честная клетка» (Ирма и вдова Грейс),
«Ярмарка без жребия» (город учится смеяться; бусы Мэри Хоторн для Кэла) — навыки, вещи, связь с Приммом.

    .venv/bin/python tests/test_npquests.py
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



def fresh(lid="nipton_mine"):
    g = Game(intro=False)
    g.player.max_hp = g.player.hp = 10 ** 5
    go(g, lid)
    return g


# ===================================================== Луис из Примма
g = fresh()
talk(g, "np_captive"); say(g, "вытащу"); say(g, "вернусь")
ok(g.stage("sq_luis") == 10, "мальчишка из Примма в клетке")
g.inventory.add("отмычка", 1)
talk(g, "np_captive"); say(g, "вытащу"); say(g, "вскрыть"); say(g, "Беги")
fr(g)
ok(g.stage("sq_luis") == 50 and not any(n.npc_id == "np_captive" for n in g.npcs), "клетка вскрыта, Луис бежит")
go(g, "nipton_mine")
ok(not any(n.npc_id == "np_captive" for n in g.npcs), "клетка пуста и после возвращения")
go(g, "primm_bison")
c0 = g.inventory.count("крышки")
talk(g, "pr_manager"); say(g, "Луис свободен"); say(g, "...")
ok(g.stage("sq_luis") == 100 and g.inventory.count("крышки") - c0 == 150, "Луис дома у Риты в Примме")
talk(g, "pr_manager")
ok(g.dialogue.active_node == "lu_home", "Луис выдаёт ключи постояльцам")

g = fresh()
g.player.skills["speech"] = 60
talk(g, "np_captive"); say(g, "вытащу"); say(g, "вернусь")
talk(g, "cult_guard_np_b"); say(g, "помнишь"); say(g, "Красноречие"); say(g, "...")
fr(g)
ok(g.flags.get("luis_free") and not any(n.npc_id == "cult_guard_np_b" for n in g.npcs), "Красноречие: шахтёр из Сёрчлайта открыл клетку и ушёл")

g = fresh()
talk(g, "np_captive"); say(g, "вытащу"); say(g, "вернусь")
g.inventory.add("крышки", 250)
talk(g, "brother_t"); say(g, "Продай"); say(g, "...")
ok(g.flags.get("luis_bought") and g.flags.get("luis_free"), "выкупил у брата Т. — деньги ушли культу")

g = fresh()
g.flags["grooms_turned"] = True
g.sync_story()
ok(g.flags.get("luis_free"), "«женихи» открыли клетки — Луис свободен")

# ===================================================== Честная клетка
g = fresh("nipton_camp")
talk(g, "groom_c"); say(g, "осталась"); say(g, "Как тебя звали"); say(g, "Понимаю")
ok(g.stage("sq_irma") == 10, "её звали Ирма")
go(g, "nipton")
talk(g, "grace_widow"); say(g, "Ирма"); say(g, "Отнесу")
ok(g.stage("sq_irma") == 50 and g.inventory.has("платок Ирмы"), "Грейс отдала платок с васильками")
go(g, "nipton_camp")
talk(g, "groom_c"); say(g, "платок")
opts = [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]
ok(not any("Жребия больше нет" in o for o in opts), "пока жребий жив — домой не позвать")
say(g, "строчку"); say(g, "Передам")
go(g, "nipton")
talk(g, "grace_widow"); say(g, "Письмо"); say(g, "...")
ok(g.flags.get("irma_letter") and g.stage("sq_irma") == 100, "«Вышей мне ещё» — Грейс ждёт")

g = fresh("nipton_camp")
g.flags["nipton_mayor_exposed"] = True
talk(g, "groom_c"); say(g, "осталась"); say(g, "Как тебя звали"); say(g, "Понимаю")
go(g, "nipton")
talk(g, "grace_widow"); say(g, "Ирма"); say(g, "Отнесу")
go(g, "nipton_camp")
talk(g, "groom_c"); say(g, "платок"); say(g, "Жребия больше нет"); say(g, "...")
go(g, "nipton")
talk(g, "grace_widow")
ok(g.flags.get("irma_home") and g.dialogue.active_node == "ir_g_home", "Ирма дома: ругаются из-за ведра")

g = fresh("nipton_camp")
talk(g, "groom_c"); say(g, "осталась"); say(g, "Как тебя звали"); say(g, "Понимаю")
go(g, "nipton")
talk(g, "grace_widow"); say(g, "Ирма"); say(g, "Отнесу")
talk(g, "grace_widow"); say(g, "умерла"); say(g, "...")
ok(g.flags.get("irma_dead_lie") and g.karma <= -25, "солгал «умерла» — Грейс продаёт участок")

# ===================================================== Ярмарка без жребия
g = fresh("nipton")
talk(g, "np_crier")
opts = [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]
ok(not any("вместо жребия" in o for o in opts), "пока жребий жив — ярмарки без жребия нет")
g.dialogue.active_node = None
g.flags["nipton_mayor_exposed"] = True
talk(g, "np_crier"); say(g, "вместо жребия"); say(g, "Конкурс пирогов"); say(g, "бабка Мэй"); say(g, "..."); say(g, "...")
ok(g.stage("sq_fair") == 100 and g.inventory.has("бусы Мэри Хоторн"), "пирог Мэй победил — бусы Мэри Хоторн")
go(g, "nipton_camp")
talk(g, "groom_cal"); say(g, "Бусы"); say(g, "...")
ok(g.flags.get("cal_beads"), "Кэл надел бусы матери")

g = fresh("nipton")
g.flags["nipton_mayor_exposed"] = True
g.player.skills["guns"] = 10
talk(g, "np_crier"); say(g, "вместо жребия"); say(g, "бутылкам")
opts = [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]
ok(not any("Десять из десяти" in o for o in opts), "без Стрельбы — только «как получится»")
say(g, "как получится"); say(g, "..."); say(g, "...")
ok(g.flags.get("fair_chicken") and g.stage("sq_fair") == 100, "две бутылки и курица — площадь хохочет")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
