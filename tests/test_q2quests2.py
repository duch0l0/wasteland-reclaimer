"""
Q2, часть 2 — вторые пути без навыка и «невидимые» квесты:

  1. «Жёлтые треугольники»: без противогаза баржу заливает Речная стража (Морроу берёт цемент и славу,
     репутация +10 вместо +30/+35) — и бот идёт этим путём, а не бросает квест;
  2. «Отчаянный»: пороги бота = пороги диалога (Наука 55 → ток, 60/Выживание 50 → рельсы), а без них
     рельсы осматривает Абнер, который их строил;
  3. «Колокольня»: ночной подъём и катушка руками (night: true) — днём реплики нет, ночью есть;
  4. «Вода для Арадеша»: насос Вика из каньона за долю Ханов; провал квеста попадает в side_fails
     бота с честной причиной, а не молчит;
  5. «Мальтийский сокол»: бот возвращается к птице позже (отмычка/сто крышек), а не бросает с нулём крышек;
  6. «Зачистка Барстоу»: ворота на базу морпехов открываются с пульта депо, а не шагом с карты депо
     (из-за этого шага бот терял один район и застревал на 50);
  7. «Вода Хаба»: пароль шлюза нацарапан на кромке экрана (know_sluice_pass) — взлом больше не лотерея.

    .venv/bin/python tests/test_q2quests2.py
"""
import importlib.util
import os
import sys
import tempfile

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))     # playthrough импортирует bot_sides как соседний модуль
os.chdir(ROOT)

import pygame  # noqa: E402

pygame.mouse.get_pos = lambda: (-50, -50)
pygame.mouse.get_focused = lambda: True

from src.game import Game, saveload  # noqa: E402
from src.combat import tile_of, rect_pos_for_tile  # noqa: E402

_spec = importlib.util.spec_from_file_location("playthrough", os.path.join(ROOT, "tools", "playthrough.py"))
PT = importlib.util.module_from_spec(_spec)
sys.modules["playthrough"] = PT
_spec.loader.exec_module(PT)
SQ = PT.SQ

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
        while g.perk_choices:          # уровень за квесты — выбрать первое
            g.handle_key(pygame.K_1)


def goto(g, t):
    g.player.rect.topleft = rect_pos_for_tile(g.player, t)
    g.snap_camera()
    fr(g)


def go(g, lid):
    g.dialogue.active_node = None
    g.enter_location(lid)
    g.slides = None
    for e in g.enemies:
        e.alive = False
    fr(g)


def stand_near(g, t):
    for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (-1, 1)):
        c = (t[0] + dx, t[1] + dy)
        if not g.level.is_wall(*c):
            g.player.rect.topleft = rect_pos_for_tile(g.player, c)
            g.snap_camera()
            return


def talk(g, nid):
    g.dialogue.active_node = None
    npc = next(n for n in g.npcs if n.npc_id == nid)
    stand_near(g, tile_of(npc))
    g.handle_key(pygame.K_e)
    assert g.dialogue.is_active(), nid


def opts(g):
    return [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]


def has_line(g, part):
    return any(part in lbl for lbl in opts(g))


def say(g, part, required=True):
    labels = opts(g)
    idx = next((i for i, l in enumerate(labels) if part in l), None)
    if idx is None:
        assert not required, f"нет реплики «{part}» среди {labels}"
        return False
    g.handle_key(pygame.K_1 + idx)
    fr(g, 1)
    return True


def fresh(lid, hp=10 ** 5):
    g = Game(intro=False)
    g.player.max_hp = g.player.hp = hp
    go(g, lid)
    return g


