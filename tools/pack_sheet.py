"""
Лист предметов нарезанного набора с подписями — выбирать спрайты по имени (pk:<набор>/<имя>).

  .venv/bin/python tools/pack_sheet.py <набор> <страница> <out.png> [ширина ячейки]
  .venv/bin/python tools/pack_sheet.py west 2 /tmp/west_2.png
"""
import json
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    pack, page, out = sys.argv[1], sys.argv[2], sys.argv[3]
    cell = int(sys.argv[4]) if len(sys.argv) > 4 else 150
    pygame.init()
    pygame.display.set_mode((1, 1))
    base = os.path.join(ROOT, "assets", "packs", pack)
    items = json.load(open(os.path.join(base, "index.json")))["items"]
    names = sorted(n for n in items if n.startswith(f"{pack}_{page}_"))
    cols = max(1, 1500 // cell)
    rows = (len(names) + cols - 1) // cols
    sheet = pygame.Surface((cols * cell, rows * (cell + 18)))
    sheet.fill((58, 54, 50))
    font = pygame.font.SysFont(None, 18)
    for i, n in enumerate(names):
        img = pygame.image.load(os.path.join(base, items[n].get("dir", "props"), n + ".png")).convert_alpha()
        k = min(1.0, (cell - 8) / max(img.get_width(), img.get_height()))
        if k < 1:
            img = pygame.transform.smoothscale(img, (max(1, int(img.get_width() * k)), max(1, int(img.get_height() * k))))
        x, y = (i % cols) * cell, (i // cols) * (cell + 18)
        sheet.blit(img, img.get_rect(midbottom=(x + cell // 2, y + cell - 2)))
        label = font.render(n[len(pack) + 1:] + ("" if k >= 1 else f" ×{k:.1f}"), True, (235, 225, 200))
        sheet.blit(label, (x + 4, y + cell))
    pygame.image.save(sheet, out)
    print(out, len(names), "предметов")


if __name__ == "__main__":
    main()
