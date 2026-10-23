"""
Чистый снимок участка карты в игре — для приёмки расстановки «глазами» (docs/furnish/logic.md):
герой в центре участка, крыша дотаяла, масштаб подобран так, чтобы участок влез в кадр.

  .venv/bin/python tools/area_shot.py <папка> <локация> <имя>=<x0>,<y0>,<x1>,<y1> […]
  .venv/bin/python tools/area_shot.py /tmp/shots ruins sheriff=20,55,37,67 saloon=50,24,71,37
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
from src import settings as S  # noqa: E402
from src.ui.common import PANEL_H  # noqa: E402


def main():
    out, loc, specs = sys.argv[1], sys.argv[2], sys.argv[3:]
    os.makedirs(out, exist_ok=True)
    saveload.SAVE_DIR = tempfile.mkdtemp()
    g = Game(intro=False)
    g.player.max_hp = g.player.hp = 10 ** 6
    g.enter_location(loc)
    while g.slides:
        g.update(5000)
        g.slides_next()
    for e in g.enemies:                 # снимаем, а не воюем
        e.hostile = False
    view_w, view_h = S.SCREEN_W / S.TILE, (S.SCREEN_H - PANEL_H) / S.TILE
    for spec in specs:
        name, rect = spec.split("=")
        x0, y0, x1, y1 = map(int, rect.split(","))
        g.zoom = max(0.5, min(1.6, view_w / (x1 - x0 + 3), view_h / (y1 - y0 + 3)))
        g.apply_view()
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        g.player.rect.topleft = rect_pos_for_tile(g.player, (cx, cy))
        g.snap_camera()
        roof = g.level.roof_over((cx, cy)) if hasattr(g.level, "roof_over") else None
        for _ in range(60):              # крыша тает ~0.2 с: снимать, когда её уже нет
            g.update(16)
            g.combat.active = False
            g.dialogue.close()
            g.speech = None
            if roof is None or roof["alpha"] <= 0.0:
                break
        g.draw()
        path = os.path.join(out, f"{name}.png")
        pygame.image.save(g.screen, path)
        print(path)


if __name__ == "__main__":
    main()
