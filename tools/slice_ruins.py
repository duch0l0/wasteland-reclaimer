"""
Нарезка набора «War ruins» (comshadow, post-apocalyptic war ruins tileset) в отдельные картинки.

Исходники — папка «War ruins/»: страницы 1.png … 28.png (768×768, сетка 48) и две
страницы автотайлов стен RPG Maker (Auto-tile-A4-*.png). Объекты на страницах стоят
порознь на прозрачном фоне — находим их по альфе так же, как в tools/slice_town.py.
Одинаковые объекты (страницы набора частично повторяют друг друга) сохраняются один раз.

Результат:
  assets/ruins/props/r<стр>_<номер>.png — объекты
  assets/ruins/ground/g<стр>_<кол><ряд>.png — плитки земли и пола 96×96 (страницы 20 и 11:
                                          песок, трещины, брусчатка, бетон, дорога; полы домов)
  assets/ruins/index.json               — откуда вырезан объект и его размер
  assets/ruins/catalog_<стр>.png        — сводка с подписями (для подбора объектов, в git не идёт)

Запуск из папки game_project:  .venv/bin/python tools/slice_ruins.py [--catalog]
"""
import hashlib
import json
import os
import re
import sys

import pygame

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slice_town import detect, cut_object  # noqa: E402

SRC = "War ruins"
OUT = os.path.join("assets", "ruins")


GROUND_PAGES = (20, 11)   # здесь плитки земли и полов стоят вплотную по сетке 96 — режем по сетке
G = 96


def cut_ground(n, im):
    """Плитки 96×96 без прозрачных пикселей — земля и полы."""
    out = []
    for cy in range(im.get_height() // G):
        for cx in range(im.get_width() // G):
            cell = im.subsurface((cx * G, cy * G, G, G))
            if pygame.mask.from_surface(cell, 250).count() == G * G:
                gid = f"g{n}_{cx}{cy}"
                pygame.image.save(cell, os.path.join(OUT, "ground", f"{gid}.png"))
                out.append(gid)
    return out


def pages():
    names = [f for f in os.listdir(SRC) if re.fullmatch(r"\d+\.png", f)]
    return sorted(names, key=lambda f: int(f[:-4]))


def catalog(page_no, im, items):
    """Страница с рамками и номерами объектов — чтобы выбрать нужные по картинке."""
    font = pygame.font.SysFont(None, 16)
    sheet = pygame.Surface(im.get_size())
    sheet.fill((90, 80, 70))
    sheet.blit(im, (0, 0))
    for pid, r in items:
        pygame.draw.rect(sheet, (255, 255, 0), r, 1)
        tag = font.render(pid.split("_")[1], True, (255, 255, 255), (0, 0, 0))
        sheet.blit(tag, (r.x + 1, r.y + 1))
    pygame.image.save(sheet, os.path.join(OUT, f"catalog_{page_no:02d}.png"))


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)
    pygame.init()
    with_catalog = "--catalog" in sys.argv
    os.makedirs(os.path.join(OUT, "props"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "ground"), exist_ok=True)
    index, seen = {}, {}
    for fname in pages():
        n = int(fname[:-4])
        im = pygame.image.load(os.path.join(SRC, fname))
        if n in GROUND_PAGES:
            print(f"стр. {n}: плиток земли {len(cut_ground(n, im))}")
        soft = pygame.mask.from_surface(im, 8)
        soft_parts = [(pygame.Rect(c.get_bounding_rects()[0]), c) for c in soft.connected_components(4)]
        shown = []
        for i, r in enumerate(detect(im)):
            img = cut_object(im, r, soft_parts)
            h = hashlib.md5(pygame.image.tobytes(img, "RGBA") + bytes(str(img.get_size()), "ascii")).hexdigest()
            pid = seen.get(h) or f"r{n}_{i:03d}"
            if h not in seen:
                seen[h] = pid
                pygame.image.save(img, os.path.join(OUT, "props", f"{pid}.png"))
                index[pid] = {"page": n, "rect": list(r), "size": list(img.get_size())}
            shown.append((f"r{n}_{i:03d}", r))
        if with_catalog:
            catalog(n, im, shown)
        print(f"стр. {n}: {len(shown)} объектов")
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=1)
    print(f"объектов без повторов: {len(index)} -> {OUT}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
