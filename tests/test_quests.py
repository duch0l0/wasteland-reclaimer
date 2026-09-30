"""
Новые квесты Пятнадцатой и приёмы боя — без окна:
  «Крысы в ливнёвке» (самопал от шерифа), «Колбаса», «Нижний ярус»,
  «Святая вода», «Должок салуна», брошь Ордена Тайн;
  порталы в подземелья, гермодверь, тьма под землёй;
  яд, радиация, гранаты, взрыв бочки, турель, трус, укрытие; сохранение.

    .venv/bin/python tests/test_quests.py
"""
import os
import random
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
from src.combat import tile_of, rect_pos_for_tile, chebyshev  # noqa: E402
from src.location import make_enemy  # noqa: E402
from src import props as P  # noqa: E402

saveload.SAVE_DIR = tempfile.mkdtemp()
failed = []


def ok(cond, msg):
    print(("OK   " if cond else "FAIL ") + msg)
    if not cond:
        failed.append(msg)


def fr(g, n=2):
    for _ in range(n):
        g.update(16)
        g.draw()
        if g.perk_choices:
            g.handle_key(pygame.K_1)


def calm(g):
    for e in g.enemies:
        e.aggro = 0
        e.wander_wait = 10 ** 9
    for n in g.npcs:
        n.wander_wait = 10 ** 9


def stand_near(g, tiles):
    for t in tiles:
        for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (-1, 1), (0, 2)):
            c = (t[0] + dx, t[1] + dy)
            if not g.level.is_wall(*c) and c not in tiles and not g.level.is_exit(*c) \
                    and not g.level.portal_at(*c):
                g.player.rect.topleft = rect_pos_for_tile(g.player, c)
                g.snap_camera()
                return
    raise AssertionError(f"негде встать рядом с {tiles}")


def talk(g, npc_id):
    npc = next(n for n in g.npcs if n.npc_id == npc_id)
    stand_near(g, [tile_of(npc)])
    g.handle_key(pygame.K_e)
    assert g.dialogue.is_active(), f"разговор с {npc_id} не начался"


def options(g):
    return [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]


def say(g, part):
    opts = options(g)
    idx = next((i for i, lbl in enumerate(opts) if part in lbl), None)
    assert idx is not None, f"нет реплики «{part}» среди {opts}"
    g.handle_key(pygame.K_1 + idx)
    fr(g, 1)


def open_box(g, title):
    box = next(c for c in g.level.containers if c["name"].startswith(title))
    stand_near(g, box["tiles"])
    g.open_container(box)
    return box


def take_all(g, title):
    open_box(g, title)
    if g.loot:
        g.loot_take_all()
        g.close_loot()


def read_terminal(g, tid, label_part):
    g.open_terminal(tid)
    entries = g.term_entries()
    idx = next(i for i, (_, e) in enumerate(entries) if label_part in e["label"])
    g.term_open_entry(idx)
    g.close_terminal()


def through_portal(g, to):
    """Встать на клетку портала — как если бы герой дошёл туда сам."""
    p = next(p for p in g.level.portals if p["to"] == to)
    tile = sorted(p["tiles"])[0]
    here = g.loc.id
    for _ in range(10):  # окно перка после нового уровня сначала закроется
        g.player.rect.topleft = rect_pos_for_tile(g.player, tile)
        fr(g, 1)
        if g.loc.id != here:
            break


random.seed(7)
g = Game(intro=False)
g.player.max_hp = g.player.hp = 10 ** 5
calm(g)

# ================================================================ город
ok(all(any(n.npc_id == i for n in g.npcs) for i in ("sheriff", "doc", "ada", "silas", "mo", "lenny", "marta", "dale")),
   "в городе живут шериф, Док, Смотрительница, проповедник, Мо, Лен, Марта, Дейл")
