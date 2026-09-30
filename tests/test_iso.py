"""
Изометрия и Барстоу — без окна:
проекция туда-обратно, 8 направлений; Барстоу на карте мира; переходы трасса ↔ депо ↔ центр,
тайная дверь в святилище (только с брошью Ордена); клик по земле и по NPC; крыша снимается
внутри; квест Розы «Зачистка Барстоу» (зачистка обоих районов -> награда); бой с гулями и тела;
сохранение и загрузка в изометрии; скорость кадра.

    .venv/bin/python tests/test_iso.py
"""
import os
import random
import sys
import tempfile
import time

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import pygame  # noqa: E402

MOUSE = [(-50, -50)]
PRESSED = [False]
pygame.mouse.get_pos = lambda: MOUSE[0]
pygame.mouse.get_pressed = lambda num_buttons=3: (PRESSED[0], False, False)
pygame.mouse.get_focused = lambda: True

from src.game import Game, saveload  # noqa: E402
from src.combat import tile_of, rect_pos_for_tile  # noqa: E402
from src.entities import sprite_of  # noqa: E402
from src.iso import w2i, i2w, IsoAnimator, screen_dir  # noqa: E402

saveload.SAVE_DIR = tempfile.mkdtemp()
failed = []


def ok(cond, msg):
    print(("OK   " if cond else "FAIL ") + msg)
    if not cond:
        failed.append(msg)


def fr(g, n=1):
    for _ in range(n):
        g.update(16)
        g.draw()
        if g.perk_choices:
            g.handle_key(pygame.K_1)


def calm(g):
    for e in g.enemies:
        e.aggro = 0


def click_world(g, wx, wy, button=1):
    cx, cy = g.cam.p(wx, wy)
    pos = (int(cx * g.zoom), int(cy * g.zoom))
    MOUSE[0] = pos
    g.handle_click(pos, button)


def step_on_portal(g, to):
    p = next(p for p in g.level.portals if p["to"] == to)
    tile = sorted(p["tiles"])[0]
    here = g.loc.id
    for _ in range(10):
        g.player.rect.topleft = rect_pos_for_tile(g.player, tile)
        fr(g, 1)
        if g.loc.id != here:
            break
    calm(g)


def say(g, part):
    opts = [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]
    idx = next((i for i, lbl in enumerate(opts) if part in lbl), None)
    assert idx is not None, f"нет реплики «{part}» среди {opts}"
    g.handle_key(pygame.K_1 + idx)
    fr(g, 1)


def talk(g, npc_id):
    npc = next(n for n in g.npcs if n.npc_id == npc_id)
    nx, ny = tile_of(npc)
    for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1), (1, 1)):
        if not g.level.is_wall(nx + dx, ny + dy):
            g.player.rect.topleft = rect_pos_for_tile(g.player, (nx + dx, ny + dy))
            break
    g.handle_key(pygame.K_e)
    assert g.dialogue.is_active(), f"разговор с {npc_id} не начался"


def wipe_out(g):
    """Перебить всех гулей района (как будто зачистили в бою), толпы из домов — тоже вышли."""
    for h in getattr(g.level, "hordes", []):
        h["done"] = True
    for e in list(g.enemies):
        if e.alive:
            e.apply_damage(9999)
            g.on_enemy_killed(e)
    fr(g, 3)


# ------------------------------------------------------------ проекция
x, y = i2w(*w2i(123.0, 456.0))
ok(abs(x - 123) < 1e-6 and abs(y - 456) < 1e-6, "проекция мир -> экран -> мир обратима")
ok(screen_dir(1, 1) == "s" and screen_dir(-1, -1) == "n" and screen_dir(1, -1) == "e", "8 направлений по экрану")

random.seed(3)
g = Game(intro=False)
ok("barstow" not in g.worldmap.known_list(), "Барстоу не на карте мира — туда ходит наёмник")
calm(g)
# ------------------------------------------------------------ Пятнадцатая: нанять Дэкса
hero_pos = tuple(g.player.rect.topleft)
hero_hp = g.player.hp
g.inventory.add("крышки", 120)
talk(g, "dex")
say(g, "Кто ты?")
say(g, "Караван нужен")
say(g, "Нанимаю")
say(g, "Держи сотню")
hero_pos = tuple(g.player.rect.topleft)   # здесь герой и будет ждать
say(g, "Удачи, Дэкс")
ok(g.slides and g.slides["id"] == "merc_go", "слайды «Тем временем» — Дэкс уходит в Барстоу")
g.handle_key(pygame.K_ESCAPE)
fr(g, 2)
ok(g.merc_mode and g.loc.id == "barstow" and g.player.weapon == "rifle", "играем за Дэкса: Барстоу, винтовка")
ok(g.inventory.has("охотничья винтовка") and not g.inventory.has("письмо деда"), "у Дэкса свой рюкзак")
ok(g.stage("sq_merc") == 20, "журнал: Дэкс в Барстоу")
g.player.max_hp = g.player.hp = 900
calm(g)
ok(g.cam.iso and getattr(g.level, "iso", False), "Барстоу — изометрический")
ok(isinstance(g.player.anim, IsoAnimator), "герой — в 8 направлениях")
fr(g, 5)

