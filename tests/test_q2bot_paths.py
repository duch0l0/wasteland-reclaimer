"""
Q2, часть 2 — бот идёт новыми путями сам (не диалог вручную, а сценарий бота):

  1. «Жёлтые треугольники» без противогаза: barge закрывается через Речную стражу (Морроу);
     ни Stuck, ни side_fails — раньше здесь стояло «без противогаза — 350 рад»;
  2. «Колокольня»: бот ждёт ночи (advance_time), поднимается и снимает катушку руками;
  3. «Отчаянный»: бот покупает пять канистр (по 5 крышек), а рельсы осматривает Абнер —
     пороги диалога 55/60/50, а не 70, как было в сценарии;
  4. «Вода для Арадеша»: матка не по зубам — бот идёт вторым путём (Ханы → Вик → насос),
     и квест всё равно 100, а не «тихая потеря» в отчёте.

    .venv/bin/python tests/test_q2bot_paths.py
"""
import importlib.util
import os
import sys
import tempfile

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
os.chdir(ROOT)

import pygame  # noqa: E402

pygame.mouse.get_pos = lambda: (-50, -50)
pygame.mouse.get_focused = lambda: True

_spec = importlib.util.spec_from_file_location("playthrough", os.path.join(ROOT, "tools", "playthrough.py"))
PT = importlib.util.module_from_spec(_spec)
sys.modules["playthrough"] = PT
_spec.loader.exec_module(PT)
SQ = PT.SQ

failed = []


def ok(cond, msg):
    print(("OK   " if cond else "FAIL ") + msg)
    if not cond:
        failed.append(msg)


def hero(lid, level=10, hp=120, weapon="assault", item="автомат", skill="guns", val=110):
    """Бот с героем «середины игры»: не умирает в первой стычке и не покупает лишнего."""
    b = PT.Bot(seed=7, sides=True)
    b.go(lid)
    g = b.g
    p = g.player
    p.level_sys.level = level
    p.max_hp = p.hp = hp
    p.skills[skill] = val
    p.weapon = weapon
    g.inventory.add(item, 1)
    g.inventory.add("патроны", 200)
    for n in ("металлическая броня", "шлем металлической брони"):
        g.inventory.add(n, 1)
    p.equipment["body"] = "металлическая броня"
    p.equipment["head"] = "шлем металлической брони"
    g.inventory.add("стимулятор", 8)
    return b, g


# ===================================================== 1. Баржа: бот без маски идёт к Морроу
b, g = hero("needles")
g.inventory.items.pop("крышки", None)                  # ни крышек на противогаз, ни маски
g.player.skills["speech"] = 20
b.chat("kate", "Что с рекой", "Что за баржа", "залить бочку цементом", "Нырну")
g.inventory.add("мешок цемента", 1)
ok(g.stage("sq_barge") == 10, "баржа взята: мешок цемента есть, противогаза нет")
SQ.needles_finish(b)
ok(g.stage("sq_barge") == 100 and g.flags.get("barge_cement_deal"),
   "бот без маски закрыл баржу через Морроу — 0 рад, цемент ушёл страже")
ok(not b.side_fails, f"ни одного провала в отчёте: {b.side_fails}")

# ===================================================== 2. Колокольня: бот ждёт ночи
b, g = hero("boneyard")
g.flags["time_min"] = (g.flags.get("time_min", 0) // 1440) * 1440 + 11 * 60     # 11:00
b.chat("adytum_worker", "Что строит", "медный кабель", "Спасибо")
g.set_stage("sq_bell", 10)
ok(not g.inventory.has("динамит") and g.player.skill("science") < 55,
   "ни динамита, ни Науки 55 — старый сценарий здесь бросал «нечем взорвать»")
SQ.bell_finish(b)
ok(g.stage("sq_bell") == 100 and g.flags.get("bell_night"), "бот дождался ночи и снял катушку руками")
ok(g.is_night(), "время в прогоне сдвинулось на ночь (advance_time), а не «телепорт в ночь»")
ok(not b.side_fails, f"ни одного провала в отчёте: {b.side_fails}")

# ===================================================== 3. Отчаянный: топливо и Абнер
b, g = hero("primm")
g.player.skills["science"] = 20
g.player.skills["survival"] = 20
g.inventory.add("топливо", 5)                          # канистры в рюкзаке (по 5 крышек у Вика/Роуз)
SQ.primm(b)
ok(g.flags.get("coaster_power"), "мотор получил ток от пяти канистр — Науки 55 у героя нет")
ok(g.stage("sq_coaster") == 100 and g.flags.get("abner_checked") and not g.flags.get("coaster_crash"),
   "рельсы осмотрел Абнер: квест 100, Вик цел (аварии нет)")
ok(not any("Отчаянный" in f for f in b.side_fails), f"«Отчаянный» не в провалах: {b.side_fails}")

# порог диалога, а не 70: Наука 55 без топлива — ветряк у колонок
b, g = hero("primm")
g.player.skills["science"] = 56
g.player.skills["survival"] = 20
g.inventory.items.pop("топливо", None)
SQ.primm(b)
ok(g.flags.get("coaster_power") and not g.inventory.has("топливо"),
   "Наука 55 (порог диалога, а не 70) запускает мотор от ветряка — топливо не нужно")
ok(g.stage("sq_coaster") == 100 and g.flags.get("abner_checked"),
   "рельсы проверил Абнер: Наука 56 не дотянула до порога диалога 60, а Выживание 20 — до 50")

# ===================================================== 4. Арадеш: матка не по зубам — насос Вика
b, g = hero("aradesh", hp=200)
b.chat("aradesh", "Что случилось с колодцем", "Я очищу пещеру")
ok(g.stage("sq_aradesh") == 10, "Арадеш дал работу")
g.enter_location("aradesh_cave")
g.slides = None
for e in g.enemies:                                    # выжила только матка — и затаилась
    if e.type_id == "radscorpion_queen":
        e.hostile = False
        e.faction = "radscorpions"
    else:
        e.alive = False
g.inventory.items["крышки"] = 40
SQ.aradesh(b)
ok(g.flags.get("aradesh_free_water") and g.stage("sq_aradesh") == 100,
   "квест закрыт вторым путём: насос Вика поднял воду из каньона")
flags = {k: g.flags.get(k) for k in ("khans_pump_ok", "khans_water_share", "pump_fixed", "aradesh_spring_cleared")}
ok(flags["khans_pump_ok"] and flags["khans_water_share"] and flags["pump_fixed"],
   f"цена названа в флагах: Ханы пропустили, доля воды у них, затвор починен {flags}")
ok(not flags["aradesh_spring_cleared"], "в пещеру бот не лез: родник так и остался за маткой")
ok(not any("Арадеш" in f for f in b.side_fails), f"провала нет — путь найден: {b.side_fails}")

# путь не нашёлся (нет пружины и крышек) — честная причина в side_fails, а не тишина
b, g = hero("aradesh", hp=200)
b.chat("aradesh", "Что случилось с колодцем", "Я очищу пещеру")
g.enter_location("aradesh_cave")
g.slides = None
for e in g.enemies:
    if e.type_id == "radscorpion_queen":
        e.hostile = False
        e.faction = "radscorpions"
    else:
        e.alive = False
g.inventory.items["крышки"] = 0
b.side("Вода для Арадеша", lambda: SQ.aradesh(b))
ok(any("Вода для Арадеша" in f and ("пещера не зачищена" in f or "насос не поднят" in f) for f in b.side_fails),
   f"провал попадает в отчёт с причиной: {b.side_fails}")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
