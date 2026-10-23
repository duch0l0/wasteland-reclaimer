"""
Q1, часть 2 — бот проходит четыре квеста, которые не трогал ни один прогон:
«Цена воды» (sq_water_war), «Кровь Убежища 11» (sq_vault11), «Последний банк Вегаса» (sq_heist),
«Беглый субъект» (sq_subject). Гоняются только эти куски бота — и вместе с ними честные причины,
когда путь не вышел:

  1. Цена воды: Сэл в Джанктауне, артель Веги в Хабе, гроссбух Декера из сейфа и мэр Дарквотер —
     Вега и Джанктаун договариваются напрямую; у сборки с Наукой 50 и гаечным ключом — свой насос
     на свалке. В долю с Декером бот не идёт. Нет ни отмычки, ни Науки — причина в side_fails.
  2. Кровь Убежища 11: устав Ярмарки в ратуше Ниптона, зал выборов с дневником смотрителя,
     взлом «Протокола эксперимента» в вычислительном центре и мэр Кэрролл — с Красноречием 60
     он сам выходит на площадь, без него бот говорит площадь сам. Если мэр уже ушёл из города
     по исходу лотереи (nipton_mayor_drawn / nipton_mayor_exposed), протокол принимает вдова Грейс:
     исход тот же, реплики другие. Шантаж бот не берёт.
     Закрытый терминал не поддался — причина в side_fails.
  3. Последний банк Вегаса: крупье Змей, команда (Джин за двести крышек, Ред за идею), пульт
     охраны снят командой, хранилище запечатано — крышки в пустоши не обесценились. Нет денег
     на Джин — причина в side_fails.
  4. Беглый субъект: Тед в Ниптоне, лифт на нижний ярус Убежища 4 открывает Тихоня, клетка № 12
     по терминалу, Марта идёт в Ниптон сама. Терминал заблокирован — причина в side_fails.

Плюс регрессия «Контракта на Барстоу»: 15 гулей толпы вываливались из комнаты 6×4 с двумя
одноклеточными лазами и застревали в углу (8,31) — живы ['feral@(8, 31)', 'feral@(8, 31)', ...],
контракт вставал на стадии 20. Проверяются карта (толпа выходит из проёма на двор, в развалинах
никого нет), расталкивание гулей в движке и сам контракт на двух бросках, где он раньше вставал.

    .venv/bin/python tests/test_q1bot_part2.py
"""
import importlib.util
import json
import os
import sys

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

from src import action as ACTION  # noqa: E402
from src.combat import tile_of  # noqa: E402

failed = []


def ok(cond, msg):
    print(("OK   " if cond else "FAIL ") + msg)
    if not cond:
        failed.append(msg)


CITIES = ("hub", "needles", "aradesh", "spot_toll", "junktown", "zzyzx", "primm", "vault15",
          "vegas_strip", "mariposa", "boneyard", "nipton", "vault4", "vault11", "ruins", "barstow")


def hero(lid, level=14, hp=220, speech=40, science=40, caps=800, bare=False):
    """Бот с героем конца акта II — начала акта III: переживает ярус Убежища 4 и не покупает лишнего."""
    b = PT.Bot(seed=7, sides=True)
    b.go(lid)
    g = b.g
    p = g.player
    p.level_sys.level = level
    p.max_hp = p.hp = hp
    p.skills["guns"] = 120
    p.skills["speech"] = speech
    p.skills["science"] = science
    p.weapon = "assault"
    g.inventory.add("автомат", 1)
    if not bare:                                   # «бедный» герой: ни отмычки, ни патронов на продажу
        g.inventory.add("патроны", 400)
        g.inventory.add("отмычка", 2)
    g.inventory.add("стимулятор", 12)
    for n in ("броня «Пустынный рейнджер»", "шлем боевой брони"):
        g.inventory.add(n, 1)
    p.equipment["body"] = "броня «Пустынный рейнджер»"
    p.equipment["head"] = "шлем боевой брони"
    g.inventory.add("крышки", caps)
    for c in CITIES:
        g.reveal_location(c)
    return b, g