def hour(g, h):
    """Переставить часы: 0..23 (движок считает время минутами от начала игры)."""
    g.flags["time_min"] = (g.flags.get("time_min", 8 * 60) // 1440) * 1440 + h * 60


# ===================================================== 1. Жёлтые треугольники: цемент Морроу
g = fresh("needles")
talk(g, "kate")
say(g, "Что с рекой"); say(g, "Что за баржа"); say(g, "залить бочку цементом"); say(g, "Нырну")
ok(g.flags.get("barge_job"), "Кейт взяла на баржу: мешок цемента и нырок")
g.inventory.add("мешок цемента", 1)
go(g, "needles_bridge")
talk(g, "captain_morrow")
say(g, "Баржа ниже моста")
ok(has_line(g, "Цемент мой") and not has_line(g, "Красноречие"),
   "без Красноречия у Морроу виден новый путь — цемент как рычаг")
say(g, "Цемент мой"); say(g, "...")
ok(g.flags.get("barge_cement_deal") and g.flags.get("barge_done") and g.stage("sq_barge") == 100,
   "Речная стража залила баржу: квест закрыт без противогаза и без Красноречия")
ok(g.player.rads == 0 and not g.inventory.has("мешок цемента"),
   "герой не нырял: 0 рад, цемент ушёл стражникам")
ok(g.rep("needles") == 35 and g.karma == 5,
   "репутация Нидлса 35 (+10 сделка, +25 за квест) — ниже нырка (55) и ныряния без маски (60)")

# нырок в маске никуда не делся — пути видны оба
g = fresh("needles")
talk(g, "kate")
say(g, "Что с рекой"); say(g, "Что за баржа"); say(g, "залить бочку цементом"); say(g, "Нырну")
g.inventory.add("мешок цемента", 1)
g.inventory.add("противогаз", 1)
talk(g, "kate")
say(g, "Цемент у меня")
ok(has_line(g, "костюме химзащиты") and has_line(g, "так — быстро"),
   "с маской видны оба пути: в костюме и «быстро, на одном вдохе»")

# ===================================================== 2. Отчаянный: рельсы Абнера
g = fresh("primm")
g.player.skills["science"] = 20
g.player.skills["survival"] = 20
talk(g, "pr_mechanic")
say(g, "горки"); say(g, "Найду ток")
g.inventory.add("топливо", 5)
talk(g, "pr_mechanic")
say(g, "Ток для горок"); say(g, "Пять канистр"); say(g, "...")
ok(g.flags.get("coaster_power") and not g.inventory.has("топливо"),
   "пять канистр топлива крутят мотор (Науки 55 у героя нет)")
talk(g, "pr_mechanic")
say(g, "Запускай")
ok(has_line(g, "проверю рельсы") is False and has_line(g, "обойду опоры") is False,
   "без Науки 60 и Выживания 50 обеих реплик проверки нет — только «Запускай сейчас!»")
g.dialogue.active_node = None
talk(g, "pr_old")
ok(has_line(g, "ты же их строил"), "Абнер идёт смотреть рельсы, если горки под током")
say(g, "ты же их строил"); say(g, "...")
ok(g.flags.get("coaster_ok") and g.flags.get("coaster_done") and g.stage("sq_coaster") == 100,
   "«Отчаянный» поехал: рельсы проверил тот, кто их строил")
ok(g.flags.get("abner_checked") and g.flags.get("abner_credit") and not g.flags.get("coaster_crash"),
   "Вик не калечится: абнер_checked + abner_credit, аварии нет")

# ===================================================== 3. Колокольня: ночь
g = fresh("boneyard")
g.player.level_sys.level = 25          # 250 опыта за ночь не должны поднять уровень и «вылечить» падение
hour(g, 11)
talk(g, "adytum_worker")
say(g, "Что строит"); say(g, "медный кабель"); say(g, "Спасибо")
ok(g.flags.get("bell_job"), "рабочий рассказал про маяк на колокольне")
g.dialogue.active_node = None
talk(g, "adytum_worker")
ok(not has_line(g, "ночью наверху никого"), "днём ночного подъёма в разговоре нет")
g.dialogue.active_node = None
hour(g, 21)
talk(g, "adytum_worker")
ok(has_line(g, "ночью наверху никого"), "ночью — есть (night: true)")
hp0 = g.player.hp
say(g, "ночью наверху никого"); say(g, "...")
ok(g.flags.get("bell_night") and g.flags.get("bell_done") and g.stage("sq_bell") == 100,
   "катушка снята руками: маяк замолчал без динамита и без Науки")
ok(g.inventory.has("дубликат передатчика") and g.flags.get("know_cult_beacon"), "катушка в рюкзаке, про маяк теперь известно")
ok(g.player.hp == hp0 - 10, f"сорвался с последней скобы: −10 HP ({hp0} → {g.player.hp})")

# ===================================================== 4. Вода для Арадеша: насос Вика
g = fresh("aradesh")
talk(g, "aradesh")
say(g, "Что случилось с колодцем"); say(g, "Я очищу пещеру")
ok(g.flags.get("aradesh_job"), "Арадеш дал работу: пещера в северном отроге")
go(g, "aradesh_canyon")
talk(g, "khan_chief")
say(g, "Пропусти механика"); say(g, "...")
ok(g.flags.get("khans_pump_ok") and g.flags.get("khans_water_share"),
   "Ханы пропустили к насосной за первую бочку")
go(g, "aradesh")
talk(g, "mechanic_vic")
ok(has_line(g, "чинил насосы") is False, "без пружины Вик про насос молчит")
g.inventory.add("пружина", 1)
g.dialogue.active_node = None
talk(g, "mechanic_vic")
say(g, "чинил насосы"); say(g, "...")
ok(g.flags.get("pump_fixed") and not g.inventory.has("пружина"), "Вик поднял воду: пружина ушла в затвор")
g.dialogue.active_node = None
talk(g, "aradesh")
say(g, "Насос Вика поднял воду"); say(g, "...")
ok(g.flags.get("aradesh_free_water") and g.stage("sq_aradesh") == 100,
   "колодец полон без боя с маткой: квест закрыт вторым путём")
ok(g.flags.get("khans_water_share") and not g.flags.get("aradesh_spring_cleared"),
   "цена названа: первая вода у Ханов, пещера не тронута")
g.dialogue.active_node = None
talk(g, "aradesh")
ok(g.get_location("aradesh_cave") is not None, "пещеру после насоса всё ещё можно зачистить")

# ===================================================== 5. Мальтийский сокол: бот возвращается позже
def bot_hero(npc_flags=True):
    b = PT.Bot(seed=7, sides=True)
    b.go("hub_falcon")
    g = b.g
    g.player.max_hp = g.player.hp = 400
    if npc_flags:
        g.flags["falcon_job"] = True
        g.flags["know_falcon_decker"] = True
    return b, g


b, g = bot_hero()
b.g.inventory.items.pop("крышки", None)
try:
    SQ.falcon_deal(b)
    ok(False, "с нулём крышек и без отмычки бот не должен закрывать птицу")
except PT.Stuck as ex:
    ok("птицы нет" in str(ex), f"пустой карман — честная причина: {ex}")

b, g = bot_hero()
b.g.inventory.items.pop("крышки", None)
g.inventory.add("отмычка", 1)
SQ.falcon_deal(b)
ok(g.stage("sq_falcon") == 100 and g.flags.get("falcon_done"), "бот вернулся к соколу и закрыл дело отмычкой")
ok(g.inventory.has("гроссбух Декера"), "в сейфе нашёлся гроссбух Декера — нить «выкупа» открыта")
ok(g.flags.get("decker_robbed"),
   "вскрытие не осталось незамеченным: Декер видел (карма −5, Хаб −15 — on_theft_seen)")

b, g = bot_hero()
g.inventory.items.pop("крышки", None)
g.inventory.add("крышки", 300)                 # деньги появились позже — как в обходе act2
g.player.skills["speech"] = 20                 # Красноречия 60 нет — значит, ключ за сто
SQ.falcon_deal(b)
ok(g.flags.get("falcon_dk_done") and g.stage("sq_falcon") == 100,
   "позже, когда крышки есть: бот платит Декеру сотню за ключ и забирает птицу")

# ===================================================== 6. Зачистка Барстоу: ворота и два района
g = fresh("barstow_depot")
goto(g, (41, 15))
ok(g.loc.id == "barstow_depot", "шаг на ворота базы без пульта никуда не ведёт — район не теряется")
g.flags["barstow_base_gate"] = True
goto(g, (41, 15))
ok(g.loc.id == "barstow_base", "после пульта депо ворота открыты")

g = fresh("barstow_depot")
g.open_terminal("barstow_depot")
ents = g.term_entries()
i = next(k for k, (_, e) in enumerate(ents) if e["label"].startswith("[Развод ворот"))
g.term_open_entry(i)
g.close_terminal()
ok(g.flags.get("barstow_base_gate"), "пульт конторы депо разводит ворота на базу морпехов")

b = PT.Bot(seed=7, sides=True)
g = b.g
b.go("barstow")
p = g.player
p.level_sys.level, p.max_hp, p.hp = 9, 70, 70
p.skills["guns"] = 90
g.inventory.add("автомат", 1)
p.weapon = "assault"
g.inventory.add("патроны", 300)
for n in ("металлическая броня", "шлем металлической брони"):
    g.inventory.add(n, 1)
p.equipment["body"] = "металлическая броня"
p.equipment["head"] = "шлем металлической брони"
g.inventory.add("стимулятор", 10)
b.pursue("rose", "quest:sq_barstow", required=False)
for m in ("barstow_depot", "barstow_center", "barstow_depot"):
    if not g.flags.get(m + "_cleared"):
        b.visit(m)
ok(g.flags.get("barstow_depot_cleared") and g.flags.get("barstow_center_cleared"),
   "бот выбил гулей из обоих районов (депо больше не теряется на воротах)")
b.walk_to_map("barstow")
b.pursue("rose", "quest:sq_barstow", required=False)
ok(g.stage("sq_barstow") == 100 and g.flags.get("barstow_paid"), "Роза расплатилась: 150 крышек и патроны")

# ===================================================== 7. Вода Хаба: пароль шлюза
g = fresh("hub_tunnels")
g.open_terminal("hub_sluice")
ents = g.term_entries()
i = next(k for k, (_, e) in enumerate(ents) if e["label"] == "Положение затворов")
g.term_open_entry(i)
g.term_back()
ok(g.flags.get("know_sluice"), "шлюз прочитан: культ уводит воду в цистерну")
ok(g.flags.get("know_sluice_pass"), "пароль нацарапан на кромке экрана — читается вместе с затворами")
ents = g.term_entries()
i = next(k for k, (_, e) in enumerate(ents) if e["label"].startswith("[Открыть затвор 1"))
g.term_open_entry(i)
lock_opts = dict(g.lock_options())
pw = next((lbl for lbl in lock_opts if lbl.startswith("Ввести пароль")), None)
ok(pw is not None and "ОАЗИС" in pw, f"вместо лотереи взлома — пароль: {pw}")
lock_opts[pw]()
g.term_back()
g.close_terminal()
ok(g.flags.get("sluice_restored"), "затвор 1 открыт полностью — вода вернулась в оазис")
ok(g.stage("sq_hub") == 100, "«Вода Хаба» закрыта (раньше бот застревал на 50: взлом молча не выходил)")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
