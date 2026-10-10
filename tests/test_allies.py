"""
Спутники: сами говорят о местах и поступках героя (один раз), уходят, если герой опустился ниже их порога,
и не возвращаются; разговор — история, мнение о герое по карме, личные темы (Коббс и Рид, Лира и брат).

    .venv/bin/python tests/test_allies.py
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




def ally_talk(g):
    g.dialogue.active_node = None
    g.player.rect.topleft = rect_pos_for_tile(g.player, (tile_of(g.ally)[0] - 1, tile_of(g.ally)[1]))
    g.handle_key(pygame.K_e)
    assert g.dialogue.is_active()


def wait_voice(g, ms=16000):
    for _ in range(ms // 16):
        g.update(16)
        while g.perk_choices:          # новый уровень — выбрать навык/перк, иначе окно держит игру
            g.handle_key(pygame.K_1)


def fresh(ally, lid="hub"):
    g = Game(intro=False)
    g.player.max_hp = g.player.hp = 10 ** 5
    g.enter_location(lid)
    g.slides = None
    for e in g.enemies:
        e.alive = False
    g.join_ally(ally)
    fr(g)
    return g


# ---- реплики о местах: один раз
g = fresh("lira")
g.enter_location("hub"); g.slides = None
wait_voice(g)
ok(g.flags.get("ally_said_lira_hub") and any("Разведчица у колодца" in l for l in g.log_lines), "Лира в Хабе: разведчица у колодца — наша")
n = sum("Разведчица у колодца" in l for l in g.log_lines)
g.enter_location("hub"); g.slides = None
wait_voice(g)
ok(sum("Разведчица у колодца" in l for l in g.log_lines) == n, "второй раз о Хабе не говорит")
g.enter_location("vault22_living"); g.slides = None
wait_voice(g)
ok(g.flags.get("ally_said_lira_vault"), "Убежище — по префиксу: «Vault-Tec строил клетки»")

# ---- отклик на поступок
g.flags["karl_home"] = True
wait_voice(g)
ok(any("Карл дома" in l for l in g.log_lines), "Лира отметила: Карл дома без единого выстрела")

# ---- разговор: история, мнение по карме, брат
ally_talk(g)
opts = [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]
ok("Расскажи о себе." in opts and opts.count("Что ты обо мне думаешь?") == 1, f"разговор с Лирой: {opts}")
say(g, "Расскажи")
ok(g.dialogue.active_node == "story0" and "Корвин" in g.dialogue.trees["ally_lira"]["nodes"]["story0"]["text"], "история Лиры: брат Корвин")
g.dialogue.active_node = None
g.inventory.add("жетон паладина Корвина", 1)
ally_talk(g); say(g, "Паладин Корвин"); say(g, "...")
ok(g.flags.get("lira_knows_corvin") and not g.inventory.has("жетон паладина Корвина"), "жетон брата — Лира узнала, какой приказ стоит брата")

# ---- уход: карма ниже порога
g.flags["karma"] = -200
wait_voice(g)
ok(g.ally is None and g.flags.get("lira_quit"), "карма −200 — Лира ушла")
g.join_ally("lira")
ok(g.ally is None, "второй раз не пойдёт")

# ---- Панк уходит за проданных детей, Коббс — никогда
g = fresh("punk")
g.flags["robes_sold"] = True
wait_voice(g)
ok(g.ally is None and g.flags.get("punk_quit"), "продал записку культу — Панк ушёл к Искре")

g = fresh("cobbs")
g.flags["karma"] = -500
g.flags["baker_done"] = True
wait_voice(g, 30000)
ok(g.ally is not None, "Коббс не уходит — у него приказ")
ally_talk(g); say(g, "Рид жив"); say(g, "Отведу")
ok(g.flags.get("cobbs_knows_reid"), "Коббс: «РИД — ЖИВ. Я — НЕ ОДИН»")

# ---- жетон Корвина лежит у чанов
g.enter_location("mariposa_vats"); g.slides = None
ok(any(c["name"] == "останки в силовой броне" and "жетон паладина Корвина" in c["loot"] for c in g.level.containers),
   "в Марипозе у чанов — пустая броня и жетон Корвина")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
