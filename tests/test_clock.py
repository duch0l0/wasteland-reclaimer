"""
Игровое время (docs/city_plan.md, этап 4): часы, день недели, ночь; путь по карте съедает часы; сроки —
не успел, мир решает сам (Мило, Луис, лихорадка); ночные сеансы «Фокса», воскресная ярмарка Ниптона.

    .venv/bin/python tests/test_clock.py
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

g = Game(intro=False)
g.player.max_hp = g.player.hp = 500
go(g, "hub")
ok(g.clock_text() == "День 1 · пн 08:00" or g.clock_text().startswith("День 1 · пн 08:0"), f"начало: {g.clock_text()}")
t0 = g.time_min
for _ in range(60 * 1000 // 16 + 2):
    g.update(16)
ok(55 <= g.time_min - t0 <= 65, "минута реального времени — час игрового")

# ---- путь по карте
g.mode = "world"
g.worldmap.go_to("junktown") if hasattr(g.worldmap, "go_to") else None
t0 = g.time_min
from src.location import LOCATION_DEFS  # noqa: E402
import pygame as _pg  # noqa: E402
wm = g.worldmap
wm.start = _pg.Vector2(wm.pos)
wm.dest = _pg.Vector2(LOCATION_DEFS["junktown"]["world_pos"])
wm.target, wm.progress, wm.encounter_at = "junktown", 0.0, None
for _ in range(2000):
    g.update(16)
    if g.mode == "local":
        break
dist = wm.start.distance_to(wm.dest)
ok(g.loc.id == "junktown" and g.time_min - t0 >= dist * 1.2, f"дорога в Джанктаун: {dist:.0f} единиц — {(g.time_min - t0) // 60} ч")

# ---- срок: Мило продадут через три дня
g = Game(intro=False)
go(g, "vegas_snakes")
talk(g, "snake_gambler"); say(g, "выиграть"); say(g, "Сколько"); say(g, "придумаю")
left = g.deadline_left("sq_milo")
ok(left is not None and abs(left - 3 * DAY) < 120, f"срок пошёл: осталось {left // 60} ч")
g.journal_open, g.journal_sel = True, "sq_milo"
fr(g, 1)
g.journal_open = False
g.advance_time(3 * DAY + 10)
go(g, "vegas_snakes")
ok(g.flags.get("milo_sold") and g.stage("sq_milo") == 100 and not any(n.npc_id == "snake_gambler" for n in g.npcs),
   "не успел — Мило продали, его стола больше нет")

# ---- успел — срок снимается
g = Game(intro=False)
go(g, "nipton_mine")
g.inventory.add("отмычка", 1)
talk(g, "np_captive"); say(g, "вытащу"); say(g, "вскрыть"); say(g, "Беги")
g.advance_time(10 * DAY)
ok(not g.flags.get("luis_shipped") and g.deadline_left("sq_luis") is None, "Луис освобождён — фургон на запад не ушёл")

# ---- лихорадка: мать не дождалась
g = Game(intro=False)
go(g, "hub_old")
talk(g, "slum_mother"); say(g, "весь красный"); say(g, "найду"); say(g, "Пока нечего")
g.advance_time(4 * DAY + 5)
talk(g, "slum_mother")
ok(g.flags.get("fever_cult") and g.dialogue.active_node == "f_empty", "через четыре дня мать сама пошла к сестре Мирре")
g.dialogue.active_node = None

# ---- ночь: сеанс в «Фоксе» и отдых
g = Game(intro=False)
go(g, "necropolis")
g.flags["fox_truth"] = True
g.player.hp = 5
talk(g, "nc_old")
ok(not any("сеанс" in g.dialogue.option_label(o) for o in g.dialogue.visible_options()), "днём сеанса нет")
g.dialogue.active_node = None
g.advance_time((21 - g.game_hour()) * 60)
ok(g.is_night(), "21:00 — ночь")
t0 = g.time_min
talk(g, "nc_old"); say(g, "сеанс"); say(g, "смотреть"); say(g, "...")
ok(g.time_min - t0 == 120 and g.player.hp == g.player.hp_cap, "два часа кино — герой отдохнул")

# ---- воскресная ярмарка
g = Game(intro=False)
go(g, "nipton")
g.flags["fair_done"] = True
g.player.skills["guns"] = 80
g.advance_time(6 * DAY)
ok((g.game_day() - 1) % 7 == 6, "седьмой день — воскресенье")
c0 = g.inventory.count("крышки")
talk(g, "np_crier"); say(g, "Воскресенье"); say(g, "Десять из десяти"); say(g, "...")
ok(g.inventory.count("крышки") - c0 == 50, "победитель недели — 50 крышек")
talk(g, "np_crier")
ok(not any("Воскресенье" in g.dialogue.option_label(o) for o in g.dialogue.visible_options()), "второй раз за неделю — нельзя")
g.dialogue.active_node = None
g.advance_time(7 * DAY)
talk(g, "np_crier")
ok(any("Воскресенье" in g.dialogue.option_label(o) for o in g.dialogue.visible_options()), "в следующее воскресенье — снова")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
