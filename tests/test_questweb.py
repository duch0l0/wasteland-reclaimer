"""
Паутина квестов: «Пропавшие караваны», «Экспедиция Гарольда», «Цена воды», «Штурм Форта», «Кровь Убежища 11»,
«Последний банк Вегаса», «Беглый субъект» — улики, тактика, выборы и их последствия.

    .venv/bin/python tests/test_questweb.py
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


def start():
    g = Game(intro=False)
    g.player.max_hp = g.player.hp = 10 ** 5
    for lid in ("hub", "needles", "aradesh", "spot_toll"):
        g.reveal_location(lid)
    go(g, "hub")
    talk(g, "crimson_boss"); say(g, "пропадают караваны"); say(g, "Дай мне время"); say(g, "Договорились")
    return g


# ---- 1. обвинить Ханов сразу — ошибка
g = start()
ok(g.stage("sq_caravans") == 10, "Красный караван нанял искать пропавших")
talk(g, "crimson_boss"); say(g, "Я знаю, кто виноват"); say(g, "Ханы"); say(g, "...")
ok(g.flags.get("khans_wiped") and g.stage("sq_caravans") == 100 and g.karma < 0, "назвал Ханов — их вырезали, карма вниз")
go(g, "aradesh_canyon")
ok(not any(n.npc_id.startswith("khan") for n in g.npcs), "в каньоне Ханов больше нет")

# ---- 2. вся правда: улики, Билли через мать
g = start()
talk(g, "caravan_lars"); say(g, "Кто напал"); say(g, "Спасибо")
ok(g.flags.get("clue_survivor") and g.stage("sq_caravans") == 30, "Ларс: «брод держи» — так говорят речники")
go(g, "spot_toll")
take(g, "сожжённый фургон каравана")
read(g, "стрела Ханов"); read(g, "обрывок накладной")
ok(g.flags.get("clue_arrow") and g.flags.get("clue_route"), "стрела с заводским клеймом, маршрут знали заранее")
ok(g.stage("sq_caravans") == 60, "три улики — картина складывается")
go(g, "aradesh_canyon")
g.open_terminal("convoy_wreck")
idx = next(k for k, (_, e) in enumerate(g.term_entries()) if e["label"] == "Груз")
g.term_open_entry(idx); g.close_terminal()
ok(g.flags.get("clue_cargo"), "фургон культа: «люди — 6, возницы каравана»")
go(g, "needles_bridge")
g.flags["term_needles_toll_tollside_open"] = True                   # пароль ПЕРЕПРАВА — взлом проверен в других тестах
g.open_terminal("needles_toll")
idx = next(k for k, (_, e) in enumerate(g.term_entries()) if "Платные" in e["label"])
g.term_open_entry(idx); g.close_terminal()
ok(g.flags.get("clue_toll"), "журнал моста: маршруты проданы «белым», подпись Б.")
g.flags["ferry_done"] = True                      # Кейт доверяет герою
talk(g, "billy"); say(g, "платные проводки"); say(g, "Пойдём к матери"); say(g, "Пойдём")
go(g, "needles")
talk(g, "kate"); say(g, "Билли должен"); say(g, "...")
ok(g.flags.get("billy_turned"), "Кейт решила: Билли будет сливать маршруты культа каравану")
go(g, "hub")
talk(g, "crimson_boss"); say(g, "Я знаю, кто виноват"); say(g, "Стражник Билли"); say(g, "С ним разобрались"); say(g, "...")
ok(g.flags.get("caravans_truth") and g.flags.get("caravan_pass") and not g.flags.get("khans_wiped"),
   "лучший исход: правда, Ханы целы, пропуск Красного каравана")
ok(any(t[0] == "sleuth" for t in g.titles()), "звание «Сыщик трассы 15»")

# ---- 3. только культ
g = start()
g.flags["clue_cargo"] = True
talk(g, "crimson_boss"); say(g, "Я знаю, кто виноват"); say(g, "забирает культ"); say(g, "...")
ok(g.flags.get("caravans_detour") and not g.flags.get("billy_hanged"), "только культ: караваны в обход, Билли остался безнаказанным")


# ------------------------------------------------------------ «Экспедиция Гарольда»: обход финального штурма
g = Game(intro=False)
g.player.max_hp = g.player.hp = 10 ** 5
g.reveal_location("hub"); g.reveal_location("mariposa")
go(g, "mariposa")
gate = next(p for p in g.level.portals if p["to"] == "mariposa_vats")
g.player.rect.topleft = rect_pos_for_tile(g.player, sorted(gate["tiles"])[0])
fr(g, 4)
ok(g.loc.id == "mariposa", "без Гарольда решётка грузового въезда заперта")
go(g, "hub_old")
talk(g, "harold"); say(g, "Что с тобой"); say(g, "А потом"); say(g, "Ещё вопрос"); say(g, "Создатель"); say(g, "Как попасть"); say(g, "Передам")
ok(g.flags.get("know_cargo_bay") and g.stage("sq_harold") == 50, "Гарольд: грузовой въезд, скоба у петли")
go(g, "mariposa")
gate = next(p for p in g.level.portals if p["to"] == "mariposa_vats")
g.player.rect.topleft = rect_pos_for_tile(g.player, sorted(gate["tiles"])[0])
fr(g, 4)
ok(g.loc.id == "mariposa_vats", "через кран-бэй — прямо к чанам, мимо двора и лаборатории")
g.open_terminal("mariposa_1977")
idx = next(k for k, (_, e) in enumerate(g.term_entries()) if "Купели" in e["label"])
g.term_open_entry(idx); g.close_terminal()
ok(g.stage("sq_harold") == 100, "журнал «Купели»: Грей выжил — Создатель это он")


# ------------------------------------------------------------ «Цена воды»: Хаб ↔ Джанктаун, Декер посередине
def water_start():
    g = Game(intro=False)
    g.player.max_hp = g.player.hp = 10 ** 5
    for lid in ("hub", "junktown"):
        g.reveal_location(lid)
    go(g, "junktown")
    talk(g, "water_seller"); say(g, "подорожала"); say(g, "Разберусь")
    go(g, "hub") if any(True for _ in []) else None
    return g


g = water_start()
ok(g.stage("sq_water_war") == 10, "водовоз Сэл: вода по шестнадцать, винит Вегу")
go(g, "hub")
talk(g, "water_clerk"); say(g, "подняли цену"); say(g, "Кто берёт"); say(g, "Спасибо")
ok(g.flags.get("clue_middleman") and g.stage("sq_water_war") == 50, "артель: цену не поднимали, берёт посредник «Д.»")
go(g, "hub_old")
g.inventory.add("гроссбух Декера", 1)            # вскрыть сейф Декера — кража проверена в других тестах
read(g, "гроссбух Декера")
go(g, "junktown_hall")
talk(g, "mayor_darkwater"); say(g, "гроссбух Декера"); say(g, "...")
ok(g.flags.get("water_direct") and g.stage("sq_water_war") == 100 and g.rep("junktown") > 0,
   "гроссбух у мэра: Вега и Дарквотер напрямую, Декер разоблачён")

g = water_start()
go(g, "hub"); talk(g, "water_clerk"); say(g, "подняли цену"); say(g, "Кто берёт"); say(g, "Спасибо")
go(g, "hub_old")
talk(g, "decker"); say(g, "перекупаешь"); say(g, "По рукам"); say(g, "...")
ok(g.flags.get("water_decker") and g.karma < 0 and g.inventory.count("крышки") >= 600, "доля с Декером: 600 крышек, карма вниз")

g = water_start()
g.player.skills["science"] = 60
g.inventory.add("гаечный ключ", 1)
talk(g, "water_seller"); say(g, "старый насос"); say(g, "Пейте")
ok(g.flags.get("junktown_pump") and g.rep("junktown") >= 40, "свой насос: Джанктаун больше никому не должен за воду")


# ------------------------------------------------------------ «Штурм Форта»: подготовка решает
g = Game(intro=False)
g.player.max_hp = g.player.hp = 10 ** 5
g.reveal_location("searchlight")
g.flags["fort_job"] = True
go(g, "fort_searchlight")
talk(g, "recruit_danny"); say(g, "пароль пульта"); say(g, "Маме")
ok(g.flags.get("know_fort_pw"), "Дэнни изнутри: пароль пульта охраны — ГАРНИЗОН")


def press(g, tid, label):
    g.open_terminal(tid)
    idx = next(k for k, (_, e) in enumerate(g.term_entries()) if label in e["label"])
    g.term_open_entry(idx)
    if g.term and g.term.get("view") == "locked":
        g.lock_options()[0][1]()                  # пароль известен — «Ввести пароль»
    g.close_terminal()


press(g, "fort_security", "Отключить турели")
g.player.skills["science"] = 75
press(g, "fort_security", "учения")
bunker = g.get_location("fort_bunker")
ok(not any(e.type_id == "turret" for e in bunker.enemies) and not any(e.type_id == "robot_guard" for e in bunker.enemies),
   "турели выключены, роботы ушли на учения — бункер пуст")
g.enter_location("fort_bunker"); fr(g)
ok(not g.enemies, "в бункере ни одного врага")
ok(any(t[0] == "tactician" for t in g.titles()) is False, "звание «Тактик» — только после роспуска призыва")


# ------------------------------------------------------------ «Кровь Убежища 11»
def v11_start():
    g = Game(intro=False)
    g.player.max_hp = g.player.hp = 10 ** 5
    g.reveal_location("nipton")
    go(g, "nipton_hall")
    g.open_terminal("nipton_ledger")
    idx = next(k for k, (_, e) in enumerate(g.term_entries()) if "Устав" in e["label"])
    g.term_open_entry(idx); g.close_terminal()
    fr(g)
    return g


g = v11_start()
ok(g.stage("sq_vault11") == 10 and "vault11" in g.worldmap.known, "устав Ярмарки: Э. Кэрролл из Убежища 11 — убежище на карте")
go(g, "vault11_hall")
take(g, "шкафчик Кэтрин Стоун")
read(g, "дневник Кэтрин Стоун")
go(g, "vault11_core")
g.flags["term_v11_core_v11core_open"] = True
g.open_terminal("v11_core")
for label in ("Протокол", "Список выживших"):
    idx = next(k for k, (_, e) in enumerate(g.term_entries()) if label in e["label"])
    g.term_open_entry(idx)
    g.term_back()
g.close_terminal()
ok(g.flags.get("know_v11_truth") and g.stage("sq_vault11") == 50, "протокол: угроза была ложью — дверь открывалась тем, кто откажется")
g.player.skills["speech"] = 70
go(g, "nipton")
talk(g, "mayor_carroll"); say(g, "Убежище 11"); say(g, "Выйди на площадь"); say(g, "...")
ok(g.flags.get("v11_confessed") and g.flags.get("nipton_decided") and g.rep("nipton") >= 50, "мэр сам читает дневник на площади и сжигает жребии")

g = v11_start()
g.flags["know_v11_truth"] = True
go(g, "nipton")
talk(g, "mayor_carroll"); say(g, "Убежище 11"); say(g, "Пятьсот крышек"); say(g, "...")
ok(g.flags.get("v11_blackmail") and g.karma < 0, "шантаж: 500 крышек, Ниптон так и не узнал")


# ------------------------------------------------------------ «Последний банк Вегаса»
def heist_start():
    g = Game(intro=False)
    g.player.max_hp = g.player.hp = 10 ** 5
    for lid in ("vegas_strip", "junktown"):
        g.reveal_location(lid)
    go(g, "vegas_den")
    talk(g, "den_dealer"); say(g, "новенькие крышки"); say(g, "Спасибо")
    return g


def term(g, tid, label):
    g.open_terminal(tid)
    idx = next(k for k, (_, e) in enumerate(g.term_entries()) if label in e["label"])
    g.term_open_entry(idx); g.close_terminal()
    fr(g, 2)


g = heist_start()
ok(g.stage("sq_heist") == 10 and g.flags.get("know_bank"), "крупье Змей проговорился: люк в подвал банка")
g.inventory.add("крышки", 500)
go(g, "junktown_dump")
talk(g, "scrapper_girl"); say(g, "сейф довоенного банка"); say(g, "Двести")
go(g, "vegas_boots")
talk(g, "boots_rider_b"); say(g, "прикрытие"); say(g, "в деле")
go(g, "vegas_strip")
hatch = next(p for p in g.level.portals if p["to"] == "vegas_bank")
g.player.rect.topleft = rect_pos_for_tile(g.player, sorted(hatch["tiles"])[0])
fr(g, 4)
ok(g.loc.id == "vegas_bank", "по наводке — вниз, в подвал банка")
term(g, "bank_security", "Джин — сейф, Ред")
door = g.level.gates[0]
ok(g.flags.get("bank_vault_open") and not g.enemies and door["open"], "команда: турель и роботы обезврежены, бронедверь открыта")
ok(g.stage("sq_heist") == 50, "журнал: хранилище открыто")
price0 = None
g.enemies[:] = []
term(g, "bank_vault", "Набить рюкзак")
ok(g.flags.get("bank_looted") and g.inventory.count("крышки") >= 2500, "мешки крышек — в рюкзак")
ok(abs(g.rep_price_mult() - (1 - min(0.15, g.rep("vegas") / 400)) * 1.15) < 1e-9, "крышек стало больше — всё на 15% дороже (инфляция)")
ok(any(t[0] == "heister" for t in g.titles()), "звание «Медвежатник»")

g = heist_start()
g.inventory.add("динамит", 1)
go(g, "vegas_bank")
term(g, "bank_security", "динамит")
ok(g.flags.get("bank_vault_open") and g.flags.get("bank_loud"), "динамит: дверь вынесена — и тревога")
g.enemies[:] = []
term(g, "bank_vault", "Запечатать")
ok(g.flags.get("bank_sealed") and g.rep("hub") > 0 and g.rep_price_mult() <= 1.0, "запечатал: деньги пустоши остались деньгами")


# ------------------------------------------------------------ «Беглый субъект»: Марта из Ниптона
g = Game(intro=False)
g.player.max_hp = g.player.hp = 10 ** 5
for lid in ("nipton", "vault4"):
    g.reveal_location(lid)
go(g, "nipton")
talk(g, "np_drunk"); say(g, "Как её звали"); say(g, "Я поищу")
ok(g.stage("sq_subject") == 10, "Тед: Марту двадцать лет назад продали на запад, к «учёным»")
go(g, "vault4_lower")
talk(g, "marta_subject"); say(g, "Тед из Ниптона"); say(g, "вытащу"); say(g, "Жди")
g.flags["term_v4_lab_v4cages_open"] = True
term(g, "v4_lab", "клетку субъекта")
ok(g.flags.get("marta_cage_open"), "терминал лаборатории: клетка № 12 открыта")
talk(g, "marta_subject"); say(g, "Клетка открыта"); say(g, "Дойди")
ok(g.flags.get("marta_free") and not any(n.npc_id == "marta_subject" for n in g.npcs), "Марта ушла в Ниптон сама")
go(g, "nipton")
talk(g, "np_drunk"); say(g, "Марта жива"); say(g, "встать рядом"); say(g, "...")
ok(g.flags.get("marta_home") and g.stage("sq_subject") == 100 and g.rep("nipton") >= 30, "Ниптон принял Марту, Тед трезв")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
