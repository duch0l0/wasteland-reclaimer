"""
Карма и репутация: поступки меняют карму и отношение городов, свои платят меньше,
жители пересказывают слухи о делах героя (эхо между городами), звания за особые дела, кражи и убийства.

    .venv/bin/python tests/test_reputation.py
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


g = Game(intro=False)
g.player.max_hp = g.player.hp = 10 ** 6
ok(g.karma == 0 and g.karma_title() == "Бродяга", "начало: карма 0, «Бродяга»")

# поступок → карма и репутация города (один раз)
g.flags["clean_slate_off"] = True
g.sync_story(); g.sync_story()
ok(g.karma == 60 and g.rep("zzyzx") == 45,
   f"отключил «Чистый лист»: карма {g.karma}, Зайзикс {g.rep('zzyzx')} (поступок +20 и задание города +25)")
g.flags["nipton_bribed"] = True
g.sync_story()
ok(g.karma == 10 and g.rep("nipton") == -30, "взял взятку в Ниптоне: карма вниз, Ниптон недоволен")

# выполненное задание города — +25
g.set_stage("sq_hub", 100)
ok(g.rep("hub") == 25, "задание Хаба выполнено — Хаб +25")

# цены: свой — скидка
g.enter_location("hub"); fr(g)
g.slides = None
trader = next(t for t in g.traders if t == "arms_seller")
g.open_trade(trader)
p0 = dict((r[0], r[2]) for r in g.trade_rows())
g.trade = None
g.flags["rep_hub"] = 60
g.open_trade(trader)
p1 = dict((r[0], r[2]) for r in g.trade_rows())
g.trade = None
ok(p1["10-мм пистолет"] < p0["10-мм пистолет"], f"друг Хаба покупает дешевле ({p0['10-мм пистолет']} → {p1['10-мм пистолет']})")

# слухи: эхо поступков и реакция на репутацию
npc = next(n for n in g.npcs if n.npc_id not in ("dog",))
lines = g.bark_lines(npc)
ok(any("Зайзиксе родился ребёнок" in l for l in lines), "в Хабе пересказывают, что сделал герой в Зайзиксе")
ok(any("тебя знают" in l for l in lines), "друга Хаба узнают на улице")
ok(not any("оазис снова полон" in l for l in lines), "о несделанном не болтают")

# звания
g.flags["ferry_done"] = True
ok(any(t[0] == "ferryman" for t in g.titles()), "звание «Паромщик»")
g.flags["karma"] = 300
ok(g.karma_title() == "Хранитель пустоши", "карма 300 — «Хранитель пустоши»")

# убийство жителя
r0, k0 = g.rep("hub"), g.karma
g.on_npc_killed("street_kid")
ok(g.rep("hub") == r0 - 30 and g.karma == k0 - 25, "убил жителя: Хаб −30, карма −25")

# реплика с условием по репутации (диалоговые условия)
ok(g.check_condition({"rep_ge": ["hub", 25]}) and not g.check_condition({"rep_lt": ["hub", 0]}), "условия rep_ge / rep_lt")
ok(g.check_condition({"karma_ge": 200}) and g.check_condition({"title": "ferryman"}), "условия karma_ge / title")

# журнал: вкладка репутации рисуется
g.journal_open = True
g.journal_tab = "rep"
fr(g)
g.handle_key(pygame.K_TAB)
ok(g.journal_tab == "quests", "Tab переключает вкладки журнала")
for _ in range(20):
    g.handle_key(pygame.K_DOWN)
fr(g)
ok(g.journal_scroll >= 0, "журнал листается")


# импланты у хирургов: дорого, навсегда, один раз
g2 = Game(intro=False)
g2.enter_location("junktown_clinic"); fr(g2)
g2.slides = None
g2.inventory.add("крышки", 5000)
hp0 = g2.player.max_hp


def ask(g, nid, part):
    g.dialogue.active_node = None
    npc = next(n for n in g.npcs if n.npc_id == nid)
    for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1)):
        c = (tile_of(npc)[0] + dx, tile_of(npc)[1] + dy)
        if not g.level.is_wall(*c):
            g.player.rect.topleft = rect_pos_for_tile(g.player, c)
            break
    g.handle_key(pygame.K_e)
    for p_ in ("операции", part):
        opts = [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]
        idx = next((k for k, l in enumerate(opts) if p_ in l), None)
        if idx is None:
            return False
        g.handle_key(pygame.K_1 + idx)
        fr(g, 1)
    g.dialogue.active_node = None
    return True


ok(ask(g2, "anna_shaw", "сердце") and g2.player.max_hp == hp0 + 15 and g2.inventory.count("крышки") == 3800,
   "Анна Шоу: усиленное сердце — +15 HP за 1200")
ok(not ask(g2, "anna_shaw", "сердце"), "второй раз то же сердце не поставить")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