# ===================================================== 0. маршрут бота зовёт все четыре квеста
route = open("tools/playthrough.py", encoding="utf-8").read()
for fn, act in (("SQ.water_war(b)", "акт II, Джанктаун"), ("SQ.vault11(b)", "акт III, Ниптон"),
                ("SQ.subject(b)", "акт III, Ниптон"), ("SQ.heist(b)", "акт III, побочки Вегаса")):
    ok(fn in route, f"маршрут бота зовёт {fn} ({act}) — квест не остаётся в стороне от прогона")

# ===================================================== 1. Цена воды
b, g = hero("junktown", caps=300)
karma0 = g.karma
b.side("Цена воды", lambda: SQ.water_war(b))
ok(g.stage("sq_water_war") == 100 and g.flags.get("water_direct") and g.flags.get("decker_exposed"),
   f"гроссбух Декера у мэра: Вега и Джанктаун напрямую, посредник разоблачён (стадия {g.stage('sq_water_war')})")
ok(g.flags.get("clue_middleman"), "артель Веги назвала посредника «Д.» — улика до сейфа, а не после")
ok(g.inventory.has("гроссбух Декера") is False, "гроссбух остался у мэра — в рюкзаке его нет")
ok(not g.flags.get("water_decker") and g.karma >= karma0,
   f"в долю с Декером бот не пошёл: карма {g.karma} (было {karma0}), флага water_decker нет")
ok(g.rep("junktown") >= 30 and not b.side_fails, f"Джанктаун благодарен ({g.rep('junktown')}), провалов нет: {b.side_fails}")

b, g = hero("junktown", science=60)
g.inventory.add("гаечный ключ", 1)
b.side("Цена воды", lambda: SQ.water_war(b))
ok(g.stage("sq_water_war") == 100 and g.flags.get("junktown_pump") and g.rep("junktown") >= 40,
   f"свой насос вместо сделки: Джанктаун никому не платит за воду (репутация {g.rep('junktown')})")
ok(not g.flags.get("water_direct") and not g.inventory.has("гроссбух Декера"),
   "с Наукой 50 и ключом бот даже не лезет в сейф Декера — кражи не было")

b, g = hero("junktown", science=30, caps=0, bare=True)
b.side("Цена воды", lambda: SQ.water_war(b))
ok(any("Цена воды" in f and "гроссбуха" in f for f in b.side_fails),
   f"ни отмычки, ни Науки 50 — причина в отчёте: {b.side_fails}")

# ===================================================== 2. Кровь Убежища 11
b, g = hero("nipton", speech=30)
b.side("Кровь Убежища 11", lambda: SQ.vault11(b))
ok(g.stage("sq_vault11") == 100 and g.flags.get("v11_told_town"),
   f"без Красноречия бот сам говорит площадь: Ниптон знает правду (стадия {g.stage('sq_vault11')})")
ok(g.flags.get("know_vault11") and "vault11" in g.worldmap.known,
   "устав Ярмарки открыл Убежище 11 на карте мира (а не телепорт по флагу)")
ok(g.flags.get("read_stone_diary") and g.flags.get("know_v11_truth") and g.flags.get("know_v11_survivors"),
   "дневник смотрителя и протокол: угроза была ложью, дверь открывалась тем, кто откажется")
ok(g.flags.get("term_v11_core_v11core_open") and not g.flags.get("term_v11_core_v11core_lockout"),
   "служебная запись взята взломом по подсказкам «Совпадение=N» (терминал не заблокирован)")
ok(not g.flags.get("v11_blackmail") and g.karma > 0,
   f"шантаж на 500 крышек бот не взял: карма {g.karma}, флага v11_blackmail нет")
ok(g.rep("nipton") >= 40 and not b.side_fails, f"репутация Ниптона {g.rep('nipton')}, провалов нет: {b.side_fails}")

b, g = hero("nipton", speech=70)
b.side("Кровь Убежища 11", lambda: SQ.vault11(b))
ok(g.flags.get("v11_confessed") and g.flags.get("nipton_decided") and g.rep("nipton") >= 60,
   f"с Красноречием 70 Кэрролл выходит на площадь сам (репутация {g.rep('nipton')})")


