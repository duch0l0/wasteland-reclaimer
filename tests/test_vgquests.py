"""
Вегас: «Лёгкие Шпоры» (вода Зайзикса как лекарство, наследник Сапогов), «Монета судьи» (свинец под орлом,
карман крупье Змей), «Человек, который сидит и играет» (напёрстки Матери-Змеи) — улики, навыки, связь с Джанктауном и Зайзиксом.

    .venv/bin/python tests/test_vgquests.py
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



def fresh(lid="vegas_boots"):
    g = Game(intro=False)
    g.player.max_hp = g.player.hp = 10 ** 5
    go(g, lid)
    return g


# ===================================================== Лёгкие Шпоры
g = fresh()
talk(g, "boots_rider_c"); say(g, "Что с Хэнком"); say(g, "вылечить"); say(g, "Схожу")
ok(g.stage("sq_hank") == 10, "Бетт: Хэнк кашляет кровью")
talk(g, "hank_spur")
opts = [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]
ok(not any("Кто поведёт" in o for o in opts), "наследника не назначить, пока Короны не решены")
g.dialogue.active_node = None
go(g, "vegas_palms")
talk(g, "palms_doctor"); say(g, "лёгкими"); say(g, "Спасибо")
ok(g.stage("sq_hank") == 50, "Ирен: хелатор в воде Зайзикса")
go(g, "junktown_clinic")
talk(g, "anna_shaw"); say(g, "Чудо-вода"); say(g, "Понятно")
ok(g.flags.get("know_zz_truth"), "Анна Шоу: лекарство для старика, проклятие для молодых")
g.inventory.add("вода Зайзикса", 2)
go(g, "vegas_boots")
talk(g, "hank_spur"); say(g, "Выпей"); say(g, "Бесплодие"); say(g, "...")
ok(g.flags.get("hank_cured") and g.inventory.has("пыльник Шпоры") and g.stage("sq_hank") == 100, "Хэнк дышит — пыльник Шпоры герою")

g = fresh()
talk(g, "boots_rider_c"); say(g, "Что с Хэнком"); say(g, "вылечить"); say(g, "Схожу")
g.flags["boots_member"] = True
talk(g, "hank_spur"); say(g, "Кто поведёт"); say(g, "Бетт"); say(g, "...")
go(g, "vegas_boots")
ok(g.flags.get("hank_heir_bett") and not any(n.npc_id == "hank_spur" for n in g.npcs), "Хэнк умер, шпоры у Бетт")

# ---- «Лёгкие Шпоры»: второй путь без фракции — две бутыли у Абдула (60 крышек)
g = fresh()
g.player.skills["speech"] = 20
talk(g, "boots_rider_c"); say(g, "Что с Хэнком"); say(g, "вылечить"); say(g, "Схожу")
go(g, "vegas_palms")
talk(g, "palms_doctor"); say(g, "лёгкими"); say(g, "Спасибо")
ok(g.flags.get("know_hank_zz"), "Ирен: хелатор в воде Зайзикса, две бутыли")
go(g, "zzyzx")
g.inventory.add("крышки", 100)
c0 = g.inventory.count("крышки")
g.open_trade("merchant_zz")
while not g.inventory.has("вода Зайзикса", 2):
    row = next(r for r in g.trade_rows() if r[0] == "вода Зайзикса")
    g._buy(*row[:3])
g.trade = None
ok(g.inventory.has("вода Зайзикса", 2) and c0 - g.inventory.count("крышки") >= 60,
   "Абдул: две бутыли — шестьдесят (дороже без Красноречия)")
go(g, "vegas_boots")
talk(g, "hank_spur"); say(g, "Выпей"); say(g, "Бесплодие"); say(g, "...")
ok(g.flags.get("hank_cured") and g.stage("sq_hank") == 100, "лекарство вместо Короны — «Лёгкие Шпоры» закрыты")

# ---- «Лёгкие Шпоры»: наследника можно назвать по подкове, без вступления в Корону
g = fresh()
talk(g, "boots_rider_c"); say(g, "Что с Хэнком"); say(g, "вылечить"); say(g, "Схожу")
g.inventory.add("подкова Шпоры", 1)
talk(g, "hank_spur"); say(g, "Вот твоя подкова"); say(g, "Слушаю"); say(g, "Принесу")
ok(g.flags.get("boots_job1") and not g.flags.get("boots_member"), "Хэнк принял подкову — герой не Сапог")
talk(g, "hank_spur"); say(g, "Кто поведёт"); say(g, "Ред"); say(g, "...")
ok(g.flags.get("hank_heir_red") and g.stage("sq_hank") == 100, "наследник назван по подкове — квест закрыт без фракции")

# ===================================================== Монета судьи
g = fresh("vegas_strip")
talk(g, "strip_kid"); say(g, "главный"); say(g, "всегда прав"); say(g, "Проверю")
ok(g.stage("sq_coin") == 10, "Тим: семь решек подряд")
talk(g, "judge_sol"); say(g, "монету"); say(g, "десять раз"); say(g, "..."); say(g, "Верну")
ok(g.stage("sq_coin") == 50 and g.inventory.has("фальшивая монета"), "десять решек — монета фальшивая")
ok("монета судьи Сола" in g.pocket("den_dealer"), "настоящая — в кармане крупье Змей")
go(g, "vegas_den")
g.player.skills["speech"] = 70
talk(g, "den_dealer"); say(g, "Монета судьи"); say(g, "Красноречие"); say(g, "...")
ok(g.inventory.has("монета судьи Сола") and "монета судьи Сола" not in g.pocket("den_dealer"), "крупье отдал монету")
go(g, "vegas_strip")
talk(g, "judge_sol"); say(g, "Настоящая"); say(g, "...")
ok(g.flags.get("coin_returned") and g.stage("sq_coin") == 100, "семь приговоров пересужены")

g = fresh("vegas_strip")
g.flags["dice_exposed"] = True
talk(g, "strip_kid"); say(g, "главный"); say(g, "всегда прав"); say(g, "Проверю")
talk(g, "judge_sol"); say(g, "монету"); say(g, "кости Гизмо"); say(g, "Верну")
go(g, "vegas_den")
talk(g, "mother_snake"); say(g, "Судья знает"); say(g, "По рукам")
ok(g.flags.get("coin_sold") and g.karma < 0, "опыт с костями Гизмо помог — но тайну продал Змеям")

# ---- «Монета судьи»: второй путь без денег и без Красноречия — услуга Матери-Змее
g = fresh("vegas_strip")
g.player.skills["speech"] = 20
talk(g, "strip_kid"); say(g, "главный"); say(g, "всегда прав"); say(g, "Проверю")
talk(g, "judge_sol"); say(g, "монету"); say(g, "десять раз"); say(g, "..."); say(g, "Верну")
go(g, "vegas_den")
talk(g, "mother_snake"); say(g, "Монета у твоего крупье"); say(g, "Проведу")
ok(g.inventory.has("монета судьи Сола") and g.flags.get("coin_from_mother") and g.flags.get("snakes_job1_taken")
   and not g.inventory.has("фальшивая монета"), "монета вернулась за услугу — долг Змеям, не двести крышек")
g.dialogue.active_node = None
talk(g, "mother_snake")
ok(not any("Судья знает" in g.dialogue.option_label(o) for o in g.dialogue.visible_options()),
   "фальшивки нет — и продать её Матери больше нельзя")
g.dialogue.active_node = None
go(g, "vegas_strip")
talk(g, "judge_sol"); say(g, "Настоящая"); say(g, "...")
ok(g.stage("sq_coin") == 100 and g.flags.get("coin_returned"), "второй путь закрыл «Монету» без навыка и без крышек")

# ===================================================== Мило
g = fresh("vegas_snakes")
talk(g, "snake_gambler"); say(g, "выиграть"); say(g, "Сколько"); say(g, "придумаю")
ok(g.stage("sq_milo") == 10, "Мило — товар на пятничном аукционе")
go(g, "vegas_den")
g.inventory.add("крышки", 200)
talk(g, "mother_snake"); say(g, "Долг Мило"); say(g, "Левый"); say(g, "...")
ok(not g.flags.get("milo_free") and g.inventory.count("крышки") < 200, "угадывал стакан — проиграл двести")
talk(g, "mother_snake"); say(g, "Долг Мило"); say(g, "перстнем"); say(g, "...")
ok(g.flags.get("milo_free") and g.stage("sq_milo") == 100, "шарик под перстнем с изумрудом — Мило свободен")
go(g, "vegas_snakes")
talk(g, "snake_gambler")
ok(g.dialogue.active_node == "ml_free", "Мило больше не играет — смотрит")

g = fresh("vegas_snakes")
talk(g, "snake_gambler"); say(g, "выиграть"); say(g, "Сколько"); say(g, "придумаю")
go(g, "vegas_boots")
talk(g, "boots_rider_b"); say(g, "Сапоги возьмут"); say(g, "...")
go(g, "vegas_snakes")
ok(g.flags.get("milo_boots") and not any(n.npc_id == "snake_gambler" for n in g.npcs), "Мило ушёл к Сапогам")

g = fresh("vegas_snakes")
g.flags["gambler_eaten"] = True
go(g, "vegas_snakes")
ok(not any(n.npc_id == "snake_gambler" for n in g.npcs), "отданного Ладоням игрока больше нет на месте")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