# ------------------------------------------------------------ клик по земле, крыша мотеля
g.player.rect.topleft = rect_pos_for_tile(g.player, (6, 13))   # в экшене ходят на WASD, ЛКМ — огонь
fr(g, 120)
ok(tile_of(g.player) == (6, 13), "Дэкс в конторе мотеля")
roof = g.level.roof_over((6, 13))
ok(roof is not None and roof["alpha"] == 0, "внутри конторы крыша снята")

# ------------------------------------------------------------ Роза: работа
talk(g, "rose")
say(g, "Могу помочь с гулями")
say(g, "Договорились")
ok(g.stage("sq_barstow") == 10, "Роза дала работу: зачистить депо и центр")
g.dialogue.close()

# ------------------------------------------------------------ депо: переход, терминал, зачистка
step_on_portal(g, "barstow_depot")
ok(g.loc.id == "barstow_depot", "дорога на север ведёт в депо")
g.open_terminal("barstow_depot")
g.term_open_entry(0)
g.close_terminal()
ok(g.flags.get("know_depot_rail"), "журнал депо: состав West Tek на «Бейкер-7»")
wipe_out(g)
ok(g.flags.get("barstow_depot_cleared") and g.stage("sq_barstow") == 50, "депо зачищено — журнал: один район")
step_on_portal(g, "barstow")
ok(g.loc.id == "barstow", "из депо — обратно на трассу")

# ------------------------------------------------------------ центр: бой, тайная дверь, зачистка
step_on_portal(g, "barstow_center")
ok(g.loc.id == "barstow_center", "дорога на юг ведёт в центр")
# экшен: стрельба в реальном времени
a = g.action
ok(a.active, "в Барстоу за Дэкса — экшен-режим")
f0 = min((e for e in g.enemies if e.alive and not getattr(e, "awake", False)),
         key=lambda e: abs(tile_of(e)[0] - 21) + abs(tile_of(e)[1] - 15))
fx, fy = tile_of(f0)
spot = next((fx + dx, fy + dy) for dx, dy in ((3, 0), (-3, 0), (0, 3), (0, -3), (2, 2)) if not g.level.is_wall(fx + dx, fy + dy))
g.player.rect.topleft = rect_pos_for_tile(g.player, spot)
g.snap_camera()
fr(g, 2)
PRESSED[0] = True
for _ in range(240):
    if not f0.alive:
        break
    cx, cy = g.cam.p(*f0.rect.center)
    MOUSE[0] = (int(cx * g.zoom), int(cy * g.zoom))
    fr(g, 1)
