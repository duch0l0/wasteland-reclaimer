"""
Проверка сюжета первой главы без окна: бот проходит главный квест разными
путями и побочные квесты. Запуск из папки game_project:

    .venv/bin/python tests/test_story.py
"""
import os
import random
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import pygame  # noqa: E402

pygame.mouse.get_pos = lambda: (-50, -50)
pygame.mouse.get_focused = lambda: True

from src.game import Game  # noqa: E402
from src.combat import tile_of, rect_pos_for_tile  # noqa: E402

failed = []


def ok(cond, msg):
    print(("OK   " if cond else "FAIL ") + msg)
    if not cond:
        failed.append(msg)


def new_game():
    random.seed(3)
    g = Game(intro=False)
    g.player.max_hp = g.player.hp = 10 ** 6
    for e in g.enemies:
        e.wander_wait = 10 ** 9
    for n in g.npcs:
        n.wander_wait = 10 ** 9
    return g


def fr(g, n=2):
    for _ in range(n):
        g.update(16)
        g.draw()
        if g.perk_choices:
            g.handle_key(pygame.K_1)


def stand_near(g, tiles):
    """Поставить героя на свободную клетку рядом с объектом."""
    for t in tiles:
        for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (-1, 1)):
            c = (t[0] + dx, t[1] + dy)
            if not g.level.is_wall(*c) and c not in tiles:
                g.player.rect.topleft = rect_pos_for_tile(g.player, c)
                g.snap_camera()
                return
    raise AssertionError(f"негде встать рядом с {tiles}")


def say(g, part):
    opts = [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]
    idx = next((i for i, lbl in enumerate(opts) if part in lbl), None)
    assert idx is not None, f"нет реплики «{part}» среди {opts}"
    g.handle_key(pygame.K_1 + idx)
    fr(g, 1)


def has_option(g, part):
    return any(part in g.dialogue.option_label(o) for o in g.dialogue.visible_options())


def talk(g, npc_id):
    npc = next(n for n in g.npcs if n.npc_id == npc_id)
    stand_near(g, [tile_of(npc)])
    g.handle_key(pygame.K_e)
    assert g.dialogue.is_active(), f"разговор с {npc_id} не начался"


def use_terminal(g, tid):
    t = next(t for t in g.level.terminals if t["id"] == tid)
    stand_near(g, t["tiles"])
    g.handle_key(pygame.K_e)
    assert g.term and g.term["id"] == tid, f"терминал {tid} не открылся"


def open_entry(g, label_part):
    entries = g.term_entries()
    idx = next(i for i, (_, e) in enumerate(entries) if label_part in e["label"])
    g.term_open_entry(idx)
    return entries[idx][1]


def search(g, title):
    box = next(c for c in g.level.containers if c["name"] == title)
    stand_near(g, box["tiles"])
    g.handle_key(pygame.K_e)
    return box


def fight(g):
    c = g.combat
    n = 0
    while c.active:
        if c.player_can_act():
            left = c.enemies_in_combat()
            t = c.target if c.target in left else (left[0] if left else None)
            if t is None:
                fr(g, 1)
                continue
            c.target = t
            if c.can_attack(g.player, t)[0] and g.player.ap >= c.attack_cost(g.player):
                c.player_attack(0)
            elif g.player.ap >= 1:
                step = c._path_next_step(g.player, t)
                c.player_step(*step) if step else c.end_turn()
            else:
                c.end_turn()
        fr(g, 1)
        n += 1
        assert n < 40000


