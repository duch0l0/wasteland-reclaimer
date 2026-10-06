"""
Спутники-люди (src/companion.ALLIES): позвать с собой, вместе войти в другую локацию, вместе драться,
сохраниться и загрузиться, отпустить домой — житель возвращается на своё место.

    .venv/bin/python tests/test_party.py
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
        if not g.level.is_wall(*c):
            g.player.rect.topleft = rect_pos_for_tile(g.player, c)
            break
    g.handle_key(pygame.K_e)
    assert g.dialogue.is_active(), nid


g = Game(intro=False)
g.player.max_hp = g.player.hp = 10 ** 6
g.flags.update({"cobbs_clear": True})
g.enter_location("necropolis_cobbs")
fr(g)
talk(g, "cobbs")
say(g, "Пойдёмте со мной")
ok(g.ally is not None and g.ally.name == "Капрал Коббс" and not any(n.npc_id == "cobbs" for n in g.npcs),
   "Коббс в отряде, из квартиры ушёл")

g.dialogue.active_node = None
g.enter_location("necropolis_under")
fr(g, 10)
ok(g.ally is not None and g.loc.id == "necropolis_under", "спутник входит в локацию вместе с героем")
d = max(abs(a - b) for a, b in zip(tile_of(g.ally), tile_of(g.player)))
ok(d <= 2, "спутник рядом с героем")

# бой: враги в канализации — спутник в очереди хода и стреляет
for e in g.enemies:
    e.hostile = True
target = g.enemies[0]
g.player.rect.topleft = rect_pos_for_tile(g.player, (tile_of(target)[0] - 3, tile_of(target)[1]))
from src import companion  # noqa: E402
companion.place_near_player(g)
g.combat.start(player_first=True)
ok(g.combat.active and g.ally in g.combat.order, "в бою спутник в очереди хода")
g.combat.active = False

# сохранение и загрузка
g.save_game("2")
g2 = Game(intro=False)
g2.load_game("2")
ok(g2.ally is not None and g2.ally.type_id == "cobbs", "спутник сохраняется и загружается")

# отпустить — Коббс снова дома
g.enter_location("necropolis")
fr(g)
g.dialogue.active_node = None
g.ally.rect.topleft = rect_pos_for_tile(g.ally, (tile_of(g.player)[0] + 1, tile_of(g.player)[1]))
g.handle_key(pygame.K_e)
ok(g.dialogue.is_active(), "со спутником можно поговорить")
say(g, "Подожди меня дома")
ok(g.ally is None, "спутник ушёл домой")
g.dialogue.active_node = None
g.enter_location("necropolis_cobbs")
fr(g)
ok(any(n.npc_id == "cobbs" for n in g.npcs), "Коббс снова в своей квартире")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
