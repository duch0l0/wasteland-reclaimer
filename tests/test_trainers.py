"""
Платные учителя (экономика): у десяти мастеров по три урока +5 к навыку; цена растёт (250 / 550 / 950),
второй урок — с 6 уровня, третий — с 10-го; без денег урока не видно; после третьего — «учить нечему».

    .venv/bin/python tests/test_trainers.py
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


def opts(g):
    return [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]


g = Game(intro=False)
g.enter_location("hub")
fr(g)
p = g.player
g.inventory.remove("крышки", g.inventory.count("крышки"))
talk(g, "arms_seller")
say(g, "Научишь стрелять")
ok(not any("урок" in l for l in opts(g)), "без крышек уроков не видно")
g.dialogue.close()

g.inventory.add("крышки", 5000)
was = p.skill("guns")
t0 = g.flags.get("time_min", 0)
talk(g, "arms_seller")
say(g, "Научишь стрелять")
say(g, "Первый урок")
ok(p.skill("guns") == was + 5, f"первый урок: стрельба {was} → {p.skill('guns')}")
ok(g.inventory.count("крышки") == 5000 - 250, "урок стоит 250")
ok(g.flags.get("time_min", 0) - t0 >= 360, "урок занимает полдня")
say(g, "Ещё урок")
ok(not any("Второй урок" in l for l in opts(g)), "второй урок закрыт до 6 уровня")
g.dialogue.close()

while p.level_sys.level < 10:
    p.level_sys.add_xp(1000)
    fr(g, 1)
talk(g, "arms_seller")
say(g, "Научишь стрелять")
ok(any("[Уровень 6+] Второй урок" in l for l in opts(g)), "второй урок помечен уровнем")
say(g, "Второй урок")
say(g, "Ещё урок")
say(g, "Третий урок")
ok(p.skill("guns") == was + 15, "три урока — +15")
ok(g.inventory.count("крышки") == 5000 - 250 - 550 - 950, "всего 1750 крышек")
ok(not any("Ещё урок" in l for l in opts(g)), "после третьего урока — больше нечего")
g.dialogue.close()
talk(g, "arms_seller")
say(g, "Научишь стрелять")
ok("нечему" in g.dialogue.current_node()["text"], "мастер: «учить нечему»")
g.dialogue.close()

import json  # noqa: E402
D = json.load(open("data/dialogues.json", encoding="utf-8"))
teach = {e["skill"] for t in D.values() for n in t["nodes"].values() for o in n["options"]
         for e in o.get("effects", []) if e.get("type") == "train"}
ok(len(teach) == 10, f"учителя есть у всех десяти навыков: {sorted(teach)}")

print("\nИТОГ:", "всё прошло" if not failed else f"провалено {len(failed)}")
sys.exit(1 if failed else 0)