PRESSED[0] = False
ok(not f0.alive and g.level.corpses, "Дэкс застрелил гуля из автомата, тело лежит")
ok(g.player.level_sys.xp == 0 and g.player.level_sys.level == 4, "за Дэкса опыт не начисляется")
from src.action import GUNS, ACTION_HP  # noqa: E402
ok({k: v // GUNS["ar"].dmg[0] for k, v in ACTION_HP.items() if k != "mutant"} ==
   {"ghoul_runner": 2, "feral": 3, "rad_mutant": 5}, "бегун — 2 пули, гуль — 3, светящийся — 5")
ok(a.ammo["ar"] < 30, f"автомат тратит магазин ({a.ammo['ar']}/30)")
fr(g, 10)   # окна новых перков после зачисток — закрыть
a.ammo["ar"] = 1
PRESSED[0] = True
MOUSE[0] = (300, 200)
for _ in range(20):
    fr(g, 1)
    if a.reload_left:
        break
PRESSED[0] = False
ok(a.reload_left > 2700, "магазин кончился — перезарядка 3 с")
fr(g, 200)
ok(a.ammo["ar"] == 30 and not a.reload_left, "автомат перезаряжен")
a.switch("sg")
a.ammo["sg"] = 0
a.reload()
fr(g, 160)
ok(0 < a.ammo["sg"] < 8 and a.reload_left, "дробовик: патроны закладываются по одному (5 с)")
fr(g, 200)
ok(a.ammo["sg"] == 8, "дробовик заряжен: 8 выстрелов")
h = g.level.hordes[0]
x0, y0, x1, y1 = h["trigger"]
g.player.rect.topleft = rect_pos_for_tile(g.player, (x0 + 1, y1))
alive0 = sum(e.alive for e in g.enemies)
fr(g, 180)
ok(h["done"] and sum(e.alive for e in g.enemies) >= alive0 + 15, "толпа гулей вывалилась из отеля (15+)")
ok(g.can_save() is not None, "пока гонятся — сохраняться нельзя")
door = next(p for p in g.level.portals if p["to"] == "barstow_order")
g.player.rect.topleft = rect_pos_for_tile(g.player, sorted(door["tiles"])[0])
fr(g, 3)
ok(g.loc.id == "barstow_center", "без броши Ордена тайная дверь не открывается")
g.inventory.add("знак Ордена Тайн", 1)
g.player.rect.topleft = rect_pos_for_tile(g.player, (6, 30))
fr(g, 2)
step_on_portal(g, "barstow_order")
ok(g.loc.id == "barstow_order", "с брошью — тайная дверь ведёт в святилище Ордена")
g.open_terminal("order")
g.term_open_entry(0)
g.close_terminal()
ok(g.flags.get("order_found"), "терминал Ордена прочитан")
step_on_portal(g, "barstow_center")
wipe_out(g)
ok(g.flags.get("barstow_center_cleared") and g.stage("sq_barstow") == 90, "центр зачищен — вернуться к Розе")
step_on_portal(g, "barstow")
talk(g, "rose")
say(g, "Депо и центр чисты")
ok(g.stage("sq_barstow") == 100 and g.inventory.count("крышки") >= 150, "Роза расплатилась")
g.dialogue.close()

# ------------------------------------------------------------ сохранение посреди контракта
wipe_out(g)   # за Дэксом гонятся гули трассы — сохраниться можно, когда вокруг тихо
fr(g, 10)
ok(g.save_game("4"), "сохранение за Дэкса")
g3 = Game(intro=False)
g3.load_game("4")
fr(g3, 2)
ok(g3.merc_mode and g3.other_profile and g3.other_profile["inventory"].get("письмо деда"),
   "загрузка: снова Дэкс, герой ждёт со своим рюкзаком")

# ------------------------------------------------------------ домой: караван и доля
exit_tile = sorted(g.level.exits)[0]
g.player.rect.topleft = rect_pos_for_tile(g.player, exit_tile)
fr(g, 2)
ok(g.slides and g.slides["id"] == "merc_back", "выход с трассы — «Дорога домой»")
g.handle_key(pygame.K_ESCAPE)
fr(g, 2)
ok(not g.merc_mode and g.loc.id == "ruins" and tuple(g.player.rect.topleft) == hero_pos,
   "снова играем героем — там же, где он ждал")
ok(g.inventory.has("письмо деда") and not g.inventory.has("охотничья винтовка"), "у героя его рюкзак")
ok(any(n.npc_id == "rose" for n in g.npcs), "Роза с караваном — в Пятнадцатой")
talk(g, "dex")
say(g, "Спасибо, Дэкс")
ok(g.stage("sq_merc") == 100 and g.inventory.count("крышки") >= 150, "Дэкс отдал долю")
g.dialogue.close()
g.enter_location("barstow")   # дальше тест проверяет сохранение в изометрии уже героем
calm(g)

# ------------------------------------------------------------ сохранение
fr(g, 10)
ok(g.save_game("3"), "сохранение в Барстоу")
g2 = Game(intro=False)
g2.load_game("3")
fr(g2, 2)
ok(g2.loc.id == "barstow" and g2.cam.iso and isinstance(g2.player.anim, IsoAnimator),
   "загрузка возвращает в изометрический Барстоу")
ok(g2.flags.get("barstow_depot_cleared") and g2.stage("sq_barstow") == 100 and g2.stage("sq_merc") == 100,
   "зачистка и квесты сохраняются")
g2.enter_location("ruins")
fr(g2, 2)
ok(not g2.cam.iso and not isinstance(g2.player.anim, IsoAnimator), "в Пятнадцатой — прямой вид и прежний герой")

# ------------------------------------------------------------ скорость
g.enter_location("barstow_center")
g.player.rect.topleft = rect_pos_for_tile(g.player, (21, 19))
g.snap_camera()
fr(g, 5)
t0 = time.time()
fr(g, 60)
ms = (time.time() - t0) / 60 * 1000
ok(ms < 30, f"кадр в изометрии — {ms:.1f} мс")

print("\nВСЁ ОК" if not failed else f"\nПРОВАЛЕНО: {len(failed)}")
sys.exit(1 if failed else 0)
