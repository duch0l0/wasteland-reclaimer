"""
Q1, часть 1 — бот проходит четыре квеста, которые не трогал ни один прогон:
«Контракт на Барстоу» (sq_merc), «Письма почтальона» (sq_letters), «Пропавшие караваны»
(sq_caravans), «Экспедиция Гарольда» (sq_harold). Гоняются только эти куски бота —
и вместе с ними честные причины, когда путь не вышел:

  1. Письма: мешок у Почтальона-3000 (встреча в пустоши), семь адресатов по своим городам,
     восьмое (Убежище 13) остаётся в рюкзаке; чужие письма бот не вскрывает — карма цела;
  2. Караваны: бот берёт неделю на правду, собирает улики (застава I-15, журнал моста, фургон
     культа) и называет Билли — ветку «Билли» берёт по Красноречию 60 или через паром Кейт;
     без улик — честная причина в side_fails;
  3. Гарольд: рассказ в Старом городе (грузовой въезд) и журнал «Купели» в Марипозе;
  4. Контракт на Барстоу: наём Дэкса своими крышками, экшен за него (бот целится и стреляет
     сам), зачистка депо и центра, расчёт Розы, доля герою.

    .venv/bin/python tests/test_q1bot_part1.py
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


CITIES = ("hub", "needles", "aradesh", "spot_toll", "junktown", "zzyzx", "primm", "vault15",
          "vegas_strip", "mariposa", "boneyard")


def hero(lid, level=10, hp=160, weapon="assault", item="автомат", skill="guns", val=110, caps=0):
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
    g.inventory.add("патроны", 300)
    for n in ("металлическая броня", "мотошлем"):
        g.inventory.add(n, 1)
    p.equipment["body"] = "металлическая броня"
    p.equipment["head"] = "мотошлем"
    g.inventory.add("стимулятор", 8)
    g.inventory.add("крышки", caps)
    for c in CITIES:
        g.reveal_location(c)
    return b, g


# ===================================================== 1. Письма почтальона
b, g = hero("ruins", caps=50)
SQ.mail_sack(b)
letters = [k for k in g.inventory.nonzero() if k.startswith("письмо: ")]
ok(g.stage("sq_letters") == 10 and len(letters) == 8 and g.flags.get("mail_sack"),
   f"Почтальон-3000 отдал мешок: {len(letters)} писем, стадия {g.stage('sq_letters')}")
ok(g.loc.id == "encounter:robot" and g.mode == "world", "встреча в пустоши, а не отдельная локация-город")
k0 = g.karma
b.read_books()                                     # все читаемые бумаги в рюкзаке — кроме чужой почты
ok(g.karma == k0 and not any(str(k).startswith("mail_opened") for k in g.flags),
   f"чужие письма бот не вскрывает: карма {g.karma}, вскрытых 0")

for npc, item, flag, where in SQ.MAIL:
    SQ.mail(b, npc, item, flag, where)
b.visit("vegas_strip", clear=False)
SQ.mail_house(b)
ok(all(g.flags.get(flag) for _, _, flag, _ in SQ.MAIL) and g.flags.get("mail_done_house"),
   "семь писем доставлены: Ривзы, Дарквотер, Шоу, Убежище 15, Спрингер, Грей, Хаус")
ok(g.inventory.has("письмо: жителям Убежища 13") and g.stage("sq_letters") == 100,
   "восьмое письмо (Убежище 13) оставлено в рюкзаке — доставить его некуда, квест всё равно 100")
ok(any(t[0] == "postman" for t in g.titles()), "звание «Почтальон пустоши»")
ok(not b.side_fails, f"ни одного провала в доставке: {b.side_fails}")

SQ.mail_sisters(b)
ok(g.flags.get("sisters_reconciled"), "письмо Убежища 15 отыграно в Арадеше: Лейла идёт мириться")

# нет конверта — честная причина, а не тишина
b, g = hero("ruins")
SQ.mail_sack(b)
g.inventory.remove("письмо: Ривзам, Примм", 1)
b.side("Письма: Ривзам, Примм", lambda: SQ.mail_to(b, "mae_reeves", "письмо: Ривзам, Примм", "mail_done_reeves"))
ok(any("Ривзам" in f and "рюкзаке" in f for f in b.side_fails), f"пропавший конверт — с причиной: {b.side_fails}")

# ===================================================== 2. Пропавшие караваны: полная правда
b, g = hero("hub")
g.player.skills["speech"] = 70
SQ.caravans_take(b)
ok(g.stage("sq_caravans") == 30 and g.flags.get("caravans_job") and g.flags.get("clue_survivor"),
   "Маргарет дала неделю, Ларс рассказал про «брод держи»")
b.side("Караваны: фургон", lambda: SQ.caravans_wreck(b))
ok(g.flags.get("clue_arrow") and g.flags.get("clue_route"),
   "сгоревший фургон: стрела с клеймом «Барстоу, 2076» и обрывок накладной")
g.flags["clue_cargo"] = True                       # журнал фургона культа читается у Арадеша (акт II)
b.side("Караваны: мост", lambda: SQ.caravans_toll(b))
ok(g.flags.get("clue_toll") and g.stage("sq_caravans") == 60, "журнал пошлин моста: подпись «Б.» — три улики")
SQ.caravans_billy(b)
ok(g.flags.get("billy_turned"), "Красноречие 70: Билли согласился сливать маршруты культа")
SQ.caravans_finish(b)
ok(g.stage("sq_caravans") == 100 and g.flags.get("caravans_truth") and g.flags.get("caravan_pass"),
   "полная правда: Ханы целы, пропуск Красного каравана, квест 100")
ok(any(t[0] == "sleuth" for t in g.titles()) and g.karma > 0, f"звание «Сыщик трассы 15», карма {g.karma}")
ok(not b.side_fails, f"караваны прошли без провалов: {b.side_fails}")

# ветка без Красноречия: через паром Кейт (обе ветки должны быть пройдены ботом)
b, g = hero("hub")
g.player.skills["speech"] = 30
g.flags["ferry_done"] = True                       # паром переправлен в акте I (проверено в test_ndquests)
SQ.caravans_take(b)
SQ.caravans_toll(b)
SQ.caravans_billy(b)
ok(g.flags.get("billy_to_kate") and g.flags.get("billy_turned"),
   "Красноречия не хватило — бот повёл Билли к матери, Кейт сама решила за сына")
g.flags["clue_cargo"] = True
SQ.caravans_finish(b)
ok(g.stage("sq_caravans") == 100 and g.flags.get("caravans_detour") and not g.flags.get("khans_wiped"),
   "без журнала пошлин бот назвал культ: караваны в обход, Ханы целы")

# без улик — честная причина
b, g = hero("hub")
SQ.caravans_take(b)
b.side("Караваны: виновный", lambda: SQ.caravans_finish(b))
ok(any("виновный" in f and "улик" in f for f in b.side_fails), f"без улик — причина в отчёте: {b.side_fails}")

# ===================================================== 3. Экспедиция Гарольда
b, g = hero("hub")
SQ.harold_story(b)
ok(g.stage("sq_harold") == 50 and g.flags.get("know_cargo_bay") and g.flags.get("harold_message"),
   "Гарольд рассказал про Грея и скобу у петли на грузовом въезде")
g.go_world_map()
b.go("mariposa")
SQ.harold_finish(b)
ok(g.stage("sq_harold") == 100 and g.flags.get("know_master_vat"),
   "журнал «Купели»: «Р. Грей. Создатель» — квест 100")
ok(not b.side_fails, f"Гарольд без провалов: {b.side_fails}")

b, g = hero("hub")
g.flags["know_cargo_bay"] = True                   # герой знает про въезд, но о Грее ему не рассказывали
g.go_world_map()
b.go("mariposa")
b.side("Гарольд: журнал", lambda: SQ.harold_finish(b))
ok(any("Купели" in f for f in b.side_fails), f"журнал без рассказа Гарольда — причина в отчёте: {b.side_fails}")

# ===================================================== 4. Контракт на Барстоу (экшен за Дэкса)
b, g = hero("ruins", caps=200)
caps0 = g.inventory.count("крышки")
SQ.merc_contract(b)
ok(g.stage("sq_merc") == 100 and g.stage("sq_barstow") == 100,
   f"контракт закрыт: sq_merc {g.stage('sq_merc')}, зачистка/расчёт Розы {g.stage('sq_barstow')}")
ok(g.flags.get("barstow_depot_cleared") and g.flags.get("barstow_center_cleared"),
   "депо и центр зачищены в экшене за Дэкса (не телепортом флагов)")
ok(not g.merc_mode and g.loc.id == "ruins" and g.flags.get("dex_back"),
   "Дэкс вернулся с караваном, управление снова у героя")
ok(g.inventory.count("крышки") == caps0 - 100 + 150,
   f"бот заплатил свои сто крышек и получил долю 150: было {caps0}, стало {g.inventory.count('крышки')}")
ok(not b.side_fails, f"контракт без провалов: {b.side_fails}")

# контракт сорвался в бою — управление возвращается герою, причина в отчёте (а не «игра за Дэкса до конца»)
b, g = hero("ruins", caps=200)
_real_clear = PT.Bot.action_clear


def _broken(self, where="", **k):
    raise self.Stuck(f"{where}: гули смяли Дэкса")


PT.Bot.action_clear = _broken
try:
    b.side("Контракт на Барстоу", lambda: SQ.merc_contract(b))
finally:
    PT.Bot.action_clear = _real_clear
ok(not g.merc_mode and g.player.alive and g.loc.id == "ruins" and g.stage("sq_merc") < 100,
   "боевой провал: Дэкс вернулся ни с чем, игра снова за героя, квест не закрыт")
ok(any("Контракт на Барстоу" in f and "Дэкса" in f for f in b.side_fails),
   f"причина боевого провала в отчёте: {b.side_fails}")

# нечем платить — честный отказ, герой остаётся героем
b, g = hero("ruins", caps=0)
g.inventory.items.pop("крышки", None)
b.side("Контракт на Барстоу", lambda: SQ.merc_contract(b))
ok(any("Контракт на Барстоу" in f and "крышек" in f for f in b.side_fails),
   f"без денег — причина в отчёте: {b.side_fails}")
ok(not g.merc_mode and g.player.alive, "управление не перешло к Дэксу: играть дальше можно")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
