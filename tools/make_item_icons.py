"""
Иконки оружия из листа npc/raw/weapons.png (3547×1493, оружие вразброс на прозрачном фоне).

Объекты на листе находятся по альфе и сортируются по рядам (как в сводке, которую
печатает --catalog), каждой иконке — номер объекта. Иконка — квадрат 64×64, оружие
вписано по ширине и стоит по центру: игра масштабирует иконку в квадрат (src/loader.item_icon),
и вытянутое оружие не сплющивается.

Запуск из папки game_project:  .venv/bin/python tools/make_item_icons.py
"""
import os
import sys

import pygame

SRC = os.path.join("npc", "raw", "weapons.png")
OUT = os.path.join("assets", "items")
SIZE = 64

# icon (поле в data/items.json) -> номер объекта на листе
ICONS = {
    "shotgun": 20,         # помповый дробовик
    "assault_rifle": 72,   # автомат с деревянным прикладом
    "pistol10": 81,        # армейский пистолет деда
    "hunting_rifle": 3,    # охотничья винтовка Дэкса
}


def objects(sheet):
    m = pygame.mask.from_surface(sheet, 60)
    rects = [pygame.Rect(c.get_bounding_rects()[0]) for c in m.connected_components(400)]
    rects = [r for r in rects if r.w > 60]
    rects.sort(key=lambda r: (r.y // 120, r.x))
    return rects


def icon(sheet, rect):
    img = sheet.subsurface(rect).copy()
    k = (SIZE - 4) / max(rect.w, rect.h)
    img = pygame.transform.smoothscale(img, (max(1, round(rect.w * k)), max(1, round(rect.h * k))))
    out = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
    out.blit(img, ((SIZE - img.get_width()) // 2, (SIZE - img.get_height()) // 2))
    return out


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)
    pygame.init()
    sheet = pygame.image.load(SRC)
    rects = objects(sheet)
    os.makedirs(OUT, exist_ok=True)
    for name, idx in ICONS.items():
        pygame.image.save(icon(sheet, rects[idx]), os.path.join(OUT, f"{name}.png"))
        print(f"{name}: объект {idx} {tuple(rects[idx])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
