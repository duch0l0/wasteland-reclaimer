"""
Бейкер без окна: три пути спасения деда и финал главы на складе «Бейкер-7».

  Тень   — с Панком: калитка ломом, Искра даёт ключ, дед уходит тихо; Искра уходит к брату.
  Сделка — Хэтти ручается, страж пропускает, Ансельм отпускает деда за голозапись.
  Сталь  — с Лирой: штурм, бой, Ансельм отдаёт ключ.
  Ещё: тревога во дворе без пропуска; Тобиас и самогон; дед открывает склад, журнал —
  слайды финала, жетон и допуск; сохранение посреди Бейкера.

    .venv/bin/python tests/test_baker.py
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
from src.combat import tile_of, rect_pos_for_tile  # noqa: E402

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


def goto(g, tile):
    g.player.rect.topleft = rect_pos_for_tile(g.player, tile)
    g.snap_camera()


def stand_near(g, tiles):
    for t in tiles:
        for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (-1, 1), (0, 2)):
            c = (t[0] + dx, t[1] + dy)
            if not g.level.is_wall(*c) and c not in tiles:
                goto(g, c)
                return
    raise AssertionError(f"негде встать рядом с {tiles}")


def options(g):
    return [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]


def say(g, part):
    opts = options(g)
    idx = next((i for i, lbl in enumerate(opts) if part in lbl), None)
    assert idx is not None, f"нет реплики «{part}» среди {opts}"
    g.handle_key(pygame.K_1 + idx)
    fr(g, 1)


def talk(g, npc_id):
    end_talk(g)
    npc = next(n for n in g.npcs if n.npc_id == npc_id)
    stand_near(g, [tile_of(npc)])
    g.handle_key(pygame.K_e)
    assert g.dialogue.is_active(), f"разговор с {npc_id} не начался"


def talk_enemy(g, enemy):
    """Мирный враг с диалогом (страж культа)."""
    stand_near(g, [tile_of(enemy)])
    enemy.talked = True    # сам он уже не заговорит — заговорили мы
    g.talk_to(enemy, enemy.talk)
    assert g.dialogue.is_active()


def end_talk(g):
    if g.dialogue.is_active():
        g.dialogue.active_node = None   # просто отойти от собеседника
        fr(g, 1)


def use_gate(g, flag):
    gate = next(gt for gt in g.level.gates if gt["flag"] == flag)
    stand_near(g, gate["tiles"])
    g.use_gate(gate)
    return gate["open"]


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
        assert n < 60000


def arrive(flags=()):
    random.seed(4)
    g = Game(intro=False)
    g.player.max_hp = g.player.hp = 10 ** 6
    g.player.base_damage = 40
    for f in flags:
        g.flags[f] = True
    g.set_stage("mq_grandpa", 60)
    g.enter_location("baker")
    shown = g.slides is not None and g.slides["id"] == "baker_arrival"
    while g.slides:
        g.update(5000)
        g.slides_next()
    for e in g.enemies:
        e.wander_wait = 10 ** 9
    for n in g.npcs:
        n.wander_wait = 10 ** 9
    fr(g)
    ok(shown and g.loc.id == "baker" and g.stage("mq_grandpa") == 70, f"Бейкер: слайды прибытия, стадия 70 {flags}")
    return g


def finale(g, path):
    """Дед у склада -> склад -> журнал -> слайды финала."""
    ok(g.flags.get(f"baker_path_{path}") and g.stage("mq_grandpa") == 80, f"дед свободен, путь — {path}")
    ok(any(n.npc_id == "amos_b7" for n in g.npcs) and not any(n.npc_id == "amos" for n in g.npcs),
       "дед ушёл из кельи к складу")
    goto(g, (72, 15))
    fr(g, 2)
    ok(g.loc.id == "baker", "без деда дверь склада не открыть")
    talk(g, "amos_b7")
    say(g, "Открывай")
    say(g, "Идём вниз")
    end_talk(g)
    ok(g.flags.get("baker7_open") and g.stage("mq_grandpa") == 90, "дед открыл склад: глаз, голос, код")
    goto(g, (72, 14))
    fr(g, 3)
    ok(g.loc.id == "baker7", "спуск в «Бейкер-7»")
    for e in g.enemies:
        e.alive = False
    sealed = next(c for c in g.level.containers if c["name"] == "контейнер ВРЭ")
    ok(sealed.get("requires") is not None, "контейнеры ВРЭ опломбированы")
    t = next(t for t in g.level.terminals if t["id"] == "baker7_log")
    stand_near(g, t["tiles"])
    g.handle_key(pygame.K_e)
    entries = g.term_entries()
    g.term_open_entry(next(i for i, (_, e) in enumerate(entries) if "Журнал" in e["label"]))
    g.term_back()
    entries = g.term_entries()
    g.term_open_entry(next(i for i, (_, e) in enumerate(entries) if "Подняться" in e["label"]))
    g.close_terminal()
    shown = g.slides is not None and g.slides["id"] == "baker_finale"
    text = " ".join(p["text"] for sl in (g.slides or {}).get("list", []) for p in sl["parts"])
    while g.slides:
        g.update(5000)
        g.slides_next()
    ok(shown and g.stage("mq_grandpa") == 100 and g.flags.get("baker_done"), "журнал отгрузки — финал главы")
    ok(g.inventory.has("жетон Эймоса") and g.inventory.has("допуск Марипозы"), "дед отдал жетон и допуск")
    return text


# ============================================================ тревога: чужак во дворе
print("— тревога во дворе миссии")
g = arrive()
ok(use_gate(g, "mission_back_open"), "калитка в дюнах — ломом")
goto(g, (36, 22))     # прямо к стражу у ворот
fr(g, 2)
ok(g.flags.get("baker_alarm") and g.flags.get("cult_hostile") and g.combat.active, "без пропуска во дворе — тревога и бой")

# ============================================================ путь 1: Тень
print("— Тень: Панк, Искра, ключ, тихо")
g = arrive(["route_loner"])
ok(any(n.npc_id == "loner_baker" for n in g.npcs), "Панк ждёт у калитки")
talk(g, "loner_baker")
say(g, "Скажу")
ok(g.flags.get("know_iskra") and g.stage("sq_iskra") == 10, "Панк просит найти Искру")
ok(use_gate(g, "mission_back_open"), "калитка открыта")
goto(g, (55, 12))     # вдоль восточной стены — вдали от стражи
fr(g, 2)
ok(not g.flags.get("baker_alarm"), "у восточной стены не заметили")
talk(g, "iskra")
say(g, "Мне нужен ключ")
say(g, "Спасибо")
ok(g.inventory.has("ключ от келий"), "Искра отдала слепок ключа")
say(g, "Он ждёт тебя")
fr(g, 2)
ok(g.flags.get("iskra_free") and g.stage("sq_iskra") == 100 and not any(n.npc_id == "iskra" for n in g.npcs),
   "Искра ушла к брату")
ok(use_gate(g, "cells_open"), "решётка кельи — ключом")
fr(g, 2)
ok(not g.flags.get("baker_alarm"), "тихо")
talk(g, "amos")
say(g, "Иди")
fr(g, 2)
text = finale(g, "shadow")
ok("вентиляционную шахту" in text and "глаз в треугольнике" in text, "финал Тени: культ по следам, Орден заметил")

# ============================================================ путь 2: Сделка
print("— Сделка: Хэтти, страж, Ансельм")
g = arrive(["safe_code"])
g.inventory.add("голозапись деда", 1)
talk(g, "hattie")
say(g, "Я ищу деда")
say(g, "Город мне поможет")
say(g, "Скажи стражу")
end_talk(g)
guard = next(e for e in g.enemies if e.type_id == "cult_guard" and tile_of(e)[1] < 30)
talk_enemy(g, guard)
say(g, "прислала Хэтти")
say(g, "Свет с тобой")
fr(g, 2)
ok(g.flags.get("mission_pass") and next(gt for gt in g.level.gates if gt["flag"] == "mission_gate_open")["open"],
   "страж пропустил — ворота открыты")
talk(g, "anselm")
say(g, "держишь моего деда")
ok(any("10-23-77" in o for o in options(g)), "можно выменять деда на код склада")
say(g, "его голос на записи")
say(g, "Договорились")
fr(g, 2)
ok(g.flags.get("cells_open") and g.flags.get("deal_anselm"), "Ансельм отпустил деда")
goto(g, (49, 15))
fr(g, 2)
ok(not g.flags.get("baker_alarm"), "с пропуском по двору можно ходить")
talk(g, "amos")
say(g, "Иди")
fr(g, 2)
text = finale(g, "deal")
ok("Холлиса увезли" in text or "люди Холлиса" in text, "финал Сделки: Ансельм нарушает слово, Холлис забирает ящики")

# ============================================================ путь 3: Сталь
print("— Сталь: Лира и штурм")
g = arrive(["route_lira"])
talk(g, "lira_baker")
say(g, "Штурмуем")
ok(g.flags.get("baker_assault") and g.flags.get("cult_hostile"), "штурм начат, культ враждебен")
alive_before = sum(e.alive for e in g.enemies if e.faction == "cult")
ok(alive_before < 5, f"паладины сняли часть охраны (осталось {alive_before} из 5)")
fight(g)
in_mission = [e for e in g.enemies if e.faction == "cult" and tile_of(e)[1] < 25]
for _ in range(6):      # во двор: оставшиеся балахоны замечают и вступают в бой
    left = [e for e in in_mission if e.alive]
    if not left:
        break
    stand_near(g, [tile_of(left[0])])
    fr(g, 3)
    fight(g)
ok(not any(e.alive for e in in_mission), "охрана миссии перебита")
talk(g, "anselm")
say(g, "Ключ от келий")
say(g, "Иди")
fr(g, 2)
ok(g.inventory.has("ключ от келий") and not any(n.npc_id == "anselm" for n in g.npcs), "Ансельм отдал ключ и ушёл")
ok(use_gate(g, "cells_open"), "келья открыта")
talk(g, "amos")
say(g, "Иди")
fr(g, 2)
text = finale(g, "steel")
ok("паладина" in text, "финал Стали: Братство запомнило")

# ============================================================ Тобиас и самогон
print("— Тобиас")
g = arrive()
g.inventory.add("крышки", 20)
talk(g, "nick")
say(g, "Самогон")
say(g, "За них")
end_talk(g)
talk(g, "tobias")
say(g, "Ты ключник")
say(g, "Угощаю")
say(g, "Тихо поднять")
ok(g.inventory.has("ключ от келий") and not g.inventory.has("самогон"), "Тобиас уронил ключ")

# ============================================================ сохранение
print("— сохранение в Бейкере")
g = arrive(["route_loner"])
talk(g, "loner_baker")
say(g, "Скажу")
g.save_game("1")
g2 = Game(intro=False)
g2.load_game("1")
fr(g2, 2)
ok(g2.loc.id == "baker" and any(n.npc_id == "loner_baker" for n in g2.npcs) and g2.flags.get("know_iskra"),
   "после загрузки Панк на месте, флаги целы")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
