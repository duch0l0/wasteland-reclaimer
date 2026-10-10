"""
Смерть героя: герой лежит телом (а не стоит), выбитый спутник не встаёт и не бежит к нему.

    .venv/bin/python tests/test_death.py
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


from src.companion import make_ally  # noqa: E402

SHOTS = sys.argv[1] if len(sys.argv) > 1 else None
g = Game(intro=False)
g.enter_location("hub")
g.slides = None
for e in g.enemies:
    e.alive = False
fr(g)
g.ally = make_ally("punk")
t = tile_of(g.player)
g.ally.rect.topleft = rect_pos_for_tile(g.ally, (t[0] + 3, t[1]))
g.ally.down, g.ally.alive, g.ally.hp = True, False, 0        # выбит из боя
g.player.apply_damage(10 ** 6)
pos0 = g.ally.rect.topleft
for _ in range(120):
    g.update(16)
g.draw()
ok(g.game_over, "герой погиб — конец игры")
ok(g.ally.down and not g.ally.alive and g.ally.rect.topleft == pos0, "выбитый спутник лежит, не встаёт и не бежит")
if SHOTS:
    pygame.image.save(g.screen, os.path.join(SHOTS, "death.png"))

# живой спутник при смерти героя тоже не бегает за телом
g = Game(intro=False)
g.enter_location("hub")
g.slides = None
fr(g)
g.ally = make_ally("punk")
t = tile_of(g.player)
g.ally.rect.topleft = rect_pos_for_tile(g.ally, (t[0] + 4, t[1]))
g.player.apply_damage(10 ** 6)
pos0 = g.ally.rect.topleft
for _ in range(120):
    g.update(16)
ok(g.ally.rect.topleft == pos0, "живой спутник остаётся на месте")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
