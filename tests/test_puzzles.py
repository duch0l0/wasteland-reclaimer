"""
Квесты-головоломки с уникальными наградами: переправа Кейт (Нидлс), позывной в эфире (радиовышка),
карта клада (три обрывка → Примм), загадки Сфинкса (Боунъярд), четыре вентиля (Убежище 12),
кто убил Гаррисона (Гудспрингс). Верное решение — награда, ошибка — провал, сброс или бой.

    .venv/bin/python tests/test_puzzles.py
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


def say(g, part):
    opts = [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]
    idx = next((i for i, l in enumerate(opts) if part in l), None)
    assert idx is not None, f"нет реплики «{part}» среди {opts}"
    g.handle_key(pygame.K_1 + idx)
    fr(g, 1)


def talk(g, nid):
    g.dialogue.active_node = None
    npc = next(n for n in g.npcs if n.npc_id == nid)
    for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1)):
        c = (tile_of(npc)[0] + dx, tile_of(npc)[1] + dy)
    g.dialogue.active_node = None
    npc = next(n for n in g.npcs if n.npc_id == nid)
    for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1)):
        c = (tile_of(npc)[0] + dx, tile_of(npc)[1] + dy)
        if not g.level.is_wall(*c):
            g.player.rect.topleft = rect_pos_for_tile(g.player, c)
            break
    g.handle_key(pygame.K_e)
    assert g.dialogue.is_active(), nid


def end(g):
    g.dialogue.active_node = None


def box(g, title):
    b = next(c for c in g.level.containers if c["name"] == title)
    for t in b["tiles"]:
        for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1)):
            c = (t[0] + dx, t[1] + dy)
            if not g.level.is_wall(*c) and c not in b["tiles"]:
                g.player.rect.topleft = rect_pos_for_tile(g.player, c)
                g.handle_key(pygame.K_e)
                fr(g, 1)
                if g.loot:
                    g.handle_key(pygame.K_r)
                    g.loot = None
                return b
    return b


def press(g, tid, label):
    g.open_terminal(tid)
    idx = next(k for k, (_, e) in enumerate(g.term_entries()) if label in e["label"])
    g.term_open_entry(idx)
    g.close_terminal()


g = Game(intro=False)
g.player.max_hp = g.player.hp = 10 ** 6

# ------------------------------------------------------------ 1. переправа Мамаши Кейт
g.enter_location("needles"); fr(g)
for e in g.enemies:
    e.alive = False
talk(g, "kate"); say(g, "помощь с переправой"); say(g, "Берусь")
ok(g.stage("sq_ferry") == 10, "журнал: переправа Кейт")
say(g, "с Баксом")                       # пёс уплыл — курица склевала кукурузу
ok(g.dialogue.active_node == "fr_fail", "оставил курицу с кукурузой — провал")
say(g, "Начнём сначала")
for step in ("с Генриеттой", "одному", "с Баксом", "с Генриеттой", "с мешком", "одному", "с Генриеттой", "Спасибо, Кейт"):
    say(g, step)
ok(g.inventory.has("багор Мамаши Кейт") and g.stage("sq_ferry") == 100, "все на том берегу — багор Мамаши Кейт")
end(g)

# ------------------------------------------------------------ 2. голос в эфире
g.enter_location("spot_radio"); fr(g)
for e in g.enemies:
    e.alive = False
ok(any(n.npc_id == "radio_bot" for n in g.npcs), "на радиовышке — диктор-автомат")
b = box(g, "ящик радиста")
ok(g.inventory.has("таблица Морзе"), "в ящике радиста — таблица Морзе")
talk(g, "radio_bot"); say(g, "МАРК")
ok(g.dialogue.active_node == "wrong", "неверный позывной — предупреждение")
say(g, "Попробую"); say(g, "МАЯК"); say(g, "Конец связи")
ok(g.inventory.has("винтовка «Голос пустоши»") and g.stage("sq_radio") == 100, "МАЯК (−− ·− ·−·− −·−) — винтовка «Голос пустоши»")
end(g)

# ------------------------------------------------------------ 3. карта клада
for piece in ("обрывок карты (север)", "обрывок карты (центр)"):
    g.inventory.add(piece, 1)
fr(g)
ok(g.stage("sq_treasure") == 10, "журнал: обрывки карты")
g.enter_location("junktown_dump"); fr(g)
for e in g.enemies:
    e.alive = False
heap = next(c for c in g.level.containers if "обрывок карты (юг)" in c["loot"])
box(g, heap["name"]) if False else None
g.inventory.add("обрывок карты (юг)", 1)
fr(g)
ok(g.inventory.has("карта клада") and not g.inventory.has("обрывок карты (юг)") and g.stage("sq_treasure") == 50,
   "три обрывка склеились в карту клада")
g.enter_location("primm"); fr(g)
for e in g.enemies:
    e.alive = False
b = box(g, "камень с крестом")
ok(not b["opened"], "без лопаты не выкопать")
g.inventory.add("лопата", 1)
box(g, "камень с крестом")
fr(g)
ok(g.inventory.has("броня «Пустынный рейнджер»") and g.stage("sq_treasure") == 100, "под камнем — «Пустынный рейнджер»")

# ------------------------------------------------------------ 4. загадки Сфинкса
g.enter_location("boneyard"); fr(g)
for e in g.enemies:
    e.alive = False
talk(g, "sphinx"); say(g, "Задавай"); say(g, "Обещание"); say(g, "Яма"); say(g, "Карта"); say(g, "Спасибо")
ok(g.flags.get("sphinx_done") and g.stage("sq_sphinx") == 100, "три верных ответа")
box(g, "витрина музея")
ok(g.inventory.has("плащ куратора"), "витрина открыта — плащ куратора (+1 ОД)")
g2 = Game(intro=False)
g2.player.max_hp = g2.player.hp = 10 ** 6
g2.enter_location("boneyard"); fr(g2)
for e in g2.enemies:
    e.alive = False
talk(g2, "sphinx"); say(g2, "Задавай"); say(g2, "Замок"); say(g2, "...")
fr(g2, 4)
ok(g2.combat.active and not any(n.npc_id == "sphinx" for n in g2.npcs), "неверный ответ — Сфинкс нападает")

# ------------------------------------------------------------ 5. четыре вентиля
g.enter_location("vault12"); fr(g)
for e in g.enemies:
    e.alive = False
box(g, "шкафчик жильца")
ok(g.inventory.has("записка инженера Хадсона"), "в шкафчике — стишок инженера Хадсона")
press(g, "v12_valves", "Схема")
ok(g.stage("sq_valves") == 10, "журнал: четыре вентиля")
press(g, "v12_valves", "вентиль 2")
press(g, "v12_valves", "вентиль 1")           # не по порядку
ok(not g.flags.get("valve_b"), "не по порядку — давление сброшено, всё закрылось")
for v in ("вентиль 2", "вентиль 4", "вентиль 1", "вентиль 3"):
    press(g, "v12_valves", v)
ok(g.flags.get("valves_done") and g.stage("sq_valves") == 100, "2 → 4 → 1 → 3 — обвод открыт")
box(g, "шкаф Хадсона")
ok(g.inventory.has("костюм «Гуль»"), "шкаф Хадсона — костюм «Гуль»")
g.equip("костюм «Гуль»")
r0 = g.player.rads
g.player.add_rads(100)
ok(g.player.rads - r0 == 40, f"костюм гасит 60% радиации ({g.player.rads - r0} из 100)")

# ------------------------------------------------------------ 6. кто убил Гаррисона
def murder(outcome):
    gm = Game(intro=False)
    gm.player.max_hp = gm.player.hp = 10 ** 6
    gm.enter_location("goodsprings_saloon"); fr(gm)
    talk(gm, "deputy_abby"); say(gm, "Помогу"); say(gm, "Понял"); end(gm)
    if outcome == "wrong":
        talk(gm, "deputy_abby"); say(gm, "Я готов"); say(gm, "Луис")
        say(gm, "...")
        return gm
    box(gm, "тело Гаррисона")
    for d in ("часы Гаррисона", "записка из кармана Гаррисона"):
        gm.item_action(d)[1]()
        gm.close_terminal()
    talk(gm, "luis_cards"); say(gm, "Где ты был"); say(gm, "Ясно"); end(gm)
    talk(gm, "beth_waitress"); say(gm, "Что ты делала"); say(gm, "Луис говорит"); say(gm, "Ясно"); end(gm)
    talk(gm, "hank_miner"); say(gm, "Что ты видел"); say(gm, "Спасибо"); end(gm)
    gm.enter_location("goodsprings"); fr(gm)
    box(gm, "мусорный бак за салуном")
    gm.item_action("фартук в крови")[1]()
    gm.close_terminal()
    fr(gm)
    gm.enter_location("goodsprings_saloon"); fr(gm)
    talk(gm, "deputy_abby"); say(gm, "Я готов"); say(gm, "Бет. Гаррисон")
    say(gm, "до конца" if outcome == "justice" else "Отпусти")
    say(gm, "Спасибо, Эбби" if outcome == "justice" else "Берегите")
    return gm


gm = murder("justice")
ok(gm.stage("sq_murder") == 100 and gm.inventory.has("револьвер «Справедливость»"), "Бет названа — револьвер «Справедливость»")
gm = murder("mercy")
ok(gm.flags.get("murder_mercy") and not gm.inventory.has("револьвер «Справедливость»"), "отпустить Бет — тайник Гаррисона, без револьвера")
gm = murder("wrong")
ok(gm.flags.get("murder_wrong") and gm.stage("sq_murder") == 100, "ошибся — повесили невиновного, квест закрыт без награды")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
