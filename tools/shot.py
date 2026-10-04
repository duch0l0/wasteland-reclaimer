"""
Снимки локаций без окна — проверить, как выглядит карта.

  .venv/bin/python tools/shot.py <папка> <локация>:<x>:<y> [<локация>:<x>:<y> …]

Герой ставится в клетку (x, y), враги замирают, через полсекунды игры снимается экран:
<папка>/z_<локация>_<x>_<y>.png.
"""
import os
import sys
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import pygame  # noqa: E402

pygame.mouse.get_pos = lambda: (-50, -50)
pygame.mouse.get_focused = lambda: True

from src.game import Game, saveload  # noqa: E402
from src.combat import rect_pos_for_tile  # noqa: E402


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    saveload.SAVE_DIR = tempfile.mkdtemp()
    g = Game(intro=False)
    g.player.max_hp = g.player.hp = 10 ** 6
    for spec in sys.argv[2:]:
        loc, x, y = spec.split(":")
        g.enter_location(loc)
        while g.slides:
            g.update(5000)
            g.slides_next()
        for e in g.enemies:
            e.wander_wait = 10 ** 9
            e.hostile = False
        g.dialogue.active_node = None
        g.player.rect.topleft = rect_pos_for_tile(g.player, (int(x), int(y)))
        g.snap_camera()
        for _ in range(30):
            g.update(16)
            g.combat.active = False
        g.dialogue.active_node = None
        g.draw()
        path = os.path.join(out, f"z_{loc}_{x}_{y}.png")
        pygame.image.save(g.screen, path)
        print(path)


if __name__ == "__main__":
    main()