ok(not any(p["kind"] == "самопал" for p in g.level.pickups), "самопал на земле не валяется — его надо заработать")
ok(len(g.level.portals) == 2, "в городе два спуска: ливнёвка и Убежище 57")
g.open_terminal("doc:doc_board_market")
ok(g.term and g.term.get("doc") == "doc_board_market", "доска объявлений читается")
g.close_terminal()

# крыши: снаружи дом накрыт, внутри крыша тает
saloon = next(r for r in g.level.roofs if r.get("sign") == "САЛУН")
g.player.rect.topleft = rect_pos_for_tile(g.player, (22, 30))
fr(g, 30)
ok(saloon["alpha"] == 255, "снаружи у салуна крыша")
g.player.rect.topleft = rect_pos_for_tile(g.player, (22, 23))
fr(g, 30)
ok(saloon["alpha"] == 0, "внутри салуна крыша исчезла")
ok(not any(r.get("sign") is None and r["x0"] == 2 and r["y0"] == 37 for r in g.level.roofs), "у дома Черепана крыши нет")

# ================================================================ Крысы в ливнёвке (отравленная приманка)
talk(g, "sheriff")
say(g, "Мне нужно оружие")
say(g, "Берусь")
ok(g.stage("sq_rats") == 10, "шериф дал работу: крысы в ливнёвке")
talk(g, "doc")
say(g, "Крысолюды в ливнёвке")
ok(g.inventory.has("отравленная приманка"), "Док дала отравленную приманку")
g.dialogue.close()
through_portal(g, "drain")
ok(g.loc.id == "drain" and g.level.dark, "люк в руинах ведёт в тёмную ливнёвку")
calm(g)
box = open_box(g, "кормушка крысолюдов")
ok(g.loot is not None, "кормушку крысолюдов можно обыскать")
g.loot_put("отравленная приманка")
ok(not any(e.alive and e.pack == "ratmen" for e in g.enemies), "приманка в кормушке — крысолюды отравлены")
ok(g.flags.get("rats_cleared") and g.stage("sq_rats") == 50, "ливнёвка чиста — вернуться к шерифу")
take_all(g, "сумка культиста")
ok(g.inventory.has("листовка Единства"), "в ливнёвке — сумка культиста")
through_portal(g, "ruins")
ok(g.loc.id == "ruins", "по лестнице — обратно в город")
calm(g)
talk(g, "sheriff")
say(g, "Спасибо, шериф")
ok(g.inventory.has("самопал") and g.inventory.count("патроны") >= 12 and g.stage("sq_rats") == 100,
   "шериф отдал самопал и 12 патронов")
g.dialogue.close()