# мэр уходит из Ниптона по исходу лотереи (npc_leave в узлах «swapped» и «list»). Квест не должен
# ломаться от исхода другого: протокол тогда принимает вдова Грейс — она теперь отвечает за город.
# Исход тот же (те же репутация и карма), реплики другие.
def v11_run(speech, leave=None):
    """Прогнать «Кровь Убежища 11» ботом; leave — флаг исхода лотереи, из-за которого мэр уходит.

    nipton_decided ставится до замера в обоих случаях: в игре к моменту протокола лотерея уже
    решена (изгнание, жребий мэра или взятка), и +25 за «Ярмарку» не должен попадать в счёт.
    """
    b, g = hero("nipton", speech=speech)
    effs = ([{"type": "npc_leave", "npc": "mayor_carroll"}, {"type": "set_flag", "flag": leave}]
            if leave else []) + [{"type": "set_flag", "flag": "nipton_decided"}]
    for eff in effs:
        g.apply_effect(eff)
    rep0, karma0 = g.rep("nipton"), g.karma
    b.side("Кровь Убежища 11", lambda: SQ.vault11(b))
    return b, g, g.rep("nipton") - rep0, g.karma - karma0


b, g, rep_m, karma_m = v11_run(70)                       # мэр на месте: Кэрролл выходит сам
b2, g2, rep_g, karma_g = v11_run(70, "nipton_mayor_drawn")   # мэр вытянул свой жребий и ушёл с холмов
ok(b2.find_npc("mayor_carroll") is None, "мэр ушёл (жребий) и в Ниптон не вернулся")
ok(g2.stage("sq_vault11") == 100 and g2.flags.get("v11_confessed") and not b2.side_fails,
   f"мэра нет — протокол приняла вдова Грейс, город сожёг жребии без него ({b2.side_fails})")
ok((rep_g, karma_g) == (rep_m, karma_m),
   f"исход не хуже и не лучше мэра: репутация +{rep_g} (у мэра +{rep_m}), карма +{karma_g} (у мэра +{karma_m})")

b3, g3, rep_g3, karma_g3 = v11_run(30, "nipton_mayor_exposed")   # мэра вынесли на площади: бот говорит сам
ok(g3.stage("sq_vault11") == 100 and g3.flags.get("v11_told_town") and not b3.side_fails,
   f"мэра нет (список показан городу) — Грейс отдала протокол, площадь слушает героя ({b3.side_fails})")
b4, g4, rep_m4, karma_m4 = v11_run(30)
ok((rep_g3, karma_g3) == (rep_m4, karma_m4),
   f"без Красноречия исход тот же, что через мэра: репутация +{rep_g3} (у мэра +{rep_m4}), "
   f"карма +{karma_g3} (у мэра +{karma_m4})")

b, g = hero("nipton")
g.flags["term_v11_core_v11core_lockout"] = True        # взлом уже провален раньше (терминал заблокирован)
b.side("Кровь Убежища 11", lambda: SQ.vault11(b))
ok(any("Кровь Убежища 11" in f and "протокол" in f for f in b.side_fails),
   f"заблокированный терминал — честная причина в отчёте: {b.side_fails}")
ok(g.stage("sq_vault11") == 10, "квест остался на «знаю про убежище» — мэру идти не с чем")

# ===================================================== 3. Последний банк Вегаса
b, g = hero("vegas_strip", caps=900)
caps0 = g.inventory.count("крышки")
b.side("Последний банк Вегаса", lambda: SQ.heist(b))
ok(g.stage("sq_heist") == 100 and g.flags.get("bank_sealed"),
   f"хранилище запечатано (стадия {g.stage('sq_heist')}) — деньги пустоши остались деньгами")
ok(g.flags.get("know_bank") and g.flags.get("crew_jin") and g.flags.get("crew_red") and g.flags.get("bank_crew"),
   "наводка крупье, команда Джин и Ред, охрана снята командой (не взломом и не динамитом)")
ok(not g.flags.get("bank_looted") and abs(g.rep_price_mult() - (1 - min(0.15, g.rep("vegas") / 400))) < 1e-9,
   f"крышки не обесценены: множитель цен {g.rep_price_mult():.2f} (инфляции 1.15 нет)")
ok(g.inventory.count("крышки") == caps0 - 200,
   f"Джин заплачено двести вперёд: было {caps0}, стало {g.inventory.count('крышки')}")