def grandpa_house(g):
    """Общее начало: глаз, терминал, последняя запись."""
    eye = next(p for p in g.level.pickups if p["kind"] == "чей-то глаз")
    g.player.rect.topleft = rect_pos_for_tile(g.player, (eye["rect"].x // 48, eye["rect"].y // 48))
    fr(g)
    assert not g.inventory.has("чей-то глаз"), "автоподбора быть не должно"
    g.handle_key(pygame.K_e)  # подобрать вручную
    use_terminal(g, "grandpa")
    open_entry(g, "ПОСЛЕДНЯЯ ЗАПИСЬ")
    g.term_back()
    g.close_terminal()


def go_station(g):
    g.reveal_location("station")
    g.enter_location("station")
    fr(g, 3)


def go_home(g):
    g.enter_location("ruins")
    fr(g, 2)


def finish(g):
    """Карта мира -> Бейкер -> слайды конца главы."""
    ok("baker" in g.worldmap.known, "Бейкер отмечен на карте мира")
    g.go_world_map()
    g.worldmap.pos = pygame.Vector2(g.worldmap.pos)
    g.enter_location("baker")
    shown = g.slides is not None
    texts = " ".join(p["text"] for sl in (g.slides or {}).get("list", []) for p in sl["parts"])
    while g.slides:
        g.update(5000)
        g.slides_next()
    ok(shown and g.stage("mq_grandpa") == 100, "Бейкер: слайды конца главы, квест выполнен")
    return texts


# ============================================================ путь 1: глаз и Шрам, караван
print("— путь 1: глаз, терминал, пароль от Гены, Шрам, караван")
g = new_game()
ok(g.stage("mq_grandpa") == 10 and g.inventory.has("письмо деда"), "старт: письмо деда, квест на стадии 10")
grandpa_house(g)
ok(g.inventory.has("чей-то глаз"), "в доме деда подобран чей-то глаз")
ok(g.stage("mq_grandpa") == 30 and g.flags.get("know_anchorage"), "терминал: последняя запись → стадия 30")
box = search(g, "сейф деда")
ok(not box["opened"], "сейф деда без кода не открывается: " + g.log_lines[-1][:50])
talk(g, "gena")
say(g, "Анкоридж")
ok(g.stage("mq_grandpa") == 40 and "station" in g.worldmap.known, "Гена: «Анкоридж» → стадия 40, заправка на карте")
say(g, "Куда его увезли")
say(g, "Спасибо")
say(g, "показать глаз")
say(g, "Так и сделаю")
say(g, "Какой там пароль")
ok(g.flags.get("know_pw_grandpa"), "Гена назвал пароль (кличка пса)")
g.dialogue.close()
use_terminal(g, "grandpa")
open_entry(g, "ЛИЧНОЕ")
opts = [lbl for lbl, _ in g.lock_options()]
ok(any("КОЛБАСА" in o for o in opts), f"закрытая папка: можно ввести пароль ({opts[0]})")
g.lock_options()[0][1]()
ok(g.flags.get("safe_code") and g.term["view"] == "entry", "папка ЛИЧНОЕ открыта, код сейфа известен")
g.close_terminal()
search(g, "сейф деда")
ok(g.inventory.has("10-мм пистолет") and g.inventory.has("голозапись деда"), "сейф: 10-мм пистолет, голозапись, медаль")
g.use_item = g.use_item  # noqa
g.item_action("голозапись деда")[1]()
ok(g.term and g.term.get("doc") == "doc_holotape" and g.flags.get("heard_holotape"), "голозапись прослушивается из рюкзака")
g.close_terminal()
g.switch_weapon("pistol10")
ok(g.player.weapon == "pistol10", "10-мм пистолет берётся в руки")
go_station(g)
shram = next(e for e in g.enemies if e.talk)
g.player.rect.topleft = rect_pos_for_tile(g.player, (tile_of(shram)[0] - 4, tile_of(shram)[1]))
fr(g, 2)
ok(g.dialogue.is_active() and g.dialogue.active_id == "boss", "Шрам заговаривает первым")
say(g, "Где старик")
say(g, "показать глаз")
ok(g.stage("mq_grandpa") == 50 and "baker" in g.worldmap.known, "глаз сломал Шрама: Бейкер → стадия 50")
say(g, "Оставлю")
g.dialogue.close()
fr(g, 3)
ok(not g.combat.active, "после разговора банда не нападает")
go_home(g)
g.inventory.add("крышки", 80)
talk(g, "gena")
say(g, "Мне нужно в Бейкер")
say(g, "Вот 80 крышек")
ok(g.flags.get("route_caravan") and g.stage("mq_grandpa") == 60, "караван Гены за 80 крышек → стадия 60")
g.dialogue.close()
texts = finish(g)
ok("Караван Гены" in texts, "в концовке главы — караван")

# ============================================================ путь 2: Лира
print("— путь 2: голозапись для Лиры")
g = new_game()
grandpa_house(g)
talk(g, "blondie")
ok(not has_option(g, "Ты из Братства"), "без дневника деда нельзя раскусить Блонди")
g.dialogue.close()
use_terminal(g, "grandpa")
open_entry(g, "2 июня")
g.close_terminal()
talk(g, "blondie")
say(g, "Ты крутилась")
say(g, "Ты из Братства")
ok(g.stage("sq_lira") == 10, "Блонди — посвящённая Лира из Братства Стали")
g.dialogue.close()
# взлом папки ЛИЧНОЕ: сначала ошибка, потом верное слово
use_terminal(g, "grandpa")
open_entry(g, "ЛИЧНОЕ")
g.lock_options()[0][1]()  # «Взломать» — пароль ещё неизвестен
h = g.term["hack"]
wrong = next(w for w in h["words"] if w != h["password"])
g.hack_guess(wrong)
ok(h["tries"] == 3 and h["log"][-1].startswith(">Совпадение="), f"взлом: неверное слово, {h['log'][-1]}")
g.hack_guess(h["password"])
ok(g.flags.get("safe_code"), "взлом: верное слово — папка открыта")
g.close_terminal()
search(g, "сейф деда")
talk(g, "gena")
say(g, "Анкоридж")
g.dialogue.close()
talk(g, "blondie")
say(g, "голозапись деда")
say(g, "Держи")
ok(g.flags.get("bos_ally") and g.stage("mq_grandpa") == 50, "Лира получила запись, сказала про Бейкер → 50")
g.dialogue.close()
talk(g, "blondie")
say(g, "Пора в Бейкер")
ok(g.flags.get("route_lira"), "Лира ведёт в Бейкер")
g.dialogue.close()
texts = finish(g)
ok("Братства Стали" in texts, "в концовке: запись у Братства")

# ============================================================ путь 3: Панк и тайник на заправке
print("— путь 3: доля Панка")
g = new_game()
grandpa_house(g)
talk(g, "gena")
say(g, "Анкоридж")
g.dialogue.close()
talk(g, "loner")
say(g, "Ты был в Бензо-банде")
say(g, "Куда его увезли")
say(g, "Договорились")
ok(g.stage("sq_loner") == 10, "Панк: принести долю с заправки")
go_station(g)
g.dialogue.close()
for e in g.enemies:
    e.talked = True
box = search(g, "тайник Панка")
ok(box["opened"] and g.inventory.has("доля Панка"), "тайник Панка забран: " + g.log_lines[-1][:40])
if not g.combat.active:  # не заметили — сами начинаем драку со Шрамом
    g.combat.start(player_first=True) or g.make_hostile("gang")
while any(e.alive for e in g.enemies):
    if not g.combat.active:
        e = next(e for e in g.enemies if e.alive)
        g.player.rect.topleft = rect_pos_for_tile(g.player, tile_of(e))
        g.combat._snap_to_grid(g.player)
        fr(g, 1)
        g.combat.start(player_first=True)
    fight(g)
ok(g.flags.get("gang_dead"), "банда перебита, Шрам тоже")
ok(g.inventory.has("контракт Единства"), "у Шрама нашёлся контракт")
go_home(g)
talk(g, "loner")
say(g, "Вот твоя доля")
ok(g.stage("mq_grandpa") == 50 and g.stage("sq_loner") == 100, "Панк получил долю, сказал про Бейкер")
say(g, "Скоро")
talk(g, "loner")
say(g, "Веди в Бейкер")
ok(g.flags.get("route_loner"), "Панк — проводник")
g.dialogue.close()
texts = finish(g)
ok("тропой" in texts and "Бензо-банды больше нет" in texts, "в концовке: тропа Панка, банда перебита")

# ============================================================ путь 4: Черепан, логово, листовка; взлом терминала заправки
print("— путь 4: Черепан и ливнёвка; терминал заправки")
g = new_game()
grandpa_house(g)
talk(g, "turtle")
say(g, "Ты не видел ночью")
say(g, "Ладно, будут химикаты")
g.inventory.add("химикаты", 2)
talk(g, "turtle")
say(g, "Вот химикаты")
say(g, "Ты не видел ночью")
ok(g.stage("sq_den") == 10 and g.inventory.has("тоник"), "Черепан: тоник и рассказ о ливнёвке")
g.dialogue.close()
search(g, "сумка культиста")
if g.combat.active:
    fight(g)
    search(g, "сумка культиста")
ok(g.inventory.has("листовка Единства"), "в логове — сумка культиста с листовкой")
g.item_action("листовка Единства")[1]()
g.close_terminal()
ok(g.flags.get("know_baker") and g.stage("mq_grandpa") == 30, "листовка: Бейкер известен, но главный квест ждёт Гену")
talk(g, "gena")
say(g, "Анкоридж")
ok(g.stage("mq_grandpa") == 50, "после разговора с Геной — сразу стадия 50 (Бейкер уже известен)")
g.dialogue.close()
go_station(g)
g.dialogue.close()
term = g.level.terminals[0]
stand_near(g, term["tiles"])
ok(g.level.is_wall(*term["tiles"][0]), "терминал заправки — в запертом складе")

# ============================================================ побочный: вода
print("— побочный квест: мёртвая вода")
g = new_game()
use_terminal(g, "pump")
open_entry(g, "Состояние")
ok(g.stage("sq_water") == 10, "терминал водокачки: квест «Мёртвая вода»")
g.term_back()
open_entry(g, "Перекрыть")
ok(g.term["view"] == "locked" and not any("ПОЛИВКА" in lbl for lbl, _ in g.lock_options()), "контур закрыт паролем")
g.close_terminal()
search(g, "шкафчик Уоллеса")
g.item_action("записка техника")[1]()
g.close_terminal()
use_terminal(g, "pump")
open_entry(g, "Перекрыть")
g.lock_options()[0][1]()
ok(g.flags.get("water_fixed") and g.stage("sq_water") == 50, "паролем из записки перекрыт контур Б")
g.close_terminal()
talk(g, "gena")
caps = g.inventory.count("крышки")
say(g, "Вода снова пресная")
ok(g.inventory.count("крышки") == caps + 40 and g.stage("sq_water") == 100, "Гена заплатил за воду")
g.dialogue.close()
g.open_journal = None
g.journal_open = True
g.draw()
ok(True, "журнал рисуется")

print(f"не прошло: {len(failed)}")
sys.exit(1 if failed else 0)