# ================================================================ Колбаса: лопата и жетон
grave = next(c for c in g.level.containers if c["name"] == "могила «Колбаса»")
stand_near(g, grave["tiles"])
g.open_container(grave)
ok(g.loot is None, "без лопаты могилу не раскопать")
shovel = next(p for p in g.level.pickups if p["kind"] == "лопата")
g.player.rect.topleft = rect_pos_for_tile(g.player, (shovel["rect"].x // 48, shovel["rect"].y // 48))
g.handle_key(pygame.K_e)
ok(g.inventory.has("лопата"), "лопата у сторожки")
take_all(g, "могила «Колбаса»")
ok(g.inventory.has("жетон Эймоса") and g.stage("sq_kolbasa") == 100, "в могиле Колбасы — жетон деда")
g.open_document("doc_dogtag")
g.close_terminal()
ok(g.flags.get("know_mariposa_list"), "жетон: Список Марипозы из семи фамилий")

# ================================================================ Нижний ярус
talk(g, "ada")
say(g, "Расскажите про Убежище 57")
say(g, "Что на нижнем ярусе")
say(g, "Ясно")
say(g, "Мне нужна ключ-карта")
say(g, "На жетоне деда")
ok(g.inventory.has("ключ-карта Б"), "Ада отдала ключ-карту, увидев фамилию отца на жетоне")
g.dialogue.close()
through_portal(g, "vault57")
ok(g.loc.id == "vault57", "дверь-шестерня ведёт в Убежище 57")
calm(g)
gate = g.level.gates[0]
ok(g.level.is_wall(*gate["tiles"][0]), "гермодверь яруса Б закрыта")
stand_near(g, gate["tiles"])
g.handle_key(pygame.K_e)
ok(gate["open"] and not g.level.is_wall(*gate["tiles"][0]), "ключ-карта открыла гермодверь")
ok(g.stage("sq_vault") >= 30, "журнал: гермодверь открыта")
turret = next(e for e in g.enemies if e.type_id == "turret")
read_terminal(g, "vault_lab", "Результаты")
read_terminal(g, "vault_overseer", "Последняя запись")
ok(g.flags.get("know_serum") and g.flags.get("know_cross_last"), "терминалы яруса Б прочитаны")
take_all(g, "шкаф с журналами")
take_all(g, "холодильник с сывороткой")
ok(g.inventory.has("журнал «Проект Панцирь»") and g.inventory.has("сыворотка «Панцирь»"),
   "журналы и сыворотка «Проекта Панцирь»")
ok(g.stage("sq_vault") == 50, "журнал: решить, кому отдать правду")
through_portal(g, "ruins")
calm(g)
talk(g, "turtle")
say(g, "Вот сыворотка")
ok(g.flags.get("turtle_serum"), "Черепану стало легче от сыворотки")
g.dialogue.close()
talk(g, "gena")
say(g, "Вот журналы «Проекта Панцирь»")
ok(g.flags.get("panzer_to_gena") and g.stage("sq_vault") == 100, "Гена узнал, откуда рога")
g.dialogue.close()
talk(g, "ada")
say(g, "Я был в ярусе Б")
say(g, "Он не бросил вас")
ok(g.flags.get("ada_told"), "Ада узнала правду об отце")
g.dialogue.close()

# ================================================================ Святая вода
talk(g, "doc")
say(g, "Проповедник раздаёт воду")
say(g, "Принесу")
talk(g, "silas")
say(g, "Дай пробу")
ok(g.inventory.has("святая вода") and g.stage("sq_holywater") == 30, "проба «святой воды» у героя")
g.dialogue.close()
talk(g, "doc")
say(g, "Вот проба")
ok(g.flags.get("holy_proof") and g.stage("sq_holywater") == 50, "Док нашла снотворное и мутаген")
g.dialogue.close()
g.set_stage("mq_grandpa", 20)      # дом деда уже видели
talk(g, "silas")
say(g, "Твои братья увезли старика")
ok(g.flags.get("know_baker"), "Сайлас выдал, что дед — в Бейкере")
say(g, "...")
say(g, "Док нашла в твоей воде")
say(g, "Люди! Его вода")
ok(not any(n.npc_id == "silas" for n in g.npcs) and g.stage("sq_holywater") == 100, "проповедника разоблачили при всех")
g.dialogue.close()

# ================================================================ Должок салуна и брошь Ордена
talk(g, "mo")
say(g, "Лен тебе должен")
say(g, "Выбью")
g.flags["heard_holotape"] = True
say(g, "Что это за значок")
say(g, "Да. Про Марипозу")
ok(g.inventory.has("знак Ордена Тайн"), "Мо отдал брошь Ордена Тайн")
g.dialogue.close()
g.inventory.add("крышки", 30)
talk(g, "lenny")
say(g, "Мо говорит")
say(g, "Ладно, я заплачу")
ok(g.stage("sq_debt") == 100, "долг Лена закрыт")
g.dialogue.close()

# ================================================================ бой: яд, радиация, гранаты, бочка, турель, трус, укрытие
g.enter_location("vault57")
calm(g)
c = g.combat
p = g.player
p.hp = p.max_hp = 200
roach = next(e for e in g.enemies if e.type_id == "radroach" and e.alive)
stand_near(g, [tile_of(roach)])
roach.aggro = 300
c.start(player_first=True)
ok(c.active, "бой в убежище начался")
c._add_dot(p, "poison", 2, 3)
hp0 = p.hp
c._tick_dots(p)
ok(p.hp == hp0 - 2 and p.dots[0]["turns"] == 2, "яд отнимает HP в начале хода")
p.add_rads(120)
ok(p.hp_cap == p.max_hp - 12, "радиация съедает максимум HP")
g.inventory.add("антирадин", 1)
c.active = False
g.use_item("антирадин")
ok(p.rads == 0, "антирадин выводит радиацию")
c.active = True

# граната: бросок, полёт, взрыв задевает соседей
g.inventory.add("граната", 1)
c.target = roach
p.ap = p.max_ap
c.busy_ms = 0
stand = tile_of(roach)
g.player.rect.topleft = rect_pos_for_tile(p, next(t for t in ((stand[0] - 3, stand[1]), (stand[0] + 3, stand[1]),
                                                              (stand[0], stand[1] - 3), (stand[0], stand[1] + 3))
                                                   if not g.level.is_wall(*t)))
random.seed(1)
if c.los(p, roach):
    hp_r = roach.hp
    c.player_throw()
    ok(len(c.throws) == 1 and not g.inventory.has("граната"), "граната летит")
    for _ in range(80):
        c.update(16)
    ok(not c.throws and (roach.hp < hp_r or not roach.alive or c.blasts), "граната взорвалась")

# бочка: взрыв ранит всех рядом и исчезает
barrel = next(o for o in g.level.objects if P.info(o["name"]).get("explosive"))
bt = barrel["foot"][0]
feral = make_enemy((0, 0), "feral")
free = next((bt[0] + dx, bt[1] + dy) for dx, dy in ((1, 0), (-1, 0), (0, -1), (0, 1), (1, -1), (-1, -1))
            if not g.level.is_wall(bt[0] + dx, bt[1] + dy))
feral.rect.topleft = rect_pos_for_tile(feral, free)
g.loc.enemies.append(feral)
c.order.append(feral)
hp_f = feral.hp
c.blow_barrel(barrel)
ok(barrel.get("hidden") and not g.level.is_wall(*bt), "бочка взорвалась и исчезла")
ok(feral.hp < hp_f, "взрыв бочки задел гуля рядом")

# турель не двигается
t0 = tile_of(turret)
c.order.append(turret) if turret not in c.order else None
turret.ap = turret.max_ap
c._enemy_turret(turret)
ok(tile_of(turret) == t0, "турель стоит на месте")

# трус бежит
raider = make_enemy((0, 0), "raider")
raider.rect.topleft = rect_pos_for_tile(raider, tile_of(p))
raider.rect.x += 48
if g.level.is_wall(*tile_of(raider)):
    raider.rect.x -= 96
g.loc.enemies.append(raider)
c.order.append(raider)
raider.hp = 3
raider.ap = raider.max_ap
d0 = chebyshev(tile_of(raider), tile_of(p))
c._enemy_special(raider)
for _ in range(30):
    c.update(16)
ok(getattr(raider, "fleeing", False), "рейдер с малым HP бросается бежать")
c.end("тест")

# ================================================================ сохранение
p.add_rads(40)
g.save_game("2")
g2 = Game(intro=False)
g2.load_game("2")
fr(g2, 2)
ok(g2.player.rads == 40, "радиация сохраняется")
ok(g2.loc.id == "vault57" and g2.level.gates[0]["open"], "открытая гермодверь сохраняется")
ok(any(o.get("hidden") and P.info(o["name"]).get("explosive") for o in g2.level.objects), "взорванная бочка не возвращается")
ok(g2.inventory.has("самопал") and g2.stage("sq_vault") == 100, "квесты и награды сохраняются")

print("\nВСЁ ОК" if not failed else f"\nПРОВАЛЕНО: {len(failed)}")
sys.exit(1 if failed else 0)