ok(g.rep("hub") >= 25 and any(t[0] == "heister" for t in g.titles()) and not b.side_fails,
   f"звание «Медвежатник» и репутация Хаба {g.rep('hub')}; провалов нет: {b.side_fails}")

b, g = hero("vegas_strip", caps=0, bare=True)
b.side("Последний банк Вегаса", lambda: SQ.heist(b))
ok(any("Последний банк Вегаса" in f and "Джин" in f for f in b.side_fails),
   f"нечем платить Джин — причина в отчёте: {b.side_fails}")
ok(g.stage("sq_heist") == 10 and not g.flags.get("bank_vault_open"),
   "люк найден, но в подвал бот не лез: охрана на пульте, квест не тронут")

# ===================================================== 4. Беглый субъект
b, g = hero("nipton", speech=55)
b.side("Беглый субъект", lambda: SQ.subject(b))
ok(g.stage("sq_subject") == 100 and g.flags.get("marta_home"),
   f"Марта дома, Ниптон её принял (стадия {g.stage('sq_subject')})")
ok(g.flags.get("know_ted_marta") and g.flags.get("marta_free") and g.flags.get("marta_cage_open"),
   "Тед рассказал про Марту, Тихоня открыл лифт, клетка № 12 открыта терминалом")
ok(g.rep("nipton") >= 30 and not b.side_fails, f"репутация Ниптона {g.rep('nipton')}, провалов нет: {b.side_fails}")

b, g = hero("nipton")
g.flags["v4_open"] = True                              # дверь-шестерня открыта в акте II
g.flags["term_v4_lab_v4cages_lockout"] = True          # лабораторный терминал заблокирован, с Сим не договорено
b.side("Беглый субъект", lambda: SQ.subject(b))
ok(any("Беглый субъект" in f and "клетка" in f for f in b.side_fails),
   f"клетка не открылась — причина в отчёте: {b.side_fails}")
ok(g.stage("sq_subject") == 10 and not g.flags.get("marta_free"),
   "Марта в клетке: квест не закрыт выдуманным флагом")

# ===================================================== 5. Барстоу: гули в одной клетке (регрессия)
m = json.load(open("data/maps/barstow.json", encoding="utf-8"))
blocked = {tuple(t) for t in m["blocked"]}
h = m["hordes"][0]
door = tuple(h["door"])
ok(door == (7, 26) and door not in blocked,
   f"толпа вываливается из дверного проёма на двор {door}, а не изнутри развалин")
ok(h["count"] == 15 and h["trigger"] == [4, 24, 11, 26],
   "толпа та же: 15 гулей по зоне двора (4,24)-(11,26)")
inside = [(e[1], e[2]) for e in m["enemies"] if 4 <= e[1] <= 11 and 27 <= e[2] <= 32]
ok(not inside, f"в каменной коробке развалин (4..11, 27..32) ни одного гуля: {inside}")
ok(ACTION._nudge(0.5) == 1 and ACTION._nudge(-0.49) == -1 and ACTION._nudge(0) == 0 and ACTION._nudge(7.4) == 7,
   "расталкивание гулей не округляется в ноль: полпикселя даёт сдвиг на пиксель")


def barstow(seed):
    b = PT.Bot(seed=seed, sides=True)
    b.go("ruins")
    g = b.g
    p = g.player
    p.level_sys.level = 10
    p.max_hp = p.hp = 160
    p.skills["guns"] = 110
    p.weapon = "assault"
    g.inventory.add("автомат", 1)
    g.inventory.add("патроны", 300)
    g.inventory.add("крышки", 200)
    for c in ("hub", "barstow"):
        g.reveal_location(c)
    b.side("Контракт на Барстоу", lambda: SQ.merc_contract(b))
    return b, g


for seed in (6, 9):                                    # эти два броска раньше вставали на 20
    b, g = barstow(seed)
    yard = g.get_location("barstow")
    alive = [f"{e.type_id}@{tile_of(e)}" for e in yard.enemies if e.alive and e.hostile]
    ok(g.stage("sq_merc") == 100 and g.stage("sq_barstow") == 100 and not b.side_fails,
       f"бросок {seed}: двор Барстоу зачищен, контракт 100 ({b.side_fails})")
    ok(not alive, f"бросок {seed}: во дворе не осталось ни одного гуля — в том числе в клетке (8,31) {alive[:4]}")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
